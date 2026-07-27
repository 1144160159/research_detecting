from __future__ import annotations

import argparse
import binascii
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, BinaryIO
from zipfile import ZipFile

import dpkt
import pandas as pd
from nfstream import NFStreamer

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def verify_protocol(
    protocol: dict[str, Any], project_root: Path, protocol_path: Path
) -> None:
    if (
        protocol.get("schema_version")
        != "parrot2025_no_decryption_canary_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("formal_model_metric_count_at_freeze") != 0
    ):
        raise ValueError("invalid PARROT canary protocol")
    if protocol.get("claim_boundary", {}).get(
        "training_validation_or_calibration_use_allowed"
    ) is not False:
        raise ValueError("PARROT canary protocol permits forbidden fitting use")
    for relative, expected in protocol["implementation_sha256"].items():
        if file_hash(project_root / relative) != expected:
            raise ValueError(f"PARROT canary implementation changed: {relative}")
    if file_hash(Path(protocol["archive"])) != protocol["archive_sha256"]:
        raise ValueError("PARROT archive changed after protocol freeze")
    if file_hash(protocol_path) == "":
        raise ValueError("unreachable protocol file")


def convert_sll2_to_ethernet(
    source: BinaryIO, destination: BinaryIO
) -> dict[str, int]:
    reader = dpkt.pcap.Reader(source)
    if reader.datalink() != dpkt.pcap.DLT_LINUX_SLL2:
        raise ValueError("PARROT canary requires Linux cooked v2 input")
    writer = dpkt.pcap.Writer(destination, linktype=dpkt.pcap.DLT_EN10MB)
    packet_count = 0
    converted_count = 0
    skipped_non_ip_count = 0
    malformed_count = 0
    for timestamp, packet in reader:
        packet_count += 1
        try:
            cooked = dpkt.sll2.SLL2(packet)
            if cooked.ethtype not in (
                dpkt.ethernet.ETH_TYPE_IP,
                dpkt.ethernet.ETH_TYPE_IP6,
            ):
                skipped_non_ip_count += 1
                continue
            ethernet = (
                b"\x00" * 12
                + int(cooked.ethtype).to_bytes(2, "big")
                + bytes(cooked.data)
            )
            writer.writepkt(ethernet, timestamp)
            converted_count += 1
        except (dpkt.UnpackError, ValueError):
            malformed_count += 1
    return {
        "input_packets": packet_count,
        "converted_ip_packets": converted_count,
        "skipped_non_ip_packets": skipped_non_ip_count,
        "malformed_packets": malformed_count,
    }


def member_crc32(archive: ZipFile, member: str) -> str:
    checksum = 0
    with archive.open(member) as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            checksum = binascii.crc32(block, checksum)
    return f"{checksum & 0xFFFFFFFF:08x}"


