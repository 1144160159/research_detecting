from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import f1_score

from caeos.data import prepare_tabular_closed_set
from caeos.multiclass import multiclass_report


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Select an RF/ET convex ensemble on validation data"
    )
    parser.add_argument("--csv", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--benign-class", default="benign")
    parser.add_argument("--max-per-class", type=int, default=500)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--random-forest", required=True)
    parser.add_argument("--extra-trees", required=True)
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def features(dataset) -> np.ndarray:
    return np.concatenate([view.numpy() for view in dataset.views], axis=1)


def main() -> None:
    args = parse_arguments()
    with open(args.config, "r", encoding="utf-8") as handle:
        config = json.load(handle)
    bundle = prepare_tabular_closed_set(
        args.csv,
        config,
        args.benign_class,
        args.max_per_class,
        args.chunksize,
        args.seed,
    )
    with open(args.random_forest, "rb") as handle:
        random_forest = pickle.load(handle)
    with open(args.extra_trees, "rb") as handle:
        extra_trees = pickle.load(handle)

    validation_x = features(bundle.validation)
    test_x = features(bundle.test)
    validation_y = bundle.validation.labels.numpy()
    rf_validation = random_forest.predict_proba(validation_x)
    et_validation = extra_trees.predict_proba(validation_x)

    candidates = []
    for rf_weight in np.linspace(0.0, 1.0, 101):
        probability = rf_weight * rf_validation + (1.0 - rf_weight) * et_validation
        score = f1_score(
            validation_y, probability.argmax(axis=1), average="macro", zero_division=0
        )
        candidates.append((float(score), float(rf_weight)))
    validation_score, rf_weight = max(candidates, key=lambda item: (item[0], -item[1]))

    test_probability = (
        rf_weight * random_forest.predict_proba(test_x)
        + (1.0 - rf_weight) * extra_trees.predict_proba(test_x)
    )
    report = multiclass_report(
        bundle.test.labels,
        torch.as_tensor(test_probability, dtype=torch.float32),
        bundle.class_names,
    )
    report.update(
        {
            "model": "rf_et_validation_ensemble",
            "rf_weight": rf_weight,
            "et_weight": 1.0 - rf_weight,
            "validation_macro_f1": validation_score,
        }
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
