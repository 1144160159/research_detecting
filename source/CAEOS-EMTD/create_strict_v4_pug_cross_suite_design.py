from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


PUG_DESIGN_MANIFEST_SHA256 = (
    "dd5339d86af37455b3abf2febf9e0ae3675557d97ad80f590f735aae682241e6"
)
PUG_DESIGN_FILE_SHA256 = (
    "18551cb1caec615145e8a0cf6ee55f69b3bdc506c9c7267658c46a10d1bbd3c2"
)
PUG_PROTOCOL_MANIFEST_SHA256 = (
    "9f6e38e819b1d3a00c6ef527c83bc9be26f9252d18668e6f7cd4d5fa51869665"
)
PUG_PROTOCOL_FILE_SHA256 = (
    "3a5dcb527092ac759343671f19ce839166e905491c3fe48ee21f0e6fb921fdba"
)
KRC_PROTOCOL_MANIFEST_SHA256 = (
    "1504cae7d0407eabf267e2d6a08ddfe12a0797d687801c584223b77afbaf7101"
)
KRC_PROTOCOL_FILE_SHA256 = (
    "00cca15e11302692a33373c3261089d0b9fed0fbc1c5bd965cfb6fa8abfe4b8f"
)
SEEDS = [269, 271, 277]
SUITE_SCENARIO_COUNTS = {
    "cic_iot2023": 32,
    "cic_ton_iot": 9,
    "cicids2017": 14,
    "edge_iiot": 14,
    "nf_cse": 14,
    "nf_unsw": 9,
    "ustc_tfc2016": 10,
}
MAX_PER_CLASS = {
    "cic_iot2023": 1000,
    "cic_ton_iot": 1000,
    "cicids2017": 5000,
    "edge_iiot": 1000,
    "nf_cse": 1000,
    "nf_unsw": 5000,
    "ustc_tfc2016": 3000,
}
FORMAL_OUTPUTS = (
    "activation.json",
    "execution_protocol.json",
    "summary.json",
    "audit.json",
    "execution_complete",
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: dict[str, Any],
    path: Path,
    *,
    schema: str,
    expected_manifest: str,
    expected_file: str,
) -> None:
    if (
        value.get("schema_version") != schema
        or value.get("manifest_sha256") != expected_manifest
        or value.get("manifest_sha256") != canonical_hash(value)
        or file_hash(path) != expected_file
    ):
        raise ValueError(f"canonical input drifted: {path}")


def frozen_universe(krc_protocol: dict[str, Any]) -> dict[str, list[str]]:
    registry = krc_protocol.get("source_registry", [])
    if not isinstance(registry, list) or len(registry) != 102:
        raise ValueError("KRC source registry must contain 102 scenarios")
    by_suite = {suite: [] for suite in SUITE_SCENARIO_COUNTS}
    identities: set[tuple[str, str]] = set()
    for row in registry:
        suite = row.get("suite")
        scenario = row.get("scenario")
        identity = (suite, scenario)
        if (
            suite not in by_suite
            or not isinstance(scenario, str)
            or not scenario
            or identity in identities
        ):
            raise ValueError("invalid or duplicate KRC scenario identity")
        identities.add(identity)
        by_suite[suite].append(scenario)
    observed = {
        suite: len(scenarios) for suite, scenarios in by_suite.items()
    }
    if observed != SUITE_SCENARIO_COUNTS:
        raise ValueError("strict-v4 seven-suite universe drifted")
    return {
        suite: sorted(scenarios) for suite, scenarios in sorted(by_suite.items())
    }


def formal_output_counts(result_root: Path) -> dict[str, int]:
    counts = {
        name: int((result_root / name).is_file()) for name in FORMAL_OUTPUTS
    }
    counts["tasks"] = sum(
        1 for path in result_root.glob("tasks/*.json") if path.is_file()
    )
    return counts


