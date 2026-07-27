from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import numpy as np
from scipy.stats import beta

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


DIRECTED_METRICS = (
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)
FAMILIES = (
    "modality_missing",
    "field_missing",
    "row_missing",
    "feature_shuffle",
    "gaussian_drift",
)
TaskIdentity = Tuple[str, str, int, int]
EvaluationIdentity = Tuple[str, str, int, str]


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def validate_protocol(protocol: Dict[str, Any]) -> None:
    if (
        protocol.get("schema_version")
        != "strict_v4_krc_csr_confirmation_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("execution_admitted") is not True
    ):
        raise ValueError("canonical admitted KRC confirmation protocol required")


def directed_delta(
    candidate: Dict[str, Any],
    pairwise: Dict[str, Any],
    metric: str,
) -> float:
    if metric == "unknown_fpr95":
        return float(pairwise[metric]) - float(candidate[metric])
    return float(candidate[metric]) - float(pairwise[metric])


def clopper_pearson_upper(
    successes: int, trials: int, confidence: float = 0.95
) -> float:
    if not 0 <= successes <= trials or trials <= 0:
        raise ValueError("valid positive binomial counts required")
    if successes == trials:
        return 1.0
    return float(beta.ppf(confidence, successes + 1, trials - successes))


def aggregate(
    rows: List[Dict[str, Any]],
    scenario_identities: Iterable[Tuple[str, str]],
) -> Dict[str, Any]:
    identities = set(scenario_identities)
    selected = [
        row
        for row in rows
        if (row["suite"], row["scenario"]) in identities
    ]
    suites = sorted({suite for suite, _ in identities})
    overall = {}
    suite_means = {}
    family_means = {}
    for metric in DIRECTED_METRICS:
        metric_rows = [
            row for row in selected if row["metric"] == metric
        ]
        overall[metric] = float(
            np.mean([row["directed_delta"] for row in metric_rows])
        )
        suite_means[metric] = {
            suite: float(
                np.mean(
                    [
                        row["directed_delta"]
                        for row in metric_rows
                        if row["suite"] == suite
                    ]
                )
            )
            for suite in suites
        }
        family_means[metric] = {
            family: float(
                np.mean(
                    [
                        row["directed_delta"]
                        for row in metric_rows
                        if row["family"] == family
                    ]
                )
            )
            for family in FAMILIES
        }
    suite_nonnegative = {
        metric: sum(
            value >= -1e-12
            for value in suite_means[metric].values()
        )
        for metric in DIRECTED_METRICS
    }
    family_composite = {
        family: float(
            np.mean(
                [
                    family_means[metric][family]
                    for metric in DIRECTED_METRICS
                ]
            )
        )
        for family in FAMILIES
    }
    scenario_composite = {}
    for suite, scenario in sorted(identities):
        values = [
            row["directed_delta"]
            for row in selected
            if row["suite"] == suite and row["scenario"] == scenario
        ]
        if len(values) != 3 * len(FAMILIES) * len(DIRECTED_METRICS):
            raise ValueError(
                f"incomplete KRC scenario aggregation: {suite}/{scenario}"
            )
        scenario_composite[f"{suite}/{scenario}"] = float(np.mean(values))
    return {
        "scenario_count": len(identities),
        "overall_directed_mean": overall,
        "suite_directed_mean": suite_means,
        "suite_nonnegative_count": suite_nonnegative,
        "family_directed_mean": family_means,
        "family_composite_directed_mean": family_composite,
        "scenario_composite_directed_mean": scenario_composite,
    }


def bootstrap_primary(
    scenario_composite: Dict[str, float],
    *,
    replicates: int,
    seed: int,
) -> Dict[str, Any]:
    by_suite: Dict[str, List[float]] = defaultdict(list)
    for identity, value in scenario_composite.items():
        suite, _ = identity.split("/", 1)
        by_suite[suite].append(float(value))
    if len(by_suite) != 7 or sum(map(len, by_suite.values())) != 88:
        raise ValueError(
            "KRC primary bootstrap requires 88 scenarios in seven suites"
        )
    arrays = {
        suite: np.asarray(values, dtype=np.float64)
        for suite, values in sorted(by_suite.items())
    }
    point = float(
        np.mean([float(values.mean()) for values in arrays.values()])
    )
    rng = np.random.default_rng(int(seed))
    samples = np.empty(int(replicates), dtype=np.float64)
    for index in range(int(replicates)):
        suite_values = []
        for values in arrays.values():
            drawn = rng.integers(0, len(values), size=len(values))
            suite_values.append(float(values[drawn].mean()))
        samples[index] = float(np.mean(suite_values))
    return {
        "unit": "scenario",
        "stratification": "within_suite_then_equal_weight_seven_suites",
        "point_estimate": point,
        "lower_95": float(np.quantile(samples, 0.025)),
        "upper_95": float(np.quantile(samples, 0.975)),
        "replicates": int(replicates),
        "seed": int(seed),
    }


