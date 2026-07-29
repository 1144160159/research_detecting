from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)
from train_strict_v4_xgboost_warning_task import train_task
from verify_xgboost_cuda_backend import (
    GPUSampler,
    find_device_values,
    query_gpu,
)


def update_gpu_evidence(
    *,
    output_dir: Path,
    xgboost_module: Any,
    trained_classifier: Any,
    sampler: GPUSampler,
    initial_gpu: dict[str, Any],
) -> dict[str, Any]:
    booster = trained_classifier.get_booster()
    booster_configuration = json.loads(booster.save_config())
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
    build_info = xgboost_module.build_info()
    passes = (
        bool(build_info.get("USE_CUDA"))
        and any(value.startswith("cuda") for value in device_values)
        and compute_process_observed
        and peak_memory > 1.0
        and not sampler.errors
    )
    gpu_evidence: dict[str, Any] = {
        "schema_version": "strict_v4_xgboost_cuda_task_evidence_v1",
        "state": "complete",
        "requested_device": "cuda",
        "booster_device_values": device_values,
        "xgboost_version": xgboost_module.__version__,
        "xgboost_build_info": build_info,
        "gpu_identity": {
            key: initial_gpu[key]
            for key in ("index", "name", "uuid")
        },
        "sample_count": len(sampler.samples),
        "samples": sampler.samples,
        "sample_errors": sampler.errors,
        "peak_gpu_utilization_percent": peak_utilization,
        "peak_gpu_memory_mib": peak_memory,
        "compute_process_observed_by_nvidia_smi": compute_process_observed,
        "passes": passes,
        "claim_boundary": {
            "model_training_backend": "cuda",
            "data_preparation_and_metrics_may_use_cpu": True,
            "pid_namespace_may_differ_from_nvidia_smi": True,
        },
    }
    gpu_evidence["manifest_sha256"] = canonical_hash(gpu_evidence)
    evidence_path = output_dir / "gpu_execution.json"
    atomic_json(evidence_path, gpu_evidence)
    metrics_path = output_dir / "metrics.json"
    metrics = load_canonical(metrics_path, "XGBoost task metrics")
    metrics.pop("manifest_sha256")
    metrics["schema_version"] = "strict_v4_xgboost_cuda_warning_task_v1"
    metrics["model"]["device"] = "cuda"
    metrics["model"]["tree_method"] = "hist"
    metrics["gpu_execution"] = {
        "file": evidence_path.name,
        "file_sha256": file_hash(evidence_path),
        "manifest_sha256": gpu_evidence["manifest_sha256"],
        "passes": passes,
    }
    metrics["claim_boundary"]["formal_model_training_uses_cuda"] = True
    metrics["manifest_sha256"] = canonical_hash(metrics)
    atomic_json(metrics_path, metrics)
    provenance_path = output_dir / "provenance.json"
    provenance = load_canonical(provenance_path, "XGBoost task provenance")
    provenance.pop("manifest_sha256")
    provenance["schema_version"] = (
        "strict_v4_xgboost_cuda_warning_provenance_v1"
    )
    provenance["metrics_file_sha256"] = file_hash(metrics_path)
    provenance["gpu_execution_file_sha256"] = file_hash(evidence_path)
    provenance["gpu_execution_manifest_sha256"] = gpu_evidence[
        "manifest_sha256"
    ]
    provenance["manifest_sha256"] = canonical_hash(provenance)
    atomic_json(provenance_path, provenance)
    if not passes:
        raise RuntimeError("XGBoost CUDA device evidence did not pass")
    return metrics


def run_cuda_task(args: argparse.Namespace) -> dict[str, Any]:
    xgboost_root = args.xgboost_root.resolve()
    if str(xgboost_root) not in sys.path:
        sys.path.insert(0, str(xgboost_root))
    import xgboost

    original_classifier = xgboost.XGBClassifier
    trained_classifiers: list[Any] = []

    def cuda_classifier(*classifier_args: Any, **classifier_kwargs: Any) -> Any:
        classifier_kwargs["tree_method"] = "hist"
        classifier_kwargs["device"] = "cuda"
        classifier = original_classifier(*classifier_args, **classifier_kwargs)
        trained_classifiers.append(classifier)
        return classifier

    xgboost.XGBClassifier = cuda_classifier
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    initial_gpu = query_gpu()
    sampler = GPUSampler(args.gpu_sample_interval_seconds)
    sampler.start()
    try:
        train_task(
            pairwise_task_dir=args.pairwise_task_dir.resolve(),
            cache_csv=args.cache_csv.resolve(),
            config_path=args.config.resolve(),
            output_dir=args.output_dir.resolve(),
            xgboost_root=xgboost_root,
            validation_benign_fpr_budget=args.validation_benign_fpr_budget,
            estimators=args.estimators,
            max_depth=args.max_depth,
            learning_rate=args.learning_rate,
            subsample=args.subsample,
            colsample_bytree=args.colsample_bytree,
            early_stopping_rounds=args.early_stopping_rounds,
            jobs=args.jobs,
        )
    finally:
        sampler.stop()
        xgboost.XGBClassifier = original_classifier
    if len(trained_classifiers) != 1:
        raise RuntimeError(
            "expected exactly one captured CUDA XGBoost classifier, got "
            f"{len(trained_classifiers)}"
        )
    return update_gpu_evidence(
        output_dir=args.output_dir.resolve(),
        xgboost_module=xgboost,
        trained_classifier=trained_classifiers[0],
        sampler=sampler,
        initial_gpu=initial_gpu,
    )


def parse_arguments() -> argparse.Namespace:
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
    parser.add_argument("--gpu-sample-interval-seconds", type=float, default=0.1)
    return parser.parse_args()


def main() -> None:
    metrics = run_cuda_task(parse_arguments())
    print(json.dumps(metrics, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
