from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
PAIRWISE = "caeos_pairwise"


def oriented_gain(candidate: float, reference: float, metric: str) -> float:
    return reference - candidate if metric == "unknown_fpr95" else candidate - reference


def route_values(
    route: dict[str, str],
    means: dict[str, dict[str, dict[str, float]]],
    counts: dict[str, int],
) -> dict[str, float]:
    total = sum(counts.values())
    return {
        metric: sum(
            means[suite][route[suite]][metric] * counts[suite]
            for suite in sorted(route)
        )
        / total
        for metric in METRICS
    }


def metric_gains(
    candidate: dict[str, float], reference: dict[str, float]
) -> dict[str, float]:
    return {
        metric: oriented_gain(candidate[metric], reference[metric], metric)
        for metric in METRICS
    }


def collect(raw: dict[str, Any]) -> tuple[
    dict[str, dict[str, dict[str, float]]], dict[str, int], list[str]
]:
    runs = raw.get("runs", [])
    if not runs:
        raise ValueError("raw fusion contains no runs")
    values: dict[str, Any] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    method_set: set[str] | None = None
    tasks: set[tuple[str, str]] = set()
    for run in runs:
        suite = run["suite"]
        task = run["task"]
        if (suite, task) in tasks:
            raise ValueError(f"duplicate raw fusion task: {suite}/{task}")
        tasks.add((suite, task))
        reports = {PAIRWISE: run["gate_report"], **run["reports"]}
        methods = set(reports)
        if method_set is None:
            method_set = methods
        elif methods != method_set:
            raise ValueError("fixed fusion method set differs across runs")
        for method, report in reports.items():
            for metric in METRICS:
                values[suite][method][metric].append(float(report[metric]))
    means = {
        suite: {
            method: {
                metric: sum(items) / len(items)
                for metric, items in metric_values.items()
            }
            for method, metric_values in method_values.items()
        }
        for suite, method_values in values.items()
    }
    counts = {
        suite: len(values[suite][PAIRWISE][METRICS[0]]) for suite in values
    }
    return means, counts, sorted(method_set or ())


