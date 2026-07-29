from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
    materialize_attack_family_cache,
)


REQUIRED_PAIRWISE = ("metrics.json", "scores.npz", "evidence_package.npz")
REQUIRED_XGBOOST = ("metrics.json", "scores.npz", "provenance.json")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def verify_protocol(project_root: Path, protocol_path: Path) -> dict[str, Any]:
    protocol = load_canonical(protocol_path, "attack-family protocol")
    if protocol.get("state") not in {
        "frozen_zero_result_development",
        "frozen_zero_result_confirmation",
    }:
        raise ValueError("protocol is not executable")
    for name, expected in protocol["implementation_sha256"].items():
        if file_hash(project_root / name) != expected:
            raise ValueError(f"implementation hash drifted: {name}")
    source = protocol["source"]
    if file_hash(Path(source["csv"])) != source["csv_sha256"]:
        raise ValueError("source CSV hash drifted")
    if file_hash(Path(source["config"])) != source["config_sha256"]:
        raise ValueError("config hash drifted")
    return protocol


def artifact_hashes(directory: Path, names: tuple[str, ...]) -> dict[str, str]:
    paths = {name: directory / name for name in names}
    if not all(path.is_file() for path in paths.values()):
        missing = [name for name, path in paths.items() if not path.is_file()]
        raise FileNotFoundError(f"missing artifacts in {directory}: {missing}")
    return {name: file_hash(path) for name, path in paths.items()}


def read_cpu_times() -> tuple[int, int]:
    fields = Path("/proc/stat").read_text(encoding="ascii").splitlines()[0].split()
    values = [int(value) for value in fields[1:]]
    idle = values[3] + (values[4] if len(values) > 4 else 0)
    return sum(values), idle


def read_memory() -> dict[str, int]:
    values: dict[str, int] = {}
    for line in Path("/proc/meminfo").read_text(encoding="ascii").splitlines():
        key, raw = line.split(":", 1)
        values[key] = int(raw.strip().split()[0])
    return {
        "total_kib": values["MemTotal"],
        "available_kib": values["MemAvailable"],
    }


class ResourceSampler:
    def __init__(self, path: Path, interval_seconds: float = 5.0) -> None:
        self.path = path
        self.interval_seconds = interval_seconds
        self.samples: list[dict[str, Any]] = []
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> dict[str, Any]:
        self._stop.set()
        self._thread.join(timeout=self.interval_seconds * 2)
        busy_values = [
            float(sample["cpu_busy_fraction"])
            for sample in self.samples
            if sample.get("cpu_busy_fraction") is not None
        ]
        report: dict[str, Any] = {
            "schema_version": "strict_v4_attack_family_resource_samples_v1",
            "state": "complete",
            "sample_count": len(self.samples),
            "samples": self.samples,
            "cpu_busy_fraction": {
                "minimum": min(busy_values) if busy_values else None,
                "maximum": max(busy_values) if busy_values else None,
                "mean": (
                    sum(busy_values) / len(busy_values) if busy_values else None
                ),
                "at_least_50_fraction": (
                    sum(value >= 0.5 for value in busy_values) / len(busy_values)
                    if busy_values
                    else None
                ),
                "at_least_80_fraction": (
                    sum(value >= 0.8 for value in busy_values) / len(busy_values)
                    if busy_values
                    else None
                ),
            },
        }
        report["manifest_sha256"] = canonical_hash(report)
        atomic_json(self.path, report)
        return report

    def _run(self) -> None:
        previous_total, previous_idle = read_cpu_times()
        while not self._stop.wait(self.interval_seconds):
            total, idle = read_cpu_times()
            delta_total = total - previous_total
            delta_idle = idle - previous_idle
            busy = (
                1.0 - (delta_idle / delta_total) if delta_total > 0 else None
            )
            memory = read_memory()
            self.samples.append(
                {
                    "sampled_at_utc": utc_now(),
                    "cpu_busy_fraction": busy,
                    "memory_used_fraction": (
                        1.0
                        - memory["available_kib"] / memory["total_kib"]
                    ),
                }
            )
            previous_total, previous_idle = total, idle


