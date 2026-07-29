from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.utils.class_weight import compute_sample_weight

from caeos.data import prepare_tabular_open_set
from evaluate_strict_v4_benign_calibrated_warning import calibrate_threshold


def canonical_hash(payload: dict[str, Any]) -> str:
    body = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def features(dataset: Any) -> np.ndarray:
    return np.concatenate([view.numpy() for view in dataset.views], axis=1)


def operational_metrics(
    *,
    test_probability: np.ndarray,
    test_labels: np.ndarray,
    test_unknown: np.ndarray,
    benign_index: int,
    alert_threshold: float,
) -> dict[str, float]:
    attack_score = 1.0 - test_probability[:, benign_index]
    predicted_alert = attack_score >= alert_threshold
    actual_attack = test_unknown | (test_labels != benign_index)
    true_positive = int((predicted_alert & actual_attack).sum())
    false_positive = int((predicted_alert & ~actual_attack).sum())
    true_negative = int((~predicted_alert & ~actual_attack).sum())
    false_negative = int((~predicted_alert & actual_attack).sum())
    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive
        else 0.0
    )
    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative
        else 0.0
    )
    malicious_probability = test_probability.copy()
    malicious_probability[:, benign_index] = -np.inf
    type_prediction = malicious_probability.argmax(axis=1)
    known_attack = (~test_unknown) & (test_labels != benign_index)
    correctly_typed = (
        known_attack & predicted_alert & (type_prediction == test_labels)
    )
    return {
        "alert_accuracy": float(
            (true_positive + true_negative) / test_labels.size
        ),
        "alert_precision": float(precision),
        "alert_recall": float(recall),
        "alert_f1": float(
            2.0 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        ),
        "benign_fpr": float(
            false_positive / (false_positive + true_negative)
            if false_positive + true_negative
            else 0.0
        ),
        "known_attack_type_accuracy": float(
            correctly_typed.sum() / known_attack.sum()
            if known_attack.sum()
            else 0.0
        ),
        "unknown_attack_alert_recall": float(
            (test_unknown & predicted_alert).sum() / test_unknown.sum()
            if test_unknown.sum()
            else 0.0
        ),
        "unknown_attack_recall": 0.0,
        "unknown_label_precision": 0.0,
    }


