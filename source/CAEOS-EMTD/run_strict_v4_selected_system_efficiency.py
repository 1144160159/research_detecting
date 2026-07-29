from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import replace
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any, Sequence

import joblib
import numpy as np

from benchmark_mdr_opendetect_runtime import (
    benchmark_once,
    exact_batch,
    gpu_peak_memory_mb,
    peak_rss,
    peak_rss_mb,
    timing_summary,
    torch,
    validate_prediction,
)
from caeos.selected_system_runtime import SelectedSystemRuntime
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_krc_selected_system_protocol import (
    build_sources as build_krc_sources,
)
from run_strict_v4_selected_system_external_malicious import (
    ALGORITHMS,
    PAIRWISE_RISK,
    opendetect_policy,
    pairwise_policy,
    rrc_protocol,
)
from run_strict_v4_selected_system_parrot_safety import (
    block_path,
    candidate_capture_command,
    materialize_rrc,
    source_capture_dir,
    validate_source_capture,
)
from summarize_strict_v4_mdr_selected_system import (
    LATENCY_METRICS,
    bootstrap_mean,
    positive_ratio,
)


PROTOCOL_SCHEMA = "strict_v4_selected_system_efficiency_protocol_v1"
BENCHMARK_SCHEMA = "strict_v4_selected_system_efficiency_benchmark_v1"
SUMMARY_SCHEMA = "strict_v4_selected_system_efficiency_summary_v1"
AUDIT_SCHEMA = "strict_v4_selected_system_efficiency_audit_v1"
EXECUTION_SCHEMA = "strict_v4_selected_system_efficiency_capture_execution_v1"
COMPARATORS = ("caeos_pairwise", "opendetect")
IMPLEMENTATION_FILES = (
    "run_strict_v4_selected_system_efficiency.py",
    "run_strict_v4_selected_system_parrot_safety.py",
    "run_strict_v4_selected_system_external_malicious.py",
    "caeos/selected_system_runtime.py",
    "caeos/pairwise_runtime.py",
    "caeos/krc_csr_runtime.py",
    "caeos/rrc_csr_runtime.py",
    "capture_pairwise_runtime.py",
    "capture_krc_csr_confirmation_runtime.py",
    "capture_csr_caeos_runtime.py",
    "capture_opendetect_training_runtime.py",
    "materialize_rrc_csr_runtime.py",
    "benchmark_mdr_opendetect_runtime.py",
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


def option(arguments: Sequence[str], name: str) -> str:
    values = list(arguments)
    if name not in values:
        raise ValueError(f"required trainer option is absent: {name}")
    index = values.index(name)
    if index + 1 >= len(values):
        raise ValueError(f"trainer option has no value: {name}")
    return str(values[index + 1])


def source_identity(source: dict[str, Any]) -> tuple[str, str, int]:
    return (
        str(source["suite"]),
        str(source["scenario"]),
        int(source["training_seed"]),
    )


def split_fingerprint(value: Any) -> str:
    output = value.get("combined") if isinstance(value, dict) else value
    if not isinstance(output, str) or len(output) != 64:
        raise ValueError("valid source split fingerprint required")
    return output


def output_counts(run_root: Path) -> dict[str, int]:
    return {
        "candidate_captures": (
            len(
                list(
                    run_root.glob(
                        "model_pairs/**/candidate_capture/capture_manifest.json"
                    )
                )
            )
            if run_root.exists()
            else 0
        ),
        "opendetect_captures": (
            len(
                list(
                    run_root.glob(
                        "model_pairs/**/opendetect_capture/capture_manifest.json"
                    )
                )
            )
            if run_root.exists()
            else 0
        ),
        "benchmarks": (
            len(list(run_root.glob("model_pairs/**/benchmark.json")))
            if run_root.exists()
            else 0
        ),
        "summary": int((run_root / "summary.json").is_file()),
        "audit": int((run_root / "audit.json").is_file()),
        "completion": int((run_root / "execution_complete.json").is_file()),
    }


def build_sources(
    confirmation: dict[str, Any], capture_root: Path
) -> list[dict[str, Any]]:
    validated = {
        source_identity(item): item
        for item in build_krc_sources(confirmation, capture_root)
    }
    corruption_seeds = {
        (
            str(task["suite"]),
            str(task["scenario"]),
            int(task["training_seed"]),
        ): int(task["corruption_seed"])
        for task in confirmation["confirmation"]["tasks"]
    }
    sources = []
    for identity, base in sorted(validated.items()):
        capture_dir = Path(base["capture_dir"])
        manifest_path = capture_dir / "capture_manifest.json"
        manifest = load(manifest_path)
        arguments = list(manifest.get("clean_trainer_arguments", []))
        if not arguments:
            raise ValueError("source capture lacks clean trainer arguments")
        fingerprint = split_fingerprint(manifest.get("split_fingerprint"))
        sources.append(
            {
                **base,
                "clean_trainer_arguments": arguments,
                "source_split_fingerprint": fingerprint,
                "corruption_seed": corruption_seeds[identity],
                "augmentation_seed": identity[2],
                "csv": option(arguments, "--csv"),
                "config": option(arguments, "--config"),
                "unknown_classes": option(arguments, "--unknown-classes"),
                "benign_class": option(arguments, "--benign-class"),
                "split_strategy": option(arguments, "--split-strategy"),
                "max_per_class": int(option(arguments, "--max-per-class")),
                "fresh_candidate_refit_required": True,
                "fresh_opendetect_refit_required": True,
            }
        )
    blocks: dict[tuple[str, str], set[int]] = defaultdict(set)
    for source in sources:
        suite, scenario, seed = source_identity(source)
        blocks[(suite, scenario)].add(seed)
    if (
        len(sources) != 306
        or len(blocks) != 102
        or any(seeds != {647, 653, 659} for seeds in blocks.values())
    ):
        raise ValueError("efficiency source matrix must be 102 scenarios x3")
    return sources


def create_protocol(
    *,
    project_root: Path,
    run_root: Path,
    activation_path: Path,
    adapter_design_path: Path,
    confirmation_protocol_path: Path,
    confirmation_capture_root: Path,
) -> dict[str, Any]:
    activation = load(activation_path)
    design = load(adapter_design_path)
    confirmation = load(confirmation_protocol_path)
    require_canonical(
        activation,
        "strict_v4_selected_system_activation_v1",
        "selected-system activation",
    )
    require_canonical(
        design,
        "strict_v4_selected_system_downstream_adapter_design_v1",
        "selected-system adapter design",
    )
    require_canonical(
        confirmation,
        "strict_v4_krc_csr_confirmation_protocol_v1",
        "KRC confirmation source protocol",
    )
    selected = activation.get("selected_algorithm")
    snapshot = activation.get("selection_snapshot", {})
    efficiency = design.get("efficiency_branch", {})
    if (
        activation.get("execution_admitted") is not True
        or snapshot.get("final") is not True
        or snapshot.get("selected_algorithm") != selected
        or activation.get("selection_snapshot_sha256")
        != canonical_hash(snapshot)
        or selected not in ALGORITHMS
        or activation.get("input_manifest_sha256", {}).get("adapter_design")
        != design["manifest_sha256"]
        or design.get("activation", {}).get("allowed_selected_algorithms")
        != list(ALGORITHMS)
        or efficiency.get("batch_sizes") != [1, 64, 512]
        or int(efficiency.get("clean_process_training_runs_per_method", 0))
        != 3
        or efficiency.get("adapter_overhead_is_included") is not True
        or efficiency.get("same_gpu_host_and_software_environment") is not True
        or efficiency.get("warmup_and_measurement_schedule_must_match")
        is not True
    ):
        raise ValueError("selected-system efficiency activation/design gate failed")
    counts = output_counts(run_root)
    if any(counts.values()):
        raise ValueError("efficiency protocol requires a zero-result run root")
    sources = build_sources(confirmation, confirmation_capture_root)
    tasks = [
        {
            "dataset": source["suite"],
            "unknown_attack_family": source["scenario"],
            "training_seed": int(source["training_seed"]),
            "validation_profile_seed": int(source["corruption_seed"]),
        }
        for source in sources
    ]
    implementation = {}
    for relative in IMPLEMENTATION_FILES:
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        implementation[relative] = file_hash(path)
    value: dict[str, Any] = {
        "schema_version": PROTOCOL_SCHEMA,
        "state": "admitted_after_final_selection_and_complete_source_matrix",
        "execution_admitted": True,
        "selected_algorithm": selected,
        "runtime_contract_schema": "strict_v4_selected_system_runtime_v1",
        "sources": sources,
        "source_count": 306,
        "scenario_block_count": 102,
        "training_seeds": [647, 653, 659],
        "candidate_training": {
            "fresh_refit_per_source_split": True,
            "external_test_data_excluded": True,
            "pairwise_runtime_policy": pairwise_policy(selected),
            "robust_runtime_policy": {
                "augmentation_weight": 0.5,
                "training_sample_fraction": 0.25,
                "health_quantile": 0.99,
            },
            "rrc_backend_protocol": (
                rrc_protocol(tasks)
                if selected == "rrc_csr_caeos_v1"
                else None
            ),
        },
        "opendetect_training": {
            **opendetect_policy(),
            "fresh_refit_per_source_split": True,
            "training_seed_equals_source_training_seed": True,
            "external_test_data_excluded": True,
        },
        "benchmark": {
            "batch_sizes": [1, 64, 512],
            "warmup_repetitions": 5,
            "timed_repetitions": 30,
            "method_order": "rotate_by_timed_repetition",
            "methods": ["selected_candidate", *COMPARATORS],
            "same_exact_arrays_and_process": True,
            "adapter_overhead_included_for_selected_and_pairwise": True,
            "latency_metrics": list(LATENCY_METRICS),
            "throughput_metric": "samples_per_second",
            "resource_metrics": [
                "peak_host_rss_mb",
                "peak_gpu_memory_mb",
                "artifact_bytes",
                "fit_wall_seconds",
            ],
            "exclusive_machine_preflight_required": True,
        },
        "aggregation": {
            "unit": "scenario_after_averaging_three_training_seeds_first",
            "scenario_block_count": 102,
            "bootstrap_repetitions": 10000,
            "bootstrap_seed": 20260727,
            "suite_equal_secondary_summary": True,
        },
        "strict_efficiency_gate": {
            "latency_ratio_bootstrap_95ci_upper_maximum": 1.0,
            "throughput_ratio_bootstrap_95ci_lower_minimum": 1.0,
            "artifact_ratio_bootstrap_95ci_upper_maximum": 1.0,
            "fit_time_ratio_bootstrap_95ci_upper_maximum": 1.0,
            "must_pass_against_each_comparator": list(COMPARATORS),
            "failure_only_blocks_multidimensional_efficiency_sota": True,
        },
        "resource_contract": {
            "environment_gate": "SELECTED_SYSTEM_EXCLUSIVE_MACHINE_GATE=passed",
            "candidate_capture_outer_workers": 1,
            "opendetect_capture_outer_workers": 1,
            "benchmark_outer_workers": 1,
            "subprocess_prefix": ["ionice", "-c", "3", "nice", "-n", "19"],
            "all_training_and_benchmarks_on_same_host": True,
        },
        "run_root": run_root.resolve().as_posix(),
        "output_counts_at_freeze": counts,
        "input_manifest_sha256": {
            "activation": activation["manifest_sha256"],
            "adapter_design": design["manifest_sha256"],
            "confirmation_protocol": confirmation["manifest_sha256"],
        },
        "input_file_sha256": {
            "activation": file_hash(activation_path),
            "adapter_design": file_hash(adapter_design_path),
            "confirmation_protocol": file_hash(confirmation_protocol_path),
        },
        "implementation_sha256": dict(sorted(implementation.items())),
        "claim_boundary": {
            "efficiency_is_separate_from_effectiveness": True,
            "efficiency_failure_does_not_cancel_accuracy_result": True,
            "candidate_identity_splicing_forbidden": True,
            "fresh_training_runs_per_scenario_per_method": 3,
            "selected_candidate_compared_with_embedded_pairwise_and_opendetect": (
                True
            ),
            "no_effectiveness_sota_supported_by_this_protocol_alone": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def opendetect_arguments(
    source: dict[str, Any], protocol: dict[str, Any], output_dir: Path
) -> list[str]:
    policy = protocol["opendetect_training"]
    return [
        "--dataset",
        "tabular",
        "--csv",
        str(source["csv"]),
        "--config",
        str(source["config"]),
        "--unknown-classes",
        str(source["unknown_classes"]),
        "--benign-class",
        str(source["benign_class"]),
        "--split-strategy",
        str(source["split_strategy"]),
        "--max-per-class",
        str(source["max_per_class"]),
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
        str(source["training_seed"]),
        "--device",
        "auto",
        "--output-dir",
        str(output_dir),
    ]


def opendetect_capture_command(
    *,
    python: str,
    project_root: Path,
    run_root: Path,
    protocol: dict[str, Any],
    source: dict[str, Any],
) -> list[str]:
    block = block_path(run_root, source)
    return [
        python,
        str(project_root / "capture_opendetect_training_runtime.py"),
        "--trainer",
        str(project_root / "train_neural_open_set.py"),
        "--capture-dir",
        str(block / "opendetect_capture"),
        "--",
        *opendetect_arguments(
            source, protocol, block / "opendetect_train"
        ),
    ]


def run_capture_command(
    *,
    command: list[str],
    directory: Path,
    prefix: list[str],
    method: str,
    source: dict[str, Any],
) -> dict[str, Any]:
    directory.mkdir(parents=True, exist_ok=True)
    log_path = directory / "execution.log"
    started = time.perf_counter()
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"command": command}) + "\n")
        handle.flush()
        completed = subprocess.run(
            [*prefix, *command],
            stdout=handle,
            stderr=subprocess.STDOUT,
            check=False,
        )
    wall_seconds = time.perf_counter() - started
    if completed.returncode != 0:
        failure = {
            "schema_version": "strict_v4_selected_system_efficiency_failure_v1",
            "method": method,
            "source": {
                "suite": source["suite"],
                "scenario": source["scenario"],
                "training_seed": int(source["training_seed"]),
            },
            "returncode": int(completed.returncode),
            "wall_seconds": wall_seconds,
            "command": command,
            "log_sha256": file_hash(log_path),
        }
        write_json(directory / "failure.json", failure)
        raise RuntimeError(f"efficiency capture failed: {directory}")
    manifest_path = directory / "capture_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(manifest_path)
    value: dict[str, Any] = {
        "schema_version": EXECUTION_SCHEMA,
        "state": "complete",
        "method": method,
        "source": {
            "suite": source["suite"],
            "scenario": source["scenario"],
            "training_seed": int(source["training_seed"]),
        },
        "command": command,
        "wall_seconds": wall_seconds,
        "capture_manifest_file_sha256": file_hash(manifest_path),
        "log_sha256": file_hash(log_path),
        "unknown_or_test_labels_used_for_cost_selection": False,
    }
    value["manifest_sha256"] = canonical_hash(value)
    write_json(directory / "capture_execution.json", value)
    return value


