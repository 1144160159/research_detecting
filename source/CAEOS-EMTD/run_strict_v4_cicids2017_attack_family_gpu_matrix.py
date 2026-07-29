from __future__ import annotations

import argparse
import json
import subprocess
import threading
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


REQUIRED_PAIRWISE = (
    "metrics.json",
    "scores.npz",
    "evidence_package.npz",
    "provenance.json",
)
REQUIRED_XGBOOST = (
    "metrics.json",
    "scores.npz",
    "provenance.json",
    "model.ubj",
    "gpu_execution.json",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def verify_protocol(project_root: Path, protocol_path: Path) -> dict[str, Any]:
    protocol = load_canonical(protocol_path, "GPU attack-family protocol")
    if (
        protocol.get("schema_version")
        != "strict_v4_cicids2017_attack_family_gpu_protocol_v1"
        or protocol.get("state")
        not in {
            "frozen_zero_result_development",
            "frozen_zero_result_confirmation",
        }
    ):
        raise ValueError("protocol is not executable")
    for name, expected in protocol["implementation_sha256"].items():
        if file_hash(project_root / name) != expected:
            raise ValueError(f"implementation hash drifted: {name}")
    source = protocol["source"]
    if file_hash(Path(source["csv"])) != source["csv_sha256"]:
        raise ValueError("source CSV hash drifted")
    if file_hash(Path(source["config"])) != source["config_sha256"]:
        raise ValueError("config hash drifted")
    if (
        protocol["xgboost_known_expert"]["execution_backend"] != "cuda"
        or protocol["claim_boundary"]["all_model_training_is_gpu"]
    ):
        raise ValueError("invalid heterogeneous GPU execution declaration")
    return protocol


def artifact_hashes(directory: Path, names: tuple[str, ...]) -> dict[str, str]:
    paths = {name: directory / name for name in names}
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing:
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
            "schema_version": "strict_v4_attack_family_gpu_resource_samples_v1",
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
    return [
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


def xgboost_cuda_command(
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
        str(project_root / "train_strict_v4_xgboost_warning_task_cuda.py"),
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
        "--gpu-sample-interval-seconds",
        str(parameters["gpu_sample_interval_seconds"]),
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


def write_pairwise_provenance(
    *,
    protocol: dict[str, Any],
    cache_path: Path,
    pairwise_dir: Path,
    scenario: str,
    unknown_family: str,
    seed: int,
) -> dict[str, Any]:
    artifacts = artifact_hashes(
        pairwise_dir, REQUIRED_PAIRWISE[:-1]
    )
    provenance: dict[str, Any] = {
        "schema_version": "strict_v4_attack_family_pairwise_provenance_v1",
        "state": "complete",
        "task": {
            "suite": protocol["suite"],
            "scenario": scenario,
            "seed": seed,
        },
        "unknown_family": unknown_family,
        "execution_backend": protocol["pairwise_caeos"]["execution_backend"],
        "cache_csv": str(cache_path),
        "cache_csv_sha256": file_hash(cache_path),
        "config": protocol["source"]["config"],
        "config_sha256": protocol["source"]["config_sha256"],
        "artifact_sha256": artifacts,
        "protocol_manifest_sha256": protocol["manifest_sha256"],
    }
    provenance["manifest_sha256"] = canonical_hash(provenance)
    atomic_json(pairwise_dir / "provenance.json", provenance)
    return provenance


def verify_gpu_task(
    protocol: dict[str, Any], xgboost_dir: Path
) -> dict[str, Any]:
    evidence = load_canonical(
        xgboost_dir / "gpu_execution.json", "XGBoost CUDA task evidence"
    )
    required = protocol["xgboost_known_expert"]
    if (
        not evidence.get("passes")
        or evidence.get("requested_device") != "cuda"
        or evidence.get("gpu_identity", {}).get("uuid")
        != required["required_gpu_uuid"]
        or not any(
            str(value).startswith("cuda")
            for value in evidence.get("booster_device_values", [])
        )
        or float(evidence.get("peak_gpu_memory_mib", 0.0)) <= 1.0
        or not evidence.get("compute_process_observed_by_nvidia_smi")
    ):
        raise ValueError(f"GPU evidence did not pass: {xgboost_dir}")
    return evidence


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
    xgboost_dir = run_root / "xgboost_cuda" / identity
    pairwise_dir.mkdir(parents=True, exist_ok=True)
    xgboost_dir.mkdir(parents=True, exist_ok=True)
    state = "reused"
    try:
        pairwise_hashes = artifact_hashes(pairwise_dir, REQUIRED_PAIRWISE)
        pairwise_provenance = load_canonical(
            pairwise_dir / "provenance.json", "Pairwise task provenance"
        )
        if (
            pairwise_provenance.get("task", {}).get("scenario") != scenario
            or int(pairwise_provenance.get("task", {}).get("seed", -1)) != seed
        ):
            raise ValueError("Pairwise task provenance identity mismatch")
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
        write_pairwise_provenance(
            protocol=protocol,
            cache_path=cache_path,
            pairwise_dir=pairwise_dir,
            scenario=scenario,
            unknown_family=unknown_family,
            seed=seed,
        )
        pairwise_hashes = artifact_hashes(pairwise_dir, REQUIRED_PAIRWISE)
        state = "trained"
    try:
        xgboost_hashes = artifact_hashes(xgboost_dir, REQUIRED_XGBOOST)
        gpu_evidence = verify_gpu_task(protocol, xgboost_dir)
    except FileNotFoundError:
        run_command(
            xgboost_cuda_command(
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
        gpu_evidence = verify_gpu_task(protocol, xgboost_dir)
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
        "gpu_execution": {
            "manifest_sha256": gpu_evidence["manifest_sha256"],
            "gpu_uuid": gpu_evidence["gpu_identity"]["uuid"],
            "peak_gpu_utilization_percent": gpu_evidence[
                "peak_gpu_utilization_percent"
            ],
            "peak_gpu_memory_mib": gpu_evidence["peak_gpu_memory_mib"],
            "sample_count": gpu_evidence["sample_count"],
            "passes": gpu_evidence["passes"],
        },
    }


def progress_payload(
    protocol: dict[str, Any],
    *,
    states: dict[str, dict[str, Any]],
    failures: dict[str, str],
    started_at: str,
) -> dict[str, Any]:
    return {
        "schema_version": "strict_v4_attack_family_gpu_matrix_progress_v1",
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
        existing = load_canonical(completion_path, "GPU matrix completion")
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
            max_workers=int(
                protocol["resource_contract"]["pairwise_outer_workers"]
            )
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
        raise RuntimeError(f"GPU attack-family matrix failures: {failures}")
    if len(states) != protocol["expected_task_count"]:
        raise RuntimeError("GPU attack-family matrix task count mismatch")

    peak_utilization = max(
        float(task["gpu_execution"]["peak_gpu_utilization_percent"])
        for task in states.values()
    )
    peak_memory = max(
        float(task["gpu_execution"]["peak_gpu_memory_mib"])
        for task in states.values()
    )
    completion: dict[str, Any] = {
        "schema_version": "strict_v4_attack_family_gpu_matrix_completion_v1",
        "state": "complete_heterogeneous_gpu_execution",
        "completed_at_utc": utc_now(),
        "protocol_path": str(protocol_path),
        "protocol_file_sha256": file_hash(protocol_path),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "stage": protocol["stage"],
        "expected_task_count": protocol["expected_task_count"],
        "complete_task_count": len(states),
        "cache_reports": cache_reports,
        "task_artifacts": dict(sorted(states.items())),
        "gpu_execution": {
            "required_gpu_uuid": protocol["xgboost_known_expert"][
                "required_gpu_uuid"
            ],
            "passing_task_count": sum(
                bool(task["gpu_execution"]["passes"])
                for task in states.values()
            ),
            "all_tasks_passed": all(
                bool(task["gpu_execution"]["passes"])
                for task in states.values()
            ),
            "peak_gpu_utilization_percent": peak_utilization,
            "peak_gpu_memory_mib": peak_memory,
        },
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
