#!/usr/bin/env python3
"""Fail-closed attribution of capture-path throughput bottlenecks.

The analyzer deliberately reports observations instead of extrapolating them.
In particular, a loss-free TPACKET run below 12 Mpps can prove that the
generator was the limiting component for that run, but it cannot qualify the
12 Mpps capture target.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence


SHA256_RE = re.compile(r"[0-9a-f]{64}")
REQUIRED_TARGET_MPPS = 12.0
DPDK_RESULT_SCOPE = "r0_dpdk_bnx2x_capture_only"
DPDK_ACCEPTANCE_SCOPE = "dpdk_release_gate_runner_acceptance"
TPACKET_SCOPE = "tpacket_v3_breakthrough_r0_acceptance"


def _append_once(errors: list[str], error: str) -> None:
    if error not in errors:
        errors.append(error)


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def _finite_number(value: Any, *, minimum: Optional[float] = None) -> Optional[float]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    converted = float(value)
    if not math.isfinite(converted):
        return None
    if minimum is not None and converted < minimum:
        return None
    return converted


def _nonnegative_integer(value: Any) -> Optional[int]:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _json_object(raw: bytes) -> dict[str, Any]:
    def reject_constant(value: str) -> None:
        raise ValueError(f"non-finite JSON constant: {value}")

    parsed = json.loads(raw.decode("utf-8"), parse_constant=reject_constant)
    if not isinstance(parsed, dict):
        raise ValueError("top-level JSON value must be an object")
    return parsed


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_artifact(
    path: Path,
    kind: str,
    expected_sha256: Optional[str] = None,
) -> dict[str, Any]:
    """Load one path-bound JSON artifact and compute its content identity."""

    errors: list[str] = []
    resolved = path.resolve()
    payload: Optional[dict[str, Any]] = None
    digest: Optional[str] = None
    if not path.is_file():
        errors.append("path_missing")
    else:
        try:
            raw = path.read_bytes()
            digest = _sha256(raw)
            payload = _json_object(raw)
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
            errors.append("json_invalid")

    normalized_expected: Optional[str] = None
    if expected_sha256 is not None:
        normalized_expected = expected_sha256.lower()
        if not _is_sha256(normalized_expected):
            errors.append("expected_sha256_invalid")
        elif digest != normalized_expected:
            errors.append("sha256_mismatch")

    return {
        "kind": kind,
        "path": str(resolved),
        "sha256": digest,
        "expected_sha256": normalized_expected,
        "binding_qualified": bool(digest and not errors),
        "payload": payload,
        "errors": errors,
    }


def _validate_contract(contract: Any, errors: list[str]) -> dict[str, Any]:
    if not isinstance(contract, dict):
        _append_once(errors, "contract_type")
        return {}
    target = _finite_number(contract.get("target_mpps"), minimum=0.0)
    ratio = _finite_number(contract.get("rate_match_ratio_min"), minimum=0.0)
    binding = contract.get("evidence_binding")
    integrity = contract.get("integrity_gates")
    if (
        contract.get("schema_version") != 1
        or contract.get("scope") != "capture_bottleneck_decision_contract"
        or target != REQUIRED_TARGET_MPPS
        or ratio is None
        or ratio < 0.95
        or ratio > 1.0
        or not isinstance(binding, dict)
        or binding.get("path_required") is not True
        or binding.get("sha256_computed_for_every_input") is not True
        or binding.get("expected_sha256_optional") is not True
        or binding.get("expected_sha256_must_match_when_present") is not True
        or not isinstance(integrity, dict)
        or integrity.get("finite_numbers_required") is not True
        or integrity.get("exact_packet_gap_required") is not True
        or integrity.get("exact_drop_accounting_required") is not True
        or integrity.get("restoration_required") is not True
        or integrity.get("sealed_runner_evidence_required_for_dpdk") is not True
        or contract.get("full_pipeline_qualified") is not False
        or contract.get("final_pareto_ingestion_allowed") is not False
    ):
        _append_once(errors, "contract_schema")
    return contract


def _artifact_identity(artifact: dict[str, Any], errors: list[str]) -> bool:
    artifact_errors = artifact.get("errors")
    valid = (
        isinstance(artifact.get("path"), str)
        and bool(artifact.get("path"))
        and _is_sha256(artifact.get("sha256"))
        and artifact.get("binding_qualified") is True
        and isinstance(artifact_errors, list)
        and not artifact_errors
        and isinstance(artifact.get("payload"), dict)
    )
    if not valid:
        _append_once(errors, "artifact_binding")
    return valid


def _rate_matched(first: float, second: float, ratio_min: float) -> bool:
    high = max(first, second)
    return high > 0.0 and min(first, second) / high >= ratio_min


def _valid_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(
        isinstance(item, str) and item for item in value
    )


def _validate_dpdk_acceptance(
    acceptance: dict[str, Any], errors: list[str]
) -> bool:
    status = acceptance.get("status")
    input_sha256 = acceptance.get("input_sha256")
    receipt_errors = acceptance.get("errors")
    integrity_status_names = (
        "restore_status",
        "evidence_status",
        "base_hash_check_status",
        "complete_hash_check_status",
    )
    status_shape_ok = (
        isinstance(status, dict)
        and all(
            type(status.get(name)) is int
            for name in (
                "original_exit_status",
                "validator_exit_status",
                *integrity_status_names,
            )
        )
        and all(status.get(name) == 0 for name in integrity_status_names)
    )
    if acceptance.get("runner_qualified") is True:
        outcome_status_ok = (
            status_shape_ok
            and status.get("original_exit_status") == 0
            and status.get("validator_exit_status") == 0
            and acceptance.get("data_resource_qualified") is True
            and receipt_errors == []
        )
    else:
        outcome_status_ok = (
            status_shape_ok
            and (
                status.get("original_exit_status") != 0
                or status.get("validator_exit_status") != 0
            )
            and acceptance.get("data_resource_qualified") is False
            and _valid_string_list(receipt_errors)
            and bool(receipt_errors)
        )
    schema_ok = (
        acceptance.get("schema_version") == 1
        and acceptance.get("scope") == DPDK_ACCEPTANCE_SCOPE
        and acceptance.get("receipt_semantics")
        == "derived_from_preacceptance_sealed_evidence_v1"
        and acceptance.get("standalone_receipt_trusted") is False
        and acceptance.get("evidence_seal_excludes")
        == ["acceptance.json", "acceptance.stdout.json"]
        and isinstance(acceptance.get("candidate_id"), str)
        and bool(acceptance.get("candidate_id"))
        and _is_sha256(acceptance.get("frozen_thresholds_sha256"))
        and outcome_status_ok
        and isinstance(acceptance.get("termination_signal"), str)
        and acceptance.get("termination_signal", "").strip().lower()
        in ("", "none")
        and acceptance.get("restoration_verified") is True
        and acceptance.get("evidence_complete_before_hash") is True
        and acceptance.get("hash_checks_verified") is True
        and isinstance(input_sha256, dict)
        and bool(input_sha256)
        and all(_is_sha256(value) for value in input_sha256.values())
        and _valid_string_list(receipt_errors)
        and type(acceptance.get("runner_qualified")) is bool
        and type(acceptance.get("r0_capture_only_qualified")) is bool
        and acceptance.get("runner_qualified")
        is acceptance.get("r0_capture_only_qualified")
        and acceptance.get("full_pipeline_qualified") is False
        and acceptance.get("final_pareto_ingestion_allowed") is False
    )
    if not schema_ok:
        _append_once(errors, "dpdk_acceptance_integrity")
    return schema_ok


def _analyze_dpdk(
    result_artifact: dict[str, Any],
    acceptance_artifact: dict[str, Any],
    target: float,
    ratio_min: float,
) -> dict[str, Any]:
    errors: list[str] = []
    result_bound = _artifact_identity(result_artifact, errors)
    acceptance_bound = _artifact_identity(acceptance_artifact, errors)
    result = result_artifact.get("payload")
    acceptance = acceptance_artifact.get("payload")
    if not isinstance(result, dict):
        result = {}
    if not isinstance(acceptance, dict):
        acceptance = {}

    if (
        result.get("schema_version") != 5
        or result.get("scope") != DPDK_RESULT_SCOPE
        or not isinstance(result.get("candidate_id"), str)
        or not result.get("candidate_id")
        or not _is_sha256(result.get("frozen_thresholds_sha256"))
        or result.get("full_pipeline_qualified") is not False
        or result.get("final_pareto_ingestion_allowed") is not False
        or result.get("r0_capture_only_qualified") is not False
        or result.get("resource_gate_evaluated") is not False
        or not _valid_string_list(result.get("hard_gate_errors"))
        or type(result.get("data_plane_qualified")) is not bool
    ):
        _append_once(errors, "dpdk_result_schema")

    acceptance_ok = _validate_dpdk_acceptance(acceptance, errors)
    if (
        result.get("candidate_id") != acceptance.get("candidate_id")
        or result.get("frozen_thresholds_sha256")
        != acceptance.get("frozen_thresholds_sha256")
    ):
        _append_once(errors, "dpdk_pair_identity")

    requested = _finite_number(result.get("target_mpps"), minimum=0.0)
    tx = _finite_number(result.get("observed_tx_mpps_min_1s"), minimum=0.0)
    rx = _finite_number(result.get("observed_rx_mpps_min_1s"), minimum=0.0)
    queue_count = _nonnegative_integer(result.get("queue_count"))
    offered = _nonnegative_integer(result.get("offered_packets"))
    received = _nonnegative_integer(result.get("received_packets"))
    gap = _nonnegative_integer(result.get("offered_received_gap"))
    capture_stats = result.get("capture_stats_delta")
    replay_stats = result.get("replay_stats_delta")
    latency = result.get("end_to_end_latency_us")
    if not isinstance(capture_stats, dict):
        capture_stats = {}
    if not isinstance(replay_stats, dict):
        replay_stats = {}
    if not isinstance(latency, dict):
        latency = {}
    drops = [
        _nonnegative_integer(capture_stats.get(name))
        for name in ("imissed", "ierrors", "rx_nombuf")
    ]
    replay_errors = _nonnegative_integer(replay_stats.get("oerrors"))
    p99 = _finite_number(latency.get("p99"), minimum=0.0)
    p999 = _finite_number(latency.get("p999"), minimum=0.0)
    samples = _nonnegative_integer(latency.get("samples"))
    if (
        requested is None
        or tx is None
        or rx is None
        or queue_count is None
        or queue_count == 0
        or offered is None
        or offered == 0
        or received is None
        or gap is None
        or any(value is None for value in drops)
        or replay_errors is None
        or p99 is None
        or p999 is None
        or samples is None
        or samples == 0
    ):
        _append_once(errors, "dpdk_nonfinite_or_missing_metrics")

    drop_total = sum(value for value in drops if value is not None)
    if (
        offered is None
        or received is None
        or gap is None
        or gap != offered - received
        or gap != drop_total
    ):
        _append_once(errors, "dpdk_loss_accounting")

    eligible = result_bound and acceptance_bound and acceptance_ok and not errors
    zero_loss = bool(
        eligible
        and gap == 0
        and drop_total == 0
        and replay_errors == 0
        and offered == received
    )
    rate_matched = bool(
        eligible and tx is not None and rx is not None and _rate_matched(tx, rx, ratio_min)
    )
    target_requested = bool(eligible and requested is not None and requested >= target)
    offered_target = bool(eligible and tx is not None and tx >= target)
    capture_target = bool(eligible and rx is not None and rx >= target)
    single_queue = bool(
        eligible
        and (
            queue_count == 1
            or "single_queue" in str(result.get("backend", ""))
        )
    )
    capture_limited = bool(
        eligible
        and (
            (gap is not None and gap > 0)
            or (drop_total > 0)
            or (offered_target and not capture_target)
        )
    )
    single_queue_limited = bool(
        eligible
        and target_requested
        and single_queue
        and not offered_target
        and zero_loss
        and rate_matched
    )
    generator_limited = bool(
        eligible
        and target_requested
        and not single_queue
        and not offered_target
        and zero_loss
        and rate_matched
    )
    target_qualified = bool(
        eligible
        and acceptance.get("runner_qualified") is True
        and target_requested
        and offered_target
        and capture_target
        and zero_loss
    )
    return {
        "source_kind": "dpdk_result_acceptance_pair",
        "candidate_id": result.get("candidate_id"),
        "eligible": eligible,
        "restoration_verified": acceptance.get("restoration_verified") is True,
        "data_integrity_qualified": eligible,
        "metrics": {
            "requested_mpps": requested,
            "offered_tx_min_mpps": tx,
            "capture_rx_min_mpps": rx,
            "queue_count": queue_count,
            "offered_packets": offered,
            "received_packets": received,
            "packet_gap": gap,
            "capture_drop_total": drop_total if all(value is not None for value in drops) else None,
            "p99_us": p99,
            "p999_us": p999,
        },
        "findings": {
            "generator_limited": generator_limited,
            "capture_limited": capture_limited,
            "single_queue_path_limited": single_queue_limited,
        },
        "target_qualified": target_qualified,
        "errors": errors,
        "artifacts": [
            {
                key: result_artifact.get(key)
                for key in ("kind", "path", "sha256", "expected_sha256", "binding_qualified")
            },
            {
                key: acceptance_artifact.get(key)
                for key in ("kind", "path", "sha256", "expected_sha256", "binding_qualified")
            },
        ],
    }


def _analyze_tpacket(
    artifact: dict[str, Any], target: float, ratio_min: float
) -> dict[str, Any]:
    errors: list[str] = []
    bound = _artifact_identity(artifact, errors)
    receipt = artifact.get("payload")
    if not isinstance(receipt, dict):
        receipt = {}
    if (
        receipt.get("schema_version") != 1
        or receipt.get("scope") != TPACKET_SCOPE
        or not isinstance(receipt.get("candidate_id"), str)
        or not receipt.get("candidate_id")
        or receipt.get("full_pipeline_qualified") is not False
        or receipt.get("final_pareto_ingestion_allowed") is not False
        or type(receipt.get("r0_capture_only_qualified")) is not bool
        or type(receipt.get("latency_gate_qualified")) is not bool
        or type(receipt.get("resource_gate_qualified")) is not bool
    ):
        _append_once(errors, "tpacket_schema")

    offered = _nonnegative_integer(receipt.get("offered_packets"))
    received = _nonnegative_integer(receipt.get("synthetic_test_packets"))
    gap = _nonnegative_integer(receipt.get("offered_received_gap"))
    rx_discards = _nonnegative_integer(receipt.get("rx_discards_delta"))
    socket_drops = _nonnegative_integer(receipt.get("packet_socket_drops"))
    socket_freezes = _nonnegative_integer(
        receipt.get("packet_socket_freeze_queue_count")
    )
    offered_mpps = _finite_number(receipt.get("offered_mpps_sum"), minimum=0.0)
    capture_mpps = _finite_number(
        receipt.get("synthetic_rx_min_full_epoch_mpps"), minimum=0.0
    )
    p99 = _finite_number(receipt.get("p99_us"), minimum=0.0)
    p999 = _finite_number(receipt.get("p999_us"), minimum=0.0)
    host_cpu = _finite_number(receipt.get("host_cpu_fraction"), minimum=0.0)
    memory = _finite_number(receipt.get("capture_memory_fraction"), minimum=0.0)
    per_device = receipt.get("per_device_pps")
    per_device_values = (
        [_nonnegative_integer(value) for value in per_device]
        if isinstance(per_device, list)
        else []
    )
    pktgen_devices = _nonnegative_integer(receipt.get("pktgen_devices"))
    if (
        offered is None
        or offered == 0
        or received is None
        or gap is None
        or rx_discards is None
        or socket_drops is None
        or socket_freezes is None
        or offered_mpps is None
        or capture_mpps is None
        or p99 is None
        or p999 is None
        or host_cpu is None
        or memory is None
        or pktgen_devices is None
        or pktgen_devices == 0
        or len(per_device_values) != pktgen_devices
        or any(value is None for value in per_device_values)
    ):
        _append_once(errors, "tpacket_nonfinite_or_missing_metrics")

    derived_gap = None
    if offered is not None and received is not None:
        derived_gap = offered - received
    exact_loss = bool(
        gap is not None
        and derived_gap is not None
        and gap == derived_gap
        and rx_discards is not None
        and socket_drops is not None
        and gap == rx_discards + socket_drops
    )
    if receipt.get("loss_accounting_exact") is not exact_loss or not exact_loss:
        _append_once(errors, "tpacket_loss_accounting")

    if (
        offered_mpps is not None
        and per_device_values
        and all(value is not None for value in per_device_values)
        and not math.isclose(
            offered_mpps,
            sum(value for value in per_device_values if value is not None) / 1_000_000.0,
            rel_tol=0.0,
            abs_tol=1e-9,
        )
    ):
        _append_once(errors, "tpacket_rate_accounting")

    restoration_fields = (
        "restoration_verified",
        "irq_restoration_verified",
        "ring_restoration_verified",
        "coalesce_restoration_verified",
        "links_restored",
        "pktgen_module_unloaded",
    )
    if (
        any(receipt.get(name) is not True for name in restoration_fields)
        or receipt.get("runner_exit_status") != 0
    ):
        _append_once(errors, "tpacket_restoration")

    if (
        receipt.get("irq_assignment_verified") is not True
        or receipt.get("irq_affinity_stable") is not True
    ):
        _append_once(errors, "tpacket_execution_identity")

    eligible = bound and not errors
    zero_loss = bool(
        eligible
        and gap == 0
        and rx_discards == 0
        and socket_drops == 0
        and socket_freezes == 0
        and offered == received
    )
    rate_matched = bool(
        eligible
        and offered_mpps is not None
        and capture_mpps is not None
        and _rate_matched(offered_mpps, capture_mpps, ratio_min)
    )
    offered_target = bool(eligible and offered_mpps is not None and offered_mpps >= target)
    capture_target = bool(eligible and capture_mpps is not None and capture_mpps >= target)

    # Check that derived booleans in the receipt agree with the raw metrics.
    claimed_booleans = {
        "generator_12mpps_gate_qualified": offered_target,
        "capture_rate_12mpps_gate_qualified": capture_target,
        "loss_gate_qualified": zero_loss,
    }
    if any(receipt.get(name) is not expected for name, expected in claimed_booleans.items()):
        _append_once(errors, "tpacket_derived_gate_mismatch")
        eligible = False
        zero_loss = False
        rate_matched = False
        offered_target = False
        capture_target = False

    capture_limited = bool(
        eligible
        and (
            (gap is not None and gap > 0)
            or (rx_discards is not None and rx_discards > 0)
            or (socket_drops is not None and socket_drops > 0)
            or (offered_target and not capture_target)
        )
    )
    generator_limited = bool(
        eligible and not offered_target and zero_loss and rate_matched
    )
    target_qualified = bool(
        eligible
        and receipt.get("r0_capture_only_qualified") is True
        and offered_target
        and capture_target
        and zero_loss
    )
    return {
        "source_kind": "tpacket_breakthrough_acceptance",
        "candidate_id": receipt.get("candidate_id"),
        "eligible": eligible,
        "restoration_verified": receipt.get("restoration_verified") is True,
        "data_integrity_qualified": eligible,
        "metrics": {
            "offered_mpps": offered_mpps,
            "capture_min_mpps": capture_mpps,
            "offered_packets": offered,
            "received_packets": received,
            "packet_gap": gap,
            "rx_discards": rx_discards,
            "packet_socket_drops": socket_drops,
            "p99_us": p99,
            "p999_us": p999,
        },
        "findings": {
            "generator_limited": generator_limited,
            "capture_limited": capture_limited,
            "single_queue_path_limited": False,
        },
        "target_qualified": target_qualified,
        "errors": errors,
        "artifacts": [
            {
                key: artifact.get(key)
                for key in ("kind", "path", "sha256", "expected_sha256", "binding_qualified")
            }
        ],
    }


def analyze_capture_bottleneck(
    contract_artifact: dict[str, Any],
    dpdk_pairs: Iterable[tuple[dict[str, Any], dict[str, Any]]],
    tpacket_artifacts: Iterable[dict[str, Any]],
    *,
    input_errors: Iterable[str] = (),
) -> dict[str, Any]:
    """Combine independently bound observations without promoting diagnostics."""

    errors = [error for error in input_errors if isinstance(error, str) and error]
    contract_bound = _artifact_identity(contract_artifact, errors)
    contract = _validate_contract(contract_artifact.get("payload"), errors)
    target = _finite_number(contract.get("target_mpps"), minimum=0.0)
    ratio_min = _finite_number(contract.get("rate_match_ratio_min"), minimum=0.0)
    if target is None:
        target = REQUIRED_TARGET_MPPS
    if ratio_min is None:
        ratio_min = 1.0

    observations: list[dict[str, Any]] = []
    for result, acceptance in dpdk_pairs:
        observations.append(
            _analyze_dpdk(result, acceptance, target, ratio_min)
        )
    for artifact in tpacket_artifacts:
        observations.append(_analyze_tpacket(artifact, target, ratio_min))
    if not observations:
        _append_once(errors, "evidence_missing")
    for index, observation in enumerate(observations):
        for error in observation["errors"]:
            _append_once(errors, f"observation_{index}:{error}")

    eligible_count = sum(1 for value in observations if value["eligible"])
    if observations and eligible_count == 0:
        _append_once(errors, "no_eligible_observation")
    analysis_valid = bool(contract_bound and eligible_count > 0 and not errors)
    target_qualified = bool(
        analysis_valid and any(value["target_qualified"] for value in observations)
    )
    findings = {
        name: any(value["findings"][name] for value in observations)
        for name in (
            "generator_limited",
            "capture_limited",
            "single_queue_path_limited",
        )
    }
    if not analysis_valid:
        findings = {name: False for name in findings}
    findings["target_unproven"] = not target_qualified
    return {
        "schema_version": 1,
        "scope": "capture_bottleneck_analysis",
        "decision_id": contract.get("decision_id"),
        "target_mpps": target,
        "analysis_valid": analysis_valid,
        "evidence_binding_qualified": bool(
            analysis_valid
            and all(
                artifact["binding_qualified"]
                for observation in observations
                for artifact in observation["artifacts"]
            )
        ),
        "data_integrity_qualified": bool(
            analysis_valid
            and all(value["data_integrity_qualified"] for value in observations)
        ),
        "restoration_qualified": bool(
            analysis_valid
            and all(value["restoration_verified"] for value in observations)
        ),
        "eligible_observations": eligible_count,
        "findings": findings,
        "capture_target_qualified": target_qualified,
        "extrapolation_performed": False,
        "observations": observations,
        "errors": errors,
        "full_pipeline_qualified": False,
        "final_pareto_ingestion_allowed": False,
    }


def _expected_hashes(values: Sequence[str]) -> tuple[dict[str, str], list[str]]:
    expected: dict[str, str] = {}
    errors: list[str] = []
    for value in values:
        if "=" not in value:
            errors.append("expected_sha256_syntax")
            continue
        raw_path, digest = value.rsplit("=", 1)
        resolved = str(Path(raw_path).resolve())
        normalized = digest.lower()
        if not raw_path or not _is_sha256(normalized):
            errors.append("expected_sha256_syntax")
        elif resolved in expected and expected[resolved] != normalized:
            errors.append("expected_sha256_conflict")
        else:
            expected[resolved] = normalized
    return expected, errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--dpdk-result", type=Path)
    parser.add_argument("--dpdk-acceptance", type=Path)
    parser.add_argument("--tpacket-acceptance", type=Path, action="append", default=[])
    parser.add_argument(
        "--expected-sha256",
        action="append",
        default=[],
        metavar="PATH=SHA256",
        help="optionally pin any supplied input path to an expected SHA-256",
    )
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    expected, input_errors = _expected_hashes(args.expected_sha256)
    supplied_paths = [args.contract, *args.tpacket_acceptance]
    if args.dpdk_result is not None:
        supplied_paths.append(args.dpdk_result)
    if args.dpdk_acceptance is not None:
        supplied_paths.append(args.dpdk_acceptance)
    supplied_resolved = {str(path.resolve()) for path in supplied_paths}
    if any(path not in supplied_resolved for path in expected):
        input_errors.append("expected_sha256_path_not_supplied")

    def load(path: Path, kind: str) -> dict[str, Any]:
        return load_artifact(path, kind, expected.get(str(path.resolve())))

    contract = load(args.contract, "decision_contract")
    dpdk_pairs = []
    if (args.dpdk_result is None) != (args.dpdk_acceptance is None):
        input_errors.append("dpdk_pair_incomplete")
    elif args.dpdk_result is not None and args.dpdk_acceptance is not None:
        dpdk_pairs.append(
            (
                load(args.dpdk_result, "dpdk_result"),
                load(args.dpdk_acceptance, "dpdk_acceptance"),
            )
        )
    tpacket = [
        load(path, "tpacket_acceptance") for path in args.tpacket_acceptance
    ]
    analysis = analyze_capture_bottleneck(
        contract,
        dpdk_pairs,
        tpacket,
        input_errors=input_errors,
    )
    rendered = json.dumps(analysis, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if analysis["analysis_valid"] else 10


if __name__ == "__main__":
    raise SystemExit(main())