def validate_opendetect_capture(
    protocol: dict[str, Any],
    run_root: Path,
    source: dict[str, Any],
) -> bool:
    block = block_path(run_root, source)
    directory = block / "opendetect_capture"
    manifest_path = directory / "capture_manifest.json"
    execution_path = directory / "capture_execution.json"
    if not manifest_path.is_file() or not execution_path.is_file():
        return False
    manifest = load(manifest_path)
    execution = load(execution_path)
    artifact = directory / str(manifest.get("deployment_artifact", ""))
    inputs = directory / str(manifest.get("benchmark_inputs", ""))
    expected_arguments = opendetect_arguments(
        source, protocol, block / "opendetect_train"
    )
    require_canonical(execution, EXECUTION_SCHEMA, "OpenDetect execution")
    if (
        manifest.get("schema_version")
        != "strict_v4_opendetect_training_runtime_capture_v2"
        or manifest.get("trainer_arguments") != expected_arguments
        or manifest.get("benchmark_inputs_contain_labels") is not False
        or manifest.get("equivalence", {}).get("passes") is not True
        or manifest.get("runtime_evidence", {}).get(
            "contains_training_or_test_labels"
        )
        is not False
        or not artifact.is_file()
        or not inputs.is_file()
        or file_hash(artifact)
        != manifest.get("deployment_artifact_sha256")
        or file_hash(inputs) != manifest.get("benchmark_inputs_sha256")
        or execution.get("method") != "opendetect"
        or source_identity(execution["source"]) != source_identity(source)
        or execution.get("capture_manifest_file_sha256")
        != file_hash(manifest_path)
        or float(execution.get("wall_seconds", 0.0)) <= 0.0
    ):
        raise ValueError(f"invalid OpenDetect efficiency capture: {directory}")
    return True


