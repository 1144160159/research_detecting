#!/usr/bin/env python3
"""Aggregate multi-seed modality-corruption robustness experiments."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


def describe(values):
    array = np.asarray(values, dtype=float)
    return {
        "mean": float(np.mean(array)),
        "std": float(np.std(array, ddof=1)) if len(array) > 1 else 0.0,
        "minimum": float(np.min(array)),
        "maximum": float(np.max(array)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    reports = [json.loads(path.read_text(encoding="utf-8")) for path in args.inputs]
    method_values = defaultdict(lambda: defaultdict(list))
    for report in reports:
        for method, metrics in report["aggregate"].items():
            for metric, value in metrics.items():
                method_values[method][metric].append(value)

    methods = {
        method: {metric: describe(values) for metric, values in metrics.items()}
        for method, metrics in method_values.items()
    }
    comparisons = {}
    for baseline in ("standard", "uniform_views", "reliability_views", "robust_views"):
        mean_gains = []
        minimum_gains = []
        clean_gains = []
        for report in reports:
            robust = report["aggregate"]["mc8_robust"]
            reference = report["aggregate"][baseline]
            mean_gains.append(
                robust["mean_corrupted_macro_f1"]
                - reference["mean_corrupted_macro_f1"]
            )
            minimum_gains.append(
                robust["minimum_corrupted_macro_f1"]
                - reference["minimum_corrupted_macro_f1"]
            )
            clean_gains.append(
                robust["clean_macro_f1"] - reference["clean_macro_f1"]
            )
        comparisons[baseline] = {
            "clean_gain": describe(clean_gains),
            "mean_corrupted_gain": describe(mean_gains),
            "minimum_corrupted_gain": describe(minimum_gains),
            "mean_corrupted_win_rate": float(np.mean(np.asarray(mean_gains) > 0)),
            "minimum_corrupted_win_rate": float(
                np.mean(np.asarray(minimum_gains) > 0)
            ),
        }

    parameter_counts = Counter(
        tuple(sorted(report["selected_parameters"].items())) for report in reports
    )
    by_kind_values = defaultdict(lambda: defaultdict(list))
    for report in reports:
        for kind, metrics in report.get("by_kind", {}).items():
            for method, value in metrics.items():
                by_kind_values[kind][method].append(value)
    output = {
        "seeds": [report["seed"] for report in reports],
        "methods": methods,
        "comparisons": comparisons,
        "selected_parameter_counts": [
            {"parameters": dict(parameters), "count": count}
            for parameters, count in parameter_counts.most_common()
        ],
    }
    if by_kind_values:
        output["by_kind"] = {
            kind: {method: describe(values) for method, values in methods.items()}
            for kind, methods in by_kind_values.items()
        }
    rendered = json.dumps(output, ensure_ascii=False, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
