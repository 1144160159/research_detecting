from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze validation-calibrated hybrid/neural prediction conflict"
    )
    parser.add_argument("--hybrid-root", required=True)
    parser.add_argument("--neural-root", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def empirical_upper_tail(reference: np.ndarray, values: np.ndarray) -> np.ndarray:
    ordered = np.sort(np.asarray(reference, dtype=np.float64))
    rank = np.searchsorted(ordered, np.asarray(values, dtype=np.float64), side="right")
    return rank.astype(np.float64) / max(1, len(ordered))


def risks(hybrid, neural) -> dict[str, np.ndarray]:
    support = empirical_upper_tail(
        hybrid["validation_support_union"], hybrid["test_support_union"]
    )
    neural_tail = empirical_upper_tail(
        neural["validation_mahalanobis"], neural["test_mahalanobis"]
    )
    disagreement = (
        hybrid["test_prediction"] != neural["prediction_mahalanobis"]
    ).astype(np.float64)
    result = {
        "support": support,
        "neural_mahalanobis": neural_tail,
        "prediction_disagreement": disagreement,
        "rescue_max": np.where(disagreement > 0, np.maximum(support, neural_tail), support),
    }
    for weight in (0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1.00):
        suffix = ("%.2f" % weight).replace(".", "p")
        result[f"disagreement_add_{suffix}"] = support + weight * disagreement
        result[f"gated_neural_add_{suffix}"] = (
            support + weight * disagreement * neural_tail
        )
    return result


def main() -> None:
    args = parse_arguments()
    hybrid_root = Path(args.hybrid_root)
    neural_root = Path(args.neural_root)
    rows = []
    for metrics_path in sorted(hybrid_root.glob("*_seed*/metrics.json")):
        run_name = metrics_path.parent.name
        neural_dir = neural_root / f"{run_name}_mlp"
        hybrid = np.load(metrics_path.parent / "scores.npz")
        neural = np.load(neural_dir / "scores.npz")
        if not np.array_equal(hybrid["test_unknown"], neural["test_unknown"]):
            raise ValueError(f"test split mismatch for {run_name}")
        if not np.array_equal(hybrid["test_labels"], neural["test_labels"]):
            raise ValueError(f"test label mismatch for {run_name}")
        target = hybrid["test_unknown"].astype(np.int64)
        scenario, seed_text = run_name.rsplit("_seed", 1)
        score_map = risks(hybrid, neural)
        row = {
            "scenario": scenario,
            "seed": int(seed_text),
            "known_disagreement_rate": float(
                score_map["prediction_disagreement"][target == 0].mean()
            ),
            "unknown_disagreement_rate": float(
                score_map["prediction_disagreement"][target == 1].mean()
            ),
            "auroc": {
                name: float(roc_auc_score(target, score))
                for name, score in score_map.items()
            },
        }
        rows.append(row)

    names = sorted(rows[0]["auroc"])
    summary = {}
    for name in names:
        values = np.asarray([row["auroc"][name] for row in rows])
        summary[name] = {
            "mean_auroc": float(values.mean()),
            "std_auroc": float(values.std()),
            "minimum_auroc": float(values.min()),
            "wins_vs_support": int(
                sum(
                    row["auroc"][name] > row["auroc"]["support"] + 1e-12
                    for row in rows
                )
            ),
            "losses_vs_support": int(
                sum(
                    row["auroc"][name] < row["auroc"]["support"] - 1e-12
                    for row in rows
                )
            ),
        }
    result = {
        "number_of_runs": len(rows),
        "mean_known_disagreement_rate": float(
            np.mean([row["known_disagreement_rate"] for row in rows])
        ),
        "mean_unknown_disagreement_rate": float(
            np.mean([row["unknown_disagreement_rate"] for row in rows])
        ),
        "summary": summary,
        "runs": rows,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