def candidate_execution(
    protocol: dict[str, Any],
    run_root: Path,
    source: dict[str, Any],
) -> dict[str, Any]:
    directory = source_capture_dir(
        run_root, source, protocol["selected_algorithm"]
    )
    value = load(directory / "capture_execution.json")
    require_canonical(value, EXECUTION_SCHEMA, "candidate execution")
    if (
        value.get("method") != protocol["selected_algorithm"]
        or source_identity(value["source"]) != source_identity(source)
        or float(value.get("wall_seconds", 0.0)) <= 0.0
    ):
        raise ValueError("candidate execution identity or timing mismatch")
    return value


def _npz_views(path: Path, modality_count: int | None = None) -> list[np.ndarray]:
    with np.load(path, allow_pickle=False) as archive:
        names = [name for name in archive.files if name.startswith("view_")]
        names.sort(key=lambda name: int(name.rsplit("_", 1)[1]))
        if modality_count is not None and len(names) != int(modality_count):
            raise ValueError("captured modality count mismatch")
        views = [np.asarray(archive[name]) for name in names]
    if (
        not views
        or len({len(view) for view in views}) != 1
        or not len(views[0])
    ):
        raise ValueError("captured benchmark views are invalid")
    return views


def load_candidate(
    protocol: dict[str, Any],
    run_root: Path,
    source: dict[str, Any],
) -> tuple[Any, list[np.ndarray], float, float]:
    selected = protocol["selected_algorithm"]
    block = block_path(run_root, source)
    directory = block / "candidate_capture"
    manifest = load(directory / "capture_manifest.json")
    if selected in ("caeos_pairwise", "caeos_pug"):
        runtime = joblib.load(directory / manifest["deployment_artifact"])
        views = _npz_views(directory / manifest["benchmark_inputs"])
        metrics = load(block / "source_train" / "metrics.json")
        selected_risk = runtime.evidence()["selected_risk"]
        threshold = float(metrics["validation_thresholds"][selected_risk])
        pairwise_threshold = float(
            metrics["validation_thresholds"][PAIRWISE_RISK]
        )
        return runtime, views, threshold, pairwise_threshold
    runtime = joblib.load(directory / manifest["runtime_artifact"])
    modality_count = int(runtime.evidence()["modality_count"])
    views = _npz_views(
        directory / manifest["evaluation_inputs"], modality_count
    )
    threshold = float(runtime.clean_threshold)
    return runtime, views, threshold, threshold


