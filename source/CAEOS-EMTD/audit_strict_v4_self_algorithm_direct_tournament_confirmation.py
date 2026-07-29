from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


PROTOCOL_SCHEMA = "strict_v4_self_algorithm_direct_tournament_protocol_v1"
RECORD_SCHEMA = (
    "strict_v4_self_algorithm_direct_tournament_task_evaluation_v1"
)
SUMMARY_SCHEMA = "strict_v4_self_algorithm_direct_tournament_summary_v1"
AUDIT_SCHEMA = "strict_v4_self_algorithm_direct_tournament_audit_v1"
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


def record_path(result_root: Path, task: dict[str, Any]) -> Path:
    return (
        result_root
        / "task_records"
        / task["suite"]
        / task["scenario"]
        / f"seed{int(task['training_seed'])}"
        / "evaluation.json"
    )


def close_tree(left: Any, right: Any, tolerance: float = 1e-12) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return left is right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return abs(float(left) - float(right)) <= tolerance
    if isinstance(left, dict) and isinstance(right, dict):
        return set(left) == set(right) and all(
            close_tree(left[key], right[key], tolerance) for key in left
        )
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(
            close_tree(a, b, tolerance) for a, b in zip(left, right)
        )
    return left == right


def oriented(metric: str, challenger: float, incumbent: float) -> float:
    value = float(challenger) - float(incumbent)
    return -value if metric == "unknown_fpr95" else value


def independently_load_rows(
    protocol: dict[str, Any], result_root: Path
) -> tuple[list[dict[str, Any]], list[dict[str, str]], list[bool]]:
    rows = []
    inventory = []
    validity = []
    expected_conditions = protocol["confirmation_universe"]["conditions"]
    for task in protocol["confirmation_universe"]["tasks"]:
        path = record_path(result_root, task)
        value = load(path)
        canonical = bool(
            value.get("schema_version") == RECORD_SCHEMA
            and value.get("manifest_sha256") == canonical_hash(value)
        )
        observed = value.get("task", {})
        conditions = value.get("condition_evaluations", [])
        identity = bool(
            observed.get("identity") == task["identity"]
            and observed.get("suite") == task["suite"]
            and observed.get("scenario") == task["scenario"]
            and int(observed.get("seed", -1))
            == int(task["training_seed"])
            and value.get("incumbent_algorithm")
            == protocol["incumbent_algorithm"]
            and value.get("challenger_algorithm")
            == protocol["challenger_algorithm"]
            and [row.get("condition") for row in conditions]
            == expected_conditions
            and value.get("input_evidence", {}).get(
                "protocol_manifest_sha256"
            )
            == protocol["manifest_sha256"]
        )
        validity.append(canonical and identity)
        inventory.append(
            {
                "path": str(path.relative_to(result_root)).replace("\\", "/"),
                "file_sha256": file_hash(path),
                "manifest_sha256": value.get("manifest_sha256"),
            }
        )
        for condition in conditions:
            rows.append(
                {
                    "suite": task["suite"],
                    "scenario": task["scenario"],
                    "seed": int(task["training_seed"]),
                    "condition": condition["condition"],
                    "deltas": {
                        metric: oriented(
                            metric,
                            condition["challenger_report"][metric],
                            condition["incumbent_report"][metric],
                        )
                        for metric in METRICS
                    },
                }
            )
    return rows, inventory, validity


def means(rows: list[dict[str, Any]]) -> dict[str, float]:
    if not rows:
        raise ValueError("nonempty audit rows required")
    return {
        metric: mean(float(row["deltas"][metric]) for row in rows)
        for metric in METRICS
    }


def aggregate(
    rows: list[dict[str, Any]],
) -> tuple[
    dict[str, float],
    dict[str, dict[str, float]],
    dict[str, dict[str, dict[str, float]]],
]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(
        list
    )
    for row in rows:
        grouped[(row["suite"], row["scenario"])].append(row)
    scenarios: dict[str, dict[str, dict[str, float]]] = defaultdict(dict)
    for (suite, scenario), values in sorted(grouped.items()):
        scenarios[suite][scenario] = means(values)
    suites = {
        suite: {
            metric: mean(row[metric] for row in values.values())
            for metric in METRICS
        }
        for suite, values in sorted(scenarios.items())
    }
    overall = {
        metric: mean(row[metric] for row in suites.values())
        for metric in METRICS
    }
    return overall, suites, dict(scenarios)


def four(row: dict[str, float]) -> float:
    return mean(float(row[name]) for name in UNKNOWN_METRICS)


def bootstrap_lower(
    scenarios: dict[str, dict[str, dict[str, float]]]
) -> float:
    rng = np.random.default_rng(20260727)
    suites = sorted(scenarios)
    draws = np.empty(10000, dtype=np.float64)
    for index in range(10000):
        chosen_suites = rng.choice(suites, size=7, replace=True)
        values = []
        for suite in chosen_suites:
            names = sorted(scenarios[str(suite)])
            chosen = rng.choice(names, size=len(names), replace=True)
            values.append(
                mean(four(scenarios[str(suite)][str(name)]) for name in chosen)
            )
        draws[index] = mean(values)
    return float(np.quantile(draws, 0.025))


