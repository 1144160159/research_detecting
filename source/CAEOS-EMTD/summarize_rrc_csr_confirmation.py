from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_rrc_csr_capture_pipeline import (
    CONDITIONS,
    load_json,
    validate_certificate,
    validate_evaluation,
    validate_protocol,
    validate_rrc_capture,
)


DIRECTED_METRICS = (
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)
FAMILIES = CONDITIONS[1:]
Scenario = Tuple[str, str]


def directed_delta(
    candidate: Dict[str, Any],
    pairwise: Dict[str, Any],
    metric: str,
) -> float:
    if metric == "unknown_fpr95":
        return float(pairwise[metric]) - float(candidate[metric])
    return float(candidate[metric]) - float(pairwise[metric])


def suite_balanced(values: Dict[Scenario, float]) -> Dict[str, Any]:
    by_suite: Dict[str, List[float]] = defaultdict(list)
    for (suite, _), value in values.items():
        by_suite[suite].append(float(value))
    suite_means = {
        suite: float(np.mean(rows)) for suite, rows in sorted(by_suite.items())
    }
    if len(suite_means) != 7:
        raise ValueError("RRC suite-balanced aggregation requires seven suites")
    return {
        "suite_means": suite_means,
        "overall_equal_suite_mean": float(
            np.mean(list(suite_means.values()))
        ),
    }


def bootstrap_suite_balanced(
    scenario_composite: Dict[Scenario, float],
    *,
    replicates: int,
    seed: int,
) -> Dict[str, Any]:
    by_suite: Dict[str, List[float]] = defaultdict(list)
    for (suite, _), value in scenario_composite.items():
        by_suite[suite].append(float(value))
    if len(by_suite) != 7 or sum(map(len, by_suite.values())) != 83:
        raise ValueError("RRC bootstrap requires 83 scenarios in seven suites")
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
        suite_rows = []
        for values in arrays.values():
            selected = rng.integers(0, len(values), size=len(values))
            suite_rows.append(float(values[selected].mean()))
        samples[index] = float(np.mean(suite_rows))
    return {
        "unit": "scenario",
        "stratification": "within_suite_equal_suite_weight",
        "point_estimate": point,
        "lower_95": float(np.quantile(samples, 0.025)),
        "upper_95": float(np.quantile(samples, 0.975)),
        "replicates": int(replicates),
        "seed": int(seed),
        "interval_is_report_only_not_an_unregistered_gate": True,
    }


