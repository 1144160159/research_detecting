from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(value: dict[str, Any]) -> str:
    payload = dict(value)
    payload.pop("manifest_sha256", None)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def create_protocol(
    *,
    project_root: Path,
    output_root: Path,
    preparer: Path,
    runner: Path,
) -> dict[str, Any]:
    artifacts = list(output_root.glob("*/manifest.json")) if output_root.exists() else []
    if artifacts:
        raise ValueError("preparation protocol must be frozen before prepared manifests")
    bindings = {
        name: {"path": str(path.resolve()), "sha256": file_sha256(path)}
        for name, path in {
            "expansion_protocol": project_root
            / "results/gpu_malicious_dataset_expansion_protocol_v1/protocol.json",
            "admission_execution_protocol": project_root
            / "results/gpu_dataset_admission_execution_protocol_v1/protocol.json",
            "preparer": preparer,
            "lsnm_config": project_root / "configs/lsnm2024_external.json",
            "cic_config": project_root / "configs/cicids2017_strict.json",
            "runner": runner,
        }.items()
    }
    protocol: dict[str, Any] = {
        "schema_version": "gpu_external_dataset_preparation_protocol_v1",
        "status": "frozen_before_preparation",
        "prepared_manifest_count_at_freeze": 0,
        "admission_prerequisite": {
            "audit": str(
                (
                    project_root
                    / "results/gpu_dataset_full_admission_audit_v1/admission_audit.json"
                ).resolve()
            ),
            "passed_marker": str(
                (
                    project_root
                    / "results/gpu_dataset_full_admission_audit_v1/admission_passed"
                ).resolve()
            ),
        },
        "output_root": str(output_root.resolve()),
        "seeds": [223, 227, 229],
        "datasets": {
            "LSNM2024": {
                "groups_per_label": 500,
                "rows_per_group": 8,
                "maximum_rows_per_label": 4000,
                "unit": "packet_rows_grouped_by_bidirectional_session",
            },
            "CICDDoS2019": {
                "groups_per_label": 4000,
                "rows_per_group": 1,
                "maximum_rows_per_label": 4000,
                "unit": "cicflowmeter_flow_rows",
            },
        },
        "selection_rule": (
            "deterministic minimum-hash groups per label followed by deterministic "
            "minimum-hash rows per selected group"
        ),
        "claim_boundary": {
            "formal_selection_evidence": False,
            "unknown_or_test_metric_used_for_preparation": False,
            "prepared_data_may_be_used_before_sidecar_gate": False,
        },
        "bindings": bindings,
    }
    protocol["manifest_sha256"] = canonical_sha256(protocol)
    return protocol


def verify_protocol(protocol: dict[str, Any]) -> None:
    if protocol.get("schema_version") != "gpu_external_dataset_preparation_protocol_v1":
        raise ValueError("unexpected preparation protocol schema")
    if protocol.get("manifest_sha256") != canonical_sha256(protocol):
        raise ValueError("preparation protocol canonical hash mismatch")
    for binding in protocol["bindings"].values():
        path = Path(binding["path"])
        if file_sha256(path) != binding["sha256"]:
            raise ValueError(f"bound preparation input changed: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--preparer", type=Path, required=True)
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = create_protocol(
        project_root=args.project_root,
        output_root=args.output_root,
        preparer=args.preparer,
        runner=args.runner,
    )
    verify_protocol(protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
