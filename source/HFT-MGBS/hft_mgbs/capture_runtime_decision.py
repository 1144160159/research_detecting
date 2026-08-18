"""Fail-closed XDP-primary/DPDK-fallback runtime decision contract.

The module only decides whether a transition is admissible.  It never binds a
PCI function, attaches XDP, changes queues, or starts a data-plane process.
Those mutations belong to a separate, state-snapshotting executor.
"""

from __future__ import annotations

import math
import re
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple


NATIVE_XDP_BACKEND = "native_af_xdp_zerocopy"
GENERIC_XDP_BACKEND = "generic_xdp_skb"
DPDK_BACKEND = "dpdk"
NO_BACKEND = "none"
KNOWN_BACKENDS = {
    NATIVE_XDP_BACKEND,
    GENERIC_XDP_BACKEND,
    DPDK_BACKEND,
    NO_BACKEND,
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class RuntimeDecisionContractError(ValueError):
    """Raised when an observation cannot be safely interpreted."""


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RuntimeDecisionContractError(f"{path} must be an object")
    return value


def _sequence(value: Any, path: str) -> Sequence[Any]:
    if not isinstance(value, list):
        raise RuntimeDecisionContractError(f"{path} must be an array")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise RuntimeDecisionContractError(f"{path} must be a non-empty string")
    return value


def _boolean(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise RuntimeDecisionContractError(f"{path} must be a boolean")
    return value


def _number(value: Any, path: str, *, minimum: Optional[float] = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RuntimeDecisionContractError(f"{path} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise RuntimeDecisionContractError(f"{path} must be a finite number")
    if minimum is not None and result < minimum:
        raise RuntimeDecisionContractError(f"{path} must be >= {minimum}")
    return result


def _integer(value: Any, path: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise RuntimeDecisionContractError(f"{path} must be an integer >= {minimum}")
    return value


def _timestamp(value: Any, path: str) -> datetime:
    text = _string(value, path)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as error:
        raise RuntimeDecisionContractError(f"{path} must be an ISO-8601 timestamp") from error
    if parsed.tzinfo is None:
        raise RuntimeDecisionContractError(f"{path} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _requirements(policy: Mapping[str, Any]) -> Tuple[Mapping[str, Any], ...]:
    if _integer(policy.get("schema_version"), "policy.schema_version", minimum=1) != 1:
        raise RuntimeDecisionContractError("policy.schema_version must equal 1")
    _string(policy.get("policy_id"), "policy.policy_id")
    priority = _sequence(policy.get("backend_priority"), "policy.backend_priority")
    if list(priority) != [NATIVE_XDP_BACKEND, DPDK_BACKEND]:
        raise RuntimeDecisionContractError(
            "policy.backend_priority must be native AF_XDP zero-copy then DPDK"
        )
    guards = _mapping(policy.get("semantic_guards"), "policy.semantic_guards")
    expected_guards = {
        "generic_xdp_skb_is_native": False,
        "generic_xdp_skb_is_zerocopy": False,
        "generic_xdp_skb_production_eligible": False,
        "empty_key_flow_denominator_is_qualified": False,
        "same_pf_rebind_is_automatic": False,
    }
    for name, expected in expected_guards.items():
        if _boolean(guards.get(name), f"policy.semantic_guards.{name}") is not expected:
            raise RuntimeDecisionContractError(
                f"policy.semantic_guards.{name} must remain {str(expected).lower()}"
            )
    freshness = _mapping(policy.get("freshness"), "policy.freshness")
    _number(freshness.get("observation_max_age_s"), "policy.freshness.observation_max_age_s", minimum=0)
    _number(freshness.get("capability_max_age_s"), "policy.freshness.capability_max_age_s", minimum=0)
    _number(freshness.get("max_future_clock_skew_s"), "policy.freshness.max_future_clock_skew_s", minimum=0)
    xdp = _mapping(policy.get("xdp_requirements"), "policy.xdp_requirements")
    if _string(xdp.get("attach_mode"), "policy.xdp_requirements.attach_mode") != "native":
        raise RuntimeDecisionContractError("XDP attach mode requirement must remain native")
    if _string(xdp.get("af_xdp_bind_mode"), "policy.xdp_requirements.af_xdp_bind_mode") != "zerocopy":
        raise RuntimeDecisionContractError("AF_XDP bind mode requirement must remain zerocopy")
    _integer(xdp.get("min_rx_queues"), "policy.xdp_requirements.min_rx_queues", minimum=1)
    dpdk = _mapping(policy.get("dpdk_requirements"), "policy.dpdk_requirements")
    _integer(dpdk.get("min_rx_queues"), "policy.dpdk_requirements.min_rx_queues", minimum=1)
    _number(dpdk.get("capture_headroom_mpps"), "policy.dpdk_requirements.capture_headroom_mpps", minimum=0)
    online = _mapping(policy.get("online_gates"), "policy.online_gates")
    _integer(online.get("evaluation_windows"), "policy.online_gates.evaluation_windows", minimum=1)
    _number(online.get("max_capture_drop_rate"), "policy.online_gates.max_capture_drop_rate", minimum=0)
    _integer(online.get("max_poll_errors"), "policy.online_gates.max_poll_errors")
    _integer(online.get("max_invalid_descriptors"), "policy.online_gates.max_invalid_descriptors")
    _integer(online.get("max_ring_full"), "policy.online_gates.max_ring_full")
    _integer(online.get("max_fill_empty"), "policy.online_gates.max_fill_empty")
    cpu_max = _number(online.get("max_host_cpu_fraction"), "policy.online_gates.max_host_cpu_fraction", minimum=0)
    memory_max = _number(online.get("max_memory_fraction"), "policy.online_gates.max_memory_fraction", minimum=0)
    if cpu_max > 1 or memory_max > 1:
        raise RuntimeDecisionContractError("CPU and memory fraction gates must be <= 1")
    _integer(online.get("max_budget_overrun_count"), "policy.online_gates.max_budget_overrun_count")
    _number(online.get("max_fallback_recovery_ms"), "policy.online_gates.max_fallback_recovery_ms", minimum=0)
    _number(online.get("kernel_to_feature_p99_us_max"), "policy.online_gates.kernel_to_feature_p99_us_max", minimum=0)
    _number(online.get("kernel_to_feature_p999_us_max"), "policy.online_gates.kernel_to_feature_p999_us_max", minimum=0)
    coverage = _number(online.get("min_key_flow_coverage"), "policy.online_gates.min_key_flow_coverage", minimum=0)
    if coverage > 1:
        raise RuntimeDecisionContractError("policy.online_gates.min_key_flow_coverage must be <= 1")
    _string(online.get("key_flow_coverage_basis"), "policy.online_gates.key_flow_coverage_basis")
    switch = _mapping(policy.get("switch_safety"), "policy.switch_safety")
    auto = _sequence(switch.get("automatic_topologies"), "policy.switch_safety.automatic_topologies")
    maintenance = _sequence(switch.get("maintenance_topologies"), "policy.switch_safety.maintenance_topologies")
    if "same_pf_rebind" in auto or "same_adapter_all_pf_rebind" in auto:
        raise RuntimeDecisionContractError("same-PF/all-PF rebind cannot be automatic")
    if not all(isinstance(item, str) and item for item in [*auto, *maintenance]):
        raise RuntimeDecisionContractError("switch topologies must be non-empty strings")
    handoff = _sequence(switch.get("required_handoff_flags"), "policy.switch_safety.required_handoff_flags")
    if not handoff or not all(isinstance(item, str) and item for item in handoff):
        raise RuntimeDecisionContractError("required handoff flags must be non-empty strings")
    return freshness, xdp, dpdk, online, switch


def _fresh(
    timestamp_value: Any,
    path: str,
    reference: datetime,
    maximum_age_s: float,
    future_skew_s: float,
) -> Tuple[bool, str]:
    observed = _timestamp(timestamp_value, path)
    age = (reference - observed).total_seconds()
    if age < -future_skew_s:
        return False, f"{path}.future"
    if age > maximum_age_s:
        return False, f"{path}.stale"
    return True, ""


def _xdp_capability(
    capability: Mapping[str, Any],
    requirements: Mapping[str, Any],
    observation_time: datetime,
    freshness: Mapping[str, Any],
) -> Dict[str, Any]:
    reasons: List[str] = []
    is_fresh, freshness_reason = _fresh(
        capability.get("observed_at_utc"),
        "observation.capabilities.xdp.observed_at_utc",
        observation_time,
        _number(freshness["capability_max_age_s"], "policy.freshness.capability_max_age_s"),
        _number(freshness["max_future_clock_skew_s"], "policy.freshness.max_future_clock_skew_s"),
    )
    if not is_fresh:
        reasons.append(freshness_reason)
    attach_mode = _string(capability.get("attach_mode"), "observation.capabilities.xdp.attach_mode")
    bind_mode = _string(capability.get("af_xdp_bind_mode"), "observation.capabilities.xdp.af_xdp_bind_mode")
    native_attach = _boolean(
        capability.get("native_attach_succeeded"),
        "observation.capabilities.xdp.native_attach_succeeded",
    )
    forced_zc = _boolean(
        capability.get("forced_zerocopy_bind_succeeded"),
        "observation.capabilities.xdp.forced_zerocopy_bind_succeeded",
    )
    copy_active = _boolean(capability.get("copy_mode_active"), "observation.capabilities.xdp.copy_mode_active")
    queues = _integer(capability.get("rx_queue_count"), "observation.capabilities.xdp.rx_queue_count")
    restored = _boolean(
        capability.get("probe_restoration_verified"),
        "observation.capabilities.xdp.probe_restoration_verified",
    )
    isolated = _boolean(
        capability.get("management_isolated"),
        "observation.capabilities.xdp.management_isolated",
    )
    if attach_mode != requirements["attach_mode"]:
        reasons.append("xdp.attach_mode_not_native")
    if not native_attach:
        reasons.append("xdp.native_attach_not_verified")
    if bind_mode != requirements["af_xdp_bind_mode"]:
        reasons.append("xdp.bind_mode_not_zerocopy")
    if not forced_zc:
        reasons.append("xdp.forced_zerocopy_bind_not_verified")
    if copy_active:
        reasons.append("xdp.copy_mode_active")
    if queues < _integer(requirements["min_rx_queues"], "policy.xdp_requirements.min_rx_queues", minimum=1):
        reasons.append("xdp.rx_queues_insufficient")
    if not restored:
        reasons.append("xdp.capability_probe_not_restored")
    if not isolated:
        reasons.append("xdp.interface_not_management_isolated")
    return {
        "eligible": not reasons,
        "native_verified": attach_mode == "native" and native_attach,
        "zerocopy_verified": bind_mode == "zerocopy" and forced_zc and not copy_active,
        "attach_mode": attach_mode,
        "af_xdp_bind_mode": bind_mode,
        "reasons": reasons,
    }


def _dpdk_capability(
    capability: Mapping[str, Any],
    requirements: Mapping[str, Any],
    observation_time: datetime,
    freshness: Mapping[str, Any],
) -> Dict[str, Any]:
    reasons: List[str] = []
    is_fresh, freshness_reason = _fresh(
        capability.get("observed_at_utc"),
        "observation.capabilities.dpdk.observed_at_utc",
        observation_time,
        _number(freshness["capability_max_age_s"], "policy.freshness.capability_max_age_s"),
        _number(freshness["max_future_clock_skew_s"], "policy.freshness.max_future_clock_skew_s"),
    )
    if not is_fresh:
        reasons.append(freshness_reason)
    topology = _string(capability.get("topology"), "observation.capabilities.dpdk.topology")
    pmd_probe = _boolean(capability.get("pmd_probe_succeeded"), "observation.capabilities.dpdk.pmd_probe_succeeded")
    capacity = _boolean(capability.get("capacity_qualified"), "observation.capabilities.dpdk.capacity_qualified")
    min_rx = _number(capability.get("observed_min_rx_mpps"), "observation.capabilities.dpdk.observed_min_rx_mpps", minimum=0)
    queues = _integer(capability.get("rx_queue_count"), "observation.capabilities.dpdk.rx_queue_count")
    rss = _boolean(capability.get("rss_supported"), "observation.capabilities.dpdk.rss_supported")
    queue_coverage = _boolean(
        capability.get("rx_queue_coverage_qualified"),
        "observation.capabilities.dpdk.rx_queue_coverage_qualified",
    )
    latest_diagnostic = capability.get("latest_symmetric_q2_tcp_diagnostic")
    if latest_diagnostic is not None:
        diagnostic = _mapping(
            latest_diagnostic,
            "observation.capabilities.dpdk.latest_symmetric_q2_tcp_diagnostic",
        )
        rx_packets = _sequence(
            diagnostic.get("rx_queue_packets"),
            "observation.capabilities.dpdk.latest_symmetric_q2_tcp_diagnostic.rx_queue_packets",
        )
        if len(rx_packets) < 2 or any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in rx_packets
        ):
            raise RuntimeDecisionContractError(
                "latest DPDK diagnostic RX queue counters are invalid"
            )
        if diagnostic.get("diagnostic_passed") is True and any(
            value == 0 for value in rx_packets
        ):
            raise RuntimeDecisionContractError(
                "latest DPDK diagnostic cannot pass with an idle required RX queue"
            )
    zero_errors = _boolean(capability.get("zero_error_probe"), "observation.capabilities.dpdk.zero_error_probe")
    restored = _boolean(
        capability.get("restoration_verified"),
        "observation.capabilities.dpdk.restoration_verified",
    )
    isolated = _boolean(
        capability.get("management_isolated"),
        "observation.capabilities.dpdk.management_isolated",
    )
    standby = _boolean(
        capability.get("standby_preflight_passed"),
        "observation.capabilities.dpdk.standby_preflight_passed",
    )
    binary_sha256 = _string(capability.get("binary_sha256"), "observation.capabilities.dpdk.binary_sha256")
    if not pmd_probe:
        reasons.append("dpdk.pmd_probe_failed")
    if not capacity:
        reasons.append("dpdk.capacity_not_qualified")
    required_mpps = _number(
        requirements["capture_headroom_mpps"],
        "policy.dpdk_requirements.capture_headroom_mpps",
        minimum=0,
    )
    if min_rx < required_mpps:
        reasons.append("dpdk.rx_capacity_insufficient")
    if queues < _integer(requirements["min_rx_queues"], "policy.dpdk_requirements.min_rx_queues", minimum=1):
        reasons.append("dpdk.rx_queues_insufficient")
    if not rss:
        reasons.append("dpdk.rss_not_verified")
    if not queue_coverage:
        reasons.append("dpdk.rx_queue_coverage_not_verified")
    if latest_diagnostic is not None:
        diagnostic = _mapping(latest_diagnostic, "latest DPDK diagnostic")
        rx_packets = _sequence(diagnostic.get("rx_queue_packets"), "latest DPDK RX queues")
        if diagnostic.get("diagnostic_passed") is not True:
            reasons.append("dpdk.latest_symmetric_q2_tcp_diagnostic_failed")
        if any(value == 0 for value in rx_packets):
            reasons.append("dpdk.latest_symmetric_q2_tcp_rx_queue_coverage_failed")
    if not zero_errors:
        reasons.append("dpdk.error_counters_nonzero_or_unverified")
    if not restored:
        reasons.append("dpdk.restoration_not_verified")
    if not isolated:
        reasons.append("dpdk.interface_not_management_isolated")
    if not standby:
        reasons.append("dpdk.standby_preflight_not_passed")
    if not SHA256_RE.fullmatch(binary_sha256):
        reasons.append("dpdk.binary_sha256_invalid")
    return {
        "eligible": not reasons,
        "topology": topology,
        "observed_min_rx_mpps": min_rx,
        "reasons": reasons,
    }


def _online_windows(
    windows_value: Any,
    current_backend: str,
    observation_time: datetime,
    requirements: Mapping[str, Any],
    xdp_requirements: Mapping[str, Any],
    dpdk_requirements: Mapping[str, Any],
) -> Dict[str, Any]:
    windows = _sequence(windows_value, "observation.online_windows")
    required_count = _integer(
        requirements["evaluation_windows"],
        "policy.online_gates.evaluation_windows",
        minimum=1,
    )
    if current_backend == NO_BACKEND:
        if windows:
            raise RuntimeDecisionContractError(
                "observation.online_windows must be empty when current_backend is none"
            )
        return {
            "evaluated_windows": 0,
            "capture_gate_qualified": False,
            "key_flow_gate_qualified": False,
            "capture_reasons": ["online.windows_unavailable"],
            "key_flow_reasons": ["online.windows_unavailable"],
            "runtime_safety_gate_qualified": False,
            "runtime_safety_reasons": ["online.windows_unavailable"],
            "windows": [],
        }
    if len(windows) < required_count:
        return {
            "evaluated_windows": len(windows),
            "capture_gate_qualified": False,
            "key_flow_gate_qualified": False,
            "capture_reasons": ["online.windows_insufficient"],
            "key_flow_reasons": ["online.windows_insufficient"],
            "runtime_safety_gate_qualified": False,
            "runtime_safety_reasons": ["online.windows_insufficient"],
            "windows": [],
        }

    selected = windows[-required_count:]
    capture_reasons: List[str] = []
    key_reasons: List[str] = []
    safety_reasons: List[str] = []
    evaluated: List[Dict[str, Any]] = []
    previous_end: Optional[datetime] = None
    for offset, value in enumerate(selected):
        path = f"observation.online_windows[{len(windows) - required_count + offset}]"
        window = _mapping(value, path)
        backend = _string(window.get("capture_backend"), f"{path}.capture_backend")
        if backend != current_backend:
            raise RuntimeDecisionContractError(
                f"{path}.capture_backend must equal observation.current_backend"
            )
        start = _timestamp(window.get("start_utc"), f"{path}.start_utc")
        end = _timestamp(window.get("end_utc"), f"{path}.end_utc")
        if end <= start or end > observation_time:
            raise RuntimeDecisionContractError(f"{path} has an invalid time interval")
        if previous_end is not None and start < previous_end:
            raise RuntimeDecisionContractError("observation.online_windows must not overlap")
        previous_end = end

        received = _integer(window.get("packets_received"), f"{path}.packets_received")
        dropped = _integer(window.get("packets_dropped"), f"{path}.packets_dropped")
        denominator = received + dropped
        measured_drop_rate = 0.0 if denominator == 0 else dropped / denominator
        reported_drop_rate = _number(window.get("capture_drop_rate"), f"{path}.capture_drop_rate", minimum=0)
        if reported_drop_rate > 1 or not math.isclose(
            reported_drop_rate, measured_drop_rate, rel_tol=0.0, abs_tol=1e-12
        ):
            raise RuntimeDecisionContractError(f"{path}.capture_drop_rate does not match counters")
        poll_errors = _integer(window.get("poll_errors"), f"{path}.poll_errors")
        invalid = _integer(window.get("invalid_descriptors"), f"{path}.invalid_descriptors")
        ring_full = _integer(window.get("ring_full"), f"{path}.ring_full")
        fill_empty = _integer(window.get("fill_empty"), f"{path}.fill_empty")
        host_cpu = _number(window.get("host_cpu_fraction"), f"{path}.host_cpu_fraction", minimum=0)
        memory = _number(window.get("memory_fraction"), f"{path}.memory_fraction", minimum=0)
        if host_cpu > 1 or memory > 1:
            raise RuntimeDecisionContractError(f"{path} resource fractions must be <= 1")
        budget_overruns = _integer(
            window.get("budget_overrun_count"), f"{path}.budget_overrun_count"
        )
        fallback_recovery_ms = _number(
            window.get("fallback_recovery_ms"), f"{path}.fallback_recovery_ms", minimum=0
        )
        p99 = _number(
            window.get("kernel_to_feature_p99_us"),
            f"{path}.kernel_to_feature_p99_us",
            minimum=0,
        )
        p999 = _number(
            window.get("kernel_to_feature_p999_us"),
            f"{path}.kernel_to_feature_p999_us",
            minimum=0,
        )
        active_queues = _integer(window.get("active_rx_queues"), f"{path}.active_rx_queues")
        key_total = _integer(window.get("key_flow_total"), f"{path}.key_flow_total")
        key_covered = _integer(window.get("key_flow_covered"), f"{path}.key_flow_covered")
        if key_covered > key_total:
            raise RuntimeDecisionContractError(f"{path}.key_flow_covered exceeds total")
        coverage_value = window.get("key_flow_coverage")
        if key_total == 0:
            if coverage_value is not None:
                raise RuntimeDecisionContractError(
                    f"{path}.key_flow_coverage must be null when key_flow_total is zero"
                )
            coverage: Optional[float] = None
        else:
            coverage = _number(coverage_value, f"{path}.key_flow_coverage", minimum=0)
            expected = key_covered / key_total
            if coverage > 1 or not math.isclose(coverage, expected, rel_tol=0.0, abs_tol=1e-12):
                raise RuntimeDecisionContractError(
                    f"{path}.key_flow_coverage does not match counters"
                )
        basis = _string(window.get("key_flow_coverage_basis"), f"{path}.key_flow_coverage_basis")

        window_capture_reasons: List[str] = []
        window_key_reasons: List[str] = []
        window_safety_reasons: List[str] = []
        if received == 0:
            window_capture_reasons.append("packets_received_zero")
        if measured_drop_rate > _number(
            requirements["max_capture_drop_rate"],
            "policy.online_gates.max_capture_drop_rate",
            minimum=0,
        ):
            window_capture_reasons.append("capture_drop_rate")
        if poll_errors > _integer(requirements["max_poll_errors"], "policy.online_gates.max_poll_errors"):
            window_capture_reasons.append("poll_errors")
        if invalid > _integer(
            requirements["max_invalid_descriptors"],
            "policy.online_gates.max_invalid_descriptors",
        ):
            window_capture_reasons.append("invalid_descriptors")
        if ring_full > _integer(requirements["max_ring_full"], "policy.online_gates.max_ring_full"):
            window_capture_reasons.append("ring_full")
        if fill_empty > _integer(requirements["max_fill_empty"], "policy.online_gates.max_fill_empty"):
            window_capture_reasons.append("fill_empty")
        if p99 > _number(
            requirements["kernel_to_feature_p99_us_max"],
            "policy.online_gates.kernel_to_feature_p99_us_max",
            minimum=0,
        ):
            window_capture_reasons.append("kernel_to_feature_p99_us")
        if p999 > _number(
            requirements["kernel_to_feature_p999_us_max"],
            "policy.online_gates.kernel_to_feature_p999_us_max",
            minimum=0,
        ):
            window_capture_reasons.append("kernel_to_feature_p999_us")
        if host_cpu > _number(
            requirements["max_host_cpu_fraction"],
            "policy.online_gates.max_host_cpu_fraction",
            minimum=0,
        ):
            window_safety_reasons.append("host_cpu_fraction")
        if memory > _number(
            requirements["max_memory_fraction"],
            "policy.online_gates.max_memory_fraction",
            minimum=0,
        ):
            window_safety_reasons.append("memory_fraction")
        if budget_overruns > _integer(
            requirements["max_budget_overrun_count"],
            "policy.online_gates.max_budget_overrun_count",
        ):
            window_safety_reasons.append("budget_overrun_count")
        if fallback_recovery_ms > _number(
            requirements["max_fallback_recovery_ms"],
            "policy.online_gates.max_fallback_recovery_ms",
            minimum=0,
        ):
            window_safety_reasons.append("fallback_recovery_ms")

        if current_backend == NATIVE_XDP_BACKEND:
            attach_mode = _string(window.get("xdp_attach_mode"), f"{path}.xdp_attach_mode")
            bind_mode = _string(window.get("af_xdp_bind_mode"), f"{path}.af_xdp_bind_mode")
            if attach_mode != "native":
                window_capture_reasons.append("runtime_xdp_not_native")
            if bind_mode != "zerocopy":
                window_capture_reasons.append("runtime_af_xdp_not_zerocopy")
            minimum_queues = _integer(
                xdp_requirements["min_rx_queues"],
                "policy.xdp_requirements.min_rx_queues",
                minimum=1,
            )
        elif current_backend == GENERIC_XDP_BACKEND:
            attach_mode = _string(window.get("xdp_attach_mode"), f"{path}.xdp_attach_mode")
            bind_mode = _string(window.get("af_xdp_bind_mode"), f"{path}.af_xdp_bind_mode")
            if attach_mode != "generic" or bind_mode != "copy":
                raise RuntimeDecisionContractError(
                    f"{path} generic XDP identity must be generic/copy"
                )
            minimum_queues = _integer(
                xdp_requirements["min_rx_queues"],
                "policy.xdp_requirements.min_rx_queues",
                minimum=1,
            )
        else:
            if current_backend != DPDK_BACKEND:
                raise RuntimeDecisionContractError("unsupported current backend")
            if not _boolean(window.get("dpdk_pmd_active"), f"{path}.dpdk_pmd_active"):
                window_capture_reasons.append("runtime_dpdk_pmd_inactive")
            minimum_queues = _integer(
                dpdk_requirements["min_rx_queues"],
                "policy.dpdk_requirements.min_rx_queues",
                minimum=1,
            )
        if active_queues < minimum_queues:
            window_capture_reasons.append("active_rx_queues")

        required_basis = _string(
            requirements["key_flow_coverage_basis"],
            "policy.online_gates.key_flow_coverage_basis",
        )
        if basis != required_basis:
            window_key_reasons.append("coverage_basis")
        if key_total == 0:
            window_key_reasons.append("empty_denominator")
        elif coverage is None or coverage < _number(
            requirements["min_key_flow_coverage"],
            "policy.online_gates.min_key_flow_coverage",
            minimum=0,
        ):
            window_key_reasons.append("coverage")

        capture_reasons.extend(
            f"window[{offset}].{reason}" for reason in window_capture_reasons
        )
        key_reasons.extend(f"window[{offset}].{reason}" for reason in window_key_reasons)
        safety_reasons.extend(
            f"window[{offset}].{reason}" for reason in window_safety_reasons
        )
        evaluated.append(
            {
                "capture_qualified": not window_capture_reasons,
                "key_flow_qualified": not window_key_reasons,
                "runtime_safety_qualified": not window_safety_reasons,
                "capture_drop_rate": measured_drop_rate,
                "key_flow_coverage": coverage,
                "capture_reasons": window_capture_reasons,
                "key_flow_reasons": window_key_reasons,
                "runtime_safety_reasons": window_safety_reasons,
            }
        )
    return {
        "evaluated_windows": len(evaluated),
        "capture_gate_qualified": not capture_reasons,
        "key_flow_gate_qualified": not key_reasons,
        "runtime_safety_gate_qualified": not safety_reasons,
        "capture_reasons": capture_reasons,
        "key_flow_reasons": key_reasons,
        "runtime_safety_reasons": safety_reasons,
        "windows": evaluated,
    }


def _fallback_decision(
    dpdk: Mapping[str, Any],
    observation: Mapping[str, Any],
    switch: Mapping[str, Any],
    reasons: List[str],
) -> Tuple[str, Optional[str], bool, List[str]]:
    if not dpdk["eligible"]:
        return "stop_fail_closed", None, False, reasons + list(dpdk["reasons"])
    topology = dpdk["topology"]
    automatic_topologies = set(
        _sequence(switch["automatic_topologies"], "policy.switch_safety.automatic_topologies")
    )
    maintenance_topologies = set(
        _sequence(switch["maintenance_topologies"], "policy.switch_safety.maintenance_topologies")
    )
    if topology in maintenance_topologies:
        return (
            "request_maintenance_dpdk_fallback",
            DPDK_BACKEND,
            False,
            reasons + ["dpdk.topology_requires_maintenance"],
        )
    if topology not in automatic_topologies:
        return (
            "stop_fail_closed",
            None,
            False,
            reasons + ["dpdk.topology_not_allowed"],
        )
    authorized = _boolean(
        observation.get("automatic_switch_authorized"),
        "observation.automatic_switch_authorized",
    )
    handoff = _mapping(observation.get("handoff"), "observation.handoff")
    missing = [
        name
        for name in _sequence(
            switch["required_handoff_flags"],
            "policy.switch_safety.required_handoff_flags",
        )
        if not _boolean(handoff.get(name), f"observation.handoff.{name}")
    ]
    if not authorized or missing:
        blockers = []
        if not authorized:
            blockers.append("dpdk.automatic_switch_not_authorized")
        blockers.extend(f"handoff.{name}" for name in missing)
        return "prepare_dpdk_fallback", DPDK_BACKEND, False, reasons + blockers
    return "switch_to_dpdk", DPDK_BACKEND, True, reasons


def evaluate_runtime_decision(
    policy_value: Mapping[str, Any],
    observation_value: Mapping[str, Any],
    *,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Evaluate one immutable observation and return a non-mutating decision."""

    policy = _mapping(policy_value, "policy")
    observation = _mapping(observation_value, "observation")
    freshness, xdp_requirements, dpdk_requirements, online_requirements, switch = (
        _requirements(policy)
    )
    if _integer(observation.get("schema_version"), "observation.schema_version", minimum=1) != 1:
        raise RuntimeDecisionContractError("observation.schema_version must equal 1")
    observation_time = _timestamp(
        observation.get("observed_at_utc"), "observation.observed_at_utc"
    )
    decision_time = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    current_is_fresh, observation_freshness_reason = _fresh(
        observation.get("observed_at_utc"),
        "observation.observed_at_utc",
        decision_time,
        _number(freshness["observation_max_age_s"], "policy.freshness.observation_max_age_s"),
        _number(freshness["max_future_clock_skew_s"], "policy.freshness.max_future_clock_skew_s"),
    )
    current_backend = _string(observation.get("current_backend"), "observation.current_backend")
    if current_backend not in KNOWN_BACKENDS:
        raise RuntimeDecisionContractError("observation.current_backend is unsupported")
    capabilities = _mapping(observation.get("capabilities"), "observation.capabilities")
    xdp = _xdp_capability(
        _mapping(capabilities.get("xdp"), "observation.capabilities.xdp"),
        xdp_requirements,
        observation_time,
        freshness,
    )
    dpdk = _dpdk_capability(
        _mapping(capabilities.get("dpdk"), "observation.capabilities.dpdk"),
        dpdk_requirements,
        observation_time,
        freshness,
    )
    online = _online_windows(
        observation.get("online_windows"),
        current_backend,
        observation_time,
        online_requirements,
        xdp_requirements,
        dpdk_requirements,
    )

    reasons: List[str] = []
    if not current_is_fresh:
        reasons.append(observation_freshness_reason)
        if not xdp["eligible"]:
            reasons.extend(xdp["reasons"])
        if not dpdk["eligible"]:
            reasons.extend(dpdk["reasons"])
        action, selected, permitted = "stop_fail_closed", None, False
    elif not online["runtime_safety_gate_qualified"] and current_backend != NO_BACKEND:
        reasons.extend(online["runtime_safety_reasons"])
        reasons.append("runtime_safety_failure_is_not_a_capture_backend_fallback_signal")
        action, selected, permitted = "stop_fail_closed", None, False
    elif current_backend == NATIVE_XDP_BACKEND:
        if xdp["eligible"] and online["capture_gate_qualified"] and online["key_flow_gate_qualified"]:
            action, selected, permitted = "keep_xdp", NATIVE_XDP_BACKEND, False
        elif online["capture_gate_qualified"] and not online["key_flow_gate_qualified"]:
            action, selected, permitted = "stop_fail_closed", None, False
            reasons.extend(online["key_flow_reasons"])
            reasons.append("key_flow_failure_is_not_a_capture_backend_fallback_signal")
        else:
            reasons.extend(xdp["reasons"])
            reasons.extend(online["capture_reasons"])
            if not online["key_flow_gate_qualified"]:
                reasons.extend(online["key_flow_reasons"])
            action, selected, permitted, reasons = _fallback_decision(
                dpdk, observation, switch, reasons
            )
    elif current_backend == GENERIC_XDP_BACKEND:
        reasons.extend(
            [
                "generic_xdp_skb_is_diagnostic_copy_mode",
                "generic_xdp_skb_is_not_native_or_zerocopy",
            ]
        )
        reasons.extend(xdp["reasons"])
        if not online["key_flow_gate_qualified"]:
            reasons.extend(online["key_flow_reasons"])
        action, selected, permitted, reasons = _fallback_decision(
            dpdk, observation, switch, reasons
        )
    elif current_backend == DPDK_BACKEND:
        if dpdk["eligible"] and online["capture_gate_qualified"] and online["key_flow_gate_qualified"]:
            action, selected, permitted = "keep_dpdk", DPDK_BACKEND, False
        else:
            action, selected, permitted = "stop_fail_closed", None, False
            reasons.extend(dpdk["reasons"])
            reasons.extend(online["capture_reasons"])
            reasons.extend(online["key_flow_reasons"])
    else:
        if xdp["eligible"]:
            action, selected, permitted = "prepare_xdp_primary", NATIVE_XDP_BACKEND, False
            reasons.append("xdp.start_requires_external_state_snapshot_executor")
        else:
            reasons.extend(xdp["reasons"])
            action, selected, permitted, reasons = _fallback_decision(
                dpdk, observation, switch, reasons
            )

    return {
        "schema_version": 1,
        "policy_id": policy["policy_id"],
        "observed_at_utc": observation["observed_at_utc"],
        "decision_is_non_mutating": True,
        "action": action,
        "current_backend": current_backend,
        "selected_backend": selected,
        "transition_permitted": permitted,
        "production_backend_available": bool(xdp["eligible"] or dpdk["eligible"]),
        "diagnostic_only_backends": [
            backend
            for backend, eligible in (
                (GENERIC_XDP_BACKEND, False),
                (DPDK_BACKEND, dpdk["eligible"]),
            )
            if not eligible
        ],
        "xdp_capability": xdp,
        "dpdk_capability": dpdk,
        "online_gates": online,
        "generic_xdp_production_eligible": False,
        "empty_key_flow_denominator_qualified": False,
        "reasons": list(dict.fromkeys(reasons)),
    }


def build_runtime_decision_receipt(
    policy_value: Mapping[str, Any],
    observation_value: Mapping[str, Any],
    *,
    policy_sha256: str,
    observation_sha256: str,
    raw_runtime_evidence_sha256: str,
    observation_artifact: Mapping[str, Any],
    raw_runtime_evidence: Mapping[str, Any],
    decision_at_utc: str,
) -> Dict[str, Any]:
    """Build a sealed decision receipt without treating it as release evidence.

    The caller supplies file identities; the production selector independently
    re-reads and re-hashes every referenced file and replays this decision.
    """

    for name, value in (
        ("policy_sha256", policy_sha256),
        ("observation_sha256", observation_sha256),
        ("raw_runtime_evidence_sha256", raw_runtime_evidence_sha256),
    ):
        if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
            raise RuntimeDecisionContractError(f"{name} must be a lowercase SHA-256")
    policy_bytes = json.dumps(
        policy_value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    observation_bytes = json.dumps(
        observation_value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    # These canonical hashes are informational tamper detectors in addition to
    # the exact raw-file hashes supplied by the CLI.
    canonical_policy_sha256 = hashlib.sha256(policy_bytes).hexdigest()
    canonical_observation_sha256 = hashlib.sha256(observation_bytes).hexdigest()
    decision_time = _timestamp(decision_at_utc, "decision_at_utc")
    decision = evaluate_runtime_decision(
        policy_value, observation_value, now=decision_time
    )
    return {
        "receipt_scope": "hft_mgbs_capture_runtime_decision_receipt_v1",
        **decision,
        "decision_at_utc": decision_at_utc,
        "runtime_policy_sha256": policy_sha256,
        "runtime_policy_canonical_sha256": canonical_policy_sha256,
        "observation_sha256": observation_sha256,
        "observation_canonical_sha256": canonical_observation_sha256,
        "raw_runtime_evidence_sha256": raw_runtime_evidence_sha256,
        "observation_artifact": dict(observation_artifact),
        "raw_runtime_evidence": dict(raw_runtime_evidence),
        "release_qualification": False,
        "pareto_metrics_must_be_recomputed_from_raw": True,
    }
