from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


SCHEMA = "strict_v4_selected_system_preconfirmation_design_v1"
ALGORITHMS = (
    "caeos_pairwise",
    "krc_csr_caeos_v1",
    "rrc_csr_caeos_v1",
    "caeos_pug",
)
MAIN_METHODS = (
    "mlp_msp",
    "mlp_energy",
    "mlp_openmax",
    "mlp_knn",
    "mlp_vim",
    "mahalanobis_pp",
    "opendetect",
)
CORRUPTION_FAMILIES = (
    "modality_missing",
    "field_missing",
    "row_missing",
    "feature_shuffle",
    "gaussian_drift",
)
IMPLEMENTATION_FILES = (
    "create_strict_v4_selected_system_preconfirmation_design.py",
    "write_strict_v4_selected_system_preconfirmation_activation.py",
    "audit_strict_v4_selected_system_preconfirmation_design.py",
)
FUTURE_IMPLEMENTATION_FILES = (
    "create_strict_v4_selected_system_preconfirmation_protocol.py",
    "run_strict_v4_selected_system_preconfirmation.py",
    "evaluate_strict_v4_selected_system_preconfirmation.py",
    "summarize_strict_v4_selected_system_preconfirmation.py",
    "audit_strict_v4_selected_system_preconfirmation.py",
    "watch_strict_v4_selected_system_preconfirmation.py",
)
FORMAL_OUTPUTS = (
    "activation.json",
    "protocol.json",
    "summary.json",
    "audit.json",
    "execution_complete.json",
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: dict[str, Any], schema: str, label: str
) -> None:
    if (
        value.get("schema_version") != schema
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError(f"canonical {label} required")


def formal_output_counts(result_root: Path) -> dict[str, int]:
    return {
        name: int((result_root / name).is_file())
        for name in FORMAL_OUTPUTS
    }


def build_design(
    *,
    project_root: Path,
    classic_protocol_path: Path,
    krc_protocol_path: Path,
    corruption_protocol_path: Path,
    comparative_protocol_path: Path,
    adapter_design_path: Path,
    result_root: Path,
) -> dict[str, Any]:
    paths = {
        "classic_main_protocol": classic_protocol_path.resolve(),
        "krc_source_protocol": krc_protocol_path.resolve(),
        "absolute_corruption_protocol": corruption_protocol_path.resolve(),
        "comparative_corruption_protocol": comparative_protocol_path.resolve(),
        "selected_system_adapter_design": adapter_design_path.resolve(),
    }
    classic = load(paths["classic_main_protocol"])
    krc = load(paths["krc_source_protocol"])
    corruption = load(paths["absolute_corruption_protocol"])
    comparative = load(paths["comparative_corruption_protocol"])
    adapter = load(paths["selected_system_adapter_design"])
    require_canonical(
        classic,
        "strict_v4_classical_main_baseline_protocol_v1",
        "classic main protocol",
    )
    require_canonical(
        krc, "strict_v4_krc_csr_confirmation_protocol_v1", "KRC source protocol"
    )
    require_canonical(
        corruption,
        "strict_v4_postselection_corruption_suite_gate_protocol_v1",
        "absolute corruption protocol",
    )
    require_canonical(
        comparative,
        "strict_v4_comparative_corruption_protocol_v2",
        "comparative corruption protocol",
    )
    require_canonical(
        adapter,
        "strict_v4_selected_system_downstream_adapter_design_v1",
        "selected-system adapter design",
    )

    baselines = classic.get("main_table", {}).get("baselines", [])
    methods = tuple(row.get("method") for row in baselines)
    tasks = krc.get("confirmation", {}).get("tasks", [])
    identities = {
        (
            str(task.get("suite")),
            str(task.get("scenario")),
            int(task.get("training_seed", -1)),
        )
        for task in tasks
    }
    scenario_identities = {(suite, scenario) for suite, scenario, _ in identities}
    seeds = sorted({seed for _, _, seed in identities})
    families = tuple(corruption.get("corruption_families", []))
    comparative_families = tuple(
        comparative.get("corruption_conditions", {}).get("families", [])
    )
    if (
        methods != MAIN_METHODS
        or len(tasks) != 306
        or len(identities) != 306
        or len(scenario_identities) != 102
        or seeds != [647, 653, 659]
        or families != CORRUPTION_FAMILIES
        or comparative_families != CORRUPTION_FAMILIES
        or adapter.get("activation", {}).get("allowed_selected_algorithms")
        != list(ALGORITHMS)
    ):
        raise ValueError("selected-system preconfirmation universe drifted")

    counts = formal_output_counts(result_root)
    if any(counts.values()):
        raise ValueError("preconfirmation design requires zero formal outputs")
    implementation = {
        name: file_hash(project_root / name) for name in IMPLEMENTATION_FILES
    }
    result: dict[str, Any] = {
        "schema_version": SCHEMA,
        "state": (
            "frozen_before_final_self_algorithm_selection_and_"
            "preconfirmation_results"
        ),
        "purpose": (
            "Replace Pairwise-only clean and corruption blockers with fresh "
            "evidence for the finally selected self algorithm before downstream "
            "activation."
        ),
        "allowed_selected_algorithms": list(ALGORITHMS),
        "source_manifest_sha256": {
            name: load(path)["manifest_sha256"] for name, path in paths.items()
        },
        "source_file_sha256": {
            name: file_hash(path) for name, path in paths.items()
        },
        "implementation_sha256": implementation,
        "required_future_implementation": list(FUTURE_IMPLEMENTATION_FILES),
        "universe": {
            "suite_count": 7,
            "scenario_count": 102,
            "training_seeds": seeds,
            "source_task_count": 306,
            "selected_candidate_capture_count": 306,
            "fresh_opendetect_capture_count": 306,
            "classic_main_baseline_count": 7,
            "classic_main_methods": list(MAIN_METHODS),
            "corruption_family_count": 5,
            "corruption_families": list(CORRUPTION_FAMILIES),
            "paired_corruption_record_count": 1530,
        },
        "clean_main_baseline_contract": {
            "same_source_csv_config_seed_and_split": True,
            "six_non_opendetect_reports_from_same_clean_training_run": (
                list(MAIN_METHODS[:-1])
            ),
            "opendetect_requires_fresh_training_per_source_task": True,
            "selected_runtime_identity_bound_to_final_selection": True,
            "metrics": [
                "known_macro_f1",
                "unknown_auroc",
                "unknown_aupr",
                "unknown_fpr95",
                "oscr",
            ],
            "strict_five_metric_dominance_required_against_all_seven": True,
        },
        "corruption_contract": {
            "families": list(CORRUPTION_FAMILIES),
            "fixed_severity": comparative["corruption_conditions"][
                "fixed_severity"
            ],
            "modality_selection_rule": comparative["corruption_conditions"][
                "modality_selection_rule"
            ],
            "same_condition_rng_and_test_identity_for_candidate_and_opendetect": (
                True
            ),
            "absolute_maximum_mean_degradation": corruption[
                "maximum_mean_degradation"
            ],
            "absolute_gate_preserves_all_family_suite_metric_checks": True,
            "comparative_gate": comparative["comparative_robustness_gate"],
            "no_threshold_tuning_or_condition_selection": True,
        },
        "aggregation_contract": {
            "order": [
                "training_seed",
                "scenario",
                "dataset_suite",
                "seven_suite_equal_weight",
            ],
            "three_training_seeds_averaged_before_scenario_aggregation": True,
            "scenario_complete_before_suite_aggregation": True,
            "bootstrap_repetitions": 10000,
            "bootstrap_unit": "suite_and_scenario_block",
        },
        "activation_contract": {
            "final_self_algorithm_selection_required": True,
            "activation_is_not_effect_or_downstream_execution": True,
            "preconfirmation_completion_required_before_selected_system_activation": (
                True
            ),
        },
        "formal_output_counts_at_freeze": counts,
        "claim_boundary": {
            "design_is_not_execution_or_effect": True,
            "pairwise_evidence_cannot_substitute_for_nonpairwise_final_algorithm": (
                True
            ),
            "negative_preconfirmation_is_a_valid_scientific_outcome": True,
            "comprehensive_sota_authorized_at_freeze": False,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--classic-protocol", type=Path, required=True)
    parser.add_argument("--krc-protocol", type=Path, required=True)
    parser.add_argument("--corruption-protocol", type=Path, required=True)
    parser.add_argument("--comparative-protocol", type=Path, required=True)
    parser.add_argument("--adapter-design", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_design(
        project_root=args.project_root.resolve(),
        classic_protocol_path=args.classic_protocol,
        krc_protocol_path=args.krc_protocol,
        corruption_protocol_path=args.corruption_protocol,
        comparative_protocol_path=args.comparative_protocol,
        adapter_design_path=args.adapter_design,
        result_root=args.result_root.resolve(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open(
        "w", encoding="utf-8", newline="\n"
    ) as handle:
        handle.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "manifest_sha256": result["manifest_sha256"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
