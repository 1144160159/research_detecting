#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


HEX64 = set("0123456789abcdef")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hex64(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and set(value).issubset(HEX64)
    )


def number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    parsed = float(value)
    return parsed if math.isfinite(parsed) else None


def integer(value: object) -> int | None:
    return value if type(value) is int and value >= 0 else None


def append_once(errors: list[str], value: str) -> None:
    if value not in errors:
        errors.append(value)


def restoration_ledger_is_complete(
    contract: dict[str, Any], ledger: object
) -> tuple[bool, list[str]]:
    if not isinstance(ledger, list):
        return False, []
    names = [item.get("step") for item in ledger if isinstance(item, dict)]
    if len(names) != len(ledger):
        return False, names
    expected_prefix = [
        "child_stopped",
        f"bind_{contract.get('capture_pci')}_bnx2x",
        f"bind_{contract.get('replay_pci')}_bnx2x",
        "netdevs_reappeared",
        f"restore_{contract.get('capture_interface')}",
        f"restore_{contract.get('replay_interface')}",
        "runtime_prefix_removed",
        "hugepage_count_restored",
    ]
    expected_suffix = ["restored_snapshot_collection", "final_state_verification"]
    structure_valid = (
        len(names) == 13
        and names[:8] == expected_prefix
        and names[8] in {"hugetlb_unmounted", "hugetlb_mount_preserved"}
        and names[9]
        in {"uio_pci_generic_unloaded", "uio_pci_generic_preserved"}
        and names[10] in {"uio_unloaded", "uio_preserved"}
        and names[11:] == expected_suffix
        and len(set(names)) == len(names)
    )
    entries_valid = all(
        isinstance(item, dict)
        and type(item.get("status")) is int
        and item["status"] == 0
        and item.get("ok") is True
        for item in ledger
    )
    return structure_valid and entries_valid, names


