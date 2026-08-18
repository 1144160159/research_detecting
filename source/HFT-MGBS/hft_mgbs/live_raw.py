"""Compose strict live evidence from raw HFT-MGBS acceptance artifacts."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .live_evidence import audit_live_run


AGGREGATE_ETHTOOL = re.compile(r"^\s+([^:\[\]]+):\s*(\d+)\s*$")
DIAGNOSTIC_OPTIONAL_ERRORS = {
    "missing_external_evidence.cross_host_resource_maxima",
    "missing_external_evidence.live_fallback_under_traffic",
    "cpu_utilization_max.missing_or_invalid",
    "gpu_utilization_max.missing_or_invalid",
    "memory_utilization_max.missing_or_invalid",
    "gpu_memory_utilization_max.missing_or_invalid",
    "recovery_s_max.missing_or_invalid",
}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_manifest(path):
    values = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values.setdefault(key, []).append(value)
    return {key: items[-1] for key, items in values.items()}


def parse_counter_file(path):
    values = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = int(value.strip())
    return values


def parse_ethtool_aggregates(path):
    values = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        match = AGGREGATE_ETHTOOL.match(line)
        if match:
            values[match.group(1).strip()] = int(match.group(2))
    return values


def _delta(before, after, counter, errors, prefix):
    if counter not in before or counter not in after:
        errors.append("{}.counter_missing.{}".format(prefix, counter))
        return None
    value = after[counter] - before[counter]
    if value < 0:
        errors.append("{}.counter_reset.{}".format(prefix, counter))
        return None
    return value


def _mapped_delta(mapping, sources_before, sources_after, errors, prefix):
    source = mapping.get("source")
    counter = mapping.get("counter")
    if source not in sources_before or not str(counter):
        errors.append("{}.mapping_invalid".format(prefix))
        return None
    return _delta(
        sources_before[source],
        sources_after[source],
        str(counter),
        errors,
        prefix,
    )


def _load_optional(path, missing_name, errors):
    if path is None:
        errors.append("missing_external_evidence.{}".format(missing_name))
        return {}
    try:
        values = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        errors.append(
            "invalid_external_evidence.{}:{}".format(
                missing_name, type(error).__name__
            )
        )
        return {}
    if not isinstance(values, dict):
        errors.append("invalid_external_evidence.{}".format(missing_name))
        return {}
    return values


def compose_live_run(
    run_dir,
    release,
    counter_map,
    latency_evidence=None,
    resource_evidence=None,
    fallback_evidence=None,
):
    run_dir = Path(run_dir)
    errors = []
    manifest = parse_manifest(run_dir / "manifest.txt")
    evidence_scope = manifest.get(
        "evidence_scope", "physical_nic_live_replay"
    )
    virtual_diagnostic = (
        evidence_scope == "virtual_link_live_diagnostic"
    )
    physical_diagnostic = (
        evidence_scope == "physical_link_live_diagnostic"
    )
    diagnostic = virtual_diagnostic or physical_diagnostic
    if evidence_scope not in (
        "physical_nic_live_replay",
        "physical_link_live_diagnostic",
        "virtual_link_live_diagnostic",
    ):
        errors.append("manifest.evidence_scope")
    if diagnostic and manifest.get("diagnostic_only") != "true":
        errors.append("manifest.diagnostic_only")
    metrics = json.loads(
        (run_dir / "metrics.json").read_text(encoding="utf-8")
    )
    injector = json.loads(
        (run_dir / "injector_metrics.json").read_text(encoding="utf-8")
    )
    if injector.get("scope") != evidence_scope:
        errors.append("injector.scope")
    capture_preflight = json.loads(
        (run_dir / "capture_preflight.json").read_text(encoding="utf-8")
    )
    replay_preflight = json.loads(
        (run_dir / "replay_preflight.json").read_text(encoding="utf-8")
    )
    thresholds_path = run_dir / "frozen_thresholds.json"
    thresholds = json.loads(thresholds_path.read_text(encoding="utf-8"))
    actual_thresholds_sha = sha256(thresholds_path)

    if manifest.get("status") != "raw_evidence_complete":
        errors.append("manifest.status")
    if capture_preflight.get("accepted") is not True:
        errors.append("capture_preflight.not_accepted")
    if replay_preflight.get("accepted") is not True:
        errors.append("replay_preflight.not_accepted")
    expected_preflight_scope = (
        "virtual_link_live_host_preflight"
        if virtual_diagnostic
        else "physical_nic_live_host_preflight"
    )
    if capture_preflight.get("scope") != expected_preflight_scope:
        errors.append("capture_preflight.scope")
    if replay_preflight.get("scope") != expected_preflight_scope:
        errors.append("replay_preflight.scope")
    if capture_preflight.get("driver") != counter_map.get("driver"):
        errors.append("counter_map.driver_mismatch")
    if manifest.get("capture_interface") == manifest.get(
        "replay_interface"
    ):
        errors.append("capture_interfaces.not_isolated")
    if manifest.get("thresholds_sha256") != actual_thresholds_sha:
        errors.append("identity.thresholds_sha256_mismatch")
    binary_path = Path(str(manifest.get("binary", "")))
    if not binary_path.is_file():
        errors.append("identity.binary_missing")
    elif sha256(binary_path) != manifest.get("binary_sha256"):
        errors.append("identity.binary_sha256_mismatch")
    input_path = Path(str(manifest.get("replay_input", "")))
    if not input_path.is_file():
        errors.append("identity.input_missing")
    elif sha256(input_path) != manifest.get("input_sha256"):
        errors.append("identity.input_sha256_mismatch")

    sources_before = {
        "sysfs": parse_counter_file(
            run_dir / "capture_before_sysfs_counters.txt"
        ),
        "ethtool": parse_ethtool_aggregates(
            run_dir / "capture_before_ethtool_stats.txt"
        ),
    }
    sources_after = {
        "sysfs": parse_counter_file(
            run_dir / "capture_after_sysfs_counters.txt"
        ),
        "ethtool": parse_ethtool_aggregates(
            run_dir / "capture_after_ethtool_stats.txt"
        ),
    }
    replay_before = {
        "sysfs": parse_counter_file(
            run_dir / "replay_before_sysfs_counters.txt"
        )
    }
    replay_after = {
        "sysfs": parse_counter_file(
            run_dir / "replay_after_sysfs_counters.txt"
        )
    }

    replay_tx = _mapped_delta(
        counter_map["replay_transmitted_packets"],
        replay_before,
        replay_after,
        errors,
        "replay_transmitted_packets",
    )
    nic_received = _mapped_delta(
        counter_map["capture_received_packets"],
        sources_before,
        sources_after,
        errors,
        "capture_received_packets",
    )
    nic_drop = _mapped_delta(
        counter_map["capture_nic_drop_packets"],
        sources_before,
        sources_after,
        errors,
        "capture_nic_drop_packets",
    )
    for mapping in counter_map.get(
        "fail_if_nonzero_capture_counters", []
    ):
        value = _mapped_delta(
            mapping,
            sources_before,
            sources_after,
            errors,
            "unmapped_capture_error",
        )
        if value not in (None, 0):
            errors.append(
                "unmapped_capture_error.nonzero.{}".format(
                    mapping.get("counter")
                )
            )

    offered = injector.get("offered_packets")
    source_packets = injector.get("source_packets_read")
    segmented_source_packets = injector.get(
        "segmented_source_packets"
    )
    generated_tcp_segments = injector.get("generated_tcp_segments")
    rate_headroom_ratio = injector.get("rate_headroom_ratio")
    if not all(
        isinstance(value, int) and not isinstance(value, bool) and value >= 0
        for value in (
            source_packets,
            segmented_source_packets,
            generated_tcp_segments,
        )
    ):
        errors.append("injector.segmentation_accounting")
    elif (
        source_packets
        - segmented_source_packets
        + generated_tcp_segments
        != offered
    ):
        errors.append("injector.segmentation_reconciliation")
    if (
        isinstance(rate_headroom_ratio, bool)
        or not isinstance(rate_headroom_ratio, (int, float))
        or not 1.0 <= float(rate_headroom_ratio) <= 1.05
    ):
        errors.append("injector.rate_headroom_ratio")
    if replay_tx is not None and offered != replay_tx:
        errors.append("counter_reconciliation.injector_to_replay_tx")

    if latency_evidence is None:
        measured_latency = metrics.get(
            "kernel_receive_to_feature_enqueue_latency"
        ) or {}
        timestamp_provenance = metrics.get("timestamp_provenance")
        provenance_start_points = {
            "kernel_software_receive_realtime_so_timestampns": (
                "kernel_receive_realtime"
            ),
            "xdp_bpf_ktime_get_ns_converted_realtime_metadata": (
                "kernel_xdp_entry_realtime"
            ),
        }
        provenance_ok = (
            timestamp_provenance in provenance_start_points
            and metrics.get("kernel_timestamp_anomalies") == 0
            and metrics.get("realtime_clock_step_count") == 0
            and isinstance(measured_latency.get("samples"), int)
            and measured_latency.get("samples", 0) > 0
        )
        if provenance_ok:
            latency = {
                "timestamp_provenance_verified": True,
                "start_point": provenance_start_points[
                    timestamp_provenance
                ],
                "end_point": "feature_event_enqueued",
                "sample_count": measured_latency.get("samples"),
                "p99_us": measured_latency.get("p99_us"),
                "p999_us": measured_latency.get("p999_us"),
                "max_us": measured_latency.get("max_us"),
                "realtime_clock_step_count": 0,
            }
        else:
            errors.append(
                "missing_external_evidence.kernel_to_feature_latency"
            )
            latency = {}
    else:
        latency = _load_optional(
            latency_evidence, "kernel_to_feature_latency", errors
        )
    if latency:
        if latency.get("timestamp_provenance_verified") is not True:
            errors.append("latency.timestamp_provenance_unverified")
        if latency.get("start_point") not in (
            "nic_hardware_timestamp",
            "kernel_receive_monotonic",
            "kernel_receive_realtime",
            "kernel_xdp_entry_realtime",
        ):
            errors.append("latency.start_point")
        if latency.get("end_point") != "feature_event_enqueued":
            errors.append("latency.end_point")

    resources = _load_optional(
        resource_evidence, "cross_host_resource_maxima", errors
    )
    fallback = _load_optional(
        fallback_evidence, "live_fallback_under_traffic", errors
    )

    physical = release["observed_physical_offline_confirmation"]
    quality = release["observed_confirmatory_lower_bounds"]
    release_gates = release["frozen_non_live_gates"]
    internal_latency = (
        metrics.get("flow_materialization_to_feature_enqueue_latency")
        or {}
    )
    gpu_batch_latency = metrics.get("gpu_batch_round_trip_latency") or {}
    internal_p99 = internal_latency.get("p99_us")
    gpu_batch_p99 = gpu_batch_latency.get("p99_us")
    if (
        isinstance(internal_p99, bool)
        or not isinstance(internal_p99, (int, float))
    ):
        errors.append("runtime_latency.internal_feature_p99")
    elif internal_p99 > release_gates[
        "max_internal_feature_enqueue_p99_us"
    ]:
        errors.append("hard_constraint.internal_feature_p99")
    if (
        isinstance(gpu_batch_p99, bool)
        or not isinstance(gpu_batch_p99, (int, float))
    ):
        errors.append("runtime_latency.gpu_batch_p99")
    elif gpu_batch_p99 > release_gates["max_gpu_batch_p99_us"]:
        errors.append("hard_constraint.gpu_batch_p99")
    driver = metrics.get("capture_driver")
    if driver in ("xdp_skb", "xdp"):
        driver = "xdp"
    elif driver in ("af_packet", "af-packet", "af_packet_ts", "af-packet-ts"):
        driver = "af_packet"

    capture_accepted = metrics.get("packets_received")
    capture_ring_drop = metrics.get("capture_packets_dropped")
    parser_accepted = metrics.get("packets_parsed")
    parser_rejected = metrics.get("parse_rejected")
    feature_events = metrics.get("flows_emitted")
    sender_delivered = metrics.get("gpu_flows_scored")
    sender_dropped = metrics.get("fallback_flows")
    counters = {
        "offered_packets": offered,
        "nic_received_packets": nic_received,
        "nic_drop_packets": nic_drop,
        "capture_accepted_packets": capture_accepted,
        "capture_ring_drop_packets": capture_ring_drop,
        "parser_accepted_packets": parser_accepted,
        "parser_rejected_packets": parser_rejected,
        "hft_processed_packets": parser_accepted,
        "hft_drop_packets": 0,
        "feature_events_produced": feature_events,
        "sender_delivered_events": sender_delivered,
        "sender_dropped_events": sender_dropped,
    }
    payload = {
        "schema_version": 1,
        "scope": evidence_scope,
        "run_status": "complete",
        "identity": {
            "run_id": manifest.get("run_id"),
            "candidate_id": manifest.get("candidate_id"),
            "config_version": release.get("release_id"),
            "code_sha256": manifest.get("binary_sha256"),
            "input_sha256": manifest.get("input_sha256"),
            "thresholds_sha256": actual_thresholds_sha,
        },
        "capture": {
            "physical_nic_visible": capture_preflight.get(
                "physical_nic_visible"
            ),
            "virtual_interface_visible": capture_preflight.get(
                "virtual_interface_visible"
            ),
            "driver": driver,
            "interface": manifest.get("capture_interface"),
            "driver_counter_source": counter_map.get("config_version"),
            "isolated_test_traffic": (
                manifest.get("capture_interface")
                != manifest.get("replay_interface")
            ),
        },
        "frozen_thresholds": thresholds,
        "counters": counters,
        "load": {
            "packet_profile": "real",
            "observed_mpps_min": injector.get("observed_mpps_min_1s"),
            "observed_gbps_min": injector.get("observed_gbps_min_1s"),
            "rate_window_s": injector.get("rate_window_s"),
            "rate_sample_count": injector.get("rate_sample_count"),
            "interface_mtu": injector.get("interface_mtu"),
            "source_packets_read": source_packets,
            "segmented_source_packets": segmented_source_packets,
            "generated_tcp_segments": generated_tcp_segments,
            "rate_headroom_ratio": rate_headroom_ratio,
        },
        "end_to_end_latency": {
            "start_point": latency.get("start_point"),
            "end_point": latency.get("end_point"),
            "sample_count": latency.get("sample_count"),
            "p99_us": latency.get("p99_us"),
            "p999_us": latency.get("p999_us"),
            "max_us": latency.get("max_us"),
            "timestamp_provenance_verified": latency.get(
                "timestamp_provenance_verified"
            ),
            "realtime_clock_step_count": latency.get(
                "realtime_clock_step_count"
            ),
        },
        "internal_latency_not_end_to_end": internal_latency,
        "inference_batch_round_trip_latency": gpu_batch_latency,
        "resources": resources,
        "hft": {
            "budget_overrun_count": metrics.get(
                "budget_overrun_count"
            ),
            "key_flow_coverage": metrics.get("key_flow_coverage"),
        },
        "fallback": fallback,
        "independent_quality": {
            "macro_f1_min": quality["macro_f1_min"],
            "attack_recall_min": quality["attack_recall_min"],
            "benign_recall_min": quality["benign_recall_min"],
            "auprc_min": quality["auprc_min"],
            "ece_max": quality["ece_max"],
            "ground_truth_event_recall_min": quality[
                "ground_truth_event_recall_min"
            ],
        },
        "duration_s": injector.get("duration_s"),
        "composition": {
            "accepted": False,
            "errors": errors,
            "replay_tx_packets_delta": replay_tx,
            "physical_offline_reference_runs": physical.get("run_count"),
        },
    }
    audit = audit_live_run(
        payload,
        allow_virtual_diagnostic=virtual_diagnostic,
        allow_physical_diagnostic=physical_diagnostic,
    )
    combined = list(errors)
    combined.extend(
        error for error in audit.errors if error not in combined
    )
    diagnostic_errors = []
    if diagnostic:
        diagnostic_errors = [
            error
            for error in combined
            if error not in DIAGNOSTIC_OPTIONAL_ERRORS
            and not error.startswith("resources.")
            and not error.startswith("fallback.")
        ]
    diagnostic_accepted = diagnostic and not diagnostic_errors
    payload["composition"] = {
        "accepted": not combined and not diagnostic,
        "diagnostic_accepted": diagnostic_accepted,
        "diagnostic_errors": diagnostic_errors,
        "final_pareto_ingestion_allowed": False,
        "errors": combined,
        "replay_tx_packets_delta": replay_tx,
        "physical_offline_reference_runs": physical.get("run_count"),
    }
    if diagnostic_accepted:
        payload["run_status"] = "diagnostic_complete"
    else:
        payload["run_status"] = "complete" if not combined else "incomplete"
    return payload
