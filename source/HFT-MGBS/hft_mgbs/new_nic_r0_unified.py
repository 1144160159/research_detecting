"""Fail-closed bridge from a sealed new-NIC R0 campaign into unified audit.

The bridge never trusts the saved campaign audit as a verdict.  It verifies
the external provenance roots and all manifest members, then invokes the
frozen R0 evaluator and requires canonical equality with the saved audit.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import stat
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

from hft_mgbs.new_nic_r0 import canonical_sha256, evaluate_r0_campaign


SHA_RE = re.compile(r"^[0-9a-f]{64}$")
UNIFIED_PRIMARY_BACKEND = "native_af_xdp_forced_zerocopy"
UNIFIED_FALLBACK_BACKEND = "dpdk_multiqueue_rss_tss"


def stage_backend_binding_from_r0_identity(
    identity: Mapping[str, Any],
) -> Dict[str, str]:
    """Return the exact dual-backend stage binding from a qualified R0 identity.

    The caller still owns the R0 qualification gate.  This adapter only makes
    it impossible to silently discard the DPDK fallback identity or reorder the
    XDP-primary/DPDK-fallback pair while wiring the subsequent stage campaign.
    """

    if not isinstance(identity, Mapping):
        raise ValueError("new-NIC R0 identity must be an object")
    primary = identity.get("primary_backend")
    fallback = identity.get("fallback_backend")
    if (
        primary != UNIFIED_PRIMARY_BACKEND
        or fallback != UNIFIED_FALLBACK_BACKEND
        or identity.get("backends") != [primary, fallback]
        or primary == fallback
    ):
        raise ValueError("new-NIC R0 stage backend identity is invalid")
    return {
        "primary_backend": primary,
        "fallback_backend": fallback,
    }


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _pairs(pairs: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: {}".format(key))
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    raise ValueError("non-finite JSON number: {}".format(value))


def _read_json(path: Path) -> Dict[str, Any]:
    result = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_pairs,
        parse_constant=_nonfinite,
    )
    if not isinstance(result, dict):
        raise ValueError("JSON object required: {}".format(path))
    return result


def _is_sha(value: Any) -> bool:
    return isinstance(value, str) and SHA_RE.fullmatch(value) is not None


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _resolve_remote(receipt_root: Path, remote_path: Any) -> Path:
    if not isinstance(remote_path, str) or not remote_path.startswith("/"):
        raise ValueError("remote artifact path must be absolute")
    base = receipt_root.resolve(strict=True)
    candidate = base.joinpath(*PurePosixPath(remote_path).parts[1:])
    current = base
    for part in PurePosixPath(remote_path).parts[1:]:
        current = current / part
        if current.is_symlink():
            raise ValueError("remote artifact path contains a symlink")
    resolved = candidate.resolve(strict=True)
    resolved.relative_to(base)
    if not stat.S_ISREG(resolved.stat().st_mode):
        raise ValueError("remote artifact is not a regular file")
    return resolved


def _verify_reference(
    reference: Any,
    receipt_root: Path,
    expected_parent: Optional[Path] = None,
) -> Path:
    if not isinstance(reference, Mapping) or set(reference) != {"path", "sha256"}:
        raise ValueError("artifact reference must contain only path and sha256")
    expected = reference.get("sha256")
    if not _is_sha(expected):
        raise ValueError("artifact reference SHA-256 is invalid")
    path = _resolve_remote(receipt_root, reference.get("path"))
    if expected_parent is not None and path.parent != expected_parent:
        raise ValueError("campaign artifact is outside the sealed root")
    if _sha_file(path) != expected:
        raise ValueError("artifact reference SHA-256 mismatch")
    return path


def _resolve_manifest_member(root: Path, raw: Any) -> Path:
    if not isinstance(raw, str) or not raw or "\x00" in raw:
        raise ValueError("invalid manifest member path")
    relative = PurePosixPath(raw)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("manifest member path escapes root")
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("manifest member path contains a symlink")
    resolved = current.resolve(strict=True)
    resolved.relative_to(root)
    if not stat.S_ISREG(resolved.stat().st_mode):
        raise ValueError("manifest member is not a regular file")
    return resolved


def _read_single_sha(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) != 1 or SHA_RE.fullmatch(lines[0]) is None:
        raise ValueError("external trust receipt must contain one lowercase SHA-256")
    return lines[0]


def _validate_profile(profile: Mapping[str, Any]) -> Tuple[list[str], Mapping[str, str]]:
    if (
        profile.get("schema_version") != 1
        or profile.get("scope") != "hft_mgbs_new_nic_r0_unified_trust_profile"
        or profile.get("status") != "approved_for_new_nic_r0_unified_recompute"
        or profile.get("contract_id") != "hft-new-nic-r0-xdp-primary-dpdk-fallback-v1"
        or profile.get("evaluator_entrypoint")
        != "hft_mgbs.new_nic_r0:evaluate_r0_campaign"
        or profile.get("expected_audit_scope")
        != "new_high_speed_nic_r0_campaign_audit"
        or profile.get("production_qualified") is not False
        or profile.get("final_pareto_ingestion_allowed") is not False
    ):
        raise ValueError("new-NIC R0 trust profile envelope is invalid")
    roles = profile.get("required_artifact_roles")
    hashes = profile.get("approved_role_sha256")
    if (
        not isinstance(roles, list)
        or not roles
        or len(roles) != len(set(roles))
        or not all(isinstance(role, str) and role for role in roles)
        or not isinstance(hashes, Mapping)
        or not all(_is_sha(value) for value in hashes.values())
    ):
        raise ValueError("new-NIC R0 trust profile roles or hashes are invalid")
    approved_roles = {
        "contract",
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
    }
    if set(hashes) != approved_roles:
        raise ValueError("trust profile must approve every executable/code role exactly")
    return list(roles), hashes


def audit_new_nic_r0_campaign(
    bridge: Any,
    trust_profile: Mapping[str, Any],
    receipt_root: Optional[Path],
    errors: list[str],
    evidence_hashes: dict[str, str],
) -> Tuple[bool, bool, Dict[str, Any]]:
    """Verify and recompute one complete XDP-primary/DPDK-fallback campaign."""

    empty_identity: Dict[str, Any] = {
        "campaign_id": None,
        "run_bundle_identities": [],
        "generator_run_identities": [],
        "hardware_identity_sha256": [],
        "backends": [],
        "contracts": [],
        "primary_backend": None,
        "fallback_backend": None,
        "artifact_manifest_sha256": None,
    }
    if bridge is None:
        errors.append("new_nic_r0_campaign.pending")
        return False, False, empty_identity
    prefix = "new_nic_r0_campaign"
    try:
        if receipt_root is None:
            raise ValueError("receipt root is required")
        if not isinstance(bridge, Mapping):
            raise ValueError("bridge must be an object")
        required_bridge = {
            "schema_version", "scope", "integration_mode", "campaign_id",
            "artifact_root", "trust_profile_config_name", "artifact_manifest",
            "r0_audit", "runner_state", "frozen_helper_manifest",
            "external_trust_root_receipt", "external_change_record",
            "trusted_evidence_manifest_sha256", "trusted_helper_manifest_sha256",
            "trusted_arrival_manifest_sha256", "backend_mapping", "expected_result",
        }
        if set(bridge) != required_bridge:
            raise ValueError("bridge fields do not match frozen schema")
        if (
            bridge.get("schema_version") != 1
            or bridge.get("scope") != "hft_mgbs_new_nic_r0_unified_bridge"
            or bridge.get("integration_mode") != "exclusive_new_nic_campaign_v1"
            or bridge.get("trust_profile_config_name") != "new_nic_r0_trust_profile"
        ):
            raise ValueError("bridge envelope is invalid")
        campaign_id = bridge.get("campaign_id")
        if not isinstance(campaign_id, str) or re.fullmatch(r"[A-Za-z0-9._:-]{1,128}", campaign_id) is None:
            raise ValueError("campaign_id is invalid")
        roles, approved_hashes = _validate_profile(trust_profile)
        if bridge.get("backend_mapping") != trust_profile.get("backend_mapping"):
            raise ValueError("backend mapping differs from approved profile")
        mapping = bridge["backend_mapping"]
        if mapping != {
            "campaign_primary": "native_af_xdp_forced_zerocopy",
            "unified_primary": "native_af_xdp_forced_zerocopy",
            "campaign_fallback": "dpdk_rss_tss_multiqueue",
            "unified_fallback": "dpdk_multiqueue_rss_tss",
        }:
            raise ValueError("backend mapping is not the approved mapping")
        expected_result = bridge.get("expected_result")
        if not isinstance(expected_result, Mapping) or expected_result != {
            "status": "r0_qualified",
            "xdp_primary_repeats_qualified": 3,
            "dpdk_fallback_repeats_qualified": 3,
            "fallback_trials_qualified": 3,
            "restoration_qualified": True,
            "r0_qualified": True,
            "mutations_performed": True,
            "production_qualified": False,
            "final_pareto_ingestion_allowed": False,
        }:
            raise ValueError("bridge expected result is not frozen")
        evidence_sha = bridge.get("trusted_evidence_manifest_sha256")
        helper_sha = bridge.get("trusted_helper_manifest_sha256")
        arrival_sha = bridge.get("trusted_arrival_manifest_sha256")
        if not all(_is_sha(value) for value in (evidence_sha, helper_sha, arrival_sha)):
            raise ValueError("bridge trust roots are invalid")

        artifact_root_text = bridge.get("artifact_root")
        if not isinstance(artifact_root_text, str) or not artifact_root_text.startswith("/"):
            raise ValueError("artifact_root must be an absolute remote path")
        mirror_root = receipt_root.resolve(strict=True)
        campaign_root = mirror_root.joinpath(*PurePosixPath(artifact_root_text).parts[1:])
        current = mirror_root
        for part in PurePosixPath(artifact_root_text).parts[1:]:
            current = current / part
            if current.is_symlink():
                raise ValueError("artifact root contains a symlink")
        campaign_root = campaign_root.resolve(strict=True)
        campaign_root.relative_to(mirror_root)
        if not campaign_root.is_dir():
            raise ValueError("artifact root is not a directory")

        manifest_path = _verify_reference(
            bridge.get("artifact_manifest"), receipt_root, campaign_root
        )
        audit_path = _verify_reference(bridge.get("r0_audit"), receipt_root, campaign_root)
        state_path = _verify_reference(bridge.get("runner_state"), receipt_root, campaign_root)
        helper_manifest_path = _verify_reference(
            bridge.get("frozen_helper_manifest"), receipt_root, campaign_root
        )
        trust_receipt_path = _verify_reference(
            bridge.get("external_trust_root_receipt"), receipt_root
        )
        change_record_path = _verify_reference(
            bridge.get("external_change_record"), receipt_root
        )
        for external in (trust_receipt_path, change_record_path):
            try:
                external.relative_to(campaign_root)
            except ValueError:
                pass
            else:
                raise ValueError("external trust artifact is inside campaign root")
        if _sha_file(manifest_path) != evidence_sha or _read_single_sha(trust_receipt_path) != evidence_sha:
            raise ValueError("evidence manifest external root mismatch")
        change = _read_json(change_record_path)
        if (
            change.get("schema_version") != 1
            or change.get("scope") != "new_nic_r0_external_change_record"
            or change.get("campaign_id") != campaign_id
            or change.get("trusted_evidence_manifest_sha256") != evidence_sha
            or change.get("trusted_helper_manifest_sha256") != helper_sha
            or change.get("trusted_arrival_manifest_sha256") != arrival_sha
            or change.get("approved") is not True
        ):
            raise ValueError("external change record does not bind all three roots")
        if _sha_file(helper_manifest_path) != helper_sha:
            raise ValueError("frozen helper manifest root mismatch")

        manifest = _read_json(manifest_path)
        if (
            manifest.get("schema_version") != 1
            or manifest.get("scope") != "new_nic_r0_artifact_manifest"
            or manifest.get("campaign_id") != campaign_id
        ):
            raise ValueError("artifact manifest envelope is invalid")
        artifacts = manifest.get("artifacts")
        if not isinstance(artifacts, list) or len(artifacts) != len(roles):
            raise ValueError("artifact manifest role cardinality is invalid")
        paths: Dict[str, Path] = {}
        hashes: Dict[str, str] = {}
        relative_paths: set[str] = set()
        for raw in artifacts:
            if not isinstance(raw, Mapping) or set(raw) != {"role", "path", "sha256"}:
                raise ValueError("artifact manifest entry fields are invalid")
            role, relative, declared = raw.get("role"), raw.get("path"), raw.get("sha256")
            if not isinstance(role, str) or role in paths or role not in roles:
                raise ValueError("artifact role is missing, duplicated, or unknown")
            if not isinstance(relative, str) or relative in relative_paths or not _is_sha(declared):
                raise ValueError("artifact path or SHA-256 is invalid")
            path = _resolve_manifest_member(campaign_root, relative)
            actual = _sha_file(path)
            if actual != declared:
                raise ValueError("artifact member SHA-256 mismatch")
            paths[role], hashes[role] = path, actual
            relative_paths.add(relative)
        if set(paths) != set(roles):
            raise ValueError("artifact manifest roles are not exact")
        for role, approved in approved_hashes.items():
            if hashes.get(role) != approved:
                raise ValueError("artifact {} is not independently approved".format(role))

        contract = _read_json(paths["contract"])
        if contract.get("required_manifest_roles") != roles:
            raise ValueError("campaign contract role list differs from profile")
        campaign = _read_json(paths["campaign"])
        if campaign.get("campaign_id") != campaign_id:
            raise ValueError("campaign artifact identity mismatch")
        if campaign.get("arrival_evidence_manifest_sha256") != arrival_sha:
            raise ValueError("campaign does not bind approved arrival root")
        if hashes["arrival_evidence_manifest"] != arrival_sha:
            raise ValueError("arrival evidence manifest root mismatch")

        arrival_lines = paths["arrival_evidence_manifest"].read_text(encoding="utf-8").splitlines()
        arrival_entries: Dict[str, str] = {}
        for line in arrival_lines:
            match = re.fullmatch(r"([0-9a-f]{64}) [ *](.+)", line)
            if match is None:
                raise ValueError("arrival manifest line is malformed")
            name = PurePosixPath(match.group(2)).name
            if name in arrival_entries:
                raise ValueError("arrival manifest basename is duplicated")
            arrival_entries[name] = match.group(1)
        if (
            arrival_entries.get("inventory.probes.json") != hashes["arrival_inventory"]
            or arrival_entries.get("preflight.probes.json") != hashes["arrival_preflight"]
        ):
            raise ValueError("arrival manifest does not bind copied arrival JSON")

        result = evaluate_r0_campaign(
            contract=contract,
            campaign=campaign,
            arrival_inventory=_read_json(paths["arrival_inventory"]),
            arrival_preflight=_read_json(paths["arrival_preflight"]),
            xdp_runs=[_read_json(paths["xdp_run_{}".format(i)]) for i in (1, 2, 3)],
            dpdk_runs=[_read_json(paths["dpdk_run_{}".format(i)]) for i in (1, 2, 3)],
            fallback_trials=[_read_json(paths["fallback_trial_{}".format(i)]) for i in (1, 2, 3)],
            restoration_before=_read_json(paths["restoration_before"]),
            restoration_after=_read_json(paths["restoration_after"]),
            producer_hashes=hashes,
            trusted_manifest_verified=True,
            trusted_manifest_sha256=evidence_sha,
        )
        saved_audit = _read_json(audit_path)
        if _canonical(result) != _canonical(saved_audit):
            raise ValueError("saved R0 audit differs from independent recomputation")
        state = _read_json(state_path)
        if (
            state.get("schema_version") != 1
            or state.get("scope") != "new_nic_r0_runner_state"
            or state.get("status") != "r0_qualified"
            or state.get("phase") != "COMPOSE"
            or state.get("mutations_performed") is not True
        ):
            raise ValueError("runner state is not a completed COMPOSE")
        if (campaign_root / "RECOVERY_REQUIRED").exists():
            raise ValueError("campaign has a recovery-required marker")
        restored = (result.get("restoration") or {}).get("qualified") is True
        if not (
            result.get("status") == "r0_qualified"
            and result.get("errors") == []
            and result.get("xdp_primary_repeats_qualified") == 3
            and result.get("dpdk_fallback_repeats_qualified") == 3
            and result.get("fallback_trials_qualified") == 3
            and restored
            and result.get("r0_qualified") is True
            and result.get("mutations_performed") is True
            and result.get("production_qualified") is False
            and result.get("final_pareto_ingestion_allowed") is False
        ):
            raise ValueError("recomputed campaign did not satisfy the full R0 gate")

        xdp_runs = [_read_json(paths["xdp_run_{}".format(i)]) for i in (1, 2, 3)]
        dpdk_runs = [_read_json(paths["dpdk_run_{}".format(i)]) for i in (1, 2, 3)]
        fallback = [_read_json(paths["fallback_trial_{}".format(i)]) for i in (1, 2, 3)]
        run_identities = [hashes["xdp_run_{}".format(i)] for i in (1, 2, 3)] + [
            hashes["dpdk_run_{}".format(i)] for i in (1, 2, 3)
        ]
        generator_identities = [
            canonical_sha256(run["generator"]) for run in xdp_runs + dpdk_runs
        ] + [canonical_sha256(trial["generator_transition"]) for trial in fallback]
        if len(run_identities) != len(set(run_identities)) or len(generator_identities) != len(set(generator_identities)):
            raise ValueError("campaign run or generator receipt identities are not independent")
        inventory = _read_json(paths["arrival_inventory"])
        candidate_ports = inventory.get("candidate_ports")
        if not isinstance(candidate_ports, list) or not candidate_ports:
            raise ValueError("arrival candidate ports are missing")
        hardware_identity = canonical_sha256(candidate_ports)
        identity = {
            "campaign_id": campaign_id,
            "run_bundle_identities": run_identities,
            "generator_run_identities": generator_identities,
            "hardware_identity_sha256": [hardware_identity],
            "backends": [mapping["unified_primary"], mapping["unified_fallback"]],
            "contracts": [hashes["contract"]],
            "primary_backend": mapping["unified_primary"],
            "fallback_backend": mapping["unified_fallback"],
            "artifact_manifest_sha256": evidence_sha,
        }
        evidence_hashes.update(
            {
                "new_nic_r0_campaign.artifact_manifest": evidence_sha,
                "new_nic_r0_campaign.r0_audit": _sha_file(audit_path),
                "new_nic_r0_campaign.runner_state": _sha_file(state_path),
                "new_nic_r0_campaign.helper_manifest": helper_sha,
                "new_nic_r0_campaign.arrival_manifest": arrival_sha,
                "new_nic_r0_campaign.change_record": _sha_file(change_record_path),
                **{"new_nic_r0_campaign.role.{}".format(k): v for k, v in hashes.items()},
            }
        )
        return True, True, identity
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, TypeError, KeyError, ArithmeticError) as exc:
        errors.append("{}.{}:{}".format(prefix, type(exc).__name__, exc))
        return False, False, empty_identity
