from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


PILOT_TRAINING_SEED = 331
PILOT_CORRUPTION_SEED = 337
CONFIRMATION_TRAINING_SEEDS = [347, 349, 353]
CONFIRMATION_CORRUPTION_SEEDS = [359, 367, 373]
FAMILIES = [
    "modality_missing",
    "field_missing",
    "row_missing",
    "feature_shuffle",
    "gaussian_drift",
]
FIXED_SEVERITY = {
    "modality_missing": 1.0,
    "field_missing": 0.3,
    "row_missing": 0.3,
    "feature_shuffle": 0.3,
    "gaussian_drift": 0.5,
}


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def select_pilot_scenarios(coverage: Dict[str, Any]) -> Dict[str, List[str]]:
    registry = coverage.get("scenario_registry", {})
    if not isinstance(registry, dict) or len(registry) != 7:
        raise ValueError("seven-suite coverage registry required")
    selected: Dict[str, List[str]] = {}
    for suite, record in sorted(registry.items()):
        scenarios = record.get("scenarios", [])
        if not isinstance(scenarios, list) or len(scenarios) < 2:
            raise ValueError(f"suite has fewer than two scenarios: {suite}")
        ranked = sorted(
            scenarios,
            key=lambda scenario: hashlib.sha256(
                (
                    f"{coverage['manifest_sha256']}:{suite}:{scenario}:"
                    "mdr-caeos-pilot-v1"
                ).encode("utf-8")
            ).hexdigest(),
        )
        selected[suite] = ranked[:2]
    return selected


def failed_suite_threshold_checks(suite_audit: Dict[str, Any]) -> int:
    results = suite_audit.get("suite_results")
    if not isinstance(results, dict):
        raise ValueError("suite audit results are missing")
    observed = 0
    failed = 0
    for family in FAMILIES:
        suites = results.get(family)
        if not isinstance(suites, dict) or len(suites) != 7:
            raise ValueError(f"invalid suite results for {family}")
        for metrics in suites.values():
            if not isinstance(metrics, dict):
                raise ValueError("invalid suite metric result")
            for record in metrics.values():
                if not isinstance(record, dict) or not record.get("thresholded"):
                    continue
                observed += 1
                failed += int(record.get("passes") is not True)
    if observed != 175:
        raise ValueError("suite audit must contain 175 thresholded checks")
    return failed


