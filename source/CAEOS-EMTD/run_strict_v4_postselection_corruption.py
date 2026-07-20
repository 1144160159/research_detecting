from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


@dataclass(frozen=True)
class Task:
    tier: str
    suite: str
    scenario: str
    corruption: str
    modality: int
    severity: float


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selected_modality(
    coverage_sha: str, suite: str, scenario: str, corruption: str
) -> int:
    raw = f"{coverage_sha}:{suite}:{scenario}:{corruption}".encode("utf-8")
    return int(hashlib.sha256(raw).hexdigest()[:16], 16) % 3


def build_tasks(protocol: dict[str, Any], coverage: dict[str, Any]) -> list[Task]:
    if protocol.get("schema_version") != "strict_v4_postselection_corruption_protocol_v1":
        raise ValueError("unexpected corruption protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("corruption protocol SHA mismatch")
    if protocol.get("status") != "frozen_post_selection_before_corruption_results":
        raise ValueError("corruption protocol is not frozen")
    if protocol.get("coverage_manifest_sha256") != coverage.get("manifest_sha256"):
        raise ValueError("corruption protocol coverage binding mismatch")
    registry = coverage.get("scenario_registry", {})
    tasks = []
    screen = protocol["sentinel_severity_screen"]
    families = protocol["corruption_definitions"]["families"]
    for suite, scenario in sorted(screen["sentinel_scenarios"].items()):
        for corruption, severities in families.items():
            for modality in range(3):
                for severity in severities:
                    tasks.append(
                        Task(
                            "sentinel",
                            suite,
                            scenario,
                            corruption,
                            modality,
                            float(severity),
                        )
                    )
    confirmation = protocol["full102_confirmation"]
    coverage_sha = protocol["coverage_manifest_sha256"]
    for suite in sorted(registry):
        for scenario in registry[suite]["scenarios"]:
            for corruption in confirmation["corruption_families"]:
                tasks.append(
                    Task(
                        "full102",
                        suite,
                        scenario,
                        corruption,
                        selected_modality(
                            coverage_sha, suite, scenario, corruption
                        ),
                        float(confirmation["fixed_severity"][corruption]),
                    )
                )
    if len(tasks) != protocol.get("total_expected_corruption_runs"):
        raise ValueError("corruption task count does not match protocol")
    if len({task_key(task) for task in tasks}) != len(tasks):
        raise ValueError("corruption task plan contains duplicates")
    return tasks


def _slug(value: float) -> str:
    return f"{value:.12g}".replace(".", "p")


def task_key(task: Task) -> str:
    return (
        f"{task.tier}/{task.suite}/{task.scenario}/"
        f"{task.corruption}_m{task.modality}_s{_slug(task.severity)}"
    )


def cache_arguments(suite: str, cache_root: Path) -> list[str]:
    options = {
        "edge_iiot": ("--edge-iiot-cache-dir", "--edge-iiot-max-per-class", 1000),
        "nf_cse": ("--nf-cse-cache-dir", "--nf-cse-max-per-class", 1000),
        "ustc_tfc2016": ("--ustc-cache-dir", "--ustc-max-per-class", 3000),
        "nf_unsw": ("--nf-unsw-cache-dir", "--nf-unsw-max-per-class", 5000),
        "cicids2017": (
            "--cicids2017-cache-dir",
            "--cicids2017-max-per-class",
            5000,
        ),
        "cic_ton_iot": (
            "--cic-ton-iot-cache-dir",
            "--cic-ton-iot-max-per-class",
            1000,
        ),
        "cic_iot2023": (
            "--cic-iot2023-cache-dir",
            "--cic-iot2023-max-per-class",
            1000,
        ),
    }
    if suite not in options:
        raise ValueError(f"unsupported corruption suite: {suite}")
    cache_option, maximum_option, maximum = options[suite]
    return [cache_option, str(cache_root / suite), maximum_option, str(maximum)]


def command_for(
    task: Task,
    output_root: Path,
    cache_root: Path,
    candidate: dict[str, Any],
) -> list[str]:
    output = output_root / task_key(task)
    return [
        sys.executable,
        "run_nested_gate_matrix.py",
        "--suite",
        task.suite,
        "--scenarios",
        task.scenario,
        "--seeds",
        "7",
        "--workers",
        "1",
        "--model-jobs",
        "8",
        "--estimators",
        "80",
        "--risk-selection",
        "nested_boundary_pairwise_pseudo_unknown_blend",
        "--pseudo-unknown-max-alpha",
        str(candidate["maximum_alpha"]),
        "--pseudo-unknown-min-fold-gain",
        str(candidate["minimum_fold_gain"]),
        "--boundary-hard-pseudo-fraction",
        str(candidate["hard_pseudo_fraction"]),
        "--boundary-interpolation",
        str(candidate["interpolation"]),
        "--boundary-max-per-task",
        str(candidate["max_per_task"]),
        "--boundary-training-objective",
        str(candidate["training_objective"]),
        "--risk-policy-name",
        "strict_v4_postselection_corruption_pairwise_v1",
        "--test-corruption-kind",
        task.corruption,
        "--test-corruption-modality",
        str(task.modality),
        "--test-corruption-severity",
        str(task.severity),
        "--test-corruption-seed",
        "211",
        "--output-root",
        str(output),
        *cache_arguments(task.suite, cache_root),
    ]


def validate_run(
    task: Task,
    task_root: Path,
    clean_root: Path,
) -> dict[str, Any]:
    run = task_root / task.suite / f"{task.scenario}_seed7"
    metrics_path = run / "metrics.json"
    provenance_path = run / "provenance.json"
    clean_metrics_path = clean_root / task.suite / f"{task.scenario}_seed7" / "metrics.json"
    for path in (metrics_path, provenance_path, clean_metrics_path):
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"missing corruption validation artifact: {path}")
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    clean = json.loads(clean_metrics_path.read_text(encoding="utf-8"))
    arguments = metrics.get("arguments", {})
    expected = {
        "test_corruption_kind": task.corruption,
        "test_corruption_modality": task.modality,
        "test_corruption_severity": task.severity,
        "test_corruption_seed": 211,
        "risk_selection": "nested_boundary_pairwise_pseudo_unknown_blend",
    }
    for key, value in expected.items():
        if arguments.get(key) != value:
            raise ValueError(f"corruption argument mismatch for {key} under {run}")
    fingerprint = metrics["split_metadata"]["split_fingerprint"]["combined"]
    clean_fingerprint = clean["split_metadata"]["split_fingerprint"]["combined"]
    if fingerprint != clean_fingerprint:
        raise ValueError(f"corruption split fingerprint mismatch under {run}")
    learned = metrics.get("risk_selection_details", {}).get(
        "pseudo_unknown_learned_blend", {}
    )
    if learned.get("unknown_or_test_labels_used") is not False:
        raise ValueError(f"corruption no-leak declaration failed under {run}")
    record = {
        "schema_version": "strict_v4_postselection_corruption_run_v1",
        "task": asdict(task),
        "metrics_path": metrics_path.as_posix(),
        "metrics_sha256": file_hash(metrics_path),
        "provenance_sha256": file_hash(provenance_path),
        "clean_metrics_sha256": file_hash(clean_metrics_path),
        "split_fingerprint": fingerprint,
        "validation_passes": True,
        "unknown_or_test_labels_used_for_generation_fitting_or_selection": False,
    }
    record["record_sha256"] = canonical_hash(record)
    wrapper = task_root / "corruption_metrics.json"
    wrapper.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--pairwise-candidate", type=Path, required=True)
    parser.add_argument("--clean-root", type=Path, required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    manifest = json.loads(args.pairwise_candidate.read_text(encoding="utf-8"))
    if file_hash(Path(__file__)) != protocol["implementation_sha256"]["matrix_runner"]:
        raise ValueError("corruption runner implementation SHA mismatch")
    if file_hash(args.pairwise_candidate) != protocol["input_file_sha256"][
        "pairwise_candidate_manifest"
    ]:
        raise ValueError("pairwise candidate manifest file SHA mismatch")
    candidate = manifest.get("candidate", {})
    tasks = build_tasks(protocol, coverage)
    args.output_root.mkdir(parents=True, exist_ok=True)
    completed = 0
    for index, task in enumerate(tasks, start=1):
        task_root = args.output_root / task_key(task)
        wrapper = task_root / "corruption_metrics.json"
        if wrapper.is_file():
            record = json.loads(wrapper.read_text(encoding="utf-8"))
            if record.get("record_sha256") != canonical_hash(record):
                raise ValueError(f"corruption wrapper SHA mismatch: {wrapper}")
            completed += 1
            continue
        task_root.mkdir(parents=True, exist_ok=True)
        command = command_for(task, args.output_root, args.cache_root, candidate)
        with (task_root / "launcher.log").open("w", encoding="utf-8") as log:
            result = subprocess.run(
                command,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
        if result.returncode != 0:
            (task_root / "failure.json").write_text(
                json.dumps(
                    {"task": asdict(task), "return_code": result.returncode},
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            raise RuntimeError(f"corruption task failed: {task_key(task)}")
        validate_run(task, task_root, args.clean_root)
        completed += 1
        print(f"completed={completed}/{len(tasks)} task={task_key(task)}", flush=True)
    if completed != protocol["total_expected_corruption_runs"]:
        raise RuntimeError("corruption matrix finished with incomplete coverage")


if __name__ == "__main__":
    main()
