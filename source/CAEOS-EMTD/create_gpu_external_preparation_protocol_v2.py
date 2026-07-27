from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from create_gpu_dataset_label_reconciliation_protocol import (
    verify_protocol as verify_reconciliation_protocol,
)
from external_dataset_protocol_utils import canonical_hash, file_hash, load_json


def _binding(path: Path) -> Dict[str, str]:
    return {"path": str(path.resolve()), "sha256": file_hash(path)}


def create_protocol(
    *,
    project_root: Path,
    data_root: Path,
    result_root: Path,
    runner: Path,
) -> Dict[str, Any]:
    if list(data_root.glob("*/manifest.json")):
        raise ValueError("v2 preparation protocol must precede prepared manifests")
    if (result_root / "summary.json").exists():
        raise ValueError("v2 preparation protocol must precede summary")

    reconciliation_path = (
        project_root
        / "results/gpu_dataset_label_reconciliation_protocol_v1/protocol.json"
    )
    admission_path = (
        project_root
        / "results/gpu_dataset_reconciled_admission_audit_v2/admission_audit.json"
    )
    admission_marker = admission_path.parent / "admission_passed"
    expansion_path = (
        project_root
        / "results/gpu_malicious_dataset_expansion_protocol_v1/protocol.json"
    )
    reconciliation = load_json(reconciliation_path)
    admission = load_json(admission_path)
    verify_reconciliation_protocol(reconciliation)
    if (
        admission.get("schema_version")
        != "gpu_malicious_dataset_reconciled_admission_audit_v2"
        or admission.get("manifest_sha256") != canonical_hash(admission)
        or admission.get("admission_passed") is not True
        or admission.get("protocol_manifest_sha256")
        != reconciliation["manifest_sha256"]
        or not admission_marker.is_file()
    ):
        raise ValueError("canonical passed reconciled admission required")

    protocol: Dict[str, Any] = {
        "schema_version": "gpu_external_dataset_preparation_protocol_v2",
        "status": "frozen_before_v2_preparation",
        "execution_admitted": True,
        "prepared_manifest_count_at_freeze": 0,
        "summary_count_at_freeze": 0,
        "output_root": str(data_root.resolve()),
        "result_root": str(result_root.resolve()),
        "seeds": [223, 227, 229],
        "datasets": {
            "LSNM2024": {
                "groups_per_label": 500,
                "rows_per_group": 8,
                "expected_attack_family_count": 15,
            },
            "CICDDoS2019": {
                "groups_per_label": 4000,
                "rows_per_group": 1,
                "expected_attack_family_count": 17,
                "label_aliases": {"UDP-lag": "UDPLag"},
                "retained_new_families": ["WebDDoS"],
            },
        },
        "selection_rule": (
            "deterministic minimum-hash groups per label followed by "
            "deterministic minimum-hash rows per selected group"
        ),
        "bindings": {
            "creator": _binding(
                project_root / "create_gpu_external_preparation_protocol_v2.py"
            ),
            "protocol_utils": _binding(
                project_root / "external_dataset_protocol_utils.py"
            ),
            "reconciliation_protocol": _binding(reconciliation_path),
            "reconciled_admission_audit": _binding(admission_path),
            "expansion_protocol": _binding(expansion_path),
            "preparer": _binding(
                project_root / "prepare_gpu_external_datasets_v2.py"
            ),
            "label_module": _binding(
                project_root / "external_dataset_labels.py"
            ),
            "lsnm_config": _binding(
                project_root / "configs/lsnm2024_external.json"
            ),
            "cic_config": _binding(
                project_root / "configs/cicids2017_strict.json"
            ),
            "runner": _binding(runner),
        },
        "claim_boundary": {
            "formal_selection_evidence": False,
            "unknown_or_test_metric_used_for_preparation": False,
            "label_reconciliation_changes_no_model_feature_value": True,
            "prepared_data_may_be_used_before_sidecar_gate": False,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def verify_protocol(protocol: Dict[str, Any]) -> None:
    if (
        protocol.get("schema_version")
        != "gpu_external_dataset_preparation_protocol_v2"
        or protocol.get("status") != "frozen_before_v2_preparation"
        or protocol.get("execution_admitted") is not True
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("seeds") != [223, 227, 229]
        or protocol.get("datasets", {})
        .get("CICDDoS2019", {})
        .get("expected_attack_family_count")
        != 17
    ):
        raise ValueError("invalid v2 preparation protocol")
    for binding in protocol["bindings"].values():
        path = Path(binding["path"])
        if file_hash(path) != binding["sha256"]:
            raise ValueError(f"bound v2 preparation input changed: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = create_protocol(
        project_root=args.project_root.resolve(),
        data_root=args.data_root.resolve(),
        result_root=args.result_root.resolve(),
        runner=args.runner.resolve(),
    )
    verify_protocol(protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
