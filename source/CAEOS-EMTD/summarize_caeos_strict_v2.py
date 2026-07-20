from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping

from run_nested_gate_matrix import (
    EDGE_IIOT_SCENARIOS,
    NF_CSE_SCENARIOS,
    USTC_TFC2016_SCENARIOS,
)


METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)
SCENARIO_MAPS: dict[str, Mapping[str, str]] = {
    "edge_iiot": EDGE_IIOT_SCENARIOS,
    "nf_cse": NF_CSE_SCENARIOS,
    "ustc_tfc2016": USTC_TFC2016_SCENARIOS,
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Descriptive strict-v2 summary of completed CAEOS runs"
    )
    parser.add_argument("--root", required=True)
    parser.add_argument("--seeds", default="7,11,19,23,37")
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def parse_seeds(value: str) -> tuple[int, ...]:
    tokens = [token.strip() for token in value.split(",")]
    if not tokens or any(not token for token in tokens):
        raise ValueError("seeds must be a non-empty comma-separated list")
    try:
        seeds = tuple(int(token) for token in tokens)
    except ValueError as error:
        raise ValueError("seeds must contain integers") from error
    if any(seed < 0 for seed in seeds) or len(set(seeds)) != len(seeds):
        raise ValueError("seeds must contain unique non-negative integers")
    return tuple(sorted(seeds))


def _read_metrics(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"metrics root must be an object: {path}")
    return payload


def _task(path: Path, payload: dict[str, object]) -> tuple[str, str, int]:
    suite = path.parent.parent.name
    try:
        seed = int(payload["seed"])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"missing integer seed: {path}") from error
    marker = f"_seed{seed}"
    if not path.parent.name.endswith(marker):
        raise ValueError(f"invalid CAEOS run directory: {path.parent}")
    return suite, path.parent.name[: -len(marker)], seed


def _report(payload: dict[str, object], path: Path) -> dict[str, float]:
    report = payload.get("selected_report")
    if not isinstance(report, dict):
        raise ValueError(f"missing selected_report: {path}")
    result = {}
    for metric in METRICS:
        try:
            result[metric] = float(report[metric])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"missing numeric {metric}: {path}") from error
    return result


def _aggregate(rows: list[dict[str, object]]) -> dict[str, object]:
    by_scenario: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        scenario_key = f"{row['suite']}/{row['scenario']}"
        by_scenario[scenario_key].append(row)
    metric_summary: dict[str, object] = {}
    for metric in METRICS:
        scenario_means = [
            statistics.mean(float(row["report"][metric]) for row in items)
            for _, items in sorted(by_scenario.items())
        ]
        metric_summary[metric] = {
            "scenario_mean": statistics.mean(scenario_means),
            "scenario_stddev": (
                statistics.stdev(scenario_means) if len(scenario_means) > 1 else 0.0
            ),
            "minimum_scenario_mean": min(scenario_means),
            "maximum_scenario_mean": max(scenario_means),
        }
    scenario_summary = {
        scenario: {
            "seed_count": len({int(row["seed"]) for row in items}),
            "metrics": {
                metric: statistics.mean(
                    float(row["report"][metric]) for row in items
                )
                for metric in METRICS
            },
        }
        for scenario, items in sorted(by_scenario.items())
    }
    return {
        "run_count": len(rows),
        "scenario_count": len(by_scenario),
        "seed_counts_by_scenario": {
            scenario: len({int(row["seed"]) for row in items})
            for scenario, items in sorted(by_scenario.items())
        },
        "selected_risk_counts": dict(
            sorted(Counter(str(row["selected_risk"]) for row in rows).items())
        ),
        "risk_selection_counts": dict(
            sorted(Counter(str(row["risk_selection"]) for row in rows).items())
        ),
        "metrics": metric_summary,
        "by_scenario": scenario_summary,
    }


def build_summary(
    root: Path,
    seeds: tuple[int, ...],
    scenario_maps: Mapping[str, Mapping[str, str]] = SCENARIO_MAPS,
) -> dict[str, object]:
    expected = {
        (suite, scenario, seed)
        for suite, scenarios in scenario_maps.items()
        for scenario in scenarios
        for seed in seeds
    }
    rows: list[dict[str, object]] = []
    observed = set()
    for path in sorted(root.glob("*/*/metrics.json")):
        payload = _read_metrics(path)
        suite, scenario, seed = _task(path, payload)
        task = (suite, scenario, seed)
        if task in observed:
            raise ValueError(f"duplicate task: {task}")
        observed.add(task)
        rows.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed": seed,
                "selected_risk": payload.get("selected_risk", "missing"),
                "risk_selection": payload.get("risk_selection", "missing"),
                "report": _report(payload, path),
                "metrics_path": str(path),
            }
        )
    if not rows:
        raise ValueError(f"no metrics found under {root}")
    unexpected = sorted(observed - expected)
    if unexpected:
        raise ValueError(f"unexpected tasks: {unexpected}")
    missing = sorted(expected - observed)
    by_suite_rows: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_suite_rows[str(row["suite"])].append(row)
    return {
        "schema_version": "strict_v2_caeos_descriptive_v1",
        "root": str(root),
        "state": "complete" if not missing else "incomplete",
        "expected_run_count": len(expected),
        "observed_run_count": len(rows),
        "missing_count": len(missing),
        "missing": missing,
        "seeds": list(seeds),
        "inference_warning": (
            "descriptive only; scenario-level paired inference belongs in "
            "summarize_neural_comparison_strict_v2.py"
        ),
        "global": _aggregate(rows),
        "by_suite": {
            suite: _aggregate(items)
            for suite, items in sorted(by_suite_rows.items())
        },
    }


def markdown(summary: dict[str, object]) -> str:
    lines = [
        "# CAEOS strict-v2 descriptive summary",
        "",
        f"State: {summary['state']}; runs: {summary['observed_run_count']}/"
        f"{summary['expected_run_count']}.",
        "",
        "These are scenario-balanced descriptive means. They are not paired "
        "SOTA significance tests.",
        "",
        "| Scope | Runs | Scenarios | Known macro-F1 | AUROC | AUPR | FPR95 | OSCR |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    scopes = [("global", summary["global"]), *summary["by_suite"].items()]
    for name, item in scopes:
        metrics = item["metrics"]
        lines.append(
            f"| {name} | {item['run_count']} | {item['scenario_count']} | "
            f"{metrics['known_macro_f1']['scenario_mean']:.6f} | "
            f"{metrics['unknown_auroc']['scenario_mean']:.6f} | "
            f"{metrics['unknown_aupr']['scenario_mean']:.6f} | "
            f"{metrics['unknown_fpr95']['scenario_mean']:.6f} | "
            f"{metrics['oscr']['scenario_mean']:.6f} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_arguments()
    summary = build_summary(Path(args.root), parse_seeds(args.seeds))
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "caeos_strict_v2_descriptive.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output / "caeos_strict_v2_descriptive.md").write_text(
        markdown(summary), encoding="utf-8"
    )
    print(markdown(summary), end="")


if __name__ == "__main__":
    main()
