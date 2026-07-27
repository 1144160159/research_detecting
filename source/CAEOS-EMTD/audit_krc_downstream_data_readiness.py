from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_gpu_dataset_admission_execution_protocol import (
    verify_protocol as verify_admission_protocol,
)
from create_gpu_dataset_expansion_protocol import (
    central_directory_identity,
)
from create_gpu_external_preparation_protocol import (
    verify_protocol as verify_preparation_protocol,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def prepared_dataset(
    data_root: Path, dataset: str
) -> Dict[str, Any]:
    root = data_root / dataset
    manifest_path = root / "manifest.json"
    complete = root / "preparation_complete"
    if not manifest_path.is_file() or not complete.is_file():
        return {
            "dataset": dataset,
            "manifest_exists": manifest_path.is_file(),
            "complete_marker_exists": complete.is_file(),
            "passed": False,
        }
    manifest = load_json(manifest_path)
    files = manifest.get("files", {})
    seed_checks = {}
    for seed in ("223", "227", "229"):
        entry = files.get(seed, {})
        csv_path = root / f"seed{seed}.csv"
        sidecar_path = root / f"seed{seed}.csv.json"
        seed_checks[seed] = bool(
            csv_path.is_file()
            and sidecar_path.is_file()
            and entry.get("passed") is True
            and entry.get("csv_sha256") == file_hash(csv_path)
        )
    return {
        "dataset": dataset,
        "manifest_exists": True,
        "manifest_file_sha256": file_hash(manifest_path),
        "complete_marker_exists": True,
        "seed_checks": seed_checks,
        "passed": bool(
            manifest.get("schema_version")
            == "gpu_external_prepared_dataset_manifest_v1"
            and manifest.get("dataset") == dataset
            and manifest.get("passed") is True
            and all(seed_checks.values())
        ),
    }


def audit(
    project_root: Path,
    dataset_root: Path,
) -> Dict[str, Any]:
    expansion_path = (
        project_root
        / "results/gpu_malicious_dataset_expansion_protocol_v1/protocol.json"
    )
    admission_protocol_path = (
        project_root
        / "results/gpu_dataset_admission_execution_protocol_v1/protocol.json"
    )
    admission_path = (
        project_root
        / "results/gpu_dataset_full_admission_audit_v1/admission_audit.json"
    )
    admission_marker = (
        project_root
        / "results/gpu_dataset_full_admission_audit_v1/admission_passed"
    )
    preparation_protocol_path = (
        project_root
        / "results/gpu_external_dataset_preparation_protocol_v1/protocol.json"
    )
    external_design_path = (
        project_root
        / "results/gpu_external_dataset_evaluation_v1/design_protocol.json"
    )
    parrot_feature_path = (
        project_root
        / "results/parrot2025_full_no_decryption_features_v1/protocol.json"
    )
    expansion = load_json(expansion_path)
    admission_protocol = load_json(admission_protocol_path)
    preparation_protocol = load_json(preparation_protocol_path)
    external_design = load_json(external_design_path)
    parrot_features = load_json(parrot_feature_path)
    verify_admission_protocol(admission_protocol)
    verify_preparation_protocol(preparation_protocol)
    if (
        external_design.get("schema_version")
        != "gpu_external_dataset_evaluation_design_protocol_v1"
        or external_design.get("manifest_sha256")
        != canonical_hash(external_design)
        or parrot_features.get("schema_version")
        != "parrot2025_full_no_decryption_feature_protocol_v1"
        or parrot_features.get("manifest_sha256")
        != canonical_hash(parrot_features)
    ):
        raise ValueError("canonical external and PARROT protocols required")

    raw_rows = []
    for expected in expansion["source_identity"]:
        path = Path(expected["path"])
        actual = central_directory_identity(path) if path.is_file() else None
        raw_rows.append(
            {
                "path": str(path),
                "exists": path.is_file(),
                "size_bytes": path.stat().st_size if path.is_file() else None,
                "central_directory_identity_matches": actual == expected,
            }
        )
    raw_external_passes = len(raw_rows) == 3 and all(
        row["central_directory_identity_matches"] for row in raw_rows
    )

    admission = (
        load_json(admission_path) if admission_path.is_file() else None
    )
    admission_passes = bool(
        admission is not None
        and admission.get("schema_version")
        == "gpu_malicious_dataset_full_admission_audit_v1"
        and admission.get("admission_passed") is True
        and admission_marker.is_file()
    )
    prepared_root = dataset_root / "caeos_external_open_set_v1"
    prepared = {
        name: prepared_dataset(prepared_root, name)
        for name in ("LSNM2024", "CICDDoS2019")
    }
    prepared_passes = all(
        value["passed"] for value in prepared.values()
    )

    parrot_root = dataset_root / "PARROT2025_mitmproxy"
    pcaps = sorted(parrot_root.glob("*.pcap"))
    expected_captures = {
        str(record["member"]).split("/", 1)[-1]: int(record["size_bytes"])
        for record in parrot_features["captures"]
    }
    observed_captures = {
        path.name: path.stat().st_size for path in pcaps
    }
    parrot_raw_passes = observed_captures == expected_captures
    parrot_feature_passes = bool(
        parrot_features.get("capture_count") == 320
        and parrot_features.get("application_count") == 80
        and parrot_features.get("feature_count") == 56
        and parrot_features.get("formal_model_metric_count_at_freeze") == 0
        and parrot_features.get("safety_policy", {}).get(
            "payload_decryption"
        )
        is False
        and parrot_features.get("safety_policy", {}).get("training_use")
        is False
        and parrot_features.get("safety_policy", {}).get(
            "threshold_selection_use"
        )
        is False
    )
    checks = {
        "external_raw_archives_match_frozen_identity": raw_external_passes,
        "external_full_admission_passes": admission_passes,
        "external_three_seed_preparation_passes": prepared_passes,
        "parrot_320_raw_captures_match_protocol": parrot_raw_passes,
        "parrot_56_feature_no_decryption_protocol_passes": (
            parrot_feature_passes
        ),
    }
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_downstream_data_readiness_v1",
        "state": "read_only_snapshot",
        "raw_external_archives": raw_rows,
        "external_admission": {
            "audit_exists": admission_path.is_file(),
            "passed_marker_exists": admission_marker.is_file(),
            "passes": admission_passes,
        },
        "external_prepared": prepared,
        "parrot": {
            "raw_capture_count": len(pcaps),
            "application_count": parrot_features["application_count"],
            "feature_count": parrot_features["feature_count"],
            "raw_captures_match_protocol": parrot_raw_passes,
            "feature_protocol_passes": parrot_feature_passes,
        },
        "checks": checks,
        "raw_data_available": bool(
            raw_external_passes
            and parrot_raw_passes
            and parrot_feature_passes
        ),
        "ready_for_downstream_execution": all(checks.values()),
        "next_step": (
            "wait_for_krc_selection_then_freeze_execution_protocols"
            if all(checks.values())
            else (
                "complete_external_full_admission_then_three_seed_"
                "preparation_without_model_effect_access"
            )
        ),
        "input_file_sha256": {
            "expansion_protocol": file_hash(expansion_path),
            "admission_execution_protocol": file_hash(
                admission_protocol_path
            ),
            "preparation_protocol": file_hash(preparation_protocol_path),
            "external_design": file_hash(external_design_path),
            "parrot_feature_protocol": file_hash(parrot_feature_path),
        },
        "claim_boundary": {
            "readiness_is_not_model_effect_evidence": True,
            "raw_data_available_does_not_imply_prepared": True,
            "parrot_supports_benign_safety_only": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = audit(
        args.project_root.resolve(), args.dataset_root.resolve()
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