def pairwise_command(
    *,
    python: Path,
    project_root: Path,
    protocol: dict[str, Any],
    cache_path: Path,
    unknown_family: str,
    seed: int,
    output_dir: Path,
) -> list[str]:
    parameters = protocol["pairwise_caeos"]
    values = [
        str(python),
        str(project_root / "train_hybrid_open_set.py"),
        "--csv",
        str(cache_path),
        "--config",
        protocol["source"]["config"],
        "--unknown-classes",
        unknown_family,
        "--benign-class",
        protocol["benign_family"],
        "--max-per-class",
        str(protocol["cache_policy"]["maximum_per_family"]),
        "--estimators",
        str(parameters["estimators"]),
        "--jobs",
        str(parameters["jobs_per_task"]),
        "--split-strategy",
        parameters["split_strategy"],
        "--risk-selection",
        parameters["risk_selection"],
        "--risk-policy-name",
        parameters["risk_policy_name"],
        "--modality-gate-minimum-gain",
        str(parameters["modality_gate_minimum_gain"]),
        "--conflict-fallback-minimum-gain",
        str(parameters["conflict_fallback_minimum_gain"]),
        "--joint-fallback-minimum-gain",
        str(parameters["joint_fallback_minimum_gain"]),
        "--density-gate-minimum-gain",
        str(parameters["density_gate_minimum_gain"]),
        "--density-gate-minimum-known-classes",
        str(parameters["density_gate_minimum_known_classes"]),
        "--density-gate-blend-weight",
        str(parameters["density_gate_blend_weight"]),
        "--pseudo-unknown-max-alpha",
        str(parameters["pseudo_unknown_max_alpha"]),
        "--pseudo-unknown-min-fold-gain",
        str(parameters["pseudo_unknown_min_fold_gain"]),
        "--pseudo-unknown-local-rank-bins",
        str(parameters["pseudo_unknown_local_rank_bins"]),
        "--pseudo-unknown-local-rank-beta",
        str(parameters["pseudo_unknown_local_rank_beta"]),
        "--boundary-hard-pseudo-fraction",
        str(parameters["boundary_hard_pseudo_fraction"]),
        "--boundary-interpolation",
        str(parameters["boundary_interpolation"]),
        "--boundary-max-per-task",
        str(parameters["boundary_max_per_task"]),
        "--boundary-training-objective",
        parameters["boundary_training_objective"],
        "--structural-gate-minimum-gain",
        str(parameters["structural_gate_minimum_gain"]),
        "--seed",
        str(seed),
        "--output-dir",
        str(output_dir),
        "--test-corruption-kind",
        "none",
        "--test-corruption-modality",
        "0",
        "--test-corruption-severity",
        "0.0",
        "--test-corruption-seed",
        "20260717",
        "--train-label-noise",
        "0.0",
    ]
    return values


def xgboost_command(
    *,
    python: Path,
    project_root: Path,
    protocol: dict[str, Any],
    cache_path: Path,
    pairwise_dir: Path,
    output_dir: Path,
) -> list[str]:
    parameters = protocol["xgboost_known_expert"]
    return [
        str(python),
        str(project_root / "train_strict_v4_xgboost_warning_task.py"),
        "--pairwise-task-dir",
        str(pairwise_dir),
        "--cache-csv",
        str(cache_path),
        "--config",
        protocol["source"]["config"],
        "--output-dir",
        str(output_dir),
        "--xgboost-root",
        parameters["package_root"],
        "--validation-benign-fpr-budget",
        str(parameters["validation_benign_fpr_budget"]),
        "--estimators",
        str(parameters["estimators"]),
        "--max-depth",
        str(parameters["max_depth"]),
        "--learning-rate",
        str(parameters["learning_rate"]),
        "--subsample",
        str(parameters["subsample"]),
        "--colsample-bytree",
        str(parameters["colsample_bytree"]),
        "--early-stopping-rounds",
        str(parameters["early_stopping_rounds"]),
        "--jobs",
        str(parameters["jobs_per_task"]),
    ]


