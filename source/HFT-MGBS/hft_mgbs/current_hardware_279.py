"""Fail-closed evidence composer for the current BCM57810 2.79 Mpps scope.

This module is deliberately independent from the 10/12 Mpps release chain.
It recomputes one bounded operating-point candidate from six raw runs (normal
and fallback, three independent repeats each).  It never grants production
release or final-Pareto ingestion.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
MODES = ("normal", "fallback")
BACKENDS = ("xdp_skb", "tpacket_v3", "dpdk")
FALLBACK_STEPS = (
    "fault_injection_observed",
    "local_fallback_activated",
    "post_switch_traffic_observed",
    "primary_recovered",
    "fallback_state_cleared",
    "capture_backend_restored",
    "interfaces_restored",
    "final_state_verification",
)
FORBIDDEN_SELF_REPORTS = {
    "accepted",
    "qualified",
    "candidate_evidence_qualified",
    "full_pipeline_qualified",
    "production_release_accepted",
    "final_pareto_ingestion_allowed",
}


def _parse_json(raw: bytes, path: Path) -> Mapping[str, Any]:
    value = json.loads(
        raw.decode("utf-8"),
        parse_constant=lambda token: (_ for _ in ()).throw(
            ValueError("non-finite JSON constant: " + token)
        ),
    )
    if not isinstance(value, Mapping):
        raise ValueError("JSON input must be an object: " + str(path))
    return value


def _strict_json(path: Path) -> Mapping[str, Any]:
    return _parse_json(path.read_bytes(), path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _finite(value: Any, minimum: float | None = None) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if not math.isfinite(number) or (minimum is not None and number < minimum):
        return None
    return number


def _count(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _is_sha(value: Any) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def _add(errors: list[str], value: str) -> None:
    if value not in errors:
        errors.append(value)


def _resolve(root: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value or any(c in value for c in "\r\n\x00"):
        return None
    candidate = Path(value)
    candidate = candidate if candidate.is_absolute() else root / candidate
    if candidate.is_symlink():
        return None
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return None
    return resolved


def _reference(root: Path, reference: Any, prefix: str, errors: list[str]):
    if not isinstance(reference, Mapping):
        _add(errors, prefix)
        return None, None
    path = _resolve(root, reference.get("path"))
    expected = reference.get("sha256")
    if path is None:
        _add(errors, prefix + ".path")
        return None, None
    if not path.is_file() or path.is_symlink():
        _add(errors, prefix + ".file")
        return None, None
    try:
        raw = path.read_bytes()
    except OSError:
        _add(errors, prefix + ".file")
        return path, None
    if not _is_sha(expected) or hashlib.sha256(raw).hexdigest() != expected:
        _add(errors, prefix + ".sha256")
        return path, None
    try:
        return path, _parse_json(raw, path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        _add(errors, prefix + ".json")
        return path, None


def _profile(path: Path):
    raw = path.read_bytes()
    value = _parse_json(raw, path)
    if (
        value.get("schema_version") != 1
        or value.get("scope") != "hft_mgbs_current_hardware_2_79_release_profile_v1"
    ):
        raise ValueError("unsupported current-hardware profile")
    boundary_claim = value.get("claim_boundary")
    traffic = value.get("traffic_contract")
    backend = value.get("backend_policy")
    trust = value.get("evidence_trust")
    boundary = value.get("output_boundary")
    gates = value.get("hard_gates")
    if not all(isinstance(item, Mapping) for item in (boundary_claim, traffic, backend, trust, boundary, gates)):
        raise ValueError("current-hardware profile sections are missing")
    if (
        traffic.get("nominal_mpps") != 2.79
        or traffic.get("minimum_complete_windows_per_run") != 15
        or traffic.get("minimum_run_duration_s") != 15.0
        or traffic.get("minimum_latency_samples_per_window") != 1000
        or traffic.get("modes") != list(MODES)
        or traffic.get("required_repeats_per_mode") != 3
        or backend.get("allowed_backends") != list(BACKENDS)
        or boundary_claim != {
            "current_hardware_operating_point_only": True,
            "ten_mpps_or_line_rate_claim_allowed": False,
            "capture_only_is_full_pipeline": False,
            "production_release_is_out_of_scope": True,
        }
        or backend.get("xdp_probe_required") is not True
        or backend.get("xdp_candidate_required_when_probe_succeeds") is not True
        or backend.get("xdp_priority_if_full_pipeline_qualified") is not True
        or backend.get("non_xdp_backends_required_for_comparison") != [
            "tpacket_v3",
            "dpdk",
        ]
        or trust.get("self_reported_qualification_fields_forbidden") is not True
        or boundary.get("production_release_accepted") is not False
        or boundary.get("final_pareto_ingestion_allowed") is not False
    ):
        raise ValueError("current-hardware profile drift")
    expected_gates = {
        "capture": {
            "packet_drop_count_max_per_window": 0,
            "kernel_entry_to_shard_p99_us_max_per_window": 100.0,
            "kernel_entry_to_shard_p999_us_max_per_window": 500.0,
        },
        "parse": {"parse_reject_rate_max_per_window": 0.001},
        "feature": {
            "feature_update_reject_count_max_per_window": 0,
            "budget_overrun_count_max_per_window": 0,
            "key_flow_coverage_min_per_nonempty_window": 0.99,
            "key_flow_skipped_due_budget_max_per_window": 0,
            "kernel_entry_to_feature_enqueue_p99_us_max_per_window": 10000.0,
            "kernel_entry_to_feature_enqueue_p999_us_max_per_window": 50000.0,
            "internal_feature_enqueue_p99_us_max_per_window": 5000.0,
            "internal_feature_enqueue_p999_us_max_per_window": 50000.0,
        },
        "inference": {
            "end_to_end_p99_us_max_per_window": 10000.0,
            "end_to_end_p999_us_max_per_window": 50000.0,
            "gpu_queue_full_max_per_window": 0,
            "inference_batch_failure_max_per_window": 0,
        },
        "resource": {
            "samples_min_per_run": 15,
            "host_cpu_fraction_max": 0.85,
            "host_memory_fraction_max": 0.85,
            "service_gpu_fraction_max": 0.85,
            "service_gpu_memory_fraction_max": 0.85,
        },
        "quality": {
            "grouped_macro_f1_min": 0.9,
            "independent_macro_f1_min": 0.7,
            "independent_attack_recall_min": 0.72,
            "independent_benign_recall_min": 0.93,
            "independent_auprc_min": 0.45,
            "independent_ece_max": 0.05,
            "ground_truth_event_recall_min": 0.7,
        },
    }
    if any(dict(gates.get(name) or {}) != expected for name, expected in expected_gates.items()):
        raise ValueError("current-hardware hard gates drift")
    fallback = gates.get("fallback")
    if not isinstance(fallback, Mapping) or (
        fallback.get("required_steps") != list(FALLBACK_STEPS)
        or fallback.get("one_unique_trial_per_fallback_repeat") is not True
        or fallback.get("strictly_ordered_nonoverlapping_trials") is not True
        or fallback.get("recovery_ms_max") != 300.0
        or fallback.get("transition_packet_gap_max") != 0
        or fallback.get("capture_drop_during_fallback_max") != 0
        or fallback.get("primary_restored_required") is not True
        or fallback.get("host_restored_required") is not True
    ):
        raise ValueError("current-hardware fallback gate drift")
    return value, hashlib.sha256(raw).hexdigest()


def _contains_forbidden_self_report(value: Any) -> bool:
    if isinstance(value, Mapping):
        if set(value).intersection(FORBIDDEN_SELF_REPORTS):
            return True
        return any(_contains_forbidden_self_report(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_forbidden_self_report(item) for item in value)
    return False


def _quantile(histogram: Any, quantile: float, minimum_samples: int) -> float | None:
    if not isinstance(histogram, Mapping):
        return None
    bounds = histogram.get("upper_bounds_us")
    counts = histogram.get("bucket_counts")
    overflow = _count(histogram.get("overflow_count"))
    if (
        not isinstance(bounds, list)
        or not isinstance(counts, list)
        or len(bounds) != len(counts)
        or not bounds
        or overflow is None
    ):
        return None
    parsed_bounds = [_finite(value, 0) for value in bounds]
    parsed_counts = [_count(value) for value in counts]
    if any(value is None for value in parsed_bounds + parsed_counts):
        return None
    if any(parsed_bounds[index] >= parsed_bounds[index + 1] for index in range(len(parsed_bounds) - 1)):
        return None
    total = sum(parsed_counts) + overflow  # type: ignore[arg-type]
    if total < minimum_samples or overflow:
        return None
    rank = math.ceil(total * quantile)
    cumulative = 0
    for bound, count in zip(parsed_bounds, parsed_counts):
        cumulative += count  # type: ignore[operator]
        if cumulative >= rank:
            return bound
    return None


def _f1(tp: int, fp: int, fn: int) -> float:
    denominator = 2 * tp + fp + fn
    return (2 * tp / denominator) if denominator else 0.0


def _confusion(value: Any) -> tuple[int, int, int, int] | None:
    if not isinstance(value, Mapping):
        return None
    fields = tuple(_count(value.get(name)) for name in ("tp", "fp", "fn", "tn"))
    return fields if all(item is not None for item in fields) else None  # type: ignore[return-value]


def _quality(value: Any) -> Mapping[str, float] | None:
    if not isinstance(value, Mapping):
        return None
    groups = value.get("group_confusions")
    independent = _confusion(value.get("independent_confusion"))
    buckets = value.get("score_buckets_descending")
    bins = value.get("calibration_bins")
    events = value.get("events")
    if not isinstance(groups, list) or not groups or independent is None:
        return None
    group_scores = []
    for raw in groups:
        confusion = _confusion(raw)
        if confusion is None:
            return None
        tp, fp, fn, tn = confusion
        group_scores.append((_f1(tp, fp, fn) + _f1(tn, fn, fp)) / 2)
    tp, fp, fn, tn = independent
    attack_recall = tp / (tp + fn) if tp + fn else 0.0
    benign_recall = tn / (tn + fp) if tn + fp else 0.0
    macro_f1 = (_f1(tp, fp, fn) + _f1(tn, fn, fp)) / 2
    if not isinstance(buckets, list) or not buckets:
        return None
    total_positive = sum((_count(row.get("positive_count")) or 0) for row in buckets if isinstance(row, Mapping))
    if total_positive <= 0:
        return None
    seen_positive = 0
    seen_total = 0
    auprc = 0.0
    previous_recall = 0.0
    previous_score = math.inf
    for row in buckets:
        if not isinstance(row, Mapping):
            return None
        score = _finite(row.get("score"))
        positive = _count(row.get("positive_count"))
        negative = _count(row.get("negative_count"))
        if score is None or positive is None or negative is None or score > previous_score:
            return None
        previous_score = score
        seen_positive += positive
        seen_total += positive + negative
        recall = seen_positive / total_positive
        precision = seen_positive / seen_total
        auprc += (recall - previous_recall) * precision
        previous_recall = recall
    if not isinstance(bins, list) or not bins:
        return None
    calibration_total = 0
    calibration_error = 0.0
    for row in bins:
        if not isinstance(row, Mapping):
            return None
        count = _count(row.get("count"))
        confidence = _finite(row.get("confidence_sum"), 0)
        correct = _count(row.get("correct_count"))
        if count is None or confidence is None or correct is None or count == 0 or correct > count:
            return None
        calibration_total += count
        calibration_error += abs(confidence - correct)
    matched = _count(events.get("matched")) if isinstance(events, Mapping) else None
    total = _count(events.get("total")) if isinstance(events, Mapping) else None
    if not calibration_total or matched is None or total is None or not total or matched > total:
        return None
    return {
        "grouped_macro_f1": min(group_scores),
        "independent_macro_f1": macro_f1,
        "independent_attack_recall": attack_recall,
        "independent_benign_recall": benign_recall,
        "independent_auprc": auprc,
        "independent_ece": calibration_error / calibration_total,
        "ground_truth_event_recall": matched / total,
    }


def _run_metrics(payload: Mapping[str, Any], profile: Mapping[str, Any], prefix: str, errors: list[str]):
    traffic = profile["traffic_contract"]
    gates = profile["hard_gates"]
    if _contains_forbidden_self_report(payload):
        _add(errors, prefix + ".self_reported_state")
    windows = payload.get("windows")
    minimum_windows = traffic["minimum_complete_windows_per_run"]
    if not isinstance(windows, list) or len(windows) < minimum_windows:
        _add(errors, prefix + ".windows")
        return None
    rates, p99s, p999s, resources = [], [], [], []
    for index, window in enumerate(windows):
        item = f"{prefix}.windows.{index}"
        if not isinstance(window, Mapping):
            _add(errors, item)
            continue
        duration = _finite(window.get("duration_s"), 0)
        offered = _count(window.get("packets_offered"))
        received = _count(window.get("packets_received"))
        drops = [_count(window.get(name)) for name in ("nic_rx_missed", "nic_rx_errors", "socket_drops", "sequence_gaps")]
        if duration is None or duration < traffic["window_duration_s"] or offered is None or received is None or any(value is None for value in drops):
            _add(errors, item + ".counters")
            continue
        offered_rate = offered / duration / 1_000_000
        received_rate = received / duration / 1_000_000
        rates.append(min(offered_rate, received_rate))
        if offered - received != drops[3] or drops[3] != sum(drops[:3]) or any(drops):
            _add(errors, item + ".drop")
        if offered_rate < traffic["nominal_mpps"] or received_rate < traffic["nominal_mpps"]:
            _add(errors, item + ".throughput")
        parse_rejected = _count(window.get("parse_rejected"))
        if parse_rejected is None or (parse_rejected / received if received else math.inf) > gates["parse"]["parse_reject_rate_max_per_window"]:
            _add(errors, item + ".parse")
        for name, gate_name in (
            ("feature_update_rejected", "feature_update_reject_count_max_per_window"),
            ("budget_overrun_count", "budget_overrun_count_max_per_window"),
            ("key_flow_skipped_due_budget", "key_flow_skipped_due_budget_max_per_window"),
        ):
            value = _count(window.get(name))
            if value is None or value > gates["feature"][gate_name]:
                _add(errors, item + "." + name)
        eligible = _count(window.get("key_flow_eligible"))
        completed = _count(window.get("key_flow_completed"))
        if eligible is None or completed is None or eligible <= 0 or completed / eligible < gates["feature"]["key_flow_coverage_min_per_nonempty_window"]:
            _add(errors, item + ".key_flow")
        for name, section, q99_gate, q999_gate in (
            ("kernel_entry_to_shard", "capture", "kernel_entry_to_shard_p99_us_max_per_window", "kernel_entry_to_shard_p999_us_max_per_window"),
            ("kernel_entry_to_feature_enqueue", "feature", "kernel_entry_to_feature_enqueue_p99_us_max_per_window", "kernel_entry_to_feature_enqueue_p999_us_max_per_window"),
            ("internal_feature_enqueue", "feature", "internal_feature_enqueue_p99_us_max_per_window", "internal_feature_enqueue_p999_us_max_per_window"),
            ("end_to_end", "inference", "end_to_end_p99_us_max_per_window", "end_to_end_p999_us_max_per_window"),
        ):
            p99 = _quantile(window.get(name), 0.99, traffic["minimum_latency_samples_per_window"])
            p999 = _quantile(window.get(name), 0.999, traffic["minimum_latency_samples_per_window"])
            if p99 is None or p999 is None or p99 > gates[section][q99_gate] or p999 > gates[section][q999_gate]:
                _add(errors, item + "." + name)
            if name == "end_to_end" and p99 is not None and p999 is not None:
                p99s.append(p99)
                p999s.append(p999)
        for name, gate_name in (
            ("gpu_queue_full_count", "gpu_queue_full_max_per_window"),
            ("inference_batch_failure_count", "inference_batch_failure_max_per_window"),
        ):
            value = _count(window.get(name))
            if value is None or value > gates["inference"][gate_name]:
                _add(errors, item + "." + name)
        resource = window.get("resource_sample")
        if not isinstance(resource, Mapping):
            _add(errors, item + ".resource")
        else:
            values = []
            for name, gate_name in (
                ("host_cpu_fraction", "host_cpu_fraction_max"),
                ("host_memory_fraction", "host_memory_fraction_max"),
                ("service_gpu_fraction", "service_gpu_fraction_max"),
                ("service_gpu_memory_fraction", "service_gpu_memory_fraction_max"),
            ):
                number = _finite(resource.get(name), 0)
                if number is None or number > gates["resource"][gate_name]:
                    _add(errors, item + ".resource." + name)
                values.append(number or 0.0)
            resources.append(max(values))
    if len(resources) < gates["resource"]["samples_min_per_run"]:
        _add(errors, prefix + ".resource_samples")
    quality = _quality(payload.get("quality_counts"))
    if quality is None:
        _add(errors, prefix + ".quality")
    else:
        for name, value in quality.items():
            gate_name = name + ("_max" if name == "independent_ece" else "_min")
            limit = gates["quality"][gate_name]
            if (name == "independent_ece" and value > limit) or (name != "independent_ece" and value < limit):
                _add(errors, prefix + ".quality." + name)
    if (
        len(rates) < minimum_windows
        or len(p99s) < minimum_windows
        or len(p999s) < minimum_windows
        or len(resources) < gates["resource"]["samples_min_per_run"]
        or quality is None
    ):
        return None
    return {
        "throughput_mpps": min(rates),
        "p99_latency_us": max(p99s),
        "p999_latency_us": max(p999s),
        "resource_pressure": max(resources),
        "quality": quality,
    }


def _fallback_trial(payload: Mapping[str, Any], profile: Mapping[str, Any], prefix: str, errors: list[str]):
    trial = payload.get("fallback_trial")
    gate = profile["hard_gates"]["fallback"]
    if payload.get("mode") == "normal":
        if trial is not None:
            _add(errors, prefix + ".unexpected_fallback_trial")
        return None
    if not isinstance(trial, Mapping):
        _add(errors, prefix + ".fallback_trial")
        return None
    start = _count(trial.get("start_monotonic_ns"))
    end = _count(trial.get("end_monotonic_ns"))
    recovery = _finite(trial.get("recovery_ms"), 0)
    if (
        not isinstance(trial.get("trial_id"), str)
        or start is None
        or end is None
        or end <= start
        or trial.get("steps") != gate["required_steps"]
        or recovery is None
        or recovery > gate["recovery_ms_max"]
        or trial.get("transition_packet_gap") != 0
        or trial.get("capture_drop_during_fallback") != 0
        or trial.get("primary_restored") is not True
        or trial.get("host_restored") is not True
    ):
        _add(errors, prefix + ".fallback_trial")
    return (trial.get("trial_id"), start, end, recovery)


def _candidate(candidate: Any, root: Path, profile: Mapping[str, Any], profile_sha: str, campaign_id: str):
    errors: list[str] = []
    structural_valid = True
    if not isinstance(candidate, Mapping):
        return {"candidate_id": "<invalid>", "backend": None, "evaluation_complete": False, "qualified": False, "errors": ["candidate.schema"], "metrics": None}
    candidate_id = candidate.get("candidate_id")
    backend = candidate.get("backend")
    if not isinstance(candidate_id, str) or not candidate_id:
        _add(errors, "candidate.candidate_id")
        structural_valid = False
        candidate_id = "<invalid>"
    if backend not in BACKENDS:
        _add(errors, "candidate.backend")
        structural_valid = False
    if _contains_forbidden_self_report(candidate):
        _add(errors, "candidate.self_reported_state")
        structural_valid = False
    references = candidate.get("raw_runs")
    if not isinstance(references, list):
        references = []
        _add(errors, "candidate.raw_runs")
        structural_valid = False
    matrix: dict[tuple[str, int], Mapping[str, Any]] = {}
    metrics = []
    common_identity = None
    run_ids, generator_ids, content_hashes = set(), set(), set()
    fallback_trials = []
    for index, reference in enumerate(references):
        prefix = f"candidate.raw_runs.{index}"
        before_reference_errors = len(errors)
        path, payload = _reference(root, reference, prefix, errors)
        if payload is None or path is None:
            structural_valid = False
            continue
        if len(errors) != before_reference_errors:
            structural_valid = False
        content_hashes.add(_sha256(path))
        mode = payload.get("mode")
        repeat = payload.get("repeat_index")
        key = (mode, repeat)
        if (
            payload.get("schema_version") != 1
            or payload.get("scope") != "hft_mgbs_current_hardware_2_79_raw_run_v1"
            or payload.get("campaign_id") != campaign_id
            or payload.get("profile_sha256") != profile_sha
            or payload.get("candidate_id") != candidate_id
            or payload.get("backend") != backend
            or mode not in MODES
            or repeat not in (1, 2, 3)
            or key in matrix
        ):
            _add(errors, prefix + ".schema")
            structural_valid = False
            continue
        matrix[key] = payload
        if payload.get("pair_id") != f"{candidate_id}-pair-{repeat}":
            _add(errors, prefix + ".pair_id")
            structural_valid = False
        identities = tuple(payload.get(name) for name in ("hardware_identity_sha256", "code_sha256", "input_sha256", "runtime_manifest_sha256", "capture_binary_sha256"))
        if not all(_is_sha(value) for value in identities):
            _add(errors, prefix + ".identity")
            structural_valid = False
        elif common_identity is None:
            common_identity = identities
        elif identities != common_identity:
            _add(errors, prefix + ".identity_drift")
            structural_valid = False
        run_id = payload.get("run_id")
        generator_id = payload.get("generator_run_id")
        if not isinstance(run_id, str) or run_id in run_ids:
            _add(errors, prefix + ".run_id")
            structural_valid = False
        else:
            run_ids.add(run_id)
        if not isinstance(generator_id, str) or generator_id in generator_ids:
            _add(errors, prefix + ".generator_run_id")
            structural_valid = False
        else:
            generator_ids.add(generator_id)
        local_errors: list[str] = []
        derived = _run_metrics(payload, profile, prefix, local_errors)
        trial = _fallback_trial(payload, profile, prefix, local_errors)
        errors.extend(value for value in local_errors if value not in errors)
        if any(value.endswith(".self_reported_state") for value in local_errors):
            structural_valid = False
        if derived is not None:
            metrics.append(derived)
        if trial is not None:
            fallback_trials.append(trial)
    expected = {(mode, repeat) for mode in MODES for repeat in (1, 2, 3)}
    if set(matrix) != expected or len(references) != 6:
        _add(errors, "candidate.repeat_matrix")
        structural_valid = False
    if len(content_hashes) != len(references):
        _add(errors, "candidate.raw_payload_identity")
        structural_valid = False
    ordered_trials = sorted(fallback_trials, key=lambda value: value[1])
    if len(ordered_trials) != 3 or len({value[0] for value in ordered_trials}) != 3 or any(ordered_trials[i][2] >= ordered_trials[i + 1][1] for i in range(len(ordered_trials) - 1)):
        _add(errors, "candidate.fallback_trials")
    evaluation_complete = (
        structural_valid
        and
        set(matrix) == expected
        and len(metrics) == 6
        and common_identity is not None
        and len(run_ids) == 6
        and len(generator_ids) == 6
        and len(content_hashes) == 6
        and len(ordered_trials) == 3
    )
    combined = None
    if evaluation_complete:
        qualities = [item["quality"] for item in metrics]
        combined = {
            "throughput_mpps": min(item["throughput_mpps"] for item in metrics),
            "p99_latency_us": max(item["p99_latency_us"] for item in metrics),
            "p999_latency_us": max(item["p999_latency_us"] for item in metrics),
            "resource_pressure": max(item["resource_pressure"] for item in metrics),
            "fallback_recovery_s": max(item[3] for item in ordered_trials) / 1000,
            **{name: (max(value[name] for value in qualities) if name == "independent_ece" else min(value[name] for value in qualities)) for name in qualities[0]},
        }
    layer_tokens = {
        "capture": (".counters", ".drop", ".throughput", ".kernel_entry_to_shard"),
        "parse": (".parse",),
        "feature": (".feature_update_rejected", ".budget_overrun_count", ".key_flow", ".kernel_entry_to_feature_enqueue", ".internal_feature_enqueue"),
        "inference": (".end_to_end", ".gpu_queue_full_count", ".inference_batch_failure_count"),
        "resource": (".resource",),
        "quality": (".quality",),
        "fallback": (".fallback",),
    }
    layer_qualified = {
        name: evaluation_complete and not any(
            any(token in error for token in tokens) for error in errors
        )
        for name, tokens in layer_tokens.items()
    }
    return {"candidate_id": candidate_id, "backend": backend, "evaluation_complete": evaluation_complete, "layer_qualified": layer_qualified, "qualified": evaluation_complete and not errors, "errors": errors, "metrics": combined}


def _dominates(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    maximize = ("throughput_mpps", "grouped_macro_f1", "independent_macro_f1", "independent_attack_recall", "independent_benign_recall", "independent_auprc", "ground_truth_event_recall")
    minimize = ("p99_latency_us", "p999_latency_us", "resource_pressure", "fallback_recovery_s", "independent_ece")
    no_worse = all(left[name] >= right[name] for name in maximize) and all(left[name] <= right[name] for name in minimize)
    better = any(left[name] > right[name] for name in maximize) or any(left[name] < right[name] for name in minimize)
    return no_worse and better


def compose_current_hardware_audit(profile_path: Path, evidence_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        profile, profile_sha = _profile(profile_path)
        evidence_raw = evidence_path.read_bytes()
        evidence = _parse_json(evidence_raw, evidence_path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        return {"schema_version": 1, "scope": "hft_mgbs_current_hardware_2_79_candidate_evidence_audit_v1", "audit_complete": False, "candidate_evidence_qualified": False, "full_pipeline_qualified": False, "production_release_accepted": False, "final_pareto_ingestion_allowed": False, "errors": ["input:{}:{}".format(type(error).__name__, error)]}
    if evidence.get("schema_version") != 1 or evidence.get("scope") != "hft_mgbs_current_hardware_2_79_evidence_manifest_v1":
        _add(errors, "manifest.schema")
    campaign_id = evidence.get("campaign_id")
    if not isinstance(campaign_id, str) or not campaign_id:
        _add(errors, "manifest.campaign_id")
    if evidence.get("profile_sha256") != profile_sha:
        _add(errors, "manifest.profile_sha256")
    root_value = evidence.get("evidence_root")
    root_candidate = (
        Path(root_value)
        if isinstance(root_value, str) and Path(root_value).is_absolute()
        else evidence_path.parent / str(root_value)
    )
    root = root_candidate.resolve() if isinstance(root_value, str) and root_value else None
    if root is None or not root.is_dir() or root_candidate.is_symlink():
        _add(errors, "manifest.evidence_root")
        root = evidence_path.parent.resolve()
    probe_errors: list[str] = []
    _path, probe = _reference(root, evidence.get("xdp_probe"), "xdp_probe", probe_errors)
    xdp_available = False
    if probe is not None:
        if (
            probe.get("schema_version") != 1
            or probe.get("scope") != "hft_mgbs_current_hardware_2_79_xdp_probe_v1"
            or probe.get("campaign_id") != campaign_id
            or probe.get("profile_sha256") != profile_sha
            or probe.get("attempted_backend") != "xdp_skb"
            or probe.get("interface_state_before_sha256") != probe.get("interface_state_after_sha256")
            or probe.get("xdp_program_ids_before") != probe.get("xdp_program_ids_after")
        ):
            _add(probe_errors, "xdp_probe.schema_or_restoration")
        else:
            xdp_available = probe.get("attach_exit_status") == 0 and probe.get("capture_probe_exit_status") == 0 and (_count(probe.get("packets_observed")) or 0) > 0
    errors.extend(probe_errors)
    candidates = evidence.get("candidates")
    if not isinstance(candidates, list):
        candidates = []
        _add(errors, "manifest.candidates")
    audits = [_candidate(item, root, profile, profile_sha, str(campaign_id)) for item in candidates]
    ids = [item["candidate_id"] for item in audits]
    if len(ids) != len(set(ids)):
        _add(errors, "manifest.duplicate_candidate_id")
    qualified = [item for item in audits if item["qualified"]]
    xdp_qualified = [item for item in qualified if item["backend"] == "xdp_skb"]
    by_backend = {item["backend"] for item in audits if item["evaluation_complete"]}
    if xdp_available and "xdp_skb" not in by_backend:
        _add(errors, "selection.xdp_candidate_missing")
    if not xdp_qualified and not {"tpacket_v3", "dpdk"}.issubset(by_backend):
        _add(errors, "selection.non_xdp_comparison_incomplete")
    selected = None
    front: list[Mapping[str, Any]] = []
    pool = xdp_qualified if xdp_qualified else qualified
    for item in pool:
        if not any(_dominates(other["metrics"], item["metrics"]) for other in pool if other is not item):
            front.append(item)
    if front and not errors:
        front.sort(key=lambda item: (-item["metrics"]["throughput_mpps"], item["metrics"]["p999_latency_us"], item["metrics"]["p99_latency_us"], item["metrics"]["resource_pressure"], item["metrics"]["fallback_recovery_s"], item["candidate_id"]))
        selected = front[0]["candidate_id"]
    legacy = evidence.get("legacy_discovery")
    legacy_count = len(legacy) if isinstance(legacy, list) else 0
    legacy_qualified = 0
    if isinstance(legacy, list):
        for index, item in enumerate(legacy):
            if not isinstance(item, Mapping) or item.get("counts_toward_qualification") is not False:
                _add(errors, f"legacy_discovery.{index}")
            else:
                reference_errors: list[str] = []
                _reference(root, item.get("source"), f"legacy_discovery.{index}.source", reference_errors)
                errors.extend(reference_errors)
    candidate_evidence = selected is not None and not errors
    claims = evidence.get("claimed_state")
    expected_claims = {"candidate_evidence_qualified": candidate_evidence, "full_pipeline_qualified": candidate_evidence, "production_release_accepted": False, "final_pareto_ingestion_allowed": False}
    if not isinstance(claims, Mapping):
        _add(errors, "manifest.claimed_state")
    else:
        for name, expected in expected_claims.items():
            if claims.get(name) is not expected:
                _add(errors, "manifest.claim." + name)
    candidate_evidence = candidate_evidence and not errors
    return {
        "schema_version": 1,
        "scope": "hft_mgbs_current_hardware_2_79_candidate_evidence_audit_v1",
        "profile_id": profile.get("profile_id"),
        "profile_sha256": profile_sha,
        "evidence_manifest_sha256": hashlib.sha256(evidence_raw).hexdigest(),
        "audit_complete": True,
        "xdp_probe_verified": probe is not None and not probe_errors,
        "xdp_available": xdp_available,
        "legacy_discovery_count": legacy_count,
        "legacy_qualification_count": legacy_qualified,
        "candidate_audits": audits,
        "evaluated_backends": sorted(by_backend),
        "pareto_front": sorted(item["candidate_id"] for item in front) if candidate_evidence else [],
        "selected_candidate": selected if candidate_evidence else None,
        "candidate_evidence_qualified": candidate_evidence,
        "full_pipeline_qualified": candidate_evidence,
        "production_release_accepted": False,
        "final_pareto_ingestion_allowed": False,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# Current-hardware v2 evidence closure
# ---------------------------------------------------------------------------

V2_PROFILE_SCOPE = "hft_mgbs_current_hardware_2_79_release_profile_v2"
V2_RAW_INPUT_SCOPE = "hft_mgbs_current_hardware_2_79_raw_run_input_v2"
V2_RAW_RUN_SCOPE = "hft_mgbs_current_hardware_2_79_raw_run_v2"
V2_CANDIDATE_INPUT_SCOPE = "hft_mgbs_current_hardware_2_79_candidate_input_v2"
V2_CANDIDATE_AUDIT_SCOPE = "hft_mgbs_current_hardware_2_79_candidate_audit_v2"
V2_WINDOW_SCOPE = "hft_mgbs_current_hardware_2_79_window_observations_v2"
V2_RESOURCE_SCOPE = "hft_mgbs_current_hardware_2_79_resource_samples_v2"
V2_IDENTITY_SCOPE = "hft_mgbs_current_hardware_2_79_run_identity_receipt_v2"
V2_FALLBACK_SCOPE = "hft_mgbs_current_hardware_2_79_fallback_events_v2"
V2_LABEL_SCOPE = "hft_mgbs_independent_ground_truth_labels_v1"
V2_PREDICTION_SCOPE = "hft_mgbs_independent_predictions_v1"
V2_LABEL_SCOPE_V2 = "hft_mgbs_independent_ground_truth_labels_v2"
V2_PREDICTION_SCOPE_V2 = "hft_mgbs_independent_predictions_v2"
V2_QUALITY_SOURCE_SCOPE = "hft_mgbs_unsw_official_quality_source_v1"

V2_COUNTERS = (
    "pktgen_offered",
    "nic_rx_ucast",
    "nic_rx_discards",
    "socket_drops",
    "sequence_gaps",
    "packets_received",
    "packets_parsed",
    "parse_rejected",
    "flows_emitted",
    "feature_submitted",
    "feature_drops",
    "gpu_flows_enqueued",
    "gpu_flows_scored",
    "gpu_flows_failed",
    "gpu_outstanding",
    "gpu_batches_ok",
    "gpu_batches_failed",
    "gpu_queue_full",
    "key_flows_total",
    "key_flows_enqueued",
    "key_flows_enqueue_failed",
    "key_flows_scored",
    "key_flows_inference_failed",
    "key_flows_local_fallback_completed",
    "key_flows_terminal_failed",
    "key_flows_outstanding",
    "key_flows_skipped_due_budget",
    "budget_overrun_count",
)

V2_LATENCIES = (
    "packet_latency_us",
    "flow_latency_us",
    "kernel_to_feature_latency_us",
    "end_to_end_latency_us",
    "gpu_batch_latency_us",
)


def _v2_profile(path: Path) -> tuple[Mapping[str, Any], str]:
    raw = path.read_bytes()
    value = _parse_json(raw, path)
    if value.get("schema_version") != 2 or value.get("scope") != V2_PROFILE_SCOPE:
        raise ValueError("unsupported current-hardware v2 profile")
    exact = {
        ("campaign", "modes"): list(MODES),
        ("campaign", "required_repeats_per_mode"): 3,
        ("campaign", "independent_run_and_generator_identities_required"): True,
        ("traffic", "nominal_mpps"): 2.79,
        ("traffic", "window_duration_ns"): 1_000_000_000,
        ("traffic", "minimum_consecutive_complete_windows"): 15,
        ("traffic", "packet_loss_max_per_window"): 0,
        ("traffic", "parse_reject_rate_max_per_window"): 0.001,
        ("sample_gates", "packet_latency_min_per_window"): 1000,
        ("sample_gates", "flow_latency_min_per_window"): 1000,
        ("sample_gates", "kernel_to_feature_latency_min_per_window"): 1000,
        ("sample_gates", "end_to_end_latency_min_per_window"): 1000,
        ("sample_gates", "gpu_batch_latency_min_per_window"): 100,
        ("sample_gates", "physical_resource_min_per_window"): 1,
        ("sample_gates", "service_resource_min_per_window"): 1,
        ("latency_gates_us", "packet_p99_max"): 100.0,
        ("latency_gates_us", "packet_p999_max"): 500.0,
        ("latency_gates_us", "flow_p99_max"): 5000.0,
        ("latency_gates_us", "flow_p999_max"): 50000.0,
        ("latency_gates_us", "kernel_to_feature_p99_max"): 10000.0,
        ("latency_gates_us", "kernel_to_feature_p999_max"): 50000.0,
        ("latency_gates_us", "end_to_end_p99_max"): 10000.0,
        ("latency_gates_us", "end_to_end_p999_max"): 50000.0,
        ("latency_gates_us", "gpu_batch_max"): 50000.0,
        ("pipeline_gates", "feature_drop_max_per_window"): 0,
        ("pipeline_gates", "budget_overrun_max_per_window"): 0,
        ("pipeline_gates", "gpu_queue_full_max_per_window"): 0,
        ("pipeline_gates", "gpu_batch_failure_max_per_window"): 0,
        ("pipeline_gates", "key_flow_coverage_min_per_nonempty_window"): 0.99,
        ("pipeline_gates", "key_flow_budget_skip_max_per_window"): 0,
        ("fallback", "recovery_ms_max"): 300.0,
        ("fallback", "transition_packet_gap_max"): 0,
        ("fallback", "capture_drop_during_fallback_max"): 0,
        ("identity", "evidence_manifest_rehash_all_entries"): True,
        ("identity", "runtime_manifest_must_bind_model_and_service_sources"): True,
        ("quality_evidence", "separate_label_and_prediction_artifacts_required"): True,
        ("quality_evidence", "independent_holdout_required"): True,
        ("quality_evidence", "synthetic_evidence_forbidden"): True,
        ("quality_evidence", "prediction_must_bind_labels_model_and_runtime"): True,
        ("output_boundary", "production_release_accepted"): False,
        ("output_boundary", "final_pareto_ingestion_allowed"): False,
    }
    quality_schema = value.get("quality_evidence", {}).get("artifact_schema_version", 1)
    if quality_schema not in (1, 2) or isinstance(quality_schema, bool):
        raise ValueError("current-hardware v2 quality artifact schema drift")
    for keys, wanted in exact.items():
        current: Any = value
        for key in keys:
            if not isinstance(current, Mapping) or key not in current:
                raise ValueError("current-hardware v2 profile section missing: " + ".".join(keys))
            current = current[key]
        if current != wanted or type(current) is not type(wanted):
            raise ValueError("current-hardware v2 profile drift: " + ".".join(keys))
    if value.get("claim_boundary") != {
        "current_hardware_operating_point_only": True,
        "ten_mpps_or_line_rate_claim_allowed": False,
        "capture_only_is_full_pipeline": False,
        "production_release_is_out_of_scope": True,
    }:
        raise ValueError("current-hardware v2 claim boundary drift")
    if value.get("fallback", {}).get("required_steps") != list(FALLBACK_STEPS):
        raise ValueError("current-hardware v2 fallback steps drift")
    required = value.get("identity", {}).get("required_artifacts")
    expected_required = [
        "runner",
        "config",
        "capture_binary",
        "model",
        "runtime_manifest",
        "service_source",
        "engine_source",
        "service_launcher",
        "pipeline_raw",
        "diagnostic_receipt",
        "pipeline_ready",
        "execution_events",
        "identity_receipt",
        "window_observations",
        "physical_resources",
        "service_resources",
        "nic_statistics_before",
        "nic_statistics_after",
    ]
    if required != expected_required:
        raise ValueError("current-hardware v2 required artifacts drift")
    return value, hashlib.sha256(raw).hexdigest()


def _v2_fail(scope: str, error: Exception | str) -> dict[str, Any]:
    detail = error if isinstance(error, str) else f"{type(error).__name__}:{error}"
    return {
        "schema_version": 2,
        "scope": scope,
        "audit_complete": False,
        "run_qualified": False,
        "candidate_evidence_qualified": False,
        "full_pipeline_qualified": False,
        "production_release_accepted": False,
        "final_pareto_ingestion_allowed": False,
        "errors": [f"input:{detail}"],
    }


def _v2_root(input_path: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value or any(char in value for char in "\r\n\x00"):
        raise ValueError("invalid evidence_root")
    candidate = Path(value)
    candidate = candidate if candidate.is_absolute() else input_path.parent / candidate
    if candidate.is_symlink():
        raise ValueError("evidence_root must not be a symlink")
    resolved = candidate.resolve()
    if not resolved.is_dir():
        raise ValueError("evidence_root is not a directory")
    return resolved


def _v2_ref_bytes(
    root: Path,
    reference: Any,
    prefix: str,
    errors: list[str],
) -> tuple[Path | None, bytes | None]:
    if not isinstance(reference, Mapping):
        _add(errors, prefix + ".reference")
        return None, None
    path = _resolve(root, reference.get("path"))
    expected = reference.get("sha256")
    if path is None or not path.is_file() or path.is_symlink():
        _add(errors, prefix + ".path")
        return path, None
    try:
        raw = path.read_bytes()
    except OSError:
        _add(errors, prefix + ".read")
        return path, None
    if not _is_sha(expected) or hashlib.sha256(raw).hexdigest() != expected:
        _add(errors, prefix + ".sha256")
        return path, None
    return path, raw


def _v2_ref_json(
    root: Path,
    reference: Any,
    prefix: str,
    errors: list[str],
) -> tuple[Path | None, bytes | None, Mapping[str, Any] | None]:
    path, raw = _v2_ref_bytes(root, reference, prefix, errors)
    if path is None or raw is None:
        return path, raw, None
    try:
        return path, raw, _parse_json(raw, path)
    except (UnicodeError, json.JSONDecodeError, ValueError):
        _add(errors, prefix + ".json")
        return path, raw, None


def _v2_manifest_entries(
    root: Path,
    reference: Any,
    errors: list[str],
) -> tuple[Path | None, bytes | None, Mapping[str, str]]:
    path, raw = _v2_ref_bytes(root, reference, "evidence_manifest", errors)
    if path is None or raw is None:
        return path, raw, {}
    entries: dict[str, str] = {}
    try:
        text = raw.decode("utf-8")
    except UnicodeError:
        _add(errors, "evidence_manifest.encoding")
        return path, raw, {}
    for index, line in enumerate(text.splitlines()):
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\r\n\x00]+)", line)
        if match is None:
            _add(errors, f"evidence_manifest.line.{index}")
            continue
        digest, raw_name = match.groups()
        posix = PurePosixPath(raw_name)
        if posix.is_absolute() or ".." in posix.parts or raw_name in entries:
            _add(errors, f"evidence_manifest.path.{index}")
            continue
        candidate = _resolve(root, raw_name)
        if candidate is None or not candidate.is_file() or candidate.is_symlink():
            _add(errors, f"evidence_manifest.file.{index}")
            continue
        try:
            observed = _sha256(candidate)
        except OSError:
            _add(errors, f"evidence_manifest.read.{index}")
            continue
        if observed != digest:
            _add(errors, f"evidence_manifest.sha256.{raw_name}")
        entries[raw_name] = digest
    if not entries:
        _add(errors, "evidence_manifest.empty")
    return path, raw, entries


def _v2_relative_name(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _v2_positive_claim(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key in FORBIDDEN_SELF_REPORTS and item is True:
                return True
            if _v2_positive_claim(item):
                return True
    elif isinstance(value, list):
        return any(_v2_positive_claim(item) for item in value)
    return False


def _v2_int(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def _v2_series(
    value: Any,
    seen_sample_ids: set[str],
    seen_source_ids: set[str],
) -> list[float] | None:
    if not isinstance(value, list):
        return None
    parsed: list[float] = []
    for item in value:
        if not isinstance(item, Mapping):
            return None
        sample_id = item.get("sample_id")
        source_id = item.get("source_event_id")
        number = _finite(item.get("value_us"), 0)
        if (
            not isinstance(sample_id, str)
            or not sample_id
            or sample_id in seen_sample_ids
            or not isinstance(source_id, str)
            or not source_id
            or source_id in seen_source_ids
            or number is None
        ):
            return None
        seen_sample_ids.add(sample_id)
        seen_source_ids.add(source_id)
        parsed.append(number)
    return parsed


def _v2_percentile(values: Sequence[float], quantile: float) -> float:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(len(ordered) * quantile) - 1)]


def _v2_counter_snapshot(value: Any) -> dict[str, int] | None:
    if not isinstance(value, Mapping):
        return None
    result: dict[str, int] = {}
    for name in V2_COUNTERS:
        number = _v2_int(value.get(name))
        if number is None:
            return None
        result[name] = number
    return result


def _v2_ethtool_counter(raw: bytes, name: str) -> int | None:
    try:
        text = raw.decode("utf-8")
    except UnicodeError:
        return None
    matches = re.findall(rf"^\s+{re.escape(name)}:\s*(\d+)\s*$", text, flags=re.MULTILINE)
    return int(matches[-1]) if matches else None


def _v2_pktgen_packets(raw: bytes) -> int | None:
    try:
        text = raw.decode("utf-8")
    except UnicodeError:
        return None
    match = re.search(r"^Result:\s+OK:\s+\d+\([^\r\n]*\)\s+usec,\s+(\d+)\s+", text, re.MULTILINE)
    return int(match.group(1)) if match else None


def _v2_execution_events(raw: bytes) -> tuple[dict[str, datetime], list[str]]:
    errors: list[str] = []
    try:
        lines = raw.decode("utf-8").splitlines()
    except UnicodeError:
        return {}, ["execution_events.encoding"]
    if not lines or lines[0] != "utc\tevent":
        return {}, ["execution_events.header"]
    events: dict[str, datetime] = {}
    for index, line in enumerate(lines[1:], 1):
        parts = line.split("\t")
        if len(parts) != 2 or parts[1] in events:
            _add(errors, f"execution_events.line.{index}")
            continue
        try:
            timestamp = datetime.fromisoformat(parts[0].replace("Z", "+00:00"))
        except ValueError:
            _add(errors, f"execution_events.timestamp.{index}")
            continue
        events[parts[1]] = timestamp
    required = (
        "pipeline_spawned",
        "gpu_reverse_ready",
        "generator_started",
        "generator_stopped",
        "pipeline_completed",
    )
    if any(name not in events for name in required):
        _add(errors, "execution_events.required")
    elif any(events[left] >= events[right] for left, right in zip(required, required[1:])):
        _add(errors, "execution_events.order")
    return events, errors


def _v2_resource_samples(
    payload: Any,
    role: str,
    errors: list[str],
    expected_run_id: str | None = None,
) -> dict[int, list[Mapping[str, Any]]]:
    if (
        not isinstance(payload, Mapping)
        or payload.get("schema_version") != 2
        or payload.get("scope") != V2_RESOURCE_SCOPE
        or payload.get("node_role") != role
        or (expected_run_id is not None and payload.get("run_id") != expected_run_id)
        or not isinstance(payload.get("samples"), list)
    ):
        _add(errors, f"resources.{role}.schema")
        return {}
    grouped: dict[int, list[Mapping[str, Any]]] = {}
    required = (
        ("cpu_fraction", "physical_cpu_fraction_max" if role == "physical" else "service_cpu_fraction_max"),
        ("memory_fraction", "physical_memory_fraction_max" if role == "physical" else "service_memory_fraction_max"),
    )
    for index, sample in enumerate(payload["samples"]):
        if not isinstance(sample, Mapping):
            _add(errors, f"resources.{role}.sample.{index}")
            continue
        epoch = _v2_int(sample.get("epoch_second"))
        if epoch is None or any(_finite(sample.get(name), 0) is None for name, _ in required):
            _add(errors, f"resources.{role}.sample.{index}")
            continue
        if role == "service" and any(
            _finite(sample.get(name), 0) is None
            for name in ("gpu_fraction", "gpu_memory_fraction")
        ):
            _add(errors, f"resources.{role}.sample.{index}")
            continue
        grouped.setdefault(epoch, []).append(sample)
    return grouped


def _v2_runtime_binding(
    runtime: Any,
    artifacts: Mapping[str, tuple[Path | None, bytes | None]],
    errors: list[str],
) -> None:
    if not isinstance(runtime, Mapping) or runtime.get("schema_version") != 2:
        _add(errors, "runtime_manifest.schema")
        return
    bindings = {
        "model_sha256": "model",
        "service_source_sha256": "service_source",
        "numpy_engine_source_sha256": "engine_source",
        "launcher_sha256": "service_launcher",
    }
    for field, artifact in bindings.items():
        _path, raw = artifacts.get(artifact, (None, None))
        if raw is None or runtime.get(field) != hashlib.sha256(raw).hexdigest():
            _add(errors, "runtime_manifest." + field)
    if not isinstance(runtime.get("process_start_ticks"), int) or runtime.get("process_start_ticks", 0) <= 0:
        _add(errors, "runtime_manifest.process_start_ticks")
    if not isinstance(runtime.get("inference_engine"), str) or not runtime.get("inference_engine"):
        _add(errors, "runtime_manifest.inference_engine")


def _v2_fallback(
    mode: Any,
    payload: Mapping[str, Any] | None,
    profile: Mapping[str, Any],
    errors: list[str],
    expected_run_id: str | None = None,
) -> tuple[bool, str | None, int | None, int | None, float | None]:
    if mode == "normal":
        if payload is not None:
            _add(errors, "fallback.unexpected")
        return True, None, None, None, None
    if payload is None:
        _add(errors, "fallback.missing_raw_events")
        return False, None, None, None, None
    events = payload.get("events")
    if (
        payload.get("schema_version") != 2
        or payload.get("scope") != V2_FALLBACK_SCOPE
        or (expected_run_id is not None and payload.get("run_id") != expected_run_id)
        or not isinstance(events, list)
        or len(events) != len(FALLBACK_STEPS)
    ):
        _add(errors, "fallback.schema")
        return False, None, None, None, None
    names: list[Any] = []
    timestamps: list[int] = []
    for item in events:
        if not isinstance(item, Mapping) or _v2_int(item.get("monotonic_ns")) is None:
            _add(errors, "fallback.events")
            return False, None, None, None, None
        names.append(item.get("step"))
        timestamps.append(int(item["monotonic_ns"]))
    recovery_ms = (timestamps[3] - timestamps[0]) / 1_000_000 if len(timestamps) >= 4 else math.inf
    trial_id = payload.get("trial_id")
    valid = True
    checks = (
        names == list(FALLBACK_STEPS),
        all(left < right for left, right in zip(timestamps, timestamps[1:])),
        isinstance(trial_id, str) and bool(trial_id),
        recovery_ms <= profile["fallback"]["recovery_ms_max"],
        payload.get("transition_packet_gap") == profile["fallback"]["transition_packet_gap_max"],
        payload.get("capture_drop_during_fallback") == profile["fallback"]["capture_drop_during_fallback_max"],
    )
    if not all(checks):
        valid = False
        _add(errors, "fallback.gates")
    return valid, trial_id if isinstance(trial_id, str) else None, timestamps[0], timestamps[-1], recovery_ms


def _v2_longest_consecutive(windows: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    ordered = sorted(windows, key=lambda item: int(item["epoch_second"]))
    best: list[Mapping[str, Any]] = []
    current: list[Mapping[str, Any]] = []
    for window in ordered:
        epoch = int(window["epoch_second"])
        if not current or epoch == int(current[-1]["epoch_second"]) + 1:
            current.append(window)
        else:
            if len(current) > len(best):
                best = current
            current = [window]
    if len(current) > len(best):
        best = current
    return best


def _v2_window_metrics(
    payload: Any,
    pipeline: Mapping[str, Any],
    physical_resources: Mapping[int, list[Mapping[str, Any]]],
    service_resources: Mapping[int, list[Mapping[str, Any]]],
    profile: Mapping[str, Any],
    errors: list[str],
    expected_run_id: str | None = None,
    expected_generator_run_id: str | None = None,
) -> tuple[list[dict[str, Any]], Mapping[str, Any] | None]:
    if (
        not isinstance(payload, Mapping)
        or payload.get("schema_version") != 2
        or payload.get("scope") != V2_WINDOW_SCOPE
        or (expected_run_id is not None and payload.get("run_id") != expected_run_id)
        or (
            expected_generator_run_id is not None
            and payload.get("generator_run_id") != expected_generator_run_id
        )
        or not isinstance(payload.get("windows"), list)
    ):
        _add(errors, "windows.schema")
        return [], None
    raw_windows = payload["windows"]
    parsed: list[Mapping[str, Any]] = []
    seen_epochs: set[int] = set()
    for index, window in enumerate(raw_windows):
        if not isinstance(window, Mapping):
            _add(errors, f"windows.{index}.schema")
            continue
        epoch = _v2_int(window.get("epoch_second"))
        duration = _v2_int(window.get("duration_ns"))
        start = _v2_counter_snapshot(window.get("counters_start"))
        end = _v2_counter_snapshot(window.get("counters_end"))
        if (
            epoch is None
            or epoch in seen_epochs
            or duration != profile["traffic"]["window_duration_ns"]
            or start is None
            or end is None
            or any(end[name] < start[name] for name in V2_COUNTERS)
        ):
            _add(errors, f"windows.{index}.counters")
            continue
        seen_epochs.add(epoch)
        parsed.append(window)
    selected = _v2_longest_consecutive(parsed)
    minimum = profile["traffic"]["minimum_consecutive_complete_windows"]
    if len(selected) < minimum:
        _add(errors, "windows.consecutive_complete")
    if not selected:
        return [], None
    epoch_counts = pipeline.get("epoch_second_counts")
    if not isinstance(epoch_counts, Mapping):
        _add(errors, "pipeline_raw.epoch_second_counts")
        epoch_counts = {}
    traffic = profile["traffic"]
    samples = profile["sample_gates"]
    latency_gates = profile["latency_gates_us"]
    pipeline_gates = profile["pipeline_gates"]
    resource_gates = profile["resource_gates"]
    results: list[dict[str, Any]] = []
    previous_end: Mapping[str, int] | None = None
    aggregate = {name: 0 for name in V2_COUNTERS}
    seen_latency_ids: dict[str, set[str]] = {name: set() for name in V2_LATENCIES}
    seen_latency_sources: dict[str, set[str]] = {name: set() for name in V2_LATENCIES}
    for position, window in enumerate(selected):
        epoch = int(window["epoch_second"])
        prefix = f"windows.epoch.{epoch}"
        start = _v2_counter_snapshot(window["counters_start"])
        end = _v2_counter_snapshot(window["counters_end"])
        if start is None or end is None:
            continue
        if previous_end is not None and any(start[name] != previous_end[name] for name in V2_COUNTERS):
            _add(errors, prefix + ".counter_discontinuity")
        previous_end = end
        delta = {name: end[name] - start[name] for name in V2_COUNTERS}
        for name, value in delta.items():
            aggregate[name] += value
        expected_epoch = _v2_int(epoch_counts.get(str(epoch)))
        if expected_epoch is None or expected_epoch != delta["packets_received"]:
            _add(errors, prefix + ".pipeline_epoch_count")
        target_packets = int(traffic["nominal_mpps"] * 1_000_000)
        if any(
            delta[name] < target_packets
            for name in ("pktgen_offered", "nic_rx_ucast", "packets_received")
        ):
            _add(errors, prefix + ".throughput")
        if not (
            delta["pktgen_offered"]
            == delta["nic_rx_ucast"]
            == delta["packets_received"]
        ):
            _add(errors, prefix + ".delivery_conservation")
        loss = sum(
            delta[name]
            for name in ("nic_rx_discards", "socket_drops", "sequence_gaps")
        )
        if loss > traffic["packet_loss_max_per_window"]:
            _add(errors, prefix + ".packet_loss")
        if delta["packets_parsed"] + delta["parse_rejected"] != delta["packets_received"]:
            _add(errors, prefix + ".parse_conservation")
        reject_rate = (
            delta["parse_rejected"] / delta["packets_received"]
            if delta["packets_received"]
            else math.inf
        )
        if reject_rate > traffic["parse_reject_rate_max_per_window"]:
            _add(errors, prefix + ".parse_reject_rate")
        if delta["feature_submitted"] + delta["feature_drops"] != delta["flows_emitted"]:
            _add(errors, prefix + ".feature_conservation")
        if delta["feature_drops"] > pipeline_gates["feature_drop_max_per_window"]:
            _add(errors, prefix + ".feature_drop")
        if delta["budget_overrun_count"] > pipeline_gates["budget_overrun_max_per_window"]:
            _add(errors, prefix + ".budget_overrun")
        if (
            start["gpu_outstanding"] + delta["gpu_flows_enqueued"]
            != delta["gpu_flows_scored"] + delta["gpu_flows_failed"] + end["gpu_outstanding"]
        ):
            _add(errors, prefix + ".gpu_conservation")
        if delta["gpu_flows_enqueued"] > delta["feature_submitted"]:
            _add(errors, prefix + ".gpu_enqueue_exceeds_feature")
        if delta["gpu_queue_full"] > pipeline_gates["gpu_queue_full_max_per_window"]:
            _add(errors, prefix + ".gpu_queue_full")
        if delta["gpu_batches_failed"] > pipeline_gates["gpu_batch_failure_max_per_window"]:
            _add(errors, prefix + ".gpu_batch_failure")
        if delta["key_flows_total"] != delta["key_flows_enqueued"] + delta["key_flows_enqueue_failed"]:
            _add(errors, prefix + ".key_flow_admission_conservation")
        if (
            start["key_flows_outstanding"] + delta["key_flows_enqueued"]
            != delta["key_flows_scored"]
            + delta["key_flows_inference_failed"]
            + end["key_flows_outstanding"]
        ):
            _add(errors, prefix + ".key_flow_inference_conservation")
        if (
            delta["key_flows_inference_failed"]
            != delta["key_flows_local_fallback_completed"] + delta["key_flows_terminal_failed"]
        ):
            _add(errors, prefix + ".key_flow_fallback_conservation")
        completed = delta["key_flows_scored"] + delta["key_flows_local_fallback_completed"]
        coverage = completed / delta["key_flows_total"] if delta["key_flows_total"] else 1.0
        if coverage < pipeline_gates["key_flow_coverage_min_per_nonempty_window"]:
            _add(errors, prefix + ".key_flow_coverage")
        if delta["key_flows_terminal_failed"] or delta["key_flows_enqueue_failed"]:
            _add(errors, prefix + ".key_flow_terminal_loss")
        if delta["key_flows_skipped_due_budget"] > pipeline_gates["key_flow_budget_skip_max_per_window"]:
            _add(errors, prefix + ".key_flow_budget_skip")
        latency_values: dict[str, list[float]] = {}
        for name in V2_LATENCIES:
            values = _v2_series(
                window.get(name), seen_latency_ids[name], seen_latency_sources[name]
            )
            if values is None:
                _add(errors, prefix + "." + name + ".schema")
                values = []
            latency_values[name] = values
        latency_contracts = (
            ("packet_latency_us", "packet_latency_min_per_window", "packet_p99_max", "packet_p999_max"),
            ("flow_latency_us", "flow_latency_min_per_window", "flow_p99_max", "flow_p999_max"),
            ("kernel_to_feature_latency_us", "kernel_to_feature_latency_min_per_window", "kernel_to_feature_p99_max", "kernel_to_feature_p999_max"),
            ("end_to_end_latency_us", "end_to_end_latency_min_per_window", "end_to_end_p99_max", "end_to_end_p999_max"),
        )
        latency_summary: dict[str, Any] = {}
        for name, minimum_name, p99_name, p999_name in latency_contracts:
            values = latency_values[name]
            if len(values) < samples[minimum_name]:
                _add(errors, prefix + "." + name + ".sample_count")
                continue
            p99 = _v2_percentile(values, 0.99)
            p999 = _v2_percentile(values, 0.999)
            latency_summary[name] = {"samples": len(values), "p99_us": p99, "p999_us": p999}
            if p99 > latency_gates[p99_name] or p999 > latency_gates[p999_name]:
                _add(errors, prefix + "." + name + ".latency")
        gpu_values = latency_values["gpu_batch_latency_us"]
        if len(gpu_values) < samples["gpu_batch_latency_min_per_window"]:
            _add(errors, prefix + ".gpu_batch_latency_us.sample_count")
        elif max(gpu_values) > latency_gates["gpu_batch_max"]:
            _add(errors, prefix + ".gpu_batch_latency_us.max")
        latency_summary["gpu_batch_latency_us"] = {
            "samples": len(gpu_values),
            "max_us": max(gpu_values) if gpu_values else None,
        }
        physical = physical_resources.get(epoch, [])
        service = service_resources.get(epoch, [])
        if len(physical) < samples["physical_resource_min_per_window"]:
            _add(errors, prefix + ".physical_resource_samples")
        if len(service) < samples["service_resource_min_per_window"]:
            _add(errors, prefix + ".service_resource_samples")
        for role, rows, fields in (
            (
                "physical",
                physical,
                (("cpu_fraction", "physical_cpu_fraction_max"), ("memory_fraction", "physical_memory_fraction_max")),
            ),
            (
                "service",
                service,
                (
                    ("cpu_fraction", "service_cpu_fraction_max"),
                    ("memory_fraction", "service_memory_fraction_max"),
                    ("gpu_fraction", "service_gpu_fraction_max"),
                    ("gpu_memory_fraction", "service_gpu_memory_fraction_max"),
                ),
            ),
        ):
            for row in rows:
                for field, gate in fields:
                    number = _finite(row.get(field), 0)
                    if number is None or number > resource_gates[gate]:
                        _add(errors, prefix + f".{role}_resource.{field}")
        results.append(
            {
                "epoch_second": epoch,
                "duration_ns": int(window["duration_ns"]),
                "derived_counters": delta,
                "derived_loss": loss,
                "derived_parse_reject_rate": reject_rate,
                "derived_key_flow_coverage": coverage,
                "derived_latency": latency_summary,
                "physical_resource_samples": len(physical),
                "service_resource_samples": len(service),
            }
        )
    if len(results) < minimum:
        return results, None
    throughput = min(
        min(item["derived_counters"][name] for name in ("pktgen_offered", "nic_rx_ucast", "packets_received"))
        / 1_000_000
        for item in results
    )
    summary = {
        "consecutive_complete_windows": len(results),
        "first_epoch_second": results[0]["epoch_second"],
        "last_epoch_second": results[-1]["epoch_second"],
        "minimum_mpps": throughput,
        "aggregate_counters": aggregate,
    }
    return results, summary


def _v2_pipeline_cross_checks(
    pipeline: Any,
    summary: Mapping[str, Any] | None,
    errors: list[str],
) -> None:
    if (
        not isinstance(pipeline, Mapping)
        or pipeline.get("schema_version") != 1
        or pipeline.get("scope")
        != "hft_mgbs_tpacket_v3_borrowed_sharded_full_pipeline_raw"
        or pipeline.get("backend") != "tpacket_v3_packet_fanout_borrowed"
        or pipeline.get("gpu_ready_at_start") is not True
    ):
        _add(errors, "pipeline_raw.schema")
        return
    metrics = pipeline.get("pipeline_metrics")
    scheduler = pipeline.get("scheduler")
    shutdown = pipeline.get("shutdown")
    if not isinstance(metrics, Mapping):
        _add(errors, "pipeline_raw.pipeline_metrics")
        return
    checks = (
        (pipeline.get("all_workers_error_free") is True, "pipeline_raw.worker_error"),
        (pipeline.get("internal_delivery_lossless") is True, "pipeline_raw.internal_delivery"),
        (isinstance(scheduler, Mapping) and scheduler.get("fatal_error") is None, "pipeline_raw.scheduler"),
        (
            isinstance(shutdown, Mapping)
            and shutdown.get("capture_workers_joined") == shutdown.get("capture_workers_expected")
            and shutdown.get("scheduler_thread_joined") is True
            and shutdown.get("scheduler_input_channel_drained") is True
            and shutdown.get("dispatcher_finish_called") is True,
            "pipeline_raw.shutdown",
        ),
    )
    for condition, name in checks:
        if not condition:
            _add(errors, name)
    if summary is None:
        return
    aggregate = summary["aggregate_counters"]
    cross = (
        ("packets", "packets_received"),
        ("packets_parsed", "packets_parsed"),
        ("parse_rejected", "parse_rejected"),
        ("flows_closed", "flows_emitted"),
        ("feature_queue_submitted", "feature_submitted"),
        ("feature_queue_drops", "feature_drops"),
    )
    # Window observations may cover only the qualifying interior interval, so
    # their deltas cannot exceed the raw run totals.
    for raw_name, aggregate_name in cross:
        raw_value = _v2_int(pipeline.get(raw_name))
        if raw_value is None or aggregate[aggregate_name] > raw_value:
            _add(errors, "pipeline_raw.cross_check." + raw_name)
    metric_cross = (
        ("gpu_flows_enqueued", "gpu_flows_enqueued"),
        ("gpu_flows_scored", "gpu_flows_scored"),
        ("gpu_batches_ok", "gpu_batches_ok"),
        ("gpu_batches_failed", "gpu_batches_failed"),
        ("gpu_queue_full", "gpu_queue_full"),
        ("key_flows_total", "key_flows_total"),
        ("key_flows_enqueued", "key_flows_enqueued"),
        ("key_flows_enqueue_failed", "key_flows_enqueue_failed"),
        ("key_flows_scored", "key_flows_scored"),
        ("key_flows_inference_failed", "key_flows_inference_failed"),
        ("key_flows_local_fallback_completed", "key_flows_local_fallback_completed"),
        ("budget_overrun_count", "budget_overrun_count"),
    )
    for raw_name, aggregate_name in metric_cross:
        raw_value = _v2_int(metrics.get(raw_name))
        if raw_value is None or aggregate[aggregate_name] > raw_value:
            _add(errors, "pipeline_raw.cross_check." + raw_name)


def _v2_quality(
    root: Path,
    quality: Any,
    artifacts: Mapping[str, tuple[Path | None, bytes | None]],
    runtime: Mapping[str, Any] | None,
    profile: Mapping[str, Any],
    manifest_entries: Mapping[str, str],
    errors: list[str],
) -> Mapping[str, float] | None:
    if not isinstance(quality, Mapping):
        _add(errors, "quality.reference")
        return None
    _label_path, label_raw, labels = _v2_ref_json(root, quality.get("labels"), "quality.labels", errors)
    _prediction_path, prediction_raw, predictions = _v2_ref_json(
        root, quality.get("predictions"), "quality.predictions", errors
    )
    if labels is None or predictions is None or label_raw is None or prediction_raw is None:
        return None
    required_schema = profile.get("quality_evidence", {}).get("artifact_schema_version", 1)
    labels_schema = labels.get("schema_version")
    predictions_schema = predictions.get("schema_version")
    expected_label_scope = V2_LABEL_SCOPE_V2 if required_schema == 2 else V2_LABEL_SCOPE
    expected_prediction_scope = V2_PREDICTION_SCOPE_V2 if required_schema == 2 else V2_PREDICTION_SCOPE
    if (
        labels_schema != required_schema
        or labels.get("scope") != expected_label_scope
        or labels.get("source_kind") not in {"official_labels", "independent_manual_labels"}
        or labels.get("synthetic") is not False
        or labels.get("independent_holdout") is not True
        or not isinstance(labels.get("records"), list)
        or predictions_schema != required_schema
        or predictions.get("scope") != expected_prediction_scope
        or predictions.get("synthetic") is not False
        or not isinstance(predictions.get("records"), list)
    ):
        _add(errors, "quality.schema")
        return None
    if required_schema == 2:
        source_path, source_raw, source = _v2_ref_json(
            root, quality.get("source"), "quality.source", errors
        )
        if (
            source_path is None
            or source_raw is None
            or source is None
            or source.get("schema_version") != 1
            or source.get("scope") != V2_QUALITY_SOURCE_SCOPE
            or source.get("source_kind") != "official_unsw_ground_truth_and_frozen_pcap_inputs"
            or source.get("synthetic") is not False
            or source.get("portable") is not True
            or hashlib.sha256(source_raw).hexdigest() != labels.get("source_artifact_sha256")
            or labels.get("source_artifact_path") != source_path.name
            or source.get("eligible_events") != labels.get("eligible_events")
            or source.get("sample_event_relations") != labels.get("sample_event_relations")
        ):
            _add(errors, "quality.source_binding")
            return None
        relative = _v2_relative_name(root, source_path)
        if manifest_entries.get(relative) != hashlib.sha256(source_raw).hexdigest():
            _add(errors, "evidence_manifest.missing_or_drifted.quality_source")
    model_raw = artifacts.get("model", (None, None))[1]
    runtime_raw = artifacts.get("runtime_manifest", (None, None))[1]
    if (
        predictions.get("labels_sha256") != hashlib.sha256(label_raw).hexdigest()
        or model_raw is None
        or predictions.get("model_sha256") != hashlib.sha256(model_raw).hexdigest()
        or runtime_raw is None
        or predictions.get("runtime_manifest_sha256") != hashlib.sha256(runtime_raw).hexdigest()
    ):
        _add(errors, "quality.binding")
        return None
    if runtime is not None and predictions.get("model_sha256") != runtime.get("model_sha256"):
        _add(errors, "quality.runtime_model_binding")
        return None
    label_rows = labels["records"]
    prediction_rows = predictions["records"]
    label_map: dict[str, tuple[int, str, str | None]] = {}
    for row in label_rows:
        if not isinstance(row, Mapping):
            _add(errors, "quality.label_row")
            return None
        sample_id = row.get("sample_id")
        label = row.get("label")
        group = row.get("group")
        event_id = row.get("event_id")
        if (
            not isinstance(sample_id, str)
            or not sample_id
            or sample_id in label_map
            or isinstance(label, bool)
            or label not in (0, 1)
            or not isinstance(group, str)
            or not group
            or (
                required_schema == 1
                and (not isinstance(event_id, str) or not event_id)
            )
            or (required_schema == 2 and event_id is not None)
        ):
            _add(errors, "quality.label_row")
            return None
        label_map[sample_id] = (int(label), group, event_id if isinstance(event_id, str) else None)
    prediction_map: dict[str, tuple[int, float]] = {}
    for row in prediction_rows:
        if not isinstance(row, Mapping):
            _add(errors, "quality.prediction_row")
            return None
        sample_id = row.get("sample_id")
        prediction = row.get("prediction")
        score = _finite(row.get("score"), 0)
        if (
            not isinstance(sample_id, str)
            or sample_id not in label_map
            or sample_id in prediction_map
            or isinstance(prediction, bool)
            or prediction not in (0, 1)
            or score is None
            or score > 1
        ):
            _add(errors, "quality.prediction_row")
            return None
        prediction_map[sample_id] = (int(prediction), score)
    if set(label_map) != set(prediction_map) or not label_map:
        _add(errors, "quality.sample_set")
        return None
    groups: dict[str, list[int]] = {}
    tp = fp = fn = tn = 0
    scored: list[tuple[float, int]] = []
    ece_sum = 0.0
    event_truth: dict[str, bool] = {}
    event_detected: dict[str, bool] = {}
    event_relations: dict[str, set[str]] = {}
    if required_schema == 2:
        eligible = labels.get("eligible_events")
        relations = labels.get("sample_event_relations")
        if not isinstance(eligible, list) or not isinstance(relations, list) or not eligible:
            _add(errors, "quality.event_inventory")
            return None
        for row in eligible:
            if not isinstance(row, Mapping):
                _add(errors, "quality.event_inventory")
                return None
            event_id = row.get("event_id")
            if (
                not isinstance(event_id, str)
                or not event_id
                or event_id in event_truth
            ):
                _add(errors, "quality.event_inventory")
                return None
            event_truth[event_id] = True
            event_detected[event_id] = False
        seen_relations: set[tuple[str, str, str]] = set()
        for row in relations:
            if not isinstance(row, Mapping):
                _add(errors, "quality.event_relations")
                return None
            sample_id = row.get("sample_id")
            group = row.get("group")
            event_id = row.get("event_id")
            relation = (sample_id, group, event_id)
            if (
                not isinstance(sample_id, str)
                or sample_id not in label_map
                or label_map[sample_id][0] != 1
                or label_map[sample_id][1] != group
                or event_id not in event_truth
                or relation in seen_relations
            ):
                _add(errors, "quality.event_relations")
                return None
            seen_relations.add(relation)
            event_relations.setdefault(sample_id, set()).add(event_id)
        positive_ids = {sample_id for sample_id, value in label_map.items() if value[0] == 1}
        if positive_ids != set(event_relations):
            _add(errors, "quality.event_relations")
            return None
    for sample_id, (label, group, event_id) in label_map.items():
        prediction, score = prediction_map[sample_id]
        counts = groups.setdefault(group, [0, 0, 0, 0])
        if label == 1 and prediction == 1:
            tp += 1
            counts[0] += 1
        elif label == 0 and prediction == 1:
            fp += 1
            counts[1] += 1
        elif label == 1 and prediction == 0:
            fn += 1
            counts[2] += 1
        else:
            tn += 1
            counts[3] += 1
        scored.append((score, label))
        ece_sum += abs(score - label)
        if label == 1:
            if required_schema == 1 and event_id is not None:
                event_truth[event_id] = True
                event_detected[event_id] = event_detected.get(event_id, False) or prediction == 1
            elif required_schema == 2 and prediction == 1:
                for key in event_relations[sample_id]:
                    event_detected[key] = True
    group_macro = min(
        (_f1(values[0], values[1], values[2]) + _f1(values[3], values[2], values[1])) / 2
        for values in groups.values()
    )
    independent_macro = (_f1(tp, fp, fn) + _f1(tn, fn, fp)) / 2
    attack_recall = tp / (tp + fn) if tp + fn else 0.0
    benign_recall = tn / (tn + fp) if tn + fp else 0.0
    positives = tp + fn
    seen_positive = 0
    auprc = 0.0
    previous_recall = 0.0
    for index, (_score, label) in enumerate(sorted(scored, reverse=True), 1):
        seen_positive += label
        recall = seen_positive / positives if positives else 0.0
        auprc += (recall - previous_recall) * (seen_positive / index)
        previous_recall = recall
    metrics = {
        "grouped_macro_f1": group_macro,
        "independent_macro_f1": independent_macro,
        "independent_attack_recall": attack_recall,
        "independent_benign_recall": benign_recall,
        "independent_auprc": auprc,
        "independent_ece": ece_sum / len(label_map),
        "ground_truth_event_recall": (
            sum(bool(event_detected.get(key, False)) for key in event_truth) / len(event_truth)
            if event_truth
            else 0.0
        ),
    }
    for name, value in metrics.items():
        gate = name + ("_max" if name == "independent_ece" else "_min")
        limit = profile["quality_gates"][gate]
        if (gate.endswith("_max") and value > limit) or (gate.endswith("_min") and value < limit):
            _add(errors, "quality.gate." + name)
    return metrics


def compose_current_hardware_raw_run_v2(
    profile_path: Path,
    input_path: Path,
) -> dict[str, Any]:
    """Recompute and seal one run from raw, independently hashed evidence.

    The input is only a path map.  No qualification field from the runner or
    Rust process is trusted.  Missing or non-per-window evidence fails closed.
    """

    try:
        profile, profile_sha = _v2_profile(profile_path)
        input_raw = input_path.read_bytes()
        request = _parse_json(input_raw, input_path)
        if request.get("schema_version") != 2 or request.get("scope") != V2_RAW_INPUT_SCOPE:
            raise ValueError("unsupported current-hardware raw-run v2 input")
        root = _v2_root(input_path, request.get("evidence_root"))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        return _v2_fail(V2_RAW_RUN_SCOPE, error)
    errors: list[str] = []
    if request.get("profile_sha256") != profile_sha:
        _add(errors, "input.profile_sha256")
    mode = request.get("mode")
    repeat = request.get("repeat_index")
    if mode not in MODES:
        _add(errors, "input.mode")
    if repeat not in (1, 2, 3):
        _add(errors, "input.repeat_index")
    if not isinstance(request.get("campaign_id"), str) or not request.get("campaign_id"):
        _add(errors, "input.campaign_id")
    if not isinstance(request.get("candidate_id"), str) or not request.get("candidate_id"):
        _add(errors, "input.candidate_id")
    if not isinstance(request.get("backend"), str) or not request.get("backend"):
        _add(errors, "input.backend")
    if _v2_positive_claim(request):
        _add(errors, "input.positive_self_report")

    manifest_path, manifest_raw, manifest_entries = _v2_manifest_entries(
        root, request.get("evidence_manifest"), errors
    )
    artifacts_request = request.get("artifacts")
    if not isinstance(artifacts_request, Mapping):
        artifacts_request = {}
        _add(errors, "input.artifacts")
    artifacts: dict[str, tuple[Path | None, bytes | None]] = {}
    for name in profile["identity"]["required_artifacts"]:
        path, raw = _v2_ref_bytes(root, artifacts_request.get(name), f"artifacts.{name}", errors)
        artifacts[name] = (path, raw)
        if path is not None and raw is not None:
            relative = _v2_relative_name(root, path)
            if manifest_entries.get(relative) != hashlib.sha256(raw).hexdigest():
                _add(errors, f"evidence_manifest.missing_or_drifted.{name}")
    if manifest_path is not None and any(
        manifest_path.resolve() == path.resolve()
        for path, _raw in artifacts.values()
        if path is not None
    ):
        _add(errors, "evidence_manifest.self_reference")

    json_artifacts: dict[str, Mapping[str, Any] | None] = {}
    for name in (
        "runtime_manifest",
        "pipeline_raw",
        "diagnostic_receipt",
        "pipeline_ready",
        "identity_receipt",
        "window_observations",
        "physical_resources",
        "service_resources",
    ):
        path, raw = artifacts.get(name, (None, None))
        if path is None or raw is None:
            json_artifacts[name] = None
            continue
        try:
            json_artifacts[name] = _parse_json(raw, path)
        except (UnicodeError, json.JSONDecodeError, ValueError):
            json_artifacts[name] = None
            _add(errors, f"artifacts.{name}.json")

    runtime = json_artifacts["runtime_manifest"]
    _v2_runtime_binding(runtime, artifacts, errors)
    identity = json_artifacts["identity_receipt"]
    if (
        not isinstance(identity, Mapping)
        or identity.get("schema_version") != 2
        or identity.get("scope") != V2_IDENTITY_SCOPE
        or identity.get("campaign_id") != request.get("campaign_id")
        or identity.get("candidate_id") != request.get("candidate_id")
        or identity.get("mode") != mode
        or identity.get("repeat_index") != repeat
        or identity.get("backend") != request.get("backend")
        or not isinstance(identity.get("run_id"), str)
        or not identity.get("run_id")
        or not isinstance(identity.get("generator_run_id"), str)
        or not identity.get("generator_run_id")
        or not isinstance(identity.get("generator_process_start_ticks"), int)
        or identity.get("generator_process_start_ticks", 0) <= 0
        or not _is_sha(identity.get("hardware_identity_sha256"))
        or not _is_sha(identity.get("code_tree_sha256"))
    ):
        _add(errors, "identity_receipt.schema")

    receipt = json_artifacts["diagnostic_receipt"]
    if not isinstance(receipt, Mapping):
        _add(errors, "diagnostic_receipt.schema")
    else:
        if receipt.get("runner_exit_status") != 0:
            _add(errors, "diagnostic_receipt.runner_exit_status")
        if receipt.get("restoration_verified") is not True:
            _add(errors, "diagnostic_receipt.restoration")
    ready = json_artifacts["pipeline_ready"]
    if not isinstance(ready, Mapping) or ready.get("ready") is not True or ready.get("gpu_ready_at_start") is not True:
        _add(errors, "pipeline_ready.schema")

    execution_raw = artifacts.get("execution_events", (None, None))[1]
    if execution_raw is None:
        _add(errors, "execution_events.missing")
    else:
        _events, event_errors = _v2_execution_events(execution_raw)
        errors.extend(item for item in event_errors if item not in errors)

    expected_run_id = identity.get("run_id") if isinstance(identity, Mapping) else None
    expected_generator_run_id = identity.get("generator_run_id") if isinstance(identity, Mapping) else None
    physical = _v2_resource_samples(
        json_artifacts["physical_resources"], "physical", errors, expected_run_id
    )
    service = _v2_resource_samples(
        json_artifacts["service_resources"], "service", errors, expected_run_id
    )
    pipeline = json_artifacts["pipeline_raw"]
    windows, window_summary = _v2_window_metrics(
        json_artifacts["window_observations"],
        pipeline if isinstance(pipeline, Mapping) else {},
        physical,
        service,
        profile,
        errors,
        expected_run_id,
        expected_generator_run_id,
    )
    _v2_pipeline_cross_checks(pipeline, window_summary, errors)

    pktgen_total = 0
    pktgen_refs = request.get("pktgen_devices")
    if not isinstance(pktgen_refs, list) or not pktgen_refs:
        _add(errors, "pktgen_devices")
    else:
        for index, reference in enumerate(pktgen_refs):
            path, raw = _v2_ref_bytes(root, reference, f"pktgen_devices.{index}", errors)
            if path is not None and raw is not None:
                relative = _v2_relative_name(root, path)
                if manifest_entries.get(relative) != hashlib.sha256(raw).hexdigest():
                    _add(errors, f"evidence_manifest.missing_or_drifted.pktgen_devices.{index}")
                packets = _v2_pktgen_packets(raw)
                if packets is None:
                    _add(errors, f"pktgen_devices.{index}.parse")
                else:
                    pktgen_total += packets

    before_raw = artifacts.get("nic_statistics_before", (None, None))[1]
    after_raw = artifacts.get("nic_statistics_after", (None, None))[1]
    nic_delta: dict[str, int] | None = None
    if before_raw is not None and after_raw is not None:
        before_ucast = _v2_ethtool_counter(before_raw, "rx_ucast_packets")
        after_ucast = _v2_ethtool_counter(after_raw, "rx_ucast_packets")
        before_discards = _v2_ethtool_counter(before_raw, "rx_discards")
        after_discards = _v2_ethtool_counter(after_raw, "rx_discards")
        if None in (before_ucast, after_ucast, before_discards, after_discards) or after_ucast < before_ucast or after_discards < before_discards:  # type: ignore[operator]
            _add(errors, "nic_statistics.parse")
        else:
            nic_delta = {
                "rx_ucast_packets": int(after_ucast - before_ucast),  # type: ignore[operator]
                "rx_discards": int(after_discards - before_discards),  # type: ignore[operator]
            }
            if nic_delta["rx_discards"] != 0:
                _add(errors, "nic_statistics.rx_discards")
    if window_summary is not None:
        aggregate = window_summary["aggregate_counters"]
        if aggregate["pktgen_offered"] > pktgen_total:
            _add(errors, "pktgen.aggregate_cross_check")
        if nic_delta is None or aggregate["nic_rx_ucast"] > nic_delta["rx_ucast_packets"]:
            _add(errors, "nic_statistics.aggregate_cross_check")
        if nic_delta is None or aggregate["nic_rx_discards"] > nic_delta["rx_discards"]:
            _add(errors, "nic_statistics.discard_cross_check")

    fallback_payload: Mapping[str, Any] | None = None
    if mode == "fallback":
        _path, _raw, fallback_payload = _v2_ref_json(
            root, request.get("fallback_events"), "fallback_events", errors
        )
    elif request.get("fallback_events") is not None:
        _add(errors, "fallback.unexpected_reference")
    fallback_valid, trial_id, fallback_start, fallback_end, recovery_ms = _v2_fallback(
        mode, fallback_payload, profile, errors, expected_run_id
    )
    quality = _v2_quality(
        root, request.get("quality"), artifacts, runtime, profile, manifest_entries, errors
    )

    hashes = {
        name: hashlib.sha256(raw).hexdigest()
        for name, (_path, raw) in artifacts.items()
        if raw is not None
    }
    run_qualified = (
        not errors
        and isinstance(identity, Mapping)
        and window_summary is not None
        and quality is not None
        and fallback_valid
        and manifest_raw is not None
    )
    return {
        "schema_version": 2,
        "scope": V2_RAW_RUN_SCOPE,
        "profile_id": profile.get("profile_id"),
        "profile_sha256": profile_sha,
        "input_sha256": hashlib.sha256(input_raw).hexdigest(),
        "evidence_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest() if manifest_raw else None,
        "campaign_id": request.get("campaign_id"),
        "candidate_id": request.get("candidate_id"),
        "backend": request.get("backend"),
        "mode": mode,
        "repeat_index": repeat,
        "run_id": identity.get("run_id") if isinstance(identity, Mapping) else None,
        "generator_run_id": identity.get("generator_run_id") if isinstance(identity, Mapping) else None,
        "generator_process_start_ticks": identity.get("generator_process_start_ticks") if isinstance(identity, Mapping) else None,
        "hardware_identity_sha256": identity.get("hardware_identity_sha256") if isinstance(identity, Mapping) else None,
        "code_tree_sha256": identity.get("code_tree_sha256") if isinstance(identity, Mapping) else None,
        "artifact_sha256": hashes,
        "pktgen_total_packets": pktgen_total,
        "nic_delta": nic_delta,
        "window_summary": window_summary,
        "windows": windows,
        "quality": quality,
        "fallback_trial": {
            "valid": fallback_valid,
            "trial_id": trial_id,
            "start_monotonic_ns": fallback_start,
            "end_monotonic_ns": fallback_end,
            "recovery_ms": recovery_ms,
        } if mode == "fallback" else None,
        "audit_complete": True,
        "run_qualified": run_qualified,
        "candidate_evidence_qualified": False,
        "full_pipeline_qualified": False,
        "production_release_accepted": False,
        "final_pareto_ingestion_allowed": False,
        "errors": errors,
    }


def compose_current_hardware_candidate_v2(
    profile_path: Path,
    input_path: Path,
) -> dict[str, Any]:
    """Validate the exact 3 normal + 3 fallback v2 run matrix."""

    try:
        profile, profile_sha = _v2_profile(profile_path)
        input_raw = input_path.read_bytes()
        request = _parse_json(input_raw, input_path)
        if request.get("schema_version") != 2 or request.get("scope") != V2_CANDIDATE_INPUT_SCOPE:
            raise ValueError("unsupported current-hardware candidate v2 input")
        root = _v2_root(input_path, request.get("evidence_root"))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        return _v2_fail(V2_CANDIDATE_AUDIT_SCOPE, error)
    errors: list[str] = []
    if request.get("profile_sha256") != profile_sha:
        _add(errors, "input.profile_sha256")
    campaign_id = request.get("campaign_id")
    candidate_id = request.get("candidate_id")
    backend = request.get("backend")
    if not all(isinstance(value, str) and value for value in (campaign_id, candidate_id, backend)):
        _add(errors, "input.identity")
    references = request.get("raw_runs")
    if not isinstance(references, list):
        references = []
        _add(errors, "input.raw_runs")
    matrix: dict[tuple[str, int], Mapping[str, Any]] = {}
    run_ids: set[str] = set()
    generator_ids: set[tuple[str, int]] = set()
    raw_hashes: set[str] = set()
    common_identity: tuple[Any, ...] | None = None
    fallback_trials: list[tuple[str, int, int]] = []
    metrics: list[Mapping[str, Any]] = []
    for index, reference in enumerate(references):
        _path, raw, run = _v2_ref_json(root, reference, f"raw_runs.{index}", errors)
        if run is None or raw is None:
            continue
        digest = hashlib.sha256(raw).hexdigest()
        raw_hashes.add(digest)
        mode = run.get("mode")
        repeat = run.get("repeat_index")
        key = (mode, repeat)
        if (
            run.get("schema_version") != 2
            or run.get("scope") != V2_RAW_RUN_SCOPE
            or run.get("profile_sha256") != profile_sha
            or run.get("campaign_id") != campaign_id
            or run.get("candidate_id") != candidate_id
            or run.get("backend") != backend
            or run.get("audit_complete") is not True
            or run.get("run_qualified") is not True
            or run.get("errors") != []
            or mode not in MODES
            or repeat not in (1, 2, 3)
            or key in matrix
        ):
            _add(errors, f"raw_runs.{index}.schema_or_qualification")
            continue
        matrix[key] = run
        run_id = run.get("run_id")
        generator = (run.get("generator_run_id"), run.get("generator_process_start_ticks"))
        if not isinstance(run_id, str) or not run_id or run_id in run_ids:
            _add(errors, f"raw_runs.{index}.run_identity")
        else:
            run_ids.add(run_id)
        if (
            not isinstance(generator[0], str)
            or not generator[0]
            or not isinstance(generator[1], int)
            or generator[1] <= 0
            or generator in generator_ids
        ):
            _add(errors, f"raw_runs.{index}.generator_identity")
        else:
            generator_ids.add(generator)  # type: ignore[arg-type]
        identity = (
            run.get("hardware_identity_sha256"),
            run.get("code_tree_sha256"),
            (run.get("artifact_sha256") or {}).get("runner"),
            (run.get("artifact_sha256") or {}).get("config"),
            (run.get("artifact_sha256") or {}).get("capture_binary"),
            (run.get("artifact_sha256") or {}).get("model"),
            (run.get("artifact_sha256") or {}).get("service_source"),
            (run.get("artifact_sha256") or {}).get("engine_source"),
            (run.get("artifact_sha256") or {}).get("service_launcher"),
        )
        if not all(_is_sha(value) for value in identity):
            _add(errors, f"raw_runs.{index}.artifact_identity")
        elif common_identity is None:
            common_identity = identity
        elif identity != common_identity:
            _add(errors, f"raw_runs.{index}.identity_drift")
        window_summary = run.get("window_summary")
        quality = run.get("quality")
        if not isinstance(window_summary, Mapping) or not isinstance(quality, Mapping):
            _add(errors, f"raw_runs.{index}.derived_metrics")
        else:
            metrics.append({"window": window_summary, "quality": quality})
        if mode == "fallback":
            trial = run.get("fallback_trial")
            if (
                not isinstance(trial, Mapping)
                or trial.get("valid") is not True
                or not isinstance(trial.get("trial_id"), str)
                or not isinstance(trial.get("start_monotonic_ns"), int)
                or not isinstance(trial.get("end_monotonic_ns"), int)
            ):
                _add(errors, f"raw_runs.{index}.fallback_trial")
            else:
                fallback_trials.append(
                    (
                        trial["trial_id"],
                        trial["start_monotonic_ns"],
                        trial["end_monotonic_ns"],
                    )
                )
        elif run.get("fallback_trial") is not None:
            _add(errors, f"raw_runs.{index}.normal_has_fallback")
    expected = {(mode, repeat) for mode in MODES for repeat in (1, 2, 3)}
    if set(matrix) != expected or len(references) != 6:
        _add(errors, "campaign.repeat_matrix")
    if len(raw_hashes) != 6:
        _add(errors, "campaign.raw_run_identity")
    if len(run_ids) != 6:
        _add(errors, "campaign.run_identity")
    if len(generator_ids) != 6:
        _add(errors, "campaign.generator_identity")
    ordered = sorted(fallback_trials, key=lambda item: item[1])
    if (
        len(ordered) != 3
        or len({item[0] for item in ordered}) != 3
        or any(left[2] >= right[1] for left, right in zip(ordered, ordered[1:]))
    ):
        _add(errors, "campaign.fallback_trials")
    qualified = not errors and len(metrics) == 6 and common_identity is not None
    combined = None
    if qualified:
        combined = {
            "minimum_mpps": min(item["window"]["minimum_mpps"] for item in metrics),
            "minimum_consecutive_complete_windows": min(
                item["window"]["consecutive_complete_windows"] for item in metrics
            ),
            **{
                name: (
                    max(item["quality"][name] for item in metrics)
                    if name == "independent_ece"
                    else min(item["quality"][name] for item in metrics)
                )
                for name in metrics[0]["quality"]
            },
        }
    return {
        "schema_version": 2,
        "scope": V2_CANDIDATE_AUDIT_SCOPE,
        "profile_id": profile.get("profile_id"),
        "profile_sha256": profile_sha,
        "input_sha256": hashlib.sha256(input_raw).hexdigest(),
        "campaign_id": campaign_id,
        "candidate_id": candidate_id,
        "backend": backend,
        "verified_run_matrix": [
            {"mode": mode, "repeat_index": repeat, "run_id": matrix[(mode, repeat)]["run_id"]}
            for mode in MODES
            for repeat in (1, 2, 3)
            if (mode, repeat) in matrix
        ],
        "metrics": combined,
        "audit_complete": True,
        "candidate_evidence_qualified": qualified,
        "full_pipeline_qualified": qualified,
        "production_release_accepted": False,
        "final_pareto_ingestion_allowed": False,
        "errors": errors,
    }
