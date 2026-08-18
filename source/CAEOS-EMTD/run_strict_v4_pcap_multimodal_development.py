from __future__ import annotations

import argparse
import csv
import json
import subprocess
import time
from pathlib import Path
from typing import Any

from strict_v4_cic_iot2023_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
)


def gpu_sample() -> tuple[float, float, str]:
    completed = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=utilization.gpu,memory.used,uuid",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    fields = [
        field.strip()
        for field in completed.stdout.splitlines()[0].split(",")
    ]
    return float(fields[0]), float(fields[1]), fields[2]


def active_compute_processes() -> list[str]:
    completed = subprocess.run(
        [
            "nvidia-smi",
            "--query-compute-apps=pid,process_name",
            "--format=csv,noheader",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return [
        line.strip()
        for line in completed.stdout.splitlines()
        if line.strip() and "No running processes found" not in line
    ]


def launch_tasks(
    protocol: dict[str, Any],
    protocol_path: Path,
    python: Path,
    run_root: Path,
    result_root: Path,
) -> dict[str, Any]:
    if active_compute_processes():
        raise RuntimeError(
            "exclusive GPU preflight failed: compute processes are active"
        )
    run_root.mkdir(parents=True)
    result_root.mkdir(parents=True)
    processes: list[
        tuple[str, subprocess.Popen[str], Any, Path]
    ] = []
    seed = int(protocol["protocol"]["development_seed"])
    training = protocol["training"]
    for unknown_family in protocol["protocol"]["unknown_families"]:
        output_dir = run_root / unknown_family.lower()
        log_path = result_root / f"{unknown_family.lower()}.log"
        log_handle = log_path.open("w", encoding="utf-8")
        command = [
            str(python),
            "train_strict_v4_pcap_multimodal_task_cuda.py",
            "--cache",
            protocol["cache"]["path"],
            "--unknown-family",
            unknown_family,
            "--seed",
            str(seed),
            "--output-dir",
            str(output_dir),
            "--epochs",
            str(training["epochs"]),
            "--patience",
            str(training["patience"]),
            "--batch-size",
            str(training["batch_size"]),
            "--hidden-dim",
            str(training["hidden_dim"]),
            "--embedding-dim",
            str(training["embedding_dim"]),
            "--learning-rate",
            str(training["learning_rate"]),
            "--calibrator-profile",
            str(training.get("calibrator_profile", "base")),
            "--fine-contrastive-weight",
            str(training.get("fine_contrastive_weight", 0.0)),
            "--fine-contrastive-temperature",
            str(training.get("fine_contrastive_temperature", 0.1)),
            "--counterfactual-mix-weight",
            str(training.get("counterfactual_mix_weight", 0.0)),
            "--counterfactual-evidence-weight",
            str(training.get("counterfactual_evidence_weight", 0.05)),
            "--counterfactual-malicious-weight",
            str(training.get("counterfactual_malicious_weight", 0.5)),
            "--external-surrogate-weight",
            str(training.get("external_surrogate_weight", 0.0)),
            "--external-surrogate-evidence-weight",
            str(
                training.get(
                    "external_surrogate_evidence_weight",
                    0.05,
                )
            ),
            "--external-surrogate-malicious-weight",
            str(
                training.get(
                    "external_surrogate_malicious_weight",
                    0.5,
                )
            ),
            "--risk-weight-steps",
            str(training.get("risk_weight_steps", 400)),
            "--risk-weight-batch-size",
            str(training.get("risk_weight_batch_size", 512)),
            "--risk-weight-margin",
            str(training.get("risk_weight_margin", 0.1)),
            "--risk-weight-regularization",
            str(training.get("risk_weight_regularization", 0.05)),
            "--alert-profile",
            str(training.get("alert_profile", "dual_risk_malicious")),
            "--benign-knn-k",
            str(training.get("benign_knn_k", 5)),
            "--benign-knn-false-positive-budget",
            str(
                training.get(
                    "benign_knn_false_positive_budget",
                    0.04,
                )
            ),
            "--binary-head-hidden-dim",
            str(training.get("binary_head_hidden_dim", 64)),
            "--binary-head-steps",
            str(training.get("binary_head_steps", 400)),
            "--binary-head-batch-size",
            str(training.get("binary_head_batch_size", 1024)),
            "--binary-head-learning-rate",
            str(training.get("binary_head_learning_rate", 0.001)),
            "--binary-head-weight-decay",
            str(training.get("binary_head_weight_decay", 0.0001)),
            "--binary-head-false-positive-budget",
            str(
                training.get(
                    "binary_head_false_positive_budget",
                    0.04,
                )
            ),
            "--auxiliary-alert-branch-false-positive-budget",
            str(
                training.get(
                    "auxiliary_alert_branch_false_positive_budget",
                    0.015,
                )
            ),
            "--family-crossfit-false-positive-budget",
            str(
                training.get(
                    "family_crossfit_false_positive_budget",
                    0.005,
                )
            ),
            "--family-crossfit-checkpoint-interval",
            str(
                training.get(
                    "family_crossfit_checkpoint_interval",
                    25,
                )
            ),
            "--xgboost-behavior-estimators",
            str(training.get("xgboost_behavior_estimators", 800)),
            "--xgboost-behavior-max-depth",
            str(training.get("xgboost_behavior_max_depth", 8)),
            "--xgboost-behavior-learning-rate",
            str(training.get("xgboost_behavior_learning_rate", 0.05)),
            "--xgboost-behavior-early-stopping-rounds",
            str(
                training.get(
                    "xgboost_behavior_early_stopping_rounds",
                    40,
                )
            ),
            "--xgboost-behavior-jobs",
            str(training.get("xgboost_behavior_jobs", 20)),
            "--xgboost-behavior-false-positive-budget",
            str(
                training.get(
                    "xgboost_behavior_false_positive_budget",
                    0.04,
                )
            ),
        ]
        external_benign = protocol["cache"].get(
            "external_training_benign"
        )
        if external_benign is not None:
            command.extend(
                [
                    "--external-benign-cache",
                    str(external_benign["path"]),
                ]
            )
        external_surrogate = protocol["cache"].get(
            "external_training_surrogate_unknown"
        )
        if external_surrogate is not None:
            command.extend(
                [
                    "--external-surrogate-unknown-cache",
                    str(external_surrogate["path"]),
                ]
            )
        if training.get(
            "external_surrogate_binary_head_attack_augmentation",
            False,
        ):
            command.append(
                "--external-surrogate-binary-head-augmentation"
            )
        xgboost_root = training.get("xgboost_root")
        if xgboost_root:
            command.extend(
                [
                    "--xgboost-root",
                    str(xgboost_root),
                ]
            )
        reuse_task_root = training.get("reuse_task_root")
        if reuse_task_root:
            command.extend(
                [
                    "--reuse-task-dir",
                    str(Path(reuse_task_root) / unknown_family.lower()),
                ]
            )
        process = subprocess.Popen(
            command,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            text=True,
        )
        processes.append((unknown_family, process, log_handle, log_path))

    samples = []
    interval = float(
        protocol["execution"]["gpu_sample_interval_seconds"]
    )
    while any(process.poll() is None for _, process, _, _ in processes):
        utilization, memory, uuid = gpu_sample()
        samples.append(
            {
                "timestamp": time.time(),
                "gpu_utilization_percent": utilization,
                "memory_used_mib": memory,
                "gpu_uuid": uuid,
            }
        )
        time.sleep(interval)
    for _, _, handle, _ in processes:
        handle.close()
    failures = [
        {
            "unknown_family": family,
            "return_code": process.returncode,
            "log": str(log_path),
        }
        for family, process, _, log_path in processes
        if process.returncode != 0
    ]
    if not samples:
        utilization, memory, uuid = gpu_sample()
        samples.append(
            {
                "timestamp": time.time(),
                "gpu_utilization_percent": utilization,
                "memory_used_mib": memory,
                "gpu_uuid": uuid,
            }
        )
    csv_path = result_root / "gpu_samples.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(samples[0]))
        writer.writeheader()
        writer.writerows(samples)
    expected_uuid = protocol["execution"]["required_gpu_uuid"]
    observed_uuids = sorted({sample["gpu_uuid"] for sample in samples})
    if observed_uuids != [expected_uuid]:
        failures.append(
            {
                "reason": "GPU UUID mismatch",
                "expected": expected_uuid,
                "observed": observed_uuids,
            }
        )
    utilization_values = [
        sample["gpu_utilization_percent"] for sample in samples
    ]
    memory_values = [sample["memory_used_mib"] for sample in samples]
    completion: dict[str, Any] = {
        "schema_version": (
            "strict_v4_pcap_multimodal_development_completion_v1"
        ),
        "state": "completed" if not failures else "failed",
        "protocol_path": str(protocol_path),
        "protocol_file_sha256": file_hash(protocol_path),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "task_count": len(processes),
        "failures": failures,
        "resource_summary": {
            "sample_count": len(samples),
            "gpu_utilization_mean_percent": (
                sum(utilization_values) / len(utilization_values)
            ),
            "gpu_utilization_peak_percent": max(utilization_values),
            "gpu_samples_at_or_above_50_percent_fraction": (
                sum(value >= 50.0 for value in utilization_values)
                / len(utilization_values)
            ),
            "gpu_samples_at_or_above_80_percent_fraction": (
                sum(value >= 80.0 for value in utilization_values)
                / len(utilization_values)
            ),
            "memory_used_peak_mib": max(memory_values),
            "gpu_uuid": observed_uuids,
        },
        "task_metric_sha256": {
            family: file_hash(run_root / family.lower() / "metrics.json")
            for family, process, _, _ in processes
            if process.returncode == 0
        },
    }
    completion["manifest_sha256"] = canonical_hash(completion)
    atomic_json(result_root / "completion.json", completion)
    if failures:
        raise RuntimeError(json.dumps(failures, ensure_ascii=False))
    subprocess.run(
        [
            str(python),
            "evaluate_strict_v4_pcap_multimodal_development.py",
            "--protocol",
            str(protocol_path),
            "--run-root",
            str(run_root),
            "--completion",
            str(result_root / "completion.json"),
            "--output",
            str(result_root / "evaluation.json"),
        ],
        check=True,
    )
    return completion


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    args = parser.parse_args()
    protocol_path = args.protocol.resolve()
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    project_root = Path(protocol["paths"]["project_root"]).resolve()
    if Path.cwd().resolve() != project_root:
        raise ValueError("launcher must run from frozen project root")
    run_root = Path(protocol["paths"]["run_root"]).resolve()
    result_root = Path(protocol["paths"]["result_root"]).resolve()
    if run_root.exists() or result_root.exists():
        raise ValueError("refusing to overwrite development roots")
    launch_tasks(
        protocol,
        protocol_path,
        args.python.resolve(),
        run_root,
        result_root,
    )


if __name__ == "__main__":
    main()
