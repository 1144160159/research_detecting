from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

import numpy as np

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


PROTOCOL_SCHEMA = "strict_v4_self_algorithm_direct_tournament_protocol_v1"
RECORD_SCHEMA = (
    "strict_v4_self_algorithm_direct_tournament_task_evaluation_v1"
)
SUMMARY_SCHEMA = "strict_v4_self_algorithm_direct_tournament_summary_v1"
METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)
UNKNOWN_METRICS = METRICS[1:]


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


def oriented_delta(
    metric: str, challenger: float, incumbent: float
) -> float:
    delta = float(challenger) - float(incumbent)
    return -delta if metric == "unknown_fpr95" else delta


def task_record_path(result_root: Path, task: dict[str, Any]) -> Path:
    return (
        result_root
        / "task_records"
        / task["suite"]
        / task["scenario"]
        / f"seed{int(task['training_seed'])}"
        / "evaluation.json"
    )


def load_records(
    protocol: dict[str, Any], result_root: Path
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    require_canonical(protocol, PROTOCOL_SCHEMA, "tournament protocol")
    records = []
    inventory = []
    conditions = protocol["confirmation_universe"]["conditions"]
    for task in protocol["confirmation_universe"]["tasks"]:
        path = task_record_path(result_root, task)
        value = load(path)
        require_canonical(value, RECORD_SCHEMA, "tournament task record")
        observed = value.get("task", {})
        rows = value.get("condition_evaluations", [])
        if (
            observed.get("identity") != task["identity"]
            or observed.get("suite") != task["suite"]
            or observed.get("scenario") != task["scenario"]
            or int(observed.get("seed", -1))
            != int(task["training_seed"])
            or value.get("incumbent_algorithm")
            != protocol["incumbent_algorithm"]
            or value.get("challenger_algorithm")
            != protocol["challenger_algorithm"]
            or [row.get("condition") for row in rows] != conditions
            or value.get("input_evidence", {}).get(
                "protocol_manifest_sha256"
            )
            != protocol["manifest_sha256"]
        ):
            raise ValueError("tournament task record identity drift")
        records.append(value)
        inventory.append(
            {
                "path": str(path.relative_to(result_root)).replace("\\", "/"),
                "file_sha256": file_hash(path),
                "manifest_sha256": value["manifest_sha256"],
            }
        )
    if len(records) != 306:
        raise ValueError("exactly 306 tournament task records required")
    return records, inventory


def flat_rows(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for record in records:
        task = record["task"]
        for condition in record["condition_evaluations"]:
            deltas = {
                metric: oriented_delta(
                    metric,
                    condition["challenger_report"][metric],
                    condition["incumbent_report"][metric],
                )
                for metric in METRICS
            }
            output.append(
                {
                    "suite": task["suite"],
                    "scenario": task["scenario"],
                    "seed": int(task["seed"]),
                    "condition": condition["condition"],
                    "deltas": deltas,
                }
            )
    if len(output) != 918:
        raise ValueError("exactly 918 paired condition evaluations required")
    return output


def metric_means(rows: Iterable[dict[str, Any]]) -> dict[str, float]:
    values = list(rows)
    if not values:
        raise ValueError("nonempty metric rows required")
    return {
        metric: mean(float(row["deltas"][metric]) for row in values)
        for metric in METRICS
    }


def equal_suite_aggregate(
    rows: list[dict[str, Any]],
) -> tuple[
    dict[str, float],
    dict[str, dict[str, float]],
    dict[str, dict[str, dict[str, float]]],
]:
    by_scenario: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(
        list
    )
    for row in rows:
        by_scenario[(row["suite"], row["scenario"])].append(row)
    scenario_values: dict[str, dict[str, dict[str, float]]] = defaultdict(
        dict
    )
    for (suite, scenario), values in sorted(by_scenario.items()):
        scenario_values[suite][scenario] = metric_means(values)
    suite_values = {
        suite: {
            metric: mean(
                scenario[metric] for scenario in scenarios.values()
            )
            for metric in METRICS
        }
        for suite, scenarios in sorted(scenario_values.items())
    }
    if len(suite_values) != 7:
        raise ValueError("equal aggregation requires seven suites")
    overall = {
        metric: mean(row[metric] for row in suite_values.values())
        for metric in METRICS
    }
    return overall, suite_values, dict(scenario_values)


def condition_aggregates(
    rows: list[dict[str, Any]], conditions: list[str]
) -> dict[str, dict[str, float]]:
    output = {}
    for condition in conditions:
        subset = [row for row in rows if row["condition"] == condition]
        output[condition] = equal_suite_aggregate(subset)[0]
    return output


def four_unknown_mean(row: dict[str, float]) -> float:
    return mean(float(row[metric]) for metric in UNKNOWN_METRICS)


def deterministic_bootstrap_lower(
    scenario_values: dict[str, dict[str, dict[str, float]]],
    repetitions: int,
) -> float:
    if repetitions != 10000:
        raise ValueError("frozen tournament requires 10000 bootstrap draws")
    rng = np.random.default_rng(20260727)
    suites = sorted(scenario_values)
    draws = np.empty(repetitions, dtype=np.float64)
    for index in range(repetitions):
        selected_suites = rng.choice(suites, size=len(suites), replace=True)
        suite_means = []
        for suite in selected_suites:
            scenarios = sorted(scenario_values[str(suite)])
            selected = rng.choice(
                scenarios, size=len(scenarios), replace=True
            )
            suite_means.append(
                mean(
                    four_unknown_mean(
                        scenario_values[str(suite)][str(scenario)]
                    )
                    for scenario in selected
                )
            )
        draws[index] = mean(suite_means)
    return float(np.quantile(draws, 0.025))


def decision(
    protocol: dict[str, Any],
    overall: dict[str, float],
    suites: dict[str, dict[str, float]],
    scenarios: dict[str, dict[str, dict[str, float]]],
    conditions: dict[str, dict[str, float]],
) -> dict[str, Any]:
    gate = protocol["selection_gate"]
    four_mean = four_unknown_mean(overall)
    positive_count = sum(
        float(overall[metric]) > 0.0 for metric in UNKNOWN_METRICS
    )
    nonnegative_suites = sum(
        four_unknown_mean(row) >= 0.0 for row in suites.values()
    )
    worst_suite = min(four_unknown_mean(row) for row in suites.values())
    condition_checks = {
        name: bool(
            float(row["known_macro_f1"])
            >= float(gate["known_macro_f1_equal_suite_mean_gain_minimum"])
            and four_unknown_mean(row) >= 0.0
        )
        for name, row in conditions.items()
    }
    bootstrap_lower = deterministic_bootstrap_lower(
        scenarios,
        int(protocol["statistics"]["bootstrap_repetitions"]),
    )
    checks = {
        "known_macro_f1_protected": bool(
            float(overall["known_macro_f1"])
            >= float(gate["known_macro_f1_equal_suite_mean_gain_minimum"])
        ),
        "four_unknown_metric_mean_gain": bool(
            four_mean
            >= float(gate["four_unknown_metric_oriented_mean_gain_minimum"])
        ),
        "unknown_metric_positive_count": bool(
            positive_count
            >= int(gate["unknown_metric_positive_count_minimum"])
        ),
        "nonnegative_suite_breadth": bool(
            nonnegative_suites
            >= int(gate["nonnegative_suite_count_minimum"])
        ),
        "worst_suite_protected": bool(
            worst_suite
            >= float(
                gate["worst_suite_four_unknown_metric_mean_gain_minimum"]
            )
        ),
        "bootstrap_lower_nonnegative": bool(
            bootstrap_lower
            >= float(
                gate["four_unknown_metric_bootstrap_lower_95_minimum"]
            )
        ),
        "clean_and_each_corruption_condition": all(
            condition_checks.values()
        ),
    }
    passes = all(checks.values())
    return {
        "challenger_gate_passes": passes,
        "selected_algorithm": (
            protocol["challenger_algorithm"]
            if passes
            else protocol["incumbent_algorithm"]
        ),
        "checks": checks,
        "diagnostics": {
            "four_unknown_metric_oriented_mean_gain": four_mean,
            "unknown_metric_positive_count": positive_count,
            "nonnegative_suite_count": nonnegative_suites,
            "worst_suite_four_unknown_metric_mean_gain": worst_suite,
            "bootstrap_lower_95": bootstrap_lower,
            "condition_checks": condition_checks,
        },
    }


def build_summary(
    protocol: dict[str, Any],
    records: list[dict[str, Any]],
    inventory: list[dict[str, str]],
) -> dict[str, Any]:
    rows = flat_rows(records)
    overall, suites, scenarios = equal_suite_aggregate(rows)
    conditions = condition_aggregates(
        rows, protocol["confirmation_universe"]["conditions"]
    )
    value: dict[str, Any] = {
        "schema_version": SUMMARY_SCHEMA,
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "incumbent_algorithm": protocol["incumbent_algorithm"],
        "challenger_algorithm": protocol["challenger_algorithm"],
        "counts": {
            "task_records": len(records),
            "paired_condition_evaluations": len(rows),
            "scenarios": sum(len(value) for value in scenarios.values()),
            "suites": len(suites),
        },
        "aggregation": {
            "overall_equal_suite_oriented_gain": overall,
            "by_suite": suites,
            "by_condition_equal_suite": conditions,
        },
        "decision": decision(
            protocol, overall, suites, scenarios, conditions
        ),
        "task_record_inventory": inventory,
        "claim_boundary": {
            "summary_requires_independent_audit": True,
            "tournament_selection_does_not_authorize_comprehensive_sota": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path(
            "results/strict_v4_self_algorithm_direct_tournament_v1/"
            "protocol.json"
        ),
    )
    parser.add_argument(
        "--result-root",
        type=Path,
        default=Path(
            "results/strict_v4_self_algorithm_direct_tournament_v1"
        ),
    )
    args = parser.parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    protocol_path = resolve(args.protocol)
    result_root = resolve(args.result_root)
    protocol = load(protocol_path)
    records, inventory = load_records(protocol, result_root)
    summary = build_summary(protocol, records, inventory)
    output = result_root / "summary.json"
    if output.is_file() and load(output) != summary:
        raise ValueError("existing tournament summary is immutable")
    if not output.is_file():
        output.write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(summary["manifest_sha256"])


if __name__ == "__main__":
    main()
