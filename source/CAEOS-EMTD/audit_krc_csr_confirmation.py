from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy.stats import beta

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


METRICS = (
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


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def directed(
    candidate: Dict[str, Any],
    pairwise: Dict[str, Any],
    metric: str,
) -> float:
    if metric == "unknown_fpr95":
        return float(pairwise[metric]) - float(candidate[metric])
    return float(candidate[metric]) - float(pairwise[metric])


def close(left: Any, right: Any, tolerance: float = 1e-12) -> bool:
    return bool(
        np.isclose(
            float(left),
            float(right),
            rtol=0.0,
            atol=tolerance,
            equal_nan=False,
        )
    )


def audit(
    protocol: Dict[str, Any],
    summary: Dict[str, Any],
    capture_paths: List[Path],
    evaluation_paths: List[Path],
) -> Dict[str, Any]:
    if (
        protocol.get("schema_version")
        != "strict_v4_krc_csr_confirmation_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("execution_admitted") is not True
    ):
        raise ValueError("canonical admitted KRC protocol required")
    if (
        summary.get("schema_version")
        != "strict_v4_krc_csr_confirmation_summary_v1"
        or summary.get("manifest_sha256") != canonical_hash(summary)
        or summary.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
    ):
        raise ValueError("canonical KRC summary required")

    tasks = protocol["confirmation"]["tasks"]
    expected_tasks = {
        (
            str(task["suite"]),
            str(task["scenario"]),
            int(task["training_seed"]),
            int(task["corruption_seed"]),
        ): bool(task["primary_heldout_scenario"])
        for task in tasks
    }
    training_to_corruption = {
        identity[2]: identity[3] for identity in expected_tasks
    }
    expected_captures = {
        identity[:3] for identity in expected_tasks
    }
    captures = {}
    observed_capture_hashes = {}
    capture_contracts = []
    enabled_by_scenario: Dict[Tuple[str, str], List[bool]] = defaultdict(
        list
    )
    safety_upper = []
    for path in capture_paths:
        value = load_json(path)
        task = value.get("task", {})
        identity = (
            str(task.get("suite")),
            str(task.get("scenario")),
            int(value.get("training_seed", -1)),
        )
        if identity in captures:
            raise ValueError(f"duplicate capture: {identity}")
        captures[identity] = value
        observed_capture_hashes["/".join(map(str, identity))] = file_hash(
            path
        )
        certificate = value.get("known_only_certificate", {})
        profile = value.get("safety_profile", {})
        enabled = bool(certificate.get("routing_enabled"))
        enabled_by_scenario[identity[:2]].append(enabled)
        safety_count = int(profile.get("partition", {}).get("safety_count", 0))
        missing = int(profile.get("missing_active_count", -1))
        nonmissing = safety_count - missing
        active = int(profile.get("active_count", -1)) - missing
        upper = (
            float(beta.ppf(0.95, active + 1, nonmissing - active))
            if active < nonmissing
            else 1.0
        )
        safety_upper.append(upper)
        capture_contracts.append(
            value.get("schema_version")
            == "strict_v4_krc_csr_runtime_capture_v1"
            and value.get("manifest_sha256") == canonical_hash(value)
            and value.get("state") == "complete"
            and value.get("roundtrip", {}).get("passes") is True
            and certificate.get("test_arrays_read") == []
            and certificate.get("unknown_or_test_labels_used") is False
            and value.get(
                "unknown_or_test_labels_used_for_training_selection_or_calibration"
            )
            is False
            and profile.get("prediction_array_equal_pairwise") is True
            and float(
                profile.get("probability_max_absolute_difference", -1.0)
            )
            == 0.0
            and float(
                profile.get("inactive_risk_max_absolute_difference", -1.0)
            )
            <= 1e-12
            and float(profile.get("clean_delta", -1.0)) == 0.0
        )

    conditions = tuple(protocol["confirmation"]["conditions"])
    expected_evaluations = {
        (*identity[:3], condition)
        for identity in expected_tasks
        for condition in conditions
    }
    evaluations = {}
    observed_evaluation_hashes = {}
    evaluation_contracts = []
    known_f1_exact = []
    primary_rows = []
    for path in evaluation_paths:
        value = load_json(path)
        identity = (
            str(value.get("suite")),
            str(value.get("scenario")),
            int(value.get("training_seed", -1)),
            str(value.get("condition")),
        )
        if identity in evaluations:
            raise ValueError(f"duplicate evaluation: {identity}")
        evaluations[identity] = value
        observed_evaluation_hashes["/".join(map(str, identity))] = (
            file_hash(path)
        )
        corruption_seed = training_to_corruption.get(identity[2], -2)
        task_identity = (*identity[:3], corruption_seed)
        route = value.get("routing", {})
        enabled = bool(value.get("certificate_routing_enabled"))
        evaluation_contracts.append(
            value.get("schema_version")
            == "strict_v4_krc_csr_confirmation_evaluation_v1"
            and value.get("manifest_sha256") == canonical_hash(value)
            and value.get("protocol_manifest_sha256")
            == protocol["manifest_sha256"]
            and task_identity in expected_tasks
            and int(value.get("corruption_seed", -1)) == corruption_seed
            and bool(value.get("primary_heldout_scenario"))
            == expected_tasks.get(task_identity)
            and enabled
            == bool(
                captures.get(identity[:3], {})
                .get("known_only_certificate", {})
                .get("routing_enabled")
            )
            and route.get("prediction_exactly_pairwise_all_rows") is True
            and route.get("probability_exactly_pairwise_all_rows") is True
            and route.get("risk_monotone_not_below_pairwise") is True
            and route.get("inactive_risk_exactly_pairwise") is True
            and route.get("disabled_risk_exactly_pairwise_all_rows") is True
            and route.get("unknown_or_test_labels_used") is False
            and value.get("test_labels_used_for_final_evaluation_only")
            is True
        )
        candidate = value.get("candidate_report", {})
        pairwise = value.get("pairwise_report", {})
        known_f1_exact.append(
            candidate.get("known_macro_f1")
            == pairwise.get("known_macro_f1")
        )
        if (
            identity[3] != "clean"
            and expected_tasks.get(task_identity) is True
        ):
            for metric in METRICS:
                primary_rows.append(
                    (
                        identity[0],
                        identity[1],
                        identity[3],
                        metric,
                        directed(candidate, pairwise, metric),
                    )
                )

    primary_scenarios = {
        identity[:2]
        for identity, primary in expected_tasks.items()
        if primary
    }
    enabled_primary = {
        identity
        for identity in primary_scenarios
        if len(enabled_by_scenario[identity]) == 3
        and all(enabled_by_scenario[identity])
    }
    independent_overall = {}
    independent_suite = {}
    independent_family = {}
    for metric in METRICS:
        metric_rows = [row for row in primary_rows if row[3] == metric]
        independent_overall[metric] = float(
            np.mean([row[4] for row in metric_rows])
        )
        independent_suite[metric] = {}
        for suite in sorted({identity[0] for identity in primary_scenarios}):
            independent_suite[metric][suite] = float(
                np.mean(
                    [row[4] for row in metric_rows if row[0] == suite]
                )
            )
        independent_family[metric] = {}
        for family in FAMILIES:
            independent_family[metric][family] = float(
                np.mean(
                    [row[4] for row in metric_rows if row[2] == family]
                )
            )
    suite_nonnegative = {
        metric: sum(
            value >= -1e-12
            for value in independent_suite[metric].values()
        )
        for metric in METRICS
    }
    family_composite = {
        family: float(
            np.mean(
                [
                    independent_family[metric][family]
                    for metric in METRICS
                ]
            )
        )
        for family in FAMILIES
    }
    scenario_composite = {}
    for suite, scenario in sorted(primary_scenarios):
        values = [
            row[4]
            for row in primary_rows
            if row[0] == suite and row[1] == scenario
        ]
        scenario_composite[f"{suite}/{scenario}"] = float(np.mean(values))
    by_suite: Dict[str, np.ndarray] = {}
    for suite in sorted({identity[0] for identity in primary_scenarios}):
        by_suite[suite] = np.asarray(
            [
                value
                for identity, value in scenario_composite.items()
                if identity.startswith(f"{suite}/")
            ],
            dtype=np.float64,
        )
    gate = protocol["primary_gate"]
    rng = np.random.default_rng(int(gate["bootstrap_seed"]))
    samples = []
    for _ in range(int(gate["bootstrap_replicates"])):
        suite_draws = []
        for values in by_suite.values():
            indices = rng.integers(0, values.size, size=values.size)
            suite_draws.append(float(values[indices].mean()))
        samples.append(float(np.mean(suite_draws)))
    bootstrap_lower = float(np.quantile(samples, 0.025))

    reported_primary = summary["primary88"]
    numerical_match = (
        all(
            close(
                independent_overall[metric],
                reported_primary["overall_directed_mean"][metric],
            )
            for metric in METRICS
        )
        and all(
            close(
                independent_suite[metric][suite],
                reported_primary["suite_directed_mean"][metric][suite],
            )
            for metric in METRICS
            for suite in independent_suite[metric]
        )
        and all(
            close(
                independent_family[metric][family],
                reported_primary["family_directed_mean"][metric][family],
            )
            for metric in METRICS
            for family in FAMILIES
        )
        and all(
            close(
                scenario_composite[identity],
                reported_primary["scenario_composite_directed_mean"][
                    identity
                ],
            )
            for identity in scenario_composite
        )
        and close(
            bootstrap_lower,
            summary["primary88_bootstrap"]["lower_95"],
        )
    )
    safety_limit = float(
        protocol.get("clean_safety_gate", {}).get(
            "nonmissing_activation_rate_one_sided_95pct_upper_maximum",
            0.01,
        )
    )
    independently_recomputed_gate = {
        "clean_safety_nonmissing_activation_upper": max(safety_upper)
        <= safety_limit + 1e-12,
        "known_macro_f1_exact_pairwise_all_conditions": all(known_f1_exact),
        "enabled_primary_scenario_count_minimum": len(enabled_primary)
        >= int(gate["enabled_scenario_count_minimum"]),
        "enabled_primary_suite_count_minimum": len(
            {suite for suite, _ in enabled_primary}
        )
        >= int(gate["enabled_suite_count_minimum"]),
        "overall_directed_means_strictly_positive": all(
            independent_overall[metric] > 0.0 for metric in METRICS
        ),
        "at_least_5_of_7_suites_nonnegative_each_metric": all(
            suite_nonnegative[metric]
            >= int(gate["suite_nonnegative_count_minimum_each_metric"])
            for metric in METRICS
        ),
        "no_family_metric_regression_over_limit": all(
            independent_family[metric][family]
            >= -float(gate["each_family_metric_regression_maximum"])
            - 1e-12
            for metric in METRICS
            for family in FAMILIES
        ),
        "modality_missing_composite_improves": (
            family_composite["modality_missing"] > 0.0
        ),
        "gaussian_drift_composite_improves": (
            family_composite["gaussian_drift"] > 0.0
        ),
        "bootstrap_primary_composite_lower_bound_strictly_positive": (
            bootstrap_lower > 0.0
        ),
    }
    structural_checks = {
        "protocol_task_count_306": len(expected_tasks) == 306,
        "protocol_primary_task_count_264": sum(expected_tasks.values())
        == 264,
        "capture_universe_exact": set(captures) == expected_captures,
        "evaluation_universe_exact": set(evaluations)
        == expected_evaluations,
        "capture_contracts_pass": all(capture_contracts),
        "evaluation_contracts_pass": all(evaluation_contracts),
        "capture_file_hash_registry_exact": observed_capture_hashes
        == summary["capture_file_sha256"],
        "evaluation_file_hash_registry_exact": observed_evaluation_hashes
        == summary["evaluation_file_sha256"],
        "primary_numerical_recomputation_matches": numerical_match,
        "enabled_primary_identity_registry_exact": sorted(
            "/".join(identity) for identity in enabled_primary
        )
        == summary["enabled_primary_identities"],
        "reported_checks_match_independent_gate": all(
            summary["checks"].get(name) is passed
            for name, passed in independently_recomputed_gate.items()
        ),
        "reported_passes_is_conjunction": summary["passes"]
        is all(summary["checks"].values()),
        "selection_obeys_frozen_rule": summary["selection"]
        == (
            "krc_csr_caeos_v1"
            if summary["passes"]
            else "caeos_pairwise"
        ),
    }
    checks = {**structural_checks, **independently_recomputed_gate}
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_csr_confirmation_audit_v1",
        "state": "complete",
        "algorithm": "krc_csr_caeos_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "summary_manifest_sha256": summary["manifest_sha256"],
        "capture_count": len(captures),
        "evaluation_count": len(evaluations),
        "independent_primary_overall_directed_mean": independent_overall,
        "independent_primary_suite_nonnegative_count": suite_nonnegative,
        "independent_primary_family_composite": family_composite,
        "independent_bootstrap_lower_95": bootstrap_lower,
        "checks": checks,
        "passes": all(checks.values()),
        "decision_matches_summary": all(checks.values())
        and summary["passes"],
        "claim_boundary": {
            "audit_is_independent_of_summary_implementation": True,
            "confirmation_success_establishes_sota": False,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--evaluation-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = audit(
        load_json(args.protocol),
        load_json(args.summary),
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
