#!/usr/bin/env python3
"""Compose a fail-closed new-NIC R0 campaign audit from frozen artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import stat
import sys
import tempfile
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import hft_mgbs.new_nic_r0 as evaluator_module
from hft_mgbs.new_nic_r0 import (
    evaluate_r0_campaign,
    exit_code_for_status,
    hardware_pending_result,
)


DEFAULT_CONTRACT = ROOT / "configs" / "new_nic_r0_campaign_contract_v1.json"
SHA256_LENGTH = 64


def reject_duplicate_keys(pairs: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: {}".format(key))
        result[key] = value
    return result


def reject_nonfinite(value: str) -> None:
    raise ValueError("non-finite JSON number: {}".format(value))


def read_json(path: Path) -> Dict[str, Any]:
    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_keys,
        parse_constant=reject_nonfinite,
    )
    if not isinstance(value, dict):
        raise ValueError("{} must contain a JSON object".format(path))
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == SHA256_LENGTH
        and all(character in "0123456789abcdef" for character in value)
    )


def write_json_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(
        value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False
    ) + "\n"
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=str(path.parent),
        prefix=path.name + ".",
        suffix=".tmp",
        delete=False,
    )
    temporary = Path(handle.name)
    try:
        with handle:
            handle.write(rendered)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)
    except BaseException:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise


def safe_artifact_path(root: Path, raw: Any, role: str) -> Path:
    if not isinstance(raw, str) or not raw or "\x00" in raw:
        raise ValueError("artifact {} has invalid path".format(role))
    relative = Path(raw)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("artifact {} path escapes campaign root".format(role))
    root_resolved = root.resolve(strict=True)
    candidate = root / relative
    current = root_resolved
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("artifact {} path contains a symlink".format(role))
    resolved = candidate.resolve(strict=True)
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError("artifact {} path escapes campaign root".format(role)) from exc
    mode = resolved.stat().st_mode
    if not stat.S_ISREG(mode):
        raise ValueError("artifact {} is not a regular file".format(role))
    if resolved.stat().st_size > 64 * 1024 * 1024:
        raise ValueError("artifact {} exceeds 64 MiB evidence limit".format(role))
    return resolved


def verify_manifest(
    root: Path,
    manifest_path: Path,
    trusted_sha256: str,
) -> Tuple[Dict[str, Path], Dict[str, str], Dict[str, Any]]:
    if not is_sha256(trusted_sha256):
        raise ValueError("trusted manifest SHA-256 must be lowercase 64-hex")
    if manifest_path.is_symlink() or sha256_file(manifest_path) != trusted_sha256:
        raise ValueError("artifact manifest does not match external trusted SHA-256")
    manifest = read_json(manifest_path)
    if (
        manifest.get("schema_version") != 1
        or manifest.get("scope") != "new_nic_r0_artifact_manifest"
    ):
        raise ValueError("artifact manifest envelope is invalid")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("artifact manifest artifacts must be non-empty")
    paths: Dict[str, Path] = {}
    hashes: Dict[str, str] = {}
    seen_relative = set()
    for index, raw in enumerate(artifacts):
        if not isinstance(raw, Mapping):
            raise ValueError("artifact {} is not an object".format(index))
        role = raw.get("role")
        relative = raw.get("path")
        expected = raw.get("sha256")
        if not isinstance(role, str) or not role or role in paths:
            raise ValueError("artifact role is missing or duplicated")
        if not isinstance(relative, str) or relative in seen_relative:
            raise ValueError("artifact path is missing or duplicated")
        if not is_sha256(expected):
            raise ValueError("artifact {} SHA-256 is invalid".format(role))
        path = safe_artifact_path(root, relative, role)
        actual = sha256_file(path)
        if actual != expected:
            raise ValueError("artifact {} SHA-256 mismatch".format(role))
        paths[role] = path
        hashes[role] = actual
        seen_relative.add(relative)
    contract = read_json(paths.get("contract", Path("/__missing_contract__")))
    required = contract.get("required_manifest_roles")
    if not isinstance(required, list) or set(required) - set(paths):
        missing = sorted(set(required or []) - set(paths))
        raise ValueError("artifact manifest is missing roles: {}".format(",".join(missing)))
    if sha256_file(Path(__file__).resolve()) != hashes.get("composer"):
        raise ValueError("running composer does not match frozen composer role")
    if sha256_file(Path(evaluator_module.__file__).resolve()) != hashes.get("evaluator"):
        raise ValueError("imported evaluator does not match frozen evaluator role")
    return paths, hashes, manifest


def verify_arrival_manifest_binding(
    path: Path, inventory_sha256: str, preflight_sha256: str
) -> None:
    """Bind copied arrival JSON bytes to the prior arrival checksum list."""
    expected = {
        "inventory.probes.json": inventory_sha256,
        "preflight.probes.json": preflight_sha256,
    }
    observed: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64}) [ *](.+)", line)
        if match is None:
            raise ValueError("arrival evidence manifest contains a malformed line")
        relative = Path(match.group(2))
        basename = relative.name
        if basename in expected:
            if basename in observed or relative.is_absolute() or ".." in relative.parts:
                raise ValueError("arrival evidence manifest path is unsafe or duplicated")
            observed[basename] = match.group(1)
    if observed != expected:
        raise ValueError("arrival inventory/preflight bytes are not bound by arrival manifest")


def invalid_result(status: str, error: Exception) -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "scope": "new_high_speed_nic_r0_campaign_audit",
        "status": status,
        "errors": [str(error)],
        "trusted_evidence_manifest_verified": False,
        "xdp_primary_repeats_qualified": 0,
        "dpdk_fallback_repeats_qualified": 0,
        "fallback_trials_qualified": 0,
        "r0_qualified": False,
        "production_qualified": False,
        "final_pareto_ingestion_allowed": False,
        "mutations_performed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Recompute the frozen new-NIC R0 campaign from hash-bound raw receipts"
    )
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--hardware-pending", action="store_true")
    parser.add_argument("--artifact-root", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--trusted-manifest-sha256")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.hardware_pending:
        try:
            result = hardware_pending_result(read_json(args.contract))
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            result = invalid_result("invalid_contract", exc)
        write_json_atomic(args.output, result)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return exit_code_for_status(str(result["status"]))

    if args.artifact_root is None or args.manifest is None:
        result = invalid_result(
            "evidence_pending",
            ValueError("formal mode requires --artifact-root, --manifest and trusted SHA-256"),
        )
        write_json_atomic(args.output, result)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 21

    try:
        paths, hashes, manifest = verify_manifest(
            args.artifact_root,
            args.manifest,
            str(args.trusted_manifest_sha256 or ""),
        )
        contract = read_json(paths["contract"])
        campaign = read_json(paths["campaign"])
        verify_arrival_manifest_binding(
            paths["arrival_evidence_manifest"],
            hashes["arrival_inventory"],
            hashes["arrival_preflight"],
        )
        if manifest.get("campaign_id") != campaign.get("campaign_id"):
            raise ValueError("manifest campaign_id does not match campaign")
        result = evaluate_r0_campaign(
            contract=contract,
            campaign=campaign,
            arrival_inventory=read_json(paths["arrival_inventory"]),
            arrival_preflight=read_json(paths["arrival_preflight"]),
            xdp_runs=[read_json(paths["xdp_run_{}".format(index)]) for index in (1, 2, 3)],
            dpdk_runs=[read_json(paths["dpdk_run_{}".format(index)]) for index in (1, 2, 3)],
            fallback_trials=[
                read_json(paths["fallback_trial_{}".format(index)])
                for index in (1, 2, 3)
            ],
            restoration_before=read_json(paths["restoration_before"]),
            restoration_after=read_json(paths["restoration_after"]),
            producer_hashes=hashes,
            trusted_manifest_verified=True,
            trusted_manifest_sha256=args.trusted_manifest_sha256,
        )
    except (OSError, ValueError, TypeError, KeyError, ArithmeticError, json.JSONDecodeError) as exc:
        result = invalid_result("provenance_rejected", exc)
    write_json_atomic(args.output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return exit_code_for_status(str(result["status"]))


if __name__ == "__main__":
    raise SystemExit(main())