def create_design(
    coverage: Dict[str, Any],
    corruption_protocol: Dict[str, Any],
    suite_audit: Dict[str, Any],
    *,
    input_file_sha256: Dict[str, str],
    implementation_sha256: Dict[str, str],
    result_count_at_freeze: int,
) -> Dict[str, Any]:
    if (
        coverage.get("schema_version") != "strict_v4_coverage_manifest_v2"
        or coverage.get("manifest_sha256") != canonical_hash(coverage)
    ):
        raise ValueError("invalid coverage manifest")
    if (
        corruption_protocol.get("schema_version")
        != "strict_v4_postselection_corruption_protocol_v1"
        or corruption_protocol.get("manifest_sha256")
        != canonical_hash(corruption_protocol)
    ):
        raise ValueError("invalid corruption protocol")
    if corruption_protocol.get("coverage_manifest_sha256") != coverage["manifest_sha256"]:
        raise ValueError("coverage binding mismatch")
    if suite_audit.get("schema_version") != "strict_v4_postselection_corruption_suite_gate_audit_v1":
        raise ValueError("invalid suite audit")
    if suite_audit.get("validation", {}).get("passes") is not True:
        raise ValueError("suite audit validation must pass")
    if (
        suite_audit.get("passes") is not False
        or suite_audit.get("all_175_suite_threshold_checks_pass") is not False
    ):
        raise ValueError("MDR design requires the formal negative suite result")
    if int(result_count_at_freeze) != 0:
        raise ValueError("MDR design must freeze before candidate results")
    if set(corruption_protocol["full102_confirmation"]["corruption_families"]) != set(FAMILIES):
        raise ValueError("five-family corruption identity mismatch")
    if corruption_protocol["full102_confirmation"]["fixed_severity"] != FIXED_SEVERITY:
        raise ValueError("frozen corruption severity mismatch")
    thresholds = corruption_protocol[
        "confirmatory_graceful_degradation_gate"
    ]["maximum_mean_degradation"]
    formal_failure_count = failed_suite_threshold_checks(suite_audit)
    pilot = select_pilot_scenarios(coverage)
    used_seeds = {
        PILOT_TRAINING_SEED,
        PILOT_CORRUPTION_SEED,
        *CONFIRMATION_TRAINING_SEEDS,
        *CONFIRMATION_CORRUPTION_SEEDS,
    }
    if len(used_seeds) != 8 or min(used_seeds) <= 317:
        raise ValueError("MDR seeds must be distinct and newer than prior seed317")

    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_caeos_design_v1",
        "status": "frozen_before_candidate_results",
        "algorithm": "mdr_caeos_v1",
        "motivation": {
            "formal_suite_failures": formal_failure_count,
            "seed7_results_are_development_diagnosis_only": True,
            "no_seed7_weight_threshold_or_suite_route_search": True,
        },
        "input_manifest_sha256": {
            "coverage": coverage["manifest_sha256"],
            "corruption_protocol": corruption_protocol["manifest_sha256"],
            "suite_audit": suite_audit["manifest_sha256"],
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": implementation_sha256,
        "mechanism": {
            "clean_path": "frozen Pairwise CAEOS",
            "robust_path": (
                "same Pairwise pipeline with five-family structured augmentation "
                "on known training rows"
            ),
            "training_augmentation_weight_grid": [0.125, 0.25, 0.5],
            "training_sample_fraction": 0.25,
            "family_severities": FIXED_SEVERITY,
            "feature_shuffle_training_constraint": "within_known_class_only",
            "weight_selection": (
                "global over all 14 pilot scenarios using known-validation "
                "clean-tolerance and corrupted minimax Macro-F1 only"
            ),
            "health_gate": {
                "signals": [
                    "validation_calibrated missing mask",
                    "maximum local conflict",
                    "clean-vs-robust Jensen-Shannon disagreement",
                ],
                "quantile": 0.99,
                "unknown_or_test_labels_used": False,
            },
            "risk_scale": (
                "known-validation empirical quantile map from robust/missing "
                "risk to clean Pairwise risk"
            ),
            "inactive_path_exactly_clean": True,
            "threshold_source": "clean Pairwise known-validation only",
        },
        "pilot": {
            "training_seed": PILOT_TRAINING_SEED,
            "corruption_seed": PILOT_CORRUPTION_SEED,
            "scenarios": pilot,
            "scenario_count": 14,
            "conditions": ["clean", *FAMILIES],
            "expected_evaluations": 14 * 6,
            "development_labels_used_for_gate_evaluation_only": True,
            "expansion_gate": {
                "all_14_scenarios_complete": True,
                "clean_known_macro_f1_mean_degradation_maximum": 0.01,
                "clean_known_macro_f1_worst_degradation_maximum": 0.03,
                "all_175_suite_metric_thresholds_reapplied_to_pilot_means": True,
                "failed_suite_checks_maximum": 50,
                "must_reduce_modality_missing_failures": True,
                "must_reduce_gaussian_drift_failures": True,
                "no_family_metric_worse_than_pairwise_by_more_than": 0.02,
            },
        },
        "reserved_confirmation": {
            "training_seeds": CONFIRMATION_TRAINING_SEEDS,
            "corruption_seeds": CONFIRMATION_CORRUPTION_SEEDS,
            "training_and_corruption_seeds_are_paired_by_position": True,
            "scenario_count": 102,
            "conditions": ["clean", *FAMILIES],
            "expected_evaluations": 102 * 3 * 6,
            "all_175_suite_threshold_checks_must_pass": True,
            "aggregate_family_gate_must_pass": True,
            "known_f1_clean_noninferiority_required": True,
            "confirmation_seeds_not_used_for_weight_selection": True,
        },
        "thresholds": thresholds,
        "execution_boundary": {
            "execution_admitted": False,
            "missing_before_execution": [
                "pilot execution protocol",
                "resumable runner",
                "independent summarizer and auditor",
                "resource-idle watcher",
            ],
            "no_training_started_by_design_freeze": True,
        },
        "claim_policy": {
            "pilot_success_does_not_establish_sota": True,
            "full_confirmation_failure_retains_pairwise_incumbent": True,
            "full_confirmation_success_still_requires_external_and_system_evidence": True,
            "no_suite_selection_or_threshold_relaxation": True,
        },
        "candidate_result_count_at_freeze": 0,
    }
    if value["motivation"]["formal_suite_failures"] != 79:
        raise ValueError("unexpected formal suite failure count")
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--corruption-protocol", type=Path, required=True)
    parser.add_argument("--suite-audit", type=Path, required=True)
    parser.add_argument("--structured-module", type=Path, required=True)
    parser.add_argument("--fusion-module", type=Path, required=True)
    parser.add_argument("--trainer", type=Path, required=True)
    parser.add_argument("--evaluator", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result_count = (
        sum(1 for _ in args.result_root.rglob("evaluation.json"))
        if args.result_root.exists()
        else 0
    )
    inputs = {
        "coverage": file_hash(args.coverage),
        "corruption_protocol": file_hash(args.corruption_protocol),
        "suite_audit": file_hash(args.suite_audit),
    }
    implementations = {
        "structured_module": file_hash(args.structured_module),
        "fusion_module": file_hash(args.fusion_module),
        "trainer": file_hash(args.trainer),
        "evaluator": file_hash(args.evaluator),
        "design_creator": file_hash(Path(__file__)),
    }
    value = create_design(
        load(args.coverage),
        load(args.corruption_protocol),
        load(args.suite_audit),
        input_file_sha256=inputs,
        implementation_sha256=implementations,
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