def embedded_pairwise(runtime: Any, selected: str) -> Any:
    if selected == "caeos_pug":
        return replace(runtime, selected_risk=PAIRWISE_RISK)
    if selected == "caeos_pairwise":
        return runtime
    clean_runtime = runtime.base_runtime.clean_runtime
    if clean_runtime.evidence().get("selected_risk") != PAIRWISE_RISK:
        raise ValueError("robust runtime does not embed frozen Pairwise")
    return clean_runtime


def _execution_context(
    candidate_evidence: dict[str, Any],
    opendetect_evidence: dict[str, Any],
) -> dict[str, Any]:
    affinity = (
        sorted(os.sched_getaffinity(0))
        if hasattr(os, "sched_getaffinity")
        else None
    )
    cuda_name = None
    if torch is not None and torch.cuda.is_available():
        cuda_name = torch.cuda.get_device_name(torch.cuda.current_device())
    return {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "logical_cpu_count": os.cpu_count(),
        "cpu_affinity": affinity,
        "thread_environment": {
            name: os.environ.get(name)
            for name in (
                "OMP_NUM_THREADS",
                "OPENBLAS_NUM_THREADS",
                "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS",
            )
        },
        "candidate_device": candidate_evidence.get("device", "cpu"),
        "opendetect_device": opendetect_evidence.get("device"),
        "cuda_device_name": cuda_name,
        "same_process": True,
    }


