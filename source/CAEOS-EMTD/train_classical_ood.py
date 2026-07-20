from __future__ import annotations

import argparse
import json
import pickle
import time
from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM

from caeos.data import MultiViewFlowDataset, prepare_tabular_open_set
from caeos.hybrid_open_set import evaluate_hybrid_open_set


METHODS = (
    "isolation_forest",
    "one_class_svm",
    "local_outlier_factor",
    "pca_reconstruction",
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Shared-classifier classical one-class OOD baselines"
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
    parser.add_argument("--detector-max-samples", type=int, default=5000)
    parser.add_argument("--isolation-trees", type=int, default=200)
    parser.add_argument("--ocsvm-nu", type=float, default=0.05)
    parser.add_argument("--lof-neighbors", type=int, default=20)
    parser.add_argument("--pca-components", type=int, default=64)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def matrix(dataset: MultiViewFlowDataset) -> np.ndarray:
    return np.concatenate([view.numpy() for view in dataset.views], axis=1)


def balanced_subsample_indices(
    labels: np.ndarray, maximum: int, seed: int
) -> np.ndarray:
    labels = np.asarray(labels, dtype=np.int64)
    if maximum <= 0 or len(labels) <= maximum:
        return np.arange(len(labels), dtype=np.int64)
    classes = np.unique(labels)
    rng = np.random.default_rng(seed)
    quota = max(1, maximum // len(classes))
    selected: list[int] = []
    remaining: list[int] = []
    for class_index in classes:
        indices = np.flatnonzero(labels == class_index)
        shuffled = rng.permutation(indices)
        take = min(quota, len(shuffled))
        selected.extend(int(value) for value in shuffled[:take])
        remaining.extend(int(value) for value in shuffled[take:])
    capacity = maximum - len(selected)
    if capacity > 0 and remaining:
        selected.extend(
            int(value) for value in rng.permutation(remaining)[:capacity]
        )
    return np.asarray(sorted(selected), dtype=np.int64)


def detector_risks(
    fit_values: np.ndarray,
    validation_values: np.ndarray,
    test_values: np.ndarray,
    args: argparse.Namespace,
) -> tuple[dict[str, tuple[np.ndarray, np.ndarray]], dict[str, object], dict[str, float]]:
    if len(fit_values) < 3:
        raise ValueError("classical OOD detectors require at least three fit samples")
    models: dict[str, object] = {}
    timings: dict[str, float] = {}
    risks: dict[str, tuple[np.ndarray, np.ndarray]] = {}

    started = time.perf_counter()
    isolation = IsolationForest(
        n_estimators=args.isolation_trees,
        max_samples=min(256, len(fit_values)),
        contamination="auto",
        random_state=args.seed,
        n_jobs=-1,
    ).fit(fit_values)
    timings["isolation_forest"] = time.perf_counter() - started
    models["isolation_forest"] = isolation
    risks["isolation_forest"] = (
        -isolation.decision_function(validation_values),
        -isolation.decision_function(test_values),
    )

    started = time.perf_counter()
    ocsvm = OneClassSVM(kernel="rbf", gamma="scale", nu=args.ocsvm_nu).fit(
        fit_values
    )
    timings["one_class_svm"] = time.perf_counter() - started
    models["one_class_svm"] = ocsvm
    risks["one_class_svm"] = (
        -ocsvm.decision_function(validation_values),
        -ocsvm.decision_function(test_values),
    )

    neighbors = min(args.lof_neighbors, len(fit_values) - 1)
    started = time.perf_counter()
    lof = LocalOutlierFactor(
        n_neighbors=neighbors,
        novelty=True,
        contamination="auto",
        n_jobs=-1,
    ).fit(fit_values)
    timings["local_outlier_factor"] = time.perf_counter() - started
    models["local_outlier_factor"] = lof
    risks["local_outlier_factor"] = (
        -lof.decision_function(validation_values),
        -lof.decision_function(test_values),
    )

    components = max(
        1,
        min(args.pca_components, fit_values.shape[1], len(fit_values) - 1),
    )
    started = time.perf_counter()
    pca = PCA(
        n_components=components,
        svd_solver="randomized" if components < fit_values.shape[1] else "full",
        random_state=args.seed,
    ).fit(fit_values)
    timings["pca_reconstruction"] = time.perf_counter() - started
    models["pca_reconstruction"] = pca

    def reconstruction_risk(values: np.ndarray) -> np.ndarray:
        reconstructed = pca.inverse_transform(pca.transform(values))
        return np.square(values - reconstructed).mean(axis=1)

    risks["pca_reconstruction"] = (
        reconstruction_risk(validation_values),
        reconstruction_risk(test_values),
    )
    return risks, models, timings


def main() -> None:
    args = parse_arguments()
    if not 0.0 < args.known_acceptance < 1.0:
        raise ValueError("--known-acceptance must be in (0, 1)")
    if not 0.0 < args.ocsvm_nu < 1.0:
        raise ValueError("--ocsvm-nu must be in (0, 1)")
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
    raw_train = matrix(bundle.train)
    raw_validation = matrix(bundle.validation)
    raw_test = matrix(bundle.test)
    train_labels = bundle.train.labels.numpy()
    validation_labels = bundle.validation.labels.numpy()
    test_labels = bundle.test.labels.numpy()
    test_unknown = bundle.test.is_unknown.numpy().astype(bool)

    scaler = StandardScaler().fit(raw_train)
    train_values = scaler.transform(raw_train)
    validation_values = scaler.transform(raw_validation)
    test_values = scaler.transform(raw_test)
    classifier_started = time.perf_counter()
    classifier = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        solver="lbfgs",
        random_state=args.seed,
        n_jobs=-1,
    ).fit(train_values, train_labels)
    classifier_seconds = time.perf_counter() - classifier_started
    prediction = classifier.predict(test_values)

    fit_indices = balanced_subsample_indices(
        train_labels, args.detector_max_samples, args.seed
    )
    risks, detectors, detector_seconds = detector_risks(
        train_values[fit_indices], validation_values, test_values, args
    )
    thresholds = {}
    reports = {}
    for method, (validation_risk, test_risk) in risks.items():
        threshold = float(np.quantile(validation_risk, args.known_acceptance))
        thresholds[method] = threshold
        reports[method] = evaluate_hybrid_open_set(
            test_labels, test_unknown, prediction, test_risk, threshold
        )

    result = {
        "model": "classical_ood",
        "method": "shared_logistic_classical_one_class_detectors",
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
        "detector_fit_size": len(fit_indices),
        "reports": reports,
        "auxiliary_reports": {},
        "validation_thresholds": thresholds,
        "training_history": [],
        "training_seconds": float(
            classifier_seconds + sum(detector_seconds.values())
        ),
        "training_seconds_by_component": {
            "known_classifier": classifier_seconds,
            **detector_seconds,
        },
        "resource_usage_by_report": {
            method: {
                "training_seconds": float(
                    classifier_seconds + detector_seconds[method]
                )
            }
            for method in METHODS
        },
        "trainable_parameters": 0,
        "implementation": (
            "Protocol-adapted classical baselines: shared known-only StandardScaler "
            "and class-balanced LogisticRegression, with Isolation Forest, RBF "
            "One-Class SVM, novelty LOF, and PCA reconstruction risks fitted only "
            "on known training samples; thresholds use known validation only"
        ),
        "source_boundary": (
            "scikit-learn reference implementations under a shared CAEOS split; "
            "these are protocol adaptations, not original-paper code releases"
        ),
        "selection_evidence": {
            "unknown_or_test_labels_used_for_training": False,
            "unknown_or_test_labels_used_for_thresholds": False,
            "detector_subsample_is_class_balanced": True,
        },
        "arguments": vars(args),
    }
    (output_dir / "metrics.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    score_payload = {
        "validation_labels": validation_labels,
        "test_labels": test_labels,
        "test_unknown": test_unknown,
        "test_prediction": prediction,
    }
    for method, (validation_risk, test_risk) in risks.items():
        score_payload[f"validation_{method}"] = validation_risk
        score_payload[f"test_{method}"] = test_risk
    np.savez_compressed(output_dir / "scores.npz", **score_payload)
    with (output_dir / "model.pkl").open("wb") as handle:
        pickle.dump(
            {
                "scaler": scaler,
                "known_classifier": classifier,
                "detectors": detectors,
                "detector_fit_indices": fit_indices,
            },
            handle,
            protocol=pickle.HIGHEST_PROTOCOL,
        )
    print("metrics=" + json.dumps(reports, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
