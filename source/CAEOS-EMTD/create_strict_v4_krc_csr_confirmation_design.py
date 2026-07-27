from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from certify_krc_csr import load
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_caeos_confirmation_protocol import (
    build_source_records,
)


def counts(run_root: Path, result_root: Path) -> Dict[str, int]:
    return {
        "capture": len(list(run_root.rglob("capture_manifest.json")))
        if run_root.exists()
        else 0,
        "evaluation": len(list(run_root.rglob("evaluation.json")))
        if run_root.exists()
        else 0,
        "summary": int((result_root / "summary.json").exists()),
        "audit": int((result_root / "audit.json").exists()),
        "completion": int((result_root / "confirmation_complete").exists()),
    }


def create(
    development_protocol: Dict[str, Any],
    development_summary: Dict[str, Any],
    development_audit: Dict[str, Any],
    comparative: Dict[str, Any],
    source_records: list[Dict[str, Any]],
    observed_counts: Dict[str, int],
    *,
    input_file_sha256: Dict[str, str],
) -> Dict[str, Any]:
    if (
        development_protocol.get("schema_version")
        != "strict_v4_krc_csr_development_protocol_v1"
        or development_protocol.get("manifest_sha256")
        != canonical_hash(development_protocol)
        or development_summary.get("schema_version")
        != "strict_v4_krc_csr_pilot_summary_v1"
        or development_summary.get("manifest_sha256")
        != canonical_hash(development_summary)
        or development_summary.get("passes") is not True
        or development_audit.get("schema_version")
        != "strict_v4_krc_csr_pilot_audit_v1"
        or development_audit.get("manifest_sha256")
        != canonical_hash(development_audit)
        or development_audit.get("passes") is not True
        or comparative.get("schema_version")
        != "strict_v4_comparative_corruption_protocol_v2"
        or comparative.get("manifest_sha256") != canonical_hash(comparative)
    ):
        raise ValueError("canonical positive KRC development evidence required")
    if any(observed_counts.values()):
        raise ValueError("KRC confirmation design requires zero outputs")
    source_identities = {
        (str(record["suite"]), str(record["scenario"]))
        for record in source_records
    }
    if len(source_records) != 102 or len(source_identities) != 102:
        raise ValueError("KRC confirmation source universe must contain 102 tasks")
    development_scenarios = {
        tuple(key.split("/", 1))
        for key in development_protocol[
            "source_capture_manifest_file_sha256"
        ]
    }
    if len(development_scenarios) != 14:
        raise ValueError("KRC development scenario universe must contain 14 tasks")
    primary = source_identities - development_scenarios
    if len(primary) != 88:
        raise ValueError("KRC primary confirmation universe must contain 88 tasks")
    reserved = development_protocol["reserved_confirmation"]
    training_seeds = [int(value) for value in reserved["training_seeds"]]
    corruption_seeds = [
        int(value) for value in reserved["corruption_seeds"]
    ]
    tasks = [
        {
            "suite": record["suite"],
            "scenario": record["scenario"],
            "training_seed": training_seed,
            "corruption_seed": corruption_seed,
            "primary_heldout_scenario": (
                (record["suite"], record["scenario"]) in primary
            ),
        }
        for record in source_records
        for training_seed, corruption_seed in zip(
            training_seeds, corruption_seeds
        )
    ]
    if len(tasks) != 306 or sum(
        task["primary_heldout_scenario"] for task in tasks
    ) != 264:
        raise ValueError("KRC confirmation task count mismatch")
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_csr_confirmation_design_v1",
        "status": "frozen_before_execution_implementation_and_results",
        "execution_admitted": False,
        "algorithm": "krc_csr_caeos_v1",
        "development_protocol_manifest_sha256": development_protocol[
            "manifest_sha256"
        ],
        "development_summary_manifest_sha256": development_summary[
            "manifest_sha256"
        ],
        "development_audit_manifest_sha256": development_audit[
            "manifest_sha256"
        ],
        "comparative_protocol_manifest_sha256": comparative[
            "manifest_sha256"
        ],
        "coverage_manifest_sha256": comparative[
            "coverage_manifest_sha256"
        ],
        "input_file_sha256": input_file_sha256,
        "source_registry": source_records,
        "source_registry_count": len(source_records),
        "development_scenario_identities": sorted(
            "/".join(identity) for identity in development_scenarios
        ),
        "primary_scenario_identities": sorted(
            "/".join(identity) for identity in primary
        ),
        "confirmation": {
            "training_seeds": training_seeds,
            "corruption_seeds": corruption_seeds,
            "seeds_paired_by_position": True,
            "full_task_count": len(tasks),
            "primary_task_count": 264,
            "full_scenario_count": 102,
            "primary_scenario_count": 88,
            "conditions": [
                "clean",
                "modality_missing",
                "field_missing",
                "row_missing",
                "feature_shuffle",
                "gaussian_drift",
            ],
            "capture_count": 306,
            "evaluation_count": 1836,
            "fit_count": 612,
            "fixed_augmentation_weight": 0.5,
            "augmentation_seed_equals_training_seed": True,
            "tasks": tasks,
        },
        "known_only_certificate": development_protocol[
            "known_only_certificate"
        ],
        "primary_gate": {
            "enabled_scenario_count_minimum": int(
                reserved["enabled_scenario_count_minimum"]
            ),
            "enabled_suite_count_minimum": int(
                reserved["enabled_suite_count_minimum"]
            ),
            "known_macro_f1_exact_pairwise_all_conditions": True,
            "overall_directed_means_strictly_positive": True,
            "suite_nonnegative_count_minimum_each_metric": 5,
            "each_family_metric_regression_maximum": 0.02,
            "modality_missing_composite_improves": True,
            "gaussian_drift_composite_improves": True,
            "inactive_prediction_probability_risk_exact_pairwise_when_disabled": True,
            "bootstrap_primary_composite_lower_bound_strictly_positive": True,
            "bootstrap_replicates": 10000,
            "bootstrap_seed": 20260726,
        },
        "secondary_full102_report": {
            "required": True,
            "does_not_override_primary_failure": True,
        },
        "implementation_requirements_before_execution": [
            "real KRC runtime wrapper",
            "306 capture runner with known-only certificate",
            "1836-condition evaluator",
            "primary-88 and full102 summarizer",
            "independent capture/evaluation/statistical auditor",
            "resumable resource-aware coordinator",
        ],
        "output_counts_at_freeze": observed_counts,
        "selection_rule": {
            "if_all_primary_gates_pass": (
                "authorize KRC external, safety, and efficiency confirmation"
            ),
            "otherwise": "retain caeos_pairwise",
            "no_suite_metric_component_or_seed_splicing": True,
        },
        "claim_boundary": {
            "design_freeze_does_not_authorize_execution": True,
            "confirmation_success_does_not_alone_establish_sota": True,
            "external_malicious_parrot_and_efficiency_still_required": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--development-protocol", type=Path, required=True)
    parser.add_argument("--development-summary", type=Path, required=True)
    parser.add_argument("--development-audit", type=Path, required=True)
    parser.add_argument("--comparative-protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "development_protocol": args.development_protocol.resolve(),
        "development_summary": args.development_summary.resolve(),
        "development_audit": args.development_audit.resolve(),
        "comparative_protocol": args.comparative_protocol.resolve(),
    }
    documents = {name: load(path) for name, path in paths.items()}
    value = create(
        documents["development_protocol"],
        documents["development_summary"],
        documents["development_audit"],
        documents["comparative_protocol"],
        build_source_records(
            documents["comparative_protocol"],
            args.project_root.resolve(),
        ),
        counts(args.run_root.resolve(), args.result_root.resolve()),
        input_file_sha256={
            name: file_hash(path) for name, path in paths.items()
        },
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