def extract_capture(
    *,
    archive: ZipFile,
    capture: dict[str, Any],
    protocol: dict[str, Any],
    temp_root: Path,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    member = capture["member"]
    if not member.endswith(".pcap") or "sslkeylog_" in member.casefold():
        raise ValueError("only PCAP members are permitted in PARROT canary")
    info = archive.getinfo(member)
    if info.file_size != capture["size_bytes"]:
        raise ValueError(f"PARROT member size mismatch: {member}")
    if member_crc32(archive, member) != capture["crc32"]:
        raise ValueError(f"PARROT member CRC mismatch: {member}")
    source_path = temp_root / Path(member).name
    ethernet_path = temp_root / f"{Path(member).stem}.ethernet.pcap"
    with archive.open(member) as source, source_path.open("wb") as destination:
        while True:
            block = source.read(1024 * 1024)
            if not block:
                break
            destination.write(block)
    with source_path.open("rb") as source, ethernet_path.open("wb") as destination:
        conversion = convert_sll2_to_ethernet(source, destination)
    engine = protocol["feature_engine"]
    frame = NFStreamer(
        source=str(ethernet_path),
        statistical_analysis=bool(engine["statistical_analysis"]),
        n_dissections=int(engine["n_dissections"]),
        decode_tunnels=bool(engine["decode_tunnels"]),
    ).to_pandas()
    features = protocol["feature_columns"]
    missing = sorted(set(features) - set(frame.columns))
    if missing:
        raise ValueError(f"NFStream feature columns missing: {missing}")
    output = frame.loc[:, features].copy()
    output[protocol["metadata_columns"][0]] = member
    output[protocol["metadata_columns"][1]] = capture["application"]
    output[protocol["metadata_columns"][2]] = "benign_external_safety_only"
    values = output.loc[:, features].to_numpy(dtype=float)
    nonfinite = int((~pd.notna(values)).sum()) + int(
        sum(not math.isfinite(float(value)) for value in values.ravel() if pd.notna(value))
    )
    if len(output) == 0 or nonfinite != 0:
        raise ValueError(f"invalid PARROT canary features for {member}")
    evidence = {
        "member": member,
        "application": capture["application"],
        **conversion,
        "flow_rows": int(len(output)),
        "feature_count": len(features),
        "missing_feature_count": len(missing),
        "nonfinite_feature_count": nonfinite,
    }
    return output, evidence


def run(
    *,
    protocol_path: Path,
    project_root: Path,
    output_root: Path,
) -> dict[str, Any]:
    protocol = load_json(protocol_path)
    verify_protocol(protocol, project_root, protocol_path)
    output_root.mkdir(parents=True, exist_ok=True)
    output_csv = output_root / "parrot2025_no_decryption_canary.csv"
    if output_csv.exists():
        raise ValueError("PARROT canary output already exists")
    frames: list[pd.DataFrame] = []
    captures: list[dict[str, Any]] = []
    with ZipFile(protocol["archive"]) as archive, TemporaryDirectory(
        dir=output_root
    ) as temp:
        temp_root = Path(temp)
        for capture in protocol["selected_captures"]:
            frame, evidence = extract_capture(
                archive=archive,
                capture=capture,
                protocol=protocol,
                temp_root=temp_root,
            )
            frames.append(frame)
            captures.append(evidence)
    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(output_csv, index=False)
    result: dict[str, Any] = {
        "schema_version": "parrot2025_no_decryption_canary_result_v1",
        "status": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "protocol_file_sha256": file_hash(protocol_path),
        "output_csv": str(output_csv.resolve()),
        "output_csv_sha256": file_hash(output_csv),
        "capture_count": len(captures),
        "flow_row_count": int(len(combined)),
        "feature_count": len(protocol["feature_columns"]),
        "captures": captures,
        "safety_audit": {
            "ssl_key_members_read": 0,
            "payload_decryption": False,
            "deep_packet_inspection": False,
            "training_use": False,
            "validation_use": False,
            "calibration_use": False,
            "malicious_label_assignment": False,
            "model_metrics_generated": False,
        },
        "validation": {
            "all_selected_captures_generated_flows": all(
                item["flow_rows"] > 0 for item in captures
            ),
            "all_feature_vectors_finite": all(
                item["nonfinite_feature_count"] == 0 for item in captures
            ),
            "feature_contract_exact": all(
                item["feature_count"] == protocol["feature_count"]
                and item["missing_feature_count"] == 0
                for item in captures
            ),
            "no_malformed_packets": all(
                item["malformed_packets"] == 0 for item in captures
            ),
            "no_forbidden_data_or_model_use": True,
        },
        "claim_boundary": protocol["claim_boundary"],
    }
    result["passed"] = all(result["validation"].values())
    result["manifest_sha256"] = canonical_hash(result)
    (output_root / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if result["passed"]:
        (output_root / "canary_complete").touch()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    value = run(
        protocol_path=args.protocol,
        project_root=args.project_root,
        output_root=args.output_root,
    )
    print(json.dumps({"passed": value["passed"], "rows": value["flow_row_count"]}))


if __name__ == "__main__":
    main()
