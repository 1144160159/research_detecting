from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.utils.class_weight import compute_sample_weight

from caeos.data import prepare_tabular_open_set
from evaluate_strict_v4_benign_calibrated_warning import calibrate_threshold
from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)
from train_strict_v4_xgboost_warning_task import features
from verify_xgboost_cuda_backend import (
    GPUSampler,
    find_device_values,
    query_gpu,
)


def warning_metrics(
    *,
    test_attack_probability: np.ndarray,
    test_labels: np.ndarray,
    test_unknown: np.ndarray,
    benign_index: int,
    threshold: float,
) -> dict[str, float]:
    predicted_alert = test_attack_probability >= threshold
    actual_attack = test_unknown | (test_labels != benign_index)
    known_attack = (~test_unknown) & (test_labels != benign_index)
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
        "known_attack_alert_recall": float(
            (known_attack & predicted_alert).sum() / known_attack.sum()
            if known_attack.sum()
            else 0.0
        ),
        "unknown_attack_alert_recall": float(
            (test_unknown & predicted_alert).sum() / test_unknown.sum()
            if test_unknown.sum()
            else 0.0
        ),
    }


def train_task(args: argparse.Namespace) -> dict[str, Any]:
    xgboost_root = args.xgboost_root.resolve()
    if str(xgboost_root) not in sys.path:
        sys.path.insert(0, str(xgboost_root))
    import xgboost
    from xgboost import XGBClassifier

    pairwise_dir = args.pairwise_task_dir.resolve()
    pairwise_metrics = json.loads(
        (pairwise_dir / "metrics.json").read_text(encoding="utf-8")
    )
    if not isinstance(pairwise_metrics, dict):
        raise ValueError("Pairwise task metrics must be a JSON object")
    pairwise_provenance = load_canonical(
        pairwise_dir / "provenance.json", "Pairwise task provenance"
    )
    task = pairwise_provenance["task"]
    seed = int(task["seed"])
    unknown_classes = [
        str(value) for value in pairwise_metrics["unknown_classes"]
    ]
    known_class_names = [
        str(value) for value in pairwise_metrics["known_class_names"]
    ]
    config = json.loads(args.config.resolve().read_text(encoding="utf-8"))
    bundle = prepare_tabular_open_set(
        csv_path=str(args.cache_csv.resolve()),
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
    with np.load(pairwise_dir / "scores.npz", allow_pickle=False) as scores:
        pairwise_validation_labels = np.asarray(
            scores["validation_labels"], dtype=np.int64
        )
        pairwise_test_labels = np.asarray(
            scores["test_labels"], dtype=np.int64
        )
        pairwise_test_unknown = np.asarray(
            scores["test_unknown"], dtype=bool
        )
    validation_labels = bundle.validation.labels.numpy().astype(np.int64)
    test_labels = bundle.test.labels.numpy().astype(np.int64)
    test_unknown = bundle.test.is_unknown.numpy().astype(bool)
    if not (
        np.array_equal(validation_labels, pairwise_validation_labels)
        and np.array_equal(test_labels, pairwise_test_labels)
        and np.array_equal(test_unknown, pairwise_test_unknown)
    ):
        raise ValueError("binary XGBoost split arrays differ from Pairwise task")

    benign_index = known_class_names.index("Benign")
    train_labels = bundle.train.labels.numpy().astype(np.int64)
    train_binary = (train_labels != benign_index).astype(np.int64)
    validation_binary = (validation_labels != benign_index).astype(np.int64)
    x_train = features(bundle.train)
    x_validation = features(bundle.validation)
    x_test = features(bundle.test)
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    model = XGBClassifier(
        n_estimators=args.estimators,
        max_depth=args.max_depth,
        learning_rate=args.learning_rate,
        subsample=args.subsample,
        colsample_bytree=args.colsample_bytree,
        objective="binary:logistic",
        eval_metric="logloss",
        tree_method="hist",
        device="cuda",
        early_stopping_rounds=args.early_stopping_rounds,
        n_jobs=args.jobs,
        random_state=seed,
    )
    initial_gpu = query_gpu()
    sampler = GPUSampler(args.gpu_sample_interval_seconds)
    sampler.start()
    started = time.perf_counter()
    try:
        model.fit(
            x_train,
            train_binary,
            sample_weight=compute_sample_weight("balanced", train_binary),
            eval_set=[(x_validation, validation_binary)],
            verbose=False,
        )
        training_seconds = time.perf_counter() - started
        validation_attack_probability = np.asarray(
            model.predict_proba(x_validation)[:, 1], dtype=np.float64
        )
        started = time.perf_counter()
        test_attack_probability = np.asarray(
            model.predict_proba(x_test)[:, 1], dtype=np.float64
        )
        inference_seconds = time.perf_counter() - started
    finally:
        sampler.stop()
    booster_configuration = json.loads(model.get_booster().save_config())
    device_values = find_device_values(booster_configuration)
    peak_utilization = max(
        (sample["utilization_percent"] for sample in sampler.samples),
        default=0.0,
    )
    peak_memory = max(
        (sample["memory_used_mib"] for sample in sampler.samples), default=0.0
    )
    compute_process_observed = any(
        sample["compute_processes"] for sample in sampler.samples
    )
    gpu_passes = (
        bool(xgboost.build_info().get("USE_CUDA"))
        and any(value.startswith("cuda") for value in device_values)
        and compute_process_observed
        and peak_memory > 1.0
        and not sampler.errors
        and initial_gpu["uuid"] == args.required_gpu_uuid
    )
    calibration = calibrate_threshold(
        validation_attack_probability,
        np.zeros(validation_binary.shape, dtype=np.int64),
        validation_binary,
        0,
        args.validation_benign_fpr_budget,
    )
    if not calibration["feasible"]:
        raise ValueError("binary validation benign FPR calibration is infeasible")
    metrics = warning_metrics(
        test_attack_probability=test_attack_probability,
        test_labels=test_labels,
        test_unknown=test_unknown,
        benign_index=benign_index,
        threshold=float(calibration["threshold"]),
    )
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    model.save_model(output_dir / "model.ubj")
    np.savez_compressed(
        output_dir / "scores.npz",
        validation_attack_probability=validation_attack_probability,
        validation_labels=validation_labels,
        test_attack_probability=test_attack_probability,
        test_labels=test_labels,
        test_unknown=test_unknown,
    )
    gpu_evidence: dict[str, Any] = {
        "schema_version": "strict_v4_xgboost_binary_cuda_task_evidence_v1",
        "state": "complete",
        "requested_device": "cuda",
        "booster_device_values": device_values,
        "xgboost_version": xgboost.__version__,
        "xgboost_build_info": xgboost.build_info(),
        "gpu_identity": {
            key: initial_gpu[key] for key in ("index", "name", "uuid")
        },
        "sample_count": len(sampler.samples),
        "samples": sampler.samples,
        "sample_errors": sampler.errors,
        "peak_gpu_utilization_percent": peak_utilization,
        "peak_gpu_memory_mib": peak_memory,
        "compute_process_observed_by_nvidia_smi": compute_process_observed,
        "passes": gpu_passes,
    }
    gpu_evidence["manifest_sha256"] = canonical_hash(gpu_evidence)
    atomic_json(output_dir / "gpu_execution.json", gpu_evidence)
    report: dict[str, Any] = {
        "schema_version": "strict_v4_xgboost_binary_cuda_warning_task_v1",
        "state": "complete",
        "task": {
            "suite": str(task["suite"]),
            "scenario": str(task["scenario"]),
            "seed": seed,
        },
        "unknown_classes": unknown_classes,
        "known_class_names": known_class_names,
        "validation_benign_fpr_budget": args.validation_benign_fpr_budget,
        "calibration": calibration,
        "operational_metrics": metrics,
        "model": {
            "name": "XGBoost binary malicious-warning head",
            "version": xgboost.__version__,
            "device": "cuda",
            "tree_method": "hist",
            "estimators": args.estimators,
            "best_iteration": int(model.best_iteration),
            "max_depth": args.max_depth,
            "learning_rate": args.learning_rate,
            "class_weighting": "balanced_binary_training_sample_weight",
        },
        "efficiency": {
            "training_seconds": training_seconds,
            "inference_seconds": inference_seconds,
            "inference_samples_per_second": float(
                test_labels.size / max(inference_seconds, 1e-12)
            ),
        },
        "gpu_execution": {
            "file": "gpu_execution.json",
            "file_sha256": file_hash(output_dir / "gpu_execution.json"),
            "manifest_sha256": gpu_evidence["manifest_sha256"],
            "passes": gpu_passes,
        },
        "claim_boundary": {
            "binary_warning_head_only": True,
            "known_family_typing_capability": False,
            "unknown_label_capability": False,
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
            "formal_model_training_uses_cuda": True,
        },
        "source_sha256": {
            "pairwise_metrics": file_hash(pairwise_dir / "metrics.json"),
            "pairwise_scores": file_hash(pairwise_dir / "scores.npz"),
            "pairwise_provenance": file_hash(pairwise_dir / "provenance.json"),
            "cache_csv": file_hash(args.cache_csv.resolve()),
            "config": file_hash(args.config.resolve()),
        },
    }
    report["manifest_sha256"] = canonical_hash(report)
    atomic_json(output_dir / "metrics.json", report)
    provenance: dict[str, Any] = {
        "schema_version": "strict_v4_xgboost_binary_cuda_provenance_v1",
        "task": report["task"],
        "pairwise_task_dir": str(pairwise_dir),
        "cache_csv": str(args.cache_csv.resolve()),
        "config": str(args.config.resolve()),
        "metrics_file_sha256": file_hash(output_dir / "metrics.json"),
        "scores_file_sha256": file_hash(output_dir / "scores.npz"),
        "model_file_sha256": file_hash(output_dir / "model.ubj"),
        "gpu_execution_file_sha256": file_hash(
            output_dir / "gpu_execution.json"
        ),
    }
    provenance["manifest_sha256"] = canonical_hash(provenance)
    atomic_json(output_dir / "provenance.json", provenance)
    if not gpu_passes:
        raise RuntimeError("binary XGBoost CUDA device evidence did not pass")
    return report


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairwise-task-dir", type=Path, required=True)
    parser.add_argument("--cache-csv", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--xgboost-root", type=Path, required=True)
    parser.add_argument("--required-gpu-uuid", required=True)
    parser.add_argument("--validation-benign-fpr-budget", type=float, default=0.04)
    parser.add_argument("--estimators", type=int, default=1000)
    parser.add_argument("--max-depth", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=0.05)
    parser.add_argument("--subsample", type=float, default=0.9)
    parser.add_argument("--colsample-bytree", type=float, default=0.9)
    parser.add_argument("--early-stopping-rounds", type=int, default=30)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--gpu-sample-interval-seconds", type=float, default=0.1)
    return parser.parse_args()


def main() -> None:
    report = train_task(parse_arguments())
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