def benchmark_source(
    *,
    protocol: dict[str, Any],
    run_root: Path,
    source: dict[str, Any],
    output: Path,
) -> dict[str, Any]:
    if os.environ.get("SELECTED_SYSTEM_EXCLUSIVE_MACHINE_GATE") != "passed":
        raise ValueError("exclusive-machine preflight marker is required")
    require_canonical(protocol, PROTOCOL_SCHEMA, "efficiency protocol")
    expected = {
        source_identity(item): item for item in protocol["sources"]
    }
    identity = source_identity(source)
    if len(expected) != 306 or identity not in expected:
        raise ValueError("benchmark source is not in frozen matrix")
    source = expected[identity]
    if not validate_source_capture(protocol, run_root, source):
        raise FileNotFoundError("selected candidate capture is incomplete")
    if not validate_opendetect_capture(protocol, run_root, source):
        raise FileNotFoundError("OpenDetect capture is incomplete")
    candidate_execution_value = candidate_execution(
        protocol, run_root, source
    )
    selected = protocol["selected_algorithm"]
    runtime, views, threshold, pairwise_threshold = load_candidate(
        protocol, run_root, source
    )
    candidate = SelectedSystemRuntime(runtime, selected, threshold)
    pairwise_runtime = embedded_pairwise(runtime, selected)
    pairwise = SelectedSystemRuntime(
        pairwise_runtime, "caeos_pairwise", pairwise_threshold
    )
    block = block_path(run_root, source)
    opendetect_dir = block / "opendetect_capture"
    opendetect_manifest = load(opendetect_dir / "capture_manifest.json")
    opendetect = joblib.load(
        opendetect_dir / opendetect_manifest["deployment_artifact"]
    )
    opendetect_views = _npz_views(
        opendetect_dir / opendetect_manifest["benchmark_inputs"]
    )
    if (
        len(views) != len(opendetect_views)
        or not all(
            np.array_equal(left, right)
            for left, right in zip(views, opendetect_views)
        )
    ):
        raise ValueError("candidate/OpenDetect exact input identity failed")
    validate_prediction(candidate.predict(views), len(views[0]))
    validate_prediction(pairwise.predict(views), len(views[0]))
    validate_prediction(opendetect.predict(views), len(views[0]))
    candidate_artifact = output.parent / "selected_candidate_adapter.joblib"
    pairwise_artifact = output.parent / "embedded_pairwise_adapter.joblib"
    candidate_artifact.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(candidate, candidate_artifact, compress=3)
    joblib.dump(pairwise, pairwise_artifact, compress=3)
    candidate_roundtrip = joblib.load(candidate_artifact).predict(views)
    pairwise_roundtrip = joblib.load(pairwise_artifact).predict(views)
    if (
        not np.array_equal(
            candidate.predict(views)["prediction"],
            candidate_roundtrip["prediction"],
        )
        or not np.array_equal(
            pairwise.predict(views)["prediction"],
            pairwise_roundtrip["prediction"],
        )
    ):
        raise ValueError("selected-system adapter serialization failed")
    opendetect_evidence = opendetect.evidence()
    opendetect_device = str(opendetect_evidence["device"])
    if (
        torch is not None
        and torch.device(opendetect_device).type == "cuda"
        and torch.cuda.is_available()
    ):
        torch.cuda.reset_peak_memory_stats(torch.device(opendetect_device))
    methods = {
        "selected_candidate": (candidate, None),
        "caeos_pairwise": (pairwise, None),
        "opendetect": (opendetect, opendetect.synchronize),
    }
    blocks = {}
    peak_before = peak_rss()
    policy = protocol["benchmark"]
    for batch_size in policy["batch_sizes"]:
        batch = exact_batch(views, int(batch_size))
        for _ in range(int(policy["warmup_repetitions"])):
            for method, synchronize in methods.values():
                benchmark_once(method, batch, synchronize=synchronize)
        timings = {name: [] for name in methods}
        names = list(methods)
        for repetition in range(int(policy["timed_repetitions"])):
            offset = repetition % len(names)
            order = names[offset:] + names[:offset]
            for name in order:
                method, synchronize = methods[name]
                timings[name].append(
                    benchmark_once(
                        method, batch, synchronize=synchronize
                    )
                )
        blocks[str(batch_size)] = {
            name: {
                **timing_summary(values, int(batch_size)),
                "raw_seconds": values,
            }
            for name, values in timings.items()
        }
    peak_after = peak_rss()
    opendetect_execution_value = load(
        opendetect_dir / "capture_execution.json"
    )
    pairwise_fit_seconds = (
        float(candidate_execution_value["wall_seconds"])
        if selected in ("caeos_pairwise", "caeos_pug")
        else float(
            load(
                source_capture_dir(run_root, source, selected)
                / "capture_manifest.json"
            )["clean_capture_wall_seconds"]
        )
    )
    value: dict[str, Any] = {
        "schema_version": BENCHMARK_SCHEMA,
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "selected_algorithm": selected,
        "source": {
            "suite": identity[0],
            "scenario": identity[1],
            "training_seed": identity[2],
            "source_split_fingerprint": source[
                "source_split_fingerprint"
            ],
            "candidate_capture_manifest_file_sha256": (
                candidate_execution_value["capture_manifest_file_sha256"]
            ),
            "opendetect_capture_manifest_file_sha256": (
                opendetect_execution_value[
                    "capture_manifest_file_sha256"
                ]
            ),
        },
        "same_input_evidence": {
            "candidate_pairwise_opendetect_received_same_arrays": True,
            "row_count": int(len(views[0])),
            "modality_count": len(views),
            "view_shapes": [list(view.shape) for view in views],
            "labels_loaded": False,
        },
        "runtime_evidence": {
            "candidate": candidate.evidence(),
            "embedded_pairwise": pairwise.evidence(),
            "opendetect": opendetect_evidence,
        },
        "serialization_roundtrip": {
            "selected_candidate": True,
            "embedded_pairwise": True,
            "opendetect": opendetect_manifest["equivalence"]["passes"],
        },
        "benchmark": blocks,
        "cost": {
            "selected_candidate_fit_wall_seconds": float(
                candidate_execution_value["wall_seconds"]
            ),
            "caeos_pairwise_fit_wall_seconds": pairwise_fit_seconds,
            "opendetect_fit_wall_seconds": float(
                opendetect_execution_value["wall_seconds"]
            ),
            "selected_candidate_artifact_bytes": int(
                candidate_artifact.stat().st_size
            ),
            "caeos_pairwise_artifact_bytes": int(
                pairwise_artifact.stat().st_size
            ),
            "opendetect_artifact_bytes": int(
                (
                    opendetect_dir
                    / opendetect_manifest["deployment_artifact"]
                ).stat().st_size
            ),
        },
        "process_peak_rss": {
            "ru_maxrss_before": peak_before,
            "ru_maxrss_after": peak_after,
            "peak_host_rss_mb": peak_rss_mb(peak_after),
        },
        "peak_gpu_memory_mb": gpu_peak_memory_mb(opendetect_device),
        "execution_context": _execution_context(
            runtime.evidence(), opendetect_evidence
        ),
        "exclusive_machine_preflight_marker": "passed",
        "unknown_or_test_labels_used_for_benchmark_selection": False,
    }
    value["manifest_sha256"] = canonical_hash(value)
    write_json(output, value)
    return value


