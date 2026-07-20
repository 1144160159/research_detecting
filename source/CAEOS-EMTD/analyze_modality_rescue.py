from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon
from sklearn.metrics import roc_auc_score


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sweep fixed validation-calibrated modality rescue weights"
    )
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--weights", default="0.01,0.02,0.05,0.10,0.15,0.20,0.30,0.40,0.50")
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    weights = [float(value) for value in args.weights.split(",") if value.strip()]
    rows = []
    for score_path in sorted(Path(args.root).glob("*_seed*/scores.npz")):
        archive = np.load(score_path)
        run_name = score_path.parent.name
        scenario, seed_text = run_name.rsplit("_seed", 1)
        target = archive["test_unknown"].astype(np.int64)
        support = archive["test_support_union"]
        row = {
            "scenario": scenario,
            "seed": int(seed_text),
            "auroc": {"support": float(roc_auc_score(target, support))},
        }
        view_names = sorted(
            name.removeprefix("test_")
            for name in archive.files
            if name.startswith("test_knn_view_")
        )
        for view_name in view_names:
            view_risk = archive[f"test_{view_name}"]
            row["auroc"][view_name] = float(roc_auc_score(target, view_risk))
            for weight in weights:
                candidate = (1.0 - weight) * support + weight * view_risk
                key = f"support_{view_name}_w{weight:.2f}"
                row["auroc"][key] = float(roc_auc_score(target, candidate))
        rows.append(row)

    names = sorted(rows[0]["auroc"])
    summary = {}
    for name in names:
        values = np.asarray([row["auroc"][name] for row in rows])
        support = np.asarray([row["auroc"]["support"] for row in rows])
        summary[name] = {
            "mean_auroc": float(values.mean()),
            "minimum_auroc": float(values.min()),
            "mean_delta": float((values - support).mean()),
            "wins": int((values > support + 1e-12).sum()),
            "losses": int((values < support - 1e-12).sum()),
            "wilcoxon_p": float(
                1.0
                if np.allclose(values, support)
                else wilcoxon(values - support, alternative="two-sided").pvalue
            ),
        }
    result = {"number_of_runs": len(rows), "summary": summary, "runs": rows}
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    best = sorted(
        summary.items(), key=lambda item: item[1]["mean_auroc"], reverse=True
    )[:20]
    print(json.dumps(dict(best), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
