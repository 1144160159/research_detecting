from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
from typing import Any

import numpy as np

from prepare_strict_v4_cic_iot2023_pcap_multimodal import (
    GRAPH_NODE_FEATURES,
    PACKET_COUNT,
    PAYLOAD_TOKENS,
    SEQUENCE_FEATURES,
    extract_pcap,
    pcap_prefix_hash,
    source_stat,
)
from strict_v4_cic_iot2023_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
)


EXPECTED_ACQUISITION_MANIFEST_SHA256 = (
    "ffd50c952ee8c3d3abac841c9fed4a95a2835193f8087e83af8a010d228646a8"
)
EXPECTED_ACTIVE_CAPTURE_COUNT = 24
DATASET_NAMESPACE = "CICIoT2022"


def load_admitted_active_sources(
    dataset_root: Path,
    independent_audit_path: Path,
    expected_capture_count: int = EXPECTED_ACTIVE_CAPTURE_COUNT,
    expected_acquisition_manifest_sha256: str = (
        EXPECTED_ACQUISITION_MANIFEST_SHA256
    ),
) -> tuple[dict[str, Any], list[tuple[Path, dict[str, Any]]]]:
    root = dataset_root.resolve()
    audit_path = independent_audit_path.resolve()
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if audit.get("status") != "passed":
        raise ValueError("CICIoT2022 independent completion audit did not pass")
    if audit.get("dataset_acquisition_admitted") is not True:
        raise ValueError("CICIoT2022 acquisition is not admitted")
    if audit.get("errors"):
        raise ValueError("CICIoT2022 independent audit contains errors")
    if audit.get("manifest_sha256") != expected_acquisition_manifest_sha256:
        raise ValueError("CICIoT2022 acquisition manifest identity differs")
    if audit.get("partial_files") or audit.get("symlinks"):
        raise ValueError("CICIoT2022 audit reports partial files or symlinks")

    selected: list[tuple[Path, dict[str, Any]]] = []
    for item in audit.get("files", []):
        relative_text = str(item.get("relative_path", ""))
        relative = PurePosixPath(relative_text)
        if (
            item.get("kind") != "pcap"
            or len(relative.parts) != 2
            or relative.parts[0] != "5-Active"
        ):
            continue
        if item.get("status") != "passed":
            raise ValueError(f"Active PCAP is not admitted: {relative_text}")
        if item.get("structure", {}).get("capture_format") != "classic_pcap":
            raise ValueError(f"Active source is not classic PCAP: {relative_text}")
        source = (root / Path(*relative.parts)).resolve()
        try:
            source.relative_to(root)
        except ValueError as error:
            raise ValueError(f"Active PCAP escapes dataset root: {source}") from error
        if source.is_symlink() or not source.is_file():
            raise ValueError(f"Active PCAP is missing or a symlink: {source}")
        if source.stat().st_size != int(item["size_bytes"]):
            raise ValueError(f"Active PCAP size differs from audit: {source}")
        selected.append((source, item))

    selected.sort(key=lambda entry: str(entry[1]["relative_path"]))
    if len(selected) != expected_capture_count:
        raise ValueError(
            f"expected {expected_capture_count} admitted Active PCAPs, "
            f"found {len(selected)}"
        )
    return audit, selected


