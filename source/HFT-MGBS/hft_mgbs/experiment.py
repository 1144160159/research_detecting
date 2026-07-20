"""Conservative aggregation for repeated offline PCAP candidate runs."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Dict, Iterable, List, Mapping, Tuple


RESULT_NAME = re.compile(
    r"^(normal|fallback)_batch(\d+)_budget(\d+)_repeat(\d+)\.json$"
)

FINAL_MISSING_EVIDENCE = (
    "throughput_live_replay",
    "nic_packet_drop",
    "end_to_end_p99",
    "end_to_end_p999",
    "fallback_recovery",
    "quality_protocol",
)


def _maximum(values):
    present = [value for value in values if value is not None]
    return None if not present else max(present)


def _minimum(values):
    present = [value for value in values if value is not None]
    return None if not present else min(present)


def summarize_offline_runs(
    named_runs: Iterable[Tuple[str, Mapping[str, object]]],
    minimum_repeats: int = 3,
) -> Dict[str, object]:
    if minimum_repeats <= 0:
        raise ValueError("minimum_repeats must be positive")
    grouped = defaultdict(list)
    rejected_files = []
    for name, payload in named_runs:
        match = RESULT_NAME.match(name)
        if match is None:
            rejected_files.append(name)
            continue
        mode, batch_size, budget_us, repeat = match.groups()
        grouped[(mode, int(batch_size), int(budget_us))].append((int(repeat), payload))

    candidates: List[Dict[str, object]] = []
    for (mode, batch_size, budget_us), runs in sorted(grouped.items()):
        runs.sort(key=lambda item: item[0])
        repeat_ids = [item[0] for item in runs]
        payloads = [item[1] for item in runs]
        runtimes = [item["runtime"] for item in payloads]
        gpus = [item.get("gpu") or {} for item in payloads]
        scopes = [item.get("evidence_scope") or {} for item in payloads]
        cpu_max = _maximum(item.get("process_cpu_utilization_total_capacity") for item in runtimes)
        memory_max = _maximum(item.get("memory_utilization") for item in runtimes)
        gpu_max = _maximum(item.get("gpu_utilization_max") for item in gpus)
        gpu_memory_max = _maximum(item.get("gpu_memory_utilization_max") for item in gpus)
        resource_pressure = _maximum((cpu_max, memory_max, gpu_max, gpu_memory_max))
        verified = {
            key: all(bool(scope.get(key, False)) for scope in scopes)
            for key in (
                "processing_latency_verified",
                "application_budget_verified",
                "key_flow_coverage_verified",
                "gpu_resource_verified",
            )
        }
        candidates.append(
            {
                "name": "{}_batch{}_budget{}".format(mode, batch_size, budget_us),
                "mode": mode,
                "batch_size": batch_size,
                "budget_us": budget_us,
                "repeat_ids": repeat_ids,
                "repeat_count": len(runs),
                "repeat_gate_passed": len(runs) >= minimum_repeats,
                "throughput_mpps_min": _minimum(item.get("throughput_mpps") for item in runtimes),
                "p99_latency_us_max": _maximum(item["batch_latency_us"].get("p99") for item in runtimes),
                "p999_latency_us_max": _maximum(item["batch_latency_us"].get("p999") for item in runtimes),
                "cpu_utilization_max": cpu_max,
                "memory_utilization_max": memory_max,
                "gpu_utilization_max": gpu_max,
                "gpu_memory_utilization_max": gpu_memory_max,
                "resource_pressure_max": resource_pressure,
                "budget_overrun_count_max": _maximum(item.get("budget_overrun_count") for item in runtimes),
                "key_flow_coverage_min": _minimum(item.get("key_flow_coverage") for item in runtimes),
                "fallback_batches_max": _maximum(item.get("fallback_batches") for item in runtimes),
                "offline_evidence_verified": verified,
                "final_pareto_eligible": False,
                "missing_final_evidence": list(FINAL_MISSING_EVIDENCE),
            }
        )

    eligible = [item for item in candidates if item["repeat_gate_passed"]]

    def dominates(left, right):
        objectives = (
            ("throughput_mpps_min", "max"),
            ("p99_latency_us_max", "min"),
            ("resource_pressure_max", "min"),
            ("key_flow_coverage_min", "max"),
            ("budget_overrun_count_max", "min"),
        )
        no_worse = True
        better = False
        for key, direction in objectives:
            lv, rv = left[key], right[key]
            if lv is None or rv is None:
                return False
            if direction == "max":
                no_worse = no_worse and lv >= rv
                better = better or lv > rv
            else:
                no_worse = no_worse and lv <= rv
                better = better or lv < rv
        return no_worse and better

    front = [
        item["name"] for item in eligible
        if not any(dominates(other, item) for other in eligible if other is not item)
    ]
    return {
        "schema_version": 1,
        "scope": "offline_preselection_only",
        "aggregation_policy": "worst_case_across_repeats",
        "minimum_repeats": minimum_repeats,
        "candidate_count": len(candidates),
        "rejected_files": sorted(rejected_files),
        "preselection_front": sorted(front),
        "final_pareto_eligible": False,
        "candidates": candidates,
    }
