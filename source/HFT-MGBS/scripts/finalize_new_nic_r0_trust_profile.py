#!/usr/bin/env python3
"""Finalize a new-NIC R0 trust profile from independently pinned approval.

This program is deliberately not an approver.  It never creates a helper
manifest, trust receipt, or change record.  It only emits the approved profile
when those pre-existing artifacts, their caller-supplied trust roots, and the
actual regular files all agree exactly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from hft_mgbs.new_nic_r0_unified import _validate_profile


SHA_RE = re.compile(r"^[0-9a-f]{64}$")
CHANGE_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{4,128}$")

HELPER_ROLES = (
    "xdp_runner",
    "dpdk_runner",
    "generator_runner",
    "resource_sampler",
    "fallback_orchestrator",
    "restore_helper",
    "campaign_executor",
    "trust_root_recorder",
)
CORE_PATHS = {
    "contract": Path("configs/new_nic_r0_campaign_contract_v1.json"),
    "runner": Path("scripts/run_new_nic_r0_campaign.sh"),
    "composer": Path("scripts/compose_new_nic_r0_acceptance.py"),
    "evaluator": Path("hft_mgbs/new_nic_r0.py"),
}
CORE_SHA256 = {
    "contract": "65f483c72e0bdf2e5dd4c7be68501b4ab0d8bc85f1ae999756906c37bb4e7c4b",
    "runner": "c8e83e8017ab30d2e67a5a49fe43327d0f373882a948b42cf7f031f63b11fc90",
    "composer": "209063c8031f9289a6a1c2087e3bd2f44aca9e78088199267224249bb8e0408f",
    "evaluator": "1665ad49a32edf9ce9d8c57a47d89120257cc7408bfc0d0d8f6296a7dfda222e",
}
APPROVED_HASH_ROLES = frozenset(CORE_PATHS) | frozenset(HELPER_ROLES)
REQUIRED_ARTIFACT_ROLES = (
    "campaign",
    "contract",
    "arrival_inventory",
    "arrival_preflight",
    "arrival_evidence_manifest",
    "execution_plan",
    "execution_plan_binding",
    "restoration_before",
    "restoration_after",
    "xdp_run_1",
    "xdp_run_2",
    "xdp_run_3",
    "dpdk_run_1",
    "dpdk_run_2",
    "dpdk_run_3",
    "fallback_trial_1",
    "fallback_trial_2",
    "fallback_trial_3",
    "xdp_runner",
    "dpdk_runner",
    "generator_runner",
    "resource_sampler",
    "fallback_orchestrator",
    "restore_helper",
    "campaign_executor",
    "trust_root_recorder",
    "runner",
    "composer",
    "evaluator",
)
BACKEND_MAPPING = {
    "campaign_primary": "native_af_xdp_forced_zerocopy",
    "unified_primary": "native_af_xdp_forced_zerocopy",
    "campaign_fallback": "dpdk_rss_tss_multiqueue",
    "unified_fallback": "dpdk_multiqueue_rss_tss",
}
APPROVED_PROFILE_KEYS = {
    "schema_version",
    "scope",
    "status",
    "contract_id",
    "required_artifact_roles",
    "approved_role_sha256",
    "evaluator_entrypoint",
    "expected_audit_scope",
    "backend_mapping",
    "production_qualified",
    "final_pareto_ingestion_allowed",
}
PENDING_PROFILE_KEYS = APPROVED_PROFILE_KEYS | {"pending_roles"}
APPROVAL_RECORD_KEYS = {
    "schema_version",
    "scope",
    "change_id",
    "approver",
    "approved",
    "contract_id",
    "pending_profile_sha256",
    "helper_manifest_sha256",
    "approved_role_sha256",
}


def _pairs(items: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> None:
    raise ValueError("non-finite JSON number: " + value)


def _is_sha(value: Any) -> bool:
    return isinstance(value, str) and SHA_RE.fullmatch(value) is not None


def _reject_symlink_components(path: Path, label: str) -> Path:
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current = current / part
        if current.is_symlink():
            raise ValueError(label + " path contains a symlink")
    return absolute


def _stable_bytes(path: Path) -> bytes:
    """Read one non-symlink regular file while detecting common TOCTOU drift."""

    if not path.is_absolute():
        raise ValueError("trusted input path must be absolute")
    path = _reject_symlink_components(path, "trusted input")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError("trusted input is not a regular file")
        chunks: list[bytes] = []
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                break
            chunks.append(block)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    identity_before = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
    )
    identity_after = (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    )
    if identity_before != identity_after:
        raise ValueError("trusted input changed while being read")
    return b"".join(chunks)


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_json(path: Path) -> tuple[dict[str, Any], str]:
    raw = _stable_bytes(path)
    value = json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=_pairs,
        parse_constant=_reject_nonfinite,
    )
    if not isinstance(value, dict):
        raise ValueError("top-level JSON object required")
    return value, _digest(raw)


def _absolute_directory(path: Path, label: str) -> Path:
    if not path.is_absolute():
        raise ValueError(label + " must be an absolute directory")
    path = _reject_symlink_components(path, label)
    resolved = path.resolve(strict=True)
    if not resolved.is_dir():
        raise ValueError(label + " is not a directory")
    return resolved


def _resolved_regular_under(root: Path, raw: str, label: str) -> Path:
    if not isinstance(raw, str) or not raw or "\x00" in raw:
        raise ValueError(label + " path is invalid")
    candidate = Path(raw)
    if not candidate.is_absolute():
        raise ValueError(label + " path must be absolute")
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(label + " path escapes its trusted root") from exc
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(label + " path contains a symlink")
    resolved = candidate.resolve(strict=True)
    resolved.relative_to(root)
    if not stat.S_ISREG(resolved.stat().st_mode):
        raise ValueError(label + " is not a regular file")
    return resolved


def _outside(path: Path, roots: Sequence[Path], label: str) -> Path:
    if not path.is_absolute():
        raise ValueError(label + " must be an absolute file")
    path = _reject_symlink_components(path, label)
    resolved = path.resolve(strict=True)
    if not resolved.is_file():
        raise ValueError(label + " is not a regular file")
    for root in roots:
        try:
            resolved.relative_to(root)
        except ValueError:
            continue
        raise ValueError(label + " must be outside mutable/project roots")
    return resolved


def _validate_pending(profile: Mapping[str, Any]) -> Mapping[str, Any]:
    if set(profile) != PENDING_PROFILE_KEYS:
        raise ValueError("pending profile fields are not exact")
    if (
        profile.get("schema_version") != 1
        or profile.get("scope") != "hft_mgbs_new_nic_r0_unified_trust_profile"
        or profile.get("status") != "hardware_helpers_pending"
        or profile.get("contract_id")
        != "hft-new-nic-r0-xdp-primary-dpdk-fallback-v1"
        or profile.get("required_artifact_roles") != list(REQUIRED_ARTIFACT_ROLES)
        or profile.get("pending_roles") != list(HELPER_ROLES)
        or profile.get("evaluator_entrypoint")
        != "hft_mgbs.new_nic_r0:evaluate_r0_campaign"
        or profile.get("expected_audit_scope")
        != "new_high_speed_nic_r0_campaign_audit"
        or profile.get("backend_mapping") != BACKEND_MAPPING
        or profile.get("production_qualified") is not False
        or profile.get("final_pareto_ingestion_allowed") is not False
    ):
        raise ValueError("pending profile envelope is invalid")
    hashes = profile.get("approved_role_sha256")
    if not isinstance(hashes, Mapping) or set(hashes) != APPROVED_HASH_ROLES:
        raise ValueError("pending profile role hashes are not exact")
    if any(hashes.get(role) is not None for role in HELPER_ROLES):
        raise ValueError("pending helper roles must contain JSON null")
    if any(hashes.get(role) != expected for role, expected in CORE_SHA256.items()):
        raise ValueError("pending core identity differs from the frozen identity")
    return hashes


def _parse_helper_manifest(raw: bytes) -> dict[str, tuple[str, str]]:
    try:
        lines = raw.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise ValueError("helper manifest is not UTF-8") from exc
    result: dict[str, tuple[str, str]] = {}
    for index, line in enumerate(lines, 1):
        fields = line.split()
        if len(fields) != 3:
            raise ValueError("helper manifest line {} is malformed".format(index))
        role, path, declared = fields
        if role in result:
            raise ValueError("helper manifest role is duplicated: " + role)
        if not _is_sha(declared):
            raise ValueError("helper manifest SHA-256 is invalid: " + role)
        result[role] = (path, declared)
    if set(result) != APPROVED_HASH_ROLES:
        raise ValueError("helper manifest must contain the 12 approved roles exactly")
    return result


def _verify_schema_constants(repo_root: Path) -> None:
    schema_path = repo_root / "configs/schemas/new_nic_r0_unified_trust_profile_v1.schema.json"
    schema, _ = _read_json(schema_path)
    try:
        roles = schema["properties"]["required_artifact_roles"]["const"]
        properties = schema["properties"]["approved_role_sha256"]["properties"]
    except (KeyError, TypeError) as exc:
        raise ValueError("approved trust-profile schema structure is invalid") from exc
    if roles != list(REQUIRED_ARTIFACT_ROLES):
        raise ValueError("approved schema artifact roles drifted")
    for role, expected in CORE_SHA256.items():
        if properties.get(role, {}).get("const") != expected:
            raise ValueError("approved schema core identity drifted: " + role)


def _validate_approval_record(
    record: Mapping[str, Any],
    *,
    pending_sha256: str,
    manifest_sha256: str,
    approved_hashes: Mapping[str, str],
) -> None:
    if set(record) != APPROVAL_RECORD_KEYS:
        raise ValueError("approval record fields are not exact")
    if (
        record.get("schema_version") != 1
        or record.get("scope") != "new_nic_r0_trust_profile_external_approval"
        or record.get("approved") is not True
        or record.get("contract_id")
        != "hft-new-nic-r0-xdp-primary-dpdk-fallback-v1"
        or record.get("pending_profile_sha256") != pending_sha256
        or record.get("helper_manifest_sha256") != manifest_sha256
        or record.get("approved_role_sha256") != dict(approved_hashes)
        or not isinstance(record.get("approver"), str)
        or not record.get("approver").strip()
        or not isinstance(record.get("change_id"), str)
        or CHANGE_ID_RE.fullmatch(record["change_id"]) is None
    ):
        raise ValueError("approval record does not bind the approved identities")


def _atomic_create_json(path: Path, value: Mapping[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise ValueError("approved output already exists")
    parent = _absolute_directory(path.parent, "approved output parent")
    raw = (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix="." + path.name + ".tmp-", dir=parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists() or path.is_symlink():
            raise ValueError("approved output appeared during finalization")
        os.link(temporary, path)
        temporary.unlink()
        if os.name != "nt":
            directory_fd = os.open(parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        if temporary.exists():
            temporary.unlink()


def finalize_trust_profile(
    *,
    repo_root: Path,
    pending_profile_path: Path,
    helper_root: Path,
    helper_manifest_path: Path,
    trusted_helper_manifest_sha256: str,
    approval_record_path: Path,
    trusted_approval_record_sha256: str,
    trust_receipt_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Verify external approval and atomically create one approved instance."""

    if not _is_sha(trusted_helper_manifest_sha256):
        raise ValueError("trusted helper-manifest SHA-256 is invalid")
    if not _is_sha(trusted_approval_record_sha256):
        raise ValueError("trusted approval-record SHA-256 is invalid")
    repo = _absolute_directory(repo_root, "repository root")
    helpers = _absolute_directory(helper_root, "helper root")
    output = output_path.absolute()
    if output == pending_profile_path.absolute():
        raise ValueError("pending profile and approved output must differ")
    output_parent = _absolute_directory(output.parent, "approved output parent")

    pending_path = pending_profile_path.absolute()
    pending, pending_sha256 = _read_json(pending_path)
    _validate_pending(pending)
    _verify_schema_constants(repo)

    approval_path = _outside(
        approval_record_path,
        (repo, helpers, output_parent),
        "approval record",
    )
    receipt_path = _outside(
        trust_receipt_path,
        (repo, helpers, output_parent),
        "trust receipt",
    )
    if approval_path == receipt_path:
        raise ValueError("approval record and trust receipt must be distinct files")

    manifest_path = _outside(
        helper_manifest_path,
        (repo, helpers, output_parent),
        "helper manifest",
    )
    manifest_raw = _stable_bytes(manifest_path)
    manifest_sha256 = _digest(manifest_raw)
    if manifest_sha256 != trusted_helper_manifest_sha256:
        raise ValueError("helper manifest differs from the externally pinned root")
    manifest = _parse_helper_manifest(manifest_raw)

    approved_hashes: dict[str, str] = {}
    normalized_paths: set[Path] = set()
    file_identities: set[tuple[int, int]] = set()
    for role in sorted(APPROVED_HASH_ROLES):
        raw_path, declared = manifest[role]
        if role in CORE_PATHS:
            expected_path = (repo / CORE_PATHS[role]).resolve(strict=True)
            candidate = Path(raw_path)
            if not candidate.is_absolute() or candidate.resolve(strict=True) != expected_path:
                raise ValueError("core role path differs from the frozen path: " + role)
            path = expected_path
        else:
            path = _resolved_regular_under(helpers, raw_path, role)
            if os.name != "nt" and path.stat().st_mode & 0o111 == 0:
                raise ValueError("helper role is not executable: " + role)
        if path in normalized_paths:
            raise ValueError("multiple roles reuse one path")
        normalized_paths.add(path)
        metadata = path.stat()
        identity = (metadata.st_dev, metadata.st_ino)
        if identity in file_identities:
            raise ValueError("multiple roles reuse one file identity")
        file_identities.add(identity)
        actual = _digest(_stable_bytes(path))
        if actual != declared:
            raise ValueError("approved role content differs from its manifest: " + role)
        if role in CORE_SHA256 and actual != CORE_SHA256[role]:
            raise ValueError("frozen core role drifted: " + role)
        approved_hashes[role] = actual

    receipt_lines = _stable_bytes(receipt_path).decode("utf-8").splitlines()
    if receipt_lines != [manifest_sha256]:
        raise ValueError("external trust receipt does not contain the helper root")
    approval, approval_sha256 = _read_json(approval_path)
    if approval_sha256 != trusted_approval_record_sha256:
        raise ValueError("approval record differs from the externally pinned root")
    _validate_approval_record(
        approval,
        pending_sha256=pending_sha256,
        manifest_sha256=manifest_sha256,
        approved_hashes=approved_hashes,
    )

    result = {
        key: value
        for key, value in pending.items()
        if key in APPROVED_PROFILE_KEYS
    }
    result["status"] = "approved_for_new_nic_r0_unified_recompute"
    result["approved_role_sha256"] = approved_hashes
    if set(result) != APPROVED_PROFILE_KEYS:
        raise ValueError("approved profile fields are not exact")
    _validate_profile(result)
    _atomic_create_json(output, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--pending-profile", required=True, type=Path)
    parser.add_argument("--helper-root", required=True, type=Path)
    parser.add_argument("--helper-manifest", required=True, type=Path)
    parser.add_argument("--trusted-helper-manifest-sha256", required=True)
    parser.add_argument("--approval-record", required=True, type=Path)
    parser.add_argument("--trusted-approval-record-sha256", required=True)
    parser.add_argument("--trust-receipt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    finalize_trust_profile(
        repo_root=arguments.repo_root,
        pending_profile_path=arguments.pending_profile,
        helper_root=arguments.helper_root,
        helper_manifest_path=arguments.helper_manifest,
        trusted_helper_manifest_sha256=arguments.trusted_helper_manifest_sha256,
        approval_record_path=arguments.approval_record,
        trusted_approval_record_sha256=arguments.trusted_approval_record_sha256,
        trust_receipt_path=arguments.trust_receipt,
        output_path=arguments.output,
    )
    print("approved_profile={}".format(arguments.output.resolve()))
    print("sha256={}".format(_digest(_stable_bytes(arguments.output.resolve()))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
