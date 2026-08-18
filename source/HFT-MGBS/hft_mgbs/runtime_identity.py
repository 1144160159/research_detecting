"""Fail-closed validation for the read-only split-runtime identity receipt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def _sha(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def _pid(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_runtime_identity(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_strict_object)
    if not isinstance(value, dict):
        raise ValueError("runtime identity receipt must be a JSON object")
    return value


def validate_runtime_identity(receipt: dict[str, Any]) -> dict[str, Any]:
    """Recompute identity status; no field in the receipt is trusted by itself."""

    errors: list[str] = []

    def obj(name: str) -> dict[str, Any]:
        value = receipt.get(name)
        if not isinstance(value, dict):
            errors.append(f"{name}.missing")
            return {}
        return value

    if receipt.get("schema_version") != 1:
        errors.append("schema_version")
    if receipt.get("scope") != "hft_mgbs_split_runtime_identity":
        errors.append("scope")
    if receipt.get("read_only") is not True:
        errors.append("read_only")

    manifest = obj("runtime_manifest")
    process = obj("gpu_process")
    listener = obj("gpu_listener_50051")
    health = obj("gpu_localhost_health")
    reachability = obj("physical_to_gpu_50051")
    reverse = obj("physical_reverse_50052")

    for field in ("path",):
        if not _nonempty(manifest.get(field)):
            errors.append(f"runtime_manifest.{field}")
    for field in ("expected_sha256", "actual_sha256"):
        if not _sha(manifest.get(field)):
            errors.append(f"runtime_manifest.{field}")
    if _sha(manifest.get("expected_sha256")) and _sha(manifest.get("actual_sha256")):
        if manifest["expected_sha256"] != manifest["actual_sha256"]:
            errors.append("runtime_manifest.sha256_mismatch")
    if not _pid(manifest.get("declared_pid")):
        errors.append("runtime_manifest.declared_pid")

    if not _pid(process.get("pid")):
        errors.append("gpu_process.pid")
    if process.get("alive") is not True:
        errors.append("gpu_process.alive")
    for field in ("cmdline", "exe", "cwd"):
        if not _nonempty(process.get(field)):
            errors.append(f"gpu_process.{field}")

    if listener.get("endpoint") != "0.0.0.0:50051":
        errors.append("gpu_listener_50051.endpoint")
    if not _pid(listener.get("owner_pid")):
        errors.append("gpu_listener_50051.owner_pid")
    if _pid(process.get("pid")) and _pid(listener.get("owner_pid")):
        if listener["owner_pid"] != process["pid"]:
            errors.append("gpu_listener_50051.owner_process_mismatch")
    if _pid(manifest.get("declared_pid")) and _pid(listener.get("owner_pid")):
        if manifest["declared_pid"] != listener["owner_pid"]:
            errors.append("runtime_manifest.listener_pid_mismatch")

    failures = health.get("failures")
    if health.get("ok") is not True:
        errors.append("gpu_localhost_health.ok")
    if not isinstance(failures, list) or failures:
        errors.append("gpu_localhost_health.failures")
    if reachability.get("reachable") is not True:
        errors.append("physical_to_gpu_50051.reachable")
    if reverse.get("listener") is not True:
        errors.append("physical_reverse_50052.listener")
    if reverse.get("established") is not True:
        errors.append("physical_reverse_50052.established")

    computed = not errors
    if receipt.get("verified") is not computed:
        errors.append("verified.claim_mismatch")
        computed = False
    return {"verified": computed, "errors": errors}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
