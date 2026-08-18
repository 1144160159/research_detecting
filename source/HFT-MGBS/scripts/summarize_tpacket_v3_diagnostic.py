#!/usr/bin/env python3
"""Derive a fail-closed diagnostic receipt from TPACKET and injector evidence."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def last_counter(path: Path, name: str) -> int:
    pattern = re.compile(rf"^\s+{re.escape(name)}:\s+(\d+)\s*$")
    matches = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            matches.append(int(match.group(1)))
    if not matches:
        raise ValueError(f"counter {name!r} not found in {path}")
    return matches[-1]


def parse_irq_affinity(path: Path) -> dict:
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split("\t")
        if len(fields) != 3:
            raise ValueError(f"invalid IRQ affinity row in {path}: {line!r}")
        irq, label, affinity = fields
        values[label] = {"irq": int(irq), "affinity": affinity}
    if len(values) != 16:
        raise ValueError(f"expected 16 queue IRQ rows in {path}, got {len(values)}")
    return values


def current_setting(path: Path, heading: str) -> int:
    active = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Current hardware settings:"):
            active = True
            continue
        if active and line.startswith(f"{heading}:"):
            return int(line.split()[1])
    raise ValueError(f"current {heading} setting not found in {path}")


def named_setting(path: Path, name: str) -> int:
    pattern = re.compile(rf"^{re.escape(name)}:\s+(\d+)\s*$")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            return int(match.group(1))
    raise ValueError(f"{name} not found in {path}")


def promiscuity(path: Path) -> int:
    match = re.search(r"\bpromiscuity\s+(\d+)\b", path.read_text(encoding="utf-8"))
    if not match:
        raise ValueError(f"promiscuity not found in {path}")
    return int(match.group(1))


def proc_cpu_fraction(before_path: Path, after_path: Path) -> float:
    def counters(path: Path):
        fields = path.read_text(encoding="utf-8").split()
        if not fields or fields[0] != "cpu" or len(fields) < 5:
            raise ValueError(f"invalid aggregate /proc/stat row in {path}")
        values = [int(value) for value in fields[1:]]
        idle = values[3] + (values[4] if len(values) > 4 else 0)
        return sum(values), idle

    total_before, idle_before = counters(before_path)
    total_after, idle_after = counters(after_path)
    total_delta = total_after - total_before
    idle_delta = idle_after - idle_before
    if total_delta <= 0 or idle_delta < 0 or idle_delta > total_delta:
        raise ValueError("invalid aggregate CPU counter delta")
    return (total_delta - idle_delta) / total_delta


def kib_setting(path: Path, name: str) -> int:
    pattern = re.compile(rf"^{re.escape(name)}:\s+(\d+)\s+kB$")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            return int(match.group(1))
    raise ValueError(f"{name} not found in {path}")


def summarize(directory: Path) -> dict:
    capture = read_json(directory / "capture.json")
    injector = read_json(directory / "injector.json")
    offered = int(injector["offered_packets"])
    received = int(capture["synthetic_test_packets"])
    drops = int(capture["packet_socket_drops"])
    freezes = int(capture["packet_socket_freeze_queue_count"])
    min_mpps = capture["synthetic_rx_min_full_epoch_mpps"]
    latency = capture["packet_socket_timestamp_to_userspace_latency"]
    p99 = latency["p99_us"]
    p999 = latency["p999_us"]
    rx_discards_delta = last_counter(directory / "stats_after.txt", "rx_discards") - last_counter(
        directory / "stats_before.txt", "rx_discards"
    )
    functional = (
        offered == received
        and rx_discards_delta == 0
        and drops == 0
        and freezes == 0
        and min_mpps is not None
        and float(min_mpps) >= 1.0
    )
    latency_ok = p99 is not None and p999 is not None and float(p99) <= 100.0 and float(p999) <= 500.0
    return {
        "schema_version": 1,
        "scope": "tpacket_v3_1mpps_diagnostic_acceptance",
        "offered_packets": offered,
        "synthetic_test_packets": received,
        "offered_received_gap": offered - received,
        "rx_discards_delta": rx_discards_delta,
        "packet_socket_drops": drops,
        "packet_socket_freeze_queue_count": freezes,
        "synthetic_rx_min_full_epoch_mpps": min_mpps,
        "p99_us": p99,
        "p999_us": p999,
        "capture_functional_1mpps_qualified": functional,
        "latency_gate_qualified": latency_ok,
        "r0_capture_only_qualified": False,
        "full_pipeline_qualified": False,
        "final_pareto_ingestion_allowed": False,
    }


def summarize_pktgen(directory: Path) -> dict:
    capture = read_json(directory / "capture.json")
    result_pattern = re.compile(r"^Result: OK: \d+\([^)]*\) usec, (\d+) \(")
    pps_pattern = re.compile(r"^\s+(\d+)pps ")
    offered = 0
    offered_pps = 0
    files = sorted(directory.glob("pktgen_device_*.txt"))
    if not files:
        raise ValueError("no pktgen_device_*.txt evidence found")
    for path in files:
        lines = path.read_text(encoding="utf-8").splitlines()
        counts = []
        rates = []
        for line in lines:
            result_match = result_pattern.match(line)
            if result_match:
                counts.append(int(result_match.group(1)))
            pps_match = pps_pattern.match(line)
            if pps_match:
                rates.append(int(pps_match.group(1)))
        if len(counts) != 1 or len(rates) != 1:
            raise ValueError(f"cannot parse a unique pktgen result from {path}")
        offered += counts[0]
        offered_pps += rates[0]
    received = int(capture["synthetic_test_packets"])
    rx_discards_delta = last_counter(directory / "stats_after.txt", "rx_discards") - last_counter(
        directory / "stats_before.txt", "rx_discards"
    )
    p99 = capture["packet_socket_timestamp_to_userspace_latency"]["p99_us"]
    p999 = capture["packet_socket_timestamp_to_userspace_latency"]["p999_us"]
    return {
        "schema_version": 1,
        "scope": "tpacket_v3_pktgen_headroom_diagnostic_acceptance",
        "pktgen_devices": len(files),
        "offered_packets": offered,
        "offered_mpps_sum": offered_pps / 1_000_000.0,
        "synthetic_test_packets": received,
        "offered_received_gap": offered - received,
        "rx_discards_delta": rx_discards_delta,
        "packet_socket_drops": int(capture["packet_socket_drops"]),
        "p99_us": p99,
        "p999_us": p999,
        "loss_accounting_exact": offered - received == rx_discards_delta,
        "loss_gate_qualified": offered == received and rx_discards_delta == 0,
        "latency_gate_qualified": p99 is not None and p999 is not None and p99 <= 100 and p999 <= 500,
        "r0_capture_only_qualified": False,
        "full_pipeline_qualified": False,
        "final_pareto_ingestion_allowed": False,
    }


def summarize_breakthrough(directory: Path) -> dict:
    capture = read_json(directory / "capture.json")
    run_config = read_json(directory / "run_config.json")
    result_pattern = re.compile(r"^Result: OK: \d+\([^)]*\) usec, (\d+) \(")
    pps_pattern = re.compile(r"^\s+(\d+)pps ")
    offered = 0
    offered_pps = 0
    device_rates = []
    files = sorted(directory.glob("pktgen_device_*.txt"))
    if len(files) != 8:
        raise ValueError(f"expected 8 pktgen device reports, got {len(files)}")
    for path in files:
        counts = []
        rates = []
        for line in path.read_text(encoding="utf-8").splitlines():
            result_match = result_pattern.match(line)
            if result_match:
                counts.append(int(result_match.group(1)))
            pps_match = pps_pattern.match(line)
            if pps_match:
                rates.append(int(pps_match.group(1)))
        if len(counts) != 1 or len(rates) != 1:
            raise ValueError(f"cannot parse a unique pktgen result from {path}")
        offered += counts[0]
        offered_pps += rates[0]
        device_rates.append(rates[0])

    received = int(capture["synthetic_test_packets"])
    min_rx_mpps = capture["synthetic_rx_min_full_epoch_mpps"]
    socket_drops = int(capture["packet_socket_drops"])
    socket_freezes = int(capture["packet_socket_freeze_queue_count"])
    rx_discards_delta = last_counter(directory / "stats_after.txt", "rx_discards") - last_counter(
        directory / "stats_before.txt", "rx_discards"
    )
    p99 = capture["packet_socket_timestamp_to_userspace_latency"]["p99_us"]
    p999 = capture["packet_socket_timestamp_to_userspace_latency"]["p999_us"]

    irq_before = parse_irq_affinity(directory / "irq_affinity_before.tsv")
    irq_active = parse_irq_affinity(directory / "irq_affinity_active.tsv")
    irq_pre_restore = parse_irq_affinity(directory / "irq_affinity_pre_restore.tsv")
    irq_restored = parse_irq_affinity(directory / "irq_affinity_restored.tsv")
    expected_active = {}
    for index in range(8):
        expected_active[f"ens8f0-fp-{index}"] = str(28 + index)
        expected_active[f"ens8f1-fp-{index}"] = str(44 + index)
    irq_assignment_verified = all(
        irq_active[label]["affinity"] == affinity for label, affinity in expected_active.items()
    )
    irq_affinity_stable = irq_active == irq_pre_restore
    irq_restoration_verified = irq_before == irq_restored

    ring_before = current_setting(directory / "ring_before.txt", "RX")
    ring_restored = current_setting(directory / "ring_restored.txt", "RX")
    coalesce_before = named_setting(directory / "coalesce_before.txt", "rx-usecs")
    coalesce_restored = named_setting(directory / "coalesce_restored.txt", "rx-usecs")
    links_restored = (
        promiscuity(directory / "pre_capture_link.txt")
        == promiscuity(directory / "post_capture_link.txt")
        and promiscuity(directory / "pre_replay_link.txt")
        == promiscuity(directory / "post_replay_link.txt")
    )
    module_unloaded = not (directory / "pktgen_module_post.txt").read_text(encoding="utf-8").strip()
    runner_status_match = re.fullmatch(
        r"runner_exit_status=(\d+)\s*",
        (directory / "runner_exit_status.env").read_text(encoding="utf-8"),
    )
    if not runner_status_match:
        raise ValueError("invalid runner_exit_status.env")
    runner_exit_status = int(runner_status_match.group(1))
    restoration_verified = (
        irq_restoration_verified
        and ring_before == ring_restored
        and coalesce_before == coalesce_restored
        and links_restored
        and module_unloaded
        and runner_exit_status == 0
    )

    host_cpu_fraction = proc_cpu_fraction(
        directory / "proc_stat_before.txt", directory / "proc_stat_after.txt"
    )
    vmrss_kib = kib_setting(directory / "capture_process_status.txt", "VmRSS")
    mem_total_kib = kib_setting(directory / "meminfo_before.txt", "MemTotal")
    capture_memory_fraction = vmrss_kib / mem_total_kib
    capture_cpu_cores = float(capture["process_cpu_cores_average"])
    capture_worker_utilization = capture_cpu_cores / int(run_config["workers"])

    offered_mpps = offered_pps / 1_000_000.0
    loss_accounting_exact = offered - received == rx_discards_delta + socket_drops
    generator_gate = offered_mpps >= 12.0
    capture_rate_gate = min_rx_mpps is not None and float(min_rx_mpps) >= 12.0
    loss_gate = offered == received and rx_discards_delta == 0 and socket_drops == 0 and socket_freezes == 0
    latency_gate = p99 is not None and p999 is not None and float(p99) <= 100.0 and float(p999) <= 500.0
    resource_gate = host_cpu_fraction <= 0.85 and capture_memory_fraction <= 0.85
    r0_qualified = all(
        [
            generator_gate,
            capture_rate_gate,
            loss_gate,
            latency_gate,
            resource_gate,
            loss_accounting_exact,
            irq_assignment_verified,
            irq_affinity_stable,
            restoration_verified,
        ]
    )
    return {
        "schema_version": 1,
        "scope": "tpacket_v3_breakthrough_r0_acceptance",
        "candidate_id": run_config["candidate_id"],
        "run_config": run_config,
        "pktgen_devices": len(files),
        "offered_packets": offered,
        "offered_mpps_sum": offered_mpps,
        "per_device_pps": device_rates,
        "synthetic_test_packets": received,
        "offered_received_gap": offered - received,
        "rx_discards_delta": rx_discards_delta,
        "packet_socket_drops": socket_drops,
        "packet_socket_freeze_queue_count": socket_freezes,
        "loss_accounting_exact": loss_accounting_exact,
        "synthetic_rx_min_full_epoch_mpps": min_rx_mpps,
        "synthetic_rx_full_epoch_windows": capture["synthetic_rx_full_epoch_windows"],
        "worker_packets": [worker["synthetic_test_packets"] for worker in capture["workers"]],
        "p99_us": p99,
        "p999_us": p999,
        "capture_process_cpu_cores_average": capture_cpu_cores,
        "capture_worker_utilization_fraction": capture_worker_utilization,
        "host_cpu_fraction": host_cpu_fraction,
        "capture_vmrss_kib": vmrss_kib,
        "capture_memory_fraction": capture_memory_fraction,
        "generator_12mpps_gate_qualified": generator_gate,
        "capture_rate_12mpps_gate_qualified": capture_rate_gate,
        "loss_gate_qualified": loss_gate,
        "latency_gate_qualified": latency_gate,
        "resource_gate_qualified": resource_gate,
        "irq_assignment_verified": irq_assignment_verified,
        "irq_affinity_stable": irq_affinity_stable,
        "irq_restoration_verified": irq_restoration_verified,
        "ring_restoration_verified": ring_before == ring_restored,
        "coalesce_restoration_verified": coalesce_before == coalesce_restored,
        "links_restored": links_restored,
        "pktgen_module_unloaded": module_unloaded,
        "runner_exit_status": runner_exit_status,
        "restoration_verified": restoration_verified,
        "r0_capture_only_qualified": r0_qualified,
        "full_pipeline_qualified": False,
        "final_pareto_ingestion_allowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence_dir", type=Path)
    parser.add_argument("--pktgen", action="store_true")
    parser.add_argument("--breakthrough", action="store_true")
    args = parser.parse_args()
    if args.pktgen and args.breakthrough:
        parser.error("--pktgen and --breakthrough are mutually exclusive")
    if args.breakthrough:
        output = args.evidence_dir / "breakthrough_acceptance.json"
        receipt = summarize_breakthrough(args.evidence_dir)
    elif args.pktgen:
        output = args.evidence_dir / "pktgen_acceptance.json"
        receipt = summarize_pktgen(args.evidence_dir)
    else:
        output = args.evidence_dir / "diagnostic_acceptance.json"
        receipt = summarize(args.evidence_dir)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
