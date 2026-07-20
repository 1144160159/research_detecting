from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon


CANDIDATES = ("support_union", "cauchy_evidence")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize nested conflict-gate runs")
    parser.add_argument("inputs", nargs="+")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def statistics(values: list[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(array.mean()),
        "std": float(array.std()),
        "min": float(array.min()),
        "max": float(array.max()),
    }


def scenario_name(path: Path) -> str:
    return path.parent.name.rsplit("_seed", 1)[0]


def collect(paths: list[str]) -> list[dict[str, object]]:
    metrics_paths = []
    for value in paths:
        path = Path(value)
        if path.is_file():
            metrics_paths.append(path)
        else:
            metrics_paths.extend(path.rglob("metrics.json"))
    runs = []
    for path in sorted(set(metrics_paths)):
        with path.open(encoding="utf-8") as handle:
            metrics = json.load(handle)
        if metrics.get("risk_selection") != "nested_conflict_gate":
            continue
        candidate_auroc = {
            name: float(metrics["reports"][name]["unknown_auroc"])
            for name in CANDIDATES
        }
        selected = metrics["selected_risk"]
        oracle = max(CANDIDATES, key=candidate_auroc.get)
        selected_auroc = candidate_auroc[selected]
        oracle_auroc = candidate_auroc[oracle]
        aggregates = metrics["risk_selection_details"]["candidate_aggregates"]
        runs.append(
            {
                "scenario": scenario_name(path),
                "seed": int(metrics["seed"]),
                "unknown_classes": metrics["unknown_classes"],
                "selected_risk": selected,
                "oracle_risk": oracle,
                "selection_correct": selected == oracle,
                "selected_auroc": selected_auroc,
                "support_auroc": candidate_auroc["support_union"],
                "conflict_auroc": candidate_auroc["cauchy_evidence"],
                "oracle_auroc": oracle_auroc,
                "oracle_regret": oracle_auroc - selected_auroc,
                "inner_support_objective": float(
                    aggregates["support_union"]["robust_objective"]
                ),
                "inner_conflict_objective": float(
                    aggregates["cauchy_evidence"]["robust_objective"]
                ),
                "path": str(path),
            }
        )
    return runs


def summarize(runs: list[dict[str, object]]) -> dict[str, object]:
    if not runs:
        raise ValueError("no nested conflict-gate metrics found")
    by_scenario = defaultdict(list)
    for run in runs:
        by_scenario[run["scenario"]].append(run)

    def group_summary(selected_runs: list[dict[str, object]]) -> dict[str, object]:
        count = len(selected_runs)
        selected = [float(run["selected_auroc"]) for run in selected_runs]
        support = [float(run["support_auroc"]) for run in selected_runs]
        conflict = [float(run["conflict_auroc"]) for run in selected_runs]
        regret = [float(run["oracle_regret"]) for run in selected_runs]
        return {
            "number_of_runs": count,
            "selected_risk_counts": {
                name: sum(run["selected_risk"] == name for run in selected_runs)
                for name in CANDIDATES
            },
            "selection_accuracy": float(
                np.mean([run["selection_correct"] for run in selected_runs])
            ),
            "selected_auroc": statistics(selected),
            "support_auroc": statistics(support),
            "conflict_auroc": statistics(conflict),
            "oracle_regret": statistics(regret),
            "selected_minus_support": statistics(
                [left - right for left, right in zip(selected, support)]
            ),
            "selected_minus_conflict": statistics(
                [left - right for left, right in zip(selected, conflict)]
            ),
        }

    overall = group_summary(runs)
    support = np.asarray([run["support_auroc"] for run in runs], dtype=np.float64)
    conflict = np.asarray([run["conflict_auroc"] for run in runs], dtype=np.float64)
    selected = np.asarray([run["selected_auroc"] for run in runs], dtype=np.float64)
    for name, baseline in (("support", support), ("conflict", conflict)):
        difference = selected - baseline
        try:
            p_value = (
                1.0
                if np.allclose(difference, 0.0)
                else float(wilcoxon(difference).pvalue)
            )
        except ValueError:
            p_value = 1.0
        overall[f"selected_vs_{name}_paired"] = {
            "mean_delta": float(difference.mean()),
            "wins": int((difference > 1e-12).sum()),
            "ties": int((np.abs(difference) <= 1e-12).sum()),
            "losses": int((difference < -1e-12).sum()),
            "wilcoxon_p": p_value,
        }
    return {
        "candidates": list(CANDIDATES),
        "overall": overall,
        "per_scenario": {
            name: group_summary(selected_runs)
            for name, selected_runs in sorted(by_scenario.items())
        },
        "runs": sorted(runs, key=lambda run: (run["scenario"], run["seed"])),
    }


def main() -> None:
    args = parse_arguments()
    summary = summarize(collect(args.inputs))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)
    print(json.dumps(summary["overall"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
