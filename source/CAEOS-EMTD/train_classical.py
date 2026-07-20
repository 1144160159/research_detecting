from __future__ import annotations

import argparse
import json
import pickle
import time
from pathlib import Path

import numpy as np
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.utils.class_weight import compute_sample_weight

from caeos.data import make_synthetic_multiclass, prepare_tabular_closed_set
from caeos.multiclass import multiclass_report


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classical multiclass traffic baselines")
    parser.add_argument(
        "--model",
        choices=("random_forest", "extra_trees", "xgboost"),
        default="random_forest",
    )
    parser.add_argument("--dataset", choices=("synthetic", "tabular"), default="synthetic")
    parser.add_argument("--csv", default=None)
    parser.add_argument("--config", default="configs/nf_unsw_nb15.json")
    parser.add_argument("--benign-class", default="Benign")
    parser.add_argument("--max-per-class", type=int, default=5000)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--estimators", type=int, default=300)
    parser.add_argument("--max-depth", type=int, default=None)
    parser.add_argument("--min-samples-leaf", type=int, default=1)
    parser.add_argument("--learning-rate", type=float, default=0.05)
    parser.add_argument("--subsample", type=float, default=0.9)
    parser.add_argument("--colsample-bytree", type=float, default=0.9)
    parser.add_argument("--early-stopping-rounds", type=int, default=30)
    parser.add_argument("--jobs", type=int, default=-1)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output-dir", default="runs/multiclass/random_forest_seed7")
    return parser.parse_args()


def features(dataset) -> np.ndarray:
    return np.concatenate([view.numpy() for view in dataset.views], axis=1)


def json_dump(path: Path, value: object) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)


def main() -> None:
    args = parse_arguments()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.dataset == "synthetic":
        bundle = make_synthetic_multiclass(seed=args.seed)
    else:
        if not args.csv:
            raise ValueError("--csv is required for tabular data")
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

    if args.model in {"random_forest", "extra_trees"}:
        common = dict(
            n_estimators=args.estimators,
            max_depth=args.max_depth,
            min_samples_leaf=args.min_samples_leaf,
            class_weight="balanced_subsample",
            n_jobs=args.jobs,
            random_state=args.seed,
        )
        model = (
            RandomForestClassifier(**common)
            if args.model == "random_forest"
            else ExtraTreesClassifier(**common)
        )
    else:
        try:
            from xgboost import XGBClassifier
        except ImportError as exc:
            raise RuntimeError(
                "xgboost is required for --model xgboost; install it in an isolated "
                "PYTHONPATH or the active environment"
            ) from exc
        model = XGBClassifier(
            n_estimators=args.estimators,
            max_depth=args.max_depth or 8,
            learning_rate=args.learning_rate,
            subsample=args.subsample,
            colsample_bytree=args.colsample_bytree,
            objective="multi:softprob",
            eval_metric="mlogloss",
            tree_method="hist",
            early_stopping_rounds=args.early_stopping_rounds,
            n_jobs=args.jobs,
            random_state=args.seed,
        )

    x_train = features(bundle.train)
    y_train = bundle.train.labels.numpy()
    x_validation = features(bundle.validation)
    y_validation = bundle.validation.labels.numpy()
    x_test = features(bundle.test)
    start = time.perf_counter()
    if args.model == "xgboost":
        model.fit(
            x_train,
            y_train,
            sample_weight=compute_sample_weight("balanced", y_train),
            eval_set=[(x_validation, y_validation)],
            verbose=False,
        )
    else:
        model.fit(x_train, y_train)
    training_seconds = time.perf_counter() - start
    start = time.perf_counter()
    probabilities = model.predict_proba(x_test)
    inference_seconds = time.perf_counter() - start

    import torch

    report = multiclass_report(
        bundle.test.labels,
        torch.as_tensor(probabilities, dtype=torch.float32),
        bundle.class_names,
    )
    report.update(
        {
            "model": args.model,
            "seed": args.seed,
            "estimators": args.estimators,
            "training_seconds": training_seconds,
            "inference_seconds": inference_seconds,
            "inference_samples_per_second": len(x_test) / max(inference_seconds, 1e-9),
            "selection_evidence": {
                "checkpoint_or_iteration_selection": (
                    "known_validation_mlogloss_early_stopping"
                    if args.model == "xgboost"
                    else "not_applicable_fixed_tree_budget"
                ),
                "unknown_or_test_labels_used_for_fitting_or_selection": False,
            },
        }
    )
    if args.model == "xgboost":
        report["best_iteration"] = int(model.best_iteration)
        report["learning_rate"] = args.learning_rate
        report["subsample"] = args.subsample
        report["colsample_bytree"] = args.colsample_bytree
    print("metrics=" + json.dumps(report, ensure_ascii=False, sort_keys=True))
    with (output_dir / "model.pkl").open("wb") as handle:
        pickle.dump(model, handle, protocol=pickle.HIGHEST_PROTOCOL)
    json_dump(output_dir / "metrics.json", report)
    json_dump(
        output_dir / "data_metadata.json",
        {
            "class_names": bundle.class_names,
            "modality_names": bundle.modality_names,
            "input_dims": bundle.input_dims,
            "sample_counts": bundle.sample_counts,
            "split_sizes": {
                "train": len(bundle.train),
                "validation": len(bundle.validation),
                "test": len(bundle.test),
            },
        },
    )


if __name__ == "__main__":
    main()
