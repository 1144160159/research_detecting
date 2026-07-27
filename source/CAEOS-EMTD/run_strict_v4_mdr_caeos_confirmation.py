from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from select_mdr_caeos_weight import load


def validate_protocol(protocol: Dict[str, Any]) -> None:
    if (
        protocol.get("schema_version")
        != "strict_v4_mdr_caeos_confirmation_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("execution_admitted") is not True
        or int(protocol.get("source_registry_count", -1)) != 102
        or int(protocol.get("confirmation", {}).get("task_count", -1))
        != 306
        or int(
            protocol.get("confirmation", {}).get("evaluation_count", -1)
        )
        != 1836
    ):
        raise ValueError("invalid MDR confirmation protocol")


def validate_capture(
    path: Path,
    *,
    suite: str,
    scenario: str,
    training_seed: int,
    selected_weight: float,
) -> bool:
    if not path.exists():
        return False
    value = load(path)
    if (
        value.get("schema_version")
        != "strict_v4_mdr_caeos_runtime_capture_v1"
        or value.get("state") != "complete"
        or value.get("task") != {"suite": suite, "scenario": scenario}
        or int(value.get("training_seed", -1)) != int(training_seed)
        or float(value.get("weight", -1.0)) != float(selected_weight)
        or value.get("roundtrip", {}).get("passes") is not True
    ):
        raise ValueError(f"invalid existing MDR confirmation capture: {path}")
    root = path.parent
    if (
        file_hash(root / value["runtime_artifact"])
        != value["runtime_artifact_sha256"]
        or file_hash(root / value["evaluation_inputs"])
        != value["evaluation_inputs_sha256"]
    ):
        raise ValueError(f"MDR confirmation capture hash mismatch: {path}")
    return True


def validate_evaluation(
    path: Path,
    protocol: Dict[str, Any],
    task: Dict[str, Any],
    condition: str,
) -> bool:
    if not path.exists():
        return False
    value = load(path)
    if (
        value.get("schema_version")
        != "strict_v4_mdr_caeos_confirmation_evaluation_v1"
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or value.get("suite") != task["suite"]
        or value.get("scenario") != task["scenario"]
        or int(value.get("training_seed", -1))
        != int(task["training_seed"])
        or int(value.get("corruption_seed", -1))
        != int(task["corruption_seed"])
        or value.get("condition") != condition
    ):
        raise ValueError(
            f"invalid existing MDR confirmation evaluation: {path}"
        )
    return True


