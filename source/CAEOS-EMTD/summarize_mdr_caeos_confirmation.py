from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import numpy as np

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from select_mdr_caeos_weight import load
from summarize_mdr_caeos_pilot import METRICS, degradation, mean_records


Identity = Tuple[str, str, int, str]


def validate_protocol(protocol: Dict[str, Any]) -> None:
    if (
        protocol.get("schema_version")
        != "strict_v4_mdr_caeos_confirmation_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("execution_admitted") is not True
    ):
        raise ValueError("canonical MDR confirmation protocol required")


def bootstrap_primary(
    scenario_vectors: Dict[Tuple[str, str], np.ndarray],
    *,
    replicates: int,
    seed: int,
) -> Dict[str, float]:
    by_suite: Dict[str, List[np.ndarray]] = defaultdict(list)
    for (suite, _), vector in scenario_vectors.items():
        by_suite[suite].append(np.asarray(vector, dtype=np.float64))
    if len(by_suite) != 7 or len(scenario_vectors) != 102:
        raise ValueError("MDR bootstrap requires 102 scenarios in seven suites")
    point = float(
        np.mean(
            [
                np.asarray(vectors, dtype=np.float64).mean()
                for vectors in by_suite.values()
            ]
        )
    )
    rng = np.random.default_rng(int(seed))
    samples = np.empty(int(replicates), dtype=np.float64)
    suites = sorted(by_suite)
    arrays = {
        suite: np.asarray(by_suite[suite], dtype=np.float64)
        for suite in suites
    }
    for index in range(int(replicates)):
        suite_values = []
        for suite in suites:
            values = arrays[suite]
            drawn = rng.integers(0, len(values), size=len(values))
            suite_values.append(float(values[drawn].mean()))
        samples[index] = float(np.mean(suite_values))
    return {
        "point_estimate": point,
        "lower_95": float(np.quantile(samples, 0.025)),
        "upper_95": float(np.quantile(samples, 0.975)),
        "replicates": int(replicates),
        "seed": int(seed),
    }