def train_task(
    *,
    pairwise_task_dir: Path,
    cache_csv: Path,
    config_path: Path,
    output_dir: Path,
    xgboost_root: Path,
    validation_benign_fpr_budget: float,
    estimators: int,
    max_depth: int,
    learning_rate: float,
    subsample: float,
    colsample_bytree: float,
    early_stopping_rounds: int,
    jobs: int,
) -> dict[str, Any]:
    if str(xgboost_root) not in sys.path:
        sys.path.insert(0, str(xgboost_root))
    from xgboost import XGBClassifier

    pairwise_paths = {
        "metrics": pairwise_task_dir / "metrics.json",
        "scores": pairwise_task_dir / "scores.npz",
        "provenance": pairwise_task_dir / "provenance.json",
    }
    missing = [name for name, path in pairwise_paths.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"{pairwise_task_dir}: missing {missing}")
    pairwise_metrics = load(pairwise_paths["metrics"])
    pairwise_provenance = load(pairwise_paths["provenance"])
    task = pairwise_provenance["task"]
    seed = int(task["seed"])
    unknown_classes = [str(value) for value in pairwise_metrics["unknown_classes"]]
    known_class_names = [
        str(value) for value in pairwise_metrics["known_class_names"]
    ]
    config = load(config_path)
    bundle = prepare_tabular_open_set(
        csv_path=str(cache_csv),
        config=config,
        unknown_classes=unknown_classes,
        benign_class="Benign",
        max_per_class=5000,
        chunksize=100000,
        seed=seed,
        split_strategy="capture_grouped",
    )
    if bundle.class_names != known_class_names:
        raise ValueError("known class identity differs from Pairwise task")
    with np.load(pairwise_paths["scores"], allow_pickle=False) as pairwise_scores:
        pairwise_validation_labels = np.asarray(
            pairwise_scores["validation_labels"], dtype=np.int64
        )
        pairwise_test_labels = np.asarray(
            pairwise_scores["test_labels"], dtype=np.int64
        )
        pairwise_test_unknown = np.asarray(
            pairwise_scores["test_unknown"], dtype=bool
        )
    validation_labels = bundle.validation.labels.numpy().astype(np.int64)
    test_labels = bundle.test.labels.numpy().astype(np.int64)
    test_unknown = bundle.test.is_unknown.numpy().astype(bool)
    if not (
        np.array_equal(validation_labels, pairwise_validation_labels)
        and np.array_equal(test_labels, pairwise_test_labels)
        and np.array_equal(test_unknown, pairwise_test_unknown)
    ):
        raise ValueError("XGBoost split arrays differ from Pairwise task")

    x_train = features(bundle.train)
    y_train = bundle.train.labels.numpy().astype(np.int64)
    x_validation = features(bundle.validation)
    x_test = features(bundle.test)
    model = XGBClassifier(
        n_estimators=estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        subsample=subsample,
        colsample_bytree=colsample_bytree,
        objective="multi:softprob",
        eval_metric="mlogloss",
        tree_method="hist",
        early_stopping_rounds=early_stopping_rounds,
        n_jobs=jobs,
        random_state=seed,
    )
    started = time.perf_counter()
    model.fit(
        x_train,
        y_train,
        sample_weight=compute_sample_weight("balanced", y_train),
        eval_set=[(x_validation, validation_labels)],
        verbose=False,
    )
    training_seconds = time.perf_counter() - started
    validation_probability = np.asarray(
        model.predict_proba(x_validation), dtype=np.float64
    )
    started = time.perf_counter()
    test_probability = np.asarray(model.predict_proba(x_test), dtype=np.float64)
    inference_seconds = time.perf_counter() - started
    benign_index = known_class_names.index("Benign")
    calibration = calibrate_threshold(
        1.0 - validation_probability[:, benign_index],
        np.full(validation_labels.shape, benign_index, dtype=np.int64),
        validation_labels,
        benign_index,
        validation_benign_fpr_budget,
    )
    if not calibration["feasible"]:
        raise ValueError("validation benign FPR calibration is infeasible")
    metrics = operational_metrics(
        test_probability=test_probability,
        test_labels=test_labels,
        test_unknown=test_unknown,
        benign_index=benign_index,
        alert_threshold=float(calibration["threshold"]),
    )
    gates = {
        "alert_accuracy_at_least_95_percent": metrics["alert_accuracy"] >= 0.95,
        "alert_precision_at_least_95_percent": metrics["alert_precision"] >= 0.95,
        "alert_recall_at_least_95_percent": metrics["alert_recall"] >= 0.95,
        "benign_fpr_below_5_percent": metrics["benign_fpr"] < 0.05,
        "known_attack_type_accuracy_at_least_95_percent": (
            metrics["known_attack_type_accuracy"] >= 0.95
        ),
        "unknown_label_recall_at_least_95_percent": False,
    }
    gates["basic_warning_95_5_gate"] = all(
        gates[key]
        for key in (
            "alert_accuracy_at_least_95_percent",
            "alert_precision_at_least_95_percent",
            "alert_recall_at_least_95_percent",
            "benign_fpr_below_5_percent",
            "known_attack_type_accuracy_at_least_95_percent",
        )
    )
    gates["full_known_unknown_95_5_gate"] = False
    report: dict[str, Any] = {
        "schema_version": "strict_v4_xgboost_warning_task_v1",
        "state": "complete",
        "task": {
            "suite": str(task["suite"]),
            "scenario": str(task["scenario"]),
            "seed": seed,
        },
        "unknown_classes": unknown_classes,
        "known_class_names": known_class_names,
        "validation_benign_fpr_budget": validation_benign_fpr_budget,
        "calibration": calibration,
        "operational_metrics": metrics,
        "gates": gates,
        "model": {
            "name": "XGBoost",
            "version": __import__("xgboost").__version__,
            "estimators": estimators,
            "best_iteration": int(model.best_iteration),
            "max_depth": max_depth,
            "learning_rate": learning_rate,
            "subsample": subsample,
            "colsample_bytree": colsample_bytree,
            "early_stopping_rounds": early_stopping_rounds,
            "class_weighting": "balanced_training_sample_weight",
        },
        "efficiency": {
            "training_seconds": training_seconds,
            "inference_seconds": inference_seconds,
            "inference_samples_per_second": float(
                test_labels.size / max(inference_seconds, 1e-12)
            ),
        },
        "claim_boundary": {
            "same_split_arrays_as_pairwise": True,
            "threshold_uses_validation_benign_only": True,
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
            "unknown_label_capability": False,
            "baseline_role": "closed_set_warning_and_known_type_anchor",
        },
        "source_sha256": {
            **{
                f"pairwise_{name}": file_hash(path)
                for name, path in pairwise_paths.items()
            },
            "cache_csv": file_hash(cache_csv),
            "config": file_hash(config_path),
        },
    }
    report["manifest_sha256"] = canonical_hash(report)
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = output_dir / "metrics.json"
    metrics_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    np.savez_compressed(
        output_dir / "scores.npz",
        validation_probability=validation_probability,
        validation_labels=validation_labels,
        test_probability=test_probability,
        test_labels=test_labels,
        test_unknown=test_unknown,
    )
    model.save_model(output_dir / "model.ubj")
    provenance = {
        "schema_version": "strict_v4_xgboost_warning_provenance_v1",
        "task": report["task"],
        "pairwise_task_dir": str(pairwise_task_dir.resolve()),
        "cache_csv": str(cache_csv.resolve()),
        "config": str(config_path.resolve()),
        "metrics_file_sha256": file_hash(metrics_path),
    }
    provenance["manifest_sha256"] = canonical_hash(provenance)
    (output_dir / "provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairwise-task-dir", type=Path, required=True)
    parser.add_argument("--cache-csv", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--xgboost-root", type=Path, required=True)
    parser.add_argument("--validation-benign-fpr-budget", type=float, required=True)
    parser.add_argument("--estimators", type=int, default=1000)
    parser.add_argument("--max-depth", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=0.05)
    parser.add_argument("--subsample", type=float, default=0.9)
    parser.add_argument("--colsample-bytree", type=float, default=0.9)
    parser.add_argument("--early-stopping-rounds", type=int, default=30)
    parser.add_argument("--jobs", type=int, default=8)
    args = parser.parse_args()
    report = train_task(
        pairwise_task_dir=args.pairwise_task_dir,
        cache_csv=args.cache_csv,
        config_path=args.config,
        output_dir=args.output_dir,
        xgboost_root=args.xgboost_root,
        validation_benign_fpr_budget=args.validation_benign_fpr_budget,
        estimators=args.estimators,
        max_depth=args.max_depth,
        learning_rate=args.learning_rate,
        subsample=args.subsample,
        colsample_bytree=args.colsample_bytree,
        early_stopping_rounds=args.early_stopping_rounds,
        jobs=args.jobs,
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