def analyze(raw: dict[str, Any], router: dict[str, Any]) -> dict[str, Any]:
    means, counts, methods = collect(raw)
    suites = sorted(means)
    if set(router.get("routing", {})) != set(suites):
        raise ValueError("router and raw fusion suite sets differ")
    if "rank_union" not in methods:
        raise ValueError("rank_union is required for the hypothesis ceiling")

    admissible = {
        suite: [
            method
            for method in methods
            if all(
                oriented_gain(
                    means[suite][method][metric],
                    means[suite][PAIRWISE][metric],
                    metric,
                )
                >= -1e-12
                for metric in METRICS
            )
        ]
        for suite in suites
    }
    pairwise_route = {suite: PAIRWISE for suite in suites}
    union_route = {suite: "rank_union" for suite in suites}
    pairwise_values = route_values(pairwise_route, means, counts)
    union_values = route_values(union_route, means, counts)
    target = {
        metric: (
            min(pairwise_values[metric], union_values[metric])
            if metric == "unknown_fpr95"
            else max(pairwise_values[metric], union_values[metric])
        )
        for metric in METRICS
    }

    best_pairwise: tuple[Any, ...] | None = None
    best_target: tuple[Any, ...] | None = None
    dominating = 0
    combinations = 0
    for choices in itertools.product(*(admissible[suite] for suite in suites)):
        combinations += 1
        route = dict(zip(suites, choices))
        values = route_values(route, means, counts)
        pairwise_gains = metric_gains(values, pairwise_values)
        target_gains = metric_gains(values, target)
        deterministic_route = tuple(choices)
        pairwise_key = (
            min(pairwise_gains.values()),
            sum(pairwise_gains.values()),
            deterministic_route,
        )
        target_key = (
            min(target_gains.values()),
            sum(target_gains.values()),
            deterministic_route,
        )
        record = (route, values, pairwise_gains, target_gains)
        if best_pairwise is None or pairwise_key > best_pairwise[0]:
            best_pairwise = (pairwise_key, record)
        if best_target is None or target_key > best_target[0]:
            best_target = (target_key, record)
        if all(value >= -1e-12 for value in target_gains.values()):
            dominating += 1

    if best_pairwise is None or best_target is None:
        raise ValueError("no admissible fixed suite routes")
    current_route = {
        suite: router["routing"][suite]["method"] for suite in suites
    }
    current_values = route_values(current_route, means, counts)
    current_pairwise_gains = metric_gains(current_values, pairwise_values)
    best_pairwise_route, best_pairwise_values, best_pairwise_gains, _ = best_pairwise[1]
    best_target_route, best_target_values, _, best_target_gains = best_target[1]
    current_min_gain = min(current_pairwise_gains.values())
    best_min_gain = min(best_pairwise_gains.values())
    result = {
        "schema_version": "strict_v4_router_hypothesis_ceiling_v1",
        "inference_unit": "dataset_scenario",
        "scenario_count": sum(counts.values()),
        "suite_scenario_counts": dict(sorted(counts.items())),
        "fixed_methods": methods,
        "admissible_methods_by_suite": dict(sorted(admissible.items())),
        "enumerated_route_count": combinations,
        "metricwise_pairwise_rank_union_target": target,
        "routes_dominating_metricwise_target": dominating,
        "current_router": {
            "route": current_route,
            "values": current_values,
            "oriented_gains_vs_pairwise": current_pairwise_gains,
            "minimum_oriented_gain_vs_pairwise": current_min_gain,
        },
        "global_pairwise_maximin_route": {
            "route": best_pairwise_route,
            "values": best_pairwise_values,
            "oriented_gains_vs_pairwise": best_pairwise_gains,
            "minimum_oriented_gain_vs_pairwise": best_min_gain,
            "minimum_gain_increment_over_current": best_min_gain
            - current_min_gain,
        },
        "closest_route_to_metricwise_target": {
            "route": best_target_route,
            "values": best_target_values,
            "oriented_gains_vs_target": best_target_gains,
        },
        "decision": {
            "fixed_suite_route_can_dominate_pairwise_and_rank_union": dominating
            > 0,
            "fixed_suite_route_hypothesis_class_is_exhausted": dominating == 0,
            "recommendation": (
                "retain_fixed_suite_route_search"
                if dominating > 0
                else "stop_fixed_suite_route_search_and_train_new_ranking_head"
            ),
        },
    }
    return result


def render(result: dict[str, Any]) -> str:
    decision = result["decision"]
    current = result["current_router"]
    best = result["global_pairwise_maximin_route"]
    return "\n".join(
        [
            "# Strict-v4 fixed suite router hypothesis ceiling",
            "",
            f"Scenarios: {result['scenario_count']}; admissible route combinations: "
            f"{result['enumerated_route_count']}.",
            "",
            "Routes dominating the metricwise Pairwise/Rank-Union target: "
            f"**{result['routes_dominating_metricwise_target']}**.",
            "",
            f"Current minimum gain vs Pairwise: {current['minimum_oriented_gain_vs_pairwise']:+.9f}.",
            f"Best fixed-route minimum gain vs Pairwise: {best['minimum_oriented_gain_vs_pairwise']:+.9f}.",
            f"Increment: {best['minimum_gain_increment_over_current']:+.9f}.",
            "",
            f"Decision: `{decision['recommendation']}`.",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-fusion", type=Path, required=True)
    parser.add_argument("--router-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    raw = json.loads(args.raw_fusion.read_text(encoding="utf-8"))
    router = json.loads(args.router_manifest.read_text(encoding="utf-8"))
    result = analyze(raw, router)
    result["raw_fusion_sha256"] = hashlib.sha256(args.raw_fusion.read_bytes()).hexdigest()
    result["router_manifest_sha256"] = router.get("manifest_sha256")
    result["analysis_implementation_sha256"] = hashlib.sha256(
        Path(__file__).read_bytes()
    ).hexdigest()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "analysis.md").write_text(render(result), encoding="utf-8")
    print(render(result), end="")


if __name__ == "__main__":
    main()