def recompute(
    protocol: dict[str, Any], rows: list[dict[str, Any]]
) -> tuple[dict[str, Any], dict[str, Any]]:
    overall, suites, scenarios = aggregate(rows)
    conditions = {
        condition: aggregate(
            [row for row in rows if row["condition"] == condition]
        )[0]
        for condition in protocol["confirmation_universe"]["conditions"]
    }
    gate = protocol["selection_gate"]
    lower = bootstrap_lower(scenarios)
    condition_checks = {
        name: bool(
            row["known_macro_f1"]
            >= gate["known_macro_f1_equal_suite_mean_gain_minimum"]
            and four(row) >= 0.0
        )
        for name, row in conditions.items()
    }
    checks = {
        "known_macro_f1_protected": bool(
            overall["known_macro_f1"]
            >= gate["known_macro_f1_equal_suite_mean_gain_minimum"]
        ),
        "four_unknown_metric_mean_gain": bool(
            four(overall)
            >= gate["four_unknown_metric_oriented_mean_gain_minimum"]
        ),
        "unknown_metric_positive_count": bool(
            sum(overall[name] > 0.0 for name in UNKNOWN_METRICS)
            >= gate["unknown_metric_positive_count_minimum"]
        ),
        "nonnegative_suite_breadth": bool(
            sum(four(row) >= 0.0 for row in suites.values())
            >= gate["nonnegative_suite_count_minimum"]
        ),
        "worst_suite_protected": bool(
            min(four(row) for row in suites.values())
            >= gate["worst_suite_four_unknown_metric_mean_gain_minimum"]
        ),
        "bootstrap_lower_nonnegative": bool(
            lower >= gate["four_unknown_metric_bootstrap_lower_95_minimum"]
        ),
        "clean_and_each_corruption_condition": all(
            condition_checks.values()
        ),
    }
    passes = all(checks.values())
    aggregation = {
        "overall_equal_suite_oriented_gain": overall,
        "by_suite": suites,
        "by_condition_equal_suite": conditions,
    }
    decision = {
        "challenger_gate_passes": passes,
        "selected_algorithm": (
            protocol["challenger_algorithm"]
            if passes
            else protocol["incumbent_algorithm"]
        ),
        "checks": checks,
        "diagnostics": {
            "four_unknown_metric_oriented_mean_gain": four(overall),
            "unknown_metric_positive_count": sum(
                overall[name] > 0.0 for name in UNKNOWN_METRICS
            ),
            "nonnegative_suite_count": sum(
                four(row) >= 0.0 for row in suites.values()
            ),
            "worst_suite_four_unknown_metric_mean_gain": min(
                four(row) for row in suites.values()
            ),
            "bootstrap_lower_95": lower,
            "condition_checks": condition_checks,
        },
    }
    return aggregation, decision


def build_audit(
    *,
    project_root: Path,
    protocol_path: Path,
    result_root: Path,
) -> dict[str, Any]:
    protocol = load(protocol_path)
    summary_path = result_root / "summary.json"
    summary = load(summary_path)
    require_canonical(protocol, PROTOCOL_SCHEMA, "tournament protocol")
    require_canonical(summary, SUMMARY_SCHEMA, "tournament summary")
    rows, inventory, validity = independently_load_rows(
        protocol, result_root
    )
    aggregation, decision = recompute(protocol, rows)
    implementation_valid = all(
        (project_root / relative).is_file()
        and file_hash(project_root / relative) == expected
        for relative, expected in protocol["implementation_sha256"].items()
    )
    checks = {
        "protocol_canonical": True,
        "summary_canonical": True,
        "protocol_binding": (
            summary.get("protocol_manifest_sha256")
            == protocol["manifest_sha256"]
        ),
        "task_record_count": len(validity) == 306,
        "paired_condition_evaluation_count": len(rows) == 918,
        "all_task_records_canonical_and_bound": all(validity),
        "record_inventory_exact": (
            summary.get("task_record_inventory") == inventory
        ),
        "aggregation_recomputed_exactly": close_tree(
            summary.get("aggregation"), aggregation
        ),
        "decision_recomputed_exactly": close_tree(
            summary.get("decision"), decision
        ),
        "implementation_sha256_valid": implementation_valid,
    }
    integrity_passes = all(checks.values())
    value: dict[str, Any] = {
        "schema_version": AUDIT_SCHEMA,
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "protocol_file_sha256": file_hash(protocol_path),
        "summary_manifest_sha256": summary["manifest_sha256"],
        "summary_file_sha256": file_hash(summary_path),
        "integrity": {"passes": integrity_passes, "checks": checks},
        "independent_recomputation": {
            "aggregation": aggregation,
            "decision": decision,
        },
        "decision": {
            **decision,
            "effect_passes": bool(
                integrity_passes and decision["challenger_gate_passes"]
            ),
        },
        "claim_boundary": {
            "audit_recomputed_from_raw_task_records": True,
            "selection_final_only_with_passing_integrity": True,
            "tournament_does_not_authorize_comprehensive_sota": True,
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

    result_root = resolve(args.result_root)
    audit = build_audit(
        project_root=root,
        protocol_path=resolve(args.protocol),
        result_root=result_root,
    )
    output = result_root / "audit.json"
    if output.is_file() and load(output) != audit:
        raise ValueError("existing tournament audit is immutable")
    if not output.is_file():
        output.write_text(
            json.dumps(audit, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(audit["manifest_sha256"])


if __name__ == "__main__":
    main()