def run_command(command: list[str], log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        subprocess.run(
            command,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )


def validate_capture_execution(
    path: Path,
    *,
    suite: str,
    scenario: str,
    training_seed: int,
    capture_manifest: Path,
) -> bool:
    if not path.exists():
        return False
    value = load(path)
    if (
        value.get("schema_version")
        != "strict_v4_mdr_caeos_capture_execution_v1"
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("task") != {"suite": suite, "scenario": scenario}
        or int(value.get("training_seed", -1)) != int(training_seed)
        or value.get("capture_manifest_file_sha256")
        != file_hash(capture_manifest)
        or not isinstance(
            value.get("total_capture_wall_seconds"), (int, float)
        )
        or float(value["total_capture_wall_seconds"]) <= 0.0
        or value.get("scope")
        != (
            "full_capture_subprocess_including_training_calibration_"
            "validation_profile_and_serialization"
        )
    ):
        raise ValueError(f"invalid capture execution evidence: {path}")
    return True


def run(
    protocol: Dict[str, Any],
    protocol_path: Path,
    project_root: Path,
    run_root: Path,
    workers: int,
) -> None:
    validate_protocol(protocol)
    for name, relative in protocol["implementation"].items():
        actual = file_hash(project_root / relative)
        expected = protocol["implementation_sha256"][name]
        if actual != expected:
            raise ValueError(
                f"MDR confirmation implementation SHA mismatch: {name}"
            )
    sources = {
        (record["suite"], record["scenario"]): record
        for record in protocol["source_registry"]
    }
    if len(sources) != 102:
        raise ValueError("MDR confirmation source registry is not unique")
    selected_weight = float(protocol["selected_augmentation_weight"])

    def execute_task(index: int, task: Dict[str, Any]) -> str:
        source = sources[(task["suite"], task["scenario"])]
        provenance = (
            Path(source["candidate_source_root"]) / "provenance.json"
        )
        if (
            file_hash(provenance)
            != source["candidate_source_provenance_sha256"]
            or file_hash(Path(source["csv"])) != source["csv_sha256"]
            or file_hash(Path(source["config"])) != source["config_sha256"]
        ):
            raise ValueError("MDR confirmation source identity drift")
        task_root = (
            run_root
            / "captures"
            / task["suite"]
            / task["scenario"]
            / f"seed{int(task['training_seed'])}"
        )
        capture_manifest = task_root / "capture_manifest.json"
        capture_execution = task_root / "capture_execution.json"
        if not validate_capture(
            capture_manifest,
            suite=task["suite"],
            scenario=task["scenario"],
            training_seed=int(task["training_seed"]),
            selected_weight=selected_weight,
        ):
            if task_root.exists() and any(task_root.iterdir()):
                raise ValueError(
                    f"partial MDR confirmation capture exists: {task_root}"
                )
            command = [
                sys.executable,
                str(project_root / "capture_mdr_caeos_runtime.py"),
                "--clean-trainer",
                str(project_root / "train_hybrid_open_set.py"),
                "--robust-trainer",
                str(project_root / "train_mdr_caeos_open_set.py"),
                "--capture-dir",
                str(task_root),
                "--suite",
                task["suite"],
                "--scenario",
                task["scenario"],
                "--weight",
                str(selected_weight),
                "--sample-fraction",
                str(
                    protocol["confirmation"]["training_sample_fraction"]
                ),
                "--training-seed",
                str(task["training_seed"]),
                "--augmentation-seed",
                str(task["training_seed"]),
                "--health-quantile",
                str(protocol["confirmation"]["health_quantile"]),
                "--validation-corruption-seed",
                str(task["corruption_seed"]),
                "--",
                *source["base_trainer_arguments"],
            ]
            started = time.perf_counter()
            run_command(command, task_root / "capture.log")
            elapsed = time.perf_counter() - started
            validate_capture(
                capture_manifest,
                suite=task["suite"],
                scenario=task["scenario"],
                training_seed=int(task["training_seed"]),
                selected_weight=selected_weight,
            )
            execution_value = {
                "schema_version": (
                    "strict_v4_mdr_caeos_capture_execution_v1"
                ),
                "state": "complete",
                "task": {
                    "suite": task["suite"],
                    "scenario": task["scenario"],
                },
                "training_seed": int(task["training_seed"]),
                "capture_manifest_file_sha256": file_hash(
                    capture_manifest
                ),
                "total_capture_wall_seconds": float(elapsed),
                "timer": "time.perf_counter",
                "scope": (
                    "full_capture_subprocess_including_training_calibration_"
                    "validation_profile_and_serialization"
                ),
                "unknown_or_test_labels_used_for_cost_selection": False,
            }
            execution_value["manifest_sha256"] = canonical_hash(
                execution_value
            )
            capture_execution.write_text(
                json.dumps(
                    execution_value, indent=2, sort_keys=True
                )
                + "\n",
                encoding="utf-8",
            )
        if not validate_capture_execution(
            capture_execution,
            suite=task["suite"],
            scenario=task["scenario"],
            training_seed=int(task["training_seed"]),
            capture_manifest=capture_manifest,
        ):
            raise ValueError(
                f"missing MDR total capture timing: {capture_execution}"
            )
        for condition in protocol["confirmation"]["conditions"]:
            output = (
                run_root
                / "evaluations"
                / task["suite"]
                / task["scenario"]
                / f"seed{int(task['training_seed'])}"
                / condition
                / "evaluation.json"
            )
            if validate_evaluation(output, protocol, task, condition):
                continue
            command = [
                sys.executable,
                str(
                    project_root
                    / "evaluate_mdr_caeos_confirmation_runtime.py"
                ),
                "--protocol",
                str(protocol_path),
                "--capture-dir",
                str(task_root),
                "--suite",
                task["suite"],
                "--scenario",
                task["scenario"],
                "--training-seed",
                str(task["training_seed"]),
                "--corruption-seed",
                str(task["corruption_seed"]),
                "--condition",
                condition,
                "--output",
                str(output),
            ]
            run_command(command, output.with_suffix(".log"))
            validate_evaluation(output, protocol, task, condition)
        return (
            f"completed {index}/{len(protocol['confirmation']['tasks'])} "
            f"{task['suite']}/{task['scenario']}/"
            f"seed{task['training_seed']}"
        )

    if int(workers) < 1:
        raise ValueError("MDR confirmation workers must be positive")
    with ThreadPoolExecutor(max_workers=int(workers)) as executor:
        futures = {
            executor.submit(execute_task, index, task): index
            for index, task in enumerate(
                protocol["confirmation"]["tasks"], start=1
            )
        }
        for future in as_completed(futures):
            print(future.result(), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--workers", type=int)
    args = parser.parse_args()
    protocol_path = args.protocol.resolve()
    protocol = load(protocol_path)
    run_root = args.run_root.resolve()
    run_root.mkdir(parents=True, exist_ok=True)
    workers = (
        int(args.workers)
        if args.workers is not None
        else int(protocol["confirmation"]["outer_workers"])
    )
    run(
        protocol,
        protocol_path,
        args.project_root.resolve(),
        run_root,
        workers,
    )


if __name__ == "__main__":
    main()
