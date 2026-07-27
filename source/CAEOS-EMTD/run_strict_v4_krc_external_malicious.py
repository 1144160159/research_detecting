from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_") or (
        "unnamed"
    )


def task_block(run_root: Path, task: Dict[str, Any]) -> Path:
    return (
        run_root
        / task["dataset"]
        / (
            f"{slug(task['unknown_attack_family'])}_"
            f"seed{int(task['training_seed'])}"
        )
    )


def verify_protocol(
    protocol: Dict[str, Any],
    protocol_path: Path,
    project_root: Path,
    run_root: Path,
    capture_workers: int,
) -> None:
    if (
        protocol.get("schema_version")
        != "strict_v4_krc_external_malicious_execution_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("execution_admitted") is not True
        or protocol.get("algorithm") != "krc_csr_caeos_v1"
        or run_root.resolve().as_posix() != protocol["result_root"]
    ):
        raise ValueError("canonical admitted KRC external protocol required")
    maximum = int(
        protocol["resource_contract"]["candidate_capture_outer_workers"]
    )
    if int(capture_workers) < 1 or int(capture_workers) > maximum:
        raise ValueError("capture workers exceed frozen resource contract")
    for relative, expected in protocol["implementation_sha256"].items():
        if file_hash(project_root / relative) != expected:
            raise ValueError(
                f"KRC external implementation SHA mismatch: {relative}"
            )
    blocks = [task_block(run_root, task) for task in protocol["tasks"]]
    if len(blocks) != len(set(blocks)):
        raise ValueError("KRC external task paths collide after slugging")


def base_arguments(
    task: Dict[str, Any], policy: Dict[str, Any]
) -> list[str]:
    return [
        "--csv",
        task["csv"],
        "--config",
        task["config"],
        "--unknown-classes",
        task["unknown_attack_family"],
        "--benign-class",
        task["benign_label"],
        "--split-strategy",
        "fingerprint_grouped",
        "--max-per-class",
        "4000",
        "--estimators",
        str(policy["estimators"]),
        "--jobs",
        str(policy["jobs"]),
        "--known-acceptance",
        str(policy["known_acceptance"]),
        "--risk-selection",
        policy["risk_selection"],
        "--pseudo-unknown-max-alpha",
        str(policy["pseudo_unknown_max_alpha"]),
        "--pseudo-unknown-min-fold-gain",
        str(policy["pseudo_unknown_min_fold_gain"]),
        "--boundary-hard-pseudo-fraction",
        str(policy["boundary_hard_pseudo_fraction"]),
        "--boundary-interpolation",
        str(policy["boundary_interpolation"]),
        "--boundary-max-per-task",
        str(policy["boundary_max_per_task"]),
        "--boundary-training-objective",
        policy["boundary_training_objective"],
        "--risk-policy-name",
        "strict_v4_krc_external_pairwise_v1",
        "--seed",
        str(task["training_seed"]),
        "--output-dir",
        "replaced_by_capture",
    ]


def capture_command(
    *,
    python: str,
    project_root: Path,
    capture_dir: Path,
    task: Dict[str, Any],
    protocol: Dict[str, Any],
) -> list[str]:
    krc = protocol["krc_policy"]
    return [
        python,
        str(project_root / "capture_krc_csr_confirmation_runtime.py"),
        "--clean-trainer",
        str(project_root / "train_hybrid_open_set.py"),
        "--robust-trainer",
        str(project_root / "train_mdr_caeos_open_set.py"),
        "--capture-dir",
        str(capture_dir),
        "--suite",
        task["dataset"],
        "--scenario",
        task["unknown_attack_family"],
        "--weight",
        str(krc["augmentation_weight"]),
        "--sample-fraction",
        str(krc["sample_fraction"]),
        "--training-seed",
        str(task["training_seed"]),
        "--augmentation-seed",
        str(task["augmentation_seed"]),
        "--health-quantile",
        str(krc["health_quantile"]),
        "--validation-corruption-seed",
        str(task["validation_profile_seed"]),
        "--",
        *base_arguments(task, protocol["pairwise_runtime_policy"]),
    ]


