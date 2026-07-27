from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

try:
    import resource
except ImportError:  # pragma: no cover - formal execution is Linux-only.
    resource = None

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from run_strict_v4_vgrf_selected_system_seed317 import (
    load,
    replace_value,
)
from run_nested_gate_matrix import (
    build_run_provenance,
    freeze_or_validate_provenance,
)
from run_neural_baseline_matrix import Experiment as NeuralExperiment


def source_roots(record: dict[str, Any]) -> dict[str, Path]:
    roots = (
        record["source_roots"]
        if record["source_mode"] == "frozen_selection_artifacts"
        else record["run_output_roots"]
    )
    return {name: Path(value) for name, value in roots.items()}


def require_active_implementation(
    protocol: dict[str, Any], project: Path, name: str
) -> Path:
    path = project / name
    if (
        not path.is_file()
        or protocol.get("implementation_sha256", {}).get(name)
        != file_hash(path)
    ):
        raise ValueError(f"active implementation SHA mismatch: {name}")
    return path


def sentinel_records(protocol: dict[str, Any]) -> list[dict[str, Any]]:
    sentinels = protocol["training_calibration_efficiency"][
        "sentinel_scenarios"
    ]
    if not isinstance(sentinels, dict) or len(sentinels) != 7:
        raise ValueError("training efficiency requires seven sentinels")
    wanted = {
        (str(suite), str(scenario), seed)
        for suite, scenario in sentinels.items()
        for seed in (311, 313)
    }
    records = [
        item
        for item in protocol["source_registry"]
        if (
            str(item["suite"]),
            str(item["scenario"]),
            int(item["seed"]),
        )
        in wanted
    ]
    identities = {
        (str(item["suite"]), str(item["scenario"]), int(item["seed"]))
        for item in records
    }
    if identities != wanted or len(records) != 14:
        raise ValueError("training efficiency sentinel coverage mismatch")
    return sorted(
        records,
        key=lambda item: (
            item["suite"],
            item["scenario"],
            item["seed"],
        ),
    )


def run_subprocess(
    command: list[str], *, project: Path, log: Path
) -> float:
    log.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    with log.open("w", encoding="utf-8") as handle:
        completed = subprocess.run(
            command,
            cwd=project,
            stdout=handle,
            stderr=subprocess.STDOUT,
            check=False,
        )
    elapsed = time.perf_counter() - started
    if completed.returncode != 0:
        raise RuntimeError(
            f"training capture failed with exit {completed.returncode}: {log}"
        )
    return elapsed


def finite_nonnegative(value: object, label: str) -> float:
    import math

    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise ValueError(f"invalid efficiency metric {label}: {value}")
    return result


def child_peak_host_rss_mb() -> float:
    if resource is None:
        raise RuntimeError(
            "formal training-efficiency execution requires Linux resource"
        )
    return finite_nonnegative(
        resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024.0,
        "child peak RSS",
    )


def hardware() -> dict[str, Any]:
    try:
        import torch

        cuda = torch.cuda.is_available()
        return {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "cpu_logical_count": os.cpu_count(),
            "torch": torch.__version__,
            "cuda_available": cuda,
            "cuda_version": torch.version.cuda,
            "gpu_name": torch.cuda.get_device_name(0) if cuda else None,
        }
    except ImportError:
        return {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "cpu_logical_count": os.cpu_count(),
            "torch": None,
            "cuda_available": False,
            "cuda_version": None,
            "gpu_name": None,
        }