def summarize(
    protocol: Dict[str, Any],
    capture_paths: List[Path],
    evaluation_paths: List[Path],
) -> Dict[str, Any]:
    validate_protocol(protocol)
    tasks = protocol["confirmation"]["tasks"]
    task_map: Dict[TaskIdentity, Dict[str, Any]] = {
        (
            str(task["suite"]),
            str(task["scenario"]),
            int(task["training_seed"]),
            int(task["corruption_seed"]),
        ): task
        for task in tasks
    }
    if len(task_map) != 306:
        raise ValueError("KRC protocol must contain 306 unique tasks")
    seed_to_corruption = {
        int(task["training_seed"]): int(task["corruption_seed"])
        for task in tasks
    }
    expected_capture = {
        (suite, scenario, training_seed)
        for suite, scenario, training_seed, _ in task_map
    }
    captures: Dict[Tuple[str, str, int], Dict[str, Any]] = {}
    capture_hashes = {}
    safety_rows = []
    for path in capture_paths:
        value = load_json(path)
        task = value.get("task", {})
        identity = (
            str(task.get("suite")),
            str(task.get("scenario")),
            int(value.get("training_seed", -1)),
        )
        certificate = value.get("known_only_certificate", {})
        profile = value.get("safety_profile", {})
        if (
            value.get("schema_version")
            != "strict_v4_krc_csr_runtime_capture_v1"
            or value.get("manifest_sha256") != canonical_hash(value)
            or value.get("state") != "complete"
            or value.get("algorithm") != "krc_csr_caeos_v1"
            or value.get("roundtrip", {}).get("passes") is not True
            or float(value.get("weight", -1.0))
            != float(
                protocol["confirmation"]["fixed_augmentation_weight"]
            )
            or value.get(
                "unknown_or_test_labels_used_for_training_selection_or_calibration"
            )
            is not False
            or certificate.get("test_arrays_read") != []
            or certificate.get("unknown_or_test_labels_used") is not False
            or profile.get("test_arrays_read") != []
        ):
            raise ValueError(f"invalid KRC capture: {path}")
        if identity in captures:
            raise ValueError(f"duplicate KRC capture: {identity}")
        captures[identity] = value
        capture_hashes["/".join(map(str, identity))] = file_hash(path)
        safety_count = int(profile["partition"]["safety_count"])
        missing = int(profile["missing_active_count"])
        nonmissing_count = safety_count - missing
        nonmissing_active = int(profile["active_count"]) - missing
        safety_rows.append(
            {
                "suite": identity[0],
                "scenario": identity[1],
                "training_seed": identity[2],
                "certificate_routing_enabled": bool(
                    certificate["routing_enabled"]
                ),
                "nonmissing_count": nonmissing_count,
                "nonmissing_active_count": nonmissing_active,
                "nonmissing_active_rate_one_sided_95pct_upper": (
                    clopper_pearson_upper(
                        nonmissing_active, nonmissing_count
                    )
                ),
                "prediction_array_equal_pairwise": bool(
                    profile["prediction_array_equal_pairwise"]
                ),
                "probability_max_absolute_difference": float(
                    profile["probability_max_absolute_difference"]
                ),
                "inactive_risk_max_absolute_difference": float(
                    profile["inactive_risk_max_absolute_difference"]
                ),
                "clean_delta": float(profile["clean_delta"]),
            }
        )
    if set(captures) != expected_capture:
        raise ValueError(
            "KRC capture universe mismatch: "
            f"missing={len(expected_capture-set(captures))} "
            f"extra={len(set(captures)-expected_capture)}"
        )

    conditions = tuple(protocol["confirmation"]["conditions"])
    expected_evaluation = {
        (suite, scenario, training_seed, condition)
        for suite, scenario, training_seed, _ in task_map
        for condition in conditions
    }
    evaluations: Dict[EvaluationIdentity, Dict[str, Any]] = {}
    evaluation_hashes = {}
    directed_rows = []
    routing_checks = []
    known_f1_exact = []
    leakage_checks = []
    for path in evaluation_paths:
        value = load_json(path)
        identity = (
            str(value.get("suite")),
            str(value.get("scenario")),
            int(value.get("training_seed", -1)),
            str(value.get("condition")),
        )
        corruption_seed = seed_to_corruption.get(identity[2], -2)
        task_identity = (*identity[:3], corruption_seed)
        routing = value.get("routing", {})
        if (
            value.get("schema_version")
            != "strict_v4_krc_csr_confirmation_evaluation_v1"
            or value.get("manifest_sha256") != canonical_hash(value)
            or value.get("protocol_manifest_sha256")
            != protocol["manifest_sha256"]
            or value.get("state") != "complete"
            or task_identity not in task_map
            or int(value.get("corruption_seed", -1)) != corruption_seed
            or bool(value.get("primary_heldout_scenario"))
            != bool(task_map[task_identity]["primary_heldout_scenario"])
        ):
            raise ValueError(f"invalid KRC evaluation: {path}")
        if identity in evaluations:
            raise ValueError(f"duplicate KRC evaluation: {identity}")
        evaluations[identity] = value
        evaluation_hashes["/".join(map(str, identity))] = file_hash(path)
        enabled = bool(value["certificate_routing_enabled"])
        routing_checks.append(
            routing.get("prediction_exactly_pairwise_all_rows") is True
            and routing.get("probability_exactly_pairwise_all_rows") is True
            and routing.get("risk_monotone_not_below_pairwise") is True
            and routing.get("inactive_risk_exactly_pairwise") is True
            and routing.get("disabled_risk_exactly_pairwise_all_rows") is True
            and (
                enabled
                == bool(captures[identity[:3]][
                    "known_only_certificate"
                ]["routing_enabled"])
            )
        )
        leakage_checks.append(
            routing.get("unknown_or_test_labels_used") is False
            and value.get("test_labels_used_for_final_evaluation_only")
            is True
        )
        candidate = value["candidate_report"]
        pairwise = value["pairwise_report"]
        known_f1_exact.append(
            float(candidate["known_macro_f1"])
            == float(pairwise["known_macro_f1"])
        )
        if identity[3] != "clean":
            for metric in DIRECTED_METRICS:
                directed_rows.append(
                    {
                        "suite": identity[0],
                        "scenario": identity[1],
                        "training_seed": identity[2],
                        "family": identity[3],
                        "metric": metric,
                        "directed_delta": directed_delta(
                            candidate, pairwise, metric
                        ),
                    }
                )
    if set(evaluations) != expected_evaluation:
        raise ValueError(
            "KRC evaluation universe mismatch: "
            f"missing={len(expected_evaluation-set(evaluations))} "
            f"extra={len(set(evaluations)-expected_evaluation)}"
        )

    primary = {
        (identity[0], identity[1])
        for identity, task in task_map.items()
        if task["primary_heldout_scenario"]
    }
    full = {
        (identity[0], identity[1]) for identity in task_map
    }
    if len(primary) != 88 or len(full) != 102:
        raise ValueError("KRC primary/full scenario universe mismatch")
    scenario_seeds: Dict[Tuple[str, str], List[bool]] = defaultdict(list)
    for identity, value in captures.items():
        scenario_seeds[identity[:2]].append(
            bool(value["known_only_certificate"]["routing_enabled"])
        )
    enabled_primary = {
        identity
        for identity in primary
        if len(scenario_seeds[identity]) == 3
        and all(scenario_seeds[identity])
    }
    enabled_primary_suites = {suite for suite, _ in enabled_primary}
    primary_stats = aggregate(directed_rows, primary)
    full_stats = aggregate(directed_rows, full)
    gate = protocol["primary_gate"]
    bootstrap = bootstrap_primary(
        primary_stats["scenario_composite_directed_mean"],
        replicates=int(gate["bootstrap_replicates"]),
        seed=int(gate["bootstrap_seed"]),
    )
    safety_limit = float(
        protocol.get("clean_safety_gate", {}).get(
            "nonmissing_activation_rate_one_sided_95pct_upper_maximum",
            0.01,
        )
    )
    checks = {
        "all_306_captures_complete": len(captures) == 306,
        "all_1836_evaluations_complete": len(evaluations) == 1836,
        "all_runtime_roundtrips_pass": all(
            value["roundtrip"]["passes"] is True
            for value in captures.values()
        ),
        "known_only_certificate_has_no_test_access": all(
            value["known_only_certificate"]["test_arrays_read"] == []
            and value["known_only_certificate"][
                "unknown_or_test_labels_used"
            ]
            is False
            for value in captures.values()
        ),
        "clean_safety_nonmissing_activation_upper": max(
            row["nonmissing_active_rate_one_sided_95pct_upper"]
            for row in safety_rows
        )
        <= safety_limit + 1e-12,
        "clean_prediction_probability_and_inactive_risk_exact": all(
            row["prediction_array_equal_pairwise"]
            and row["probability_max_absolute_difference"] == 0.0
            and row["inactive_risk_max_absolute_difference"] <= 1e-12
            and row["clean_delta"] == 0.0
            for row in safety_rows
        ),
        "risk_only_routing_contract_all_evaluations": all(routing_checks),
        "zero_unknown_or_test_labels_used_for_routing_or_selection": all(
            leakage_checks
        ),
        "known_macro_f1_exact_pairwise_all_conditions": all(known_f1_exact),
        "enabled_primary_scenario_count_minimum": len(enabled_primary)
        >= int(gate["enabled_scenario_count_minimum"]),
        "enabled_primary_suite_count_minimum": len(enabled_primary_suites)
        >= int(gate["enabled_suite_count_minimum"]),
        "overall_directed_means_strictly_positive": all(
            primary_stats["overall_directed_mean"][metric] > 0.0
            for metric in DIRECTED_METRICS
        ),
        "at_least_5_of_7_suites_nonnegative_each_metric": all(
            primary_stats["suite_nonnegative_count"][metric]
            >= int(gate["suite_nonnegative_count_minimum_each_metric"])
            for metric in DIRECTED_METRICS
        ),
        "no_family_metric_regression_over_limit": all(
            primary_stats["family_directed_mean"][metric][family]
            >= -float(gate["each_family_metric_regression_maximum"])
            - 1e-12
            for metric in DIRECTED_METRICS
            for family in FAMILIES
        ),
        "modality_missing_composite_improves": (
            primary_stats["family_composite_directed_mean"][
                "modality_missing"
            ]
            > 0.0
        ),
        "gaussian_drift_composite_improves": (
            primary_stats["family_composite_directed_mean"][
                "gaussian_drift"
            ]
            > 0.0
        ),
        "bootstrap_primary_composite_lower_bound_strictly_positive": (
            bootstrap["lower_95"] > 0.0
        ),
    }
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_csr_confirmation_summary_v1",
        "state": "complete",
        "algorithm": "krc_csr_caeos_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "capture_count": len(captures),
        "evaluation_count": len(evaluations),
        "capture_file_sha256": capture_hashes,
        "evaluation_file_sha256": evaluation_hashes,
        "routing_coverage_definition": (
            "scenario_enabled_only_if_all_three_training_seeds_certify"
        ),
        "enabled_primary_scenario_count": len(enabled_primary),
        "enabled_primary_suite_count": len(enabled_primary_suites),
        "enabled_primary_identities": sorted(
            "/".join(identity) for identity in enabled_primary
        ),
        "clean_safety": {
            "nonmissing_activation_rate_one_sided_95pct_upper_maximum": (
                max(
                    row[
                        "nonmissing_active_rate_one_sided_95pct_upper"
                    ]
                    for row in safety_rows
                )
            ),
            "gate_maximum": safety_limit,
            "rows": sorted(
                safety_rows,
                key=lambda row: (
                    row["suite"],
                    row["scenario"],
                    row["training_seed"],
                ),
            ),
        },
        "primary88": primary_stats,
        "primary88_bootstrap": bootstrap,
        "secondary_full102": full_stats,
        "checks": checks,
        "passes": all(checks.values()),
        "authorize_external_safety_efficiency_confirmation": all(
            checks.values()
        ),
        "selection": (
            "krc_csr_caeos_v1"
            if all(checks.values())
            else "caeos_pairwise"
        ),
        "claim_boundary": {
            "confirmation_success_establishes_sota": False,
            "secondary_full102_does_not_override_primary_failure": True,
            "external_malicious_parrot_safety_and_efficiency_still_required": (
                True
            ),
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--evaluation-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = summarize(
        load_json(args.protocol),
        sorted(args.capture_root.rglob("capture_manifest.json")),
        sorted(args.evaluation_root.rglob("evaluation.json")),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