def candidate_command(
    *,
    python: str,
    project_root: Path,
    protocol_path: Path,
    capture_dir: Path,
    output: Path,
    task: Dict[str, Any],
) -> list[str]:
    return [
        python,
        str(project_root / "evaluate_krc_external_runtime.py"),
        "--capture-dir",
        str(capture_dir),
        "--protocol",
        str(protocol_path),
        "--dataset",
        task["dataset"],
        "--unknown-attack-family",
        task["unknown_attack_family"],
        "--training-seed",
        str(task["training_seed"]),
        "--output",
        str(output),
    ]


def opendetect_command(
    *,
    python: str,
    project_root: Path,
    output: Path,
    task: Dict[str, Any],
    policy: Dict[str, Any],
) -> list[str]:
    return [
        python,
        str(project_root / "train_neural_open_set.py"),
        "--dataset",
        "tabular",
        "--csv",
        task["csv"],
        "--config",
        task["config"],
        "--unknown-classes",
        task["unknown_attack_family"],
        "--benign-class",
        task["benign_label"],
        "--split-strategy",
        "fingerprint_grouped",
        "--max-per-class",
        "4000",
        "--model",
        "opendetect",
        "--epochs",
        str(policy["epochs"]),
        "--patience",
        str(policy["patience"]),
        "--hidden-dim",
        str(policy["hidden_dim"]),
        "--embedding-dim",
        str(policy["embedding_dim"]),
        "--known-acceptance",
        str(policy["known_acceptance"]),
        "--seed",
        str(task["opendetect_seed"]),
        "--device",
        "auto",
        "--output-dir",
        str(output),
    ]


