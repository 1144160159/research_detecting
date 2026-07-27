from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Dict, List

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def validate_protocol(protocol: Dict[str, Any]) -> None:
    confirmation = protocol.get("confirmation", {})
    if (
        protocol.get("schema_version")
        != "strict_v4_krc_csr_confirmation_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("execution_admitted") is not True
        or int(protocol.get("source_registry_count", -1)) != 102
        or int(confirmation.get("full_task_count", -1)) != 306
        or int(confirmation.get("capture_count", -1)) != 306
        or int(confirmation.get("evaluation_count", -1)) != 1836
    ):
        raise ValueError("invalid KRC confirmation protocol")


def validate_capture(
    path: Path,
    *,
    suite: str,
    scenario: str,
    training_seed: int,
    weight: float,
) -> bool:
    if not path.exists():
        return False
    value = load_json(path)
    root = path.parent
    if (
        value.get("schema_version")
        != "strict_v4_krc_csr_runtime_capture_v1"
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("state") != "complete"
        or value.get("task") != {"suite": suite, "scenario": scenario}
        or int(value.get("training_seed", -1)) != int(training_seed)
        or float(value.get("weight", -1.0)) != float(weight)
        or value.get("roundtrip", {}).get("passes") is not True
        or value.get(
            "unknown_or_test_labels_used_for_training_selection_or_calibration"
        )
        is not False
        or file_hash(root / value["runtime_artifact"])
        != value["runtime_artifact_sha256"]
        or file_hash(root / value["evaluation_inputs"])
        != value["evaluation_inputs_sha256"]
    ):
        raise ValueError(f"invalid existing KRC capture: {path}")
    return True


def validate_evaluation(
    path: Path,
    protocol: Dict[str, Any],
    task: Dict[str, Any],
    condition: str,
) -> bool:
    if not path.exists():
        return False
    value = load_json(path)
    if (
        value.get("schema_version")
        != "strict_v4_krc_csr_confirmation_evaluation_v1"
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or value.get("suite") != task["suite"]
        or value.get("scenario") != task["scenario"]
        or int(value.get("training_seed", -1))
        != int(task["training_seed"])
        or int(value.get("corruption_seed", -1))
        != int(task["corruption_seed"])
        or bool(value.get("primary_heldout_scenario"))
        != bool(task["primary_heldout_scenario"])
        or value.get("condition") != condition
    ):
        raise ValueError(f"invalid existing KRC evaluation: {path}")
    return True


def validate_capture_execution(
    path: Path,
    capture_manifest: Path,
    task: Dict[str, Any],
) -> bool:
    if not path.exists():
        return False
    value = load_json(path)
    if (
        value.get("schema_version")
        != "strict_v4_krc_csr_capture_execution_v1"
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("task")
        != {"suite": task["suite"], "scenario": task["scenario"]}
        or int(value.get("training_seed", -1))
        != int(task["training_seed"])
        or value.get("capture_manifest_file_sha256")
        != file_hash(capture_manifest)
        or float(value.get("total_capture_wall_seconds", -1.0)) <= 0.0
    ):
        raise ValueError(f"invalid KRC capture timing: {path}")
    return True


