from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize leave-family-out runs")
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def statistics(values) -> dict[str, float]:
    values = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(values.mean()),
        "std": float(values.std(ddof=1)) if len(values) > 1 else 0.0,
        "min": float(values.min()),
        "max": float(values.max()),
    }


def main() -> None:
    args = parse_arguments()
    rows = []
    pattern = re.compile(r"(.+)_seed(\d+)$")
    for path in sorted(Path(args.root).glob("*_seed*/metrics.json")):
        match = pattern.fullmatch(path.parent.name)
        if match is None:
            continue
        with path.open("r", encoding="utf-8") as handle:
            report = json.load(handle)
        scenario, seed = match.group(1), int(match.group(2))
        row = {
            "scenario": scenario,
            "seed": seed,
            "known_macro_f1": report["reports"]["baseline"]["known_macro_f1"],
            "conflict_auroc": report["reports"]["conflict"]["unknown_auroc"],
            "baseline_auroc": report["reports"]["baseline"]["unknown_auroc"],
            "conflict_augmented_auroc": report["reports"]["conflict_augmented"]["unknown_auroc"],
            "disagreement_augmented_auroc": report["reports"]["disagreement_augmented"]["unknown_auroc"],
            "baseline_oscr": report["reports"]["baseline"]["oscr"],
            "conflict_augmented_oscr": report["reports"]["conflict_augmented"]["oscr"],
            "disagreement_augmented_oscr": report["reports"]["disagreement_augmented"]["oscr"],
            "conflict_delta_auroc": report["conflict_delta_auroc"],
            "disagreement_delta_auroc": report["disagreement_delta_auroc"],
        }
        if "cauchy_evidence" in report["reports"]:
            row.update(
                {
                    "cauchy_baseline_auroc": report["reports"]["cauchy_baseline"]["unknown_auroc"],
                    "cauchy_conflict_auroc": report["reports"]["cauchy_conflict"]["unknown_auroc"],
                    "cauchy_all_auroc": report["reports"]["cauchy_all"]["unknown_auroc"],
                    "cauchy_all_aupr": report["reports"]["cauchy_all"]["unknown_aupr"],
                    "cauchy_all_oscr": report["reports"]["cauchy_all"]["oscr"],
                    "cauchy_evidence_auroc": report["reports"]["cauchy_evidence"]["unknown_auroc"],
                    "cauchy_evidence_aupr": report["reports"]["cauchy_evidence"]["unknown_aupr"],
                    "cauchy_evidence_oscr": report["reports"]["cauchy_evidence"]["oscr"],
                    "cauchy_conflict_delta_auroc": report["cauchy_conflict_delta_auroc"],
                    "cauchy_all_delta_auroc": report["cauchy_all_delta_auroc"],
                    "validation_conflict_uncertainty_correlation": report["component_diagnostics"]["validation_conflict_uncertainty_correlation"],
                }
            )
        for method, metrics in report["reports"].items():
            row.setdefault(f"{method}_auroc", metrics["unknown_auroc"])
            row.setdefault(f"{method}_aupr", metrics["unknown_aupr"])
            row.setdefault(f"{method}_oscr", metrics["oscr"])
        rows.append(row)
    if not rows:
        raise FileNotFoundError(f"no open-set metrics found below {args.root}")

    keys = [key for key in rows[0] if key not in {"scenario", "seed"}]
    scenarios = {}
    for scenario in sorted({row["scenario"] for row in rows}):
        selected = [row for row in rows if row["scenario"] == scenario]
        scenarios[scenario] = {
            "number_of_seeds": len(selected),
            **{key: statistics([row[key] for row in selected]) for key in keys},
            "positive_conflict_gain_rate": float(
                np.mean([row["conflict_delta_auroc"] > 0 for row in selected])
            ),
            "positive_disagreement_gain_rate": float(
                np.mean([row["disagreement_delta_auroc"] > 0 for row in selected])
            ),
        }
    output = {
        "number_of_runs": len(rows),
        "per_run": rows,
        "per_scenario": scenarios,
        "overall": {
            **{key: statistics([row[key] for row in rows]) for key in keys},
            "positive_conflict_gain_rate": float(
                np.mean([row["conflict_delta_auroc"] > 0 for row in rows])
            ),
            "positive_disagreement_gain_rate": float(
                np.mean([row["disagreement_delta_auroc"] > 0 for row in rows])
            ),
        },
    }
    if "cauchy_all_auroc" in rows[0]:
        comparisons = {}
        for baseline in (
            "baseline_auroc",
            "conflict_augmented_auroc",
            "disagreement_augmented_auroc",
            "cauchy_evidence_auroc",
        ):
            differences = np.asarray(
                [row["cauchy_all_auroc"] - row[baseline] for row in rows],
                dtype=np.float64,
            )
            comparisons[baseline] = {
                "mean_paired_delta": float(differences.mean()),
                "minimum_paired_delta": float(differences.min()),
                "wins": int((differences > 0).sum()),
                "ties": int(np.isclose(differences, 0.0).sum()),
                "number_of_runs": len(differences),
            }
        output["cauchy_all_comparisons"] = comparisons
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, ensure_ascii=False, indent=2)
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