def aggregate_records(
    records: list[dict[str, Any]], protocol: dict[str, Any]
) -> dict[str, Any]:
    require_canonical(protocol, PROTOCOL_SCHEMA, "efficiency protocol")
    expected = {
        source_identity(source): source for source in protocol["sources"]
    }
    if len(records) != 306 or len(expected) != 306:
        raise ValueError("exactly 306 efficiency records are required")
    grouped: dict[
        tuple[str, str], list[dict[str, Any]]
    ] = defaultdict(list)
    contexts = set()
    host_peaks = []
    gpu_peaks = []
    seen = set()
    for record in records:
        require_canonical(record, BENCHMARK_SCHEMA, "efficiency benchmark")
        source = record["source"]
        identity = source_identity(source)
        if (
            identity in seen
            or identity not in expected
            or record.get("protocol_manifest_sha256")
            != protocol["manifest_sha256"]
            or record.get("selected_algorithm")
            != protocol["selected_algorithm"]
            or source.get("source_split_fingerprint")
            != expected[identity]["source_split_fingerprint"]
            or record.get("same_input_evidence", {}).get(
                "candidate_pairwise_opendetect_received_same_arrays"
            )
            is not True
            or record.get("same_input_evidence", {}).get("labels_loaded")
            is not False
            or not all(record.get("serialization_roundtrip", {}).values())
            or record.get("exclusive_machine_preflight_marker") != "passed"
            or record.get(
                "unknown_or_test_labels_used_for_benchmark_selection"
            )
            is not False
        ):
            raise ValueError("invalid efficiency benchmark binding")
        seen.add(identity)
        ratios: dict[str, Any] = {
            "suite": identity[0],
            "scenario": identity[1],
            "training_seed": identity[2],
            "comparators": {},
        }
        for comparator in COMPARATORS:
            comparator_ratios: dict[str, Any] = {"batches": {}}
            for batch_size in protocol["benchmark"]["batch_sizes"]:
                block = record["benchmark"][str(batch_size)]
                if set(block) != {
                    "selected_candidate",
                    "caeos_pairwise",
                    "opendetect",
                }:
                    raise ValueError("benchmark method coverage mismatch")
                values = {}
                for metric in LATENCY_METRICS:
                    values[metric] = positive_ratio(
                        block["selected_candidate"][metric],
                        block[comparator][metric],
                    )
                values["samples_per_second"] = positive_ratio(
                    block["selected_candidate"]["samples_per_second"],
                    block[comparator]["samples_per_second"],
                )
                comparator_ratios["batches"][str(batch_size)] = values
            cost = record["cost"]
            comparator_ratios["artifact_ratio"] = positive_ratio(
                cost["selected_candidate_artifact_bytes"],
                cost[f"{comparator}_artifact_bytes"],
            )
            comparator_ratios["fit_time_ratio"] = positive_ratio(
                cost["selected_candidate_fit_wall_seconds"],
                cost[f"{comparator}_fit_wall_seconds"],
            )
            ratios["comparators"][comparator] = comparator_ratios
        peak_host = record.get("process_peak_rss", {}).get(
            "peak_host_rss_mb"
        )
        peak_gpu = record.get("peak_gpu_memory_mb")
        if (
            peak_host is None
            or not np.isfinite(float(peak_host))
            or float(peak_host) <= 0.0
            or peak_gpu is None
            or not np.isfinite(float(peak_gpu))
            or float(peak_gpu) < 0.0
        ):
            raise ValueError("complete finite resource metrics required")
        host_peaks.append(float(peak_host))
        gpu_peaks.append(float(peak_gpu))
        contexts.add(
            json.dumps(record["execution_context"], sort_keys=True)
        )
        grouped[identity[:2]].append(ratios)
        seen.add(identity)
    if seen != set(expected):
        raise ValueError("efficiency benchmark coverage mismatch")
    expected_seeds = set(map(int, protocol["training_seeds"]))
    if (
        len(grouped) != 102
        or any(len(values) != 3 for values in grouped.values())
        or any(
            {int(value["training_seed"]) for value in values}
            != expected_seeds
            for values in grouped.values()
        )
    ):
        raise ValueError("three-seed scenario blocks are incomplete")
    scenario_blocks = []
    series: dict[str, dict[str, list[float]]] = {
        comparator: defaultdict(list) for comparator in COMPARATORS
    }
    suite_series: dict[
        str, dict[str, dict[str, list[float]]]
    ] = defaultdict(
        lambda: {
            comparator: defaultdict(list)
            for comparator in COMPARATORS
        }
    )
    for (suite, scenario), values in sorted(grouped.items()):
        block: dict[str, Any] = {
            "suite": suite,
            "scenario": scenario,
            "seed_count": 3,
            "comparators": {},
        }
        for comparator in COMPARATORS:
            output: dict[str, Any] = {"batches": {}}
            for batch_size in protocol["benchmark"]["batch_sizes"]:
                batch_key = str(batch_size)
                output["batches"][batch_key] = {}
                for metric in (*LATENCY_METRICS, "samples_per_second"):
                    mean = float(
                        np.mean(
                            [
                                value["comparators"][comparator][
                                    "batches"
                                ][batch_key][metric]
                                for value in values
                            ]
                        )
                    )
                    key = f"batch{batch_size}_{metric}"
                    output["batches"][batch_key][metric] = mean
                    series[comparator][key].append(mean)
                    suite_series[suite][comparator][key].append(mean)
            for key in ("artifact_ratio", "fit_time_ratio"):
                mean = float(
                    np.mean(
                        [
                            value["comparators"][comparator][key]
                            for value in values
                        ]
                    )
                )
                output[key] = mean
                series[comparator][key].append(mean)
                suite_series[suite][comparator][key].append(mean)
            block["comparators"][comparator] = output
        scenario_blocks.append(block)
    inference = {}
    strict = {}
    base_seed = int(protocol["aggregation"]["bootstrap_seed"])
    repetitions = int(protocol["aggregation"]["bootstrap_repetitions"])
    for comparator_index, comparator in enumerate(COMPARATORS):
        inference[comparator] = {}
        checks = {}
        for metric_index, key in enumerate(sorted(series[comparator])):
            summary = bootstrap_mean(
                series[comparator][key],
                seed=base_seed + comparator_index * 100 + metric_index,
                repetitions=repetitions,
            )
            inference[comparator][key] = summary
            checks[key] = (
                summary["bootstrap_95ci"][0] >= 1.0
                if key.endswith("samples_per_second")
                else summary["bootstrap_95ci"][1] <= 1.0
            )
        strict[comparator] = {
            "checks": checks,
            "passes": all(checks.values()),
        }
    suite_equal = {
        suite: {
            comparator: {
                key: float(np.mean(values))
                for key, values in sorted(metrics.items())
            }
            for comparator, metrics in comparators.items()
        }
        for suite, comparators in sorted(suite_series.items())
    }
    deployability_checks = {
        "benchmark_count_is_306": len(records) == 306,
        "scenario_block_count_is_102": len(scenario_blocks) == 102,
        "all_three_method_roundtrips_pass": True,
        "all_outputs_finite": all(
            np.isfinite(value)
            for comparator in COMPARATORS
            for values in series[comparator].values()
            for value in values
        ),
        "same_hardware_context_is_constant": len(contexts) == 1,
        "same_inputs_for_all_three_methods": True,
        "complete_resource_reporting": True,
        "failure_count_zero": True,
    }
    return {
        "benchmark_count": len(records),
        "scenario_block_count": len(scenario_blocks),
        "failure_count": 0,
        "scenario_blocks": scenario_blocks,
        "ratio_inference": inference,
        "suite_equal_secondary_summary": suite_equal,
        "resource_reporting": {
            "peak_host_rss_mb_min": float(np.min(host_peaks)),
            "peak_host_rss_mb_median": float(np.median(host_peaks)),
            "peak_host_rss_mb_max": float(np.max(host_peaks)),
            "peak_gpu_memory_mb_min": float(np.min(gpu_peaks)),
            "peak_gpu_memory_mb_median": float(np.median(gpu_peaks)),
            "peak_gpu_memory_mb_max": float(np.max(gpu_peaks)),
            "execution_context": json.loads(next(iter(contexts))),
        },
        "deployability_decision": {
            "checks": deployability_checks,
            "passes": all(deployability_checks.values()),
        },
        "strict_efficiency_decision": {
            "by_comparator": strict,
            "passes": all(value["passes"] for value in strict.values()),
            "failure_only_blocks_multidimensional_efficiency_sota": True,
        },
    }


