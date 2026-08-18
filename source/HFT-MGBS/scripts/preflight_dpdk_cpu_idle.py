#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path


def parse_cpu_list(value: str) -> list[int]:
    cpus: set[int] = set()
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        if "-" in item:
            start_raw, end_raw = item.split("-", 1)
            start, end = int(start_raw), int(end_raw)
            if start < 0 or end < start:
                raise ValueError(f"invalid CPU range: {item}")
            cpus.update(range(start, end + 1))
        else:
            cpu = int(item)
            if cpu < 0:
                raise ValueError(f"invalid CPU: {item}")
            cpus.add(cpu)
    if not cpus:
        raise ValueError("at least one CPU is required")
    return sorted(cpus)


def parse_proc_stat(text: str) -> dict[int, tuple[int, int]]:
    counters: dict[int, tuple[int, int]] = {}
    for line in text.splitlines():
        fields = line.split()
        if not fields or not fields[0].startswith("cpu") or not fields[0][3:].isdigit():
            continue
        values = [int(value) for value in fields[1:]]
        if len(values) < 5:
            continue
        total = sum(values)
        idle = values[3] + values[4]
        counters[int(fields[0][3:])] = (total, idle)
    return counters


def utilization(
    before: tuple[int, int] | None, after: tuple[int, int] | None
) -> float | None:
    if before is None or after is None:
        return None
    total_delta = after[0] - before[0]
    idle_delta = after[1] - before[1]
    if total_delta <= 0 or idle_delta < 0 or idle_delta > total_delta:
        return None
    value = 1.0 - idle_delta / total_delta
    return min(1.0, max(0.0, value))


def sibling_cpus(cpu: int, sys_root: Path) -> list[int]:
    path = (
        sys_root
        / "devices"
        / "system"
        / "cpu"
        / f"cpu{cpu}"
        / "topology"
        / "thread_siblings_list"
    )
    return parse_cpu_list(path.read_text(encoding="utf-8").strip())


def read_counters(proc_stat: Path) -> dict[int, tuple[int, int]]:
    return parse_proc_stat(proc_stat.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cpus", required=True)
    parser.add_argument("--max-utilization", type=float, required=True)
    parser.add_argument("--sample-seconds", type=float, required=True)
    parser.add_argument("--samples", type=int, required=True)
    parser.add_argument("--include-smt-siblings", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--proc-stat", type=Path, default=Path("/proc/stat"))
    parser.add_argument("--sys-root", type=Path, default=Path("/sys"))
    args = parser.parse_args()

    requested = parse_cpu_list(args.cpus)
    if (
        not math.isfinite(args.max_utilization)
        or not 0.0 <= args.max_utilization < 1.0
        or not math.isfinite(args.sample_seconds)
        or args.sample_seconds <= 0
        or args.samples <= 0
    ):
        raise SystemExit("invalid CPU preflight threshold or sampling budget")
    effective = set(requested)
    sibling_map: dict[str, list[int]] = {}
    if args.include_smt_siblings:
        for cpu in requested:
            siblings = sibling_cpus(cpu, args.sys_root)
            sibling_map[str(cpu)] = siblings
            effective.update(siblings)
    effective_cpus = sorted(effective)
    observations: list[dict[str, object]] = []
    maxima = {cpu: 0.0 for cpu in effective_cpus}
    evidence_complete = True
    before = read_counters(args.proc_stat)
    for sample_index in range(args.samples):
        time.sleep(args.sample_seconds)
        after = read_counters(args.proc_stat)
        values: dict[str, float | None] = {}
        for cpu in effective_cpus:
            value = utilization(before.get(cpu), after.get(cpu))
            values[str(cpu)] = value
            if value is None:
                evidence_complete = False
            else:
                maxima[cpu] = max(maxima[cpu], value)
        observations.append({"sample": sample_index + 1, "utilization": values})
        before = after
    passed = evidence_complete and all(
        value <= args.max_utilization for value in maxima.values()
    )
    result = {
        "schema_version": 1,
        "scope": "non_mutating_dpdk_cpu_idle_preflight",
        "sampled_at": datetime.now(timezone.utc).isoformat(),
        "requested_cpus": requested,
        "include_smt_siblings": args.include_smt_siblings,
        "sibling_map": sibling_map,
        "effective_cpus": effective_cpus,
        "max_utilization_threshold": args.max_utilization,
        "sample_seconds": args.sample_seconds,
        "samples": args.samples,
        "observations": observations,
        "max_observed_utilization": {
            str(cpu): value for cpu, value in maxima.items()
        },
        "evidence_complete": evidence_complete,
        "passed": passed,
        "mutations_performed": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if passed else 10


if __name__ == "__main__":
    raise SystemExit(main())
