from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Dict, Iterable, List

from capture_pairwise_runtime import file_hash
from certify_rrc_csr_scenario import (
    certify_seed_records,
    seed_record_from_capture,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_rrc_csr_runtime import evaluate
from materialize_rrc_csr_runtime import materialize


CONDITIONS = (
    "clean",
    "modality_missing",
    "field_missing",
    "row_missing",
    "feature_shuffle",
    "gaussian_drift",
)


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def write_canonical(path: Path, value: Dict[str, Any]) -> None:
    value["manifest_sha256"] = canonical_hash(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def require_empty_or_absent(path: Path, label: str) -> None:
    if path.exists() and any(path.iterdir()):
        raise ValueError(f"partial {label} requires quarantine: {path}")


def validate_protocol(protocol: Dict[str, Any]) -> None:
    tasks = protocol.get("tasks", [])
    identities = {
        (
            task.get("suite"),
            task.get("scenario"),
            int(task.get("training_seed", -1)),
            int(task.get("corruption_seed", -1)),
        )
        for task in tasks
    }
    scenarios = {
        (task.get("suite"), task.get("scenario")) for task in tasks
    }
    if (
        protocol.get("schema_version")
        != "strict_v4_rrc_csr_execution_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("execution_admitted") is not True
        or protocol.get("algorithm") != "rrc_csr_caeos_v1"
        or tuple(protocol.get("conditions", [])) != CONDITIONS
        or len(tasks) != 249
        or len(identities) != 249
        or len(scenarios) != 83
        or sorted(protocol.get("training_seeds", [])) != [701, 709, 719]
        or sorted(protocol.get("corruption_seeds", [])) != [727, 733, 739]
    ):
        raise ValueError("invalid admitted RRC execution protocol")
    for suite, scenario in scenarios:
        rows = [
            task
            for task in tasks
            if task["suite"] == suite and task["scenario"] == scenario
        ]
        if (
            sorted(int(row["training_seed"]) for row in rows)
            != [701, 709, 719]
            or len({int(row["corruption_seed"]) for row in rows}) != 3
        ):
            raise ValueError("each RRC scenario requires three frozen seeds")


def validate_implementation(
    protocol: Dict[str, Any], project_root: Path
) -> None:
    required = {
        "source_capture",
        "clean_trainer",
        "robust_trainer",
        "scenario_certifier",
        "materializer",
        "evaluator",
        "capture_pipeline",
    }
    implementation = protocol.get("implementation", {})
    hashes = protocol.get("implementation_sha256", {})
    if not required <= set(implementation) or set(implementation) != set(hashes):
        raise ValueError("RRC execution implementation registry is incomplete")
    for name, relative in implementation.items():
        path = project_root / relative
        if not path.is_file() or file_hash(path) != hashes[name]:
            raise ValueError(f"RRC implementation SHA mismatch: {name}")


def validate_source(source: Dict[str, Any], task: Dict[str, Any]) -> None:
    provenance = Path(source["candidate_source_root"]) / "provenance.json"
    if (
        source.get("suite") != task["suite"]
        or source.get("scenario") != task["scenario"]
        or source.get("csv_sha256") != task["source_csv_sha256"]
        or source.get("config_sha256") != task["source_config_sha256"]
        or file_hash(provenance)
        != source["candidate_source_provenance_sha256"]
        or file_hash(Path(source["csv"])) != source["csv_sha256"]
        or file_hash(Path(source["config"])) != source["config_sha256"]
    ):
        raise ValueError(
            f"RRC source identity drift: {task['suite']}/{task['scenario']}"
        )


def validate_capture_execution(
    path: Path, manifest_path: Path, task: Dict[str, Any]
) -> bool:
    if not path.exists():
        return False
    value = load_json(path)
    if (
        value.get("schema_version")
        != "strict_v4_rrc_csr_base_capture_execution_v1"
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("state") != "complete"
        or value.get("task")
        != {"suite": task["suite"], "scenario": task["scenario"]}
        or int(value.get("training_seed", -1))
        != int(task["training_seed"])
        or value.get("capture_manifest_file_sha256")
        != file_hash(manifest_path)
        or float(value.get("total_capture_wall_seconds", -1.0)) <= 0.0
    ):
        raise ValueError(f"invalid RRC base capture timing: {path}")
    return True


def validate_certificate(
    path: Path,
    protocol: Dict[str, Any],
    suite: str,
    scenario: str,
) -> bool:
    if not path.exists():
        return False
    value = load_json(path)
    if (
        value.get("schema_version")
        != "strict_v4_rrc_csr_scenario_certificate_v1"
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or value.get("suite") != suite
        or value.get("scenario") != scenario
        or sorted(value.get("training_seeds", [])) != [701, 709, 719]
        or value.get("unknown_or_test_labels_used") is not False
        or value.get("test_arrays_read") is not False
        or value.get("test_effect_metrics_read") is not False
    ):
        raise ValueError(f"invalid RRC scenario certificate: {path}")
    return True


def validate_rrc_capture(
    path: Path, protocol: Dict[str, Any], task: Dict[str, Any]
) -> bool:
    if not path.exists():
        return False
    value = load_json(path)
    root = path.parent
    if (
        value.get("schema_version")
        != "strict_v4_rrc_csr_runtime_capture_v1"
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or value.get("task")
        != {"suite": task["suite"], "scenario": task["scenario"]}
        or int(value.get("training_seed", -1))
        != int(task["training_seed"])
        or int(value.get("corruption_seed", -1))
        != int(task["corruption_seed"])
        or value.get("roundtrip", {}).get("passes") is not True
        or file_hash(root / value["runtime_artifact"])
        != value["runtime_artifact_sha256"]
        or file_hash(root / value["evaluation_inputs"])
        != value["evaluation_inputs_sha256"]
    ):
        raise ValueError(f"invalid existing RRC runtime capture: {path}")
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
        != "strict_v4_rrc_csr_evaluation_v1"
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
        raise ValueError(f"invalid existing RRC evaluation: {path}")
    return True


def run_command(
    command: List[str], log_path: Path, resource_prefix: List[str]
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        subprocess.run(
            [*resource_prefix, *command],
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )


def group_tasks(
    tasks: Iterable[Dict[str, Any]]
) -> List[List[Dict[str, Any]]]:
    groups: Dict[tuple[str, str], List[Dict[str, Any]]] = {}
    for task in tasks:
        groups.setdefault(
            (task["suite"], task["scenario"]), []
        ).append(task)
    return [
        sorted(rows, key=lambda row: int(row["training_seed"]))
        for _, rows in sorted(groups.items())
    ]


def run(
    protocol: Dict[str, Any],
    protocol_path: Path,
    project_root: Path,
    run_root: Path,
    result_root: Path,
    workers: int,
) -> Dict[str, Any]:
    validate_protocol(protocol)
    validate_implementation(protocol, project_root)
    resource = protocol["resource_contract"]
    if int(workers) < 1 or int(workers) > int(resource["outer_workers"]):
        raise ValueError("RRC workers violate frozen resource contract")
    resource_prefix = list(resource["subprocess_resource_prefix"])
    sources = {
        (row["suite"], row["scenario"]): row
        for row in protocol["source_registry"]
    }
    if len(sources) != 83:
        raise ValueError("RRC source registry must contain 83 scenarios")

    def execute_scenario(
        scenario_index: int, tasks: List[Dict[str, Any]]
    ) -> str:
        suite = tasks[0]["suite"]
        scenario = tasks[0]["scenario"]
        seed_records = []
        for task in tasks:
            source = sources[(suite, scenario)]
            validate_source(source, task)
            capture_dir = (
                run_root
                / "base_csr_captures"
                / suite
                / scenario
                / f"seed{int(task['training_seed'])}"
            )
            manifest_path = capture_dir / "capture_manifest.json"
            execution_path = capture_dir / "capture_execution.json"
            if not manifest_path.exists():
                require_empty_or_absent(capture_dir, "RRC base CSR capture")
                command = [
                    sys.executable,
                    str(
                        project_root
                        / protocol["implementation"]["source_capture"]
                    ),
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
                    str(capture_dir),
                    "--suite",
                    suite,
                    "--scenario",
                    scenario,
                    "--weight",
                    str(protocol["fixed_augmentation_weight"]),
                    "--sample-fraction",
                    str(protocol["training_sample_fraction"]),
                    "--training-seed",
                    str(task["training_seed"]),
                    "--augmentation-seed",
                    str(task["training_seed"]),
                    "--health-quantile",
                    str(protocol["health_quantile"]),
                    "--validation-corruption-seed",
                    str(task["corruption_seed"]),
                    "--",
                    *source["base_trainer_arguments"],
                ]
                started = time.perf_counter()
                run_command(
                    command, capture_dir / "capture.log", resource_prefix
                )
                elapsed = time.perf_counter() - started
                seed_record_from_capture(
                    capture_dir,
                    suite=suite,
                    scenario=scenario,
                    training_seed=int(task["training_seed"]),
                )
                write_canonical(
                    execution_path,
                    {
                        "schema_version": (
                            "strict_v4_rrc_csr_base_capture_execution_v1"
                        ),
                        "state": "complete",
                        "task": {"suite": suite, "scenario": scenario},
                        "training_seed": int(task["training_seed"]),
                        "capture_manifest_file_sha256": file_hash(
                            manifest_path
                        ),
                        "total_capture_wall_seconds": float(elapsed),
                        "timer": "time.perf_counter",
                        "resource_prefix": resource_prefix,
                        "unknown_or_test_labels_used_for_cost_selection": False,
                    },
                )
            seed_records.append(
                seed_record_from_capture(
                    capture_dir,
                    suite=suite,
                    scenario=scenario,
                    training_seed=int(task["training_seed"]),
                )
            )
            if not validate_capture_execution(
                execution_path, manifest_path, task
            ):
                raise ValueError(f"missing RRC capture timing: {execution_path}")

        certificate_path = (
            run_root
            / "scenario_certificates"
            / suite
            / scenario
            / "certificate.json"
        )
        if not validate_certificate(
            certificate_path, protocol, suite, scenario
        ):
            if certificate_path.parent.exists():
                require_empty_or_absent(
                    certificate_path.parent, "RRC scenario certificate"
                )
            certificate = certify_seed_records(
                seed_records,
                protocol_manifest_sha256=protocol["manifest_sha256"],
                suite=suite,
                scenario=scenario,
                expected_training_seeds=protocol["training_seeds"],
            )
            certificate_path.parent.mkdir(parents=True, exist_ok=True)
            certificate_path.write_text(
                json.dumps(certificate, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            validate_certificate(
                certificate_path, protocol, suite, scenario
            )
        certificate = load_json(certificate_path)

        for task in tasks:
            base_dir = (
                run_root
                / "base_csr_captures"
                / suite
                / scenario
                / f"seed{int(task['training_seed'])}"
            )
            rrc_dir = (
                run_root
                / "rrc_runtime_captures"
                / suite
                / scenario
                / f"seed{int(task['training_seed'])}"
            )
            rrc_manifest = rrc_dir / "capture_manifest.json"
            if not validate_rrc_capture(rrc_manifest, protocol, task):
                require_empty_or_absent(rrc_dir, "RRC runtime capture")
                materialize(
                    protocol,
                    certificate,
                    base_dir,
                    rrc_dir,
                    suite=suite,
                    scenario=scenario,
                    training_seed=int(task["training_seed"]),
                    corruption_seed=int(task["corruption_seed"]),
                )
                validate_rrc_capture(rrc_manifest, protocol, task)
            for condition in CONDITIONS:
                output = (
                    run_root
                    / "evaluations"
                    / suite
                    / scenario
                    / f"seed{int(task['training_seed'])}"
                    / condition
                    / "evaluation.json"
                )
                if validate_evaluation(
                    output, protocol, task, condition
                ):
                    continue
                if output.parent.exists():
                    require_empty_or_absent(
                        output.parent, "RRC evaluation"
                    )
                evaluate(
                    protocol,
                    rrc_dir,
                    suite=suite,
                    scenario=scenario,
                    training_seed=int(task["training_seed"]),
                    corruption_seed=int(task["corruption_seed"]),
                    condition=condition,
                    output=output,
                )
                validate_evaluation(output, protocol, task, condition)
        return f"completed {scenario_index}/83 {suite}/{scenario}"

    groups = group_tasks(protocol["tasks"])
    with ThreadPoolExecutor(max_workers=int(workers)) as executor:
        futures = {
            executor.submit(execute_scenario, index, tasks): index
            for index, tasks in enumerate(groups, start=1)
        }
        for future in as_completed(futures):
            print(future.result(), flush=True)

    captures = sorted(
        (run_root / "base_csr_captures").rglob("capture_manifest.json")
    )
    certificates = sorted(
        (run_root / "scenario_certificates").rglob("certificate.json")
    )
    runtimes = sorted(
        (run_root / "rrc_runtime_captures").rglob("capture_manifest.json")
    )
    evaluations = sorted(
        (run_root / "evaluations").rglob("evaluation.json")
    )
    if (
        len(captures) != 249
        or len(certificates) != 83
        or len(runtimes) != 249
        or len(evaluations) != 1494
    ):
        raise RuntimeError("RRC capture pipeline inventory is incomplete")
    inventory = {
        "schema_version": "strict_v4_rrc_csr_capture_pipeline_inventory_v1",
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "counts": {
            "base_csr_captures": len(captures),
            "scenario_certificates": len(certificates),
            "rrc_runtime_captures": len(runtimes),
            "evaluations": len(evaluations),
        },
        "inventories": {
            "base_csr_captures": [
                {
                    "path": path.relative_to(run_root).as_posix(),
                    "file_sha256": file_hash(path),
                }
                for path in captures
            ],
            "scenario_certificates": [
                {
                    "path": path.relative_to(run_root).as_posix(),
                    "file_sha256": file_hash(path),
                    "manifest_sha256": load_json(path)["manifest_sha256"],
                }
                for path in certificates
            ],
            "rrc_runtime_captures": [
                {
                    "path": path.relative_to(run_root).as_posix(),
                    "file_sha256": file_hash(path),
                    "manifest_sha256": load_json(path)["manifest_sha256"],
                }
                for path in runtimes
            ],
            "evaluations": [
                {
                    "path": path.relative_to(run_root).as_posix(),
                    "file_sha256": file_hash(path),
                    "manifest_sha256": load_json(path)["manifest_sha256"],
                }
                for path in evaluations
            ],
        },
        "unknown_or_test_labels_used_for_certificate_or_selection": False,
    }
    output = result_root / "capture_pipeline_inventory.json"
    write_canonical(output, inventory)
    return inventory


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
        else int(protocol["resource_contract"]["outer_workers"])
    )
    value = run(
        protocol,
        protocol_path,
        args.project_root.resolve(),
        args.run_root.resolve(),
        args.result_root.resolve(),
        workers,
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
