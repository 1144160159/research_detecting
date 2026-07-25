"""Runtime measurements shared by offline replay and future live capture adapters."""

from __future__ import annotations

import os
import platform
import subprocess
import threading
import time
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Mapping, Optional

from .scheduler import SchedulePlan


def percentile(values: List[float], quantile: float) -> float:
    if not values:
        return 0.0
    if not 0 <= quantile <= 1:
        raise ValueError("quantile must be in [0, 1]")
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def max_rss_bytes() -> Optional[int]:
    try:
        import resource

        value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return int(value if platform.system() == "Darwin" else value * 1024)
    except (ImportError, AttributeError):
        return None


def total_memory_bytes() -> Optional[int]:
    if hasattr(os, "sysconf") and "SC_PAGE_SIZE" in os.sysconf_names:
        try:
            return int(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES"))
        except (ValueError, OSError):
            return None
    return None


def parse_nvidia_smi_sample(line: str) -> Dict[str, float]:
    parts = [part.strip() for part in line.split(",")]
    if len(parts) != 3:
        raise ValueError("expected utilization, used memory, total memory")
    utilization, memory_used, memory_total = (float(part) for part in parts)
    if memory_total <= 0:
        raise ValueError("GPU total memory must be positive")
    return {
        "gpu_utilization": utilization / 100.0,
        "gpu_memory_utilization": memory_used / memory_total,
    }


class NvidiaSmiSampler:
    """Low-frequency system GPU sampler; records scope and failures explicitly."""

    def __init__(self, gpu_index: int = 0, interval_s: float = 0.5) -> None:
        if gpu_index < 0 or interval_s <= 0:
            raise ValueError("invalid GPU sampler configuration")
        self.gpu_index = gpu_index
        self.interval_s = interval_s
        self.samples: List[Dict[str, float]] = []
        self.errors: List[str] = []
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _sample_once(self) -> None:
        try:
            completed = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=utilization.gpu,memory.used,memory.total",
                    "--format=csv,noheader,nounits",
                    "--id={}".format(self.gpu_index),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=max(2.0, self.interval_s * 2),
                check=True,
            )
            first_line = completed.stdout.strip().splitlines()[0]
            self.samples.append(parse_nvidia_smi_sample(first_line))
        except (OSError, subprocess.SubprocessError, ValueError, IndexError) as exc:
            self.errors.append(str(exc))

    def _run(self) -> None:
        while not self._stop.is_set():
            self._sample_once()
            self._stop.wait(self.interval_s)

    def start(self) -> None:
        if self._thread is not None:
            raise RuntimeError("GPU sampler already started")
        self._thread = threading.Thread(target=self._run, name="nvidia-smi-sampler", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._thread is None:
            return
        self._stop.set()
        self._thread.join(timeout=max(3.0, self.interval_s * 3))

    def summary(self) -> Dict[str, object]:
        return {
            "scope": "system_gpu",
            "gpu_index": self.gpu_index,
            "sample_count": len(self.samples),
            "available": bool(self.samples),
            "gpu_utilization_mean": None if not self.samples else sum(item["gpu_utilization"] for item in self.samples) / len(self.samples),
            "gpu_utilization_max": None if not self.samples else max(item["gpu_utilization"] for item in self.samples),
            "gpu_memory_utilization_max": None if not self.samples else max(item["gpu_memory_utilization"] for item in self.samples),
            "errors": self.errors[:5],
        }

    def __enter__(self) -> "NvidiaSmiSampler":
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.stop()


@dataclass
class RuntimeMetricsCollector:
    batch_latencies_us: List[float] = field(default_factory=list)
    packets_processed: int = 0
    budget_overrun_count: int = 0
    estimated_budget_overrun_count: int = 0
    actual_budget_overrun_count: int = 0
    actual_optional_costs_us: List[float] = field(default_factory=list)
    actual_budget_overrun_batch_indices: List[int] = field(default_factory=list)
    tier_decision_counts: Dict[str, int] = field(
        default_factory=lambda: {"base": 0, "flow": 0, "deep": 0}
    )
    key_flow_total: int = 0
    key_flow_covered: int = 0
    key_flow_coverages: List[float] = field(default_factory=list)
    fallback_batches: int = 0
    fallback_recovery_samples_s: List[float] = field(default_factory=list)
    stage_timings_us: Dict[str, List[float]] = field(default_factory=dict)
    started_wall: float = field(default_factory=time.perf_counter)
    started_cpu: float = field(default_factory=time.process_time)

    def record(
        self,
        latency_us: float,
        packets: int,
        plan: SchedulePlan,
        fallback_recovery_s: Optional[float] = None,
        stage_timings_us: Optional[Mapping[str, float]] = None,
    ) -> None:
        self.batch_latencies_us.append(latency_us)
        self.packets_processed += packets
        self.budget_overrun_count += plan.budget_overrun_count
        self.estimated_budget_overrun_count += plan.estimated_budget_overrun_count
        self.actual_budget_overrun_count += plan.actual_budget_overrun_count
        self.actual_optional_costs_us.append(plan.actual_used_us)
        if plan.actual_budget_overrun_count:
            self.actual_budget_overrun_batch_indices.append(
                len(self.batch_latencies_us) - 1
            )
        for decision in plan.decisions:
            self.tier_decision_counts.setdefault(decision.tier, 0)
            self.tier_decision_counts[decision.tier] += 1
        self.key_flow_total += plan.key_flow_total
        self.key_flow_covered += plan.key_flow_covered
        self.key_flow_coverages.append(plan.key_flow_coverage)
        self.fallback_batches += int(plan.fallback_active)
        if fallback_recovery_s is not None:
            self.fallback_recovery_samples_s.append(fallback_recovery_s)
        for name, value in (stage_timings_us or {}).items():
            self.stage_timings_us.setdefault(name, []).append(float(value))

    def summary(self) -> Dict[str, object]:
        wall = max(1e-9, time.perf_counter() - self.started_wall)
        cpu = max(0.0, time.process_time() - self.started_cpu)
        rss = max_rss_bytes()
        total_memory = total_memory_bytes()
        stage_totals = {
            name: sum(values) for name, values in self.stage_timings_us.items()
        }
        all_stage_time = sum(stage_totals.values())
        return {
            "elapsed_s": wall,
            "process_cpu_s": cpu,
            "process_cpu_utilization_total_capacity": cpu / wall / max(1, os.cpu_count() or 1),
            "max_rss_bytes": rss,
            "memory_utilization": None if rss is None or total_memory is None else rss / total_memory,
            "packets_processed": self.packets_processed,
            "throughput_mpps": self.packets_processed / wall / 1_000_000.0,
            "batch_count": len(self.batch_latencies_us),
            "batch_latency_us": {
                "p50": percentile(self.batch_latencies_us, 0.50),
                "p95": percentile(self.batch_latencies_us, 0.95),
                "p99": percentile(self.batch_latencies_us, 0.99),
                "p999": percentile(self.batch_latencies_us, 0.999),
                "max": max(self.batch_latencies_us) if self.batch_latencies_us else 0.0,
            },
            "budget_overrun_count": self.budget_overrun_count,
            "estimated_budget_overrun_count": self.estimated_budget_overrun_count,
            "actual_budget_overrun_count": self.actual_budget_overrun_count,
            "actual_budget_overrun_batch_indices": (
                self.actual_budget_overrun_batch_indices[:20]
            ),
            "actual_optional_cost_us": {
                "p99": percentile(self.actual_optional_costs_us, 0.99),
                "max": max(self.actual_optional_costs_us)
                if self.actual_optional_costs_us
                else 0.0,
            },
            "tier_decision_counts": dict(sorted(self.tier_decision_counts.items())),
            "key_flow_total": self.key_flow_total,
            "key_flow_covered": self.key_flow_covered,
            "key_flow_coverage": 1.0 if self.key_flow_total == 0 else self.key_flow_covered / self.key_flow_total,
            "key_flow_coverage_min": min(self.key_flow_coverages)
            if self.key_flow_coverages
            else 1.0,
            "fallback_batches": self.fallback_batches,
            "fallback_recovery_s": {
                "count": len(self.fallback_recovery_samples_s),
                "max": None if not self.fallback_recovery_samples_s else max(self.fallback_recovery_samples_s),
            },
            "stage_timings": {
                name: {
                    "total_us": stage_totals[name],
                    "p99_us": percentile(values, 0.99),
                    "share": 0.0 if all_stage_time == 0 else stage_totals[name] / all_stage_time,
                }
                for name, values in sorted(self.stage_timings_us.items())
            },
        }
