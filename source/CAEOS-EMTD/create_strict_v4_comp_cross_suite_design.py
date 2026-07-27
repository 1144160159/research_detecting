from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


DIAGNOSIS_FILE_SHA256 = (
    "1bfed984c44a9e95cb2e2f2b0a3d75dab779c2fcff2e94f6da7355a56c3a2da8"
)
DIAGNOSIS_MANIFEST_SHA256 = (
    "b1e1aa709fc3307cd5d7dbca3b4f495f0481881270ffb1b8427694a437d76404"
)
PILOT_PROTOCOL_FILE_SHA256 = (
    "00411a25500270d9773d4a63750628bb5c98e23e48c9885aded49e42f8d47720"
)
PILOT_PROTOCOL_MANIFEST_SHA256 = (
    "3486d4e70c5d4a9c694ae93ef2f6af1f8bd0287efcd246c621a78837d2162310"
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


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: dict[str, Any], schema: str, label: str
) -> None:
    if value.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError(f"{label} canonical SHA mismatch")


def frozen_universe(diagnosis: dict[str, Any]) -> dict[str, list[str]]:
    rows = diagnosis.get("scenario_diagnostics")
    if not isinstance(rows, list) or len(rows) != 102:
        raise ValueError("diagnosis must contain exactly 102 scenario rows")
    by_suite: dict[str, list[str]] = {
        suite: [] for suite in SUITE_SCENARIO_COUNTS
    }
    identities: set[tuple[str, str]] = set()
    for row in rows:
        suite = row.get("suite")
        scenario = row.get("scenario")
        seed = row.get("seed")
        if (
            suite not in by_suite
            or not isinstance(scenario, str)
            or not scenario
            or seed != 7
        ):
            raise ValueError("invalid strict-v4 scenario identity")
        identity = (suite, scenario)
        if identity in identities:
            raise ValueError("duplicate strict-v4 scenario identity")
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


