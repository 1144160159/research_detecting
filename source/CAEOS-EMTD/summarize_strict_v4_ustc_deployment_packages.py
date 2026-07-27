from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def summarize(protocol: dict[str, Any], project_root: Path) -> dict[str, Any]:
    expected = {
        package["package_id"]: package
        for package in protocol["package_matrix"]["inputs"]
    }
    result_root = Path(protocol["output_policy"]["result_root"])
    record_paths = sorted(result_root.rglob("package_record.json"))
    if len(record_paths) != 20:
        raise ValueError(f"expected 20 package records, got {len(record_paths)}")
    records = []
    observed = set()
    for path in record_paths:
        record = load(path)
        package_id = record.get("package_id")
        if package_id not in expected or package_id in observed:
            raise ValueError(f"unexpected or duplicate package: {package_id}")
        observed.add(package_id)
        if (
            record.get("schema_version")
            != "strict_v4_ustc_deployment_package_record_v1"
            or record.get("protocol_manifest_sha256")
            != protocol["manifest_sha256"]
            or record.get("selected_algorithm")
            != protocol["selection"]["selected_algorithm"]
            or record.get("formal_model_metrics_admitted") != 0
            or record.get("external_execution_admitted") is not False
            or record.get("storage_policy") != "gpu_private_do_not_publish"
        ):
            raise ValueError(f"package record policy mismatch: {path}")
        artifact = Path(record["selected_artifact"])
        if (
            not artifact.is_file()
            or file_hash(artifact) != record["selected_artifact_sha256"]
        ):
            raise ValueError(f"selected artifact mismatch: {artifact}")
        required_audits = {
            "pairwise",
            "selected",
            "parrot_feature_contract",
        }
        if record["selected_algorithm"].endswith(
            "reliability_fusion"
        ):
            required_audits.add("vgrf")
        if not required_audits.issubset(record.get("audits", {})):
            raise ValueError(f"required package audits missing: {path}")
        audit_summary = {}
        for name, entry in record["audits"].items():
            audit_path = Path(entry["path"])
            if not audit_path.is_file():
                raise ValueError(f"package audit mismatch: {audit_path}")
            audit = load(audit_path)
            if (
                file_hash(audit_path) != entry["sha256"]
                or audit.get("passes") is not True
            ):
                raise ValueError(f"package audit mismatch: {audit_path}")
            audit_summary[name] = entry["sha256"]
        records.append(
            {
                "package_id": package_id,
                "scenario": record["scenario"],
                "training_seed": record["training_seed"],
                "selected_artifact": record["selected_artifact"],
                "selected_artifact_sha256": record[
                    "selected_artifact_sha256"
                ],
                "selected_artifact_bytes": record[
                    "selected_artifact_bytes"
                ],
                "audit_sha256": audit_summary,
                "package_record_sha256": file_hash(path),
            }
        )
    if observed != set(expected):
        raise ValueError("package record universe is incomplete")
    scenario_counts = {}
    seed_counts = {}
    for record in records:
        scenario_counts[record["scenario"]] = (
            scenario_counts.get(record["scenario"], 0) + 1
        )
        seed = str(record["training_seed"])
        seed_counts[seed] = seed_counts.get(seed, 0) + 1
    if set(scenario_counts.values()) != {2} or seed_counts != {
        "311": 10,
        "313": 10,
    }:
        raise ValueError("package scenario/seed coverage is invalid")
    summary: dict[str, Any] = {
        "schema_version": "strict_v4_ustc_deployment_package_summary_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "selected_algorithm": protocol["selection"]["selected_algorithm"],
        "package_count": len(records),
        "scenario_count": len(scenario_counts),
        "seed_counts": seed_counts,
        "feature_count": protocol["parrot_feature_contract"][
            "feature_count"
        ],
        "all_exact_replay_audits_pass": True,
        "all_parrot_ordered_feature_contracts_pass": True,
        "all_packages_gpu_private": True,
        "formal_model_metrics_admitted": 0,
        "external_execution_admitted": True,
        "external_execution_scope": (
            "read_only_PARROT_and_domain_internal_benign_replay_only"
        ),
        "packages": sorted(records, key=lambda row: row["package_id"]),
        "claim_boundary": {
            "package_completion_does_not_establish_external_sota": True,
            "external_metrics_require_separate_frozen_protocol": True,
        },
    }
    summary["manifest_sha256"] = canonical_hash(summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = load(args.protocol)
    if (
        protocol.get("schema_version")
        != "strict_v4_ustc_deployment_package_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("invalid USTC deployment package protocol")
    summary = summarize(protocol, args.project_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output.parent / "packages_complete").touch()
    print(summary["manifest_sha256"])


if __name__ == "__main__":
    main()
