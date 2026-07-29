from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path
from typing import Any

import numpy as np

from caeos.data import prepare_tabular_open_set
from evaluate_strict_v4_benign_calibrated_warning import calibrate_threshold
from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)
from train_strict_v4_xgboost_binary_warning_task_cuda import warning_metrics
from train_strict_v4_xgboost_warning_task import features
from verify_xgboost_cuda_backend import GPUSampler, query_gpu


def reconstruction_scores(
    model: Any,
    values: np.ndarray,
    *,
    device: Any,
    batch_size: int,
) -> np.ndarray:
    import torch

    model.eval()
    result = []
    with torch.no_grad():
        for start in range(0, values.shape[0], batch_size):
            batch = torch.from_numpy(
                values[start : start + batch_size]
            ).to(device)
            reconstructed = model(batch)
            result.append(
                torch.mean((reconstructed - batch) ** 2, dim=1)
                .detach()
                .cpu()
                .numpy()
            )
    return np.concatenate(result).astype(np.float64)


def train_task(args: argparse.Namespace) -> dict[str, Any]:
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, TensorDataset

    if not torch.cuda.is_available():
        raise RuntimeError("PyTorch CUDA is unavailable")
    pairwise_dir = args.pairwise_task_dir.resolve()
    pairwise_metrics = json.loads(
        (pairwise_dir / "metrics.json").read_text(encoding="utf-8")
    )
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
    train_labels = bundle.train.labels.numpy().astype(np.int64)
    validation_labels = bundle.validation.labels.numpy().astype(np.int64)
    test_labels = bundle.test.labels.numpy().astype(np.int64)
    test_unknown = bundle.test.is_unknown.numpy().astype(bool)
    if not (
        np.array_equal(validation_labels, pairwise_validation_labels)
        and np.array_equal(test_labels, pairwise_test_labels)
        and np.array_equal(test_unknown, pairwise_test_unknown)
    ):
        raise ValueError("autoencoder split arrays differ from Pairwise task")
    benign_index = known_class_names.index("Benign")
    x_train = features(bundle.train).astype(np.float32)
    x_validation = features(bundle.validation).astype(np.float32)
    x_test = features(bundle.test).astype(np.float32)
    train_benign = x_train[train_labels == benign_index]
    validation_benign = x_validation[validation_labels == benign_index]
    if train_benign.shape[0] < 100 or validation_benign.shape[0] < 30:
        raise ValueError("insufficient benign support for autoencoder")

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    device = torch.device("cuda:0")
    input_dim = int(x_train.shape[1])
    hidden_dim = max(args.latent_dim * 4, min(128, input_dim * 2))
    model = nn.Sequential(
        nn.Linear(input_dim, hidden_dim),
        nn.GELU(),
        nn.Linear(hidden_dim, args.latent_dim),
        nn.GELU(),
        nn.Linear(args.latent_dim, hidden_dim),
        nn.GELU(),
        nn.Linear(hidden_dim, input_dim),
    ).to(device)
    generator = torch.Generator()
    generator.manual_seed(seed)
    loader = DataLoader(
        TensorDataset(torch.from_numpy(train_benign)),
        batch_size=args.batch_size,
        shuffle=True,
        generator=generator,
        num_workers=0,
        drop_last=False,
    )
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.learning_rate,
        weight_decay=args.weight_decay,
    )
    initial_gpu = query_gpu()
    if initial_gpu["uuid"] != args.required_gpu_uuid:
        raise ValueError("unexpected GPU UUID")
    sampler = GPUSampler(args.gpu_sample_interval_seconds)
    sampler.start()
    best_state = None
    best_validation_loss = float("inf")
    stale_epochs = 0
    history = []
    started = time.perf_counter()
    try:
        for epoch in range(args.epochs):
            model.train()
            total_loss = 0.0
            total_rows = 0
            for (cpu_batch,) in loader:
                batch = cpu_batch.to(device)
                optimizer.zero_grad(set_to_none=True)
                reconstructed = model(batch)
                loss = torch.mean((reconstructed - batch) ** 2)
                loss.backward()
                optimizer.step()
                total_loss += float(loss.detach().cpu()) * batch.shape[0]
                total_rows += int(batch.shape[0])
            validation_scores = reconstruction_scores(
                model,
                validation_benign,
                device=device,
                batch_size=args.batch_size,
            )
            validation_loss = float(validation_scores.mean())
            history.append(
                {
                    "epoch": epoch + 1,
                    "train_loss": total_loss / max(total_rows, 1),
                    "validation_benign_loss": validation_loss,
                }
            )
            if validation_loss < best_validation_loss - args.minimum_delta:
                best_validation_loss = validation_loss
                best_state = {
                    key: value.detach().cpu().clone()
                    for key, value in model.state_dict().items()
                }
                stale_epochs = 0
            else:
                stale_epochs += 1
                if stale_epochs >= args.patience:
                    break
        if best_state is None:
            raise RuntimeError("autoencoder did not produce a checkpoint")
        model.load_state_dict(best_state)
        training_seconds = time.perf_counter() - started
        validation_reconstruction_error = reconstruction_scores(
            model,
            x_validation,
            device=device,
            batch_size=args.batch_size,
        )
        started = time.perf_counter()
        test_reconstruction_error = reconstruction_scores(
            model,
            x_test,
            device=device,
            batch_size=args.batch_size,
        )
        inference_seconds = time.perf_counter() - started
    finally:
        sampler.stop()
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
        str(next(model.parameters()).device) == "cuda:0"
        and compute_process_observed
        and peak_memory > 1.0
        and not sampler.errors
        and initial_gpu["uuid"] == args.required_gpu_uuid
    )
    calibration = calibrate_threshold(
        validation_reconstruction_error,
        np.full(validation_labels.shape, benign_index, dtype=np.int64),
        validation_labels,
        benign_index,
        args.validation_benign_fpr_budget,
    )
    if not calibration["feasible"]:
        raise ValueError("autoencoder benign FPR calibration is infeasible")
    metrics = warning_metrics(
        test_attack_probability=test_reconstruction_error,
        test_labels=test_labels,
        test_unknown=test_unknown,
        benign_index=benign_index,
        threshold=float(calibration["threshold"]),
    )
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "state_dict": best_state,
            "input_dim": input_dim,
            "hidden_dim": hidden_dim,
            "latent_dim": args.latent_dim,
        },
        output_dir / "model.pt",
    )
    np.savez_compressed(
        output_dir / "scores.npz",
        validation_reconstruction_error=validation_reconstruction_error,
        validation_labels=validation_labels,
        test_reconstruction_error=test_reconstruction_error,
        test_labels=test_labels,
        test_unknown=test_unknown,
    )
    gpu_evidence: dict[str, Any] = {
        "schema_version": "strict_v4_benign_autoencoder_cuda_evidence_v1",
        "state": "complete",
        "requested_device": "cuda:0",
        "model_parameter_device": str(next(model.parameters()).device),
        "torch_version": torch.__version__,
        "torch_cuda_version": torch.version.cuda,
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
        "schema_version": "strict_v4_benign_autoencoder_cuda_task_v1",
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
            "name": "benign-only reconstruction autoencoder",
            "input_dim": input_dim,
            "hidden_dim": hidden_dim,
            "latent_dim": args.latent_dim,
            "epochs_requested": args.epochs,
            "epochs_completed": len(history),
            "best_validation_benign_loss": best_validation_loss,
            "device": "cuda:0",
        },
        "history": history,
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
            "benign_training_only": True,
            "validation_benign_used_for_early_stopping_and_threshold": True,
            "known_attack_validation_labels_used_for_training": False,
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
        "schema_version": "strict_v4_benign_autoencoder_cuda_provenance_v1",
        "task": report["task"],
        "pairwise_task_dir": str(pairwise_dir),
        "cache_csv": str(args.cache_csv.resolve()),
        "config": str(args.config.resolve()),
        "metrics_file_sha256": file_hash(output_dir / "metrics.json"),
        "scores_file_sha256": file_hash(output_dir / "scores.npz"),
        "model_file_sha256": file_hash(output_dir / "model.pt"),
        "gpu_execution_file_sha256": file_hash(
            output_dir / "gpu_execution.json"
        ),
    }
    provenance["manifest_sha256"] = canonical_hash(provenance)
    atomic_json(output_dir / "provenance.json", provenance)
    if not gpu_passes:
        raise RuntimeError("autoencoder CUDA device evidence did not pass")
    return report


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairwise-task-dir", type=Path, required=True)
    parser.add_argument("--cache-csv", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--required-gpu-uuid", required=True)
    parser.add_argument("--validation-benign-fpr-budget", type=float, default=0.04)
    parser.add_argument("--latent-dim", type=int, default=16)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--weight-decay", type=float, default=0.0001)
    parser.add_argument("--patience", type=int, default=12)
    parser.add_argument("--minimum-delta", type=float, default=1e-6)
    parser.add_argument("--gpu-sample-interval-seconds", type=float, default=0.1)
    return parser.parse_args()


def main() -> None:
    report = train_task(parse_arguments())
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
