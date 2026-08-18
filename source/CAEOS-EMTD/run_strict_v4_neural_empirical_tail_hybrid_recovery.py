from __future__ import annotations

import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from create_strict_v4_neural_empirical_tail_hybrid_qualification_protocol import (
    file_hash,
    load_canonical,
)
from run_strict_v4_neural_empirical_tail_hybrid_qualification import (
    canonical_hash,
    gpu_sample,
    neural_task_artifacts,
    summarize_samples,
    xgboost_task_artifacts,
)


def verify_implementation(
    project_root: Path, recovery: dict[str, Any]
) -> None:
    for name, expected in recovery["implementation_sha256"].items():
        if file_hash(project_root / name) != expected:
            raise ValueError(f"recovery implementation mismatch: {name}")


def preserve_failed_logs(parent: dict[str, Any]) -> list[str]:
    preserved = []
    neural_root = Path(parent["neural_root"])
    for seed in parent["seeds"]:
        for scenario in parent["scenarios"]:
            task_dir = neural_root / f"{scenario}_seed{seed}_mlp"
            source = task_dir / "run.log"
            target = task_dir / "run.attempt1.infrastructure_failure.log"
            if source.is_file() and not target.exists():
                source.rename(target)
                preserved.append(str(target))
    manifest = Path(parent["matrix_output_root"]) / "manifest.json"
    manifest_target = (
        Path(parent["matrix_output_root"])
        / "manifest.attempt1.infrastructure_failure.json"
    )
    if manifest.is_file() and not manifest_target.exists():
        manifest.rename(manifest_target)
        preserved.append(str(manifest_target))
    return preserved


