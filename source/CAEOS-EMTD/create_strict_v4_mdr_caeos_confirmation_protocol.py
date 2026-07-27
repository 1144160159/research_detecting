from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_caeos_pilot_execution_protocol import option_value
from select_mdr_caeos_weight import load


def validate_positive_pilot(
    design: Dict[str, Any],
    pilot_protocol: Dict[str, Any],
    selection: Dict[str, Any],
    summary: Dict[str, Any],
    audit: Dict[str, Any],
) -> None:
    if (
        design.get("schema_version") != "strict_v4_mdr_caeos_design_v2"
        or design.get("manifest_sha256") != canonical_hash(design)
    ):
        raise ValueError("canonical MDR v2 design required")
    if (
        pilot_protocol.get("schema_version")
        != "strict_v4_mdr_caeos_pilot_execution_protocol_v1"
        or pilot_protocol.get("manifest_sha256")
        != canonical_hash(pilot_protocol)
        or pilot_protocol.get("design_manifest_sha256")
        != design["manifest_sha256"]
    ):
        raise ValueError("invalid MDR pilot protocol")
    if (
        selection.get("schema_version")
        != "strict_v4_mdr_caeos_weight_selection_v1"
        or selection.get("manifest_sha256") != canonical_hash(selection)
        or selection.get("design_manifest_sha256")
        != design["manifest_sha256"]
        or selection.get("unknown_or_test_labels_used") is not False
    ):
        raise ValueError("invalid MDR pilot weight selection")
    if (
        summary.get("schema_version")
        != "strict_v4_mdr_caeos_pilot_summary_v1"
        or summary.get("manifest_sha256") != canonical_hash(summary)
        or summary.get("design_manifest_sha256")
        != design["manifest_sha256"]
        or summary.get("weight_selection_manifest_sha256")
        != selection["manifest_sha256"]
        or summary.get("decision", {}).get(
            "expand_to_full102_confirmation"
        )
        is not True
    ):
        raise ValueError("positive canonical MDR pilot summary required")
    if (
        audit.get("schema_version")
        != "strict_v4_mdr_caeos_pilot_audit_v1"
        or audit.get("manifest_sha256") != canonical_hash(audit)
        or audit.get("passes") is not True
        or audit.get("summary_manifest_sha256")
        != summary["manifest_sha256"]
        or audit.get("selection_manifest_sha256")
        != selection["manifest_sha256"]
    ):
        raise ValueError("passing canonical MDR pilot audit required")


def build_source_records(
    comparative: Dict[str, Any], project_root: Path
) -> List[Dict[str, Any]]:
    seed137 = [
        record
        for record in comparative["source_registry"]
        if int(record["seed"]) == 137
    ]
    identities = {
        (str(record["suite"]), str(record["scenario"]))
        for record in seed137
    }
    if len(seed137) != 102 or len(identities) != 102:
        raise ValueError("comparative registry must provide 102 unique seed137 sources")
    records = []
    for source in sorted(
        seed137, key=lambda item: (item["suite"], item["scenario"])
    ):
        root = Path(source["candidate_root"])
        provenance_path = root / "provenance.json"
        provenance = load(provenance_path)
        command = list(provenance["command"])
        if len(command) < 3 or Path(command[1]).name != "train_hybrid_open_set.py":
            raise ValueError("MDR confirmation source must use Pairwise trainer")
        arguments = command[2:]
        if (
            int(option_value(arguments, "--seed")) != 137
            or option_value(arguments, "--test-corruption-kind") != "none"
        ):
            raise ValueError("MDR confirmation requires clean seed137 sources")
        csv_path = Path(option_value(arguments, "--csv"))
        config_path = Path(option_value(arguments, "--config"))
        if not config_path.is_absolute():
            config_path = project_root / config_path
        records.append(
            {
                "suite": str(source["suite"]),
                "scenario": str(source["scenario"]),
                "source_seed": 137,
                "candidate_source_root": str(root),
                "candidate_source_provenance_sha256": file_hash(
                    provenance_path
                ),
                "source_split_fingerprint": source["split_fingerprint"],
                "csv": str(csv_path),
                "csv_sha256": file_hash(csv_path),
                "config": str(config_path),
                "config_sha256": file_hash(config_path),
                "base_trainer_arguments": arguments,
                "source_csv_rows_reused_without_test_effect_selection": True,
            }
        )
    return records


