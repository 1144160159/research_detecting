from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


PILOT_TRAINING_SEED = 607
PILOT_AUGMENTATION_SEED = 613
PILOT_CORRUPTION_SEED = 617
CONFIRMATION_TRAINING_SEEDS = [647, 653, 659]
CONFIRMATION_CORRUPTION_SEEDS = [661, 673, 677]
FIXED_AUGMENTATION_WEIGHT = 0.5
FAMILIES = [
    "modality_missing",
    "field_missing",
    "row_missing",
    "feature_shuffle",
    "gaussian_drift",
]


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def select_new_pilot_scenarios(
    coverage: Dict[str, Any],
    mdr_design: Dict[str, Any],
) -> Dict[str, List[str]]:
    registry = coverage.get("scenario_registry", {})
    excluded = {
        (suite, scenario)
        for suite, scenarios in mdr_design["pilot"]["scenarios"].items()
        for scenario in scenarios
    }
    selected: Dict[str, List[str]] = {}
    for suite, record in sorted(registry.items()):
        scenarios = record.get("scenarios", [])
        ranked = sorted(
            (
                str(scenario)
                for scenario in scenarios
                if (suite, str(scenario)) not in excluded
            ),
            key=lambda scenario: hashlib.sha256(
                (
                    f"{coverage['manifest_sha256']}:{suite}:{scenario}:"
                    "csr-caeos-pilot-v1"
                ).encode("utf-8")
            ).hexdigest(),
        )
        if len(ranked) < 2:
            raise ValueError(f"not enough unused scenarios for {suite}")
        selected[suite] = ranked[:2]
    if len(selected) != 7:
        raise ValueError("seven-suite coverage registry required")
    return selected


