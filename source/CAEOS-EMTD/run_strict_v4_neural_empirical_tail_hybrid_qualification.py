from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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


def load_canonical(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    declared = value.get("manifest_sha256")
    body = dict(value)
    body.pop("manifest_sha256", None)
    if not isinstance(declared, str) or canonical_hash(body) != declared:
        raise ValueError("protocol canonical mismatch")
    return value


def gpu_sample(required_uuid: str) -> dict[str, Any]:
    command = [
        "nvidia-smi",
        (
            "--query-gpu=uuid,utilization.gpu,utilization.memory,"
            "memory.used,power.draw"
        ),
        "--format=csv,noheader,nounits",
    ]
    output = subprocess.check_output(command, text=True, timeout=10)
    for raw_line in output.splitlines():
        fields = [field.strip() for field in raw_line.split(",")]
        if len(fields) != 5 or fields[0] != required_uuid:
            continue
        return {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "gpu_uuid": fields[0],
            "gpu_utilization_percent": float(fields[1]),
            "memory_utilization_percent": float(fields[2]),
            "memory_used_mib": float(fields[3]),
            "power_draw_watts": float(fields[4]),
        }
    raise RuntimeError(f"required GPU is not visible: {required_uuid}")


def summarize_samples(samples: list[dict[str, Any]]) -> dict[str, Any]:
    if not samples:
        return {
            "sample_count": 0,
            "mean_gpu_utilization_percent": None,
            "median_gpu_utilization_percent": None,
            "fraction_samples_at_least_50_percent": None,
            "fraction_samples_at_least_80_percent": None,
            "peak_gpu_utilization_percent": None,
            "peak_gpu_memory_mib": None,
            "peak_power_draw_watts": None,
        }
    utilization = [
        float(sample["gpu_utilization_percent"]) for sample in samples
    ]
    return {
        "sample_count": len(samples),
        "mean_gpu_utilization_percent": statistics.fmean(utilization),
        "median_gpu_utilization_percent": statistics.median(utilization),
        "fraction_samples_at_least_50_percent": sum(
            value >= 50.0 for value in utilization
        )
        / len(utilization),
        "fraction_samples_at_least_80_percent": sum(
            value >= 80.0 for value in utilization
        )
        / len(utilization),
        "peak_gpu_utilization_percent": max(utilization),
        "peak_gpu_memory_mib": max(
            float(sample["memory_used_mib"]) for sample in samples
        ),
        "peak_power_draw_watts": max(
            float(sample["power_draw_watts"]) for sample in samples
        ),
    }


def verify_implementation(project_root: Path, protocol: dict[str, Any]) -> None:
    for name, expected in protocol["implementation_sha256"].items():
        observed = file_hash(project_root / name)
        if observed != expected:
            raise ValueError(f"implementation hash mismatch: {name}")


def neural_task_paths(protocol: dict[str, Any]) -> list[tuple[str, Path]]:
    neural_root = Path(protocol["neural_root"])
    return [
        (
            f"{scenario}_seed{seed}",
            neural_root / f"{scenario}_seed{seed}_mlp",
        )
        for seed in protocol["seeds"]
        for scenario in protocol["scenarios"]
    ]


def neural_task_artifacts(protocol: dict[str, Any]) -> dict[str, Any]:
    artifacts = {}
    for identity, task_dir in neural_task_paths(protocol):
        metrics_path = task_dir / "metrics.json"
        scores_path = task_dir / "scores.npz"
        if not metrics_path.is_file() or not scores_path.is_file():
            continue
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        runtime = metrics.get("runtime_execution", {})
        artifacts[identity] = {
            "task_dir": str(task_dir),
            "metrics_sha256": file_hash(metrics_path),
            "scores_sha256": file_hash(scores_path),
            "requested_device": runtime.get("requested_device"),
            "resolved_device": runtime.get("resolved_device"),
            "cuda_available": runtime.get("cuda_available"),
            "cuda_device_name": runtime.get("cuda_device_name"),
        }
    return artifacts


def xgboost_task_artifacts(protocol: dict[str, Any]) -> dict[str, Any]:
    artifacts = {}
    xgboost_root = Path(protocol["xgboost_root"])
    for seed in protocol["seeds"]:
        for scenario in protocol["scenarios"]:
            identity = f"{scenario}_seed{seed}"
            task_dir = xgboost_root / identity
            metrics_path = task_dir / "metrics.json"
            scores_path = task_dir / "scores.npz"
            evidence_path = task_dir / "gpu_execution.json"
            if not (
                metrics_path.is_file()
                and scores_path.is_file()
                and evidence_path.is_file()
            ):
                continue
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            artifacts[identity] = {
                "task_dir": str(task_dir),
                "metrics_sha256": file_hash(metrics_path),
                "scores_sha256": file_hash(scores_path),
                "gpu_execution_sha256": file_hash(evidence_path),
                "requested_device": evidence.get("requested_device"),
                "booster_device_values": evidence.get(
                    "booster_device_values"
                ),
                "gpu_evidence_passes": evidence.get("passes"),
                "metrics_gpu_evidence_passes": metrics.get(
                    "gpu_execution", {}
                ).get("passes"),
            }
    return artifacts


def run_qualification(
    *,
    project_root: Path,
    protocol_path: Path,
    python_executable: Path,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    protocol_path = protocol_path.resolve()
    protocol = load_canonical(protocol_path)
    if (
        protocol.get("state")
        != "frozen_zero_result_gpu_qualification"
        or protocol.get("stage") != "qualification"
    ):
        raise ValueError("unsupported qualification protocol")
    verify_implementation(project_root, protocol)

    result_root = Path(protocol["result_root"])
    result_root.mkdir(parents=True, exist_ok=True)
    completion_path = result_root / "completion.json"
    if completion_path.exists():
        raise ValueError(f"refusing to overwrite completion: {completion_path}")

    required_uuid = protocol["resource_contract"]["required_gpu_uuid"]
    initial_sample = gpu_sample(required_uuid)
    training = protocol["training"]["neural"]
    neural_command = [
        str(python_executable),
        str(project_root / "run_neural_baseline_matrix.py"),
        "--suite",
        protocol["suite"],
        "--scenarios",
        ",".join(protocol["scenarios"]),
        "--models",
        training["model"],
        "--seeds",
        ",".join(str(seed) for seed in protocol["seeds"]),
        "--workers",
        str(training["workers"]),
        "--device",
        training["device"],
        "--epochs",
        str(training["epochs"]),
        "--patience",
        str(training["patience"]),
        "--cicids2017-csv",
        protocol["source_csv"],
        "--cicids2017-cache-dir",
        protocol["neural_cache_dir"],
        "--output-root",
        protocol["matrix_output_root"],
    ]
    xgboost_command = [
        str(python_executable),
        str(
            project_root
            / "run_strict_v4_xgboost_cuda_qualification_batch.py"
        ),
        "--project-root",
        str(project_root),
        "--protocol",
        str(protocol_path),
        "--python",
        str(python_executable),
    ]
    neural_log_path = result_root / "neural_runner.log"
    xgboost_log_path = result_root / "xgboost_runner.log"
    samples_path = result_root / "gpu_samples.jsonl"
    launch_state_path = result_root / "launch_state.json"
    started_at = datetime.now(timezone.utc)
    samples = [initial_sample]
    with neural_log_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as neural_log, xgboost_log_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as xgboost_log:
        neural_process = subprocess.Popen(
            neural_command,
            cwd=project_root,
            stdout=neural_log,
            stderr=subprocess.STDOUT,
            text=True,
        )
        xgboost_process = subprocess.Popen(
            xgboost_command,
            cwd=project_root,
            stdout=xgboost_log,
            stderr=subprocess.STDOUT,
            text=True,
        )
        launch_state = {
            "schema_version": (
                "strict_v4_neural_empirical_tail_hybrid_launch_state_v1"
            ),
            "state": "running",
            "pids": {
                "neural_matrix": neural_process.pid,
                "xgboost_cuda_batch": xgboost_process.pid,
            },
            "started_at_utc": started_at.isoformat(),
            "commands": {
                "neural_matrix": neural_command,
                "xgboost_cuda_batch": xgboost_command,
            },
            "protocol_path": str(protocol_path),
            "protocol_file_sha256": file_hash(protocol_path),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
        }
        launch_state_path.write_text(
            json.dumps(launch_state, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        with samples_path.open("w", encoding="utf-8", newline="\n") as sample_log:
            sample_log.write(json.dumps(initial_sample, sort_keys=True) + "\n")
            sample_log.flush()
            interval = float(
                protocol["resource_contract"]["sample_interval_seconds"]
            )
            while (
                neural_process.poll() is None
                or xgboost_process.poll() is None
            ):
                time.sleep(interval)
                try:
                    sample = gpu_sample(required_uuid)
                except (OSError, subprocess.SubprocessError, RuntimeError):
                    continue
                samples.append(sample)
                sample_log.write(json.dumps(sample, sort_keys=True) + "\n")
                sample_log.flush()
        neural_return_code = neural_process.wait()
        xgboost_return_code = xgboost_process.wait()

    finished_at = datetime.now(timezone.utc)
    neural_artifacts = neural_task_artifacts(protocol)
    xgboost_artifacts = xgboost_task_artifacts(protocol)
    expected = int(protocol["expected_task_count"])
    neural_all_cuda = len(neural_artifacts) == expected and all(
        artifact["requested_device"] == "cuda"
        and str(artifact["resolved_device"]).startswith("cuda")
        and artifact["cuda_available"] is True
        for artifact in neural_artifacts.values()
    )
    xgboost_all_cuda = len(xgboost_artifacts) == expected and all(
        artifact["requested_device"] == "cuda"
        and artifact["gpu_evidence_passes"] is True
        and artifact["metrics_gpu_evidence_passes"] is True
        and any(
            str(value).startswith("cuda")
            for value in artifact["booster_device_values"] or []
        )
        for artifact in xgboost_artifacts.values()
    )
    resource = summarize_samples(samples)
    minimum = float(
        protocol["resource_contract"]["minimum_mean_gpu_utilization_percent"]
    )
    preferred = float(
        protocol["resource_contract"][
            "preferred_mean_gpu_utilization_percent"
        ]
    )
    mean_utilization = resource["mean_gpu_utilization_percent"]
    resource["minimum_mean_utilization_passed"] = bool(
        mean_utilization is not None and mean_utilization >= minimum
    )
    resource["preferred_mean_utilization_met"] = bool(
        mean_utilization is not None and mean_utilization >= preferred
    )
    execution_passed = bool(
        neural_return_code == 0
        and xgboost_return_code == 0
        and len(neural_artifacts) == expected
        and len(xgboost_artifacts) == expected
        and neural_all_cuda
        and xgboost_all_cuda
        and resource["minimum_mean_utilization_passed"]
    )
    completion: dict[str, Any] = {
        "schema_version": (
            "strict_v4_neural_empirical_tail_hybrid_qualification_completion_v1"
        ),
        "state": (
            "complete_gpu_qualification_execution"
            if execution_passed
            else "gpu_qualification_execution_failed"
        ),
        "started_at_utc": started_at.isoformat(),
        "finished_at_utc": finished_at.isoformat(),
        "duration_seconds": (finished_at - started_at).total_seconds(),
        "return_codes": {
            "neural_matrix": neural_return_code,
            "xgboost_cuda_batch": xgboost_return_code,
        },
        "protocol": {
            "path": str(protocol_path),
            "file_sha256": file_hash(protocol_path),
            "manifest_sha256": protocol["manifest_sha256"],
        },
        "task_coverage": {
            "expected_per_component": expected,
            "neural_present": len(neural_artifacts),
            "xgboost_cuda_present": len(xgboost_artifacts),
            "complete": (
                len(neural_artifacts) == expected
                and len(xgboost_artifacts) == expected
            ),
        },
        "all_tasks_confirmed_cuda": {
            "neural": neural_all_cuda,
            "xgboost": xgboost_all_cuda,
        },
        "resource_observed": resource,
        "execution_passed": execution_passed,
        "neural_task_artifacts": neural_artifacts,
        "xgboost_task_artifacts": xgboost_artifacts,
        "claim_boundary": {
            "execution_pass_does_not_imply_effect_pass": True,
            "qualification_is_not_five_seed_confirmation": True,
        },
    }
    completion["manifest_sha256"] = canonical_hash(completion)
    completion_path.write_text(
        json.dumps(completion, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    launch_state["state"] = "completed"
    launch_state["finished_at_utc"] = finished_at.isoformat()
    launch_state["return_codes"] = completion["return_codes"]
    launch_state["completion_path"] = str(completion_path)
    launch_state_path.write_text(
        json.dumps(launch_state, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return completion


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    args = parser.parse_args()
    completion = run_qualification(
        project_root=args.project_root,
        protocol_path=args.protocol,
        python_executable=args.python,
    )
    print(
        json.dumps(
            {
                "execution_passed": completion["execution_passed"],
                "manifest_sha256": completion["manifest_sha256"],
                "state": completion["state"],
                "task_coverage": completion["task_coverage"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
