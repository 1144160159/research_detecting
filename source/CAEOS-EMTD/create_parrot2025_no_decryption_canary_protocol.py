from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import dpkt
import nfstream

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def feature_columns(config: dict[str, Any]) -> list[str]:
    return [
        str(column)
        for columns in config["modalities"].values()
        for column in columns
    ]


def select_captures(
    capture_pairs: list[dict[str, Any]], selected_capture_count: int
) -> list[dict[str, Any]]:
    smallest_by_app: dict[str, dict[str, Any]] = {}
    for capture in sorted(
        capture_pairs,
        key=lambda item: (
            int(item["pcap_size_bytes"]),
            str(item["pcap"]),
        ),
    ):
        smallest_by_app.setdefault(str(capture["app"]), capture)
    selected = sorted(
        smallest_by_app.values(),
        key=lambda item: (
            int(item["pcap_size_bytes"]),
            str(item["pcap"]),
        ),
    )[:selected_capture_count]
    if len(selected) != selected_capture_count:
        raise ValueError("insufficient distinct PARROT applications for canary")
    return [
        {
            "application": str(item["app"]),
            "member": str(item["pcap"]),
            "size_bytes": int(item["pcap_size_bytes"]),
            "crc32": str(item["pcap_crc32"]),
            "linktype": int(item["pcap_header"]["linktype"]),
        }
        for item in selected
    ]


def create_protocol(
    *,
    project_root: Path,
    archive: Path,
    structural_audit_path: Path,
    config_path: Path,
    output_root: Path,
) -> dict[str, Any]:
    output_csv = output_root / "parrot2025_no_decryption_canary.csv"
    if output_csv.exists():
        raise ValueError("canary protocol must be frozen before extracted features")
    audit = load_json(structural_audit_path)
    config = load_json(config_path)
    if (
        audit.get("schema_version") != "parrot2025_structural_admission_v1"
        or audit.get("admission_decision", {}).get(
            "pcap_feature_extraction_structurally_feasible"
        )
        is not True
        or audit.get("admission_decision", {}).get(
            "external_benign_safety_evaluation_admitted"
        )
        is not True
        or audit.get("admission_decision", {}).get("malicious_ground_truth_present")
        is not False
    ):
        raise ValueError("PARROT structural admission is insufficient")
    if (
        config.get("schema_version")
        != "parrot2025_external_benign_canary_config_v1"
    ):
        raise ValueError("unexpected PARROT canary config schema")
    expected_archive_sha = audit["source"]["manifest_declared_sha256"]
    if file_hash(archive) != expected_archive_sha:
        raise ValueError("PARROT archive SHA256 mismatch")
    prohibited = config["prohibitions"]
    if any(value is not False for value in prohibited.values()):
        raise ValueError("all PARROT canary prohibited uses must be frozen false")
    features = feature_columns(config)
    reference_path = project_root / config["feature_contract_reference"]
    reference_config = load_json(reference_path)
    reference_features = feature_columns(reference_config)
    if (
        features != reference_features
        or len(features) != 56
        or len(set(features)) != len(features)
    ):
        raise ValueError(
            "PARROT canary must exactly match the 56-column NFStream feature contract"
        )
    selected = select_captures(
        audit["capture_pairs"], int(config["selected_capture_count"])
    )
    if any(
        item["linktype"] != int(config["input_linktype"]) for item in selected
    ):
        raise ValueError("selected PARROT canary capture linktype mismatch")
    extractor_path = project_root / "extract_parrot2025_no_decryption_canary.py"
    protocol: dict[str, Any] = {
        "schema_version": "parrot2025_no_decryption_canary_protocol_v1",
        "status": "frozen_before_feature_extraction",
        "formal_model_metric_count_at_freeze": 0,
        "dataset": "PARROT2025",
        "dataset_role": config["dataset_role"],
        "source_doi": audit["source"]["doi"],
        "archive": str(archive.resolve()),
        "archive_sha256": expected_archive_sha,
        "structural_audit": str(structural_audit_path.resolve()),
        "structural_audit_sha256": file_hash(structural_audit_path),
        "config": str(config_path.resolve()),
        "config_sha256": file_hash(config_path),
        "feature_contract_reference": str(reference_path.resolve()),
        "feature_contract_reference_sha256": file_hash(reference_path),
        "selected_captures": selected,
        "selected_capture_count": len(selected),
        "feature_columns": features,
        "feature_count": len(features),
        "metadata_columns": [
            config["capture_group_column"],
            config["application_column"],
            config["reference_role_column"],
        ],
        "feature_engine": {
            **config["feature_engine"],
            "nfstream_version": nfstream.__version__,
            "dpkt_version": dpkt.__version__,
        },
        "input_contract": {
            "linktype": config["input_linktype"],
            "linktype_name": config["input_linktype_name"],
            "conversion": config["conversion"],
            "ssl_key_members_read": 0,
            "payload_decryption": False,
            "deep_packet_inspection": False,
        },
        "claim_boundary": {
            "feature_extraction_canary_only": True,
            "external_benign_safety_model_evaluation_completed": False,
            "malicious_unknown_positive_claim_allowed": False,
            "training_validation_or_calibration_use_allowed": False,
            "model_metrics_generated": False,
        },
        "implementation_sha256": {
            "create_parrot2025_no_decryption_canary_protocol.py": file_hash(
                project_root
                / "create_parrot2025_no_decryption_canary_protocol.py"
            ),
            "extract_parrot2025_no_decryption_canary.py": file_hash(extractor_path),
            "configs/parrot2025_external_benign_canary.json": file_hash(config_path),
            str(reference_path.relative_to(project_root)).replace("\\", "/"): file_hash(
                reference_path
            ),
        },
        "output_csv": str(output_csv.resolve()),
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--structural-audit", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = create_protocol(
        project_root=args.project_root,
        archive=args.archive,
        structural_audit_path=args.structural_audit,
        config_path=args.config,
        output_root=args.output_root,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
