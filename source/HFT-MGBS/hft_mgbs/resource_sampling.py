"""Low-overhead resource sampling for the split inference deployment."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from .runtime_metrics import parse_nvidia_smi_sample


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_json(value: object) -> str:
    serialized = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def parse_proc_stat(line: str) -> tuple[int, int]:
    """Return parent PID and cumulative user+system clock ticks."""

    closing = line.rfind(")")
    if closing < 0:
        raise ValueError("invalid /proc stat record")
    fields = line[closing + 1 :].split()
    if len(fields) < 13:
        raise ValueError("truncated /proc stat record")
    return int(fields[1]), int(fields[11]) + int(fields[12])


def parse_proc_status(text: str) -> dict[str, object]:
    values = {}
    for line in text.splitlines():
        key, separator, raw = line.partition(":")
        if separator:
            values[key] = raw.strip()
    rss_parts = str(values.get("VmRSS", "0 kB")).split()
    return {
        "rss_bytes": int(rss_parts[0]) * 1024,
        "threads": int(values.get("Threads", "0")),
        "cpu_set": str(values.get("Cpus_allowed_list", "")),
    }


def _read_processes(proc_root: Path = Path("/proc")):
    records = {}
    for entry in proc_root.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            stat = (entry / "stat").read_text(encoding="utf-8")
            status = (entry / "status").read_text(encoding="utf-8")
            cmdline = (entry / "cmdline").read_bytes()
            parent_pid, cpu_ticks = parse_proc_stat(stat)
            parsed_status = parse_proc_status(status)
        except (FileNotFoundError, PermissionError, ProcessLookupError, ValueError):
            continue
        records[int(entry.name)] = {
            "parent_pid": parent_pid,
            "cpu_ticks": cpu_ticks,
            "rss_bytes": parsed_status["rss_bytes"],
            "threads": parsed_status["threads"],
            "cpu_set": parsed_status["cpu_set"],
            "argv": [
                item.decode("utf-8", errors="replace")
                for item in cmdline.split(b"\0")
                if item
            ],
        }
    return records


def descendant_pids(records, root_pid: int) -> set[int]:
    descendants = {root_pid}
    changed = True
    while changed:
        changed = False
        for pid, record in records.items():
            if (
                pid not in descendants
                and record["parent_pid"] in descendants
            ):
                descendants.add(pid)
                changed = True
    return descendants


def _is_python_service(argv: list[str]) -> bool:
    return (
        len(argv) >= 3
        and Path(argv[0]).name.startswith("python")
        and argv[1:3] == ["-m", "hft_mgbs.gpu_service"]
    )


def process_snapshot(manifest: Mapping[str, object]) -> dict[str, object]:
    root_pid = manifest.get("pid")
    if isinstance(root_pid, bool) or not isinstance(root_pid, int):
        raise ValueError("runtime manifest PID is invalid")
    records = _read_processes()
    if root_pid not in records:
        raise RuntimeError("runtime manifest process is not running")
    tree = descendant_pids(records, root_pid)
    service_pids = [
        pid
        for pid in tree
        if _is_python_service(records[pid]["argv"])
    ]
    if len(service_pids) != 1:
        raise RuntimeError(
            "expected exactly one Python inference service, found {}".format(
                len(service_pids)
            )
        )
    expected_cpu_set = manifest.get("cpu_set")
    service_pid = service_pids[0]
    actual_cpu_set = records[service_pid]["cpu_set"]
    if actual_cpu_set != expected_cpu_set:
        raise RuntimeError(
            "service CPU affinity mismatch: {} != {}".format(
                actual_cpu_set, expected_cpu_set
            )
        )
    live_tree = sorted(pid for pid in tree if pid in records)
    return {
        "monotonic_s": time.monotonic(),
        "root_pid": root_pid,
        "service_pid": service_pid,
        "pids": live_tree,
        "cpu_ticks": sum(records[pid]["cpu_ticks"] for pid in live_tree),
        "rss_bytes": sum(records[pid]["rss_bytes"] for pid in live_tree),
        "threads": sum(records[pid]["threads"] for pid in live_tree),
        "service_cpu_set": actual_cpu_set,
    }


def summarize_process_samples(
    samples: list[Mapping[str, object]],
    host_cpu_count: int,
    clock_ticks_per_second: int,
    host_memory_bytes: int,
) -> dict[str, object]:
    if (
        len(samples) < 2
        or host_cpu_count < 1
        or clock_ticks_per_second < 1
        or host_memory_bytes < 1
    ):
        raise ValueError("insufficient or invalid process resource samples")
    core_samples = []
    for previous, current in zip(samples, samples[1:]):
        elapsed = float(current["monotonic_s"]) - float(
            previous["monotonic_s"]
        )
        ticks = int(current["cpu_ticks"]) - int(previous["cpu_ticks"])
        if elapsed <= 0:
            raise ValueError("process sample timestamps are not increasing")
        core_samples.append(
            max(0.0, ticks) / clock_ticks_per_second / elapsed
        )
    rss_max = max(int(item["rss_bytes"]) for item in samples)
    return {
        "sample_count": len(samples),
        "cpu_cores_used_max": max(core_samples),
        "host_cpu_fraction_max": max(core_samples) / host_cpu_count,
        "rss_bytes_max": rss_max,
        "host_memory_fraction_max": rss_max / host_memory_bytes,
        "threads_max": max(int(item["threads"]) for item in samples),
        "service_pid": samples[-1]["service_pid"],
        "service_cpu_set": samples[-1]["service_cpu_set"],
        "process_tree_pid_count_max": max(
            len(item["pids"]) for item in samples
        ),
    }


def sample_gpu(gpu_index: int, service_pids: set[int]) -> dict[str, object]:
    completed = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=utilization.gpu,memory.used,memory.total",
            "--format=csv,noheader,nounits",
            "--id={}".format(gpu_index),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=3.0,
        check=True,
    )
    parsed = parse_nvidia_smi_sample(
        completed.stdout.strip().splitlines()[0]
    )
    gpu_parts = [
        item.strip()
        for item in completed.stdout.strip().splitlines()[0].split(",")
    ]
    gpu_memory_total_mib = float(gpu_parts[2])
    applications = subprocess.run(
        [
            "nvidia-smi",
            "--query-compute-apps=pid,used_memory",
            "--format=csv,noheader,nounits",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=3.0,
        check=True,
    )
    service_memory_mib = 0.0
    for line in applications.stdout.splitlines():
        parts = [item.strip() for item in line.split(",")]
        if len(parts) != 2:
            continue
        try:
            pid = int(parts[0])
            memory_mib = float(parts[1])
        except ValueError:
            continue
        if pid in service_pids:
            service_memory_mib += memory_mib
    return {
        **parsed,
        "service_gpu_process_present": service_memory_mib > 0,
        "service_gpu_memory_mib": service_memory_mib,
        "service_gpu_memory_utilization": (
            service_memory_mib / gpu_memory_total_mib
        ),
    }


class DeploymentGpuSampler:
    def __init__(
        self,
        gpu_index: int,
        service_pids: set[int],
        interval_s: float,
    ) -> None:
        self.gpu_index = gpu_index
        self.service_pids = service_pids
        self.interval_s = interval_s
        self.samples: list[dict[str, object]] = []
        self.errors: list[str] = []
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                self.samples.append(
                    sample_gpu(self.gpu_index, self.service_pids)
                )
            except (
                OSError,
                subprocess.SubprocessError,
                ValueError,
                IndexError,
            ) as exc:
                self.errors.append(
                    "gpu_sample.{}:{}".format(type(exc).__name__, exc)
                )
            self._stop.wait(self.interval_s)

    def start(self) -> None:
        if self._thread is not None:
            raise RuntimeError("deployment GPU sampler already started")
        self._thread = threading.Thread(
            target=self._run,
            name="deployment-gpu-sampler",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        if self._thread is None:
            return
        self._stop.set()
        self._thread.join(timeout=7.0)
        if self._thread.is_alive():
            self.errors.append("gpu_sample.thread_stop_timeout")


def sample_deployment_resources(
    manifest_path: Path,
    release_path: Path,
    duration_s: float,
    interval_s: float,
    gpu_interval_s: float,
    gpu_index: int = 0,
) -> dict[str, object]:
    if duration_s < 2 or not 0.05 <= interval_s <= 1:
        raise ValueError("invalid sampling duration or interval")
    if gpu_interval_s < interval_s:
        raise ValueError("GPU interval must not be below process interval")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    release = json.loads(release_path.read_text(encoding="utf-8"))
    process_samples = [process_snapshot(manifest)]
    started = time.monotonic()
    gpu_sampler = DeploymentGpuSampler(
        gpu_index,
        set(process_samples[0]["pids"]),
        gpu_interval_s,
    )
    gpu_sampler.start()
    try:
        while True:
            now = time.monotonic()
            remaining = duration_s - (now - started)
            if remaining <= 0:
                break
            time.sleep(min(interval_s, remaining))
            process_samples.append(process_snapshot(manifest))
    finally:
        gpu_sampler.stop()
    gpu_samples = gpu_sampler.samples
    errors = gpu_sampler.errors

    host_cpu_count = os.cpu_count() or 0
    clock_ticks = int(os.sysconf("SC_CLK_TCK"))
    page_size = int(os.sysconf("SC_PAGE_SIZE"))
    pages = int(os.sysconf("SC_PHYS_PAGES"))
    process_summary = summarize_process_samples(
        process_samples,
        host_cpu_count,
        clock_ticks,
        page_size * pages,
    )
    if not gpu_samples:
        errors.append("gpu_sample.missing")
        gpu_summary = {
            "sample_count": 0,
            "system_gpu_utilization_fraction_max": None,
            "system_gpu_memory_fraction_max": None,
            "service_gpu_process_present": None,
            "service_gpu_utilization_fraction_max": None,
            "service_gpu_memory_fraction_max": None,
            "service_gpu_memory_mib_max": None,
        }
    else:
        gpu_summary = {
            "sample_count": len(gpu_samples),
            "system_gpu_utilization_fraction_max": max(
                item["gpu_utilization"] for item in gpu_samples
            ),
            "system_gpu_memory_fraction_max": max(
                item["gpu_memory_utilization"] for item in gpu_samples
            ),
            "service_gpu_process_present": any(
                item["service_gpu_process_present"]
                for item in gpu_samples
            ),
            "service_gpu_utilization_fraction_max": (
                None
                if any(
                    item["service_gpu_process_present"]
                    for item in gpu_samples
                )
                else 0.0
            ),
            "service_gpu_memory_fraction_max": max(
                item["service_gpu_memory_utilization"]
                for item in gpu_samples
            ),
            "service_gpu_memory_mib_max": max(
                item["service_gpu_memory_mib"] for item in gpu_samples
            ),
        }

    limits = (
        release.get("frozen_non_live_gates") or {}
    ).get("resource_max") or {}
    checks = {
        "cpu_utilization_max": process_summary["host_cpu_fraction_max"],
        "memory_utilization_max": process_summary[
            "host_memory_fraction_max"
        ],
        "gpu_utilization_max": gpu_summary[
            "service_gpu_utilization_fraction_max"
        ],
        "gpu_memory_utilization_max": gpu_summary[
            "service_gpu_memory_fraction_max"
        ],
    }
    gate_failures = []
    for name, observed in checks.items():
        limit = limits.get(name)
        if (
            isinstance(limit, bool)
            or not isinstance(limit, (int, float))
            or isinstance(observed, bool)
            or not isinstance(observed, (int, float))
            or observed > limit
        ):
            gate_failures.append(name)
    if gpu_summary["service_gpu_process_present"] is not False:
        gate_failures.append("service_gpu_process_present")

    return {
        "schema_version": 1,
        "scope": "split_inference_node_resource_sampling",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "candidate_id": release.get("candidate_id"),
        "runtime_candidate": manifest.get("runtime_candidate"),
        "algorithm_device": "cpu",
        "gpu_required": False,
        "duration_s": time.monotonic() - started,
        "interval_s": interval_s,
        "gpu_interval_s": gpu_interval_s,
        "manifest_sha256": sha256_file(manifest_path),
        "release_config_sha256": sha256_file(release_path),
        "resource_limits_sha256": sha256_json(limits),
        "process": process_summary,
        "gpu": gpu_summary,
        "resource_limits": limits,
        "gate_failures": sorted(set(gate_failures)),
        "errors": errors,
        "accepted": not errors and not gate_failures,
        "final_pareto_ingestion_allowed": False,
    }