def summarize(
    protocol: Dict[str, Any], evaluation_paths: Iterable[Path]
) -> Dict[str, Any]:
    validate_protocol(protocol)
    expected = {
        (
            task["suite"],
            task["scenario"],
            int(task["training_seed"]),
            condition,
        )
        for task in protocol["confirmation"]["tasks"]
        for condition in protocol["confirmation"]["conditions"]
    }
    seed_to_corruption = {
        int(task["training_seed"]): int(task["corruption_seed"])
        for task in protocol["confirmation"]["tasks"]
    }
    evaluations: Dict[Identity, Dict[str, Any]] = {}
    evaluation_sha = {}
    inactive_exact = True
    leakage_clean = True
    for path in evaluation_paths:
        value = load(path)
        identity = (
            str(value.get("suite")),
            str(value.get("scenario")),
            int(value.get("training_seed", -1)),
            str(value.get("condition")),
        )
        if (
            value.get("schema_version")
            != "strict_v4_mdr_caeos_confirmation_evaluation_v1"
            or value.get("manifest_sha256") != canonical_hash(value)
            or value.get("protocol_manifest_sha256")
            != protocol["manifest_sha256"]
            or int(value.get("corruption_seed", -1))
            != seed_to_corruption.get(identity[2], -2)
            or float(value.get("capture", {}).get("weight", -1.0))
            != float(protocol["selected_augmentation_weight"])
        ):
            raise ValueError(f"invalid MDR confirmation evaluation: {path}")
        if identity in evaluations:
            raise ValueError(f"duplicate MDR confirmation evaluation: {identity}")
        evaluations[identity] = value
        evaluation_sha["/".join(map(str, identity))] = file_hash(path)
        routing = value.get("routing", {})
        inactive_exact = inactive_exact and all(
            routing.get(name) is True
            for name in (
                "inactive_prediction_exactly_pairwise",
                "inactive_risk_exactly_pairwise",
                "inactive_probability_exactly_pairwise",
            )
        )
        leakage_clean = leakage_clean and (
            routing.get("unknown_or_test_labels_used") is False
            and value.get("test_labels_used_for_final_evaluation_only")
            is True
        )
    if set(evaluations) != expected:
        raise ValueError(
            "MDR confirmation evaluation universe mismatch: "
            f"missing={len(expected-set(evaluations))} "
            f"extra={len(set(evaluations)-expected)}"
        )

    families = [
        condition
        for condition in protocol["confirmation"]["conditions"]
        if condition != "clean"
    ]
    tasks = protocol["confirmation"]["tasks"]
    clean_f1_deltas = []
    by_method_suite_family = defaultdict(list)
    scenario_seed_advantages = defaultdict(list)
    active_rates = []
    for task in tasks:
        key = (
            task["suite"],
            task["scenario"],
            int(task["training_seed"]),
        )
        clean = evaluations[(*key, "clean")]
        clean_f1_deltas.append(
            float(clean["candidate_report"]["known_macro_f1"])
            - float(clean["pairwise_report"]["known_macro_f1"])
        )
        active_rates.append(float(clean["routing"]["active_rate"]))
        vector = []
        for family in families:
            corrupted = evaluations[(*key, family)]
            active_rates.append(float(corrupted["routing"]["active_rate"]))
            for method in ("candidate", "pairwise"):
                by_method_suite_family[
                    (method, task["suite"], family)
                ].append(
                    (
                        clean[f"{method}_report"],
                        corrupted[f"{method}_report"],
                    )
                )
            for metric in METRICS:
                pairwise_degradation = degradation(
                    clean["pairwise_report"][metric],
                    corrupted["pairwise_report"][metric],
                    metric,
                )
                candidate_degradation = degradation(
                    clean["candidate_report"][metric],
                    corrupted["candidate_report"][metric],
                    metric,
                )
                vector.append(pairwise_degradation - candidate_degradation)
        scenario_seed_advantages[
            (task["suite"], task["scenario"])
        ].append(np.asarray(vector, dtype=np.float64))
    scenario_vectors = {}
    for identity, vectors in scenario_seed_advantages.items():
        if len(vectors) != 3:
            raise ValueError(f"MDR scenario lacks three seed pairs: {identity}")
        scenario_vectors[identity] = np.asarray(vectors).mean(axis=0)

    thresholds = {
        name: float(value) for name, value in protocol["thresholds"].items()
    }
    suite_results = {"candidate": {}, "pairwise": {}}
    failure_counts = {
        "candidate": {family: 0 for family in families},
        "pairwise": {family: 0 for family in families},
    }
    suites = sorted(
        {record["suite"] for record in protocol["source_registry"]}
    )
    for method in ("candidate", "pairwise"):
        for family in families:
            suite_results[method][family] = {}
            for suite in suites:
                means = mean_records(
                    by_method_suite_family[(method, suite, family)]
                )
                records = {}
                for metric, value in means.items():
                    passed = value <= thresholds[metric] + 1e-12
                    failure_counts[method][family] += int(not passed)
                    records[metric] = {
                        "mean_degradation": value,
                        "maximum_mean_degradation": thresholds[metric],
                        "passes": passed,
                    }
                suite_results[method][family][suite] = records

    family_results = {"candidate": {}, "pairwise": {}}
    aggregate_passes = True
    for method in ("candidate", "pairwise"):
        for family in families:
            records = {}
            for metric in METRICS:
                values = [
                    suite_results[method][family][suite][metric][
                        "mean_degradation"
                    ]
                    for suite in suites
                ]
                mean_value = float(np.mean(values))
                passed = mean_value <= thresholds[metric] + 1e-12
                records[metric] = {
                    "equal_suite_mean_degradation": mean_value,
                    "maximum_mean_degradation": thresholds[metric],
                    "passes": passed,
                }
                if method == "candidate":
                    aggregate_passes = aggregate_passes and passed
            family_results[method][family] = records

    statistics = protocol["statistics"]
    primary = bootstrap_primary(
        scenario_vectors,
        replicates=int(statistics["bootstrap_replicates"]),
        seed=int(statistics["bootstrap_seed"]),
    )
    clean_delta = np.asarray(clean_f1_deltas, dtype=np.float64)
    clean_mean_degradation = float(-clean_delta.mean())
    clean_worst_degradation = float(-clean_delta.min())
    checks = {
        "all_306_captures_represented": len(tasks) == 306,
        "all_1836_evaluations_complete": len(evaluations) == 1836,
        "all_175_suite_threshold_checks_pass": (
            sum(failure_counts["candidate"].values()) == 0
        ),
        "aggregate_family_thresholds_pass": aggregate_passes,
        "clean_known_macro_f1_mean": (
            clean_mean_degradation
            <= float(
                protocol["gate"][
                    "clean_known_macro_f1_mean_degradation_maximum"
                ]
            )
            + 1e-12
        ),
        "clean_known_macro_f1_worst": (
            clean_worst_degradation
            <= float(
                protocol["gate"][
                    "clean_known_macro_f1_worst_degradation_maximum"
                ]
            )
            + 1e-12
        ),
        "inactive_path_exactly_pairwise": inactive_exact,
        "no_unknown_or_test_selection": leakage_clean,
        "primary_composite_bootstrap_lower_bound_positive": (
            primary["lower_95"] > 0.0
        ),
    }
    passes = all(checks.values())
    selected = "mdr_caeos_v1" if passes else "caeos_pairwise"
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_caeos_confirmation_summary_v1",
        "state": "complete",
        "algorithm": "mdr_caeos_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "selected_augmentation_weight": float(
            protocol["selected_augmentation_weight"]
        ),
        "validation": {
            "capture_count": len(tasks),
            "evaluation_count": len(evaluations),
            "scenario_count": len(scenario_vectors),
            "suite_threshold_check_count": 175,
            "aggregate_family_check_count": 25,
            "evaluation_file_sha256": evaluation_sha,
            "passes": True,
        },
        "clean_pairwise_comparison": {
            "known_macro_f1_mean_degradation": clean_mean_degradation,
            "known_macro_f1_worst_degradation": clean_worst_degradation,
        },
        "routing": {
            "mean_active_rate": float(np.mean(active_rates)),
            "minimum_active_rate": float(np.min(active_rates)),
            "maximum_active_rate": float(np.max(active_rates)),
            "inactive_path_exactly_pairwise": inactive_exact,
        },
        "suite_results": suite_results,
        "suite_failure_counts": failure_counts,
        "family_results": family_results,
        "primary_composite_advantage": primary,
        "confirmation_checks": checks,
        "decision": {
            "passes": passes,
            "selected_algorithm": selected,
            "full_confirmation_failure_retains_pairwise": not passes,
        },
        "claim_boundary": {
            "confirmation_success_does_not_establish_comprehensive_sota": True,
            "external_dataset_efficiency_and_system_gates_remain_required": True,
            "no_suite_metric_or_component_splicing": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def final_selection(
    protocol: Dict[str, Any], summary: Dict[str, Any]
) -> Dict[str, Any]:
    if (
        summary.get("manifest_sha256") != canonical_hash(summary)
        or summary.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
    ):
        raise ValueError("canonical MDR confirmation summary required")
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_final_self_algorithm_selection_v2",
        "state": "complete_after_mdr_reserved_confirmation",
        "selected_algorithm": summary["decision"]["selected_algorithm"],
        "previous_incumbent": "caeos_pairwise",
        "mdr_confirmation_passes": summary["decision"]["passes"],
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "summary_manifest_sha256": summary["manifest_sha256"],
        "selection_rule": (
            "select MDR only when every frozen reserved-confirmation gate "
            "passes; otherwise retain Pairwise"
        ),
        "no_component_or_metric_wise_splicing": True,
        "comprehensive_sota_confirmed": False,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--evaluation-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = load(args.protocol)
    summary = summarize(
        protocol, sorted(args.evaluation_root.rglob("evaluation.json"))
    )
    selection = final_selection(protocol, summary)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "final_selection.json").write_text(
        json.dumps(selection, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(summary["manifest_sha256"])


if __name__ == "__main__":
    main()