def create_protocol(
    design: Dict[str, Any],
    pilot_protocol: Dict[str, Any],
    selection: Dict[str, Any],
    summary: Dict[str, Any],
    audit: Dict[str, Any],
    comparative: Dict[str, Any],
    *,
    input_file_sha256: Dict[str, str],
    source_records: List[Dict[str, Any]],
    implementation: Dict[str, str],
    implementation_sha256: Dict[str, str],
    observed_counts: Dict[str, int],
) -> Dict[str, Any]:
    validate_positive_pilot(
        design, pilot_protocol, selection, summary, audit
    )
    if (
        comparative.get("schema_version")
        != "strict_v4_comparative_corruption_protocol_v2"
        or comparative.get("manifest_sha256")
        != canonical_hash(comparative)
        or comparative.get("coverage_manifest_sha256")
        != design["input_manifest_sha256"]["coverage"]
    ):
        raise ValueError("canonical coverage-matched comparative protocol required")
    if any(int(value) != 0 for value in observed_counts.values()):
        raise ValueError("MDR confirmation protocol requires zero outputs")
    source_identities = {
        (record["suite"], record["scenario"]) for record in source_records
    }
    if len(source_records) != 102 or len(source_identities) != 102:
        raise ValueError("MDR confirmation source universe must contain 102 tasks")
    if set(implementation) != set(implementation_sha256):
        raise ValueError("MDR confirmation implementation keys differ")
    reserved = design["reserved_confirmation"]
    training_seeds = [int(value) for value in reserved["training_seeds"]]
    corruption_seeds = [
        int(value) for value in reserved["corruption_seeds"]
    ]
    if (
        len(training_seeds) != 3
        or len(corruption_seeds) != 3
        or len(set(training_seeds + corruption_seeds)) != 6
    ):
        raise ValueError("MDR confirmation requires three disjoint seed pairs")
    tasks = []
    for source in source_records:
        for training_seed, corruption_seed in zip(
            training_seeds, corruption_seeds
        ):
            tasks.append(
                {
                    "suite": source["suite"],
                    "scenario": source["scenario"],
                    "training_seed": training_seed,
                    "corruption_seed": corruption_seed,
                }
            )
    if len(tasks) != 306 or len(
        {
            (
                task["suite"],
                task["scenario"],
                task["training_seed"],
            )
            for task in tasks
        }
    ) != 306:
        raise ValueError("MDR confirmation task universe must contain 306 tasks")
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_caeos_confirmation_protocol_v1",
        "status": (
            "frozen_after_positive_pilot_before_reserved_confirmation_results"
        ),
        "execution_admitted": True,
        "algorithm": "mdr_caeos_v1",
        "design_manifest_sha256": design["manifest_sha256"],
        "pilot_protocol_manifest_sha256": pilot_protocol[
            "manifest_sha256"
        ],
        "pilot_selection_manifest_sha256": selection["manifest_sha256"],
        "pilot_summary_manifest_sha256": summary["manifest_sha256"],
        "pilot_audit_manifest_sha256": audit["manifest_sha256"],
        "comparative_protocol_manifest_sha256": comparative[
            "manifest_sha256"
        ],
        "coverage_manifest_sha256": comparative[
            "coverage_manifest_sha256"
        ],
        "input_file_sha256": input_file_sha256,
        "selected_augmentation_weight": float(
            selection["selected_weight"]
        ),
        "weight_is_frozen_from_known_validation_pilot": True,
        "source_registry": source_records,
        "source_registry_count": len(source_records),
        "confirmation": {
            "training_seeds": training_seeds,
            "corruption_seeds": corruption_seeds,
            "seeds_paired_by_position": True,
            "task_count": len(tasks),
            "conditions": list(design["reserved_confirmation"]["conditions"]),
            "fixed_severity": dict(
                design["mechanism"]["family_severities"]
            ),
            "capture_count": 306,
            "evaluation_count": 1836,
            "fit_count": 612,
            "selected_runtime_reused_across_six_conditions": True,
            "training_sample_fraction": float(
                design["mechanism"]["training_sample_fraction"]
            ),
            "health_quantile": float(
                design["mechanism"]["health_gate"]["quantile"]
            ),
            "augmentation_seed_equals_training_seed": True,
            "outer_workers": 4,
            "trainer_jobs": 8,
            "tasks": tasks,
        },
        "gate": {
            "all_1836_evaluations_complete": True,
            "all_175_suite_threshold_checks_must_pass": True,
            "aggregate_family_thresholds_must_pass": True,
            "clean_known_macro_f1_mean_degradation_maximum": float(
                design["pilot"]["expansion_gate"][
                    "clean_known_macro_f1_mean_degradation_maximum"
                ]
            ),
            "clean_known_macro_f1_worst_degradation_maximum": float(
                design["pilot"]["expansion_gate"][
                    "clean_known_macro_f1_worst_degradation_maximum"
                ]
            ),
            "inactive_path_exactly_pairwise": True,
            "no_unknown_or_test_selection": True,
            "primary_composite_bootstrap_lower_bound_strictly_positive": True,
        },
        "statistics": {
            "bootstrap_replicates": 10000,
            "bootstrap_seed": 20260724,
            "unit": "scenario_after_mean_over_three_reserved_seed_pairs",
            "primary_endpoint": (
                "mean_pairwise_minus_mdr_degradation_advantage_over_"
                "five_families_and_five_thresholded_metrics"
            ),
        },
        "thresholds": dict(design["thresholds"]),
        "selection_rule": {
            "if_all_confirmation_gates_pass": "select_mdr_caeos_v1",
            "otherwise": "retain_caeos_pairwise",
            "no_suite_metric_or_component_splicing": True,
        },
        "leakage_policy": {
            "known_training_for_model_fit_only": True,
            "pilot_known_validation_fixed_the_single_global_weight": True,
            "confirmation_known_validation_for_health_and_risk_calibration_only": True,
            "unknown_or_test_labels_for_fit_selection_or_routing": False,
            "test_labels_for_final_confirmation_evaluation_only": True,
        },
        "implementation": implementation,
        "implementation_sha256": implementation_sha256,
        "output_counts_at_freeze": observed_counts,
        "claim_boundary": {
            "confirmation_success_requires_external_efficiency_and_system_gates": True,
            "confirmation_failure_retains_pairwise": True,
            "pilot_and_confirmation_are_disjoint_by_training_and_corruption_seed": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--pilot-protocol", type=Path, required=True)
    parser.add_argument("--pilot-selection", type=Path, required=True)
    parser.add_argument("--pilot-summary", type=Path, required=True)
    parser.add_argument("--pilot-audit", type=Path, required=True)
    parser.add_argument("--comparative-protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--implementation", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    paths = {
        "design": args.design.resolve(),
        "pilot_protocol": args.pilot_protocol.resolve(),
        "pilot_selection": args.pilot_selection.resolve(),
        "pilot_summary": args.pilot_summary.resolve(),
        "pilot_audit": args.pilot_audit.resolve(),
        "comparative_protocol": args.comparative_protocol.resolve(),
    }
    documents = {name: load(path) for name, path in paths.items()}
    implementation = {}
    implementation_sha256 = {}
    for item in args.implementation:
        name, relative = item.split("=", 1)
        implementation[name] = relative
        implementation_sha256[name] = file_hash(project_root / relative)
    run_root = args.run_root.resolve()
    result_root = args.result_root.resolve()
    observed = {
        "capture_manifests": (
            sum(1 for _ in run_root.rglob("capture_manifest.json"))
            if run_root.exists()
            else 0
        ),
        "evaluations": (
            sum(1 for _ in run_root.rglob("evaluation.json"))
            if run_root.exists()
            else 0
        ),
        "summary": int((result_root / "summary.json").exists()),
        "audit": int((result_root / "audit.json").exists()),
        "complete": int((result_root / "confirmation_complete").exists()),
    }
    value = create_protocol(
        documents["design"],
        documents["pilot_protocol"],
        documents["pilot_selection"],
        documents["pilot_summary"],
        documents["pilot_audit"],
        documents["comparative_protocol"],
        input_file_sha256={
            name: file_hash(path) for name, path in paths.items()
        },
        source_records=build_source_records(
            documents["comparative_protocol"], project_root
        ),
        implementation=implementation,
        implementation_sha256=implementation_sha256,
        observed_counts=observed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
