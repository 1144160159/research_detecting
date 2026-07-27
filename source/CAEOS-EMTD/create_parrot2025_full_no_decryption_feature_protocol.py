from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def load_canonical(path: Path, schema: str) -> dict[str, Any]:
    value = load_json(path)
    if (
        value.get("schema_version") != schema
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError(f"invalid canonical artifact: {path}")
    return value


def capture_id(member: str) -> str:
    return hashlib.sha256(member.encode("utf-8")).hexdigest()[:20]


def full_capture_inventory(
    structural: dict[str, Any], expected_linktype: int
) -> list[dict[str, Any]]:
    captures = []
    for pair in structural["capture_pairs"]:
        member = str(pair["pcap"])
        if not member.endswith(".pcap") or "sslkeylog_" in member.casefold():
            raise ValueError(f"invalid PARROT PCAP member: {member}")
        linktype = int(pair["pcap_header"]["linktype"])
        if linktype != expected_linktype:
            raise ValueError(f"unexpected PARROT linktype for {member}: {linktype}")
        captures.append(
            {
                "capture_id": capture_id(member),
                "application": str(pair["app"]),
                "member": member,
                "size_bytes": int(pair["pcap_size_bytes"]),
                "crc32": str(pair["pcap_crc32"]),
                "linktype": linktype,
            }
        )
    captures.sort(key=lambda item: item["member"])
    if len(captures) != 320:
        raise ValueError("PARROT full extraction requires exactly 320 PCAPs")
    if len({item["capture_id"] for item in captures}) != len(captures):
        raise ValueError("PARROT capture ID collision")
    app_counts = Counter(item["application"] for item in captures)
    if len(app_counts) != 80 or set(app_counts.values()) != {4}:
        raise ValueError("PARROT full extraction requires 80 applications x 4 captures")
    return captures


def create_protocol(
    *,
    project_root: Path,
    structural_audit_path: Path,
    canary_protocol_path: Path,
    canary_result_path: Path,
    output_root: Path,
) -> dict[str, Any]:
    if (
        (output_root / "feature_shard_manifest.json").exists()
        or (output_root / "full_feature_extraction_complete").exists()
        or list((output_root / "shards").glob("*/manifest.json"))
    ):
        raise ValueError("full feature protocol must be frozen before shard results")
    structural = load_json(structural_audit_path)
    canary_protocol = load_canonical(
        canary_protocol_path, "parrot2025_no_decryption_canary_protocol_v1"
    )
    canary_result = load_canonical(
        canary_result_path, "parrot2025_no_decryption_canary_result_v1"
    )
    if (
        structural.get("schema_version") != "parrot2025_structural_admission_v1"
        or structural.get("source", {}).get("manifest_declared_sha256")
        != canary_protocol["archive_sha256"]
        or canary_result.get("protocol_manifest_sha256")
        != canary_protocol["manifest_sha256"]
        or canary_result.get("passed") is not True
    ):
        raise ValueError("PARROT structural or canary binding failed")
    archive = Path(canary_protocol["archive"])
    if file_hash(archive) != canary_protocol["archive_sha256"]:
        raise ValueError("PARROT archive SHA256 mismatch before full freeze")
    captures = full_capture_inventory(
        structural, int(canary_protocol["input_contract"]["linktype"])
    )
    implementation_files = (
        "create_parrot2025_full_no_decryption_feature_protocol.py",
        "run_parrot2025_full_no_decryption_feature_extraction.py",
        "summarize_parrot2025_full_no_decryption_features.py",
        "extract_parrot2025_no_decryption_canary.py",
        "scripts/wait_and_run_parrot2025_full_no_decryption_features.sh",
    )
    implementations = {}
    for relative in implementation_files:
        path = project_root / relative
        if not path.is_file():
            raise ValueError(f"PARROT full implementation missing: {path}")
        implementations[relative] = file_hash(path)
    protocol: dict[str, Any] = {
        "schema_version": "parrot2025_full_no_decryption_feature_protocol_v1",
        "status": "frozen_before_full_feature_extraction",
        "formal_model_metric_count_at_freeze": 0,
        "dataset": "PARROT2025",
        "dataset_role": "external_benign_mobile_application_domain_shift_safety_only",
        "archive": str(archive.resolve()),
        "archive_sha256": canary_protocol["archive_sha256"],
        "captures": captures,
        "capture_count": len(captures),
        "application_count": 80,
        "captures_per_application": 4,
        "feature_columns": canary_protocol["feature_columns"],
        "feature_count": canary_protocol["feature_count"],
        "metadata_columns": canary_protocol["metadata_columns"],
        "feature_engine": canary_protocol["feature_engine"],
        "input_contract": {
            **canary_protocol["input_contract"],
            "capture_group_is_indivisible": True,
            "one_output_shard_per_pcap": True,
        },
        "safety_policy": {
            "ssl_key_members_read": 0,
            "payload_decryption": False,
            "deep_packet_inspection": False,
            "training_use": False,
            "validation_use": False,
            "calibration_use": False,
            "feature_selection_use": False,
            "threshold_selection_use": False,
            "malicious_label_assignment": False,
            "model_metrics_generated": False,
        },
        "resume_policy": {
            "reuse_only_canonical_shard_manifest_with_matching_csv_sha256": True,
            "overwrite_invalid_or_partial_shard": False,
            "fail_on_unexpected_shard": True,
        },
        "dependencies": {
            "structural_audit": {
                "path": str(structural_audit_path.resolve()),
                "file_sha256": file_hash(structural_audit_path),
            },
            "canary_protocol": {
                "path": str(canary_protocol_path.resolve()),
                "manifest_sha256": canary_protocol["manifest_sha256"],
                "file_sha256": file_hash(canary_protocol_path),
            },
            "canary_result": {
                "path": str(canary_result_path.resolve()),
                "manifest_sha256": canary_result["manifest_sha256"],
                "file_sha256": file_hash(canary_result_path),
            },
        },
        "implementation_sha256": implementations,
        "output_root": str(output_root.resolve()),
        "claim_boundary": {
            "full_feature_extraction_only": True,
            "external_benign_safety_model_evaluation_completed": False,
            "malicious_unknown_detection_claim_allowed": False,
            "accuracy_sota_claim_allowed": False,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--structural-audit", type=Path, required=True)
    parser.add_argument("--canary-protocol", type=Path, required=True)
    parser.add_argument("--canary-result", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = create_protocol(
        project_root=args.project_root,
        structural_audit_path=args.structural_audit,
        canary_protocol_path=args.canary_protocol,
        canary_result_path=args.canary_result,
        output_root=args.output_root,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
