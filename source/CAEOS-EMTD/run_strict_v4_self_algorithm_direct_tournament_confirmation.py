from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable

from capture_pairwise_runtime import file_hash
from certify_rrc_csr_scenario import (
    certify_seed_records,
    seed_record_from_capture,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash
from materialize_rrc_csr_runtime import materialize


PROTOCOL_SCHEMA = "strict_v4_self_algorithm_direct_tournament_protocol_v1"
COMPLETION_SCHEMA = (
    "strict_v4_self_algorithm_direct_tournament_completion_v1"
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def require_canonical(
    value: dict[str, Any], schema: str, label: str
) -> None:
    if (
        value.get("schema_version") != schema
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError(f"canonical {label} required")


def set_option(arguments: Iterable[str], name: str, value: Any) -> list[str]:
    output = list(arguments)
    if name in output:
        index = output.index(name)
        if index + 1 >= len(output):
            raise ValueError(f"option lacks value: {name}")
        output[index + 1] = str(value)
    else:
        output.extend([name, str(value)])
    return output


def task_root(run_root: Path, task: dict[str, Any]) -> Path:
    return (
        run_root
        / "task_runs"
        / task["suite"]
        / task["scenario"]
        / f"seed{int(task['training_seed'])}"
    )


def run_logged(command: list[str], log: Path, root: Path) -> None:
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w", encoding="utf-8") as handle:
        subprocess.run(
            command,
            cwd=root,
            stdout=handle,
            stderr=subprocess.STDOUT,
            check=True,
        )


def trainer_arguments(
    protocol: dict[str, Any],
    task: dict[str, Any],
    output_dir: Path,
    *,
    challenger: bool,
) -> list[str]:
    arguments = list(
        task["source_registry_manifest"]["base_trainer_arguments"]
    )
    for name, value in (
        ("--seed", int(task["training_seed"])),
        ("--output-dir", output_dir),
        ("--jobs", int(protocol["resource_contract"]["model_jobs"])),
        ("--test-corruption-kind", "none"),
        ("--test-corruption-severity", 0.0),
        ("--test-corruption-seed", int(task["corruption_seed"])),
        ("--train-label-noise", 0.0),
    ):
        arguments = set_option(arguments, name, value)
    if not challenger:
        return arguments
    controls = protocol["candidate_training"]["pug_execution_controls"]
    mapping = {
        "--risk-selection": controls["candidate_risk_selection"],
        "--risk-policy-name": controls["candidate_policy_name"],
        "--pseudo-unknown-max-alpha": controls["pseudo_unknown_max_alpha"],
        "--pseudo-unknown-min-fold-gain": controls[
            "pseudo_unknown_min_fold_gain"
        ],
        "--boundary-hard-pseudo-fraction": controls[
            "boundary_hard_pseudo_fraction"
        ],
        "--boundary-interpolation": controls["boundary_interpolation"],
        "--boundary-max-per-task": controls["boundary_max_per_task"],
        "--boundary-training-objective": controls[
            "boundary_training_objective"
        ],
    }
    for name, value in mapping.items():
        arguments = set_option(arguments, name, value)
    return arguments


def verify_source(task: dict[str, Any]) -> None:
    source = task["source_registry_manifest"]
    for name in ("csv", "config"):
        path = Path(source[name])
        if not path.is_file() or file_hash(path) != source[f"{name}_sha256"]:
            raise ValueError(
                f"frozen source drifted for {task['identity']}: {name}"
            )


def complete_challenger(directory: Path, train_dir: Path) -> bool:
    manifest_path = directory / "capture_manifest.json"
    if not manifest_path.is_file():
        return False
    manifest = load(manifest_path)
    return bool(
        manifest.get("schema_version")
        == "strict_v4_pairwise_runtime_capture_v1"
        and manifest.get("equivalence", {}).get("passes") is True
        and (directory / manifest["deployment_artifact"]).is_file()
        and (directory / manifest["benchmark_inputs"]).is_file()
        and all(
            (train_dir / name).is_file()
            for name in ("metrics.json", "scores.npz")
        )
    )


def capture_challenger(
    protocol: dict[str, Any],
    task: dict[str, Any],
    root: Path,
    run_root: Path,
    python: str,
) -> None:
    block = task_root(run_root, task)
    capture_dir = block / "challenger_capture"
    train_dir = block / "challenger_train"
    if complete_challenger(capture_dir, train_dir):
        return
    if (
        (capture_dir.exists() and any(capture_dir.iterdir()))
        or (train_dir.exists() and any(train_dir.iterdir()))
    ):
        raise ValueError(
            f"partial challenger task requires quarantine: {block}"
        )
    command = [
        python,
        str(root / "capture_pairwise_runtime.py"),
        "--trainer",
        str(root / "train_hybrid_open_set.py"),
        "--capture-dir",
        str(capture_dir),
        "--",
        *trainer_arguments(
            protocol, task, train_dir, challenger=True
        ),
    ]
    run_logged(command, block / "challenger_capture.log", root)
    if not complete_challenger(capture_dir, train_dir):
        raise ValueError("challenger capture did not close")


def incumbent_schema(protocol: dict[str, Any]) -> str:
    return (
        "strict_v4_krc_csr_runtime_capture_v1"
        if protocol["incumbent_algorithm"] == "krc_csr_caeos_v1"
        else "strict_v4_csr_caeos_runtime_capture_v1"
    )


def complete_incumbent_source(
    protocol: dict[str, Any], directory: Path
) -> bool:
    path = directory / "capture_manifest.json"
    if not path.is_file():
        return False
    value = load(path)
    return bool(
        value.get("schema_version") == incumbent_schema(protocol)
        and value.get("manifest_sha256") == canonical_hash(value)
        and value.get("state") == "complete"
        and (directory / value["runtime_artifact"]).is_file()
        and (directory / value["evaluation_inputs"]).is_file()
    )


def capture_incumbent_source(
    protocol: dict[str, Any],
    task: dict[str, Any],
    root: Path,
    run_root: Path,
    python: str,
) -> None:
    block = task_root(run_root, task)
    is_rrc = protocol["incumbent_algorithm"] == "rrc_csr_caeos_v1"
    directory = (
        block / "incumbent_source_capture"
        if is_rrc
        else block / "incumbent_capture"
    )
    if complete_incumbent_source(protocol, directory):
        return
    if directory.exists() and any(directory.iterdir()):
        raise ValueError(
            f"partial incumbent task requires quarantine: {directory}"
        )
    executable = (
        "capture_csr_caeos_runtime.py"
        if is_rrc
        else "capture_krc_csr_confirmation_runtime.py"
    )
    training = protocol["candidate_training"]
    command = [
        python,
        str(root / executable),
        "--clean-trainer",
        str(root / "train_hybrid_open_set.py"),
        "--robust-trainer",
        str(root / "train_mdr_caeos_open_set.py"),
        "--capture-dir",
        str(directory),
        "--suite",
        task["suite"],
        "--scenario",
        task["scenario"],
        "--weight",
        str(training["fixed_augmentation_weight"]),
        "--sample-fraction",
        str(training["training_sample_fraction"]),
        "--training-seed",
        str(task["training_seed"]),
        "--augmentation-seed",
        str(task["training_seed"]),
        "--health-quantile",
        str(training["health_quantile"]),
        "--validation-corruption-seed",
        str(task["corruption_seed"]),
        "--",
        *trainer_arguments(
            protocol,
            task,
            block / "incumbent_train",
            challenger=False,
        ),
    ]
    run_logged(command, block / "incumbent_capture.log", root)
    if not complete_incumbent_source(protocol, directory):
        raise ValueError("incumbent source capture did not close")


def materialize_rrc_incumbent(
    protocol: dict[str, Any], tasks: list[dict[str, Any]], run_root: Path
) -> None:
    backend = protocol["candidate_training"]["rrc_backend_protocol"]
    require_canonical(
        backend,
        "strict_v4_rrc_csr_execution_protocol_v1",
        "RRC backend protocol",
    )
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for task in tasks:
        grouped.setdefault(
            (task["suite"], task["scenario"]), []
        ).append(task)
    for (suite, scenario), rows in sorted(grouped.items()):
        if len(rows) != 3:
            raise ValueError("RRC tournament requires three fresh seeds")
        seed_records = [
            seed_record_from_capture(
                task_root(run_root, task) / "incumbent_source_capture",
                suite=suite,
                scenario=scenario,
                training_seed=int(task["training_seed"]),
            )
            for task in rows
        ]
        certificate = certify_seed_records(
            seed_records,
            protocol_manifest_sha256=backend["manifest_sha256"],
            suite=suite,
            scenario=scenario,
            expected_training_seeds=sorted(
                int(task["training_seed"]) for task in rows
            ),
        )
        certificate_path = (
            run_root / "rrc_certificates" / suite / f"{scenario}.json"
        )
        if certificate_path.is_file():
            if load(certificate_path) != certificate:
                raise ValueError("existing RRC certificate is immutable")
        else:
            write_json(certificate_path, certificate)
        for task in rows:
            block = task_root(run_root, task)
            output = block / "incumbent_capture"
            manifest_path = output / "capture_manifest.json"
            if manifest_path.is_file():
                value = load(manifest_path)
                require_canonical(
                    value,
                    "strict_v4_rrc_csr_runtime_capture_v1",
                    "RRC incumbent capture",
                )
                if (
                    value.get("scenario_certificate_manifest_sha256")
                    != certificate["manifest_sha256"]
                ):
                    raise ValueError("RRC incumbent certificate drift")
                continue
            if output.exists() and any(output.iterdir()):
                raise ValueError(
                    f"partial RRC incumbent requires quarantine: {output}"
                )
            materialize(
                backend,
                certificate,
                block / "incumbent_source_capture",
                output,
                suite=suite,
                scenario=scenario,
                training_seed=int(task["training_seed"]),
                corruption_seed=int(task["corruption_seed"]),
            )


def verify_implementation(
    protocol: dict[str, Any], project_root: Path
) -> None:
    require_canonical(protocol, PROTOCOL_SCHEMA, "tournament protocol")
    if protocol.get("execution_admitted") is not True:
        raise ValueError("admitted tournament protocol required")
    for relative, expected in protocol["implementation_sha256"].items():
        path = project_root / relative
        if not path.is_file() or file_hash(path) != expected:
            raise ValueError(f"tournament implementation drifted: {relative}")


def write_completion(
    protocol: dict[str, Any], result_root: Path
) -> dict[str, Any]:
    summary_path = result_root / "summary.json"
    audit_path = result_root / "audit.json"
    summary = load(summary_path)
    audit = load(audit_path)
    require_canonical(
        summary,
        "strict_v4_self_algorithm_direct_tournament_summary_v1",
        "tournament summary",
    )
    require_canonical(
        audit,
        "strict_v4_self_algorithm_direct_tournament_audit_v1",
        "tournament audit",
    )
    if (
        audit.get("integrity", {}).get("passes") is not True
        or audit.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or audit.get("summary_manifest_sha256")
        != summary["manifest_sha256"]
    ):
        raise ValueError("passing independent tournament audit required")
    selected = audit["decision"]["selected_algorithm"]
    completion: dict[str, Any] = {
        "schema_version": COMPLETION_SCHEMA,
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "protocol_file_sha256": file_hash(result_root / "protocol.json"),
        "summary_manifest_sha256": summary["manifest_sha256"],
        "summary_file_sha256": file_hash(summary_path),
        "audit_manifest_sha256": audit["manifest_sha256"],
        "audit_file_sha256": file_hash(audit_path),
        "integrity_passes": True,
        "challenger_gate_passes": bool(
            audit["decision"]["challenger_gate_passes"]
        ),
        "selected_algorithm": selected,
    }
    completion["manifest_sha256"] = canonical_hash(completion)
    output = result_root / "execution_complete.json"
    if output.is_file() and load(output) != completion:
        raise ValueError("existing tournament completion is immutable")
    if not output.is_file():
        write_json(output, completion)
    return completion


def run_confirmation(
    *,
    protocol: dict[str, Any],
    protocol_path: Path,
    project_root: Path,
    run_root: Path,
    result_root: Path,
    python: str,
    workers: int,
) -> dict[str, Any]:
    verify_implementation(protocol, project_root)
    maximum = int(protocol["resource_contract"]["outer_workers"])
    if workers < 1 or workers > maximum:
        raise ValueError("workers exceed frozen tournament contract")
    tasks = list(protocol["confirmation_universe"]["tasks"])
    for task in tasks:
        verify_source(task)

    def capture(index: int, task: dict[str, Any]) -> str:
        capture_challenger(
            protocol, task, project_root, run_root, python
        )
        capture_incumbent_source(
            protocol, task, project_root, run_root, python
        )
        return f"captured {index}/{len(tasks)} {task['identity']}"

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(capture, index, task): index
            for index, task in enumerate(tasks, start=1)
        }
        for future in as_completed(futures):
            print(future.result(), flush=True)
    if protocol["incumbent_algorithm"] == "rrc_csr_caeos_v1":
        materialize_rrc_incumbent(protocol, tasks, run_root)

    def evaluate(index: int, task: dict[str, Any]) -> str:
        output = (
            result_root
            / "task_records"
            / task["suite"]
            / task["scenario"]
            / f"seed{int(task['training_seed'])}"
            / "evaluation.json"
        )
        if not output.is_file():
            run_logged(
                [
                    python,
                    str(
                        project_root
                        / "evaluate_strict_v4_self_algorithm_direct_"
                        "tournament_confirmation.py"
                    ),
                    "--project-root",
                    str(project_root),
                    "--protocol",
                    str(protocol_path),
                    "--suite",
                    task["suite"],
                    "--scenario",
                    task["scenario"],
                    "--seed",
                    str(task["training_seed"]),
                    "--run-root",
                    str(run_root),
                    "--output",
                    str(output),
                ],
                output.with_suffix(".log"),
                project_root,
            )
        value = load(output)
        require_canonical(
            value,
            "strict_v4_self_algorithm_direct_tournament_task_evaluation_v1",
            "tournament task evaluation",
        )
        return f"evaluated {index}/{len(tasks)} {task['identity']}"

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(evaluate, index, task): index
            for index, task in enumerate(tasks, start=1)
        }
        for future in as_completed(futures):
            print(future.result(), flush=True)
    for executable, output_name in (
        (
            "summarize_strict_v4_self_algorithm_direct_tournament_"
            "confirmation.py",
            "summary.log",
        ),
        (
            "audit_strict_v4_self_algorithm_direct_tournament_"
            "confirmation.py",
            "audit.log",
        ),
    ):
        run_logged(
            [
                python,
                str(project_root / executable),
                "--project-root",
                str(project_root),
                "--protocol",
                str(protocol_path),
                "--result-root",
                str(result_root),
            ],
            result_root / output_name,
            project_root,
        )
    return write_completion(protocol, result_root)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path(
            "results/strict_v4_self_algorithm_direct_tournament_v1/"
            "protocol.json"
        ),
    )
    parser.add_argument(
        "--run-root",
        type=Path,
        default=Path(
            "runs/strict_v4_self_algorithm_direct_tournament_v1"
        ),
    )
    parser.add_argument(
        "--result-root",
        type=Path,
        default=Path(
            "results/strict_v4_self_algorithm_direct_tournament_v1"
        ),
    )
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    protocol_path = resolve(args.protocol)
    completion = run_confirmation(
        protocol=load(protocol_path),
        protocol_path=protocol_path,
        project_root=root,
        run_root=resolve(args.run_root),
        result_root=resolve(args.result_root),
        python=args.python,
        workers=args.workers,
    )
    print(json.dumps(completion, sort_keys=True))


if __name__ == "__main__":
    main()
