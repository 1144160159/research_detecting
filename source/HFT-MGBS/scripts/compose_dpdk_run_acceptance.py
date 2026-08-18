"""Compose the final, fail-closed DPDK runner acceptance record.

The data/resource validator deliberately cannot qualify the runner because host
restoration, evidence inventory, and evidence hash checks happen outside that
validator.  This module joins those independently produced facts without
allowing any missing or malformed input to default to success.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable, Sequence


SHA256_RE = re.compile(r"[0-9a-fA-F]{64}")
STATUS_NAMES = (
    "original_exit_status",
    "validator_exit_status",
    "restore_status",
    "evidence_status",
    "base_hash_check_status",
    "complete_hash_check_status",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def append_once(errors: list[str], error: str) -> None:
    if error not in errors:
        errors.append(error)


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def _valid_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(isinstance(item, str) and item for item in value)
        and len(value) == len(set(value))
    )


def _validate_data_resource(
    payload: Any, errors: list[str]
) -> tuple[dict[str, Any], bool]:
    if not isinstance(payload, dict):
        append_once(errors, "data_resource_acceptance_type")
        return {}, False

    schema_ok = (
        payload.get("schema_version") == 1
        and payload.get("scope") == "dpdk_release_gate_acceptance"
        and payload.get("qualification_mode") == "release_gate_v2"
        and isinstance(payload.get("candidate_id"), str)
        and bool(payload.get("candidate_id"))
        and _valid_sha256(payload.get("frozen_thresholds_sha256"))
        and payload.get("performance_gate_frozen") is True
        and payload.get("resource_gate_frozen") is True
        and payload.get("runner_qualified") is False
        and payload.get("r0_capture_only_qualified") is False
        and payload.get("full_pipeline_qualified") is False
        and payload.get("final_pareto_ingestion_allowed") is False
    )
    if not schema_ok:
        append_once(errors, "data_resource_acceptance_schema")

    upstream_errors = payload.get("errors")
    errors_ok = (
        isinstance(upstream_errors, list)
        and all(isinstance(item, str) and item for item in upstream_errors)
        and not upstream_errors
    )
    if not errors_ok:
        append_once(errors, "data_resource_acceptance_errors")

    qualified = payload.get("data_resource_qualified") is True
    if not qualified:
        append_once(errors, "data_resource_not_qualified")

    return payload, schema_ok and errors_ok and qualified


def _validate_inventory(
    payload: Any,
    restoration_verified: Any,
    errors: list[str],
) -> tuple[dict[str, Any], bool]:
    if not isinstance(payload, dict):
        append_once(errors, "evidence_inventory_type")
        return {}, False

    required = payload.get("required")
    present = payload.get("present")
    missing = payload.get("missing")
    empty_required = payload.get("empty_required")
    lists_ok = all(
        _valid_string_list(value)
        for value in (required, present, missing, empty_required)
    )
    if not lists_ok:
        append_once(errors, "evidence_inventory_schema")
        return payload, False

    membership_ok = (
        not missing
        and not empty_required
        and set(required).issubset(set(present))
    )
    schema_ok = (
        payload.get("schema_version") == 1
        and payload.get("restoration_verified") is restoration_verified
        and payload.get("evidence_complete_before_hash") is True
        and membership_ok
    )
    if not schema_ok:
        append_once(errors, "evidence_inventory_incomplete")
    return payload, schema_ok


def _validate_statuses(
    statuses: dict[str, Any],
    restoration_verified: Any,
    termination_signal: Any,
    errors: list[str],
) -> bool:
    statuses_ok = True
    for name in STATUS_NAMES:
        value = statuses.get(name)
        if type(value) is not int or value < 0:
            append_once(errors, f"{name}_type")
            statuses_ok = False
        elif value != 0:
            append_once(errors, f"{name}_nonzero")
            statuses_ok = False

    if type(restoration_verified) is not bool:
        append_once(errors, "restoration_verified_type")
        statuses_ok = False
    elif not restoration_verified:
        append_once(errors, "host_restoration")
        statuses_ok = False

    if not isinstance(termination_signal, str):
        append_once(errors, "termination_signal_type")
        statuses_ok = False
    elif termination_signal.strip().lower() not in ("", "none"):
        append_once(errors, "termination_signal_present")
        statuses_ok = False

    return statuses_ok


def compose_acceptance(
    data_resource_acceptance: Any,
    evidence_inventory: Any,
    *,
    data_resource_acceptance_sha256: Any,
    evidence_inventory_sha256: Any,
    base_hash_evidence_sha256: Any,
    complete_hash_evidence_sha256: Any,
    original_exit_status: Any,
    validator_exit_status: Any,
    restore_status: Any,
    restoration_verified: Any,
    evidence_status: Any,
    base_hash_check_status: Any,
    complete_hash_check_status: Any,
    termination_signal: Any,
    input_errors: Iterable[str] = (),
) -> dict[str, Any]:
    """Return a final runner record; malformed inputs can never qualify."""

    errors: list[str] = []
    for error in input_errors:
        if isinstance(error, str) and error:
            append_once(errors, error)
        else:
            append_once(errors, "input_error_type")

    data_payload, data_ok = _validate_data_resource(
        data_resource_acceptance, errors
    )
    _, inventory_ok = _validate_inventory(
        evidence_inventory, restoration_verified, errors
    )

    statuses = {
        "original_exit_status": original_exit_status,
        "validator_exit_status": validator_exit_status,
        "restore_status": restore_status,
        "evidence_status": evidence_status,
        "base_hash_check_status": base_hash_check_status,
        "complete_hash_check_status": complete_hash_check_status,
    }
    statuses_ok = _validate_statuses(
        statuses, restoration_verified, termination_signal, errors
    )

    input_sha256 = {
        "data_resource_acceptance": data_resource_acceptance_sha256,
        "evidence_inventory": evidence_inventory_sha256,
        "evidence_sha256_base_check": base_hash_evidence_sha256,
        "evidence_sha256_complete_check": complete_hash_evidence_sha256,
    }
    for name, digest in input_sha256.items():
        if not _valid_sha256(digest):
            append_once(errors, f"{name}_sha256")
        elif digest != digest.lower():
            input_sha256[name] = digest.lower()

    hashes_ok = all(_valid_sha256(digest) for digest in input_sha256.values())
    qualified = data_ok and inventory_ok and statuses_ok and hashes_ok and not errors
    signal_value = (
        termination_signal
        if isinstance(termination_signal, str)
        else None
    )
    return {
        "schema_version": 1,
        "scope": "dpdk_release_gate_runner_acceptance",
        "receipt_semantics": "derived_from_preacceptance_sealed_evidence_v1",
        "standalone_receipt_trusted": False,
        "evidence_seal_excludes": ["acceptance.json", "acceptance.stdout.json"],
        "candidate_id": data_payload.get("candidate_id"),
        "frozen_thresholds_sha256": data_payload.get(
            "frozen_thresholds_sha256"
        ),
        "input_sha256": input_sha256,
        "status": statuses,
        "termination_signal": signal_value,
        "data_resource_qualified": data_ok,
        "restoration_verified": restoration_verified is True,
        "evidence_complete_before_hash": inventory_ok,
        "hash_checks_verified": (
            hashes_ok
            and type(base_hash_check_status) is int
            and base_hash_check_status == 0
            and type(complete_hash_check_status) is int
            and complete_hash_check_status == 0
        ),
        "errors": errors,
        "runner_qualified": qualified,
        "r0_capture_only_qualified": qualified,
        "full_pipeline_qualified": False,
        "final_pareto_ingestion_allowed": False,
    }


def _read_json_input(
    path: Path, name: str, errors: list[str]
) -> tuple[Any, str | None]:
    if not path.is_file():
        append_once(errors, f"{name}_missing")
        return None, None
    try:
        digest = sha256_file(path)
    except OSError:
        append_once(errors, f"{name}_unreadable")
        return None, None
    try:
        return json.loads(path.read_text(encoding="utf-8")), digest
    except (OSError, UnicodeError, json.JSONDecodeError):
        append_once(errors, f"{name}_json_invalid")
        return None, digest


def _resolve_hash_evidence(
    value: str, name: str, errors: list[str]
) -> tuple[str | None, str]:
    if SHA256_RE.fullmatch(value):
        return value.lower(), "provided_sha256"

    path = Path(value)
    if not path.is_file():
        append_once(errors, f"{name}_missing")
        return None, "invalid"
    try:
        if path.stat().st_size == 0:
            append_once(errors, f"{name}_empty")
        return sha256_file(path), "file"
    except OSError:
        append_once(errors, f"{name}_unreadable")
        return None, "invalid"


def _parse_status(value: str, name: str, errors: list[str]) -> Any:
    try:
        parsed = int(value, 10)
    except (TypeError, ValueError):
        append_once(errors, f"{name}_type")
        return value
    if parsed < 0:
        append_once(errors, f"{name}_type")
    return parsed


def _parse_bool(value: str, name: str, errors: list[str]) -> Any:
    if value == "true":
        return True
    if value == "false":
        return False
    append_once(errors, f"{name}_type")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-resource-acceptance", type=Path, required=True)
    parser.add_argument("--evidence-inventory", type=Path, required=True)
    parser.add_argument("--original-exit-status", required=True)
    parser.add_argument("--validator-exit-status", required=True)
    parser.add_argument("--restore-status", required=True)
    parser.add_argument("--restoration-verified", required=True)
    parser.add_argument("--evidence-status", required=True)
    parser.add_argument("--base-hash-check-status", required=True)
    parser.add_argument("--complete-hash-check-status", required=True)
    parser.add_argument("--termination-signal", required=True)
    parser.add_argument("--base-hash-evidence", required=True)
    parser.add_argument("--complete-hash-evidence", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    input_errors: list[str] = []
    data_resource, data_sha = _read_json_input(
        args.data_resource_acceptance,
        "data_resource_acceptance",
        input_errors,
    )
    inventory, inventory_sha = _read_json_input(
        args.evidence_inventory,
        "evidence_inventory",
        input_errors,
    )
    base_sha, base_source = _resolve_hash_evidence(
        args.base_hash_evidence,
        "evidence_sha256_base_check",
        input_errors,
    )
    complete_sha, complete_source = _resolve_hash_evidence(
        args.complete_hash_evidence,
        "evidence_sha256_complete_check",
        input_errors,
    )

    status_values = {
        name: _parse_status(
            getattr(args, name), name, input_errors
        )
        for name in STATUS_NAMES
    }
    restoration_verified = _parse_bool(
        args.restoration_verified,
        "restoration_verified",
        input_errors,
    )
    acceptance = compose_acceptance(
        data_resource,
        inventory,
        data_resource_acceptance_sha256=data_sha,
        evidence_inventory_sha256=inventory_sha,
        base_hash_evidence_sha256=base_sha,
        complete_hash_evidence_sha256=complete_sha,
        restoration_verified=restoration_verified,
        termination_signal=args.termination_signal,
        input_errors=input_errors,
        **status_values,
    )
    acceptance["hash_evidence_source"] = {
        "evidence_sha256_base_check": base_source,
        "evidence_sha256_complete_check": complete_source,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(acceptance, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(acceptance, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if acceptance["runner_qualified"] else 10


if __name__ == "__main__":
    raise SystemExit(main())
