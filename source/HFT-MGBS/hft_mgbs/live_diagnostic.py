"""Aggregate explicitly non-production virtual-link live diagnostics."""

from __future__ import annotations

from typing import Iterable, Mapping


IDENTITY_FIELDS = (
    "candidate_id",
    "config_version",
    "code_sha256",
    "input_sha256",
    "thresholds_sha256",
)


def _number(mapping, key, errors, prefix):
    value = mapping.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append("{}.{}.missing_or_invalid".format(prefix, key))
        return None
    return float(value)


def audit_virtual_diagnostic_repeats(
    runs: Iterable[Mapping[str, object]],
    minimum_repeats: int = 3,
):
    runs = list(runs)
    errors = []
    if len(runs) < minimum_repeats:
        errors.append(
            "measured_repeats_below_{}".format(minimum_repeats)
        )
    identities = [run.get("identity") or {} for run in runs]
    for field in IDENTITY_FIELDS:
        if len({identity.get(field) for identity in identities}) > 1:
            errors.append("repeat_identity_inconsistent.{}".format(field))

    observations = []
    for index, run in enumerate(runs, 1):
        prefix = "repeat{}".format(index)
        if run.get("scope") != "virtual_link_live_diagnostic":
            errors.append("{}.scope".format(prefix))
        if run.get("run_status") != "diagnostic_complete":
            errors.append("{}.run_status".format(prefix))
        thresholds = run.get("frozen_thresholds") or {}
        if thresholds.get("diagnostic_only") is not True:
            errors.append("{}.thresholds.diagnostic_only".format(prefix))
        if thresholds.get("final_pareto_ingestion_allowed") is not False:
            errors.append(
                "{}.thresholds.final_pareto_marker".format(prefix)
            )
        capture = run.get("capture") or {}
        if capture.get("physical_nic_visible") is not False:
            errors.append("{}.capture.physical_marker".format(prefix))
        if capture.get("virtual_interface_visible") is not True:
            errors.append("{}.capture.virtual_marker".format(prefix))
        composition = run.get("composition") or {}
        if composition.get("accepted") is not False:
            errors.append("{}.composition.physical_acceptance".format(prefix))
        if composition.get("diagnostic_accepted") is not True:
            errors.append(
                "{}.composition.diagnostic_acceptance".format(prefix)
            )
        if composition.get("diagnostic_errors") != []:
            errors.append(
                "{}.composition.diagnostic_errors".format(prefix)
            )
        if composition.get("final_pareto_ingestion_allowed") is not False:
            errors.append(
                "{}.composition.final_pareto_marker".format(prefix)
            )

        counters = run.get("counters") or {}
        counter_names = (
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
        parsed = {}
        for name in counter_names:
            value = counters.get(name)
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or value < 0
            ):
                errors.append(
                    "{}.counters.{}".format(prefix, name)
                )
                parsed[name] = None
            else:
                parsed[name] = value
        if all(parsed[name] is not None for name in counter_names):
            if parsed["offered_packets"] != (
                parsed["nic_received_packets"]
                + parsed["nic_drop_packets"]
            ):
                errors.append(
                    "{}.counters.offered_to_nic".format(prefix)
                )
            if parsed["nic_received_packets"] != (
                parsed["capture_accepted_packets"]
                + parsed["capture_ring_drop_packets"]
            ):
                errors.append(
                    "{}.counters.nic_to_capture".format(prefix)
                )
            if parsed["capture_accepted_packets"] != (
                parsed["parser_accepted_packets"]
                + parsed["parser_rejected_packets"]
            ):
                errors.append(
                    "{}.counters.capture_to_parser".format(prefix)
                )
            if parsed["parser_accepted_packets"] != (
                parsed["hft_processed_packets"]
                + parsed["hft_drop_packets"]
            ):
                errors.append(
                    "{}.counters.parser_to_hft".format(prefix)
                )
            if parsed["feature_events_produced"] != (
                parsed["sender_delivered_events"]
                + parsed["sender_dropped_events"]
            ):
                errors.append(
                    "{}.counters.events_to_sender".format(prefix)
                )

        load = run.get("load") or {}
        latency = run.get("end_to_end_latency") or {}
        internal = run.get("internal_latency_not_end_to_end") or {}
        inference = run.get("inference_batch_round_trip_latency") or {}
        hft = run.get("hft") or {}
        offered = parsed.get("offered_packets")
        pipeline_drop = None
        parse_reject_rate = None
        if offered:
            pipeline_drop = (
                parsed["nic_drop_packets"]
                + parsed["capture_ring_drop_packets"]
                + parsed["hft_drop_packets"]
            ) / float(offered)
        if parsed.get("capture_accepted_packets"):
            parse_reject_rate = parsed["parser_rejected_packets"] / float(
                parsed["capture_accepted_packets"]
            )
        observations.append(
            {
                "offered_packets": offered,
                "pipeline_drop_rate": pipeline_drop,
                "parse_reject_rate": parse_reject_rate,
                "observed_mpps_min": _number(
                    load, "observed_mpps_min", errors, prefix + ".load"
                ),
                "segmented_source_packets": _number(
                    load,
                    "segmented_source_packets",
                    errors,
                    prefix + ".load",
                ),
                "end_to_end_p99_us": _number(
                    latency, "p99_us", errors, prefix + ".latency"
                ),
                "end_to_end_p999_us": _number(
                    latency, "p999_us", errors, prefix + ".latency"
                ),
                "internal_feature_p99_us": _number(
                    internal, "p99_us", errors, prefix + ".internal"
                ),
                "inference_batch_p99_us": _number(
                    inference, "p99_us", errors, prefix + ".inference"
                ),
                "key_flow_coverage": _number(
                    hft, "key_flow_coverage", errors, prefix + ".hft"
                ),
                "budget_overrun_count": _number(
                    hft, "budget_overrun_count", errors, prefix + ".hft"
                ),
            }
        )

    def maximum(name):
        values = [
            observation[name]
            for observation in observations
            if observation[name] is not None
        ]
        return max(values) if values else None

    def minimum(name):
        values = [
            observation[name]
            for observation in observations
            if observation[name] is not None
        ]
        return min(values) if values else None

    return {
        "schema_version": 1,
        "scope": "virtual_link_live_diagnostic_repeat_audit",
        "accepted": not errors,
        "errors": errors,
        "run_count": len(runs),
        "final_pareto_ingestion_allowed": False,
        "identity": identities[0] if identities else {},
        "runs": observations,
        "observed_worst_case": {
            "offered_packets_min": minimum("offered_packets"),
            "pipeline_drop_rate_max": maximum("pipeline_drop_rate"),
            "parse_reject_rate_max": maximum("parse_reject_rate"),
            "observed_mpps_min": minimum("observed_mpps_min"),
            "segmented_source_packets_max": maximum(
                "segmented_source_packets"
            ),
            "end_to_end_p99_us_max": maximum("end_to_end_p99_us"),
            "end_to_end_p999_us_max": maximum("end_to_end_p999_us"),
            "internal_feature_p99_us_max": maximum(
                "internal_feature_p99_us"
            ),
            "inference_batch_p99_us_max": maximum(
                "inference_batch_p99_us"
            ),
            "key_flow_coverage_min": minimum("key_flow_coverage"),
            "budget_overrun_count_max": maximum(
                "budget_overrun_count"
            ),
        },
    }