def run_command(command: list[str], cwd: Path, log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8", newline="\n") as log:
        log.write("$ " + " ".join(command) + "\n")
        log.flush()
        subprocess.run(
            command,
            cwd=cwd,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )


def run_task(
    *,
    python: Path,
    project_root: Path,
    protocol: dict[str, Any],
    cache_path: Path,
    scenario: str,
    unknown_family: str,
    seed: int,
) -> tuple[str, dict[str, Any]]:
    identity = f"{scenario}_seed{seed}"
    run_root = Path(protocol["paths"]["run_root"])
    pairwise_dir = run_root / "pairwise" / identity
    xgboost_dir = run_root / "xgboost" / identity
    pairwise_dir.mkdir(parents=True, exist_ok=True)
    xgboost_dir.mkdir(parents=True, exist_ok=True)
    state = "reused"
    try:
        pairwise_hashes = artifact_hashes(pairwise_dir, REQUIRED_PAIRWISE)
    except FileNotFoundError:
        run_command(
            pairwise_command(
                python=python,
                project_root=project_root,
                protocol=protocol,
                cache_path=cache_path,
                unknown_family=unknown_family,
                seed=seed,
                output_dir=pairwise_dir,
            ),
            project_root,
            pairwise_dir / "execution.log",
        )
        pairwise_hashes = artifact_hashes(pairwise_dir, REQUIRED_PAIRWISE)
        state = "trained"
    try:
        xgboost_hashes = artifact_hashes(xgboost_dir, REQUIRED_XGBOOST)
    except FileNotFoundError:
        run_command(
            xgboost_command(
                python=python,
                project_root=project_root,
                protocol=protocol,
                cache_path=cache_path,
                pairwise_dir=pairwise_dir,
                output_dir=xgboost_dir,
            ),
            project_root,
            xgboost_dir / "execution.log",
        )
        xgboost_hashes = artifact_hashes(xgboost_dir, REQUIRED_XGBOOST)
        state = "trained"
    return identity, {
        "state": state,
        "seed": seed,
        "scenario": scenario,
        "unknown_family": unknown_family,
        "cache_sha256": file_hash(cache_path),
        "pairwise_dir": str(pairwise_dir),
        "pairwise_sha256": pairwise_hashes,
        "xgboost_dir": str(xgboost_dir),
        "xgboost_sha256": xgboost_hashes,
    }


def progress_payload(
    protocol: dict[str, Any],
    *,
    states: dict[str, dict[str, Any]],
    failures: dict[str, str],
    started_at: str,
) -> dict[str, Any]:
    return {
        "schema_version": "strict_v4_attack_family_matrix_progress_v1",
        "state": "failed" if failures else "running",
        "updated_at_utc": utc_now(),
        "started_at_utc": started_at,
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "expected_task_count": protocol["expected_task_count"],
        "complete_task_count": len(states),
        "failure_count": len(failures),
        "task_states": dict(sorted(states.items())),
        "failures": dict(sorted(failures.items())),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    protocol_path = args.protocol.resolve()
    python = args.python.resolve()
    protocol = verify_protocol(project_root, protocol_path)
    result_root = Path(protocol["paths"]["result_root"])
    result_root.mkdir(parents=True, exist_ok=True)
    progress_path = result_root / "progress.json"
    completion_path = result_root / "completion.json"
    if completion_path.is_file():
        existing = load_canonical(completion_path, "matrix completion")
        if existing.get("protocol_manifest_sha256") == protocol["manifest_sha256"]:
            print(json.dumps(existing, ensure_ascii=False, sort_keys=True))
            return
        raise ValueError("existing completion belongs to another protocol")
    sampler = ResourceSampler(result_root / "resource_samples.json")
    sampler.start()
    started_at = utc_now()
    cache_reports: dict[str, Any] = {}
    states: dict[str, dict[str, Any]] = {}
    failures: dict[str, str] = {}
    try:
        for seed in protocol["seeds"]:
            cache_path = (
                Path(protocol["paths"]["cache_root"])
                / f"seed{seed}_max{protocol['cache_policy']['maximum_per_family']}.csv"
            )
            cache_reports[str(seed)] = materialize_attack_family_cache(
                source_path=Path(protocol["source"]["csv"]),
                config_path=Path(protocol["source"]["config"]),
                output_path=cache_path,
                seed=int(seed),
                maximum_per_family=int(
                    protocol["cache_policy"]["maximum_per_family"]
                ),
                chunksize=int(protocol["cache_policy"]["chunksize"]),
            )
        tasks = [
            (int(seed), scenario, unknown_family)
            for seed in protocol["seeds"]
            for scenario, unknown_family in protocol["scenarios"].items()
        ]
        with ThreadPoolExecutor(
            max_workers=int(protocol["resource_contract"]["outer_workers"])
        ) as executor:
            futures = {}
            for seed, scenario, unknown_family in tasks:
                cache_path = (
                    Path(protocol["paths"]["cache_root"])
                    / (
                        f"seed{seed}_max"
                        f"{protocol['cache_policy']['maximum_per_family']}.csv"
                    )
                )
                future = executor.submit(
                    run_task,
                    python=python,
                    project_root=project_root,
                    protocol=protocol,
                    cache_path=cache_path,
                    scenario=scenario,
                    unknown_family=unknown_family,
                    seed=seed,
                )
                futures[future] = f"{scenario}_seed{seed}"
            for future in as_completed(futures):
                identity = futures[future]
                try:
                    returned_identity, report = future.result()
                    if returned_identity != identity:
                        raise ValueError("task identity mismatch")
                    states[identity] = report
                except Exception as exc:
                    failures[identity] = f"{type(exc).__name__}: {exc}"
                atomic_json(
                    progress_path,
                    progress_payload(
                        protocol,
                        states=states,
                        failures=failures,
                        started_at=started_at,
                    ),
                )
    finally:
        resource_report = sampler.stop()
    if failures:
        raise RuntimeError(f"attack-family matrix failures: {failures}")
    completion: dict[str, Any] = {
        "schema_version": "strict_v4_attack_family_matrix_completion_v1",
        "state": "complete_gpu_execution",
        "completed_at_utc": utc_now(),
        "protocol_path": str(protocol_path),
        "protocol_file_sha256": file_hash(protocol_path),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "stage": protocol["stage"],
        "expected_task_count": protocol["expected_task_count"],
        "complete_task_count": len(states),
        "cache_reports": cache_reports,
        "task_artifacts": dict(sorted(states.items())),
        "resource_samples_file": str(result_root / "resource_samples.json"),
        "resource_samples_file_sha256": file_hash(
            result_root / "resource_samples.json"
        ),
        "resource_samples_manifest_sha256": resource_report["manifest_sha256"],
        "claim_boundary": protocol["claim_boundary"],
    }
    completion["manifest_sha256"] = canonical_hash(completion)
    atomic_json(completion_path, completion)
    atomic_json(
        progress_path,
        {
            **progress_payload(
                protocol,
                states=states,
                failures=failures,
                started_at=started_at,
            ),
            "state": "complete",
            "completion_manifest_sha256": completion["manifest_sha256"],
        },
    )
    print(json.dumps(completion, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
