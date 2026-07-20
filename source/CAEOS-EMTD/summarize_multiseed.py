from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize MC5 multi-seed runs")
    parser.add_argument("--root", required=True)
    parser.add_argument("--target", type=float, default=0.9693)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    rows = []
    for path in sorted(Path(args.root).glob("mc5_seed*/metrics.json")):
        with path.open("r", encoding="utf-8") as handle:
            report = json.load(handle)
        ablation = report["test_ablation"]
        seed = int(path.parent.name.removeprefix("mc5_seed"))
        rf = float(ablation["random_forest"]["macro_f1"])
        et = float(ablation["extra_trees"]["macro_f1"])
        global_f1 = float(ablation["validation_weighted_global"]["macro_f1"])
        final = float(ablation["conflict_gated_final"]["macro_f1"])
        rows.append(
            {
                "seed": seed,
                "random_forest_macro_f1": rf,
                "extra_trees_macro_f1": et,
                "global_ensemble_macro_f1": global_f1,
                "mc5_macro_f1": final,
                "mc5_minus_rf": final - rf,
                "mc5_above_target": final > args.target,
                "rf_weight": float(report["global_rf_weight"]),
                "view_weight": float(report["view_weight"]),
                "mean_conflict": float(report["mean_test_conflict"]),
            }
        )
    if not rows:
        raise FileNotFoundError(f"No metrics found below {args.root}")

    def stats(key: str) -> dict[str, float]:
        values = np.asarray([row[key] for row in rows], dtype=np.float64)
        return {
            "mean": float(values.mean()),
            "std": float(values.std(ddof=1)) if len(values) > 1 else 0.0,
            "min": float(values.min()),
            "max": float(values.max()),
        }

    summary = {
        "target_macro_f1": args.target,
        "number_of_seeds": len(rows),
        "per_seed": rows,
        "aggregate": {
            "random_forest_macro_f1": stats("random_forest_macro_f1"),
            "extra_trees_macro_f1": stats("extra_trees_macro_f1"),
            "global_ensemble_macro_f1": stats("global_ensemble_macro_f1"),
            "mc5_macro_f1": stats("mc5_macro_f1"),
            "mc5_minus_rf": stats("mc5_minus_rf"),
            "target_pass_rate": float(
                np.mean([row["mc5_above_target"] for row in rows])
            ),
        },
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
