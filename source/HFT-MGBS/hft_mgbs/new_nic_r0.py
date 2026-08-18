"""Strict recomputation for the new-NIC R0 XDP/DPDK campaign.

This module consumes immutable raw receipts.  It performs no capture, NIC
binding, traffic generation, or restoration itself.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class R0ContractError(ValueError):
    pass


def canonical_sha256(value: Any) -> str:
    rendered = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(rendered).hexdigest()


def _safe_canonical_sha256(value: Any) -> Optional[str]:
    try:
        return canonical_sha256(value)
    except (TypeError, ValueError):
        return None


def receipt_content_sha256(receipt: Mapping[str, Any]) -> str:
    return canonical_sha256(
        {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    )


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip() or "\n" in value:
        raise R0ContractError(path + " must be a non-empty single-line string")
    return value


def _sha(value: Any, path: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise R0ContractError(path + " must be a lowercase SHA-256")
    return value


def _bool(value: Any, path: str) -> bool:
    if type(value) is not bool:
        raise R0ContractError(path + " must be boolean")
    return value


def _int(value: Any, path: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise R0ContractError(path + " must be an integer >= {}".format(minimum))
    return value


def _number(value: Any, path: str, minimum: float = 0.0) -> float:
    if type(value) not in (int, float):
        raise R0ContractError(path + " must be numeric")
    result = float(value)
    if not math.isfinite(result) or result < minimum:
        raise R0ContractError(path + " must be finite and >= {}".format(minimum))
    return result


def _utc(value: Any, path: str) -> datetime:
    text = _text(value, path)
    if not text.endswith("Z"):
        raise R0ContractError(path + " must use UTC Z notation")
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as exc:
        raise R0ContractError(path + " is not ISO-8601") from exc
    if parsed.tzinfo is None:
        raise R0ContractError(path + " must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise R0ContractError(path + " must be an object")
    return value


def _list(value: Any, path: str) -> List[Any]:
    if not isinstance(value, list):
        raise R0ContractError(path + " must be an array")
    return value


def _append(errors: List[str], value: str) -> None:
    if value not in errors:
        errors.append(value)


def validate_contract(contract: Mapping[str, Any]) -> None:
    if contract.get("schema_version") != 1:
        raise R0ContractError("contract.schema_version")
    if contract.get("frozen") is not True:
        raise R0ContractError("contract.frozen")
    _text(contract.get("contract_id"), "contract.contract_id")
    if contract.get("scope") != "new_high_speed_nic_r0_campaign":
        raise R0ContractError("contract.scope")
    load = _mapping(contract.get("load_gate"), "contract.load_gate")
    if _int(load.get("packet_size_bytes"), "contract.load_gate.packet_size_bytes", 1) != 64:
        raise R0ContractError("contract.load_gate.packet_size_bytes must be 64")
    _number(load.get("offered_mpps_min"), "contract.load_gate.offered_mpps_min", 12.0)
    _number(load.get("duration_seconds_min"), "contract.load_gate.duration_seconds_min", 15.0)
    if _int(load.get("xdp_primary_repeats_required"), "contract.load_gate.xdp_primary_repeats_required", 3) != 3:
        raise R0ContractError("contract requires exactly three XDP repeats")
    if _int(load.get("dpdk_fallback_repeats_required"), "contract.load_gate.dpdk_fallback_repeats_required", 3) != 3:
        raise R0ContractError("contract requires exactly three DPDK repeats")
    indices = _list(load.get("repeat_indices"), "contract.load_gate.repeat_indices")
    if indices != [1, 2, 3]:
        raise R0ContractError("contract.load_gate.repeat_indices")
    latency = _mapping(contract.get("latency_gate"), "contract.latency_gate")
    methods = _list(
        latency.get("allowed_measurement_methods"),
        "contract.latency_gate.allowed_measurement_methods",
    )
    if not methods or len(methods) != len(set(methods)) or not all(
        isinstance(item, str) and item for item in methods
    ):
        raise R0ContractError("contract.latency_gate.allowed_measurement_methods")
    _number(
        latency.get("clock_sync_error_us_max"),
        "contract.latency_gate.clock_sync_error_us_max",
    )
    _int(
        latency.get("negative_latency_samples_max"),
        "contract.latency_gate.negative_latency_samples_max",
    )
    _number(latency.get("p99_us_max"), "contract.latency_gate.p99_us_max")
    _number(latency.get("p999_us_max"), "contract.latency_gate.p999_us_max")
    resources = _mapping(contract.get("resource_gate"), "contract.resource_gate")
    _int(resources.get("samples_min_per_run"), "contract.resource_gate.samples_min_per_run", 1)
    for name in (
        "sample_interval_seconds_max",
        "host_cpu_fraction_max",
        "host_memory_fraction_max",
        "process_rss_bytes_max",
        "hugepage_reserved_bytes_max",
    ):
        _number(resources.get(name), "contract.resource_gate." + name)
    key = _mapping(contract.get("key_flow_gate"), "contract.key_flow_gate")
    coverage = _number(key.get("coverage_min_per_run"), "contract.key_flow_gate.coverage_min_per_run")
    if coverage > 1:
        raise R0ContractError("contract.key_flow_gate.coverage_min_per_run > 1")
    fallback = _mapping(contract.get("fallback_gate"), "contract.fallback_gate")
    if _int(fallback.get("trials_required"), "contract.fallback_gate.trials_required", 3) != 3:
        raise R0ContractError("contract requires exactly three fallback trials")
    _number(fallback.get("recovery_ms_max"), "contract.fallback_gate.recovery_ms_max")
    _number(
        fallback.get("generator_transition_max_inter_packet_gap_us_max"),
        "contract.fallback_gate.generator_transition_max_inter_packet_gap_us_max",
    )
    backend_proof = _mapping(
        contract.get("backend_proof_gate"), "contract.backend_proof_gate"
    )
    for name in (
        "xdp_drv_mode_flag",
        "xdp_skb_mode_flag",
        "xsk_zerocopy_bind_flag",
        "xsk_copy_bind_flag",
        "dpdk_reta_entries_min",
    ):
        _int(backend_proof.get(name), "contract.backend_proof_gate." + name, 1)
    if backend_proof.get("raw_queue_counters_required") is not True:
        raise R0ContractError("contract.backend_proof_gate.raw_queue_counters_required")
    topology = _mapping(contract.get("topology"), "contract.topology")
    if topology.get("primary_backend") != "native_af_xdp_forced_zerocopy":
        raise R0ContractError("contract.topology.primary_backend")
    if topology.get("fallback_backend") != "dpdk_rss_tss_multiqueue":
        raise R0ContractError("contract.topology.fallback_backend")
    if topology.get("same_pf_runtime_driver_rebind_allowed") is not False:
        raise R0ContractError("contract.topology.same_pf_runtime_driver_rebind_allowed")
    allowed_designs = _list(
        topology.get("allowed_fallback_designs"),
        "contract.topology.allowed_fallback_designs",
    )
    if not allowed_designs or len(allowed_designs) != len(set(allowed_designs)) or not all(
        isinstance(item, str) and item for item in allowed_designs
    ):
        raise R0ContractError("contract.topology.allowed_fallback_designs")
    _int(topology.get("capture_ports_min"), "contract.topology.capture_ports_min", 1)
    _int(topology.get("rx_queues_min"), "contract.topology.rx_queues_min", 8)
    _int(topology.get("tx_queues_min"), "contract.topology.tx_queues_min", 8)
    share = _number(topology.get("min_active_queue_share"), "contract.topology.min_active_queue_share")
    if not 0 < share <= 1:
        raise R0ContractError("contract.topology.min_active_queue_share")
    roles = _list(contract.get("required_manifest_roles"), "contract.required_manifest_roles")
    if not roles or len(roles) != len(set(roles)) or not all(isinstance(item, str) for item in roles):
        raise R0ContractError("contract.required_manifest_roles")
    if contract.get("production_qualified") is not False or contract.get(
        "final_pareto_ingestion_allowed"
    ) is not False:
        raise R0ContractError("contract may not grant production or Pareto qualification")


def _histogram_quantile(
    histogram: Any, quantile: float, expected_count: int, path: str
) -> float:
    items = _list(histogram, path)
    if not items:
        raise R0ContractError(path + " is empty")
    previous_bound = -math.inf
    previous_count = -1
    parsed: List[Tuple[float, int]] = []
    for index, raw in enumerate(items):
        item = _mapping(raw, "{}[{}]".format(path, index))
        bound = _number(item.get("le_us"), "{}[{}].le_us".format(path, index))
        count = _int(item.get("cumulative_count"), "{}[{}].cumulative_count".format(path, index))
        if bound <= previous_bound or count < previous_count:
            raise R0ContractError(path + " must have increasing bounds and counts")
        previous_bound = bound
        previous_count = count
        parsed.append((bound, count))
    if parsed[-1][1] != expected_count or expected_count <= 0:
        raise R0ContractError(path + " final count must equal unique captured packets")
    target = int(math.ceil(expected_count * quantile))
    for bound, count in parsed:
        if count >= target:
            return bound
    raise R0ContractError(path + " does not cover requested quantile")


def _resource_gate(
    samples: Any,
    started: datetime,
    completed: datetime,
    gate: Mapping[str, Any],
    path: str,
) -> Dict[str, Any]:
    items = _list(samples, path)
    minimum = _int(gate.get("samples_min_per_run"), "resource.samples_min_per_run", 1)
    if len(items) < minimum:
        raise R0ContractError(path + " has insufficient samples")
    timestamps: List[datetime] = []
    maxima = {
        "host_cpu_fraction": 0.0,
        "host_memory_fraction": 0.0,
        "process_rss_bytes": 0.0,
        "hugepage_reserved_bytes": 0.0,
    }
    for index, raw in enumerate(items):
        item = _mapping(raw, "{}[{}]".format(path, index))
        timestamp = _utc(item.get("timestamp_utc"), "{}[{}].timestamp_utc".format(path, index))
        if timestamp < started or timestamp > completed:
            raise R0ContractError(path + " sample outside run window")
        timestamps.append(timestamp)
        for name in maxima:
            value = _number(item.get(name), "{}[{}].{}".format(path, index, name))
            maxima[name] = max(maxima[name], value)
    if timestamps != sorted(timestamps) or len(timestamps) != len(set(timestamps)):
        raise R0ContractError(path + " timestamps must be strictly ordered and unique")
    max_interval = _number(gate.get("sample_interval_seconds_max"), "resource.sample_interval_seconds_max")
    if (
        (timestamps[0] - started).total_seconds() > max_interval
        or (completed - timestamps[-1]).total_seconds() > max_interval
    ):
        raise R0ContractError(path + " does not cover both run boundaries")
    if any((right - left).total_seconds() > max_interval for left, right in zip(timestamps, timestamps[1:])):
        raise R0ContractError(path + " sample interval exceeds gate")
    limits = {
        "host_cpu_fraction": "host_cpu_fraction_max",
        "host_memory_fraction": "host_memory_fraction_max",
        "process_rss_bytes": "process_rss_bytes_max",
        "hugepage_reserved_bytes": "hugepage_reserved_bytes_max",
    }
    failed = [name for name, limit in limits.items() if maxima[name] > float(gate[limit])]
    return {"maxima": maxima, "failed": failed, "sample_count": len(items)}


def _queue_gate(queue_packets: Any, topology: Mapping[str, Any], path: str) -> Dict[str, Any]:
    values = _list(queue_packets, path)
    parsed = [_int(value, "{}[{}]".format(path, index)) for index, value in enumerate(values)]
    minimum = max(int(topology["rx_queues_min"]), int(topology["tx_queues_min"]))
    total = sum(parsed)
    share = float(topology["min_active_queue_share"])
    active = sum(1 for value in parsed if total > 0 and value / total >= share)
    return {
        "raw_packets": parsed,
        "queue_count": len(parsed),
        "total_packets": total,
        "queues_above_min_share": active,
        "qualified": len(parsed) >= minimum and total > 0 and active >= minimum,
    }


def _validate_receipt_envelope(
    receipt: Mapping[str, Any],
    scope: str,
    campaign_id: str,
    producer_role: str,
    producer_hashes: Mapping[str, str],
    path: str,
) -> None:
    if receipt.get("schema_version") != 1 or receipt.get("scope") != scope:
        raise R0ContractError(path + ".envelope")
    if receipt.get("campaign_id") != campaign_id:
        raise R0ContractError(path + ".campaign_id")
    if receipt.get("producer_role") != producer_role:
        raise R0ContractError(path + ".producer_role")
    expected = _sha(producer_hashes.get(producer_role), path + ".producer_manifest_sha256")
    if _sha(receipt.get("producer_sha256"), path + ".producer_sha256") != expected:
        raise R0ContractError(path + ".producer_sha256 mismatch")
    if _sha(receipt.get("receipt_sha256"), path + ".receipt_sha256") != receipt_content_sha256(receipt):
        raise R0ContractError(path + ".receipt_sha256 mismatch")


def _evaluate_run(
    receipt: Mapping[str, Any],
    backend: str,
    campaign: Mapping[str, Any],
    contract: Mapping[str, Any],
    producer_hashes: Mapping[str, str],
    path: str,
) -> Dict[str, Any]:
    campaign_id = str(campaign["campaign_id"])
    producer_role = "xdp_runner" if backend == "native_af_xdp_forced_zerocopy" else "dpdk_runner"
    _validate_receipt_envelope(
        receipt,
        "new_nic_r0_run_receipt",
        campaign_id,
        producer_role,
        producer_hashes,
        path,
    )
    errors: List[str] = []
    run_id = _text(receipt.get("run_id"), path + ".run_id")
    repeat_index = _int(receipt.get("repeat_index"), path + ".repeat_index", 1)
    if receipt.get("backend") != backend:
        _append(errors, "backend")
    if receipt.get("capture_host_id") != campaign.get("capture_host_id"):
        _append(errors, "capture_host_id")
    expected_pci = sorted(campaign.get("candidate_pci_addresses") or [])
    observed_pci = receipt.get("candidate_pci_addresses")
    if not isinstance(observed_pci, list) or sorted(observed_pci) != expected_pci:
        _append(errors, "candidate_pci_addresses")
    generator = _mapping(campaign.get("generator_identity"), "campaign.generator_identity")
    for field in ("generator_host_id", "generator_nic_serial", "physical_link_id"):
        if receipt.get(field) != generator.get(field):
            _append(errors, field)
    started = _utc(receipt.get("started_at_utc"), path + ".started_at_utc")
    completed = _utc(receipt.get("completed_at_utc"), path + ".completed_at_utc")
    duration = (completed - started).total_seconds()
    load = contract["load_gate"]
    if duration < float(load["duration_seconds_min"]):
        _append(errors, "duration")
    if _int(receipt.get("packet_size_bytes"), path + ".packet_size_bytes", 1) != int(load["packet_size_bytes"]):
        _append(errors, "packet_size")
    generator_counts = _mapping(receipt.get("generator"), path + ".generator")
    _validate_receipt_envelope(
        generator_counts,
        "new_nic_r0_generator_window_receipt",
        campaign_id,
        "generator_runner",
        producer_hashes,
        path + ".generator",
    )
    if generator_counts.get("run_id") != run_id:
        _append(errors, "generator_run_link")
    for field in ("generator_host_id", "generator_nic_serial", "physical_link_id"):
        if generator_counts.get(field) != generator.get(field):
            _append(errors, "generator_" + field)
    if generator_counts.get("marker_manifest_sha256") != generator.get("marker_manifest_sha256"):
        _append(errors, "generator_marker_manifest")
    if (
        generator_counts.get("started_at_utc") != receipt.get("started_at_utc")
        or generator_counts.get("completed_at_utc") != receipt.get("completed_at_utc")
    ):
        _append(errors, "generator_window_link")
    requested = _int(generator_counts.get("requested_packets"), path + ".generator.requested_packets")
    sent = _int(generator_counts.get("sent_packets"), path + ".generator.sent_packets")
    tx_errors = _int(generator_counts.get("tx_errors"), path + ".generator.tx_errors")
    offered_mpps = sent / max(duration, 1e-12) / 1_000_000.0
    if requested != sent or tx_errors != 0 or offered_mpps < float(load["offered_mpps_min"]):
        _append(errors, "generator_load")
    capture = _mapping(receipt.get("capture"), path + ".capture")
    unique = _int(capture.get("unique_packets"), path + ".capture.unique_packets")
    loss_fields = (
        "sequence_gaps",
        "nic_rx_missed",
        "nic_rx_errors",
        "socket_drops",
        "descriptor_errors",
    )
    loss_values = {name: _int(capture.get(name), path + ".capture." + name) for name in loss_fields}
    duplicates = _int(capture.get("duplicate_packets"), path + ".capture.duplicate_packets")
    out_of_order = _int(capture.get("out_of_order_packets"), path + ".capture.out_of_order_packets")
    if unique != sent or any(loss_values.values()) or duplicates or out_of_order:
        _append(errors, "zero_loss")
    queues = _queue_gate(capture.get("queue_packets"), contract["topology"], path + ".capture.queue_packets")
    if not queues["qualified"] or queues["total_packets"] != unique:
        _append(errors, "queue_distribution")
    histogram = receipt.get("latency_histogram")
    p99 = _histogram_quantile(histogram, 0.99, unique, path + ".latency_histogram")
    p999 = _histogram_quantile(histogram, 0.999, unique, path + ".latency_histogram")
    latency_gate = contract["latency_gate"]
    latency_proof = _mapping(receipt.get("latency_proof"), path + ".latency_proof")
    timestamped_packets = _int(
        latency_proof.get("timestamped_packets"), path + ".latency_proof.timestamped_packets"
    )
    negative_samples = _int(
        latency_proof.get("negative_latency_samples"),
        path + ".latency_proof.negative_latency_samples",
    )
    clock_error = _number(
        latency_proof.get("clock_sync_error_us"),
        path + ".latency_proof.clock_sync_error_us",
    )
    if (
        latency_proof.get("measurement_method")
        not in latency_gate["allowed_measurement_methods"]
        or timestamped_packets != unique
        or negative_samples > int(latency_gate["negative_latency_samples_max"])
        or clock_error > float(latency_gate["clock_sync_error_us_max"])
    ):
        _append(errors, "latency_provenance")
    if p99 > float(latency_gate["p99_us_max"]):
        _append(errors, "p99")
    if p999 > float(latency_gate["p999_us_max"]):
        _append(errors, "p999")
    resource_receipt = _mapping(receipt.get("resource"), path + ".resource")
    _validate_receipt_envelope(
        resource_receipt,
        "new_nic_r0_resource_window_receipt",
        campaign_id,
        "resource_sampler",
        producer_hashes,
        path + ".resource",
    )
    if resource_receipt.get("run_id") != run_id:
        _append(errors, "resource_run_link")
    if (
        resource_receipt.get("started_at_utc") != receipt.get("started_at_utc")
        or resource_receipt.get("completed_at_utc") != receipt.get("completed_at_utc")
    ):
        _append(errors, "resource_window_link")
    resources = _resource_gate(
        resource_receipt.get("samples"),
        started,
        completed,
        contract["resource_gate"],
        path + ".resource.samples",
    )
    if resources["failed"]:
        _append(errors, "resources")
    key = _mapping(receipt.get("key_flow"), path + ".key_flow")
    total = _int(key.get("total"), path + ".key_flow.total")
    covered = _int(key.get("covered"), path + ".key_flow.covered")
    skipped = _int(key.get("skipped_due_budget"), path + ".key_flow.skipped_due_budget")
    key_gate = contract["key_flow_gate"]
    coverage = covered / total if total else None
    if (
        total <= 0
        or covered > total
        or skipped > int(key_gate["skipped_due_budget_max"])
        or coverage is None
        or coverage < float(key_gate["coverage_min_per_run"])
        or key.get("basis") != key_gate["basis"]
        or key.get("marker_manifest_sha256") != generator.get("marker_manifest_sha256")
    ):
        _append(errors, "key_flow")
    proof = _mapping(receipt.get("backend_proof"), path + ".backend_proof")
    proof_gate = contract["backend_proof_gate"]
    if backend == "native_af_xdp_forced_zerocopy":
        attach_flags = _int(proof.get("xdp_attach_flags"), path + ".backend_proof.xdp_attach_flags")
        bind_flags = _int(proof.get("xsk_bind_flags"), path + ".backend_proof.xsk_bind_flags")
        program_ids = [
            _int(value, path + ".backend_proof.xdp_program_ids[{}]".format(index), 1)
            for index, value in enumerate(_list(proof.get("xdp_program_ids"), path + ".backend_proof.xdp_program_ids"))
        ]
        socket_count = _int(proof.get("xsk_socket_count"), path + ".backend_proof.xsk_socket_count")
        zc_packets = _int(
            proof.get("xsk_zerocopy_rx_packets"),
            path + ".backend_proof.xsk_zerocopy_rx_packets",
        )
        copy_packets = _int(
            proof.get("xsk_copy_rx_packets"), path + ".backend_proof.xsk_copy_rx_packets"
        )
        if not (
            proof.get("attach_mode") == "native"
            and proof.get("xsk_bind_mode") == "forced_zerocopy"
            and proof.get("zero_copy_confirmed") is True
            and proof.get("copy_fallback_detected") is False
            and attach_flags & int(proof_gate["xdp_drv_mode_flag"])
            and not attach_flags & int(proof_gate["xdp_skb_mode_flag"])
            and bind_flags & int(proof_gate["xsk_zerocopy_bind_flag"])
            and not bind_flags & int(proof_gate["xsk_copy_bind_flag"])
            and len(program_ids) >= len(expected_pci)
            and len(program_ids) == len(set(program_ids))
            and socket_count >= int(contract["topology"]["rx_queues_min"])
            and zc_packets == unique
            and copy_packets == 0
        ):
            _append(errors, "xdp_backend_proof")
    else:
        rx_count = proof.get("rx_queues_configured")
        tx_count = proof.get("tx_queues_configured")
        reta = [
            _int(value, path + ".backend_proof.rss_reta[{}]".format(index))
            for index, value in enumerate(_list(proof.get("rss_reta"), path + ".backend_proof.rss_reta"))
        ]
        rss_types = _list(proof.get("rss_hash_types"), path + ".backend_proof.rss_hash_types")
        raw_rx = [
            _int(value, path + ".backend_proof.per_queue_rx_packets[{}]".format(index))
            for index, value in enumerate(_list(proof.get("per_queue_rx_packets"), path + ".backend_proof.per_queue_rx_packets"))
        ]
        raw_tx_gate = _queue_gate(
            proof.get("per_queue_tx_packets"),
            contract["topology"],
            path + ".backend_proof.per_queue_tx_packets",
        )
        if not (
            proof.get("rss_enabled") is True
            and proof.get("tss_enabled") is True
            and proof.get("reta_programmed") is True
            and type(rx_count) is int
            and rx_count >= int(contract["topology"]["rx_queues_min"])
            and type(tx_count) is int
            and tx_count >= int(contract["topology"]["tx_queues_min"])
            and len(reta) >= int(proof_gate["dpdk_reta_entries_min"])
            and len(set(reta)) >= int(contract["topology"]["rx_queues_min"])
            and all(value < rx_count for value in reta)
            and rss_types
            and all(isinstance(value, str) and value for value in rss_types)
            and raw_rx == queues["raw_packets"]
            and raw_tx_gate["qualified"]
        ):
            _append(errors, "dpdk_backend_proof")
    return {
        "run_id": run_id,
        "repeat_index": repeat_index,
        "backend": backend,
        "duration_seconds": duration,
        "offered_mpps": offered_mpps,
        "sent_packets": sent,
        "unique_packets": unique,
        "loss_counters": loss_values,
        "p99_us": p99,
        "p999_us": p999,
        "resource": resources,
        "key_flow_coverage": coverage,
        "queue_distribution": queues,
        "errors": errors,
        "qualified": not errors,
    }


def _evaluate_fallback(
    receipt: Mapping[str, Any],
    campaign: Mapping[str, Any],
    contract: Mapping[str, Any],
    producer_hashes: Mapping[str, str],
    run_ids: Mapping[str, Tuple[str, int]],
    path: str,
) -> Dict[str, Any]:
    _validate_receipt_envelope(
        receipt,
        "new_nic_r0_fallback_trial_receipt",
        str(campaign["campaign_id"]),
        "fallback_orchestrator",
        producer_hashes,
        path,
    )
    errors: List[str] = []
    trial_id = _text(receipt.get("trial_id"), path + ".trial_id")
    repeat_index = _int(receipt.get("repeat_index"), path + ".repeat_index", 1)
    xdp_run_id = _text(receipt.get("xdp_run_id"), path + ".xdp_run_id")
    dpdk_run_id = _text(receipt.get("dpdk_run_id"), path + ".dpdk_run_id")
    if run_ids.get(xdp_run_id) != ("native_af_xdp_forced_zerocopy", repeat_index):
        _append(errors, "xdp_run_link")
    if run_ids.get(dpdk_run_id) != ("dpdk_rss_tss_multiqueue", repeat_index):
        _append(errors, "dpdk_run_link")
    fallback_gate = contract["fallback_gate"]
    if receipt.get("fault_kind") != fallback_gate["fault_kind"]:
        _append(errors, "fault_kind")
    injected = _int(receipt.get("fault_injected_monotonic_ns"), path + ".fault_injected_monotonic_ns", 1)
    recovered = _int(receipt.get("first_dpdk_packet_monotonic_ns"), path + ".first_dpdk_packet_monotonic_ns", 1)
    if recovered < injected:
        raise R0ContractError(path + " recovery precedes fault")
    recovery_ms = (recovered - injected) / 1_000_000.0
    reported = _number(receipt.get("reported_recovery_ms"), path + ".reported_recovery_ms")
    if not math.isclose(reported, recovery_ms, rel_tol=0.0, abs_tol=1e-6):
        _append(errors, "recovery_recompute")
    if recovery_ms > float(fallback_gate["recovery_ms_max"]):
        _append(errors, "recovery_gate")
    generator = _mapping(
        receipt.get("generator_transition"), path + ".generator_transition"
    )
    _validate_receipt_envelope(
        generator,
        "new_nic_r0_generator_transition_receipt",
        str(campaign["campaign_id"]),
        "generator_runner",
        producer_hashes,
        path + ".generator_transition",
    )
    if generator.get("trial_id") != trial_id:
        _append(errors, "generator_trial_link")
    expected_generator = _mapping(
        campaign.get("generator_identity"), "campaign.generator_identity"
    )
    for field in ("generator_host_id", "generator_nic_serial", "physical_link_id"):
        if generator.get(field) != expected_generator.get(field):
            _append(errors, "generator_" + field)
    if generator.get("marker_manifest_sha256") != expected_generator.get(
        "marker_manifest_sha256"
    ):
        _append(errors, "generator_marker_manifest")
    window_start = _int(
        generator.get("window_started_monotonic_ns"),
        path + ".generator_transition.window_started_monotonic_ns",
        1,
    )
    window_end = _int(
        generator.get("window_completed_monotonic_ns"),
        path + ".generator_transition.window_completed_monotonic_ns",
        1,
    )
    requested = _int(
        generator.get("requested_packets"),
        path + ".generator_transition.requested_packets",
        1,
    )
    sent = _int(
        generator.get("sent_packets"), path + ".generator_transition.sent_packets", 1
    )
    tx_errors = _int(
        generator.get("tx_errors"), path + ".generator_transition.tx_errors"
    )
    before_packets = _int(
        generator.get("packets_before_fault"),
        path + ".generator_transition.packets_before_fault",
        1,
    )
    during_packets = _int(
        generator.get("packets_fault_to_recovery"),
        path + ".generator_transition.packets_fault_to_recovery",
        1,
    )
    after_packets = _int(
        generator.get("packets_after_recovery"),
        path + ".generator_transition.packets_after_recovery",
        1,
    )
    max_gap_us = _number(
        generator.get("max_inter_packet_gap_us"),
        path + ".generator_transition.max_inter_packet_gap_us",
    )
    if not (
        window_start < injected < recovered < window_end
        and requested == sent
        and tx_errors == 0
        and before_packets + during_packets + after_packets == sent
        and max_gap_us
        <= float(fallback_gate["generator_transition_max_inter_packet_gap_us_max"])
    ):
        _append(errors, "generator_continuity")
    transition = _mapping(receipt.get("transition"), path + ".transition")
    expected = _int(transition.get("expected_packets"), path + ".transition.expected_packets")
    received = _int(transition.get("received_unique_packets"), path + ".transition.received_unique_packets")
    gaps = _int(transition.get("sequence_gaps"), path + ".transition.sequence_gaps")
    duplicates = _int(transition.get("duplicate_packets"), path + ".transition.duplicate_packets")
    out_of_order = _int(transition.get("out_of_order_packets"), path + ".transition.out_of_order_packets")
    if expected != sent or received != expected or gaps or duplicates or out_of_order:
        _append(errors, "transition_zero_loss")
    return {
        "trial_id": trial_id,
        "repeat_index": repeat_index,
        "xdp_run_id": xdp_run_id,
        "dpdk_run_id": dpdk_run_id,
        "recovery_ms": recovery_ms,
        "transition_expected_packets": expected,
        "transition_received_unique_packets": received,
        "errors": errors,
        "qualified": not errors,
    }


def hardware_pending_result(contract: Mapping[str, Any]) -> Dict[str, Any]:
    try:
        validate_contract(contract)
        contract_id = contract["contract_id"]
        contract_hash = canonical_sha256(contract)
        errors: List[str] = []
    except (R0ContractError, TypeError, ValueError) as exc:
        contract_id = None
        contract_hash = None
        errors = [str(exc)]
    return {
        "schema_version": 1,
        "scope": "new_high_speed_nic_r0_campaign_audit",
        "status": "invalid_contract" if errors else "hardware_pending",
        "contract_id": contract_id,
        "contract_sha256": contract_hash,
        "errors": errors,
        "trusted_evidence_manifest_verified": False,
        "xdp_primary_repeats_qualified": 0,
        "dpdk_fallback_repeats_qualified": 0,
        "fallback_trials_qualified": 0,
        "r0_qualified": False,
        "production_qualified": False,
        "final_pareto_ingestion_allowed": False,
        "mutations_performed": False,
    }


def evaluate_r0_campaign(
    contract: Mapping[str, Any],
    campaign: Mapping[str, Any],
    arrival_inventory: Mapping[str, Any],
    arrival_preflight: Mapping[str, Any],
    xdp_runs: Sequence[Mapping[str, Any]],
    dpdk_runs: Sequence[Mapping[str, Any]],
    fallback_trials: Sequence[Mapping[str, Any]],
    restoration_before: Mapping[str, Any],
    restoration_after: Mapping[str, Any],
    producer_hashes: Mapping[str, str],
    trusted_manifest_verified: bool,
    trusted_manifest_sha256: Optional[str],
) -> Dict[str, Any]:
    errors: List[str] = []
    try:
        validate_contract(contract)
        if campaign.get("schema_version") != 1 or campaign.get("scope") != "new_high_speed_nic_r0_campaign":
            raise R0ContractError("campaign.envelope")
        campaign_id = _text(campaign.get("campaign_id"), "campaign.campaign_id")
        capture_host_id = _text(campaign.get("capture_host_id"), "campaign.capture_host_id")
        if campaign.get("authorized_execution") is not True:
            _append(errors, "campaign.authorized_execution")
        if campaign.get("mutations_performed") is not True:
            _append(errors, "campaign.mutations_performed")
        pci_addresses = _list(campaign.get("candidate_pci_addresses"), "campaign.candidate_pci_addresses")
        if (
            len(pci_addresses) < int(contract["topology"]["capture_ports_min"])
            or len(pci_addresses) != len(set(pci_addresses))
            or not all(isinstance(item, str) and item for item in pci_addresses)
        ):
            raise R0ContractError("campaign.candidate_pci_addresses")
        generator = _mapping(campaign.get("generator_identity"), "campaign.generator_identity")
        generator_host = _text(generator.get("generator_host_id"), "campaign.generator_identity.generator_host_id")
        generator_serial = _text(generator.get("generator_nic_serial"), "campaign.generator_identity.generator_nic_serial")
        _text(generator.get("physical_link_id"), "campaign.generator_identity.physical_link_id")
        _sha(generator.get("marker_manifest_sha256"), "campaign.generator_identity.marker_manifest_sha256")
        if generator_host == capture_host_id:
            _append(errors, "topology.generator_host_not_independent")
        candidate_serials = {
            item.get("adapter_serial")
            for item in arrival_inventory.get("candidate_ports", [])
            if isinstance(item, Mapping)
        }
        if generator_serial in candidate_serials:
            _append(errors, "topology.generator_nic_not_independent")
        topology = _mapping(campaign.get("topology"), "campaign.topology")
        allowed = contract["topology"]["allowed_fallback_designs"]
        if topology.get("fallback_design") not in allowed:
            _append(errors, "topology.fallback_design")
        if topology.get("same_pf_runtime_driver_rebind") is not False:
            _append(errors, "topology.same_pf_runtime_driver_rebind")
        if topology.get("independent_generator") is not True or topology.get("same_adapter_loopback") is not False:
            _append(errors, "topology.generator")
        arrival_gate = contract["arrival_gate"]
        if arrival_preflight.get("status") != arrival_gate["required_status"]:
            _append(errors, "arrival.status")
        if arrival_preflight.get("hardware_present") is not True:
            _append(errors, "arrival.hardware_present")
        if arrival_preflight.get("self_consistent_capability_receipts_valid") is not True:
            _append(errors, "arrival.capability_receipts")
        if arrival_preflight.get("production_qualified") is not False:
            _append(errors, "arrival.production_flag")
        if arrival_preflight.get("inventory_sha256") != canonical_sha256(arrival_inventory):
            _append(errors, "arrival.inventory_hash")
        arrival_manifest_sha = _sha(
            campaign.get("arrival_evidence_manifest_sha256"),
            "campaign.arrival_evidence_manifest_sha256",
        )
        if arrival_manifest_sha != _sha(
            producer_hashes.get("arrival_evidence_manifest"),
            "producer_hashes.arrival_evidence_manifest",
        ):
            _append(errors, "arrival.evidence_manifest_hash")
        if sorted(
            item.get("pci_address")
            for item in arrival_inventory.get("candidate_ports", [])
            if isinstance(item, Mapping)
        ) != sorted(pci_addresses):
            _append(errors, "arrival.candidate_pci_addresses")
        if not trusted_manifest_verified or not isinstance(trusted_manifest_sha256, str) or SHA256_RE.fullmatch(trusted_manifest_sha256) is None:
            _append(errors, "provenance.trusted_manifest")

        xdp_results = [
            _evaluate_run(item, "native_af_xdp_forced_zerocopy", campaign, contract, producer_hashes, "xdp_runs[{}]".format(index))
            for index, item in enumerate(xdp_runs)
        ]
        dpdk_results = [
            _evaluate_run(item, "dpdk_rss_tss_multiqueue", campaign, contract, producer_hashes, "dpdk_runs[{}]".format(index))
            for index, item in enumerate(dpdk_runs)
        ]
        required_indices = [1, 2, 3]
        if len(xdp_results) != 3 or sorted(item["repeat_index"] for item in xdp_results) != required_indices:
            _append(errors, "xdp.repeat_set")
        if len(dpdk_results) != 3 or sorted(item["repeat_index"] for item in dpdk_results) != required_indices:
            _append(errors, "dpdk.repeat_set")
        all_runs = xdp_results + dpdk_results
        run_ids = [item["run_id"] for item in all_runs]
        if len(run_ids) != len(set(run_ids)):
            _append(errors, "runs.distinct_ids")
        run_map = {item["run_id"]: (item["backend"], item["repeat_index"]) for item in all_runs}
        fallback_results = [
            _evaluate_fallback(item, campaign, contract, producer_hashes, run_map, "fallback_trials[{}]".format(index))
            for index, item in enumerate(fallback_trials)
        ]
        if len(fallback_results) != 3 or sorted(item["repeat_index"] for item in fallback_results) != required_indices:
            _append(errors, "fallback.repeat_set")
        trial_ids = [item["trial_id"] for item in fallback_results]
        if len(trial_ids) != len(set(trial_ids)):
            _append(errors, "fallback.distinct_ids")
        if any(not item["qualified"] for item in xdp_results):
            _append(errors, "xdp.run_gate")
        if any(not item["qualified"] for item in dpdk_results):
            _append(errors, "dpdk.run_gate")
        if any(not item["qualified"] for item in fallback_results):
            _append(errors, "fallback.trial_gate")

        required_domains = set(contract["restoration_gate"]["required_state_domains"])
        before_state = _mapping(restoration_before.get("state_domains"), "restoration_before.state_domains")
        after_state = _mapping(restoration_after.get("state_domains"), "restoration_after.state_domains")
        for snapshot, name, phase in (
            (restoration_before, "restoration_before", "before"),
            (restoration_after, "restoration_after", "after"),
        ):
            _validate_receipt_envelope(
                snapshot,
                "new_nic_r0_restoration_snapshot",
                campaign_id,
                "restore_helper",
                producer_hashes,
                name,
            )
            if snapshot.get("phase") != phase:
                raise R0ContractError(name + ".phase")
        restoration_hash_before = canonical_sha256(before_state)
        restoration_hash_after = canonical_sha256(after_state)
        restoration_qualified = (
            required_domains <= set(before_state)
            and required_domains <= set(after_state)
            and restoration_hash_before == restoration_hash_after
        )
        if not restoration_qualified:
            _append(errors, "restoration.state_mismatch")
    except (R0ContractError, TypeError, ValueError, KeyError, ArithmeticError) as exc:
        _append(errors, "contract_or_evidence:" + str(exc))
        xdp_results = []
        dpdk_results = []
        fallback_results = []
        restoration_hash_before = None
        restoration_hash_after = None
        restoration_qualified = False
        campaign_id = campaign.get("campaign_id") if isinstance(campaign, Mapping) else None

    qualified = not errors
    return {
        "schema_version": 1,
        "scope": "new_high_speed_nic_r0_campaign_audit",
        "status": "r0_qualified" if qualified else "r0_rejected",
        "campaign_id": campaign_id,
        "contract_id": contract.get("contract_id"),
        "contract_sha256": _safe_canonical_sha256(contract) if isinstance(contract, Mapping) else None,
        "trusted_evidence_manifest_verified": trusted_manifest_verified is True,
        "trusted_evidence_manifest_sha256": trusted_manifest_sha256,
        "xdp_primary_runs": xdp_results,
        "dpdk_fallback_runs": dpdk_results,
        "fallback_trials": fallback_results,
        "xdp_primary_repeats_qualified": sum(1 for item in xdp_results if item["qualified"]),
        "dpdk_fallback_repeats_qualified": sum(1 for item in dpdk_results if item["qualified"]),
        "fallback_trials_qualified": sum(1 for item in fallback_results if item["qualified"]),
        "restoration": {
            "before_sha256": restoration_hash_before,
            "after_sha256": restoration_hash_after,
            "qualified": restoration_qualified,
        },
        "errors": errors,
        "r0_qualified": qualified,
        "production_qualified": False,
        "final_pareto_ingestion_allowed": False,
        "mutations_performed": campaign.get("mutations_performed") is True
        if isinstance(campaign, Mapping)
        else False,
    }


def exit_code_for_status(status: str) -> int:
    return {
        "r0_qualified": 0,
        "hardware_pending": 20,
        "evidence_pending": 21,
        "r0_rejected": 22,
        "invalid_contract": 24,
        "invalid_input": 25,
        "provenance_rejected": 26,
    }.get(status, 27)
