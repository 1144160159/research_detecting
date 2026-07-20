from __future__ import annotations

import argparse
import json
import pickle
import time
from pathlib import Path

import numpy as np

from caeos.data import MultiViewFlowDataset, prepare_tabular_open_set
from caeos.foss import FOSSForest
from caeos.hybrid_open_set import evaluate_hybrid_open_set


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Same-split FOSS open-set baseline")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--unknown-classes", required=True)
    parser.add_argument("--benign-class", default="Benign")
    parser.add_argument(
        "--split-strategy",
        choices=("random", "fingerprint_grouped", "capture_grouped"),
        default="fingerprint_grouped",
    )
    parser.add_argument("--max-per-class", type=int, default=2000)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--foss-trees", type=int, default=30)
    parser.add_argument("--foss-subsample-size", type=int, default=100)
    parser.add_argument("--foss-candidate-dimensions", type=int, default=5)
    parser.add_argument("--foss-min-samples", type=int, default=1)
    parser.add_argument("--known-acceptance", type=float, default=0.95)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def matrix(dataset: MultiViewFlowDataset) -> np.ndarray:
    return np.concatenate([view.numpy() for view in dataset.views], axis=1)


def main() -> None:
    args = parse_arguments()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(args.config, "r", encoding="utf-8") as handle:
        config = json.load(handle)
    unknown_classes = [
        value.strip() for value in args.unknown_classes.split(",") if value.strip()
    ]
    bundle = prepare_tabular_open_set(
        args.csv,
        config,
        unknown_classes,
        args.benign_class,
        args.max_per_class,
        args.chunksize,
        args.seed,
        args.split_strategy,
    )
    train_values = matrix(bundle.train)
    validation_values = matrix(bundle.validation)
    test_values = matrix(bundle.test)
    train_labels = bundle.train.labels.numpy()
    validation_labels = bundle.validation.labels.numpy()
    test_labels = bundle.test.labels.numpy()
    test_unknown = bundle.test.is_unknown.numpy().astype(bool)

    model = FOSSForest(
        num_trees=args.foss_trees,
        subsample_size=args.foss_subsample_size,
        candidate_dimensions=args.foss_candidate_dimensions,
        min_samples=args.foss_min_samples,
        seed=args.seed,
    )
    started = time.perf_counter()
    model.fit(train_values, train_labels)
    training_seconds = time.perf_counter() - started
    validation_prediction, validation_risk, _ = model.predict(validation_values)
    test_prediction, test_risk, _ = model.predict(test_values)
    threshold = float(np.quantile(validation_risk, args.known_acceptance))
    report = evaluate_hybrid_open_set(
        test_labels, test_unknown, test_prediction, test_risk, threshold
    )
    result = {
        "model": "foss",
        "unknown_classes": unknown_classes,
        "seed": args.seed,
        "known_class_names": bundle.class_names,
        "sample_counts": bundle.sample_counts,
        "split_metadata": bundle.split_metadata,
        "split_sizes": {
            "train": len(bundle.train),
            "validation": len(bundle.validation),
            "test": len(bundle.test),
            "test_unknown": int(test_unknown.sum()),
        },
        "validation_thresholds": {"foss": threshold},
        "reports": {"foss": report},
        "auxiliary_reports": {},
        "training_history": [],
        "training_seconds": training_seconds,
        "trainable_parameters": 0,
        "implementation": (
            "FOSS Algorithms 1-3 reimplemented from the TON 2024 paper: "
            "weighted-entropy Monte Carlo isolation trees, short-path and "
            "leaf-cloud deviation voting; shared features and known-only calibration"
        ),
        "source_boundary": (
            "official Secbrain/FOSS commit 77d9bcdb omits the imported FOSS.py; "
            "this is a paper-faithful reimplementation, not an official-code run"
        ),
        "selection_evidence": {
            "protocol": "strict_known_only",
            "model_fit": {
                "split": "known_only_train",
                "criterion": "fixed_paper_algorithm_and_hyperparameters",
            },
            "checkpoint_selection": {
                "split": "none",
                "criterion": "non_iterative_forest",
            },
            "deployment_thresholds": {
                "foss": {
                    "split": "known_only_validation",
                    "known_acceptance_quantile": args.known_acceptance,
                    "value": threshold,
                }
            },
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
            "test_labels_used_for_final_metrics_only": True,
        },
        "arguments": vars(args),
    }
    with (output_dir / "metrics.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    np.savez_compressed(
        output_dir / "scores.npz",
        validation_labels=validation_labels,
        validation_foss=validation_risk,
        test_labels=test_labels,
        test_unknown=test_unknown,
        test_foss=test_risk,
        prediction_foss=test_prediction,
    )
    with (output_dir / "model.pkl").open("wb") as handle:
        pickle.dump(model, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print("metrics=" + json.dumps({"foss": report}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
