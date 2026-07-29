from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from strict_v4_cicids2017_attack_family import atomic_json, canonical_hash


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def query_gpu() -> dict[str, Any]:
    command = [
        "nvidia-smi",
        "--query-gpu=index,name,uuid,utilization.gpu,memory.used,power.draw",
        "--format=csv,noheader,nounits",
    ]
    completed = subprocess.run(
        command, capture_output=True, text=True, check=True
    )
    fields = [value.strip() for value in completed.stdout.strip().split(",")]
    if len(fields) != 6:
        raise ValueError(f"unexpected nvidia-smi output: {completed.stdout!r}")
    process_output = subprocess.run(
        [
            "nvidia-smi",
            "--query-compute-apps=pid,process_name,used_gpu_memory",
            "--format=csv,noheader,nounits",
        ],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    processes = []
    for line in process_output.splitlines():
        values = [value.strip() for value in line.split(",", 2)]
        if len(values) == 3:
            processes.append(
                {
                    "pid": int(values[0]),
                    "process_name": values[1],
                    "used_gpu_memory_mib": float(values[2]),
                }
            )
    return {
        "sampled_at_utc": utc_now(),
        "index": int(fields[0]),
        "name": fields[1],
        "uuid": fields[2],
        "utilization_percent": float(fields[3]),
        "memory_used_mib": float(fields[4]),
        "power_draw_watts": float(fields[5]),
        "compute_processes": processes,
    }


class GPUSampler:
    def __init__(self, interval_seconds: float) -> None:
        self.interval_seconds = interval_seconds
        self.samples: list[dict[str, Any]] = []
        self.errors: list[str] = []
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=max(2.0, self.interval_seconds * 4))

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                self.samples.append(query_gpu())
            except Exception as exc:
                self.errors.append(f"{type(exc).__name__}: {exc}")
            self._stop.wait(self.interval_seconds)


def find_device_values(value: Any) -> list[str]:
    devices = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "device":
                devices.append(str(child))
            devices.extend(find_device_values(child))
    elif isinstance(value, list):
        for child in value:
            devices.extend(find_device_values(child))
    return devices


def run_probe(
    *,
    xgboost_root: Path,
    rows: int,
    columns: int,
    estimators: int,
    seed: int,
    sample_interval_seconds: float,
) -> dict[str, Any]:
    if str(xgboost_root.resolve()) not in sys.path:
        sys.path.insert(0, str(xgboost_root.resolve()))
    import xgboost
    from xgboost import XGBClassifier

    rng = np.random.default_rng(seed)
    features = rng.normal(size=(rows, columns)).astype(np.float32)
    signal = (
        features[:, 0]
        + 0.7 * features[:, 1]
        - 0.4 * features[:, 2]
        + 0.2 * rng.normal(size=rows)
    )
    labels = np.digitize(signal, bins=(-0.75, 0.0, 0.75)).astype(np.int64)
    split = int(rows * 0.8)
    sampler = GPUSampler(sample_interval_seconds)
    model = XGBClassifier(
        n_estimators=estimators,
        max_depth=8,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="multi:softprob",
        eval_metric="mlogloss",
        tree_method="hist",
        device="cuda",
        n_jobs=8,
        random_state=seed,
    )
    sampler.start()
    started = time.perf_counter()
    try:
        model.fit(
            features[:split],
            labels[:split],
            eval_set=[(features[split:], labels[split:])],
            verbose=False,
        )
        probability = np.asarray(model.predict_proba(features[split:]))
    finally:
        sampler.stop()
    elapsed_seconds = time.perf_counter() - started
    booster_configuration = json.loads(model.get_booster().save_config())
    device_values = find_device_values(booster_configuration)
    peak_utilization = max(
        (sample["utilization_percent"] for sample in sampler.samples),
        default=0.0,
    )
    peak_memory = max(
        (sample["memory_used_mib"] for sample in sampler.samples), default=0.0
    )
    own_pid = os.getpid()
    matching_namespace_pid_observed = any(
        any(
            int(process["pid"]) == own_pid
            for process in sample["compute_processes"]
        )
        for sample in sampler.samples
    )
    compute_process_observed = any(
        sample["compute_processes"] for sample in sampler.samples
    )
    cuda_configured = any(value.startswith("cuda") for value in device_values)
    passes = (
        cuda_configured
        and probability.shape == (rows - split, len(np.unique(labels)))
        and peak_utilization > 0.0
        and peak_memory > 1.0
        and compute_process_observed
        and not sampler.errors
    )
    report: dict[str, Any] = {
        "schema_version": "strict_v4_xgboost_cuda_backend_probe_v1",
        "state": "complete",
        "created_at_utc": utc_now(),
        "xgboost_version": xgboost.__version__,
        "xgboost_build_info": xgboost.build_info(),
        "python": sys.executable,
        "process_id": own_pid,
        "parameters": {
            "rows": rows,
            "columns": columns,
            "estimators": estimators,
            "seed": seed,
            "tree_method": "hist",
            "device": "cuda",
        },
        "booster_device_values": device_values,
        "elapsed_seconds": elapsed_seconds,
        "prediction_shape": list(probability.shape),
        "gpu_samples": sampler.samples,
        "gpu_sample_errors": sampler.errors,
        "peak_gpu_utilization_percent": peak_utilization,
        "peak_gpu_memory_mib": peak_memory,
        "compute_process_observed_by_nvidia_smi": compute_process_observed,
        "matching_namespace_pid_observed": matching_namespace_pid_observed,
        "pid_namespace_note": (
            "nvidia-smi may report the host PID while Python reports a "
            "container namespace PID"
        ),
        "passes": passes,
        "claim_boundary": {
            "backend_capability_probe_only": True,
            "not_an_effect_result": True,
            "formal_experiments_require_separate_frozen_protocol": True,
        },
    }
    report["manifest_sha256"] = canonical_hash(report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xgboost-root", type=Path, required=True)
    parser.add_argument("--rows", type=int, default=250_000)
    parser.add_argument("--columns", type=int, default=128)
    parser.add_argument("--estimators", type=int, default=160)
    parser.add_argument("--seed", type=int, default=20260728)
    parser.add_argument("--sample-interval-seconds", type=float, default=0.2)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = run_probe(
        xgboost_root=args.xgboost_root,
        rows=args.rows,
        columns=args.columns,
        estimators=args.estimators,
        seed=args.seed,
        sample_interval_seconds=args.sample_interval_seconds,
    )
    atomic_json(args.output.resolve(), report)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    if not report["passes"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