def phase_metrics(
    manifest: dict[str, Any],
    *,
    artifact_bytes: int,
    extra_calibration_seconds: float = 0.0,
    peak_host_rss_mb: float | None = None,
) -> dict[str, float]:
    phase = manifest["phase_timings"]
    preparation = finite_nonnegative(
        phase["feature_preparation_seconds"], "feature preparation"
    )
    training = finite_nonnegative(
        phase["training_seconds"], "training"
    )
    calibration = finite_nonnegative(
        phase["calibration_seconds"], "calibration"
    ) + finite_nonnegative(
        extra_calibration_seconds, "extra calibration"
    )
    return {
        "feature_preparation_seconds": preparation,
        "training_seconds": training,
        "calibration_seconds": calibration,
        "total_fit_seconds": preparation + training + calibration,
        "peak_gpu_memory_mb": finite_nonnegative(
            manifest.get("peak_gpu_memory_mb", 0.0), "peak GPU"
        ),
        "peak_host_rss_mb": finite_nonnegative(
            (
                manifest["peak_host_rss_mb"]
                if peak_host_rss_mb is None
                else peak_host_rss_mb
            ),
            "peak RSS",
        ),
        "serialized_deployment_artifact_bytes": float(artifact_bytes),
    }


def trainer_command(
    provenance_path: Path,
    *,
    output_dir: Path,
) -> list[str]:
    provenance = load(provenance_path)
    command = [str(value) for value in provenance["command"]]
    if len(command) < 3:
        raise ValueError("training provenance command is invalid")
    command[0] = sys.executable
    replace_value(command, "--output-dir", str(output_dir.resolve()))
    return command


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def execute_block(
    *,
    record: dict[str, Any],
    repetition: int,
    protocol: dict[str, Any],
    project: Path,
    block_root: Path,
) -> dict[str, Any]:
    from audit_opendetect_deployment_bundle import audit as audit_opendetect
    from audit_pairwise_deployment_bundle import (
        audit_capture as audit_pairwise,
    )
    from audit_vgrf_deployment_bundle import audit_capture as audit_vgrf
    from capture_opendetect_deployment_bundle import (
        capture as capture_opendetect,
    )

    sources = source_roots(record)
    pairwise_capture = block_root / "vgrf_pairwise_capture"
    pairwise_run = block_root / "vgrf_pairwise_run"
    vgrf_capture = block_root / "vgrf_capture"
    opendetect_training_capture = (
        block_root / "opendetect_training_capture"
    )
    opendetect_run = block_root / "opendetect_run"
    opendetect_deployment = block_root / "opendetect_deployment"
    for path in (
        pairwise_capture,
        pairwise_run,
        vgrf_capture,
        opendetect_training_capture,
        opendetect_run,
        opendetect_deployment,
    ):
        path.mkdir(parents=True, exist_ok=True)

    pairwise_command = trainer_command(
        sources["pairwise"] / "provenance.json",
        output_dir=pairwise_run,
    )
    if not (pairwise_capture / "capture_manifest.json").is_file():
        capture_script = require_active_implementation(
            protocol, project, "capture_pairwise_deployment_bundle.py"
        )
        trainer = require_active_implementation(
            protocol, project, "train_hybrid_open_set.py"
        )
        run_subprocess(
            [
                sys.executable,
                str(capture_script),
                "--trainer",
                str(trainer),
                "--capture-dir",
                str(pairwise_capture),
                "--",
                *pairwise_command[2:],
            ],
            project=project,
            log=block_root / "vgrf_pairwise_capture.log",
        )
    pairwise_manifest = load(pairwise_capture / "capture_manifest.json")
    pairwise_audit = audit_pairwise(pairwise_capture)
    if pairwise_audit["passes"] is not True:
        raise ValueError("training Pairwise capture audit failed")

    vgrf_build_seconds = 0.0
    vgrf_workflow_peak_host_rss_mb = 0.0
    if not (vgrf_capture / "capture_manifest.json").is_file():
        builder = require_active_implementation(
            protocol, project, "build_vgrf_deployment_bundle.py"
        )
        parameters = protocol["vgrf_known_only_parameters"]
        vgrf_build_seconds = run_subprocess(
            [
                sys.executable,
                str(builder),
                "--pairwise-capture-dir",
                str(pairwise_capture),
                "--reference-run-dir",
                str(pairwise_run),
                "--output-dir",
                str(vgrf_capture),
                "--source-protocol-manifest-sha256",
                protocol["manifest_sha256"],
                "--shrinkage",
                str(parameters["empirical_bayes_shrinkage"]),
                "--minimum-reliability",
                str(parameters["minimum_reliability"]),
                "--risk-blend",
                str(parameters["risk_blend"]),
                "--known-rejection-quantile",
                str(parameters["known_rejection_quantile"]),
                "--minimum-f1-gain",
                str(parameters["minimum_f1_gain"]),
                "--maximum-correct-risk-increase",
                str(parameters["maximum_correct_risk_increase"]),
                "--minimum-auc-gain",
                str(parameters["minimum_auc_gain"]),
                "--minimum-separation-gain",
                str(parameters["minimum_separation_gain"]),
                "--minimum-strict-proxy-gain",
                str(parameters["minimum_strict_proxy_gain"]),
            ],
            project=project,
            log=block_root / "vgrf_build.log",
        )
        vgrf_workflow_peak_host_rss_mb = max(
            finite_nonnegative(
                pairwise_manifest["peak_host_rss_mb"],
                "Pairwise peak RSS",
            ),
            child_peak_host_rss_mb(),
        )
    else:
        timing_path = block_root / "vgrf_build_timing.json"
        if not timing_path.is_file():
            raise ValueError("resumed VGRF build lacks frozen timing")
        timing = load(timing_path)
        vgrf_build_seconds = float(timing["seconds"])
        vgrf_workflow_peak_host_rss_mb = finite_nonnegative(
            timing["workflow_peak_host_rss_mb"],
            "resumed VGRF workflow peak RSS",
        )
    write_json(
        block_root / "vgrf_build_timing.json",
        {
            "schema_version": "strict_v4_vgrf_build_resource_timing_v1",
            "seconds": vgrf_build_seconds,
            "workflow_peak_host_rss_mb": (
                vgrf_workflow_peak_host_rss_mb
            ),
        },
    )
    vgrf_manifest = load(vgrf_capture / "capture_manifest.json")
    if audit_vgrf(vgrf_capture)["passes"] is not True:
        raise ValueError("training VGRF capture audit failed")

    opendetect_command = trainer_command(
        sources["opendetect"] / "provenance.json",
        output_dir=opendetect_run,
    )
    expected_open_provenance = build_run_provenance(
        NeuralExperiment(
            suite=str(record["suite"]),
            scenario=str(record["scenario"]),
            unknown_classes=str(
                record.get("source_inputs", {}).get(
                    "unknown_classes",
                    opendetect_command[
                        opendetect_command.index("--unknown-classes") + 1
                    ],
                )
            ),
            model="opendetect",
            seed=int(record["seed"]),
            output_dir=str(opendetect_run.resolve()),
        ),
        opendetect_command,
    )
    freeze_or_validate_provenance(
        opendetect_run,
        expected_open_provenance,
        (
            opendetect_run / "metrics.json",
            opendetect_run / "scores.npz",
            opendetect_run / "model.pt",
        ),
    )
    if not (
        opendetect_training_capture / "capture_manifest.json"
    ).is_file():
        capture_training = require_active_implementation(
            protocol, project, "capture_opendetect_training_runtime.py"
        )
        neural_trainer = require_active_implementation(
            protocol, project, "train_neural_open_set.py"
        )
        run_subprocess(
            [
                sys.executable,
                str(capture_training),
                "--trainer",
                str(neural_trainer),
                "--capture-dir",
                str(opendetect_training_capture),
                "--",
                *opendetect_command[2:],
            ],
            project=project,
            log=block_root / "opendetect_training_capture.log",
        )
    open_training_manifest = load(
        opendetect_training_capture / "capture_manifest.json"
    )
    if not (
        opendetect_deployment / "capture_manifest.json"
    ).is_file():
        capture_opendetect(
            opendetect_run,
            pairwise_capture,
            opendetect_deployment,
        )
    open_deployment_manifest = load(
        opendetect_deployment / "capture_manifest.json"
    )
    if audit_opendetect(opendetect_deployment)["passes"] is not True:
        raise ValueError("training OpenDetect deployment audit failed")

    methods = {
        "vgrf": phase_metrics(
            pairwise_manifest,
            artifact_bytes=int(
                vgrf_manifest["deployment_artifact_bytes"]
            ),
            extra_calibration_seconds=vgrf_build_seconds,
            peak_host_rss_mb=vgrf_workflow_peak_host_rss_mb,
        ),
        "opendetect": phase_metrics(
            open_training_manifest,
            artifact_bytes=int(
                open_deployment_manifest["deployment_artifact_bytes"]
            ),
        ),
    }
    value = {
        "schema_version": (
            "strict_v4_vgrf_selected_system_training_efficiency_block_v1"
        ),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "suite": record["suite"],
        "scenario": record["scenario"],
        "seed": int(record["seed"]),
        "repetition": repetition,
        "methods": methods,
        "clean_process_directory_is_unique": True,
        "unknown_or_test_labels_used_for_efficiency_selection": False,
        "hardware": hardware(),
        "source_capture_manifest_sha256": {
            "pairwise": file_hash(
                pairwise_capture / "capture_manifest.json"
            ),
            "vgrf": file_hash(vgrf_capture / "capture_manifest.json"),
            "opendetect_training": file_hash(
                opendetect_training_capture / "capture_manifest.json"
            ),
            "opendetect_deployment": file_hash(
                opendetect_deployment / "capture_manifest.json"
            ),
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def write_state(
    path: Path,
    *,
    protocol: dict[str, Any],
    completed: list[dict[str, Any]],
    state: str,
) -> None:
    value = {
        "schema_version": (
            "strict_v4_vgrf_selected_system_training_efficiency_state_v1"
        ),
        "state": state,
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "expected_pairs": 14,
        "repetitions_per_pair": 3,
        "expected_blocks": 42,
        "completed_blocks": len(completed),
        "blocks": completed,
    }
    write_json(path, value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    args = parser.parse_args()
    project = args.project_root.resolve()
    protocol = load(args.protocol)
    if (
        protocol.get("schema_version")
        != "strict_v4_vgrf_selected_system_execution_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("invalid selected-system execution protocol")
    require_active_implementation(
        protocol, project, Path(__file__).name
    )
    records = sentinel_records(protocol)
    completed: list[dict[str, Any]] = []
    write_state(
        args.state, protocol=protocol, completed=completed, state="running"
    )
    for record in records:
        for repetition in range(3):
            block_root = (
                args.output_root
                / record["suite"]
                / record["scenario"]
                / f"seed{record['seed']}"
                / f"rep{repetition}"
            )
            output = block_root / "training_efficiency.json"
            if output.is_file():
                value = load(output)
                if (
                    value.get("manifest_sha256")
                    != canonical_hash(value)
                    or value.get("protocol_manifest_sha256")
                    != protocol["manifest_sha256"]
                ):
                    raise ValueError("existing training block mismatch")
            else:
                value = execute_block(
                    record=record,
                    repetition=repetition,
                    protocol=protocol,
                    project=project,
                    block_root=block_root,
                )
                write_json(output, value)
            completed.append(
                {
                    "suite": record["suite"],
                    "scenario": record["scenario"],
                    "seed": int(record["seed"]),
                    "repetition": repetition,
                    "output": str(output.resolve()),
                    "output_sha256": file_hash(output),
                }
            )
            write_state(
                args.state,
                protocol=protocol,
                completed=completed,
                state="running",
            )
            print(
                f"trained {record['suite']}/{record['scenario']}_seed"
                f"{record['seed']}_rep{repetition}",
                flush=True,
            )
    write_state(
        args.state,
        protocol=protocol,
        completed=completed,
        state="complete",
    )
    (args.state.parent / "training_efficiency_complete").touch()


if __name__ == "__main__":
    main()