def build_cache(args: argparse.Namespace) -> dict[str, Any]:
    dataset_root = args.dataset_root.resolve()
    audit_path = args.independent_audit.resolve()
    output = args.output.resolve()
    audit, sources = load_admitted_active_sources(
        dataset_root,
        audit_path,
        expected_capture_count=args.expected_capture_count,
        expected_acquisition_manifest_sha256=(
            args.expected_acquisition_manifest_sha256
        ),
    )
    records: dict[str, list[np.ndarray]] = {
        "payload": [],
        "sequence": [],
        "graph": [],
        "quality": [],
    }
    fine_labels: list[str] = []
    families: list[str] = []
    capture_groups: list[str] = []
    source_records: list[dict[str, Any]] = []

    for source, admitted in sources:
        flows, extraction = extract_pcap(
            source,
            args.maximum_flows_per_capture,
        )
        if len(flows) < args.minimum_flows_per_capture:
            raise ValueError(
                f"{source} yielded {len(flows)} flows; "
                f"minimum is {args.minimum_flows_per_capture}"
            )
        relative_path = str(admitted["relative_path"])
        capture_group = f"{DATASET_NAMESPACE}::{relative_path}"
        for payload, sequence, graph, quality in flows:
            records["payload"].append(payload)
            records["sequence"].append(sequence)
            records["graph"].append(graph)
            records["quality"].append(quality)
            fine_labels.append("Benign_Final")
            families.append("Benign")
            capture_groups.append(capture_group)
        source_record = source_stat(source)
        source_record.update(
            {
                "relative_path": relative_path,
                "capture_group": capture_group,
                "independent_audit_sha256": str(admitted["sha256"]),
                "prefix_1mib_sha256": pcap_prefix_hash(source),
                **extraction,
            }
        )
        source_records.append(source_record)

    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        payload=np.stack(records["payload"]),
        sequence=np.stack(records["sequence"]),
        graph=np.stack(records["graph"]),
        quality=np.stack(records["quality"]),
        fine_label=np.asarray(fine_labels),
        family=np.asarray(families),
        capture_group=np.asarray(capture_groups),
    )
    manifest: dict[str, Any] = {
        "schema_version": (
            "strict_v4_ciciot2022_active_benign_multimodal_cache_manifest_v1"
        ),
        "source_dataset": DATASET_NAMESPACE,
        "source_experiment": "5-Active",
        "source_role": "training_only_external_benign",
        "source_root": str(dataset_root),
        "independent_audit_path": str(audit_path),
        "independent_audit_file_sha256": file_hash(audit_path),
        "acquisition_manifest_sha256": audit["manifest_sha256"],
        "cache_path": str(output),
        "cache_sha256": file_hash(output),
        "samples": len(families),
        "source_capture_count": len(source_records),
        "maximum_flows_per_capture": args.maximum_flows_per_capture,
        "minimum_flows_per_capture": args.minimum_flows_per_capture,
        "fine_to_family": {"Benign_Final": "Benign"},
        "modalities": {
            "payload_semantics": {
                "shape": [PAYLOAD_TOKENS],
                "description": "transport payload byte tokens only",
                "network_addresses_and_ports_excluded": True,
            },
            "packet_behavior": {
                "shape": [PACKET_COUNT * SEQUENCE_FEATURES],
                "description": (
                    "ordered length, interval, direction, protocol, flags, "
                    "and payload-length sequence"
                ),
            },
            "packet_interaction_graph": {
                "shape": [
                    PACKET_COUNT * GRAPH_NODE_FEATURES
                    + PACKET_COUNT * PACKET_COUNT
                ],
                "description": (
                    "packet-node attributes and temporal/direction adjacency"
                ),
            },
        },
        "capture_group_binding": (
            "dataset_namespace_plus_relative_source_pcap_path"
        ),
        "source_files": source_records,
        "claim_boundary": {
            "official_active_experiment_is_benign_device_activity": True,
            "cache_use_is_training_only": True,
            "primary_validation_and_test_are_not_modified": True,
            "full_source_hashes_inherited_from_independent_audit": True,
            "full_source_hashes_not_recomputed_during_cache_creation": True,
            "source_prefix_hash_and_stat_bound": True,
            "attack_or_unknown_labels_not_used": True,
        },
        "implementation_sha256": {
            Path(__file__).name: file_hash(Path(__file__).resolve()),
            "prepare_strict_v4_cic_iot2023_pcap_multimodal.py": file_hash(
                Path(__file__).resolve().with_name(
                    "prepare_strict_v4_cic_iot2023_pcap_multimodal.py"
                )
            ),
        },
    }
    manifest["manifest_sha256"] = canonical_hash(manifest)
    atomic_json(output.with_suffix(output.suffix + ".manifest.json"), manifest)
    return manifest


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--independent-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--maximum-flows-per-capture", type=int, default=64)
    parser.add_argument("--minimum-flows-per-capture", type=int, default=64)
    parser.add_argument(
        "--expected-capture-count",
        type=int,
        default=EXPECTED_ACTIVE_CAPTURE_COUNT,
    )
    parser.add_argument(
        "--expected-acquisition-manifest-sha256",
        default=EXPECTED_ACQUISITION_MANIFEST_SHA256,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    if args.output.exists():
        raise ValueError(f"refusing to overwrite cache: {args.output}")
    if args.maximum_flows_per_capture < args.minimum_flows_per_capture:
        raise ValueError("maximum flows must be at least minimum flows")
    manifest = build_cache(args)
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