def create_design(
    coverage: Dict[str, Any],
    mdr_design: Dict[str, Any],
    rejection: Dict[str, Any],
    diagnosis: Dict[str, Any],
    final_selection: Dict[str, Any],
    *,
    input_file_sha256: Dict[str, str],
    implementation_sha256: Dict[str, str],
    result_count_at_freeze: int,
) -> Dict[str, Any]:
    if (
        coverage.get("schema_version") != "strict_v4_coverage_manifest_v2"
        or coverage.get("manifest_sha256") != canonical_hash(coverage)
    ):
        raise ValueError("canonical coverage manifest required")
    if (
        mdr_design.get("schema_version") != "strict_v4_mdr_caeos_design_v2"
        or mdr_design.get("manifest_sha256") != canonical_hash(mdr_design)
    ):
        raise ValueError("canonical MDR v2 design required")
    if (
        rejection.get("schema_version")
        != "strict_v4_mdr_caeos_weight_rejection_v1"
        or rejection.get("manifest_sha256") != canonical_hash(rejection)
        or rejection.get("design_manifest_sha256")
        != mdr_design["manifest_sha256"]
        or rejection.get("selected_weight") is not None
        or rejection.get("test_evaluations_generated") != 0
    ):
        raise ValueError("canonical zero-test MDR rejection required")
    if (
        diagnosis.get("schema_version")
        != "strict_v4_mdr_caeos_known_validation_failure_diagnosis_v1"
        or diagnosis.get("manifest_sha256") != canonical_hash(diagnosis)
        or diagnosis.get("weight_rejection_manifest_sha256")
        != rejection["manifest_sha256"]
        or diagnosis.get("interpretation_boundary", {}).get(
            "test_arrays_read"
        )
        != []
        or diagnosis.get("interpretation_boundary", {}).get(
            "diagnosis_can_revive_or_reselect_mdr"
        )
        is not False
    ):
        raise ValueError("canonical known-validation-only diagnosis required")
    if (
        final_selection.get("manifest_sha256")
        != canonical_hash(final_selection)
        or final_selection.get("selected_algorithm") != "caeos_pairwise"
        or final_selection.get("mdr_confirmation_passes") is not False
        or final_selection.get("comprehensive_sota_confirmed") is not False
    ):
        raise ValueError("canonical Pairwise fallback selection required")
    if int(result_count_at_freeze) != 0:
        raise ValueError("CSR design must freeze before candidate results")

    diagnosed = {
        float(row["weight"]): row for row in diagnosis["weights"]
    }
    fixed = diagnosed.get(FIXED_AUGMENTATION_WEIGHT)
    if (
        fixed is None
        or fixed.get("routed_clean_tolerance_passes") is not True
        or float(fixed["routed_clean_delta_mean"]) >= 0.0
    ):
        raise ValueError("expected diagnostic boundary is absent")
    scenarios = select_new_pilot_scenarios(coverage, mdr_design)
    used_seeds = {
        PILOT_TRAINING_SEED,
        PILOT_AUGMENTATION_SEED,
        PILOT_CORRUPTION_SEED,
        *CONFIRMATION_TRAINING_SEEDS,
        *CONFIRMATION_CORRUPTION_SEEDS,
    }
    if len(used_seeds) != 9 or min(used_seeds) <= 600:
        raise ValueError("CSR seeds must be distinct and newer than MDR")

    value: Dict[str, Any] = {
        "schema_version": "strict_v4_csr_caeos_design_v1",
        "status": "frozen_before_candidate_results",
        "algorithm": "csr_caeos_v1",
        "name": "Conformal Safe Risk Routing CAEOS",
        "input_manifest_sha256": {
            "coverage": coverage["manifest_sha256"],
            "mdr_design": mdr_design["manifest_sha256"],
            "mdr_rejection": rejection["manifest_sha256"],
            "known_validation_diagnosis": diagnosis["manifest_sha256"],
            "final_selection": final_selection["manifest_sha256"],
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": implementation_sha256,
        "motivation": {
            "mdr_rejection_remains_final": True,
            "mdr_test_evaluations_used": 0,
            "diagnosis_test_arrays_used": 0,
            "observed_mdr_selection_mismatch": (
                "robust submodel failed clean tolerance while the final "
                "routed system satisfied the same clean tolerance"
            ),
            "new_candidate_is_not_mdr_reselection": True,
        },
        "mechanism": {
            "clean_path": "frozen Pairwise CAEOS",
            "robust_path": (
                "single structured-augmentation runtime with fixed weight"
            ),
            "fixed_augmentation_weight": FIXED_AUGMENTATION_WEIGHT,
            "weight_grid_or_post_result_search": False,
            "classification_prediction": "always exact clean Pairwise",
            "classification_probability": "always exact clean Pairwise",
            "routing_changes": "unknown-risk score only",
            "health_signals": [
                "explicit modality missingness",
                "maximum clean local conflict",
                "clean-vs-robust Jensen-Shannon disagreement",
            ],
            "health_boundary": (
                "maximum on a known-validation calibration partition"
            ),
            "finite_sample_interpretation": (
                "under exchangeability, a maximum threshold has next-sample "
                "false-activation bound 1/(n_calibration+1)"
            ),
            "active_risk": (
                "max(clean risk, known-validation quantile-mapped robust or "
                "missing-aware risk)"
            ),
            "inactive_prediction_probability_risk_exact": True,
            "risk_uplift_is_monotone": True,
            "unknown_or_test_labels_used_for_routing": False,
        },
        "development": {
            "training_seed": PILOT_TRAINING_SEED,
            "augmentation_seed": PILOT_AUGMENTATION_SEED,
            "corruption_seed": PILOT_CORRUPTION_SEED,
            "scenarios": scenarios,
            "scenario_count": 14,
            "overlap_with_mdr_pilot_scenarios": 0,
            "conditions": ["clean", *FAMILIES],
            "expected_evaluations": 84,
            "selection_unit": "final routed system, never robust submodel",
            "clean_gate": {
                "prediction_array_equal_pairwise": True,
                "probability_max_absolute_difference": 0.0,
                "nonmissing_risk_max_absolute_difference": 1e-12,
                "conflict_or_disagreement_activation_on_calibration": 0.0,
                "known_macro_f1_mean_degradation_maximum": 0.0,
                "known_macro_f1_worst_degradation_maximum": 0.0,
            },
            "robustness_gate": {
                "metrics": [
                    "unknown_auroc",
                    "unknown_aupr",
                    "unknown_fpr95",
                    "oscr",
                ],
                "overall_directed_mean_strictly_positive": True,
                "suite_nonnegative_count_minimum": 5,
                "each_family_metric_regression_maximum": 0.02,
                "modality_missing_and_gaussian_drift_must_improve": True,
                "known_macro_f1_exact_pairwise_by_construction": True,
            },
        },
        "reserved_confirmation": {
            "training_seeds": CONFIRMATION_TRAINING_SEEDS,
            "corruption_seeds": CONFIRMATION_CORRUPTION_SEEDS,
            "scenario_count": 102,
            "conditions": ["clean", *FAMILIES],
            "expected_evaluations": 102 * 3 * 6,
            "development_seeds_not_reused": True,
            "all_175_suite_threshold_checks_must_pass": True,
            "clean_prediction_and_probability_exact_pairwise": True,
            "inactive_risk_exact_pairwise": True,
            "unknown_or_test_selection": False,
            "bootstrap_iterations": 10000,
        },
        "execution_boundary": {
            "execution_admitted": False,
            "missing_before_execution": [
                "runtime integration and capture",
                "canonical pilot execution protocol",
                "resumable runner",
                "independent summarizer and auditor",
                "resource-idle watcher",
            ],
            "no_training_started_by_design_freeze": True,
        },
        "claim_policy": {
            "design_or_pilot_success_does_not_establish_sota": True,
            "failed_pilot_or_confirmation_retains_pairwise": True,
            "full_confirmation_success_still_requires_external_safety_and_efficiency": (
                True
            ),
            "no_metric_suite_or_component_cherry_picking": True,
        },
        "candidate_result_count_at_freeze": 0,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--mdr-design", type=Path, required=True)
    parser.add_argument("--mdr-rejection", type=Path, required=True)
    parser.add_argument("--diagnosis", type=Path, required=True)
    parser.add_argument("--final-selection", type=Path, required=True)
    parser.add_argument("--routing-module", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result_count = (
        sum(1 for _ in args.result_root.rglob("evaluation.json"))
        if args.result_root.exists()
        else 0
    )
    input_paths = {
        "coverage": args.coverage,
        "mdr_design": args.mdr_design,
        "mdr_rejection": args.mdr_rejection,
        "diagnosis": args.diagnosis,
        "final_selection": args.final_selection,
    }
    value = create_design(
        load_json(args.coverage),
        load_json(args.mdr_design),
        load_json(args.mdr_rejection),
        load_json(args.diagnosis),
        load_json(args.final_selection),
        input_file_sha256={
            name: file_hash(path) for name, path in input_paths.items()
        },
        implementation_sha256={
            "routing_module": file_hash(args.routing_module),
            "design_creator": file_hash(Path(__file__)),
        },
        result_count_at_freeze=result_count,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
