"""Audit the bounded algorithm search and frozen HFT-MGBS release candidate."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


MIN_GATE_MAP = {
    "min_grouped_macro_f1": "grouped_macro_f1_min",
    "min_independent_macro_f1": "macro_f1_min",
    "min_independent_attack_recall": "attack_recall_min",
    "min_independent_benign_recall": "benign_recall_min",
    "min_independent_auprc": "auprc_min",
    "min_ground_truth_event_recall": "ground_truth_event_recall_min",
    "min_key_flow_coverage": "key_flow_coverage_min",
}

MAX_GATE_MAP = {
    "max_independent_ece": "ece_max",
    "max_budget_overrun_count": "budget_overrun_count_max",
    "max_fallback_recovery_s": "fallback_recovery_s_max",
}

PHYSICAL_MAX_GATE_MAP = {
    "max_capture_drop_rate": "capture_drop_rate_max",
    "max_gpu_batch_p99_us": "gpu_batch_p99_us_max",
    "max_internal_feature_enqueue_p99_us": "feature_enqueue_p99_us_max",
    "max_gpu_queue_full": "gpu_queue_full_max",
    "max_gpu_batches_failed": "gpu_batches_failed_max",
    "max_normal_fallback_flows": "fallback_flows_max",
    "max_budget_overrun_count": "budget_overrun_count_max",
}

SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def same_number(left, right, tolerance=1e-12):
    return (
        isinstance(left, (int, float))
        and not isinstance(left, bool)
        and isinstance(right, (int, float))
        and not isinstance(right, bool)
        and abs(float(left) - float(right)) <= tolerance
    )


def audit(search, release):
    errors = []
    candidates = search.get("candidates") or []
    budget = search.get("exploration_budget") or {}
    actual = budget.get("actual_candidates")
    if actual != len(candidates):
        errors.append("search.actual_candidate_count")
    if not isinstance(actual, int) or not (
        budget.get("minimum_candidates", 0)
        <= actual
        <= budget.get("maximum_candidates", -1)
    ):
        errors.append("search.exploration_budget")
    candidate_ids = [candidate.get("id") for candidate in candidates]
    if len(set(candidate_ids)) != len(candidate_ids):
        errors.append("search.duplicate_candidate_id")
    dimensions = search.get("search_dimensions") or {}
    for name in (
        "feature_profiles",
        "classifier_families",
        "threshold_policies",
        "adaptation_policies",
    ):
        if len(set(dimensions.get(name) or [])) < 2:
            errors.append("search.dimension.{}".format(name))

    selected = search.get("selected_candidate")
    if selected not in candidate_ids:
        errors.append("search.selected_candidate")
    if search.get("practical_front") != [selected]:
        errors.append("search.practical_front")
    if selected not in (search.get("strict_pareto_front") or []):
        errors.append("search.strict_pareto_front")
    selected_rows = [
        candidate for candidate in candidates if candidate.get("id") == selected
    ]
    if (
        len(selected_rows) != 1
        or selected_rows[0].get("stage") != "fresh_confirmatory"
    ):
        errors.append("search.selected_not_fresh_confirmatory")

    if release.get("candidate_id") != selected:
        errors.append("release.candidate_id")
    if release.get("final_pareto_eligible") is not False:
        errors.append("release.final_pareto_eligible")
    gates = release.get("frozen_non_live_gates") or {}
    observed = release.get("observed_confirmatory_lower_bounds") or {}
    for gate_name, observed_name in MIN_GATE_MAP.items():
        gate = gates.get(gate_name)
        value = observed.get(observed_name)
        if not isinstance(gate, (int, float)) or not isinstance(
            value, (int, float)
        ):
            errors.append("release.gate.{}.missing".format(gate_name))
        elif value < gate:
            errors.append("release.gate.{}.failed".format(gate_name))
    for gate_name, observed_name in MAX_GATE_MAP.items():
        gate = gates.get(gate_name)
        value = observed.get(observed_name)
        if not isinstance(gate, (int, float)) or not isinstance(
            value, (int, float)
        ):
            errors.append("release.gate.{}.missing".format(gate_name))
        elif value > gate:
            errors.append("release.gate.{}.failed".format(gate_name))

    physical = release.get("observed_physical_offline_confirmation") or {}
    if physical.get("run_count", 0) < 3:
        errors.append("release.physical_offline.run_count")
    physical_key_coverage = physical.get("key_flow_coverage_min")
    if not isinstance(physical_key_coverage, (int, float)):
        errors.append("release.physical_offline.key_flow_coverage.missing")
    elif physical_key_coverage < gates.get("min_key_flow_coverage", 1.0):
        errors.append("release.physical_offline.key_flow_coverage.failed")
    for gate_name, observed_name in PHYSICAL_MAX_GATE_MAP.items():
        gate = gates.get(gate_name)
        value = physical.get(observed_name)
        if not isinstance(gate, (int, float)) or not isinstance(
            value, (int, float)
        ):
            errors.append(
                "release.physical_offline.{}.missing".format(gate_name)
            )
        elif value > gate:
            errors.append(
                "release.physical_offline.{}.failed".format(gate_name)
            )

    resources = gates.get("resource_max") or {}
    resource_observed = {
        "cpu_utilization_max": max(
            physical.get("physical_host_cpu_fraction_upper", float("inf")),
            physical.get("python_host_cpu_fraction_upper", float("inf")),
        ),
        "memory_utilization_max": max(
            physical.get("physical_memory_fraction_max", float("inf")),
            physical.get("python_memory_fraction_max", float("inf")),
        ),
        "gpu_utilization_max": physical.get(
            "gpu_utilization_fraction_observed", float("inf")
        ),
        "gpu_memory_utilization_max": physical.get(
            "gpu_memory_fraction_observed", float("inf")
        ),
    }
    for name, value in resource_observed.items():
        gate = resources.get(name)
        if not isinstance(gate, (int, float)) or value > gate:
            errors.append("release.resource.{}.failed".format(name))

    resource_confirmation = (
        release.get("observed_split_inference_resource_confirmation")
        or {}
    )
    if resource_confirmation.get("accepted") is not True:
        errors.append("release.resource_confirmation.accepted")
    if resource_confirmation.get("diagnostic_only") is not True:
        errors.append("release.resource_confirmation.scope")
    if (
        resource_confirmation.get("final_pareto_ingestion_allowed")
        is not False
    ):
        errors.append("release.resource_confirmation.final_pareto_marker")
    if resource_confirmation.get("run_count", 0) < 3:
        errors.append("release.resource_confirmation.run_count")
    if resource_confirmation.get("service_gpu_process_present") is not False:
        errors.append("release.resource_confirmation.service_gpu_process")
    resource_confirmation_map = {
        "host_cpu_fraction_max": "python_host_cpu_fraction_upper",
        "host_memory_fraction_max": "python_memory_fraction_max",
        "service_gpu_utilization_fraction_max": (
            "gpu_utilization_fraction_observed"
        ),
        "service_gpu_memory_fraction_max": (
            "gpu_memory_fraction_observed"
        ),
        "threads_max": "python_worker_threads_max",
    }
    for direct_name, physical_name in resource_confirmation_map.items():
        if not same_number(
            resource_confirmation.get(direct_name),
            physical.get(physical_name),
        ):
            errors.append(
                "release.resource_confirmation.{}.mismatch".format(
                    direct_name
                )
            )
    rss_bytes = resource_confirmation.get("rss_bytes_max")
    if (
        not isinstance(rss_bytes, int)
        or rss_bytes <= 0
        or not same_number(
            rss_bytes / 1024.0,
            physical.get("python_rss_kb_max"),
        )
    ):
        errors.append("release.resource_confirmation.rss_bytes_max")
    for name, gate_name in (
        ("host_cpu_fraction_max", "cpu_utilization_max"),
        ("host_memory_fraction_max", "memory_utilization_max"),
        (
            "service_gpu_utilization_fraction_max",
            "gpu_utilization_max",
        ),
        (
            "service_gpu_memory_fraction_max",
            "gpu_memory_utilization_max",
        ),
    ):
        value = resource_confirmation.get(name)
        gate = resources.get(gate_name)
        if (
            not isinstance(value, (int, float))
            or not isinstance(gate, (int, float))
            or value > gate
        ):
            errors.append(
                "release.resource_confirmation.{}.failed".format(name)
            )

    recovery = release.get("observed_split_recovery_confirmation") or {}
    if recovery.get("run_count", 0) < 3:
        errors.append("release.split_recovery.run_count")
    recovery_s = recovery.get("recovery_to_success_s_max")
    recovery_gate = gates.get("max_fallback_recovery_s")
    if not isinstance(recovery_s, (int, float)) or not isinstance(
        recovery_gate, (int, float)
    ):
        errors.append("release.split_recovery.missing")
    elif recovery_s > recovery_gate:
        errors.append("release.split_recovery.failed")

    runtime = release.get("runtime") or {}
    batch_size = runtime.get("batch_size")
    timeout_ms = runtime.get("request_timeout_ms")
    feature_flush_us = runtime.get("feature_flush_us")
    if not isinstance(batch_size, int) or not 1 <= batch_size <= 512:
        errors.append("release.runtime.batch_size")
    if (
        not isinstance(timeout_ms, (int, float))
        or not isinstance(physical.get("gpu_batch_p99_us_max"), (int, float))
        or timeout_ms * 1000 <= physical.get("gpu_batch_p99_us_max", float("inf"))
    ):
        errors.append("release.runtime.request_timeout_margin")
    if not isinstance(feature_flush_us, int) or not 1 <= feature_flush_us <= 5000:
        errors.append("release.runtime.feature_flush_us")
    if runtime.get("prediction_execution") != "thread":
        errors.append("release.runtime.prediction_execution")
    runtime_contracts = {
        "thread_all": ("all", 80),
        "thread_cpu0_3": ("0-3", 4),
    }
    runtime_candidate = runtime.get("runtime_candidate")
    runtime_contract = runtime_contracts.get(runtime_candidate)
    if runtime_contract is None:
        errors.append("release.runtime.runtime_candidate")
    else:
        expected_cpu_set, expected_cpu_count = runtime_contract
        if runtime.get("cpu_set") != expected_cpu_set:
            errors.append("release.runtime.cpu_set")
        if runtime.get("eligible_cpu_count") != expected_cpu_count:
            errors.append("release.runtime.eligible_cpu_count")

    runtime_selection = (
        release.get("observed_runtime_robust_selection") or {}
    )
    if runtime_selection.get("accepted") is not True:
        errors.append("release.runtime_selection.accepted")
    if runtime_selection.get("diagnostic_only") is not True:
        errors.append("release.runtime_selection.scope")
    if (
        runtime_selection.get("final_pareto_ingestion_allowed")
        is not False
    ):
        errors.append("release.runtime_selection.final_pareto_marker")
    if (
        runtime_selection.get("selected_candidate") != runtime_candidate
        or runtime_candidate not in (
            runtime_selection.get("pareto_front") or []
        )
    ):
        errors.append("release.runtime_selection.selected_candidate")
    runtime_candidate_count = runtime_selection.get("candidate_count")
    runtime_campaign_count = runtime_selection.get(
        "campaign_count_per_candidate"
    )
    runtime_repeats = runtime_selection.get("repeats_per_candidate")
    runtime_total = runtime_selection.get("total_runtime_runs")
    if (
        not isinstance(runtime_candidate_count, int)
        or runtime_candidate_count != 4
        or not isinstance(runtime_campaign_count, int)
        or runtime_campaign_count < 2
        or not isinstance(runtime_repeats, int)
        or runtime_repeats < 6
        or runtime_total != runtime_candidate_count * runtime_repeats
    ):
        errors.append("release.runtime_selection.search_budget")
    runtime_gates = (
        (
            "inference_batch_p99_us_max",
            gates.get("max_gpu_batch_p99_us"),
        ),
        (
            "internal_feature_p99_us_max",
            gates.get("max_internal_feature_enqueue_p99_us"),
        ),
        (
            "end_to_end_p99_us_max",
            gates.get("max_diagnostic_end_to_end_p99_us"),
        ),
        (
            "end_to_end_p999_us_max",
            gates.get("max_diagnostic_end_to_end_p999_us"),
        ),
    )
    for name, gate in runtime_gates:
        value = runtime_selection.get(name)
        if (
            not isinstance(value, (int, float))
            or not isinstance(gate, (int, float))
            or value > gate
        ):
            errors.append("release.runtime_selection.{}.failed".format(name))

    virtual = release.get("observed_virtual_link_diagnostic") or {}
    if virtual.get("accepted") is not True:
        errors.append("release.virtual_diagnostic.accepted")
    if virtual.get("diagnostic_only") is not True:
        errors.append("release.virtual_diagnostic.scope")
    if virtual.get("final_pareto_ingestion_allowed") is not False:
        errors.append("release.virtual_diagnostic.final_pareto_marker")
    if virtual.get("run_count", 0) < 3:
        errors.append("release.virtual_diagnostic.run_count")
    if virtual.get("pipeline_drop_rate_max") != 0:
        errors.append("release.virtual_diagnostic.pipeline_drop_rate")
    if virtual.get("budget_overrun_count_max") != 0:
        errors.append("release.virtual_diagnostic.budget_overrun_count")
    if (
        not isinstance(virtual.get("key_flow_coverage_min"), (int, float))
        or virtual.get("key_flow_coverage_min")
        < gates.get("min_key_flow_coverage", 1.0)
    ):
        errors.append("release.virtual_diagnostic.key_flow_coverage")
    virtual_gates = runtime_gates + (
        (
            "parse_reject_rate_max",
            gates.get("max_diagnostic_parse_reject_rate"),
        ),
    )
    for name, gate in virtual_gates:
        value = virtual.get(name)
        if (
            not isinstance(value, (int, float))
            or not isinstance(gate, (int, float))
            or value > gate
        ):
            errors.append("release.virtual_diagnostic.{}.failed".format(name))

    capability = release.get("capture_capability") or {}
    if capability.get("driver") != "bnx2x":
        errors.append("release.capture_capability.driver")
    if capability.get("selected_capture_driver") != "xdp-skb":
        errors.append("release.capture_capability.selected_driver")
    if capability.get("fallback_capture_driver") != "af-packet-ts":
        errors.append("release.capture_capability.fallback_driver")
    if capability.get("kernel_bpf_enabled") is not True:
        errors.append("release.capture_capability.kernel_bpf")
    if capability.get("kernel_xdp_sockets_enabled") is not True:
        errors.append("release.capture_capability.kernel_xdp_sockets")
    if capability.get("xdp_generic_driver_qualified_diagnostic_only") is not True:
        errors.append("release.capture_capability.xdp_generic_diagnostic")
    for name in (
        "xdp_native_driver_qualified",
        "xdp_hardware_offload_qualified",
        "af_xdp_zero_copy_qualified",
    ):
        if capability.get(name) is not False:
            errors.append("release.capture_capability.{}".format(name))

    evidence = release.get("evidence") or {}
    for name in (
        "runtime_robust_selection_sha256",
        "virtual_link_diagnostic_sha256",
        "inference_node_resource_confirmation_sha256",
        "physical_replay_confirmation_sha256",
        "physical_replay_binary_sha256",
        "split_recovery_confirmation_sha256",
        "timestamp_driver_probe_sha256",
        "timestamp_driver_probe_binary_sha256",
        "remote_release_audit_sha256",
        "latest_live_preflight_bundle_index_sha256",
        "final_10gbe_interface_readiness_sha256",
        "xdp_skb_diagnostic_stability_sha256",
        "xdp_skb_joint_resource_confirmation_sha256",
        "xdp_skb_joint_physical_summary_sha256",
        "xdp_skb_capture_fallback_diagnostic_sha256",
        "xdp_ebpf_object_sha256",
        "xdp_ebpf_source_sha256",
        "temporary_passive_shadow_summary_sha256",
        "temporary_runtime_matrix_sha256",
        "feature_base_mapping_comparison_sha256",
        "feature_determinism_comparison_sha256",
        "active_runtime_manifest_sha256",
        "live_counter_map_sha256",
        "input_manifest_sha256",
    ):
        if not SHA256_PATTERN.fullmatch(str(evidence.get(name, ""))):
            errors.append("release.evidence.{}".format(name))
    resource_runs = evidence.get("inference_node_resource_runs")
    if not isinstance(resource_runs, list) or len(resource_runs) < 3:
        errors.append("release.evidence.inference_node_resource_runs")
    else:
        for index, item in enumerate(resource_runs):
            if (
                not isinstance(item, dict)
                or not isinstance(item.get("path"), str)
                or not item.get("path")
                or not SHA256_PATTERN.fullmatch(
                    str(item.get("sha256", ""))
                )
            ):
                errors.append(
                    "release.evidence.inference_node_resource_runs.{}"
                    .format(index)
                )

    pending = release.get("pending_physical_live_gates") or {}
    latest_preflight = (
        release.get("observed_latest_physical_live_preflight") or {}
    )
    if latest_preflight.get("accepted") is not False:
        errors.append("release.latest_live_preflight.pending_marker")
    if not latest_preflight.get("blocking_errors"):
        errors.append("release.latest_live_preflight.blocking_errors")
    if latest_preflight.get("capture_driver") != "xdp-skb":
        errors.append("release.latest_live_preflight.capture_driver")
    if latest_preflight.get("kernel_xdp_timestamp_ready") is not True:
        errors.append("release.latest_live_preflight.timestamp_capability")
    readiness = (
        release.get("observed_final_10gbe_interface_readiness") or {}
    )
    if readiness.get("minimum_speed_mbps") != 10000:
        errors.append("release.interface_readiness.minimum_speed")
    if readiness.get("require_unmanaged") is not True:
        errors.append("release.interface_readiness.unmanaged")
    if readiness.get("excluded_interfaces") != []:
        errors.append("release.interface_readiness.excluded")
    if readiness.get("hardware_eligible_interfaces") != ["ens8f0", "ens8f1"]:
        errors.append("release.interface_readiness.hardware_interfaces")
    if readiness.get("hardware_pair_count") != 1:
        errors.append("release.interface_readiness.hardware_pair")
    if readiness.get("full_preflight_pair_count") != 0:
        errors.append("release.interface_readiness.full_pair")
    if readiness.get("final_live_run_allowed") is not False:
        errors.append("release.interface_readiness.run_allowed")
    interface_blockers = readiness.get("interface_blockers")
    if (
        not isinstance(interface_blockers, dict)
        or any(interface_blockers.values())
    ):
        errors.append("release.interface_readiness.interface_blockers")
    if not readiness.get("threshold_blockers"):
        errors.append("release.interface_readiness.threshold_blockers")

    xdp = release.get("observed_xdp_skb_diagnostic_stability") or {}
    if xdp.get("accepted") is not True:
        errors.append("release.xdp_skb.accepted")
    if xdp.get("diagnostic_only") is not True:
        errors.append("release.xdp_skb.scope")
    if xdp.get("run_count", 0) < 3:
        errors.append("release.xdp_skb.run_count")
    if xdp.get("capture_driver") != "xdp-skb":
        errors.append("release.xdp_skb.capture_driver")
    if xdp.get("native_xdp_supported") is not False:
        errors.append("release.xdp_skb.native_claim")
    if xdp.get("capture_packets_dropped_max") != 0:
        errors.append("release.xdp_skb.capture_drop")
    if (
        not isinstance(xdp.get("key_flow_coverage_min"), (int, float))
        or xdp.get("key_flow_coverage_min")
        < gates.get("min_key_flow_coverage", 1.0)
    ):
        errors.append("release.xdp_skb.key_flow_coverage")
    xdp_gates = (
        (
            "parse_reject_rate_max",
            gates.get("max_diagnostic_parse_reject_rate"),
        ),
        (
            "kernel_xdp_to_feature_p99_us_max",
            gates.get("max_diagnostic_end_to_end_p99_us"),
        ),
        (
            "kernel_xdp_to_feature_p999_us_max",
            gates.get("max_diagnostic_end_to_end_p999_us"),
        ),
        (
            "internal_feature_p99_us_max",
            gates.get("max_internal_feature_enqueue_p99_us"),
        ),
        ("gpu_batch_p99_us_max", gates.get("max_gpu_batch_p99_us")),
    )
    for name, gate in xdp_gates:
        value = xdp.get(name)
        if (
            not isinstance(value, (int, float))
            or not isinstance(gate, (int, float))
            or value > gate
        ):
            errors.append("release.xdp_skb.{}.failed".format(name))
    if xdp.get("diagnostic_resource_evidence_complete") is not True:
        errors.append("release.xdp_skb.diagnostic_resources")
    if xdp.get("joint_resource_run_count", 0) < 3:
        errors.append("release.xdp_skb.joint_resource_runs")
    if xdp.get("service_gpu_process_present") is not False:
        errors.append("release.xdp_skb.service_gpu_process")
    if xdp.get("production_resource_evidence_complete") is not False:
        errors.append("release.xdp_skb.production_resource_marker")
    if xdp.get("production_sla_frozen") is not False:
        errors.append("release.xdp_skb.production_sla_marker")
    if xdp.get("capture_driver_runtime_fallback_evidence_complete") is not True:
        errors.append("release.xdp_skb.capture_fallback_evidence")
    if xdp.get("capture_driver_runtime_fallback_production_complete") is not False:
        errors.append("release.xdp_skb.capture_fallback_production_marker")
    if xdp.get("final_pareto_ingestion_allowed") is not False:
        errors.append("release.xdp_skb.final_pareto_marker")

    capture_fallback = (
        release.get("observed_capture_driver_fallback_diagnostic") or {}
    )
    if capture_fallback.get("accepted") is not True:
        errors.append("release.capture_fallback.accepted")
    if capture_fallback.get("diagnostic_only") is not True:
        errors.append("release.capture_fallback.scope")
    if capture_fallback.get("run_count", 0) < 3:
        errors.append("release.capture_fallback.run_count")
    recovery_ms = capture_fallback.get("fallback_recovery_ms_max")
    recovery_limit_ms = gates.get("max_fallback_recovery_s", 0) * 1000
    if (
        not isinstance(recovery_ms, (int, float))
        or recovery_ms > recovery_limit_ms
    ):
        errors.append("release.capture_fallback.recovery")
    if capture_fallback.get("fallback_packets_min", 0) <= 0:
        errors.append("release.capture_fallback.real_traffic")
    if capture_fallback.get("post_promiscuity_max") != 0:
        errors.append("release.capture_fallback.promiscuity")
    if capture_fallback.get("post_xdp_program_absent_all_runs") is not True:
        errors.append("release.capture_fallback.xdp_cleanup")
    if capture_fallback.get("post_gro_restored_all_runs") is not True:
        errors.append("release.capture_fallback.gro_restore")
    if capture_fallback.get("normal_path_zero_drop_evidence_reused") is not False:
        errors.append("release.capture_fallback.zero_drop_scope")
    if capture_fallback.get("production_fallback_evidence_complete") is not False:
        errors.append("release.capture_fallback.production_marker")
    if capture_fallback.get("final_pareto_ingestion_allowed") is not False:
        errors.append("release.capture_fallback.final_pareto_marker")

    temporary_shadow = (
        release.get("observed_temporary_passive_shadow") or {}
    )
    if temporary_shadow.get("diagnostic_only") is not True:
        errors.append("release.temporary_shadow.scope")
    if temporary_shadow.get("final_pareto_ingestion_allowed") is not False:
        errors.append("release.temporary_shadow.final_pareto_marker")
    if temporary_shadow.get("production_10gbe_claim_allowed") is not False:
        errors.append("release.temporary_shadow.production_10gbe_marker")
    if temporary_shadow.get("pcap_injection_allowed") is not False:
        errors.append("release.temporary_shadow.pcap_injection")
    if temporary_shadow.get("traffic_generation_allowed") is not False:
        errors.append("release.temporary_shadow.traffic_generation")
    if temporary_shadow.get("production_thresholds_applied") is not False:
        errors.append("release.temporary_shadow.production_thresholds")
    if temporary_shadow.get("capture_interface") != "ens9f0":
        errors.append("release.temporary_shadow.capture_interface")
    if temporary_shadow.get("network_master") != "br0":
        errors.append("release.temporary_shadow.network_master")
    if temporary_shadow.get("speed_mbps") != 1000:
        errors.append("release.temporary_shadow.speed")
    if temporary_shadow.get("run_count", 0) < 3:
        errors.append("release.temporary_shadow.run_count")
    shadow_duration = temporary_shadow.get("confirmation_duration_s")
    if (
        not isinstance(shadow_duration, int)
        or shadow_duration < 10
        or shadow_duration > 60
    ):
        errors.append("release.temporary_shadow.duration")
    if temporary_shadow.get("runtime_candidate") != runtime_candidate:
        errors.append("release.temporary_shadow.runtime_candidate")
    if temporary_shadow.get("batch_size") != batch_size:
        errors.append("release.temporary_shadow.batch_size")
    if temporary_shadow.get("feature_flush_us") != feature_flush_us:
        errors.append("release.temporary_shadow.feature_flush_us")
    shadow_received = temporary_shadow.get("packets_received_min")
    shadow_reject_rate = temporary_shadow.get("parse_reject_rate_max")
    if (
        not isinstance(shadow_received, int)
        or shadow_received <= 0
        or not isinstance(shadow_reject_rate, (int, float))
        or shadow_reject_rate
        > gates.get("max_diagnostic_parse_reject_rate", -1)
    ):
        errors.append("release.temporary_shadow.packet_accounting")
    if temporary_shadow.get("capture_drop_rate_max") != 0:
        errors.append("release.temporary_shadow.capture_drops")
    if (
        temporary_shadow.get("key_flow_coverage_min", -1)
        < gates["min_key_flow_coverage"]
    ):
        errors.append("release.temporary_shadow.key_flow_coverage")
    for name in (
        "gpu_batches_failed_max",
        "gpu_queue_full_max",
        "fallback_flows_max",
        "budget_overrun_count_max",
    ):
        if temporary_shadow.get(name) != 0:
            errors.append(
                "release.temporary_shadow.{}".format(name)
            )
    for name, gate_name in (
        (
            "internal_feature_enqueue_p99_us_max",
            "max_internal_feature_enqueue_p99_us",
        ),
        (
            "gpu_batch_round_trip_p99_us_max",
            "max_gpu_batch_p99_us",
        ),
    ):
        value = temporary_shadow.get(name)
        gate = gates.get(gate_name)
        if (
            not isinstance(value, (int, float))
            or not isinstance(gate, (int, float))
            or value > gate
        ):
            errors.append(
                "release.temporary_shadow.{}.failed".format(name)
            )

    timestamp_probe = release.get("observed_timestamp_driver_probe") or {}
    if timestamp_probe.get("diagnostic_only") is not True:
        errors.append("release.timestamp_probe.scope")
    if timestamp_probe.get("capture_driver") != "af_packet_ts":
        errors.append("release.timestamp_probe.capture_driver")
    if (
        timestamp_probe.get("timestamp_provenance")
        != "kernel_software_receive_realtime_so_timestampns"
    ):
        errors.append("release.timestamp_probe.provenance")
    received = timestamp_probe.get("packets_received")
    parsed = timestamp_probe.get("packets_parsed")
    if (
        not isinstance(received, int)
        or received <= 0
        or not isinstance(parsed, int)
        or parsed <= 0
        or parsed > received
    ):
        errors.append("release.timestamp_probe.packet_accounting")
    timestamp_parse_reject_rate = timestamp_probe.get(
        "parse_reject_rate"
    )
    if (
        not isinstance(timestamp_parse_reject_rate, (int, float))
        or timestamp_parse_reject_rate
        > gates.get("max_diagnostic_parse_reject_rate", -1)
        or (
            isinstance(received, int)
            and received > 0
            and isinstance(parsed, int)
            and abs(
                timestamp_parse_reject_rate
                - ((received - parsed) / received)
            )
            > 1e-12
        )
    ):
        errors.append("release.timestamp_probe.parse_reject_rate")
    samples = timestamp_probe.get(
        "kernel_receive_to_feature_enqueue_samples"
    )
    if not isinstance(samples, int) or samples <= 0:
        errors.append("release.timestamp_probe.samples")
    if timestamp_probe.get("kernel_timestamp_anomalies") != 0:
        errors.append("release.timestamp_probe.timestamp_anomalies")
    if timestamp_probe.get("realtime_clock_step_count") != 0:
        errors.append("release.timestamp_probe.clock_steps")
    required_pending = (
        "physical_interface",
        "capture_driver",
        "target_load_mpps",
        "target_load_gbps",
        "max_end_to_end_p99_us",
        "max_end_to_end_p999_us",
    )
    if not any(pending.get(name) is None for name in required_pending):
        errors.append("release.physical_pending_marker")
    return {
        "schema_version": 1,
        "scope": "release_candidate_audit",
        "accepted": not errors,
        "errors": errors,
        "algorithm_candidate_count": len(candidates),
        "selected_candidate": selected,
        "offline_release_candidate_qualified": not errors,
        "split_recovery_qualified": not any(
            error.startswith("release.split_recovery") for error in errors
        ),
        "physical_live_gate_pending": True,
        "final_pareto_eligible": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("algorithm_search", type=Path)
    parser.add_argument("release_candidate", type=Path)
    args = parser.parse_args()
    with args.algorithm_search.open("r", encoding="utf-8") as handle:
        search = json.load(handle)
    with args.release_candidate.open("r", encoding="utf-8") as handle:
        release = json.load(handle)
    result = audit(search, release)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