def create_design(
    *,
    pug_design: dict[str, Any],
    pug_protocol: dict[str, Any],
    krc_protocol: dict[str, Any],
    input_file_sha256: dict[str, str],
    implementation_sha256: dict[str, str],
    observed_output_counts: dict[str, int],
) -> dict[str, Any]:
    if any(observed_output_counts.values()):
        raise ValueError("PUG cross-suite outputs must be zero at design freeze")
    pilot = pug_design.get("fresh_pilot", {})
    freshness = pug_design.get("freshness", {})
    if (
        pug_design.get("state")
        != "frozen_before_candidate_integration_and_fresh_seed_execution"
        or pug_design.get("candidate", {}).get("method") != "caeos_pug"
        or pilot.get("paired_task_count") != 18
        or pilot.get("seeds") != [283, 293, 307]
        or freshness.get("comp_reserved_cross_suite_seeds_excluded") != SEEDS
    ):
        raise ValueError("frozen PUG pilot design boundary required")
    if (
        pug_protocol.get("state") != "frozen_before_fresh_seed_execution"
        or len(pug_protocol.get("tasks", [])) != 18
        or pug_protocol.get("claim_boundary", {}).get(
            "passing_pilot_requires_fresh_cross_suite_confirmation"
        )
        is not True
        or pug_protocol.get("admission_gate", {}).get(
            "passing_requires_fresh_cross_suite_confirmation"
        )
        is not True
    ):
        raise ValueError("frozen PUG execution protocol boundary required")
    confirmation = krc_protocol.get("confirmation", {})
    if (
        confirmation.get("full_scenario_count") != 102
        or confirmation.get("capture_count") != 306
        or confirmation.get("full_task_count") != 306
    ):
        raise ValueError("frozen KRC full102 boundary required")

    suites = frozen_universe(krc_protocol)
    tasks = [
        {"suite": suite, "scenario": scenario, "seed": seed}
        for suite, scenarios in suites.items()
        for scenario in scenarios
        for seed in SEEDS
    ]
    if len(tasks) != 306 or len(
        {(row["suite"], row["scenario"], row["seed"]) for row in tasks}
    ) != 306:
        raise ValueError("PUG cross-suite universe must contain 306 tasks")

    design: dict[str, Any] = {
        "schema_version": "strict_v4_pug_cross_suite_confirmation_design_v1",
        "state": (
            "conditionally_frozen_before_pilot_completion_and_"
            "cross_suite_outputs"
        ),
        "candidate": {
            **pug_protocol["candidate"],
            "task_level_route": "caeos_pug_or_exact_pairwise_passthrough",
        },
        "activation_gate": {
            "required_pilot_schema": "strict_v4_pug_confirmation_v1",
            "required_pilot_protocol_manifest_sha256": (
                pug_protocol["manifest_sha256"]
            ),
            "pilot_task_count": 18,
            "pilot_decision_passes_must_equal": True,
            "pilot_selected_method_must_equal": "caeos_pug",
            "pilot_cross_suite_execution_admitted_must_equal": False,
            "negative_pilot_action": (
                "retain_upstream_incumbent_and_write_canonical_not_required"
            ),
            "execution_protocol_must_not_exist_before_positive_activation": True,
        },
        "confirmation_universe": {
            "suite_count": len(suites),
            "scenario_count": sum(len(values) for values in suites.values()),
            "scenario_count_by_suite": {
                suite: len(values) for suite, values in suites.items()
            },
            "scenarios_by_suite": suites,
            "fresh_seeds": SEEDS,
            "paired_task_count": len(tasks),
            "expected_pairwise_pug_runs": len(tasks),
            "expected_fresh_opendetect_runs": len(tasks),
            "tasks": tasks,
        },
        "execution_controls": {
            **pug_protocol["execution"],
            "max_per_class_by_suite": MAX_PER_CLASS,
            "split_strategy": "capture_grouped",
            "cache_must_be_seed_specific": True,
            "candidate_run_contains_exact_pairwise_reference": True,
            "opendetect_must_be_fresh_on_each_identical_split": True,
            "split_fingerprints_and_test_arrays_must_match_within_pair": True,
            "unknown_or_test_labels_used_for_fit_selection_or_threshold": False,
        },
        "primary_statistics": {
            "aggregation": "seed_mean_then_equal_suite_mean",
            "paired_unit": "suite_scenario_seed",
            "bootstrap_blocks": "suite_then_scenario",
            "bootstrap_repetitions": 10000,
            "wilcoxon_holm_is_secondary": True,
            "fpr95_direction": "lower_is_better",
        },
        "admission_gate": {
            "candidate_vs_pairwise": {
                "equal_suite_mean_fpr95_oriented_improvement_minimum": 0.02,
                "equal_suite_mean_auroc_oriented_nonregression": 0.0,
                "equal_suite_mean_aupr_oriented_nonregression": 0.0,
                "equal_suite_mean_oscr_oriented_nonregression": 0.0,
                "known_macro_f1_absolute_tolerance": 1e-12,
                "per_task_fpr95_regression_tolerance": 0.02,
                "per_task_aupr_regression_tolerance": 0.02,
                "suite_fpr95_positive_count_minimum": 5,
                "worst_suite_fpr95_oriented_regression_tolerance": 0.01,
            },
            "candidate_vs_opendetect": {
                "equal_suite_mean_fpr95_noninferiority_margin": 0.01,
                "equal_suite_mean_auroc_oriented_nonregression": 0.0,
                "equal_suite_mean_aupr_oriented_nonregression": 0.0,
                "equal_suite_mean_oscr_oriented_nonregression": 0.0,
                "equal_suite_mean_known_f1_oriented_nonregression": 0.0,
                "per_metric_nonnegative_suite_count_minimum": 5,
            },
            "route_coverage": {
                "pug_selected_scenario_count_minimum": 18,
                "pug_selected_suite_count_minimum": 4,
            },
            "integrity": {
                "complete_candidate_tasks": 306,
                "complete_opendetect_tasks": 306,
                "artifact_hashes_and_independent_metric_recomputation": True,
                "zero_failed_or_orphan_tasks": True,
                "all_checks_required": True,
            },
        },
        "selection_policy": {
            "all_admission_checks_pass": (
                "caeos_pug_becomes_provisional_self_algorithm_incumbent"
            ),
            "any_admission_check_fails": "retain_krc_rrc_or_pairwise_incumbent",
            "suite_specific_cherry_picking_forbidden": True,
            "passing_confirmation_still_requires": [
                "external_malicious_confirmation",
                "parrot_external_benign_safety",
                "deployment_equivalence",
                "same_hardware_efficiency",
                "integrated_comprehensive_sota_audit",
            ],
        },
        "required_future_implementation": [
            "activation_decision_writer",
            "execution_protocol_creator",
            "cross_suite_runner",
            "cross_suite_evaluator",
            "cross_suite_summary",
            "independent_auditor",
            "conditional_watcher",
        ],
        "execution_admitted_at_freeze": False,
        "formal_result_counts_at_freeze": {
            key: int(value)
            for key, value in sorted(observed_output_counts.items())
        },
        "input_manifest_sha256": {
            "pug_design": pug_design["manifest_sha256"],
            "pug_execution_protocol": pug_protocol["manifest_sha256"],
            "krc_protocol": krc_protocol["manifest_sha256"],
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": implementation_sha256,
        "claim_boundary": {
            "pilot_partial_metrics_are_not_read": True,
            "pilot_pass_alone_does_not_select_candidate": True,
            "cross_suite_pass_alone_does_not_authorize_comprehensive_sota": True,
            "upstream_incumbent_remains_until_full_confirmation_passes": True,
            "no_dataset_metric_or_evidence_splicing": True,
        },
    }
    design["manifest_sha256"] = canonical_hash(design)
    return design


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--pug-design",
        type=Path,
        default=Path("results/strict_v4_pug_design_v1/design_protocol.json"),
    )
    parser.add_argument(
        "--pug-protocol",
        type=Path,
        default=Path(
            "results/strict_v4_pug_confirmation_v1/execution_protocol.json"
        ),
    )
    parser.add_argument(
        "--krc-protocol",
        type=Path,
        default=Path(
            "results/strict_v4_krc_csr_confirmation_v1/protocol.json"
        ),
    )
    parser.add_argument(
        "--result-root",
        type=Path,
        default=Path(
            "results/strict_v4_pug_cross_suite_confirmation_v1"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/strict_v4_pug_cross_suite_design_v1/design.json"
        ),
    )
    args = parser.parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    paths = {
        "pug_design": resolve(args.pug_design),
        "pug_execution_protocol": resolve(args.pug_protocol),
        "krc_protocol": resolve(args.krc_protocol),
    }
    values = {key: load(path) for key, path in paths.items()}
    require_canonical(
        values["pug_design"],
        paths["pug_design"],
        schema="strict_v4_pug_design_protocol_v1",
        expected_manifest=PUG_DESIGN_MANIFEST_SHA256,
        expected_file=PUG_DESIGN_FILE_SHA256,
    )
    require_canonical(
        values["pug_execution_protocol"],
        paths["pug_execution_protocol"],
        schema="strict_v4_pug_execution_protocol_v1",
        expected_manifest=PUG_PROTOCOL_MANIFEST_SHA256,
        expected_file=PUG_PROTOCOL_FILE_SHA256,
    )
    require_canonical(
        values["krc_protocol"],
        paths["krc_protocol"],
        schema="strict_v4_krc_csr_confirmation_protocol_v1",
        expected_manifest=KRC_PROTOCOL_MANIFEST_SHA256,
        expected_file=KRC_PROTOCOL_FILE_SHA256,
    )
    output = resolve(args.output)
    result_root = resolve(args.result_root)
    design = create_design(
        pug_design=values["pug_design"],
        pug_protocol=values["pug_execution_protocol"],
        krc_protocol=values["krc_protocol"],
        input_file_sha256={
            key: file_hash(path) for key, path in paths.items()
        },
        implementation_sha256={
            Path(__file__).name: file_hash(Path(__file__).resolve())
        },
        observed_output_counts=formal_output_counts(result_root),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as destination:
        destination.write(json.dumps(design, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "output": str(output),
                "task_count": len(
                    design["confirmation_universe"]["tasks"]
                ),
                "manifest_sha256": design["manifest_sha256"],
                "file_sha256": file_hash(output),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