def create_design(
    *,
    diagnosis: dict[str, Any],
    pilot_protocol: dict[str, Any],
    input_file_sha256: dict[str, str],
    implementation_sha256: dict[str, str],
    observed_output_counts: dict[str, int],
) -> dict[str, Any]:
    require_canonical(
        diagnosis,
        "strict_v4_pairwise_opendetect_fpr95_tail_audit_v1",
        "Pairwise FPR95 diagnosis",
    )
    require_canonical(
        pilot_protocol,
        "strict_v4_comp_confirmation_protocol_v1",
        "CAEOS-COMP pilot protocol",
    )
    if diagnosis.get("passes") is not True:
        raise ValueError("passing Pairwise diagnosis required")
    pilot_scope = pilot_protocol.get("pilot_scope", {})
    pilot_gate = pilot_protocol.get("admission_gate", {})
    candidate = pilot_protocol.get("candidate", {})
    if (
        pilot_protocol.get("state") != "frozen_before_fresh_seed_execution"
        or int(pilot_scope.get("paired_task_count", -1)) != 18
        or pilot_scope.get("seeds") != [139, 149, 163]
        or pilot_gate.get("passing_pilot_requires_cross_suite_expansion")
        is not True
        or candidate.get("method") != "caeos_comp"
        or candidate.get("unknown_or_test_labels_used_for_routing") is not False
        or candidate.get("unknown_or_test_labels_used_for_threshold") is not False
    ):
        raise ValueError("frozen CAEOS-COMP pilot boundary required")
    if any(int(value) != 0 for value in observed_output_counts.values()):
        raise ValueError("cross-suite design must freeze before result outputs")

    suites = frozen_universe(diagnosis)
    tasks = [
        {"suite": suite, "scenario": scenario, "seed": seed}
        for suite, scenarios in suites.items()
        for scenario in scenarios
        for seed in SEEDS
    ]
    if len(tasks) != 306 or len(
        {(task["suite"], task["scenario"], task["seed"]) for task in tasks}
    ) != 306:
        raise ValueError("full102x3 task universe must contain 306 identities")

    design: dict[str, Any] = {
        "schema_version": (
            "strict_v4_comp_cross_suite_confirmation_design_v1"
        ),
        "state": (
            "conditionally_frozen_before_pilot_completion_and_"
            "cross_suite_outputs"
        ),
        "candidate": candidate,
        "activation_gate": {
            "required_result_schema": "strict_v4_comp_confirmation_v1",
            "required_pilot_protocol_manifest_sha256": (
                PILOT_PROTOCOL_MANIFEST_SHA256
            ),
            "paired_task_count": 18,
            "pilot_decision_passes_must_equal": True,
            "pilot_integrity_validation_must_pass": True,
            "negative_pilot_action": (
                "retain_pairwise_and_write_canonical_not_required"
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
            "expected_pairwise_comp_runs": len(tasks),
            "expected_opendetect_runs": len(tasks),
            "tasks": tasks,
        },
        "execution_controls": {
            "pairwise_risk_selection": (
                "nested_boundary_pairwise_pseudo_unknown_blend"
            ),
            "pairwise_policy_name": (
                "strict_v4_comp_cross_suite_pairwise_v1"
            ),
            "estimators": 80,
            "model_jobs": 8,
            "split_strategy": "capture_grouped",
            "max_per_class_by_suite": MAX_PER_CLASS,
            "cache_must_be_seed_specific": True,
            "candidate_is_score_only_refinement_of_same_pairwise_runtime": True,
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
                "equal_suite_mean_auroc_oriented_nonregression": -0.005,
                "equal_suite_mean_aupr_oriented_nonregression": -0.005,
                "equal_suite_mean_oscr_oriented_nonregression": -0.005,
                "known_macro_f1_absolute_tolerance": 1e-12,
                "per_task_fpr95_regression_tolerance": 0.02,
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
            "integrity": {
                "complete_pairwise_comp_tasks": 306,
                "complete_opendetect_tasks": 306,
                "artifact_hashes_and_independent_metric_recomputation": True,
                "zero_failed_or_orphan_tasks": True,
                "all_checks_required": True,
            },
        },
        "selection_policy": {
            "all_admission_checks_pass": (
                "caeos_comp_becomes_provisional_accuracy_incumbent"
            ),
            "any_admission_check_fails": "retain_pairwise_incumbent",
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
            name: int(value)
            for name, value in sorted(observed_output_counts.items())
        },
        "input_manifest_sha256": {
            "diagnosis": diagnosis["manifest_sha256"],
            "pilot_protocol": pilot_protocol["manifest_sha256"],
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": implementation_sha256,
        "claim_boundary": {
            "pilot_partial_metrics_are_not_read": True,
            "pilot_pass_alone_does_not_select_candidate": True,
            "cross_suite_pass_alone_does_not_authorize_universal_sota": True,
            "pairwise_remains_incumbent_until_full_confirmation_passes": True,
            "no_dataset_metric_or_evidence_splicing": True,
        },
    }
    design["manifest_sha256"] = canonical_hash(design)
    return design


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--diagnosis",
        type=Path,
        default=Path(
            "results/strict_v4_pairwise_opendetect_fpr95_tail_audit_v1/"
            "audit.json"
        ),
    )
    parser.add_argument(
        "--pilot-protocol",
        type=Path,
        default=Path("results/strict_v4_comp_confirmation_v1/protocol.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/strict_v4_comp_cross_suite_confirmation_design_v1/"
            "design_protocol.json"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    diagnosis_path = resolve(args.diagnosis)
    pilot_protocol_path = resolve(args.pilot_protocol)
    if (
        file_hash(diagnosis_path) != DIAGNOSIS_FILE_SHA256
        or file_hash(pilot_protocol_path) != PILOT_PROTOCOL_FILE_SHA256
    ):
        raise ValueError("exact frozen diagnosis and pilot protocol required")
    diagnosis = load(diagnosis_path)
    pilot_protocol = load(pilot_protocol_path)
    if (
        diagnosis.get("manifest_sha256") != DIAGNOSIS_MANIFEST_SHA256
        or pilot_protocol.get("manifest_sha256")
        != PILOT_PROTOCOL_MANIFEST_SHA256
    ):
        raise ValueError("frozen input canonical SHA drifted")

    output = resolve(args.output)
    output_root = output.parent
    observed_output_counts = {
        "activation_decision": len(list(output_root.glob("activation*.json"))),
        "execution_protocol": len(list(output_root.glob("execution*.json"))),
        "task_metrics": len(list(output_root.glob("tasks/**/*.json"))),
        "summary": len(list(output_root.glob("summary*.json"))),
        "audit": len(list(output_root.glob("audit*.json"))),
    }
    implementation_files = [
        Path(__file__).resolve(),
        root / "caeos/continuous_outer_min_p.py",
    ]
    implementation_sha256 = {
        str(path.relative_to(root)): file_hash(path) for path in implementation_files
    }
    design = create_design(
        diagnosis=diagnosis,
        pilot_protocol=pilot_protocol,
        input_file_sha256={
            str(diagnosis_path.relative_to(root)): file_hash(diagnosis_path),
            str(pilot_protocol_path.relative_to(root)): file_hash(
                pilot_protocol_path
            ),
        },
        implementation_sha256=implementation_sha256,
        observed_output_counts=observed_output_counts,
    )
    output_root.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(design, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"manifest_sha256={design['manifest_sha256']}")
    print(f"file_sha256={file_hash(output)}")


if __name__ == "__main__":
    main()
