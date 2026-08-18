#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


REQUIRED_THRESHOLD_FIELDS = (
    "schema_version",
    "qualification_mode",
    "candidate_id",
    "frozen",
    "diagnostic_only",
    "target_load_mpps",
    "frame_size_bytes",
    "burst_size",
    "queue_count",
    "main_cpu",
    "rx_cpus",
    "tx_cpus",
    "realtime_priority",
    "capture_pci",
    "replay_pci",
    "expected_backend",
    "binary_freeze_pending",
    "expected_binary_sha256",
    "expected_runner_sha256",
    "expected_validator_sha256",
    "expected_composer_sha256",
    "expected_cpu_preflight_sha256",
    "expected_dpdk_preflight_sha256",
    "expected_dpdk_build_manifest_sha256",
    "hugepage_count",
    "hugepage_size_bytes",
    "hugepage_target_node_path",
    "hugepage_node_glob",
    "interface_baseline",
    "max_pipeline_drop_rate",
    "max_end_to_end_p99_us",
    "max_end_to_end_p999_us",
    "rate_window_alignment",
    "min_rate_full_windows",
    "latency_sampling",
    "cpu_preflight",
    "min_run_duration_s",
    "resource_max",
    "resource_semantics",
    "final_pareto_ingestion_allowed",
)
CPU_PATTERN = re.compile(
    r"^\s*Percent of CPU this job got:\s*([0-9]+(?:\.[0-9]+)?)%\s*$",
    re.MULTILINE,
)
RSS_PATTERN = re.compile(
    r"^\s*Maximum resident set size \(kbytes\):\s*([0-9]+)\s*$",
    re.MULTILINE,
)
ELAPSED_PATTERN = re.compile(
    r"^\s*Elapsed \(wall clock\) time \(h:mm:ss or m:ss\):\s*(\S+)\s*$",
    re.MULTILINE,
)
REQUIRED_INPUT_HASHES = (
    "thresholds",
    "result",
    "process_time",
    "hugepage_snapshot",
    "runner",
    "binary",
    "dpdk_build_manifest",
    "cpu_preflight",
    "validator",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def finite_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    converted = float(value)
    return converted if math.isfinite(converted) else None


def parse_process_time(text: str) -> dict[str, float | int | None]:
    cpu_match = CPU_PATTERN.search(text)
    rss_match = RSS_PATTERN.search(text)
    elapsed_match = ELAPSED_PATTERN.search(text)
    return {
        "process_cpu_percent": (
            float(cpu_match.group(1)) if cpu_match is not None else None
        ),
        "process_max_rss_kib": (
            int(rss_match.group(1)) if rss_match is not None else None
        ),
        "process_elapsed_s": (
            parse_elapsed_time(elapsed_match.group(1))
            if elapsed_match is not None
            else None
        ),
    }


def parse_elapsed_time(value: str) -> float | None:
    parts = value.split(":")
    try:
        if len(parts) == 2:
            minutes, seconds = int(parts[0]), float(parts[1])
            elapsed = minutes * 60.0 + seconds
        elif len(parts) == 3:
            hours, minutes, seconds = int(parts[0]), int(parts[1]), float(parts[2])
            elapsed = hours * 3600.0 + minutes * 60.0 + seconds
        else:
            return None
    except ValueError:
        return None
    return elapsed if math.isfinite(elapsed) and elapsed >= 0 else None


def append_once(errors: list[str], error: str) -> None:
    if error not in errors:
        errors.append(error)


def nonnegative_integer(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def zero_counter(value: Any) -> bool:
    return nonnegative_integer(value) == 0


def evaluate(
    thresholds: dict[str, Any],
    result: dict[str, Any] | None,
    process_time_text: str,
    hugepage_count: int,
    hugepage_size_bytes: int,
    thresholds_sha256: str,
    input_sha256: dict[str, str],
    hugepage_snapshot: dict[str, Any],
    cpu_preflight_evidence: dict[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(thresholds, dict):
        thresholds = {}
        append_once(errors, "threshold_schema")
    if not isinstance(input_sha256, dict):
        input_sha256 = {}
        append_once(errors, "evidence_binding")
    missing_thresholds = [
        field for field in REQUIRED_THRESHOLD_FIELDS if field not in thresholds
    ]
    resource_max = thresholds.get("resource_max")
    if not isinstance(resource_max, dict):
        resource_max = {}
    missing_resource_thresholds = [
        field
        for field in (
            "process_cpu_cores_average",
            "process_rss_kib",
            "process_wall_overhead_s",
            "hugepage_reserved_bytes",
        )
        if field not in resource_max
    ]
    if (
        missing_thresholds
        or missing_resource_thresholds
        or thresholds.get("schema_version") != 2
        or thresholds.get("qualification_mode") != "release_gate_v2"
        or thresholds.get("frozen") is not True
        or thresholds.get("diagnostic_only") is not True
        or thresholds.get("final_pareto_ingestion_allowed") is not False
        or finite_number(thresholds.get("max_pipeline_drop_rate")) != 0.0
    ):
        append_once(errors, "threshold_schema")
    if (
        set(input_sha256) != set(REQUIRED_INPUT_HASHES)
        or any(
            not isinstance(value, str)
            or re.fullmatch(r"[0-9a-f]{64}", value) is None
            for value in input_sha256.values()
        )
        or input_sha256.get("thresholds") != thresholds_sha256
    ):
        append_once(errors, "evidence_binding")

    candidate_id = thresholds.get("candidate_id")
    main_cpu = nonnegative_integer(thresholds.get("main_cpu"))
    rx_cpus = thresholds.get("rx_cpus")
    tx_cpus = thresholds.get("tx_cpus")
    queue_count = nonnegative_integer(thresholds.get("queue_count"))
    realtime_priority = nonnegative_integer(thresholds.get("realtime_priority"))
    hugepage_count_threshold = nonnegative_integer(thresholds.get("hugepage_count"))
    hugepage_size_threshold = nonnegative_integer(
        thresholds.get("hugepage_size_bytes")
    )
    min_rate_full_windows = nonnegative_integer(
        thresholds.get("min_rate_full_windows")
    )
    latency_sampling = thresholds.get("latency_sampling")
    latency_sampling = latency_sampling if isinstance(latency_sampling, dict) else {}
    resource_semantics = thresholds.get("resource_semantics")
    interface_baseline = thresholds.get("interface_baseline")
    interface_baseline = (
        interface_baseline if isinstance(interface_baseline, dict) else {}
    )
    cpu_preflight = thresholds.get("cpu_preflight")
    cpu_preflight = cpu_preflight if isinstance(cpu_preflight, dict) else {}
    candidate_shape_valid = (
        isinstance(candidate_id, str)
        and bool(candidate_id)
        and candidate_id.isascii()
        and all(character.isalnum() or character in "_.-" for character in candidate_id)
        and queue_count == 1
        and nonnegative_integer(thresholds.get("frame_size_bytes")) is not None
        and 64 <= thresholds.get("frame_size_bytes") <= 1500
        and nonnegative_integer(thresholds.get("burst_size")) in (64, 128, 256)
        and main_cpu is not None
        and isinstance(rx_cpus, list)
        and isinstance(tx_cpus, list)
        and len(rx_cpus) == queue_count
        and len(tx_cpus) == queue_count
        and all(nonnegative_integer(cpu) is not None for cpu in rx_cpus + tx_cpus)
        and len(set([main_cpu] + rx_cpus + tx_cpus)) == 1 + 2 * queue_count
        and realtime_priority is not None
        and realtime_priority <= 20
        and isinstance(thresholds.get("capture_pci"), str)
        and isinstance(thresholds.get("replay_pci"), str)
        and re.fullmatch(
            r"[0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-7]",
            thresholds.get("capture_pci"),
        )
        is not None
        and re.fullmatch(
            r"[0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-7]",
            thresholds.get("replay_pci"),
        )
        is not None
        and thresholds.get("capture_pci") != thresholds.get("replay_pci")
        and thresholds.get("expected_backend") == "dpdk_bnx2x_single_queue"
        and all(
            isinstance(thresholds.get(field), str)
            and re.fullmatch(r"[0-9a-f]{64}", thresholds.get(field)) is not None
            for field in (
                "expected_runner_sha256",
                "expected_validator_sha256",
                "expected_composer_sha256",
                "expected_cpu_preflight_sha256",
                "expected_dpdk_preflight_sha256",
                "expected_dpdk_build_manifest_sha256",
            )
        )
        and hugepage_count_threshold is not None
        and hugepage_count_threshold > 0
        and hugepage_size_threshold is not None
        and hugepage_size_threshold > 0
        and thresholds.get("hugepage_target_node_path")
        == "/sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages"
        and thresholds.get("hugepage_node_glob")
        == "/sys/devices/system/node/node*/hugepages/hugepages-2048kB/nr_hugepages"
        and interface_baseline.get("profile")
        == "dedicated_bnx2x_kernel_default_v1"
        and interface_baseline.get("admin_up") is True
        and nonnegative_integer(interface_baseline.get("mtu")) == 1500
        and nonnegative_integer(interface_baseline.get("txqlen")) == 1000
        and all(
            isinstance(interface_baseline.get(field), str)
            and re.fullmatch(r"[0-9a-f]{64}", interface_baseline.get(field))
            is not None
            for field in (
                "features_sha256",
                "coalesce_sha256",
                "ring_sha256",
                "channels_sha256",
                "qdisc_sha256",
            )
        )
        and thresholds.get("rate_window_alignment")
        == "shared_monotonic_epoch_fixed_1s_v1"
        and min_rate_full_windows is not None
        and min_rate_full_windows > 0
        and nonnegative_integer(latency_sampling.get("stride_packets")) == 1024
        and nonnegative_integer(latency_sampling.get("min_samples")) is not None
        and nonnegative_integer(latency_sampling.get("min_samples")) > 0
        and latency_sampling.get("timestamp_source")
        == "dpdk_tsc_embedded_tx_rx_v1"
        and resource_semantics
        == {
            "process_cpu_cores_average": "gnu_time_cpu_percent_div_100",
            "process_rss_kib": "gnu_time_max_rss_kib",
            "process_wall_overhead_s": "gnu_time_elapsed_minus_rust_duration",
            "hugepage_reserved_bytes":
                "sysfs_all_numa_nodes_reserved_count_during_run",
        }
        and finite_number(cpu_preflight.get("max_utilization")) is not None
        and 0 <= cpu_preflight.get("max_utilization") < 1
        and finite_number(cpu_preflight.get("sample_seconds")) is not None
        and cpu_preflight.get("sample_seconds") > 0
        and nonnegative_integer(cpu_preflight.get("samples")) is not None
        and cpu_preflight.get("samples") > 0
        and cpu_preflight.get("include_smt_siblings") is True
    )
    if not candidate_shape_valid:
        append_once(errors, "threshold_schema")

    target_mpps = finite_number(thresholds.get("target_load_mpps"))
    max_p99 = finite_number(thresholds.get("max_end_to_end_p99_us"))
    max_p999 = finite_number(thresholds.get("max_end_to_end_p999_us"))
    min_duration = finite_number(thresholds.get("min_run_duration_s"))
    max_cpu_cores = finite_number(resource_max.get("process_cpu_cores_average"))
    max_rss_kib = finite_number(resource_max.get("process_rss_kib"))
    max_wall_overhead_s = finite_number(
        resource_max.get("process_wall_overhead_s")
    )
    max_hugepage_bytes = finite_number(resource_max.get("hugepage_reserved_bytes"))
    positive_numeric_thresholds = (
        target_mpps,
        max_p99,
        max_p999,
        min_duration,
        max_cpu_cores,
        max_rss_kib,
        max_hugepage_bytes,
    )
    if any(value is None or value <= 0 for value in positive_numeric_thresholds):
        append_once(errors, "threshold_schema")
    if max_wall_overhead_s is None or max_wall_overhead_s < 0:
        append_once(errors, "threshold_schema")
    if (
        min_duration is not None
        and min_rate_full_windows is not None
        and min_rate_full_windows != math.ceil(min_duration)
    ):
        append_once(errors, "threshold_schema")
    if (
        max_p99 is not None
        and max_p999 is not None
        and max_p999 < max_p99
    ):
        append_once(errors, "threshold_schema")
    if (
        hugepage_count_threshold is not None
        and hugepage_size_threshold is not None
        and max_hugepage_bytes is not None
        and hugepage_count_threshold * hugepage_size_threshold > max_hugepage_bytes
    ):
        append_once(errors, "threshold_schema")

    process_usage = parse_process_time(process_time_text)
    process_cpu_percent = finite_number(process_usage["process_cpu_percent"])
    process_rss_kib = finite_number(process_usage["process_max_rss_kib"])
    process_elapsed_s = finite_number(process_usage["process_elapsed_s"])
    hugepage_reserved_bytes = hugepage_count * hugepage_size_bytes
    if not isinstance(hugepage_snapshot, dict):
        hugepage_snapshot = {}
    nodes_before = hugepage_snapshot.get("nodes_before")
    nodes_during = hugepage_snapshot.get("nodes_during")
    nodes_before = nodes_before if isinstance(nodes_before, list) else []
    nodes_during = nodes_during if isinstance(nodes_during, list) else []

    def node_count_map(entries: list[Any]) -> dict[str, int] | None:
        counts: dict[str, int] = {}
        for entry in entries:
            if not isinstance(entry, dict):
                return None
            path = entry.get("path")
            count = nonnegative_integer(entry.get("count"))
            if not isinstance(path, str) or not path or count is None or path in counts:
                return None
            counts[path] = count
        return counts if counts else None

    before_counts = node_count_map(nodes_before)
    during_counts = node_count_map(nodes_during)
    target_node_path = thresholds.get("hugepage_target_node_path")
    global_count_before = nonnegative_integer(
        hugepage_snapshot.get("global_count_before")
    )
    global_count_during = nonnegative_integer(
        hugepage_snapshot.get("global_count_during")
    )
    if (
        hugepage_snapshot.get("schema_version") != 2
        or hugepage_snapshot.get("source")
        != "sysfs_all_numa_nodes_reserved_hugepages"
        or hugepage_snapshot.get("node_glob")
        != thresholds.get("hugepage_node_glob")
        or hugepage_snapshot.get("target_node_path") != target_node_path
        or not isinstance(hugepage_snapshot.get("sampled_at"), str)
        or not hugepage_snapshot.get("sampled_at")
        or before_counts is None
        or during_counts is None
        or set(before_counts) != set(during_counts)
        or target_node_path not in (before_counts or {})
        or any(count != 0 for count in (before_counts or {}).values())
        or global_count_before != 0
        or global_count_before != sum((before_counts or {}).values())
        or global_count_during != hugepage_count
        or global_count_during != sum((during_counts or {}).values())
        or (during_counts or {}).get(target_node_path) != hugepage_count
        or any(
            count != 0
            for path, count in (during_counts or {}).items()
            if path != target_node_path
        )
        or hugepage_snapshot.get("page_size_bytes") != hugepage_size_bytes
    ):
        append_once(errors, "hugepage_evidence")
    if (
        process_cpu_percent is None
        or process_rss_kib is None
        or process_elapsed_s is None
        or process_cpu_percent < 0
        or process_rss_kib <= 0
        or hugepage_count < 0
        or hugepage_size_bytes <= 0
    ):
        append_once(errors, "resource_evidence_incomplete")
    if (
        hugepage_count_threshold is None
        or hugepage_size_threshold is None
        or hugepage_count != hugepage_count_threshold
        or hugepage_size_bytes != hugepage_size_threshold
    ):
        append_once(errors, "hugepage_identity")
    if (
        process_cpu_percent is not None
        and max_cpu_cores is not None
        and process_cpu_percent > max_cpu_cores * 100.0
    ):
        append_once(errors, "process_cpu_resource")
    if (
        process_rss_kib is not None
        and max_rss_kib is not None
        and process_rss_kib > max_rss_kib
    ):
        append_once(errors, "process_rss_resource")
    if (
        max_hugepage_bytes is not None
        and hugepage_reserved_bytes > max_hugepage_bytes
    ):
        append_once(errors, "hugepage_resource")

    if not isinstance(cpu_preflight_evidence, dict):
        cpu_preflight_evidence = {}
    requested_cpus = sorted([main_cpu] + rx_cpus + tx_cpus) if candidate_shape_valid else []
    observed_cpu_maxima = cpu_preflight_evidence.get("max_observed_utilization")
    observed_cpu_maxima = (
        observed_cpu_maxima if isinstance(observed_cpu_maxima, dict) else {}
    )
    cpu_values = [
        finite_number(value) for value in observed_cpu_maxima.values()
    ]
    effective_cpus = cpu_preflight_evidence.get("effective_cpus")
    if (
        cpu_preflight_evidence.get("schema_version") != 1
        or cpu_preflight_evidence.get("scope")
        != "non_mutating_dpdk_cpu_idle_preflight"
        or cpu_preflight_evidence.get("requested_cpus") != requested_cpus
        or not isinstance(effective_cpus, list)
        or not set(requested_cpus).issubset(
            {
                cpu
                for cpu in effective_cpus
                if nonnegative_integer(cpu) is not None
            }
        )
        or any(str(cpu) not in observed_cpu_maxima for cpu in requested_cpus)
        or cpu_preflight_evidence.get("include_smt_siblings") is not True
        or cpu_preflight_evidence.get("max_utilization_threshold")
        != cpu_preflight.get("max_utilization")
        or cpu_preflight_evidence.get("sample_seconds")
        != cpu_preflight.get("sample_seconds")
        or cpu_preflight_evidence.get("samples") != cpu_preflight.get("samples")
        or cpu_preflight_evidence.get("evidence_complete") is not True
        or cpu_preflight_evidence.get("passed") is not True
        or cpu_preflight_evidence.get("mutations_performed") is not False
        or len(cpu_values) < len(requested_cpus)
        or any(value is None for value in cpu_values)
        or any(
            value > cpu_preflight.get("max_utilization")
            for value in cpu_values
            if value is not None
        )
    ):
        append_once(errors, "cpu_preflight_evidence")

    if result is not None and not isinstance(result, dict):
        append_once(errors, "result_schema")
        result = {}
    if result is None:
        append_once(errors, "result_missing")
        result = {}
    if result.get("schema_version") != 5:
        append_once(errors, "result_schema")
    if (
        result.get("scope") != "r0_dpdk_bnx2x_capture_only"
        or result.get("backend") != thresholds.get("expected_backend")
        or result.get("data_plane_qualified") is not True
        or result.get("resource_gate_evaluated") is not False
        or result.get("r0_capture_only_qualified") is not False
        or result.get("full_pipeline_qualified") is not False
        or result.get("final_pareto_ingestion_allowed") is not False
    ):
        append_once(errors, "result_schema")
    if result.get("candidate_id") != thresholds.get("candidate_id"):
        append_once(errors, "candidate_identity")
    if result.get("frozen_thresholds_sha256") != thresholds_sha256:
        append_once(errors, "threshold_identity")
    if (
        thresholds.get("binary_freeze_pending") is not False
        or input_sha256.get("binary") != thresholds.get("expected_binary_sha256")
        or input_sha256.get("runner") != thresholds.get("expected_runner_sha256")
        or input_sha256.get("validator") != thresholds.get("expected_validator_sha256")
        or input_sha256.get("dpdk_build_manifest")
        != thresholds.get("expected_dpdk_build_manifest_sha256")
    ):
        append_once(errors, "artifact_identity")
    identity_pairs = (
        ("target_mpps", "target_load_mpps"),
        ("frame_size_bytes", "frame_size_bytes"),
        ("burst_size", "burst_size"),
        ("queue_count", "queue_count"),
        ("main_cpu", "main_cpu"),
        ("rx_cpus", "rx_cpus"),
        ("tx_cpus", "tx_cpus"),
        ("realtime_priority", "realtime_priority"),
        ("capture_pci", "capture_pci"),
        ("replay_pci", "replay_pci"),
        ("max_end_to_end_p99_us", "max_end_to_end_p99_us"),
        ("max_end_to_end_p999_us", "max_end_to_end_p999_us"),
    )
    for result_key, threshold_key in identity_pairs:
        if result.get(result_key) != thresholds.get(threshold_key):
            append_once(errors, "candidate_identity")

    observed_tx = finite_number(result.get("observed_tx_mpps_min_1s"))
    observed_rx = finite_number(result.get("observed_rx_mpps_min_1s"))
    duration = finite_number(result.get("duration_s"))
    latency = result.get("end_to_end_latency_us")
    latency = latency if isinstance(latency, dict) else {}
    observed_p99 = finite_number(latency.get("p99"))
    observed_p999 = finite_number(latency.get("p999"))
    if (
        process_elapsed_s is None
        or duration is None
        or max_wall_overhead_s is None
        or process_elapsed_s + 0.1 < duration
        or process_elapsed_s > duration + max_wall_overhead_s
    ):
        append_once(errors, "process_wall_time")
    tx_rate_full_windows = nonnegative_integer(result.get("tx_rate_full_windows"))
    rx_rate_full_windows = nonnegative_integer(result.get("rx_rate_full_windows"))
    if (
        result.get("rate_window_alignment")
        != thresholds.get("rate_window_alignment")
        or min_rate_full_windows is None
        or tx_rate_full_windows is None
        or rx_rate_full_windows is None
        or tx_rate_full_windows < min_rate_full_windows
        or rx_rate_full_windows < min_rate_full_windows
    ):
        append_once(errors, "rate_window_evidence")
    if target_mpps is None or observed_tx is None or observed_tx < target_mpps:
        append_once(errors, "tx_target_load")
    if target_mpps is None or observed_rx is None or observed_rx < target_mpps:
        append_once(errors, "rx_target_load")
    if min_duration is None or duration is None or duration < min_duration:
        append_once(errors, "duration")
    offered_packets = nonnegative_integer(result.get("offered_packets"))
    received_packets = nonnegative_integer(result.get("received_packets"))
    if (
        offered_packets is None
        or received_packets is None
        or offered_packets == 0
        or received_packets == 0
        or offered_packets != received_packets
        or not zero_counter(result.get("offered_received_gap"))
    ):
        append_once(errors, "offered_received_mismatch")
    capture_stats = result.get("capture_stats_delta")
    capture_stats = capture_stats if isinstance(capture_stats, dict) else {}
    if any(
        not zero_counter(capture_stats.get(field))
        for field in ("imissed", "ierrors", "rx_nombuf")
    ):
        append_once(errors, "capture_drop")
    replay_stats = result.get("replay_stats_delta")
    replay_stats = replay_stats if isinstance(replay_stats, dict) else {}
    if not zero_counter(replay_stats.get("oerrors")):
        append_once(errors, "replay_tx_error")
    latency_samples = nonnegative_integer(latency.get("samples"))
    latency_min_samples = nonnegative_integer(latency_sampling.get("min_samples"))
    if (
        latency_samples is None
        or latency_min_samples is None
        or latency_samples < latency_min_samples
        or result.get("latency_sample_stride")
        != latency_sampling.get("stride_packets")
        or result.get("latency_timestamp_source")
        != latency_sampling.get("timestamp_source")
    ):
        append_once(errors, "latency_evidence_incomplete")
    if max_p99 is None or observed_p99 is None or observed_p99 > max_p99:
        append_once(errors, "end_to_end_p99")
    if max_p999 is None or observed_p999 is None or observed_p999 > max_p999:
        append_once(errors, "end_to_end_p999")
    rust_errors = result.get("hard_gate_errors")
    if not isinstance(rust_errors, list) or rust_errors:
        append_once(errors, "rust_gate")
    if result.get("data_plane_qualified") is not True:
        append_once(errors, "rust_gate")

    return {
        "schema_version": 1,
        "scope": "dpdk_release_gate_acceptance",
        "candidate_id": thresholds.get("candidate_id"),
        "qualification_mode": thresholds.get("qualification_mode"),
        "frozen_thresholds_sha256": thresholds_sha256,
        "performance_gate_frozen": "threshold_schema" not in errors,
        "resource_gate_frozen": "threshold_schema" not in errors,
        "observed": {
            "tx_mpps_min_1s": observed_tx,
            "rx_mpps_min_1s": observed_rx,
            "duration_s": duration,
            "end_to_end_p99_us": observed_p99,
            "end_to_end_p999_us": observed_p999,
            "process_cpu_percent": process_cpu_percent,
            "process_max_rss_kib": process_rss_kib,
            "process_elapsed_s": process_elapsed_s,
            "process_wall_overhead_s": (
                process_elapsed_s - duration
                if process_elapsed_s is not None and duration is not None
                else None
            ),
            "hugepage_reserved_bytes": hugepage_reserved_bytes,
            "hugepage_count": hugepage_count,
            "hugepage_size_bytes": hugepage_size_bytes,
        },
        "thresholds": {
            "target_load_mpps": target_mpps,
            "max_end_to_end_p99_us": max_p99,
            "max_end_to_end_p999_us": max_p999,
            "min_run_duration_s": min_duration,
            "resource_max": {
                "process_cpu_cores_average": max_cpu_cores,
                "process_rss_kib": max_rss_kib,
                "process_wall_overhead_s": max_wall_overhead_s,
                "hugepage_reserved_bytes": max_hugepage_bytes,
            },
        },
        "input_sha256": input_sha256,
        "resource_semantics": resource_semantics,
        "cpu_preflight": cpu_preflight,
        "cpu_preflight_observed_max": observed_cpu_maxima,
        "errors": errors,
        "data_resource_qualified": not errors,
        "runner_qualified": False,
        "r0_capture_only_qualified": False,
        "full_pipeline_qualified": False,
        "final_pareto_ingestion_allowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--thresholds", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--process-time", type=Path, required=True)
    parser.add_argument("--hugepage-snapshot", type=Path, required=True)
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--dpdk-build-manifest", type=Path, required=True)
    parser.add_argument("--cpu-preflight", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    thresholds = json.loads(args.thresholds.read_text(encoding="utf-8"))
    result = (
        json.loads(args.result.read_text(encoding="utf-8"))
        if args.result.is_file()
        else None
    )
    process_time_text = (
        args.process_time.read_text(encoding="utf-8", errors="replace")
        if args.process_time.is_file()
        else ""
    )
    hugepage_snapshot = (
        json.loads(args.hugepage_snapshot.read_text(encoding="utf-8"))
        if args.hugepage_snapshot.is_file()
        else {}
    )
    if not isinstance(hugepage_snapshot, dict):
        hugepage_snapshot = {}
    cpu_preflight_evidence = (
        json.loads(args.cpu_preflight.read_text(encoding="utf-8"))
        if args.cpu_preflight.is_file()
        else {}
    )
    if not isinstance(cpu_preflight_evidence, dict):
        cpu_preflight_evidence = {}
    evidence_paths = {
        "thresholds": args.thresholds,
        "result": args.result,
        "process_time": args.process_time,
        "hugepage_snapshot": args.hugepage_snapshot,
        "runner": args.runner,
        "binary": args.binary,
        "dpdk_build_manifest": args.dpdk_build_manifest,
        "cpu_preflight": args.cpu_preflight,
        "validator": Path(__file__).resolve(),
    }
    input_sha256 = {
        name: sha256_file(path)
        for name, path in evidence_paths.items()
        if path.is_file()
    }
    acceptance = evaluate(
        thresholds,
        result,
        process_time_text,
        nonnegative_integer(hugepage_snapshot.get("global_count_during")) or -1,
        nonnegative_integer(hugepage_snapshot.get("page_size_bytes")) or -1,
        sha256_file(args.thresholds),
        input_sha256,
        hugepage_snapshot,
        cpu_preflight_evidence,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(acceptance, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(acceptance, ensure_ascii=False, indent=2))
    return 0 if acceptance["data_resource_qualified"] else 10


if __name__ == "__main__":
    raise SystemExit(main())
