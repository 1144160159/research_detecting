"""Fail-closed v3 evidence contract for the current-hardware transport recovery.

This contract proves only bounded buffering/circuit/reverse-TCP reconnection to
the *same* frozen remote A09 service.  It deliberately cannot certify local
fallback or production high availability, and is independent of v1/v2 release
and Pareto contracts.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping

PROFILE_SCOPE = "current_hardware_2_79_experimental_transport_recovery"
INPUT_SCOPE = "hft_mgbs_current_hardware_2_79_transport_recovery_campaign_input_v3"
RECEIPT_SCOPE = "hft_mgbs_current_hardware_2_79_transport_recovery_receipt_v3"
FAULT_SCOPE = "hft_mgbs_external_transport_fault_injection_receipt_v1"
AUDIT_SCOPE = "hft_mgbs_current_hardware_2_79_transport_recovery_audit_v3"
SHA_FIELDS = ("model", "runtime_manifest", "service_source", "engine_source", "service_launcher")
FORBIDDEN_SELF_REPORT_KEYS = {
    "steps", "required_steps", "self_reported_steps", "fault_injection_observed",
    "local_fallback_activated", "local_quality_qualified",
}


def _load(path: Path) -> tuple[bytes, Mapping[str, Any]]:
    raw = path.read_bytes()
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=_strict_pairs)
    if not isinstance(value, Mapping):
        raise ValueError(f"object required: {path}")
    return raw, value


def _strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _is_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _contains_forbidden(value: Any) -> bool:
    if isinstance(value, Mapping):
        if any(key in FORBIDDEN_SELF_REPORT_KEYS for key in value):
            return True
        return any(_contains_forbidden(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_forbidden(item) for item in value)
    return False


def _resolve(root: Path, ref: Any, error: str, errors: list[str]) -> tuple[bytes | None, Mapping[str, Any] | None]:
    if not isinstance(ref, Mapping) or not _is_sha(ref.get("sha256")) or not isinstance(ref.get("path"), str):
        errors.append(error)
        return None, None
    path = (root / ref["path"]).resolve()
    try:
        path.relative_to(root)
        if path.is_symlink() or not path.is_file():
            raise ValueError("not regular")
        raw, value = _load(path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        errors.append(error)
        return None, None
    if _sha(raw) != ref["sha256"]:
        errors.append(error + ".sha256")
        return raw, None
    return raw, value


def _profile(path: Path) -> tuple[Mapping[str, Any], str]:
    raw, value = _load(path)
    expected_boundary = {
        "local_fallback_completed": 0,
        "local_quality_qualified": False,
        "remote_retry_is_local_fallback": False,
        "production_high_availability_qualified": False,
        "production_pareto_ingestion_allowed": False,
    }
    gate = value.get("transport_recovery", {})
    if (
        value.get("schema_version") != 3
        or value.get("scope") != PROFILE_SCOPE
        or value.get("claim_boundary") != expected_boundary
        or value.get("campaign", {}).get("required_transport_recovery_repeats") != 3
        or gate.get("mechanism") != "bounded_buffer_circuit_reverse_tcp_reconnect_same_frozen_a09"
        or gate.get("recovery_ms_max") != 300.0
        or gate.get("packet_gap_max_per_window") != 0
        or gate.get("capture_drop_max_per_window") != 0
        or not all(gate.get(name) is True for name in (
            "external_fault_receipt_required", "same_a09_identity_required",
            "primary_service_restored_required", "pf_restored_required", "host_restored_required",
        ))
        or any(gate.get(name) != 0 for name in ("pending_max", "unresolved_max", "terminal_failed_max"))
    ):
        raise ValueError("transport-recovery v3 profile drift")
    return value, _sha(raw)


def _audit_receipt(root: Path, ref: Any, profile: Mapping[str, Any], campaign_id: str,
                   candidate_id: str, errors: list[str], index: int) -> dict[str, Any] | None:
    _raw, receipt = _resolve(root, ref, f"receipts.{index}", errors)
    if receipt is None:
        return None
    prefix = f"receipts.{index}"
    if _contains_forbidden(receipt):
        errors.append(prefix + ".self_reported_or_local_fallback_fields")
    if (
        receipt.get("schema_version") != 3 or receipt.get("scope") != RECEIPT_SCOPE
        or receipt.get("campaign_id") != campaign_id or receipt.get("candidate_id") != candidate_id
    ):
        errors.append(prefix + ".identity")
    run_id, trial_id = receipt.get("run_id"), receipt.get("trial_id")
    start, end = receipt.get("start_monotonic_ns"), receipt.get("end_monotonic_ns")
    recovery = receipt.get("recovery_ms")
    if not all(isinstance(v, str) and v for v in (run_id, trial_id)) or not _positive_int(start) or not _positive_int(end) or end <= start:
        errors.append(prefix + ".trial")
    if not isinstance(recovery, (int, float)) or isinstance(recovery, bool) or not math.isfinite(recovery) or recovery < 0 or recovery > profile["transport_recovery"]["recovery_ms_max"]:
        errors.append(prefix + ".recovery_ms")

    _, fault = _resolve(root, receipt.get("external_fault_receipt"), prefix + ".external_fault_receipt", errors)
    if fault is not None and (
        fault.get("schema_version") != 1 or fault.get("scope") != FAULT_SCOPE
        or fault.get("run_id") != run_id or fault.get("trial_id") != trial_id
        or not isinstance(fault.get("controller_id"), str) or not fault.get("controller_id")
        or fault.get("action") != "disconnect_reverse_tcp"
        or not isinstance(fault.get("target_listener"), str) or not fault.get("target_listener")
        or not _positive_int(fault.get("injected_monotonic_ns"))
        or not (start <= fault["injected_monotonic_ns"] <= end)
    ):
        errors.append(prefix + ".external_fault_receipt.identity")
    if receipt.get("fault_detected") is not True:
        errors.append(prefix + ".fault_not_detected")

    counters = receipt.get("counters", {})
    names = ("eligible_key_flows", "cached", "retried", "recovery_remote_scored", "pending", "unresolved", "terminal_failed", "local_fallback_completed")
    if not isinstance(counters, Mapping) or any(not isinstance(counters.get(n), int) or isinstance(counters.get(n), bool) or counters.get(n) < 0 for n in names):
        errors.append(prefix + ".counters")
    else:
        if counters["cached"] <= 0 or counters["retried"] <= 0 or counters["recovery_remote_scored"] <= 0:
            errors.append(prefix + ".no_recovery_work")
        if counters["cached"] > counters["eligible_key_flows"] or counters["retried"] > counters["cached"]:
            errors.append(prefix + ".counter_order")
        if any(counters[n] != 0 for n in ("pending", "unresolved", "terminal_failed", "local_fallback_completed")):
            errors.append(prefix + ".unresolved_or_local_completion")
        if counters["eligible_key_flows"] != counters["recovery_remote_scored"] + counters["pending"] + counters["unresolved"] + counters["terminal_failed"]:
            errors.append(prefix + ".eligible_conservation")

    observations = receipt.get("transport_observations", {})
    if (
        not isinstance(observations, Mapping)
        or not _positive_int(observations.get("bounded_buffer_capacity"))
        or not _positive_int(observations.get("bounded_buffer_high_watermark"))
        or observations.get("bounded_buffer_high_watermark", 0) > observations.get("bounded_buffer_capacity", 0)
        or not _positive_int(observations.get("circuit_open_delta"))
        or not _positive_int(observations.get("reverse_tcp_disconnect_delta"))
        or not _positive_int(observations.get("reverse_tcp_reconnect_success_delta"))
    ):
        errors.append(prefix + ".transport_observations")

    before, after = receipt.get("a09_identity_before"), receipt.get("a09_identity_after")
    if not isinstance(before, Mapping) or not isinstance(after, Mapping) or any(not _is_sha(before.get(n)) for n in SHA_FIELDS) or dict(before) != dict(after):
        errors.append(prefix + ".a09_identity_drift")
    windows = receipt.get("windows")
    if not isinstance(windows, list) or not windows:
        errors.append(prefix + ".windows")
    else:
        seen = set()
        for window in windows:
            if not isinstance(window, Mapping) or not isinstance(window.get("window_index"), int) or window["window_index"] in seen or window.get("packet_gap") != 0 or window.get("capture_drop") != 0:
                errors.append(prefix + ".packet_continuity")
                break
            seen.add(window["window_index"])
    restoration = receipt.get("restoration", {})
    if not isinstance(restoration, Mapping) or not all(restoration.get(n) is True for n in ("primary_service_restored", "pf_restored", "host_restored")):
        errors.append(prefix + ".restoration")
    return {"run_id": run_id, "trial_id": trial_id, "start": start, "end": end, "a09": before}


def compose_transport_recovery_campaign_v3(profile_path: Path, input_path: Path) -> dict[str, Any]:
    """Audit exactly three independent transport-recovery receipts."""
    errors: list[str] = []
    try:
        profile, profile_sha = _profile(profile_path)
        input_raw, request = _load(input_path)
        root = (input_path.parent / request.get("evidence_root", ".")).resolve()
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, TypeError) as exc:
        return _failure(str(exc))
    if request.get("schema_version") != 3 or request.get("scope") != INPUT_SCOPE or request.get("profile_sha256") != profile_sha:
        errors.append("input.schema_scope_or_profile")
    campaign_id, candidate_id = request.get("campaign_id"), request.get("candidate_id")
    if not all(isinstance(v, str) and v for v in (campaign_id, candidate_id)):
        errors.append("input.identity")
    refs = request.get("receipts")
    if not isinstance(refs, list) or len(refs) != 3:
        errors.append("input.receipts_exactly_three")
        refs = refs if isinstance(refs, list) else []
    audited = [_audit_receipt(root, ref, profile, campaign_id, candidate_id, errors, i) for i, ref in enumerate(refs)]
    valid = [item for item in audited if item]
    run_ids = [item["run_id"] for item in valid]
    trial_ids = [item["trial_id"] for item in valid]
    if len(set(run_ids)) != len(valid) or len(set(trial_ids)) != len(valid):
        errors.append("campaign.unique_trials")
    ordered = sorted(valid, key=lambda item: item["start"] if isinstance(item["start"], int) else -1)
    if any(left["end"] >= right["start"] for left, right in zip(ordered, ordered[1:])):
        errors.append("campaign.nonoverlapping_trials")
    identities = [item["a09"] for item in valid]
    if identities and any(identity != identities[0] for identity in identities[1:]):
        errors.append("campaign.a09_identity_drift")
    qualified = not errors and len(valid) == 3
    return {
        "schema_version": 3, "scope": AUDIT_SCOPE, "profile_sha256": profile_sha,
        "input_sha256": _sha(input_raw), "campaign_id": campaign_id, "candidate_id": candidate_id,
        "transport_recovery_qualified": qualified,
        "local_fallback_completed": 0, "local_quality_qualified": False,
        "production_high_availability_qualified": False, "production_pareto_ingestion_allowed": False,
        "errors": errors,
    }


def _failure(error: str) -> dict[str, Any]:
    return {
        "schema_version": 3, "scope": AUDIT_SCOPE, "transport_recovery_qualified": False,
        "local_fallback_completed": 0, "local_quality_qualified": False,
        "production_high_availability_qualified": False, "production_pareto_ingestion_allowed": False,
        "errors": [error],
    }