def validate(
    contract: dict[str, Any],
    result: dict[str, Any],
    *,
    contract_sha256: str,
    runner_sha256: str,
    validator_sha256: str,
    binary_sha256: str,
    cpu_preflight_sha256: str,
    dpdk_preflight_sha256: str,
    cpu_preflight_result_sha256: str,
    dpdk_preflight_result_sha256: str,
    build_manifest_sha256: str,
    bnx2x_ethdev_sha256: str,
    build_manifest_text: str,
    cpu_preflight: dict[str, Any],
    dpdk_preflight: dict[str, Any],
    pre_mutation_gate: object,
    pre_mutation_gate_sha256: str,
    restoration_ledger: object,
    original_exit_status: int,
    restoration_claim: bool,
) -> dict[str, Any]:
    errors: list[str] = []
    cpu_preflight_is_dict = isinstance(cpu_preflight, dict)
    dpdk_preflight_is_dict = isinstance(dpdk_preflight, dict)
    cpu_preflight = cpu_preflight if cpu_preflight_is_dict else {}
    dpdk_preflight = dpdk_preflight if dpdk_preflight_is_dict else {}
    cpu_contract = contract.get("cpu_preflight")
    cpu_contract = cpu_contract if isinstance(cpu_contract, dict) else {}
    main_cpu = integer(contract.get("main_cpu"))
    rx_cpus = contract.get("rx_cpus")
    tx_cpus = contract.get("tx_cpus")
    cpu_shape_valid = (
        main_cpu is not None
        and isinstance(rx_cpus, list)
        and isinstance(tx_cpus, list)
        and len(rx_cpus) == 2
        and len(tx_cpus) == 2
        and all(integer(cpu) is not None for cpu in rx_cpus + tx_cpus)
        and len(set([main_cpu] + rx_cpus + tx_cpus)) == 5
    )
    required_contract = (
        contract.get("schema_version") == 1
        and contract.get("scope") == "dpdk_stock_bnx2x_tcp_rss_q2_diagnostic"
        and contract.get("execution_mode") == "one_shot_fail_closed"
        and contract.get("frozen") is True
        and contract.get("diagnostic_only") is True
        and contract.get("final_pareto_ingestion_allowed") is False
        and contract.get("traffic_profile") == "ipv4_tcp_multiflow"
        and contract.get("rust_traffic_profile") == "tcp-rss-diagnostic"
        and contract.get("queue_count") == 2
        and contract.get("min_per_queue_packet_fraction") == 0.40
        and contract.get("capture_port_queues") == {"rx": 2, "tx": 2}
        and contract.get("replay_port_queues") == {"rx": 2, "tx": 2}
        and contract.get("target_load_mpps") == 1.0
        and contract.get("duration_seconds") == 15
        and contract.get("min_run_duration_s") == 15
        and contract.get("frame_size_bytes") == 64
        and contract.get("burst_size") == 128
        and contract.get("synthetic_flow_count") == 256
        and contract.get("timestamp_offset_bytes") == 54
        and cpu_shape_valid
        and contract.get("q4_allowed") is False
        and contract.get("q2_failure_stops_branch") is True
    )
    if not required_contract:
        append_once(errors, "contract_schema")
    if contract.get("binary_freeze_pending") is not False:
        append_once(errors, "binary_freeze_pending")

    identity_fields = {
        "runner": runner_sha256,
        "validator": validator_sha256,
        "binary": binary_sha256,
        "cpu_preflight": cpu_preflight_sha256,
        "dpdk_preflight": dpdk_preflight_sha256,
        "dpdk_build_manifest": build_manifest_sha256,
        "bnx2x_ethdev": bnx2x_ethdev_sha256,
    }
    expected = {
        "runner": contract.get("expected_runner_sha256"),
        "validator": contract.get("expected_validator_sha256"),
        "binary": contract.get("expected_binary_sha256"),
        "cpu_preflight": contract.get("expected_cpu_preflight_sha256"),
        "dpdk_preflight": contract.get("expected_dpdk_preflight_sha256"),
        "dpdk_build_manifest": contract.get(
            "expected_dpdk_build_manifest_sha256"
        ),
        "bnx2x_ethdev": contract.get("expected_bnx2x_ethdev_sha256"),
    }
    for name, value in expected.items():
        if not hex64(value) or identity_fields[name] != value:
            append_once(errors, f"identity.{name}")

    pre_mutation_gate_valid = (
        isinstance(pre_mutation_gate, dict)
        and pre_mutation_gate.get("scope")
        == "dpdk_stock_bnx2x_tcp_rss_q2_pre_mutation_gate"
        and pre_mutation_gate.get("mutations_performed") is False
        and pre_mutation_gate.get("exact_dpdk_process_gate_clear") is True
        and pre_mutation_gate.get("exact_dpdk_runtime_gate_clear") is True
        and pre_mutation_gate.get("frozen_and_source_artifact_rehash_verified")
        is True
        and pre_mutation_gate.get("passed") is True
        and pre_mutation_gate.get("frozen_artifact_sha256")
        == {
            "contract": contract_sha256,
            "runner": runner_sha256,
            "validator": validator_sha256,
            "binary": binary_sha256,
            "cpu_preflight_script": cpu_preflight_sha256,
            "dpdk_preflight_script": dpdk_preflight_sha256,
            "dpdk_build_manifest": build_manifest_sha256,
            "bnx2x_ethdev": bnx2x_ethdev_sha256,
        }
    )
    if not pre_mutation_gate_valid:
        append_once(errors, "pre_mutation_gate")

    manifest = {}
    for line in build_manifest_text.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            manifest[key] = value
    if manifest.get("experimental_bnx2x_rss") != "NO":
        append_once(errors, "stock_manifest.experimental_bnx2x_rss")
    if manifest.get("bnx2x_ethdev_sha256") != bnx2x_ethdev_sha256:
        append_once(errors, "stock_manifest.bnx2x_ethdev")

    if (
        result.get("schema_version") != 5
        or result.get("scope") != "r0_dpdk_bnx2x_capture_only"
        or result.get("backend") != "dpdk_bnx2x_stock_tcp_rss_diagnostic"
        or result.get("candidate_id") != contract.get("candidate_id")
        or result.get("frozen_thresholds_sha256") != contract_sha256
        or result.get("traffic_profile") != "tcp_rss_diagnostic"
        or result.get("synthetic_flow_count") != 256
        or result.get("ip_protocol") != 6
        or result.get("port_configuration")
        != "stock_bnx2x_implicit_tcp_rss_mq_none_hf_zero"
        or result.get("queue_count") != 2
        or result.get("target_mpps") != 1.0
        or result.get("frame_size_bytes") != 64
        or result.get("burst_size") != contract.get("burst_size")
        or result.get("realtime_priority") != contract.get("realtime_priority")
        or result.get("main_cpu") != contract.get("main_cpu")
        or result.get("rx_cpus") != contract.get("rx_cpus")
        or result.get("tx_cpus") != contract.get("tx_cpus")
        or result.get("capture_pci") != contract.get("capture_pci")
        or result.get("replay_pci") != contract.get("replay_pci")
        or result.get("timestamp_offset_bytes") != 54
        or result.get("max_end_to_end_p99_us")
        != contract.get("max_end_to_end_p99_us")
        or result.get("max_end_to_end_p999_us")
        != contract.get("max_end_to_end_p999_us")
        or result.get("r0_capture_only_qualified") is not False
        or result.get("full_pipeline_qualified") is not False
        or result.get("final_pareto_ingestion_allowed") is not False
    ):
        append_once(errors, "result_contract")

    tx_queues = result.get("tx_queue_packets")
    rx_queues = result.get("rx_queue_packets")
    min_queue_fraction = number(contract.get("min_per_queue_packet_fraction"))
    offered_for_coverage = integer(result.get("offered_packets"))
    received_for_coverage = integer(result.get("received_packets"))
    if not (
        isinstance(tx_queues, list)
        and len(tx_queues) == 2
        and all(integer(item) is not None and item > 0 for item in tx_queues)
        and min_queue_fraction is not None
        and offered_for_coverage is not None
        and offered_for_coverage > 0
        and all(item / offered_for_coverage >= min_queue_fraction for item in tx_queues)
    ):
        append_once(errors, "tx_software_queue_coverage")
    if not (
        isinstance(rx_queues, list)
        and len(rx_queues) == 2
        and all(integer(item) is not None and item > 0 for item in rx_queues)
        and min_queue_fraction is not None
        and received_for_coverage is not None
        and received_for_coverage > 0
        and all(item / received_for_coverage >= min_queue_fraction for item in rx_queues)
    ):
        append_once(errors, "rx_software_queue_coverage")

    offered = integer(result.get("offered_packets"))
    received = integer(result.get("received_packets"))
    gap = result.get("offered_received_gap")
    tx_queue_total = (
        sum(tx_queues)
        if isinstance(tx_queues, list)
        and all(integer(item) is not None for item in tx_queues)
        else None
    )
    rx_queue_total = (
        sum(rx_queues)
        if isinstance(rx_queues, list)
        and all(integer(item) is not None for item in rx_queues)
        else None
    )
    if (
        offered is None
        or received is None
        or type(gap) is not int
        or gap != 0
        or offered != received
        or tx_queue_total != offered
        or rx_queue_total != received
    ):
        append_once(errors, "packet_conservation")

    target = number(contract.get("target_load_mpps"))
    tx_min = number(result.get("observed_tx_mpps_min_1s"))
    rx_min = number(result.get("observed_rx_mpps_min_1s"))
    windows = integer(contract.get("min_rate_full_windows"))
    min_duration = number(contract.get("min_run_duration_s"))
    duration = number(result.get("duration_s"))
    tx_windows = integer(result.get("tx_rate_full_windows"))
    rx_windows = integer(result.get("rx_rate_full_windows"))
    achieved_tx = number(result.get("achieved_tx_mpps"))
    achieved_rx = number(result.get("achieved_rx_mpps"))
    contract_duration = number(contract.get("duration_seconds"))
    derived_tx = (
        offered / duration / 1_000_000.0
        if offered is not None and duration is not None and duration > 0
        else None
    )
    derived_rx_contract_window = (
        received / contract_duration / 1_000_000.0
        if received is not None
        and contract_duration is not None
        and contract_duration > 0
        else None
    )
    if (
        target is None
        or tx_min is None
        or rx_min is None
        or tx_min < target
        or rx_min < target
        or windows is None
        or tx_windows is None
        or rx_windows is None
        or tx_windows < windows
        or rx_windows < windows
        or tx_windows != rx_windows
        or duration is None
        or min_duration is None
        or duration < min_duration
        or result.get("rate_window_alignment")
        != contract.get("rate_window_alignment")
        or achieved_tx is None
        or achieved_rx is None
        or derived_tx is None
        or derived_rx_contract_window is None
        or not math.isclose(achieved_tx, derived_tx, rel_tol=1e-9, abs_tol=1e-9)
        or achieved_tx < target
        or derived_rx_contract_window < target
    ):
        append_once(errors, "rate_windows")

    latency = result.get("end_to_end_latency_us")
    latency = latency if isinstance(latency, dict) else {}
    observed_p99 = number(latency.get("p99"))
    observed_p999 = number(latency.get("p999"))
    latency_samples = integer(latency.get("samples"))
    max_p99 = number(contract.get("max_end_to_end_p99_us"))
    max_p999 = number(contract.get("max_end_to_end_p999_us"))
    sampling = contract.get("latency_sampling")
    sampling = sampling if isinstance(sampling, dict) else {}
    if (
        observed_p99 is None
        or max_p99 is None
        or observed_p99 > max_p99
    ):
        append_once(errors, "end_to_end_p99")
    if (
        observed_p999 is None
        or max_p999 is None
        or observed_p999 > max_p999
    ):
        append_once(errors, "end_to_end_p999")
    if (
        latency_samples is None
        or latency_samples < sampling.get("min_samples", 10_000)
        or result.get("latency_sample_stride") != sampling.get("stride_packets")
        or result.get("latency_timestamp_source") != sampling.get("timestamp_source")
    ):
        append_once(errors, "latency_evidence")

    capture = result.get("capture_stats_delta")
    replay = result.get("replay_stats_delta")
    if not isinstance(capture, dict) or any(
        integer(capture.get(name)) != 0
        for name in ("imissed", "ierrors", "rx_nombuf")
    ):
        append_once(errors, "capture_errors")
    if not isinstance(replay, dict) or integer(replay.get("oerrors")) != 0:
        append_once(errors, "replay_errors")
    if not (
        isinstance(capture, dict)
        and isinstance(replay, dict)
        and received is not None
        and offered is not None
        and integer(capture.get("ipackets")) == received
        and integer(replay.get("opackets")) == offered
    ):
        append_once(errors, "nic_packet_counters")
    if result.get("data_plane_qualified") is not True:
        append_once(errors, "raw_data_plane")
    if result.get("hard_gate_errors") != []:
        append_once(errors, "raw_hard_gate_errors")
    ledger_verified, restoration_steps = restoration_ledger_is_complete(
        contract, restoration_ledger
    )
    restoration_verified = (
        ledger_verified
        and type(restoration_claim) is bool
        and restoration_claim is True
    )
    if not ledger_verified:
        append_once(errors, "restoration_ledger")
    if restoration_claim is not ledger_verified:
        append_once(errors, "restoration_claim")
    if not restoration_verified:
        append_once(errors, "restoration")
    if type(original_exit_status) is not int or original_exit_status != 0:
        append_once(errors, "original_exit_status")
    requested_cpus = sorted([main_cpu] + rx_cpus + tx_cpus) if cpu_shape_valid else []
    cpu_threshold = number(cpu_contract.get("max_utilization"))
    cpu_maxima = cpu_preflight.get("max_observed_utilization")
    cpu_preflight_valid = (
        cpu_preflight_is_dict
        and cpu_preflight.get("scope") == "non_mutating_dpdk_cpu_idle_preflight"
        and cpu_preflight.get("passed") is True
        and cpu_preflight.get("evidence_complete") is True
        and cpu_preflight.get("mutations_performed") is False
        and cpu_preflight.get("requested_cpus") == requested_cpus
        and cpu_preflight.get("include_smt_siblings") is True
        and number(cpu_preflight.get("max_utilization_threshold")) == cpu_threshold
        and number(cpu_preflight.get("sample_seconds"))
        == number(cpu_contract.get("sample_seconds"))
        and integer(cpu_preflight.get("samples"))
        == integer(cpu_contract.get("samples"))
        and isinstance(cpu_preflight.get("observations"), list)
        and len(cpu_preflight["observations"])
        == cpu_contract.get("samples")
        and isinstance(cpu_preflight.get("effective_cpus"), list)
        and all(integer(cpu) is not None for cpu in cpu_preflight["effective_cpus"])
        and set(requested_cpus).issubset(set(cpu_preflight["effective_cpus"]))
        and isinstance(cpu_maxima, dict)
        and cpu_threshold is not None
        and all(
            number(value) is not None and number(value) <= cpu_threshold
            for value in cpu_maxima.values()
        )
    )
    if not cpu_preflight_valid:
        append_once(errors, "cpu_preflight")
    expected_ports = {
        (contract.get("capture_interface"), contract.get("capture_pci")),
        (contract.get("replay_interface"), contract.get("replay_pci")),
    }
    preflight_ports = dpdk_preflight.get("ports")
    observed_ports = (
        {(item.get("interface"), item.get("pci_address")) for item in preflight_ports}
        if isinstance(preflight_ports, list)
        and all(isinstance(item, dict) for item in preflight_ports)
        else set()
    )
    dpdk_preflight_valid = (
        dpdk_preflight_is_dict
        and dpdk_preflight.get("scope") == "read_only_dpdk_bnx2x_preflight"
        and dpdk_preflight.get("ready_for_disruptive_validation") is True
        and dpdk_preflight.get("mutations_performed") is False
        and dpdk_preflight.get("blockers") == []
        and dpdk_preflight.get("explicit_approval_required") is True
        and dpdk_preflight.get("requires_all_pf_unbind") is True
        and dpdk_preflight.get("dpdk_build_manifest_present") is True
        and dpdk_preflight.get("uio_pci_generic_available") is True
        and dpdk_preflight.get("rss_supported_by_bnx2x_pmd") is False
        and isinstance(preflight_ports, list)
        and observed_ports == expected_ports
        and len(preflight_ports) == 2
        and all(
            item.get("driver") == "bnx2x"
            and item.get("carrier") == 1
            and item.get("speed_mbps") == 10_000
            for item in preflight_ports
        )
    )
    if not dpdk_preflight_valid:
        append_once(errors, "dpdk_preflight")

    passed = not errors
    return {
        "schema_version": 1,
        "scope": "dpdk_stock_bnx2x_tcp_rss_q2_acceptance",
        "diagnostic_only": True,
        "candidate_id": contract.get("candidate_id"),
        "input_sha256": {
            "contract": contract_sha256,
            **identity_fields,
            "cpu_preflight_result": cpu_preflight_result_sha256,
            "dpdk_preflight_result": dpdk_preflight_result_sha256,
            "pre_mutation_gate": pre_mutation_gate_sha256,
        },
        "traffic_profile": "ipv4_tcp_multiflow",
        "queue_count": 2,
        "tx_software_queue_packets": tx_queues,
        "rx_software_queue_packets": rx_queues,
        "packet_conservation_verified": "packet_conservation" not in errors,
        "derived_rx_contract_window_mpps": derived_rx_contract_window,
        "reported_achieved_rx_mpps": achieved_rx,
        "observed_end_to_end_p99_us": observed_p99,
        "observed_end_to_end_p999_us": observed_p999,
        "zero_error_verified": not any(
            value in errors for value in ("capture_errors", "replay_errors")
        ),
        "rate_alignment_verified": "rate_windows" not in errors,
        "nic_packet_counters_verified": "nic_packet_counters" not in errors,
        "restoration_verified": restoration_verified,
        "restoration_claim": restoration_claim,
        "restoration_steps": restoration_steps,
        "original_exit_status": original_exit_status,
        "cpu_preflight_qualified": "cpu_preflight" not in errors,
        "dpdk_preflight_qualified": "dpdk_preflight" not in errors,
        "pre_mutation_gate_qualified": "pre_mutation_gate" not in errors,
        "diagnostic_passed": passed,
        "q2_5m_unlocked": passed,
        "q4_unlocked": False,
        "q2_failure_stops_branch": not passed,
        "r0_capture_only_qualified": False,
        "resource_gate_evaluated": False,
        "full_pipeline_qualified": False,
        "final_pareto_ingestion_allowed": False,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--validator", type=Path, required=True)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--dpdk-build-manifest", type=Path, required=True)
    parser.add_argument("--bnx2x-ethdev", type=Path, required=True)
    parser.add_argument("--cpu-preflight", type=Path, required=True)
    parser.add_argument("--dpdk-preflight", type=Path, required=True)
    parser.add_argument("--cpu-preflight-script", type=Path, required=True)
    parser.add_argument("--dpdk-preflight-script", type=Path, required=True)
    parser.add_argument("--pre-mutation-gate", type=Path, required=True)
    parser.add_argument("--restoration-ledger", type=Path, required=True)
    parser.add_argument("--original-exit-status", type=int, required=True)
    parser.add_argument("--restoration-verified", choices=("true", "false"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    result = json.loads(args.result.read_text(encoding="utf-8"))
    acceptance = validate(
        contract,
        result,
        contract_sha256=sha256_file(args.contract),
        runner_sha256=sha256_file(args.runner),
        validator_sha256=sha256_file(args.validator),
        binary_sha256=sha256_file(args.binary),
        cpu_preflight_sha256=sha256_file(args.cpu_preflight_script),
        dpdk_preflight_sha256=sha256_file(args.dpdk_preflight_script),
        cpu_preflight_result_sha256=sha256_file(args.cpu_preflight),
        dpdk_preflight_result_sha256=sha256_file(args.dpdk_preflight),
        build_manifest_sha256=sha256_file(args.dpdk_build_manifest),
        bnx2x_ethdev_sha256=sha256_file(args.bnx2x_ethdev),
        build_manifest_text=args.dpdk_build_manifest.read_text(encoding="utf-8"),
        cpu_preflight=json.loads(args.cpu_preflight.read_text(encoding="utf-8")),
        dpdk_preflight=json.loads(args.dpdk_preflight.read_text(encoding="utf-8")),
        pre_mutation_gate=json.loads(
            args.pre_mutation_gate.read_text(encoding="utf-8")
        ),
        pre_mutation_gate_sha256=sha256_file(args.pre_mutation_gate),
        restoration_ledger=json.loads(
            args.restoration_ledger.read_text(encoding="utf-8")
        ),
        original_exit_status=args.original_exit_status,
        restoration_claim=args.restoration_verified == "true",
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(acceptance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(acceptance, indent=2))
    return 0 if acceptance["diagnostic_passed"] else 10


if __name__ == "__main__":
    raise SystemExit(main())
