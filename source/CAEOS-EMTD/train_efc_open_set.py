from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
from joblib import parallel_backend

from caeos.data import MultiViewFlowDataset, prepare_tabular_open_set
from caeos.hybrid_open_set import evaluate_hybrid_open_set


EFC_UPSTREAM_COMMIT = "2b935be347abf7daf4420989ef391436db418eac"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Strict-protocol open-set Energy-based Flow Classifier baseline"
    )
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
    parser.add_argument("--known-acceptance", type=float, default=0.95)
    parser.add_argument("--pseudocounts", type=float, default=0.5)
    parser.add_argument("--cutoff-quantile", type=float, default=0.95)
    parser.add_argument("--n-bins", type=int, default=30)
    parser.add_argument("--jobs", type=int, default=-1)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def matrix(dataset: MultiViewFlowDataset) -> np.ndarray:
    return np.concatenate([view.numpy() for view in dataset.views], axis=1)


def load_efc_class() -> type[Any]:
    try:
        from efc import EnergyBasedFlowClassifier
    except ImportError as exc:
        raise RuntimeError(
            "The official EFC package is required. Install pinned commit "
            f"{EFC_UPSTREAM_COMMIT} from "
            "https://github.com/EnergyBasedFlowClassifier/EFC-package."
        ) from exc
    return EnergyBasedFlowClassifier


def energy_margin_risk(
    model: Any, prediction: np.ndarray, minimum_energy: np.ndarray
) -> np.ndarray:
    classes = np.asarray(model.classes_)
    estimators = list(model.estimators_)
    predicted = np.asarray(prediction)
    energy = np.asarray(minimum_energy, dtype=np.float64)
    if predicted.shape != energy.shape or predicted.ndim != 1:
        raise ValueError("prediction and minimum energy must be aligned vectors")
    if len(classes) < 3 or len(estimators) != len(classes):
        raise ValueError("strict EFC baseline requires at least three known classes")
    class_to_index = {value.item() if hasattr(value, "item") else value: index for index, value in enumerate(classes)}
    try:
        indices = np.asarray(
            [class_to_index[value.item() if hasattr(value, "item") else value] for value in predicted],
            dtype=np.int64,
        )
    except KeyError as exc:
        raise ValueError(f"EFC predicted an unknown fitted class: {exc}") from exc
    cutoffs = np.asarray([float(estimator.cutoff_) for estimator in estimators])
    if not np.isfinite(cutoffs).all() or not np.isfinite(energy).all():
        raise ValueError("EFC energies and class cutoffs must be finite")
    return energy - cutoffs[indices]


def main() -> None:
    args = parse_arguments()
    if not 0.0 < args.known_acceptance < 1.0:
        raise ValueError("--known-acceptance must be in (0, 1)")
    if not 0.0 < args.pseudocounts < 1.0:
        raise ValueError("--pseudocounts must be in (0, 1)")
    if not 0.0 < args.cutoff_quantile < 1.0:
        raise ValueError("--cutoff-quantile must be in (0, 1)")
    if args.n_bins < 2:
        raise ValueError("--n-bins must be at least 2")

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

    EnergyBasedFlowClassifier = load_efc_class()
    model = EnergyBasedFlowClassifier(
        pseudocounts=args.pseudocounts,
        cutoff_quantile=args.cutoff_quantile,
        n_bins=args.n_bins,
        n_jobs=args.jobs,
    )
    started = time.perf_counter()
    with parallel_backend("threading", n_jobs=args.jobs):
        model.fit(train_values, train_labels)
    training_seconds = time.perf_counter() - started
    if getattr(model, "target_type_", None) != "multiclass":
        raise ValueError("strict EFC baseline requires multiclass known training data")

    started = time.perf_counter()
    with parallel_backend("threading", n_jobs=args.jobs):
        validation_prediction, validation_energy = model.predict(
            validation_values, return_energies=True, unknown_class=False
        )
        test_prediction, test_energy = model.predict(
            test_values, return_energies=True, unknown_class=False
        )
    inference_seconds = time.perf_counter() - started
    validation_risk = energy_margin_risk(
        model, validation_prediction, validation_energy
    )
    test_risk = energy_margin_risk(model, test_prediction, test_energy)
    threshold = float(np.quantile(validation_risk, args.known_acceptance))
    report = evaluate_hybrid_open_set(
        test_labels, test_unknown, test_prediction, test_risk, threshold
    )
    author_cutoff_report = evaluate_hybrid_open_set(
        test_labels, test_unknown, test_prediction, test_risk, 0.0
    )

    result = {
        "model": "efc",
        "method": "official_multiclass_energy_based_flow_classifier",
        "report_name": "efc_energy_margin",
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
        "reports": {"efc_energy_margin": report},
        "auxiliary_reports": {"author_train_cutoff": author_cutoff_report},
        "validation_thresholds": {"efc_energy_margin": threshold},
        "author_train_cutoff_margin": 0.0,
        "class_energy_cutoffs": {
            str(class_name): float(estimator.cutoff_)
            for class_name, estimator in zip(model.classes_, model.estimators_)
        },
        "training_history": [],
        "training_seconds": float(training_seconds),
        "inference_seconds": float(inference_seconds),
        "inference_samples_per_second": float(
            (len(validation_values) + len(test_values))
            / max(inference_seconds, 1e-12)
        ),
        "trainable_parameters": 0,
        "implementation": (
            "Official multiclass EnergyBasedFlowClassifier. The anomaly score is "
            "the author's minimum class energy minus the predicted class cutoff; "
            "the strict main threshold is the known-validation quantile. The "
            "joblib threading backend avoids read-only loky memory maps passed to "
            "the upstream Cython energy kernel without changing its computation."
        ),
        "source_boundary": (
            "Official BSD-3-Clause EFC-package pinned to commit "
            f"{EFC_UPSTREAM_COMMIT}; CAEOS code only adapts data splits, the scalar "
            "energy margin, validation thresholding, metrics, and artifact output."
        ),
        "selection_evidence": {
            "unknown_or_test_labels_used_for_training": False,
            "unknown_or_test_labels_used_for_preprocessing": False,
            "unknown_or_test_labels_used_for_thresholds": False,
            "author_native_unknown_rule_preserved_as_auxiliary_report": True,
        },
        "upstream": {
            "repository": "https://github.com/EnergyBasedFlowClassifier/EFC-package",
            "commit": EFC_UPSTREAM_COMMIT,
            "license": "BSD-3-Clause",
            "paper_doi": "10.1016/j.cose.2025.104569",
        },
        "arguments": vars(args),
    }
    (output_dir / "metrics.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    np.savez_compressed(
        output_dir / "scores.npz",
        validation_labels=validation_labels,
        validation_prediction=validation_prediction,
        validation_energy=validation_energy,
        validation_efc_energy_margin=validation_risk,
        test_labels=test_labels,
        test_unknown=test_unknown,
        test_prediction=test_prediction,
        test_energy=test_energy,
        test_efc_energy_margin=test_risk,
    )
    print("metrics=" + json.dumps(report, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