def summarize(
    protocol: Dict[str, Any],
    certificate_paths: List[Path],
    capture_paths: List[Path],
    evaluation_paths: List[Path],
    pipeline_inventory: Dict[str, Any],
) -> Dict[str, Any]:
    validate_protocol(protocol)
    if (
        pipeline_inventory.get("schema_version")
        != "strict_v4_rrc_csr_capture_pipeline_inventory_v1"
        or pipeline_inventory.get("manifest_sha256")
        != canonical_hash(pipeline_inventory)
        or pipeline_inventory.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or pipeline_inventory.get("counts")
        != {
            "base_csr_captures": 249,
            "scenario_certificates": 83,
            "rrc_runtime_captures": 249,
            "evaluations": 1494,
        }
    ):
        raise ValueError("canonical complete RRC pipeline inventory required")

    tasks = protocol["tasks"]
    task_map = {
        (
            task["suite"],
            task["scenario"],
            int(task["training_seed"]),
            int(task["corruption_seed"]),
        ): task
        for task in tasks
    }
    scenarios = sorted(
        {(task["suite"], task["scenario"]) for task in tasks}
    )
    if len(task_map) != 249 or len(scenarios) != 83:
        raise ValueError("exact RRC task universe required")

    certificates: Dict[Scenario, Dict[str, Any]] = {}
    for path in certificate_paths:
        value = load_json(path)
        identity = (value.get("suite"), value.get("scenario"))
        if identity not in scenarios or not validate_certificate(
            path, protocol, identity[0], identity[1]
        ):
            raise ValueError(f"unexpected RRC certificate: {path}")
        if identity in certificates:
            raise ValueError(f"duplicate RRC certificate: {identity}")
        certificates[identity] = value
    if set(certificates) != set(scenarios):
        raise ValueError("RRC certificate inventory is incomplete")

    captures = {}
    for path in capture_paths:
        value = load_json(path)
        task_value = value.get("task", {})
        identity = (
            task_value.get("suite"),
            task_value.get("scenario"),
            int(value.get("training_seed", -1)),
            int(value.get("corruption_seed", -1)),
        )
        task = task_map.get(identity)
        if task is None or not validate_rrc_capture(path, protocol, task):
            raise ValueError(f"unexpected RRC runtime capture: {path}")
        scenario_identity = identity[:2]
        if (
            value.get("scenario_certificate_manifest_sha256")
            != certificates[scenario_identity]["manifest_sha256"]
            or bool(value.get("routing_enabled"))
            != bool(certificates[scenario_identity]["routing_enabled"])
        ):
            raise ValueError("RRC capture and scenario certificate disagree")
        if identity in captures:
            raise ValueError(f"duplicate RRC capture: {identity}")
        captures[identity] = value
    if set(captures) != set(task_map):
        raise ValueError("RRC runtime capture inventory is incomplete")

    expected_evaluations = {
        (suite, scenario, training_seed, condition)
        for suite, scenario, training_seed, _ in task_map
        for condition in CONDITIONS
    }
    evaluations = {}
    rows = []
    for path in evaluation_paths:
        value = load_json(path)
        identity = (
            value.get("suite"),
            value.get("scenario"),
            int(value.get("training_seed", -1)),
            value.get("condition"),
        )
        corruption_seed = int(value.get("corruption_seed", -1))
        task = task_map.get((*identity[:3], corruption_seed))
        if (
            task is None
            or not validate_evaluation(path, protocol, task, identity[3])
            or bool(value.get("certificate_routing_enabled"))
            != bool(certificates[identity[:2]]["routing_enabled"])
        ):
            raise ValueError(f"unexpected RRC evaluation: {path}")
        if identity in evaluations:
            raise ValueError(f"duplicate RRC evaluation: {identity}")
        evaluations[identity] = value
        if identity[3] != "clean":
            for metric in DIRECTED_METRICS:
                rows.append(
                    {
                        "suite": identity[0],
                        "scenario": identity[1],
                        "training_seed": identity[2],
                        "family": identity[3],
                        "metric": metric,
                        "directed_delta": directed_delta(
                            value["candidate_report"],
                            value["pairwise_report"],
                            metric,
                        ),
                    }
                )
    if set(evaluations) != expected_evaluations:
        raise ValueError("RRC evaluation inventory is incomplete")

    metric_summary = {}
    for metric in DIRECTED_METRICS:
        scenario_values = {
            identity: float(
                np.mean(
                    [
                        row["directed_delta"]
                        for row in rows
                        if row["metric"] == metric
                        and (row["suite"], row["scenario"]) == identity
                    ]
                )
            )
            for identity in scenarios
        }
        aggregation = suite_balanced(scenario_values)
        aggregation["scenario_means"] = {
            f"{suite}/{scenario}": value
            for (suite, scenario), value in scenario_values.items()
        }
        aggregation["suite_nonnegative_count"] = sum(
            value >= -1e-12
            for value in aggregation["suite_means"].values()
        )
        metric_summary[metric] = aggregation

    family_summary = {}
    for family in FAMILIES:
        family_summary[family] = {}
        for metric in DIRECTED_METRICS:
            scenario_values = {
                identity: float(
                    np.mean(
                        [
                            row["directed_delta"]
                            for row in rows
                            if row["metric"] == metric
                            and row["family"] == family
                            and (row["suite"], row["scenario"])
                            == identity
                        ]
                    )
                )
                for identity in scenarios
            }
            family_summary[family][metric] = suite_balanced(
                scenario_values
            )["overall_equal_suite_mean"]
        family_summary[family]["composite_directed_mean"] = float(
            np.mean(
                [
                    family_summary[family][metric]
                    for metric in DIRECTED_METRICS
                ]
            )
        )

    scenario_composite = {
        identity: float(
            np.mean(
                [
                    row["directed_delta"]
                    for row in rows
                    if (row["suite"], row["scenario"]) == identity
                ]
            )
        )
        for identity in scenarios
    }
    enabled = [
        identity
        for identity, certificate in certificates.items()
        if certificate["routing_enabled"] is True
    ]
    enabled_suites = sorted({suite for suite, _ in enabled})
    gate = protocol["effect_gate"]
    checks = {
        "enabled_scenario_count_minimum": len(enabled)
        >= int(gate["primary_enabled_scenario_count_minimum"]),
        "enabled_suite_count_minimum": len(enabled_suites)
        >= int(gate["primary_enabled_suite_count_minimum"]),
        "overall_directed_means_strictly_positive": all(
            metric_summary[metric]["overall_equal_suite_mean"] > 0.0
            for metric in DIRECTED_METRICS
        ),
        "suite_nonnegative_count_minimum_each_metric": all(
            metric_summary[metric]["suite_nonnegative_count"]
            >= int(gate["suite_nonnegative_count_minimum_each_metric"])
            for metric in DIRECTED_METRICS
        ),
        "each_family_metric_regression_maximum": all(
            family_summary[family][metric]
            >= -float(gate["each_family_metric_regression_maximum"])
            for family in FAMILIES
            for metric in DIRECTED_METRICS
        ),
        "modality_missing_composite_improves": (
            family_summary["modality_missing"][
                "composite_directed_mean"
            ]
            > 0.0
        ),
        "gaussian_drift_composite_improves": (
            family_summary["gaussian_drift"][
                "composite_directed_mean"
            ]
            > 0.0
        ),
    }
    passes = all(checks.values())
    bootstrap = bootstrap_suite_balanced(
        scenario_composite,
        replicates=int(
            protocol["aggregation_protocol"]["bootstrap_replicates"]
        ),
        seed=int(protocol["aggregation_protocol"]["bootstrap_seed"]),
    )
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_rrc_csr_confirmation_summary_v1",
        "state": "complete",
        "passes": passes,
        "selection": (
            "rrc_csr_caeos_v1" if passes else "caeos_pairwise"
        ),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "pipeline_inventory_manifest_sha256": pipeline_inventory[
            "manifest_sha256"
        ],
        "observed_counts": {
            "scenarios": len(scenarios),
            "base_csr_captures": 249,
            "scenario_certificates": len(certificates),
            "rrc_runtime_captures": len(captures),
            "evaluations": len(evaluations),
            "directed_effect_rows": len(rows),
        },
        "certificate_coverage": {
            "enabled_scenarios": len(enabled),
            "disabled_scenarios": len(scenarios) - len(enabled),
            "enabled_suites": len(enabled_suites),
            "enabled_suite_names": enabled_suites,
            "enabled_scenario_identities": [
                f"{suite}/{scenario}" for suite, scenario in sorted(enabled)
            ],
        },
        "metric_summary": metric_summary,
        "family_summary": family_summary,
        "scenario_composite_directed_mean": {
            f"{suite}/{scenario}": value
            for (suite, scenario), value in scenario_composite.items()
        },
        "suite_balanced_composite_bootstrap": bootstrap,
        "effect_gate_checks": checks,
        "unknown_or_test_labels_used_for_certificate_or_selection": False,
        "test_labels_used_for_final_effect_evaluation_only": True,
        "claim_boundary": {
            "rrc_pass_is_internal_confirmation_not_full_sota": True,
            "external_and_system_gates_remain_required": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--certificate-root", type=Path, required=True)
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--evaluation-root", type=Path, required=True)
    parser.add_argument("--pipeline-inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = summarize(
        load_json(args.protocol.resolve()),
        sorted(args.certificate_root.resolve().rglob("certificate.json")),
        sorted(args.capture_root.resolve().rglob("capture_manifest.json")),
        sorted(args.evaluation_root.resolve().rglob("evaluation.json")),
        load_json(args.pipeline_inventory.resolve()),
    )
    value["input_file_sha256"] = {
        "protocol": file_hash(args.protocol.resolve()),
        "pipeline_inventory": file_hash(
            args.pipeline_inventory.resolve()
        ),
    }
    value["manifest_sha256"] = canonical_hash(value)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