def run_command(
    command: list[str],
    directory: Path,
    resource_prefix: list[str],
) -> float:
    directory.mkdir(parents=True, exist_ok=True)
    log = directory / "execution.log"
    started = time.perf_counter()
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"command": command}) + "\n")
        handle.flush()
        completed = subprocess.run(
            [*resource_prefix, *command],
            stdout=handle,
            stderr=subprocess.STDOUT,
        )
    elapsed = time.perf_counter() - started
    if completed.returncode != 0:
        failure = {
            "schema_version": (
                "strict_v4_krc_external_execution_failure_v1"
            ),
            "returncode": completed.returncode,
            "command": command,
            "log_sha256": file_hash(log),
            "wall_seconds": float(elapsed),
        }
        (directory / "failure.json").write_text(
            json.dumps(failure, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        raise RuntimeError(f"KRC external command failed: {directory}")
    return float(elapsed)


def validate_capture(
    capture_dir: Path,
    task: Dict[str, Any],
    protocol: Dict[str, Any],
) -> bool:
    manifest_path = capture_dir / "capture_manifest.json"
    if not manifest_path.is_file():
        return False
    value = load(manifest_path)
    artifact = capture_dir / value.get("runtime_artifact", "")
    inputs = capture_dir / value.get("evaluation_inputs", "")
    if (
        value.get("schema_version")
        != "strict_v4_krc_csr_runtime_capture_v1"
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("state") != "complete"
        or value.get("algorithm") != "krc_csr_caeos_v1"
        or value.get("task")
        != {
            "suite": task["dataset"],
            "scenario": task["unknown_attack_family"],
        }
        or int(value.get("training_seed", -1))
        != int(task["training_seed"])
        or float(value.get("weight", -1.0))
        != float(protocol["krc_policy"]["augmentation_weight"])
        or value.get("roundtrip", {}).get("passes") is not True
        or file_hash(artifact) != value.get("runtime_artifact_sha256")
        or file_hash(inputs) != value.get("evaluation_inputs_sha256")
    ):
        raise ValueError(f"invalid KRC external capture: {capture_dir}")
    return True


def validate_metrics(
    output: Path,
    task: Dict[str, Any],
    protocol: Dict[str, Any],
    method: str,
) -> bool:
    metrics_path = output / "metrics.json"
    provenance_path = output / "provenance.json"
    if not metrics_path.is_file() and not provenance_path.is_file():
        return False
    if not metrics_path.is_file() or not provenance_path.is_file():
        raise ValueError(f"partial KRC external metrics: {output}")
    provenance = load(provenance_path)
    if (
        provenance.get("manifest_sha256") != canonical_hash(provenance)
        or provenance.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or provenance.get("metrics_sha256") != file_hash(metrics_path)
        or provenance.get("method") != method
        or provenance.get("dataset") != task["dataset"]
        or provenance.get("unknown_attack_family")
        != task["unknown_attack_family"]
        or int(provenance.get("training_seed", -1))
        != int(task["training_seed"])
        or provenance.get(
            "unknown_or_test_metrics_used_for_configuration"
        )
        is not False
    ):
        raise ValueError(f"invalid KRC external provenance: {output}")
    return True


def write_provenance(
    *,
    output: Path,
    protocol: Dict[str, Any],
    task: Dict[str, Any],
    method: str,
    command: list[str],
) -> None:
    metrics = output / "metrics.json"
    value = {
        "schema_version": (
            "strict_v4_krc_external_malicious_provenance_v1"
        ),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "dataset": task["dataset"],
        "unknown_attack_family": task["unknown_attack_family"],
        "training_seed": int(task["training_seed"]),
        "method": method,
        "csv_sha256": task["csv_sha256"],
        "sidecar_file_sha256": task["sidecar_file_sha256"],
        "config_sha256": task["config_sha256"],
        "metrics_sha256": file_hash(metrics),
        "command": command,
        "unknown_or_test_metrics_used_for_configuration": False,
    }
    value["manifest_sha256"] = canonical_hash(value)
    (output / "provenance.json").write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def verify_task_inputs(task: Dict[str, Any]) -> None:
    if (
        file_hash(Path(task["csv"])) != task["csv_sha256"]
        or file_hash(Path(task["sidecar"]))
        != task["sidecar_file_sha256"]
        or file_hash(Path(task["config"])) != task["config_sha256"]
        or int(task["prepared_seed"])
        != int(task["training_seed"])
        or int(task["split_seed"]) != int(task["training_seed"])
        or int(task["opendetect_seed"]) != int(task["training_seed"])
    ):
        raise ValueError("KRC external task input or seed contract drift")


def execute_candidate_task(
    *,
    python: str,
    project_root: Path,
    protocol_path: Path,
    protocol: Dict[str, Any],
    run_root: Path,
    task: Dict[str, Any],
    resource_prefix: list[str],
) -> str:
    verify_task_inputs(task)
    block = task_block(run_root, task)
    capture_dir = block / "krc_capture"
    candidate_dir = block / "krc_csr_caeos_v1"
    capture_cmd = capture_command(
        python=python,
        project_root=project_root,
        capture_dir=capture_dir,
        task=task,
        protocol=protocol,
    )
    if not validate_capture(capture_dir, task, protocol):
        if capture_dir.exists() and any(capture_dir.iterdir()):
            raise ValueError(
                f"partial KRC external capture requires quarantine: "
                f"{capture_dir}"
            )
        elapsed = run_command(capture_cmd, capture_dir, resource_prefix)
        if not validate_capture(capture_dir, task, protocol):
            raise ValueError("KRC external capture missing after command")
        timing = {
            "schema_version": (
                "strict_v4_krc_external_capture_execution_v1"
            ),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "dataset": task["dataset"],
            "unknown_attack_family": task["unknown_attack_family"],
            "training_seed": int(task["training_seed"]),
            "capture_manifest_file_sha256": file_hash(
                capture_dir / "capture_manifest.json"
            ),
            "wall_seconds": elapsed,
        }
        timing["manifest_sha256"] = canonical_hash(timing)
        (capture_dir / "capture_execution.json").write_text(
            json.dumps(timing, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    candidate_cmd = candidate_command(
        python=python,
        project_root=project_root,
        protocol_path=protocol_path,
        capture_dir=capture_dir,
        output=candidate_dir / "metrics.json",
        task=task,
    )
    if not validate_metrics(
        candidate_dir, task, protocol, "krc_csr_caeos_v1"
    ):
        if candidate_dir.exists() and any(candidate_dir.iterdir()):
            raise ValueError(
                f"partial KRC external candidate requires quarantine: "
                f"{candidate_dir}"
            )
        run_command(candidate_cmd, candidate_dir, resource_prefix)
        write_provenance(
            output=candidate_dir,
            protocol=protocol,
            task=task,
            method="krc_csr_caeos_v1",
            command=candidate_cmd,
        )
        validate_metrics(
            candidate_dir, task, protocol, "krc_csr_caeos_v1"
        )
    return (
        f"{task['dataset']}/{task['unknown_attack_family']}/"
        f"seed{task['training_seed']}"
    )


def execute_opendetect_task(
    *,
    python: str,
    project_root: Path,
    protocol: Dict[str, Any],
    run_root: Path,
    task: Dict[str, Any],
    resource_prefix: list[str],
) -> str:
    verify_task_inputs(task)
    block = task_block(run_root, task)
    output = block / "opendetect"
    command = opendetect_command(
        python=python,
        project_root=project_root,
        output=output,
        task=task,
        policy=protocol["opendetect_policy"],
    )
    if not validate_metrics(output, task, protocol, "opendetect"):
        if output.exists() and any(output.iterdir()):
            raise ValueError(
                f"partial OpenDetect external output requires quarantine: "
                f"{output}"
            )
        run_command(command, output, resource_prefix)
        write_provenance(
            output=output,
            protocol=protocol,
            task=task,
            method="opendetect",
            command=command,
        )
        validate_metrics(output, task, protocol, "opendetect")
    return (
        f"{task['dataset']}/{task['unknown_attack_family']}/"
        f"seed{task['training_seed']}"
    )


def run(args: argparse.Namespace) -> None:
    protocol_path = args.protocol.resolve()
    protocol = load(protocol_path)
    run_root = args.run_root.resolve()
    project_root = args.project_root.resolve()
    workers = (
        int(args.capture_workers)
        if args.capture_workers is not None
        else int(
            protocol["resource_contract"]["candidate_capture_outer_workers"]
        )
    )
    verify_protocol(
        protocol,
        protocol_path,
        project_root,
        run_root,
        workers,
    )
    resource_prefix = list(args.resource_prefix)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(
                execute_candidate_task,
                python=args.python,
                project_root=project_root,
                protocol_path=protocol_path,
                protocol=protocol,
                run_root=run_root,
                task=task,
                resource_prefix=resource_prefix,
            )
            for task in protocol["tasks"]
        ]
        for index, future in enumerate(as_completed(futures), start=1):
            print(
                f"candidate {index}/{len(futures)} {future.result()}",
                flush=True,
            )

    for index, task in enumerate(protocol["tasks"], start=1):
        identity_value = execute_opendetect_task(
            python=args.python,
            project_root=project_root,
            protocol=protocol,
            run_root=run_root,
            task=task,
            resource_prefix=resource_prefix,
        )
        print(
            f"opendetect {index}/{len(protocol['tasks'])} "
            f"{identity_value}",
            flush=True,
        )

    failures = list(run_root.rglob("failure.json"))
    candidate_metrics = list(
        run_root.glob("**/krc_csr_caeos_v1/metrics.json")
    )
    opendetect_metrics = list(
        run_root.glob("**/opendetect/metrics.json")
    )
    captures = list(run_root.glob("**/krc_capture/capture_manifest.json"))
    expected = int(protocol["task_counts"]["total_scenarios_per_algorithm"])
    if (
        failures
        or len(captures) != expected
        or len(candidate_metrics) != expected
        or len(opendetect_metrics) != expected
    ):
        raise ValueError("KRC external execution coverage gate failed")
    (run_root / "execution_complete").touch()

    for script, output in (
        (
            "summarize_strict_v4_krc_external_malicious.py",
            run_root / "summary.json",
        ),
        (
            "audit_strict_v4_krc_external_malicious.py",
            run_root / "audit.json",
        ),
    ):
        command = [
            args.python,
            str(project_root / script),
            "--protocol",
            str(protocol_path),
            "--run-root",
            str(run_root),
            "--output",
            str(output),
        ]
        if script.startswith("audit_"):
            command.extend(["--summary", str(run_root / "summary.json")])
        run_command(command, run_root, resource_prefix)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--capture-workers", type=int)
    parser.add_argument(
        "--resource-prefix",
        nargs="*",
        default=["ionice", "-c3", "nice", "-n19"],
    )
    run(parser.parse_args())


if __name__ == "__main__":
    main()