def run_recovery(
    *,
    project_root: Path,
    recovery_protocol_path: Path,
    python_executable: Path,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    recovery_protocol_path = recovery_protocol_path.resolve()
    recovery = load_canonical(recovery_protocol_path, "recovery protocol")
    parent_path = Path(recovery["parent_protocol"]["path"])
    parent = load_canonical(parent_path, "parent protocol")
    verify_implementation(project_root, recovery)
    completion_path = Path(recovery["recovery_completion_path"])
    if completion_path.exists():
        raise ValueError(f"refusing to overwrite recovery: {completion_path}")
    preserved_logs = preserve_failed_logs(parent)

    training = parent["training"]["neural"]
    neural_output_root = Path(
        recovery["repair"].get(
            "neural_output_root", parent["matrix_output_root"]
        )
    )
    command = [
        str(python_executable),
        str(project_root / "run_neural_baseline_matrix.py"),
        "--suite",
        parent["suite"],
        "--scenarios",
        ",".join(parent["scenarios"]),
        "--models",
        training["model"],
        "--seeds",
        ",".join(str(seed) for seed in parent["seeds"]),
        "--workers",
        str(recovery["repair"].get("scheduling_workers", training["workers"])),
        "--device",
        training["device"],
        "--epochs",
        str(training["epochs"]),
        "--patience",
        str(training["patience"]),
        "--cicids2017-csv",
        recovery["repair"]["source_csv"],
        "--cicids2017-cache-dir",
        recovery["repair"]["neural_cache_dir"],
        "--output-root",
        str(neural_output_root),
    ]
    result_root = Path(parent["result_root"])
    recovery_suffix = recovery_protocol_path.stem.removeprefix(
        "recovery_protocol"
    )
    log_path = result_root / f"neural_recovery_runner{recovery_suffix}.log"
    samples_path = (
        result_root / f"gpu_samples_recovery{recovery_suffix}.jsonl"
    )
    launch_state_path = (
        result_root / f"recovery_launch_state{recovery_suffix}.json"
    )
    required_uuid = recovery["resource_contract"]["required_gpu_uuid"]
    samples = [gpu_sample(required_uuid)]
    started_at = datetime.now(timezone.utc)
    with log_path.open("w", encoding="utf-8", newline="\n") as log_handle:
        process = subprocess.Popen(
            command,
            cwd=project_root,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            text=True,
        )
        launch_state = {
            "schema_version": (
                "strict_v4_neural_empirical_tail_hybrid_recovery_launch_v1"
            ),
            "state": "running",
            "pid": process.pid,
            "started_at_utc": started_at.isoformat(),
            "command": command,
            "recovery_protocol_path": str(recovery_protocol_path),
            "recovery_protocol_manifest_sha256": recovery[
                "manifest_sha256"
            ],
            "preserved_failed_logs": preserved_logs,
        }
        launch_state_path.write_text(
            json.dumps(launch_state, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        with samples_path.open("w", encoding="utf-8") as sample_log:
            sample_log.write(json.dumps(samples[0], sort_keys=True) + "\n")
            sample_log.flush()
            interval = float(
                recovery["resource_contract"]["sample_interval_seconds"]
            )
            while process.poll() is None:
                time.sleep(interval)
                try:
                    sample = gpu_sample(required_uuid)
                except (OSError, subprocess.SubprocessError, RuntimeError):
                    continue
                samples.append(sample)
                sample_log.write(json.dumps(sample, sort_keys=True) + "\n")
                sample_log.flush()
        return_code = process.wait()

    finished_at = datetime.now(timezone.utc)
    neural_artifact_protocol = dict(parent)
    neural_artifact_protocol["neural_root"] = str(
        neural_output_root / parent["suite"]
    )
    neural_artifacts = neural_task_artifacts(neural_artifact_protocol)
    xgboost_artifacts = xgboost_task_artifacts(parent)
    expected = int(parent["expected_task_count"])
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
        for artifact in xgboost_artifacts.values()
    )
    resource = summarize_samples(samples)
    minimum = float(
        recovery["resource_contract"]["minimum_mean_gpu_utilization_percent"]
    )
    preferred = float(
        recovery["resource_contract"][
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
        return_code == 0
        and len(neural_artifacts) == expected
        and len(xgboost_artifacts) == expected
        and neural_all_cuda
        and xgboost_all_cuda
        and resource["minimum_mean_utilization_passed"]
    )
    completion: dict[str, Any] = {
        "schema_version": (
            "strict_v4_neural_empirical_tail_hybrid_recovery_completion_v1"
        ),
        "state": (
            "complete_gpu_qualification_execution_recovered"
            if execution_passed
            else "gpu_qualification_recovery_failed"
        ),
        "execution_passed": execution_passed,
        "started_at_utc": started_at.isoformat(),
        "finished_at_utc": finished_at.isoformat(),
        "duration_seconds": (finished_at - started_at).total_seconds(),
        "return_codes": {
            "neural_matrix": return_code,
            "xgboost_cuda_batch": 0,
        },
        "protocol": {
            "path": str(parent_path),
            "file_sha256": file_hash(parent_path),
            "manifest_sha256": parent["manifest_sha256"],
        },
        "recovery_protocol": {
            "path": str(recovery_protocol_path),
            "file_sha256": file_hash(recovery_protocol_path),
            "manifest_sha256": recovery["manifest_sha256"],
        },
        "failed_completion": recovery["failed_completion"],
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
        "neural_task_artifacts": neural_artifacts,
        "xgboost_task_artifacts": xgboost_artifacts,
        "preserved_failed_logs": preserved_logs,
        "claim_boundary": recovery["claim_boundary"],
    }
    completion["manifest_sha256"] = canonical_hash(completion)
    completion_path.write_text(
        json.dumps(completion, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    launch_state["state"] = "completed"
    launch_state["finished_at_utc"] = finished_at.isoformat()
    launch_state["return_code"] = return_code
    launch_state["completion_path"] = str(completion_path)
    launch_state_path.write_text(
        json.dumps(launch_state, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return completion


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--recovery-protocol", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    args = parser.parse_args()
    completion = run_recovery(
        project_root=args.project_root,
        recovery_protocol_path=args.recovery_protocol,
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
