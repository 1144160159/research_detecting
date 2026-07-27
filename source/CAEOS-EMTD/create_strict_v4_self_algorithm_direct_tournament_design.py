from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


SEEDS = (809, 811, 821)
FORMAL_OUTPUTS = (
    "protocol.json",
    "summary.json",
    "audit.json",
    "execution_complete.json",
)


def load_canonical(path: Path, schema: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        not isinstance(value, dict)
        or value.get("schema_version") != schema
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError(f"canonical {schema} required: {path}")
    return value


def output_counts(result_root: Path) -> dict[str, int]:
    return {
        name: int((result_root / name).is_file())
        for name in FORMAL_OUTPUTS
    } | {
        "task_records": (
            len(list((result_root / "tasks").rglob("*.json")))
            if (result_root / "tasks").is_dir()
            else 0
        )
    }


def build_design(
    *,
    krc_protocol: dict[str, Any],
    rrc_implementation: dict[str, Any],
    pug_cross_suite_design: dict[str, Any],
    input_file_sha256: dict[str, str],
    creator_sha256: str,
    observed_output_counts: dict[str, int],
) -> dict[str, Any]:
    universe = pug_cross_suite_design.get("confirmation_universe", {})
    scenarios = universe.get("scenarios_by_suite", {})
    if (
        universe.get("suite_count") != 7
        or universe.get("scenario_count") != 102
        or sum(len(values) for values in scenarios.values()) != 102
        or len(scenarios) != 7
    ):
        raise ValueError("frozen seven-suite 102-scenario universe required")
    if any(observed_output_counts.values()):
        raise ValueError("tournament design must freeze at zero formal output")
    if (
        krc_protocol.get("execution_admitted") is not True
        or rrc_implementation.get("execution_admitted") is not False
        or rrc_implementation.get("state")
        != "full_execution_chain_implemented_waiting_terminal_krc_decision"
    ):
        raise ValueError("KRC/RRC conditional execution boundary drifted")

    tasks = [
        {
            "suite": suite,
            "scenario": scenario,
            "seed": seed,
            "identity": f"{suite}/{scenario}/seed{seed}",
        }
        for suite, suite_scenarios in scenarios.items()
        for scenario in suite_scenarios
        for seed in SEEDS
    ]
    result: dict[str, Any] = {
        "schema_version": (
            "strict_v4_self_algorithm_direct_tournament_design_v1"
        ),
        "state": "conditionally_frozen_before_dual_positive_outcome",
        "activation": {
            "required_upstream_selection": [
                "krc_csr_caeos_v1",
                "rrc_csr_caeos_v1",
            ],
            "required_challenger_selection": "caeos_pug",
            "requires_both_independent_confirmations_to_pass": True,
            "pairwise_upstream_makes_tournament_not_required": True,
            "single_positive_candidate_is_selected_without_tournament": True,
            "dual_positive_without_tournament_is_not_final_selection": True,
        },
        "candidate_slots": {
            "incumbent": {
                "resolved_only_after_krc_rrc_terminal": True,
                "allowed_algorithms": [
                    "krc_csr_caeos_v1",
                    "rrc_csr_caeos_v1",
                ],
            },
            "challenger": {
                "algorithm": "caeos_pug",
                "requires_positive_cross_suite_audit": True,
            },
            "embedded_reference": "caeos_pairwise",
        },
        "confirmation_universe": {
            "suite_count": 7,
            "scenario_count": 102,
            "seeds": list(SEEDS),
            "paired_task_count": len(tasks),
            "expected_incumbent_runs": len(tasks),
            "expected_challenger_runs": len(tasks),
            "conditions": [
                "clean",
                "modality_missing",
                "gaussian_drift",
            ],
            "expected_paired_evaluations": len(tasks) * 3,
            "scenarios_by_suite": scenarios,
            "tasks": tasks,
        },
        "resource_contract": {
            "single_coordinator": True,
            "outer_workers": 4,
            "model_jobs": 8,
            "maximum_concurrent_fits": 4,
            "must_not_overlap_krc_rrc_pug_or_downstream_training": True,
        },
        "statistics": {
            "aggregation_order": [
                "condition_within_seed",
                "seed_within_scenario",
                "scenario_within_suite",
                "equal_weight_across_seven_suites",
            ],
            "metrics": [
                "known_macro_f1",
                "unknown_auroc",
                "unknown_aupr",
                "unknown_fpr95",
                "oscr",
            ],
            "fpr95_is_lower_better": True,
            "bootstrap_repetitions": 10000,
            "bootstrap_blocks": "suite_then_scenario",
            "bootstrap_is_reporting_only": False,
            "test_labels_are_used_only_for_frozen_final_evaluation": True,
        },
        "challenger_admission_gate": {
            "known_macro_f1_equal_suite_mean_gain_minimum": -0.002,
            "unknown_metric_positive_count_minimum": 3,
            "four_unknown_metric_oriented_mean_gain_minimum": 0.005,
            "four_unknown_metric_bootstrap_lower_95_minimum": 0.0,
            "nonnegative_suite_count_minimum": 5,
            "worst_suite_four_unknown_metric_mean_gain_minimum": -0.02,
            "clean_and_each_corruption_condition_required": True,
            "integrity_and_selection_isolation_required": True,
            "all_checks_required": True,
        },
        "selection_rule": {
            "all_challenger_gates_pass": "select_caeos_pug",
            "otherwise": "retain_krc_or_rrc_incumbent",
            "no_post_result_threshold_seed_suite_or_metric_selection": True,
            "result_is_final_only_after_independent_audit": True,
        },
        "formal_output_counts_at_freeze": observed_output_counts,
        "execution_admitted_at_freeze": False,
        "required_future_implementation": [
            "conditional_activation_writer",
            "execution_protocol_creator",
            "paired_candidate_runner",
            "single_task_evaluator",
            "equal_suite_summarizer",
            "independent_auditor",
            "resource_safe_watcher",
        ],
        "input_manifest_sha256": {
            "krc_protocol": krc_protocol["manifest_sha256"],
            "rrc_execution_implementation": rrc_implementation[
                "manifest_sha256"
            ],
            "pug_cross_suite_design": pug_cross_suite_design[
                "manifest_sha256"
            ],
        },
        "input_file_sha256": dict(sorted(input_file_sha256.items())),
        "implementation_sha256": {
            "create_strict_v4_self_algorithm_direct_tournament_design.py": (
                creator_sha256
            )
        },
        "claim_boundary": {
            "design_is_not_execution_or_effect": True,
            "pug_cross_suite_pass_is_only_provisional_against_enhanced_incumbent": (
                True
            ),
            "tournament_success_does_not_authorize_comprehensive_sota": True,
            "external_malicious_benign_safety_and_efficiency_remain_required": (
                True
            ),
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--krc-protocol", type=Path, required=True)
    parser.add_argument("--rrc-implementation", type=Path, required=True)
    parser.add_argument("--pug-cross-suite-design", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    paths = {
        "krc_protocol": resolve(args.krc_protocol),
        "rrc_execution_implementation": resolve(args.rrc_implementation),
        "pug_cross_suite_design": resolve(args.pug_cross_suite_design),
    }
    result_root = resolve(args.result_root)
    output = resolve(args.output)
    creator = Path(__file__).resolve()
    design = build_design(
        krc_protocol=load_canonical(
            paths["krc_protocol"],
            "strict_v4_krc_csr_confirmation_protocol_v1",
        ),
        rrc_implementation=load_canonical(
            paths["rrc_execution_implementation"],
            "strict_v4_rrc_csr_execution_implementation_protocol_v1",
        ),
        pug_cross_suite_design=load_canonical(
            paths["pug_cross_suite_design"],
            "strict_v4_pug_cross_suite_confirmation_design_v1",
        ),
        input_file_sha256={
            path.relative_to(root).as_posix(): file_hash(path)
            for path in paths.values()
        },
        creator_sha256=file_hash(creator),
        observed_output_counts=output_counts(result_root),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and json.loads(output.read_text(encoding="utf-8")) != design:
        raise ValueError("existing tournament design is immutable")
    if not output.exists():
        temporary = output.with_suffix(".json.tmp")
        with temporary.open(
            "w", encoding="utf-8", newline="\n"
        ) as destination:
            destination.write(
                json.dumps(design, indent=2, sort_keys=True) + "\n"
            )
        temporary.replace(output)
    print(f"manifest_sha256={design['manifest_sha256']}")
    print(f"file_sha256={file_hash(output)}")


if __name__ == "__main__":
    main()