def run_command(
    command: List[str],
    log_path: Path,
    resource_prefix: List[str],
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        subprocess.run(
            [*resource_prefix, *command],
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )


def run(
    protocol: Dict[str, Any],
    protocol_path: Path,
    project_root: Path,
    run_root: Path,
    result_root: Path,
    workers: int,
) -> None:
    validate_protocol(protocol)
    if int(workers) < 1:
        raise ValueError("KRC workers must be positive")
    if int(workers) > int(protocol["resource_contract"]["outer_workers"]):
        raise ValueError("KRC workers exceed frozen resource contract")
    for name, relative in protocol["implementation"].items():
        if (
            file_hash(project_root / relative)
            != protocol["implementation_sha256"][name]
        ):
            raise ValueError(
                f"KRC confirmation implementation SHA mismatch: {name}"
            )
    sources = {
        (record["suite"], record["scenario"]): record
        for record in protocol["source_registry"]
    }
    if len(sources) != 102:
        raise ValueError("KRC source registry is not unique")
    confirmation = protocol["confirmation"]
    resource_prefix = list(
        confirmation.get("subprocess_resource_prefix", [])
    )
    weight = float(confirmation["fixed_augmentation_weight"])

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
            raise ValueError(
                f"KRC source identity drift: {task['suite']}/"
                f"{task['scenario']}"
            )
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
            weight=weight,
        ):
            if task_root.exists() and any(task_root.iterdir()):
                raise ValueError(
                    f"partial KRC capture requires quarantine: {task_root}"
                )
            command = [
                sys.executable,
                str(project_root / protocol["implementation"]["capture"]),
                "--clean-trainer",
                str(
                    project_root
                    / protocol["implementation"]["clean_trainer"]
                ),
                "--robust-trainer",
                str(
                    project_root
                    / protocol["implementation"]["robust_trainer"]
                ),
                "--capture-dir",
                str(task_root),
                "--suite",
                task["suite"],
                "--scenario",
                task["scenario"],
                "--weight",
                str(weight),
                "--sample-fraction",
                str(confirmation["training_sample_fraction"]),
                "--training-seed",
                str(task["training_seed"]),
                "--augmentation-seed",
                str(task["training_seed"]),
                "--health-quantile",
                str(confirmation["health_quantile"]),
                "--validation-corruption-seed",
                str(task["corruption_seed"]),
                "--",
                *source["base_trainer_arguments"],
            ]
            started = time.perf_counter()
            run_command(
                command, task_root / "capture.log", resource_prefix
            )
            elapsed = time.perf_counter() - started
            validate_capture(
                capture_manifest,
                suite=task["suite"],
                scenario=task["scenario"],
                training_seed=int(task["training_seed"]),
                weight=weight,
            )
            evidence: Dict[str, Any] = {
                "schema_version": (
                    "strict_v4_krc_csr_capture_execution_v1"
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
                    "full_capture_subprocess_including_two_fits_"
                    "known_only_certificate_and_serialization"
                ),
                "resource_prefix": resource_prefix,
                "unknown_or_test_labels_used_for_cost_selection": False,
            }
            evidence["manifest_sha256"] = canonical_hash(evidence)
            capture_execution.write_text(
                json.dumps(evidence, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        if not validate_capture_execution(
            capture_execution, capture_manifest, task
        ):
            raise ValueError(f"missing KRC timing: {capture_execution}")
        for condition in confirmation["conditions"]:
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
                str(project_root / protocol["implementation"]["evaluator"]),
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
            run_command(command, output.with_suffix(".log"), resource_prefix)
            validate_evaluation(output, protocol, task, condition)
        return (
            f"completed {index}/{len(confirmation['tasks'])} "
            f"{task['suite']}/{task['scenario']}/"
            f"seed{task['training_seed']}"
        )

    with ThreadPoolExecutor(max_workers=int(workers)) as executor:
        futures = {
            executor.submit(execute_task, index, task): index
            for index, task in enumerate(confirmation["tasks"], start=1)
        }
        for future in as_completed(futures):
            print(future.result(), flush=True)

    result_root.mkdir(parents=True, exist_ok=True)
    summary_path = result_root / "summary.json"
    audit_path = result_root / "audit.json"
    run_command(
        [
            sys.executable,
            str(project_root / protocol["implementation"]["summarizer"]),
            "--protocol",
            str(protocol_path),
            "--capture-root",
            str(run_root / "captures"),
            "--evaluation-root",
            str(run_root / "evaluations"),
            "--output",
            str(summary_path),
        ],
        result_root / "summary.log",
        resource_prefix,
    )
    run_command(
        [
            sys.executable,
            str(project_root / protocol["implementation"]["auditor"]),
            "--protocol",
            str(protocol_path),
            "--summary",
            str(summary_path),
            "--capture-root",
            str(run_root / "captures"),
            "--evaluation-root",
            str(run_root / "evaluations"),
            "--output",
            str(audit_path),
        ],
        result_root / "audit.log",
        resource_prefix,
    )
    summary = load_json(summary_path)
    audit = load_json(audit_path)
    if (
        summary.get("manifest_sha256") != canonical_hash(summary)
        or audit.get("manifest_sha256") != canonical_hash(audit)
        or audit.get("summary_manifest_sha256")
        != summary["manifest_sha256"]
    ):
        raise RuntimeError("KRC finalization integrity failure")
    print(
        json.dumps(
            {
                "summary_manifest_sha256": summary["manifest_sha256"],
                "summary_passes": summary["passes"],
                "audit_manifest_sha256": audit["manifest_sha256"],
                "audit_passes": audit["passes"],
                "selection": summary["selection"],
            },
            sort_keys=True,
        ),
        flush=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--workers", type=int)
    args = parser.parse_args()
    protocol_path = args.protocol.resolve()
    protocol = load_json(protocol_path)
    workers = (
        int(args.workers)
        if args.workers is not None
        else int(protocol["confirmation"]["outer_workers"])
    )
    run(
        protocol,
        protocol_path,
        args.project_root.resolve(),
        args.run_root.resolve(),
        args.result_root.resolve(),
        workers,
    )


if __name__ == "__main__":
    main()
