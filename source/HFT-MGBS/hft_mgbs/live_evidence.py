"""Strict audit for physical-NIC live-replay evidence.

The audit deliberately requires reconciled layer counters and end-to-end
latency metadata.  A boolean such as ``nic_drop_verified=true`` is not enough
to enter final Pareto selection.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Tuple


COUNTER_FIELDS = (
    "offered_packets",
    "nic_received_packets",
    "nic_drop_packets",
    "capture_accepted_packets",
    "capture_ring_drop_packets",
    "parser_accepted_packets",
    "parser_rejected_packets",
    "hft_processed_packets",
    "hft_drop_packets",
    "feature_events_produced",
    "sender_delivered_events",
    "sender_dropped_events",
)

RESOURCE_FIELDS = (
    "cpu_utilization_max",
    "gpu_utilization_max",
    "memory_utilization_max",
    "gpu_memory_utilization_max",
)

SHA256 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class LiveEvidenceAudit:
    accepted: bool
    errors: Tuple[str, ...]

    def as_dict(self) -> Dict[str, object]:
        return {"accepted": self.accepted, "errors": list(self.errors)}


def _mapping(values, name, errors):
    item = values.get(name)
    if not isinstance(item, Mapping):
        errors.append("{}.missing_or_invalid".format(name))
        return {}
    return item


def _number(values, name, errors, minimum=None, maximum=None):
    value = values.get(name)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append("{}.missing_or_invalid".format(name))
        return None
    value = float(value)
    if minimum is not None and value < minimum:
        errors.append("{}.below_minimum".format(name))
    if maximum is not None and value > maximum:
        errors.append("{}.above_maximum".format(name))
    return value


def _integer(values, name, errors):
    value = values.get(name)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        errors.append("{}.missing_or_invalid".format(name))
        return None
    return value


def _require_equal(errors, name, left, right):
    if left is not None and right is not None and left != right:
        errors.append("counter_reconciliation.{}".format(name))


def audit_live_run(values: Mapping[str, object]) -> LiveEvidenceAudit:
    errors = []
    if values.get("schema_version") != 1:
        errors.append("schema_version")
    if values.get("scope") != "physical_nic_live_replay":
        errors.append("scope")
    if values.get("run_status") != "complete":
        errors.append("run_status")

    identity = _mapping(values, "identity", errors)
    for field in ("run_id", "candidate_id", "config_version"):
        if not str(identity.get(field, "")).strip():
            errors.append("identity.{}".format(field))
    for field in ("code_sha256", "input_sha256", "thresholds_sha256"):
        if not SHA256.fullmatch(str(identity.get(field, ""))):
            errors.append("identity.{}".format(field))

    capture = _mapping(values, "capture", errors)
    if capture.get("physical_nic_visible") is not True:
        errors.append("capture.physical_nic_visible")
    if capture.get("driver") not in ("xdp", "af_packet"):
        errors.append("capture.driver")
    if not str(capture.get("interface", "")).strip():
        errors.append("capture.interface")
    if not str(capture.get("driver_counter_source", "")).strip():
        errors.append("capture.driver_counter_source")
    if capture.get("isolated_test_traffic") is not True:
        errors.append("capture.isolated_test_traffic")

    thresholds = _mapping(values, "frozen_thresholds", errors)
    if thresholds.get("frozen") is not True:
        errors.append("frozen_thresholds.frozen")
    target_mpps = thresholds.get("target_load_mpps")
    target_gbps = thresholds.get("target_load_gbps")
    if target_mpps is None and target_gbps is None:
        errors.append("frozen_thresholds.target_load")
    if target_mpps is not None:
        target_mpps = _number(
            thresholds, "target_load_mpps", errors, minimum=0.0
        )
        if target_mpps == 0:
            errors.append("frozen_thresholds.target_load_mpps.zero")
    if target_gbps is not None:
        target_gbps = _number(
            thresholds, "target_load_gbps", errors, minimum=0.0
        )
        if target_gbps == 0:
            errors.append("frozen_thresholds.target_load_gbps.zero")
    max_drop_rate = _number(
        thresholds, "max_pipeline_drop_rate", errors, minimum=0.0, maximum=1.0
    )
    max_parse_reject_rate = _number(
        thresholds, "max_parse_reject_rate", errors, minimum=0.0, maximum=1.0
    )
    max_p99 = _number(
        thresholds, "max_end_to_end_p99_us", errors, minimum=0.0
    )
    max_p999 = _number(
        thresholds, "max_end_to_end_p999_us", errors, minimum=0.0
    )
    if max_p99 is not None and max_p999 is not None and max_p999 < max_p99:
        errors.append("frozen_thresholds.p999_below_p99")
    max_budget_overruns = _integer(
        thresholds, "max_budget_overrun_count", errors
    )
    min_key_coverage = _number(
        thresholds, "min_key_flow_coverage", errors, minimum=0.0, maximum=1.0
    )
    max_recovery = _number(
        thresholds, "max_fallback_recovery_s", errors, minimum=0.0
    )
    min_quality = _number(
        thresholds, "min_independent_macro_f1", errors, minimum=0.0, maximum=1.0
    )
    min_event_recall = _number(
        thresholds,
        "min_ground_truth_event_recall",
        errors,
        minimum=0.0,
        maximum=1.0,
    )
    min_duration = _number(
        thresholds, "min_run_duration_s", errors, minimum=0.0
    )
    if min_duration == 0:
        errors.append("frozen_thresholds.min_run_duration_s.zero")
    resource_limits = _mapping(thresholds, "resource_max", errors)
    for field in RESOURCE_FIELDS:
        _number(resource_limits, field, errors, minimum=0.0, maximum=1.0)

    counters = _mapping(values, "counters", errors)
    parsed_counters = {
        field: _integer(counters, field, errors) for field in COUNTER_FIELDS
    }
    offered = parsed_counters["offered_packets"]
    if offered == 0:
        errors.append("counters.offered_packets.zero")
    _require_equal(
        errors,
        "offered_to_nic",
        offered,
        None
        if parsed_counters["nic_received_packets"] is None
        or parsed_counters["nic_drop_packets"] is None
        else parsed_counters["nic_received_packets"]
        + parsed_counters["nic_drop_packets"],
    )
    _require_equal(
        errors,
        "nic_to_capture",
        parsed_counters["nic_received_packets"],
        None
        if parsed_counters["capture_accepted_packets"] is None
        or parsed_counters["capture_ring_drop_packets"] is None
        else parsed_counters["capture_accepted_packets"]
        + parsed_counters["capture_ring_drop_packets"],
    )
    _require_equal(
        errors,
        "capture_to_parser",
        parsed_counters["capture_accepted_packets"],
        None
        if parsed_counters["parser_accepted_packets"] is None
        or parsed_counters["parser_rejected_packets"] is None
        else parsed_counters["parser_accepted_packets"]
        + parsed_counters["parser_rejected_packets"],
    )
    _require_equal(
        errors,
        "parser_to_hft",
        parsed_counters["parser_accepted_packets"],
        None
        if parsed_counters["hft_processed_packets"] is None
        or parsed_counters["hft_drop_packets"] is None
        else parsed_counters["hft_processed_packets"]
        + parsed_counters["hft_drop_packets"],
    )
    _require_equal(
        errors,
        "events_to_sender",
        parsed_counters["feature_events_produced"],
        None
        if parsed_counters["sender_delivered_events"] is None
        or parsed_counters["sender_dropped_events"] is None
        else parsed_counters["sender_delivered_events"]
        + parsed_counters["sender_dropped_events"],
    )
    if offered:
        pipeline_drops = sum(
            parsed_counters[field] or 0
            for field in (
                "nic_drop_packets",
                "capture_ring_drop_packets",
                "hft_drop_packets",
            )
        )
        if (
            max_drop_rate is not None
            and pipeline_drops / float(offered) > max_drop_rate
        ):
            errors.append("hard_constraint.pipeline_drop_rate")
        capture_accepted = parsed_counters["capture_accepted_packets"]
        parser_rejected = parsed_counters["parser_rejected_packets"]
        if (
            capture_accepted
            and parser_rejected is not None
            and max_parse_reject_rate is not None
            and parser_rejected / float(capture_accepted)
            > max_parse_reject_rate
        ):
            errors.append("hard_constraint.parse_reject_rate")

    load = _mapping(values, "load", errors)
    if load.get("packet_profile") not in ("64B", "IMIX", "real"):
        errors.append("load.packet_profile")
    if target_mpps is not None:
        observed_mpps = _number(
            load, "observed_mpps_min", errors, minimum=0.0
        )
        if (
            observed_mpps is not None
            and observed_mpps < target_mpps
        ):
            errors.append("hard_constraint.target_load_mpps")
    if target_gbps is not None:
        observed_gbps = _number(
            load, "observed_gbps_min", errors, minimum=0.0
        )
        if (
            observed_gbps is not None
            and observed_gbps < target_gbps
        ):
            errors.append("hard_constraint.target_load_gbps")

    latency = _mapping(values, "end_to_end_latency", errors)
    if latency.get("start_point") not in (
        "nic_hardware_timestamp",
        "kernel_receive_monotonic",
    ):
        errors.append("end_to_end_latency.start_point")
    if latency.get("end_point") != "feature_event_enqueued":
        errors.append("end_to_end_latency.end_point")
    sample_count = _integer(latency, "sample_count", errors)
    if sample_count == 0:
        errors.append("end_to_end_latency.sample_count.zero")
    p99 = _number(latency, "p99_us", errors, minimum=0.0)
    p999 = _number(latency, "p999_us", errors, minimum=0.0)
    maximum_latency = _number(latency, "max_us", errors, minimum=0.0)
    if p99 is not None and p999 is not None and p999 < p99:
        errors.append("end_to_end_latency.p999_below_p99")
    if p999 is not None and maximum_latency is not None and maximum_latency < p999:
        errors.append("end_to_end_latency.max_below_p999")
    if max_p99 is not None and p99 is not None and p99 > max_p99:
        errors.append("hard_constraint.end_to_end_p99")
    if max_p999 is not None and p999 is not None and p999 > max_p999:
        errors.append("hard_constraint.end_to_end_p999")

    resources = _mapping(values, "resources", errors)
    for field in RESOURCE_FIELDS:
        observed = _number(resources, field, errors, minimum=0.0, maximum=1.0)
        limit = resource_limits.get(field)
        if (
            observed is not None
            and isinstance(limit, (int, float))
            and observed > float(limit)
        ):
            errors.append("hard_constraint.{}".format(field))

    hft = _mapping(values, "hft", errors)
    budget_overruns = _integer(hft, "budget_overrun_count", errors)
    key_coverage = _number(
        hft, "key_flow_coverage", errors, minimum=0.0, maximum=1.0
    )
    if (
        budget_overruns is not None
        and max_budget_overruns is not None
        and budget_overruns > max_budget_overruns
    ):
        errors.append("hard_constraint.budget_overrun_count")
    if (
        key_coverage is not None
        and min_key_coverage is not None
        and key_coverage < min_key_coverage
    ):
        errors.append("hard_constraint.key_flow_coverage")

    fallback = _mapping(values, "fallback", errors)
    for field in (
        "activation_verified",
        "real_traffic_during_fallback_verified",
        "same_candidate_pipeline_verified",
        "recovery_verified",
    ):
        if fallback.get(field) is not True:
            errors.append("fallback.{}".format(field))
    recovery = _number(
        fallback, "recovery_s_max", errors, minimum=0.0
    )
    if (
        recovery is not None
        and max_recovery is not None
        and recovery > max_recovery
    ):
        errors.append("hard_constraint.fallback_recovery_s")

    quality = _mapping(values, "independent_quality", errors)
    macro_f1 = _number(
        quality, "macro_f1_min", errors, minimum=0.0, maximum=1.0
    )
    event_recall = _number(
        quality,
        "ground_truth_event_recall_min",
        errors,
        minimum=0.0,
        maximum=1.0,
    )
    if (
        macro_f1 is not None
        and min_quality is not None
        and macro_f1 < min_quality
    ):
        errors.append("hard_constraint.independent_macro_f1")
    if (
        event_recall is not None
        and min_event_recall is not None
        and event_recall < min_event_recall
    ):
        errors.append("hard_constraint.ground_truth_event_recall")

    duration_s = _number(values, "duration_s", errors, minimum=0.0)
    if (
        duration_s is not None
        and min_duration is not None
        and duration_s < min_duration
    ):
        errors.append("hard_constraint.run_duration")
    return LiveEvidenceAudit(not errors, tuple(errors))


def audit_live_repeats(
    runs: Iterable[Mapping[str, object]], minimum_repeats: int = 3
) -> LiveEvidenceAudit:
    runs = list(runs)
    errors = []
    if len(runs) < minimum_repeats:
        errors.append("measured_repeats_below_{}".format(minimum_repeats))
    identities = [run.get("identity") or {} for run in runs]
    for field in (
        "candidate_id",
        "config_version",
        "code_sha256",
        "input_sha256",
        "thresholds_sha256",
    ):
        if len({identity.get(field) for identity in identities}) > 1:
            errors.append("repeat_identity_inconsistent.{}".format(field))
    for index, run in enumerate(runs, 1):
        audit = audit_live_run(run)
        errors.extend(
            "repeat{}.{}".format(index, error) for error in audit.errors
        )
    return LiveEvidenceAudit(not errors, tuple(errors))
