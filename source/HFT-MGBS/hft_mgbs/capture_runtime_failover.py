"""Three-tier capture runtime failover decision contract.

The production order is native AF_XDP zero-copy, DPDK, then the existing
BCM57810 TPACKET_V3 pipeline.  The final backend is explicitly a degraded
service-continuity fallback and can never satisfy the production SLA merely by
being selected.  This module is non-mutating; the separately hash-bound
executor performs an approved state transition.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple


NATIVE_XDP_BACKEND = "native_af_xdp_zerocopy"
DPDK_BACKEND = "dpdk"
CURRENT_HARDWARE_BACKEND = "current_tpacket_v3_bcm57810"
NO_BACKEND = "none"
BACKENDS = (NATIVE_XDP_BACKEND, DPDK_BACKEND, CURRENT_HARDWARE_BACKEND)
KNOWN_BACKENDS = frozenset(BACKENDS + (NO_BACKEND,))
POLICY_SCOPE = "hft_mgbs_capture_runtime_failover_policy_v2"
OBSERVATION_SCOPE = "hft_mgbs_capture_runtime_failover_observation_v2"
RECEIPT_SCOPE = "hft_mgbs_capture_runtime_failover_decision_receipt_v2"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class RuntimeFailoverContractError(ValueError):
    """Raised when a policy or observation is not safe to interpret."""


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RuntimeFailoverContractError(path + " must be an object")
    return value


def _sequence(value: Any, path: str) -> Sequence[Any]:
    if not isinstance(value, list):
        raise RuntimeFailoverContractError(path + " must be an array")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise RuntimeFailoverContractError(path + " must be a non-empty string")
    return value


def _boolean(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise RuntimeFailoverContractError(path + " must be a boolean")
    return value


def _integer(value: Any, path: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise RuntimeFailoverContractError(
            "{} must be an integer >= {}".format(path, minimum)
        )
    return value


def _number(value: Any, path: str, minimum: float = 0.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RuntimeFailoverContractError(path + " must be a finite number")
    result = float(value)
    if not math.isfinite(result) or result < minimum:
        raise RuntimeFailoverContractError(
            "{} must be finite and >= {}".format(path, minimum)
        )
    return result


def _timestamp(value: Any, path: str) -> datetime:
    text = _string(value, path)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as error:
        raise RuntimeFailoverContractError(path + " must be ISO-8601") from error
    if parsed.tzinfo is None:
        raise RuntimeFailoverContractError(path + " must include a timezone")
    return parsed.astimezone(timezone.utc)


def _exact(value: Mapping[str, Any], expected: Sequence[str], path: str) -> None:
    if set(value) != set(expected):
        raise RuntimeFailoverContractError(path + " fields are not exact")


def _policy(policy_value: Mapping[str, Any]) -> Tuple[
    Mapping[str, Any], Mapping[str, Any], Mapping[str, Any]
]:
    policy = _mapping(policy_value, "policy")
    _exact(
        policy,
        (
            "schema_version", "scope", "policy_id", "backend_priority",
            "freshness", "backend_requirements", "switching",
            "failure_semantics", "qualification_boundaries",
        ),
        "policy",
    )
    if _integer(policy.get("schema_version"), "policy.schema_version", 1) != 2:
        raise RuntimeFailoverContractError("policy.schema_version must equal 2")
    if _string(policy.get("scope"), "policy.scope") != POLICY_SCOPE:
        raise RuntimeFailoverContractError("policy.scope is invalid")
    _string(policy.get("policy_id"), "policy.policy_id")
    if list(_sequence(policy.get("backend_priority"), "policy.backend_priority")) != list(BACKENDS):
        raise RuntimeFailoverContractError("policy.backend_priority must be XDP, DPDK, BCM57810")

    freshness = _mapping(policy.get("freshness"), "policy.freshness")
    _exact(
        freshness,
        ("observation_max_age_s", "capability_max_age_s", "max_future_clock_skew_s"),
        "policy.freshness",
    )
    for name in freshness:
        _number(freshness[name], "policy.freshness." + name)

    requirements = _mapping(policy.get("backend_requirements"), "policy.backend_requirements")
    if set(requirements) != set(BACKENDS):
        raise RuntimeFailoverContractError("policy.backend_requirements backends are not exact")
    fields = (
        "role", "production_eligible", "service_continuity_eligible",
        "min_sustainable_mpps", "min_active_rx_queues", "allowed_topologies",
        "require_zero_drop", "require_restoration", "require_management_isolation",
        "require_binary_sha256",
    )
    for backend in BACKENDS:
        item = _mapping(requirements[backend], "policy.backend_requirements." + backend)
        _exact(item, fields, "policy.backend_requirements." + backend)
        role = _string(item.get("role"), "policy.backend_requirements.{}.role".format(backend))
        production = _boolean(item.get("production_eligible"), "backend.production_eligible")
        continuity = _boolean(
            item.get("service_continuity_eligible"), "backend.service_continuity_eligible"
        )
        if backend == CURRENT_HARDWARE_BACKEND:
            if role != "degraded_service_continuity_fallback" or production or not continuity:
                raise RuntimeFailoverContractError("BCM57810 must remain degraded fallback only")
        elif not production or not continuity:
            raise RuntimeFailoverContractError("production backends must be continuity eligible")
        _number(item.get("min_sustainable_mpps"), "backend.min_sustainable_mpps")
        _integer(item.get("min_active_rx_queues"), "backend.min_active_rx_queues", 1)
        topologies = _sequence(item.get("allowed_topologies"), "backend.allowed_topologies")
        if not topologies or any(not isinstance(value, str) or not value for value in topologies):
            raise RuntimeFailoverContractError("backend.allowed_topologies is invalid")
        for flag in (
            "require_zero_drop", "require_restoration", "require_management_isolation",
            "require_binary_sha256",
        ):
            _boolean(item.get(flag), "backend." + flag)

    switching = _mapping(policy.get("switching"), "policy.switching")
    _exact(
        switching,
        (
            "automatic_topologies", "maintenance_topologies", "required_handoff_flags",
            "prefer_higher_priority_recovery", "decision_engine_performs_mutations",
        ),
        "policy.switching",
    )
    automatic = _sequence(switching.get("automatic_topologies"), "policy.switching.automatic_topologies")
    maintenance = _sequence(switching.get("maintenance_topologies"), "policy.switching.maintenance_topologies")
    if not automatic or set(automatic) & set(maintenance):
        raise RuntimeFailoverContractError("automatic and maintenance topologies are invalid")
    handoff = _sequence(switching.get("required_handoff_flags"), "policy.switching.required_handoff_flags")
    if not handoff or any(not isinstance(value, str) or not value for value in handoff):
        raise RuntimeFailoverContractError("required handoff flags are invalid")
    _boolean(switching.get("prefer_higher_priority_recovery"), "policy.switching.prefer_higher_priority_recovery")
    if _boolean(switching.get("decision_engine_performs_mutations"), "policy.switching.decision_engine_performs_mutations"):
        raise RuntimeFailoverContractError("the decision engine must remain non-mutating")

    semantics = _mapping(policy.get("failure_semantics"), "policy.failure_semantics")
    expected_semantics = {
        "capture_backend_failure_can_trigger_fallback": True,
        "key_flow_failure_can_trigger_backend_fallback": False,
        "runtime_safety_failure_can_trigger_backend_fallback": False,
    }
    if dict(semantics) != expected_semantics:
        raise RuntimeFailoverContractError("policy.failure_semantics must remain fail-closed")
    boundaries = _mapping(policy.get("qualification_boundaries"), "policy.qualification_boundaries")
    expected_boundaries = {
        "decision_is_release_qualification": False,
        "decision_is_pareto_evidence": False,
        "current_hardware_is_production_sla_eligible": False,
        "current_hardware_role": "degraded_service_continuity_fallback_only",
    }
    if dict(boundaries) != expected_boundaries:
        raise RuntimeFailoverContractError("policy.qualification_boundaries drifted")
    return freshness, requirements, switching


def _fresh(
    value: Any, path: str, now: datetime, maximum_age_s: float, future_skew_s: float
) -> Tuple[bool, str]:
    observed = _timestamp(value, path)
    age = (now - observed).total_seconds()
    if age < -future_skew_s:
        return False, path + ".future"
    if age > maximum_age_s:
        return False, path + ".stale"
    return True, ""


def _capability(
    backend: str,
    raw: Any,
    requirement: Mapping[str, Any],
    observation_time: datetime,
    freshness: Mapping[str, Any],
) -> Dict[str, Any]:
    path = "observation.capabilities." + backend
    value = _mapping(raw, path)
    _exact(
        value,
        (
            "backend", "observed_at_utc", "ready", "health_verified", "topology",
            "observed_min_mpps", "active_rx_queues", "zero_drop_qualified",
            "restoration_verified", "management_isolated", "binary_sha256",
            "service_continuity_qualified", "production_sla_qualified",
        ),
        path,
    )
    if _string(value.get("backend"), path + ".backend") != backend:
        raise RuntimeFailoverContractError(path + ".backend identity drifted")
    reasons: List[str] = []
    fresh, reason = _fresh(
        value.get("observed_at_utc"), path + ".observed_at_utc", observation_time,
        _number(freshness["capability_max_age_s"], "freshness.capability_max_age_s"),
        _number(freshness["max_future_clock_skew_s"], "freshness.max_future_clock_skew_s"),
    )
    if not fresh:
        reasons.append(reason)
    ready = _boolean(value.get("ready"), path + ".ready")
    health = _boolean(value.get("health_verified"), path + ".health_verified")
    topology = _string(value.get("topology"), path + ".topology")
    observed_mpps = _number(value.get("observed_min_mpps"), path + ".observed_min_mpps")
    queues = _integer(value.get("active_rx_queues"), path + ".active_rx_queues")
    zero_drop = _boolean(value.get("zero_drop_qualified"), path + ".zero_drop_qualified")
    restored = _boolean(value.get("restoration_verified"), path + ".restoration_verified")
    isolated = _boolean(value.get("management_isolated"), path + ".management_isolated")
    binary_sha = _string(value.get("binary_sha256"), path + ".binary_sha256")
    continuity = _boolean(
        value.get("service_continuity_qualified"), path + ".service_continuity_qualified"
    )
    production = _boolean(value.get("production_sla_qualified"), path + ".production_sla_qualified")
    if not ready:
        reasons.append(backend + ".not_ready")
    if not health:
        reasons.append(backend + ".health_not_verified")
    if topology not in requirement["allowed_topologies"]:
        reasons.append(backend + ".topology_not_allowed")
    if observed_mpps < _number(requirement["min_sustainable_mpps"], "backend.min_sustainable_mpps"):
        reasons.append(backend + ".capacity_insufficient")
    if queues < _integer(requirement["min_active_rx_queues"], "backend.min_active_rx_queues", 1):
        reasons.append(backend + ".active_rx_queues_insufficient")
    if requirement["require_zero_drop"] and not zero_drop:
        reasons.append(backend + ".zero_drop_not_qualified")
    if requirement["require_restoration"] and not restored:
        reasons.append(backend + ".restoration_not_verified")
    if requirement["require_management_isolation"] and not isolated:
        reasons.append(backend + ".management_not_isolated")
    if requirement["require_binary_sha256"] and SHA256_RE.fullmatch(binary_sha) is None:
        reasons.append(backend + ".binary_sha256_invalid")
    if not continuity:
        reasons.append(backend + ".service_continuity_not_qualified")
    if production and not requirement["production_eligible"]:
        raise RuntimeFailoverContractError(backend + " cannot claim production SLA qualification")
    if requirement["production_eligible"] and not production:
        reasons.append(backend + ".production_sla_not_qualified")
    return {
        "backend": backend,
        "eligible": not reasons,
        "topology": topology,
        "production_eligible": bool(requirement["production_eligible"]),
        "service_continuity_eligible": bool(requirement["service_continuity_eligible"]),
        "observed_min_mpps": observed_mpps,
        "active_rx_queues": queues,
        "reasons": reasons,
    }


def _transition(
    target: str,
    observation: Mapping[str, Any],
    switching: Mapping[str, Any],
    capabilities: Mapping[str, Mapping[str, Any]],
    reasons: List[str],
) -> Tuple[str, str, bool, List[str]]:
    topology = capabilities[target]["topology"]
    if topology in switching["maintenance_topologies"]:
        return "request_maintenance_" + target, target, False, reasons + [
            target + ".topology_requires_maintenance"
        ]
    if topology not in switching["automatic_topologies"]:
        return "stop_fail_closed", target, False, reasons + [
            target + ".topology_not_automatic"
        ]
    authorized = _boolean(
        observation.get("automatic_switch_authorized"),
        "observation.automatic_switch_authorized",
    )
    handoff = _mapping(observation.get("handoff"), "observation.handoff")
    missing = [
        name for name in switching["required_handoff_flags"]
        if not _boolean(handoff.get(name), "observation.handoff." + name)
    ]
    if not authorized or missing:
        blockers = ([] if authorized else ["automatic_switch_not_authorized"])
        blockers.extend("handoff." + name for name in missing)
        return "prepare_" + target, target, False, reasons + blockers
    return "switch_to_" + target, target, True, reasons


def evaluate_failover_decision(
    policy_value: Mapping[str, Any],
    observation_value: Mapping[str, Any],
    *,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Return a non-mutating, fail-closed three-tier capture decision."""

    freshness, requirements, switching = _policy(policy_value)
    observation = _mapping(observation_value, "observation")
    _exact(
        observation,
        (
            "schema_version", "scope", "observed_at_utc", "current_backend",
            "capabilities", "current_status", "automatic_switch_authorized", "handoff",
        ),
        "observation",
    )
    if _integer(observation.get("schema_version"), "observation.schema_version", 1) != 2:
        raise RuntimeFailoverContractError("observation.schema_version must equal 2")
    if _string(observation.get("scope"), "observation.scope") != OBSERVATION_SCOPE:
        raise RuntimeFailoverContractError("observation.scope is invalid")
    observation_time = _timestamp(observation.get("observed_at_utc"), "observation.observed_at_utc")
    decision_time = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    observation_fresh, observation_reason = _fresh(
        observation.get("observed_at_utc"), "observation.observed_at_utc", decision_time,
        _number(freshness["observation_max_age_s"], "freshness.observation_max_age_s"),
        _number(freshness["max_future_clock_skew_s"], "freshness.max_future_clock_skew_s"),
    )
    current = _string(observation.get("current_backend"), "observation.current_backend")
    if current not in KNOWN_BACKENDS:
        raise RuntimeFailoverContractError("observation.current_backend is unsupported")
    raw_capabilities = _mapping(observation.get("capabilities"), "observation.capabilities")
    if set(raw_capabilities) != set(BACKENDS):
        raise RuntimeFailoverContractError("observation.capabilities backends are not exact")
    capabilities = {
        backend: _capability(
            backend, raw_capabilities[backend], requirements[backend], observation_time, freshness
        )
        for backend in BACKENDS
    }
    status = _mapping(observation.get("current_status"), "observation.current_status")
    _exact(
        status,
        (
            "consecutive_healthy_windows", "consecutive_failed_windows",
            "capture_gate_qualified", "key_flow_gate_qualified",
            "runtime_safety_gate_qualified",
        ),
        "observation.current_status",
    )
    healthy_windows = _integer(status.get("consecutive_healthy_windows"), "current_status.consecutive_healthy_windows")
    failed_windows = _integer(status.get("consecutive_failed_windows"), "current_status.consecutive_failed_windows")
    capture_ok = _boolean(status.get("capture_gate_qualified"), "current_status.capture_gate_qualified")
    key_ok = _boolean(status.get("key_flow_gate_qualified"), "current_status.key_flow_gate_qualified")
    safety_ok = _boolean(status.get("runtime_safety_gate_qualified"), "current_status.runtime_safety_gate_qualified")
    if current == NO_BACKEND and (healthy_windows or failed_windows or capture_ok or key_ok or safety_ok):
        raise RuntimeFailoverContractError("none backend cannot report online qualification")

    reasons: List[str] = []
    eligible = [backend for backend in BACKENDS if capabilities[backend]["eligible"]]
    action, selected, permitted = "stop_fail_closed", None, False
    if not observation_fresh:
        reasons.append(observation_reason)
    elif current != NO_BACKEND and not safety_ok:
        reasons.extend(["runtime_safety_gate_failed", "runtime_safety_failure_is_not_a_backend_fallback_signal"])
    elif current != NO_BACKEND and not key_ok:
        reasons.extend(["key_flow_gate_failed", "key_flow_failure_is_not_a_backend_fallback_signal"])
    else:
        current_healthy = (
            current != NO_BACKEND and capture_ok and healthy_windows > 0
            and current in capabilities and capabilities[current]["eligible"]
        )
        candidates = [backend for backend in eligible if backend != current]
        if current_healthy:
            current_rank = BACKENDS.index(current)
            higher = [backend for backend in candidates if BACKENDS.index(backend) < current_rank]
            if higher and switching["prefer_higher_priority_recovery"]:
                reasons.append("higher_priority_backend_recovered")
                action, selected, permitted, reasons = _transition(
                    higher[0], observation, switching, capabilities, reasons
                )
            else:
                action = "keep_" + current
                selected = current
        else:
            if current != NO_BACKEND:
                reasons.append("current_capture_backend_unhealthy")
                reasons.extend(capabilities[current]["reasons"])
                if not capture_ok:
                    reasons.append("capture_gate_failed")
                if failed_windows == 0:
                    reasons.append("failed_window_not_observed")
            if not candidates and current == NO_BACKEND:
                candidates = list(eligible)
            if candidates:
                action, selected, permitted, reasons = _transition(
                    candidates[0], observation, switching, capabilities, reasons
                )
            else:
                for backend in BACKENDS:
                    reasons.extend(capabilities[backend]["reasons"])
                reasons.append("no_service_continuity_backend_available")

    selected_requirement = requirements.get(selected) if selected is not None else None
    degraded = selected == CURRENT_HARDWARE_BACKEND
    production_sla = bool(
        selected == current
        and selected_requirement is not None
        and selected_requirement["production_eligible"]
        and capture_ok and key_ok and safety_ok and healthy_windows > 0
    )
    return {
        "schema_version": 2,
        "scope": "hft_mgbs_capture_runtime_failover_decision_v2",
        "policy_id": policy_value["policy_id"],
        "observed_at_utc": observation["observed_at_utc"],
        "decision_is_non_mutating": True,
        "action": action,
        "current_backend": current,
        "selected_backend": selected,
        "transition_permitted": permitted,
        "degraded_mode": degraded,
        "production_sla_qualified": production_sla,
        "production_backend_available": any(
            capabilities[backend]["eligible"] and requirements[backend]["production_eligible"]
            for backend in BACKENDS
        ),
        "service_continuity_backend_available": any(
            capabilities[backend]["eligible"] and requirements[backend]["service_continuity_eligible"]
            for backend in BACKENDS
        ),
        "current_hardware_fallback_eligible": capabilities[CURRENT_HARDWARE_BACKEND]["eligible"],
        "capabilities": capabilities,
        "reasons": list(dict.fromkeys(reasons)),
        "release_qualification": False,
        "final_pareto_ingestion_allowed": False,
    }


def build_failover_decision_receipt(
    policy_value: Mapping[str, Any],
    observation_value: Mapping[str, Any],
    *,
    policy_sha256: str,
    observation_sha256: str,
    decision_at_utc: str,
) -> Dict[str, Any]:
    for name, value in (
        ("policy_sha256", policy_sha256),
        ("observation_sha256", observation_sha256),
    ):
        if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
            raise RuntimeFailoverContractError(name + " must be a lowercase SHA-256")
    decision_time = _timestamp(decision_at_utc, "decision_at_utc")
    decision = evaluate_failover_decision(policy_value, observation_value, now=decision_time)
    canonical = lambda item: hashlib.sha256(
        json.dumps(item, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()
    return {
        "receipt_scope": RECEIPT_SCOPE,
        **decision,
        "decision_at_utc": decision_at_utc,
        "runtime_policy_sha256": policy_sha256,
        "runtime_policy_canonical_sha256": canonical(policy_value),
        "observation_sha256": observation_sha256,
        "observation_canonical_sha256": canonical(observation_value),
        "release_qualification": False,
        "pareto_metrics_must_be_recomputed_from_raw": True,
    }
