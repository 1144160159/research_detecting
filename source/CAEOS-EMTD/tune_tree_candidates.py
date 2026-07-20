from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.metrics import f1_score

from caeos.data import prepare_tabular_closed_set
from caeos.multiclass import multiclass_report


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validation-only tree search")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--benign-class", default="benign")
    parser.add_argument("--max-per-class", type=int, default=100000)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--estimators", type=int, default=300)
    parser.add_argument("--jobs", type=int, default=-1)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


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
    train = np.concatenate([view.numpy() for view in bundle.train.views], axis=1)
    validation = np.concatenate(
        [view.numpy() for view in bundle.validation.views], axis=1
    )
    test = np.concatenate([view.numpy() for view in bundle.test.views], axis=1)
    train_labels = bundle.train.labels.numpy()
    validation_labels = bundle.validation.labels.numpy()

    specifications = []
    for max_features in ("sqrt", 0.25, 0.5, 0.75):
        specifications.append(("random_forest", max_features))
    for max_features in ("sqrt", 0.25, 0.5):
        specifications.append(("extra_trees", max_features))

    validation_results = []
    trained = []
    start = time.perf_counter()
    for index, (family, max_features) in enumerate(specifications):
        classifier = (
            RandomForestClassifier if family == "random_forest" else ExtraTreesClassifier
        )(
            n_estimators=args.estimators,
            max_features=max_features,
            class_weight="balanced_subsample",
            n_jobs=args.jobs,
            random_state=args.seed + index * 101,
        )
        classifier.fit(train, train_labels)
        probability = classifier.predict_proba(validation)
        macro_f1 = float(
            f1_score(
                validation_labels,
                probability.argmax(axis=1),
                average="macro",
                zero_division=0,
            )
        )
        result = {
            "family": family,
            "max_features": max_features,
            "validation_macro_f1": macro_f1,
        }
        validation_results.append(result)
        trained.append((classifier, probability, result))

    best = None
    for left in range(len(trained)):
        for right in range(left, len(trained)):
            weights = (1.0,) if left == right else np.linspace(0.0, 1.0, 101)
            for left_weight in weights:
                probability = (
                    left_weight * trained[left][1]
                    + (1.0 - left_weight) * trained[right][1]
                )
                macro_f1 = float(
                    f1_score(
                        validation_labels,
                        probability.argmax(axis=1),
                        average="macro",
                        zero_division=0,
                    )
                )
                candidate = (
                    macro_f1,
                    -abs(float(left_weight) - 0.5),
                    -left,
                    -right,
                )
                if best is None or candidate > best[0]:
                    best = (candidate, left, right, float(left_weight))

    _, left, right, left_weight = best
    selected = {
        "left": trained[left][2],
        "right": trained[right][2],
        "left_weight": left_weight,
        "validation_macro_f1": best[0][0],
    }
    test_probability = (
        left_weight * trained[left][0].predict_proba(test)
        + (1.0 - left_weight) * trained[right][0].predict_proba(test)
    )
    test_report = multiclass_report(
        bundle.test.labels,
        torch.as_tensor(test_probability, dtype=torch.float32),
        bundle.class_names,
    )
    output = {
        "selection_rule": "maximum validation macro-F1; test evaluated once",
        "validation_results": validation_results,
        "selected": selected,
        "test": {
            key: test_report[key]
            for key in (
                "accuracy",
                "f1_weighted",
                "f1_macro",
                "balanced_accuracy",
                "ece",
                "nll",
            )
        },
        "elapsed_seconds": time.perf_counter() - start,
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, ensure_ascii=False, indent=2)
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