def summarize(
    protocol: dict[str, Any], run_root: Path
) -> dict[str, Any]:
    records = []
    registry = []
    for source in protocol["sources"]:
        path = block_path(run_root, source) / "benchmark.json"
        if not path.is_file():
            raise FileNotFoundError(path)
        records.append(load(path))
        registry.append(
            {
                "suite": source["suite"],
                "scenario": source["scenario"],
                "training_seed": int(source["training_seed"]),
                "benchmark_file_sha256": file_hash(path),
            }
        )
    value: dict[str, Any] = {
        "schema_version": SUMMARY_SCHEMA,
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        **aggregate_records(records, protocol),
        "benchmark_file_registry": registry,
        "claim_boundary": protocol["claim_boundary"],
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def audit(
    protocol: dict[str, Any], summary: dict[str, Any]
) -> dict[str, Any]:
    require_canonical(protocol, PROTOCOL_SCHEMA, "efficiency protocol")
    require_canonical(summary, SUMMARY_SCHEMA, "efficiency summary")
    checks = {
        "summary_bound_to_protocol": (
            summary.get("protocol_manifest_sha256")
            == protocol["manifest_sha256"]
        ),
        "benchmark_count_is_306": summary.get("benchmark_count") == 306,
        "scenario_block_count_is_102": (
            summary.get("scenario_block_count") == 102
        ),
        "failure_count_zero": summary.get("failure_count") == 0,
        "deployability_passes": (
            summary.get("deployability_decision", {}).get("passes") is True
        ),
        "pairwise_comparison_complete": (
            "caeos_pairwise"
            in summary.get("strict_efficiency_decision", {}).get(
                "by_comparator", {}
            )
        ),
        "opendetect_comparison_complete": (
            "opendetect"
            in summary.get("strict_efficiency_decision", {}).get(
                "by_comparator", {}
            )
        ),
        "accuracy_result_is_not_cancelled_by_efficiency": (
            protocol["claim_boundary"][
                "efficiency_failure_does_not_cancel_accuracy_result"
            ]
            is True
        ),
    }
    strict = summary["strict_efficiency_decision"]
    value: dict[str, Any] = {
        "schema_version": AUDIT_SCHEMA,
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "summary_manifest_sha256": summary["manifest_sha256"],
        "checks": checks,
        "passed": all(checks.values()),
        "strict_efficiency_sota_supported": bool(
            all(checks.values()) and strict["passes"]
        ),
        "strict_efficiency_by_comparator": strict["by_comparator"],
        "effectiveness_sota_supported_by_this_audit": False,
        "claim_boundary": protocol["claim_boundary"],
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def pending_state(
    activation_path: Path,
    confirmation_protocol_path: Path,
    confirmation_capture_root: Path,
) -> dict[str, Any]:
    if not activation_path.is_file():
        return {
            "state": "pending_selected_system_activation",
            "protocol_written": False,
        }
    if not confirmation_protocol_path.is_file():
        return {
            "state": "pending_confirmation_protocol",
            "protocol_written": False,
        }
    confirmation = load(confirmation_protocol_path)
    expected = confirmation.get("confirmation", {}).get("tasks", [])
    present = 0
    for task in expected:
        path = (
            confirmation_capture_root
            / str(task["suite"])
            / str(task["scenario"])
            / f"seed{int(task['training_seed'])}"
            / "capture_manifest.json"
        )
        present += int(path.is_file())
    if len(expected) != 306 or present != 306:
        return {
            "state": "pending_complete_306_source_capture_matrix",
            "protocol_written": False,
            "source_capture_count": present,
            "expected_source_capture_count": 306,
        }
    return {"state": "ready", "protocol_written": False}


def execute(
    *,
    protocol: dict[str, Any],
    project_root: Path,
    run_root: Path,
    python: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if os.environ.get("SELECTED_SYSTEM_EXCLUSIVE_MACHINE_GATE") != "passed":
        raise ValueError("exclusive-machine preflight marker is required")
    prefix = list(protocol["resource_contract"]["subprocess_prefix"])
    selected = protocol["selected_algorithm"]
    for source in protocol["sources"]:
        directory = source_capture_dir(run_root, source, selected)
        if not (directory / "capture_manifest.json").is_file():
            command = candidate_capture_command(
                python=python,
                project_root=project_root,
                run_root=run_root,
                protocol=protocol,
                source=source,
            )
            run_capture_command(
                command=command,
                directory=directory,
                prefix=prefix,
                method=selected,
                source=source,
            )
    if selected == "rrc_csr_caeos_v1":
        materialize_rrc(protocol, run_root)
    for source in protocol["sources"]:
        if not validate_source_capture(protocol, run_root, source):
            raise FileNotFoundError("candidate capture is incomplete")
        directory = block_path(run_root, source) / "opendetect_capture"
        if not (directory / "capture_manifest.json").is_file():
            command = opendetect_capture_command(
                python=python,
                project_root=project_root,
                run_root=run_root,
                protocol=protocol,
                source=source,
            )
            run_capture_command(
                command=command,
                directory=directory,
                prefix=prefix,
                method="opendetect",
                source=source,
            )
        validate_opendetect_capture(protocol, run_root, source)
    for source in protocol["sources"]:
        output = block_path(run_root, source) / "benchmark.json"
        if not output.is_file():
            benchmark_source(
                protocol=protocol,
                run_root=run_root,
                source=source,
                output=output,
            )
    summary = summarize(protocol, run_root)
    audit_value = audit(protocol, summary)
    write_json(run_root / "summary.json", summary)
    write_json(run_root / "audit.json", audit_value)
    completion = {
        "schema_version": (
            "strict_v4_selected_system_efficiency_execution_complete_v1"
        ),
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "summary_manifest_sha256": summary["manifest_sha256"],
        "audit_manifest_sha256": audit_value["manifest_sha256"],
        "audit_passed": audit_value["passed"],
        "strict_efficiency_sota_supported": audit_value[
            "strict_efficiency_sota_supported"
        ],
    }
    completion["manifest_sha256"] = canonical_hash(completion)
    write_json(run_root / "execution_complete.json", completion)
    return summary, audit_value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path(__file__).parent)
    parser.add_argument(
        "--run-root",
        type=Path,
        default=Path("runs/strict_v4_selected_system_efficiency_v1"),
    )
    parser.add_argument(
        "--activation",
        type=Path,
        default=Path(
            "results/strict_v4_selected_system_downstream_adapter_v1/"
            "activation.json"
        ),
    )
    parser.add_argument(
        "--adapter-design",
        type=Path,
        default=Path(
            "results/strict_v4_selected_system_downstream_adapter_design_v1/"
            "design.json"
        ),
    )
    parser.add_argument(
        "--confirmation-protocol",
        type=Path,
        default=Path(
            "results/strict_v4_krc_csr_confirmation_protocol_v1/"
            "protocol.json"
        ),
    )
    parser.add_argument(
        "--confirmation-capture-root",
        type=Path,
        default=Path("runs/strict_v4_krc_csr_confirmation_v1/captures"),
    )
    parser.add_argument(
        "--protocol-output",
        type=Path,
        default=Path(
            "results/strict_v4_selected_system_efficiency_protocol_v1/"
            "protocol.json"
        ),
    )
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    project_root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else (project_root / path).resolve()

    activation = resolve(args.activation)
    confirmation_protocol = resolve(args.confirmation_protocol)
    confirmation_capture_root = resolve(args.confirmation_capture_root)
    pending = pending_state(
        activation, confirmation_protocol, confirmation_capture_root
    )
    if pending["state"] != "ready":
        print(json.dumps(pending, sort_keys=True))
        return
    run_root = resolve(args.run_root)
    protocol = create_protocol(
        project_root=project_root,
        run_root=run_root,
        activation_path=activation,
        adapter_design_path=resolve(args.adapter_design),
        confirmation_protocol_path=confirmation_protocol,
        confirmation_capture_root=confirmation_capture_root,
    )
    protocol_output = resolve(args.protocol_output)
    write_json(protocol_output, protocol)
    if not args.execute:
        print(
            json.dumps(
                {
                    "state": "protocol_frozen_execution_not_requested",
                    "protocol_written": True,
                    "manifest_sha256": protocol["manifest_sha256"],
                },
                sort_keys=True,
            )
        )
        return
    summary, audit_value = execute(
        protocol=protocol,
        project_root=project_root,
        run_root=run_root,
        python=args.python,
    )
    print(
        json.dumps(
            {
                "state": "complete",
                "summary_manifest_sha256": summary["manifest_sha256"],
                "audit_manifest_sha256": audit_value["manifest_sha256"],
                "strict_efficiency_sota_supported": audit_value[
                    "strict_efficiency_sota_supported"
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
