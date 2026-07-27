from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import time
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from run_strict_v4_vgrf_selected_system_seed317 import load


def batch_indices(
    sample_count: int, batch_size: int, repetition: int
) -> np.ndarray:
    if sample_count <= 0 or batch_size <= 0 or repetition < 0:
        raise ValueError("invalid benchmark index arguments")
    start = (repetition * batch_size) % sample_count
    return (
        np.arange(start, start + batch_size, dtype=np.int64)
        % sample_count
    )


def method_order(repetition: int) -> tuple[str, str]:
    return (
        ("vgrf", "opendetect")
        if repetition % 2 == 0
        else ("opendetect", "vgrf")
    )


def sync_cuda() -> None:
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.synchronize()
    except ImportError:
        return


def gpu_peak_mb(reset: bool = False) -> float:
    try:
        import torch

        if not torch.cuda.is_available():
            return 0.0
        if reset:
            torch.cuda.reset_peak_memory_stats()
            return 0.0
        return float(torch.cuda.max_memory_allocated() / (1024.0**2))
    except ImportError:
        return 0.0


def host_rss_mb() -> float | None:
    try:
        import resource

        return float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0)
    except ImportError:
        return None


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


def active_gpu_processes() -> list[str]:
    completed = subprocess.run(
        [
            "nvidia-smi",
            "--query-compute-apps=pid,process_name",
            "--format=csv,noheader",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("nvidia-smi process query failed")
    return [
        line.strip()
        for line in completed.stdout.splitlines()
        if line.strip()
    ]


def load_views(path: Path) -> list[np.ndarray]:
    with np.load(path, allow_pickle=False) as payload:
        names = sorted(
            payload.files,
            key=lambda name: int(name[len("view_") :]),
        )
        if names != [f"view_{index}" for index in range(len(names))]:
            raise ValueError("benchmark views are not contiguous")
        views = [np.asarray(payload[name]) for name in names]
    if not views or len({len(view) for view in views}) != 1:
        raise ValueError("benchmark views are empty or misaligned")
    return views


def equal_views(left: Sequence[np.ndarray], right: Sequence[np.ndarray]) -> bool:
    return len(left) == len(right) and all(
        np.array_equal(first, second)
        for first, second in zip(left, right)
    )


def percentile(values: Sequence[float], quantile: float) -> float:
    return float(np.percentile(np.asarray(values, dtype=np.float64), quantile))


def benchmark_block(
    *,
    vgrf: Any,
    opendetect: Any,
    views: list[np.ndarray],
    batch_sizes: Sequence[int],
    warmups: int,
    repetitions: int,
) -> dict[str, Any]:
    if warmups < 0 or repetitions <= 0:
        raise ValueError("invalid benchmark repetition policy")
    methods = {"vgrf": vgrf, "opendetect": opendetect}
    records: list[dict[str, Any]] = []
    peak_by_method = {"vgrf": 0.0, "opendetect": 0.0}
    for batch_size in batch_sizes:
        for repetition in range(warmups):
            indices = batch_indices(
                len(views[0]), batch_size, repetition
            )
            batch = [view[indices] for view in views]
            for name in method_order(repetition):
                output = methods[name].predict_views(batch)
                if len(output["risk"]) != batch_size:
                    raise RuntimeError("warmup output batch size mismatch")
        latencies = {"vgrf": [], "opendetect": []}
        checksums = {"vgrf": 0.0, "opendetect": 0.0}
        orders = []
        for repetition in range(repetitions):
            indices = batch_indices(
                len(views[0]), batch_size, warmups + repetition
            )
            batch = [view[indices] for view in views]
            order = method_order(repetition)
            orders.append(list(order))
            for name in order:
                gpu_peak_mb(reset=True)
                sync_cuda()
                started = time.perf_counter_ns()
                output = methods[name].predict_views(batch)
                sync_cuda()
                elapsed = (
                    time.perf_counter_ns() - started
                ) / 1_000_000.0
                if len(output["risk"]) != batch_size:
                    raise RuntimeError("timed output batch size mismatch")
                latencies[name].append(elapsed)
                checksums[name] += float(
                    np.asarray(output["risk"], dtype=np.float64).sum()
                )
                peak_by_method[name] = max(
                    peak_by_method[name], gpu_peak_mb()
                )
        by_method = {}
        for name, values in latencies.items():
            total_seconds = sum(values) / 1000.0
            by_method[name] = {
                "latency_p50_ms": percentile(values, 50),
                "latency_p95_ms": percentile(values, 95),
                "latency_p99_ms": percentile(values, 99),
                "samples_per_second": float(
                    batch_size * repetitions / total_seconds
                ),
                "latency_samples_ms": values,
                "output_checksum": checksums[name],
            }
        records.append(
            {
                "batch_size": int(batch_size),
                "warmup_repetitions": warmups,
                "timed_repetitions": repetitions,
                "method_orders": orders,
                "methods": by_method,
            }
        )
    return {
        "records": records,
        "peak_gpu_memory_mb": peak_by_method,
        "peak_host_rss_mb": host_rss_mb(),
    }


def record_capture_paths(record: dict[str, Any]) -> dict[str, Path]:
    roots = record["deployment_output_roots"]
    return {
        "vgrf": Path(roots["vgrf_capture"]),
        "opendetect": Path(roots["opendetect_capture"]),
    }


def benchmark_record(
    record: dict[str, Any],
    protocol: dict[str, Any],
    output: Path,
) -> dict[str, Any]:
    import joblib

    roots = record_capture_paths(record)
    manifests = {
        name: load(root / "capture_manifest.json")
        for name, root in roots.items()
    }
    for name, expected_schema in {
        "vgrf": "strict_v4_vgrf_deployment_capture_v2",
        "opendetect": "strict_v4_opendetect_deployment_capture_v1",
    }.items():
        if manifests[name].get("schema_version") != expected_schema:
            raise ValueError(f"invalid {name} deployment capture")
    vgrf_input_path = roots["vgrf"] / manifests["vgrf"][
        "processed_benchmark_inputs"
    ]
    open_input_path = roots["opendetect"] / manifests["opendetect"][
        "processed_benchmark_inputs"
    ]
    vgrf_views = load_views(vgrf_input_path)
    open_views = load_views(open_input_path)
    if not equal_views(vgrf_views, open_views):
        raise ValueError("VGRF and OpenDetect benchmark inputs differ")
    bundles = {
        name: joblib.load(root / manifests[name]["deployment_artifact"])
        for name, root in roots.items()
    }
    design = protocol["runtime_equivalence_and_efficiency"]
    result = benchmark_block(
        vgrf=bundles["vgrf"],
        opendetect=bundles["opendetect"],
        views=vgrf_views,
        batch_sizes=design["batch_sizes"],
        warmups=int(design["warmup_repetitions"]),
        repetitions=int(design["timed_repetitions"]),
    )
    value = {
        "schema_version": (
            "strict_v4_vgrf_selected_system_runtime_block_v1"
        ),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "suite": record["suite"],
        "scenario": record["scenario"],
        "seed": int(record["seed"]),
        "same_processed_inputs_array_equal": True,
        "input_sample_count": len(vgrf_views[0]),
        "view_count": len(vgrf_views),
        "artifact_bytes": {
            name: int(manifest["deployment_artifact_bytes"])
            for name, manifest in manifests.items()
        },
        "benchmark": result,
        "scores_npz_only_postprocessing_used": False,
        "unknown_or_test_labels_used": False,
        "source_capture_manifest_sha256": {
            name: file_hash(roots[name] / "capture_manifest.json")
            for name in roots
        },
        "hardware": hardware(),
        "exclusive_machine_gate_passed_before_matrix": True,
    }
    value["manifest_sha256"] = canonical_hash(value)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
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
            "strict_v4_vgrf_selected_system_benchmark_state_v1"
        ),
        "state": state,
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "expected_blocks": 204,
        "completed_blocks": len(completed),
        "blocks": completed,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    args = parser.parse_args()
    protocol = load(args.protocol)
    if (
        protocol.get("schema_version")
        != "strict_v4_vgrf_selected_system_execution_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("invalid selected-system execution protocol")
    active = Path(__file__).resolve()
    if protocol.get("implementation_sha256", {}).get(
        active.name
    ) != file_hash(active):
        raise ValueError("active benchmark implementation SHA mismatch")
    records = [
        item
        for item in protocol["source_registry"]
        if int(item["seed"]) in (311, 313)
    ]
    if len(records) != 204:
        raise ValueError("runtime benchmark requires 204 selection blocks")
    active = active_gpu_processes()
    if active:
        raise RuntimeError(
            "exclusive GPU gate failed before benchmark: "
            + "; ".join(active)
        )
    completed: list[dict[str, Any]] = []
    write_state(
        args.state, protocol=protocol, completed=completed, state="running"
    )
    for record in records:
        output = (
            args.output_root
            / record["suite"]
            / f"{record['scenario']}_seed{record['seed']}.json"
        )
        if output.is_file():
            value = load(output)
            if (
                value.get("protocol_manifest_sha256")
                != protocol["manifest_sha256"]
                or value.get("manifest_sha256")
                != canonical_hash(value)
            ):
                raise ValueError(
                    "existing runtime block protocol or manifest mismatch"
                )
        else:
            value = benchmark_record(record, protocol, output)
        completed.append(
            {
                "suite": record["suite"],
                "scenario": record["scenario"],
                "seed": int(record["seed"]),
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
            f"benchmarked {record['suite']}/{record['scenario']}_seed"
            f"{record['seed']}",
            flush=True,
        )
    write_state(
        args.state,
        protocol=protocol,
        completed=completed,
        state="complete",
    )
    (args.state.parent / "runtime_benchmark_complete").touch()


if __name__ == "__main__":
    main()
