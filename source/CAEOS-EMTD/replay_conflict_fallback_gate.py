from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

from scipy.stats import wilcoxon


DEFAULT_CANDIDATES = (
    "msp",
    "entropy",
    "cauchy_baseline",
    "cauchy_all",
    "cauchy_conflict",
    "baseline",
    "nested_monotonic",
    "conflict_augmented",
    "disagreement_augmented",
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Replay a confidence fallback only on the conflict branch"
    )
    parser.add_argument("roots", nargs="+")
    parser.add_argument(
        "--candidates", default=",".join(DEFAULT_CANDIDATES)
    )
    parser.add_argument(
        "--minimum-gains", default="0,0.01,0.02,0.03,0.05,0.08,0.1,0.15"
    )
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def rank(aggregates: dict[str, dict[str, float]], name: str) -> tuple[float, ...]:
    values = aggregates[name]
    return (
        float(values["robust_objective"]),
        float(values["minimum_auroc"]),
        float(values["mean_auroc"]),
    )


def load_rows(roots: list[str]) -> list[dict[str, object]]:
    rows = []
    seen = set()
    for root_value in roots:
        root = Path(root_value)
        for path in sorted(root.glob("*/*/metrics.json")):
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            metrics = json.loads(path.read_text(encoding="utf-8"))
            aggregates = metrics["risk_selection_details"]["candidate_aggregates"]
            first_stage = max(
                ("support_union", "cauchy_evidence"),
                key=lambda name: rank(aggregates, name),
            )
            base = (
                "anchor_support"
                if first_stage == "support_union"
                and "anchor_support" in metrics["reports"]
                else first_stage
            )
            rows.append(
                {
                    "suite": path.parts[-3],
                    "run": path.parent.name,
                    "aggregates": aggregates,
                    "reports": metrics["reports"],
                    "first_stage": first_stage,
                    "base": base,
                    "base_auroc": float(metrics["reports"][base]["unknown_auroc"]),
                }
            )
    if not rows:
        raise ValueError("no metrics were found")
    return rows


def evaluate(
    rows: list[dict[str, object]], candidates: tuple[str, ...], gain: float
) -> dict[str, object]:
    evaluated = []
    for row in rows:
        selected = str(row["base"])
        aggregates = row["aggregates"]
        selection_gain = 0.0
        if row["first_stage"] == "cauchy_evidence":
            eligible = [
                name
                for name in ("cauchy_evidence", *candidates)
                if name in aggregates and name in row["reports"]
            ]
            challenger = max(eligible, key=lambda name: rank(aggregates, name))
            improvement = (
                rank(aggregates, challenger)[0]
                - rank(aggregates, "cauchy_evidence")[0]
            )
            selection_gain = float(improvement)
            if challenger != "cauchy_evidence" and improvement > gain:
                selected = challenger
        auroc = float(row["reports"][selected]["unknown_auroc"])
        evaluated.append(
            {
                "suite": row["suite"],
                "run": row["run"],
                "base": row["base"],
                "selected": selected,
                "base_auroc": row["base_auroc"],
                "auroc": auroc,
                "selection_gain": selection_gain,
            }
        )

    def aggregate(values: list[dict[str, object]]) -> dict[str, object]:
        delta = [float(value["auroc"]) - float(value["base_auroc"]) for value in values]
        nonzero = [value for value in delta if abs(value) > 1e-12]
        return {
            "runs": len(values),
            "mean_auroc": mean(float(value["auroc"]) for value in values),
            "minimum_auroc": min(float(value["auroc"]) for value in values),
            "base_mean_auroc": mean(float(value["base_auroc"]) for value in values),
            "mean_delta": mean(delta),
            "wins": sum(value > 1e-12 for value in delta),
            "ties": sum(abs(value) <= 1e-12 for value in delta),
            "losses": sum(value < -1e-12 for value in delta),
            "wilcoxon_p": (
                float(wilcoxon(nonzero, alternative="two-sided").pvalue)
                if nonzero
                else 1.0
            ),
            "selected": dict(Counter(str(value["selected"]) for value in values)),
        }

    by_suite: dict[str, list[dict[str, object]]] = defaultdict(list)
    for value in evaluated:
        by_suite[str(value["suite"])].append(value)
    return {
        "minimum_gain": gain,
        "global": aggregate(evaluated),
        "by_suite": {
            suite: aggregate(values) for suite, values in sorted(by_suite.items())
        },
        "runs": evaluated,
    }


def main() -> None:
    args = parse_arguments()
    candidates = tuple(value.strip() for value in args.candidates.split(",") if value.strip())
    gains = [float(value) for value in args.minimum_gains.split(",") if value.strip()]
    rows = load_rows(args.roots)
    result = {
        "candidates": candidates,
        "number_of_runs": len(rows),
        "evaluations": [evaluate(rows, candidates, gain) for gain in gains],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for evaluation in result["evaluations"]:
        print(f"gain={evaluation['minimum_gain']:.3f}")
        for suite, values in evaluation["by_suite"].items():
            print(
                "  %s: %.6f (%+.6f), W/T/L=%d/%d/%d"
                % (
                    suite,
                    values["mean_auroc"],
                    values["mean_delta"],
                    values["wins"],
                    values["ties"],
                    values["losses"],
                )
            )


if __name__ == "__main__":
    main()
