"""State-snapshotting executor for an approved XDP-to-DPDK runtime decision."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

from hft_mgbs.capture_runtime_decision import evaluate_runtime_decision


SHA_RE = re.compile(r"^[0-9a-f]{64}$")
PLAN_SCOPE = "hft_mgbs_capture_runtime_execution_plan_v1"
RECEIPT_SCOPE = "hft_mgbs_capture_runtime_execution_receipt_v1"
OPERATIONS = frozenset(
    ("snapshot", "health_xdp", "health_dpdk", "start_dpdk", "stop_xdp", "rollback")
)


class RuntimeExecutionError(RuntimeError):
    pass


def _pairs(items: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
    value: Dict[str, Any] = {}
    for key, item in items:
        if key in value:
            raise RuntimeExecutionError("duplicate JSON key: " + key)
        value[key] = item
    return value


def _nonfinite(value: str) -> None:
    raise RuntimeExecutionError("non-finite JSON: " + value)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _stable(path: Path, maximum: int = 128 * 1024 * 1024) -> bytes:
    path = path.absolute()
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        if current.is_symlink():
            raise RuntimeExecutionError("symlink component rejected: {}".format(path))
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(path), flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
            raise RuntimeExecutionError("regular bounded file required: {}".format(path))
        raw = bytearray()
        while len(raw) < before.st_size:
            block = os.read(descriptor, min(1024 * 1024, before.st_size - len(raw)))
            if not block:
                raise RuntimeExecutionError("short read: {}".format(path))
            raw.extend(block)
        if os.read(descriptor, 1):
            raise RuntimeExecutionError("file grew during read: {}".format(path))
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    identity = lambda item: (
        item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns, item.st_ctime_ns
    )
    if identity(before) != identity(after):
        raise RuntimeExecutionError("file changed during read: {}".format(path))
    current_stat = path.stat()
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
        current_stat.st_dev, current_stat.st_ino, current_stat.st_size, current_stat.st_mtime_ns
    ):
        raise RuntimeExecutionError("file was replaced during read: {}".format(path))
    return bytes(raw)


def _json_bytes(raw: bytes, label: str) -> Dict[str, Any]:
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_nonfinite)
    if not isinstance(value, dict):
        raise RuntimeExecutionError(label + " must be a JSON object")
    return value


def _canonical(value: Mapping[str, Any]) -> str:
    return _sha(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"))


def _safe_create(path: Path, value: Mapping[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise RuntimeExecutionError("execution receipt output already exists")
    parent = path.parent.absolute()
    current = Path(parent.anchor)
    for part in parent.parts[1:]:
        current = current / part
        if current.is_symlink():
            raise RuntimeExecutionError("execution receipt parent contains a symlink")
    parent = parent.resolve(strict=True)
    raw = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    descriptor, temporary_raw = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(parent))
    temporary = Path(temporary_raw)
    created = False
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists() or path.is_symlink():
            raise RuntimeExecutionError("execution receipt output raced")
        os.link(str(temporary), str(path))
        created = True
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
    if created:
        os.chmod(str(path), 0o400 if os.name != "nt" else 0o600)


def _validate_operation(name: str, raw: Any) -> Mapping[str, Any]:
    if not isinstance(raw, Mapping) or set(raw) != {
        "argv", "executable_sha256", "bound_files", "timeout_seconds"
    }:
        raise RuntimeExecutionError("operation {} is not exact".format(name))
    argv = raw.get("argv")
    if not isinstance(argv, list) or not argv or any(not isinstance(item, str) for item in argv):
        raise RuntimeExecutionError("operation {} argv is invalid".format(name))
    if not Path(argv[0]).is_absolute() or not SHA_RE.fullmatch(str(raw.get("executable_sha256", ""))):
        raise RuntimeExecutionError("operation {} executable identity is invalid".format(name))
    timeout = raw.get("timeout_seconds")
    if type(timeout) is not int or timeout < 1 or timeout > 300:
        raise RuntimeExecutionError("operation {} timeout is invalid".format(name))
    files = raw.get("bound_files")
    if not isinstance(files, list):
        raise RuntimeExecutionError("operation {} bound_files is invalid".format(name))
    for item in files:
        if not isinstance(item, Mapping) or set(item) != {"path", "sha256"} \
          or not Path(str(item.get("path"))).is_absolute() \
          or not SHA_RE.fullmatch(str(item.get("sha256", ""))):
            raise RuntimeExecutionError("operation {} bound file is invalid".format(name))
    return raw


def validate_execution_plan(plan: Mapping[str, Any]) -> None:
    if set(plan) != {"schema_version", "scope", "policy_id", "topology", "operations"} \
      or plan.get("schema_version") != 1 or plan.get("scope") != PLAN_SCOPE:
        raise RuntimeExecutionError("execution plan envelope is not exact")
    if plan.get("topology") != "dedicated_standby_adapter":
        raise RuntimeExecutionError("automatic execution requires a dedicated standby adapter")
    operations = plan.get("operations")
    if not isinstance(operations, Mapping) or set(operations) != OPERATIONS:
        raise RuntimeExecutionError("execution plan operations are not exact")
    for name, operation in operations.items():
        _validate_operation(name, operation)


def _expand(value: str, variables: Mapping[str, str]) -> str:
    output = value
    for name, replacement in variables.items():
        output = output.replace("{" + name + "}", replacement)
    if re.search(r"\{[A-Za-z0-9_]+\}", output):
        raise RuntimeExecutionError("unresolved operation placeholder")
    return output


def _run_operation(
    plan: Mapping[str, Any], name: str, work_dir: Path, sequence: int
) -> Optional[Dict[str, Any]]:
    operation = plan["operations"][name]
    output = work_dir / "{:02d}-{}.json".format(sequence, name)
    if output.exists() or output.is_symlink():
        raise RuntimeExecutionError("operation output already exists")
    variables = {"output": str(output), "work_dir": str(work_dir)}
    argv = [_expand(item, variables) for item in operation["argv"]]
    executable = Path(argv[0])
    identities = [(executable, operation["executable_sha256"])] + [
        (Path(item["path"]), item["sha256"]) for item in operation["bound_files"]
    ]
    for path, digest in identities:
        if _sha(_stable(path, 256 * 1024 * 1024)) != digest:
            raise RuntimeExecutionError("operation identity drifted before {}: {}".format(name, path))
    completed = subprocess.run(
        argv,
        cwd=str(work_dir),
        env={
            "PATH": os.environ.get("PATH", ""),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            **{key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR") if key in os.environ},
        },
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=operation["timeout_seconds"],
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeExecutionError(
            "operation {} failed rc={}: {}".format(
                name, completed.returncode, completed.stderr.decode("utf-8", errors="replace")[-2048:]
            )
        )
    for path, digest in identities:
        if _sha(_stable(path, 256 * 1024 * 1024)) != digest:
            raise RuntimeExecutionError("operation identity drifted after {}: {}".format(name, path))
    if name in {"snapshot", "health_xdp", "health_dpdk"}:
        if not output.is_file() or output.is_symlink():
            raise RuntimeExecutionError("operation {} omitted its evidence output".format(name))
        return _json_bytes(_stable(output), name)
    if output.exists() or output.is_symlink():
        raise RuntimeExecutionError("mutation operation unexpectedly wrote an evidence output")
    return None


def _verified_decision(
    policy: Mapping[str, Any], observation: Mapping[str, Any], receipt: Mapping[str, Any]
) -> Mapping[str, Any]:
    if receipt.get("receipt_scope") != "hft_mgbs_capture_runtime_decision_receipt_v1":
        raise RuntimeExecutionError("runtime decision receipt scope is invalid")
    when = receipt.get("decision_at_utc")
    if not isinstance(when, str):
        raise RuntimeExecutionError("runtime decision timestamp is missing")
    from datetime import datetime

    parsed = datetime.fromisoformat(when.replace("Z", "+00:00"))
    recomputed = evaluate_runtime_decision(policy, observation, now=parsed)
    for key, value in recomputed.items():
        if receipt.get(key) != value:
            raise RuntimeExecutionError("runtime decision receipt differs from replay: " + key)
    return recomputed


def execute_runtime_decision(
    *,
    policy_path: Path,
    observation_path: Path,
    decision_receipt_path: Path,
    execution_plan_path: Path,
    trusted_plan_sha256: str,
    authorization: str,
    work_dir: Path,
    output_path: Path,
) -> Dict[str, Any]:
    if authorization != "I_AUTHORIZE_XDP_DPDK_RUNTIME_EXECUTION":
        raise RuntimeExecutionError("exact runtime execution authorization is required")
    if not SHA_RE.fullmatch(trusted_plan_sha256):
        raise RuntimeExecutionError("trusted execution-plan SHA-256 is invalid")
    policy_raw, observation_raw, decision_raw, plan_raw = (
        _stable(policy_path),
        _stable(observation_path),
        _stable(decision_receipt_path),
        _stable(execution_plan_path),
    )
    if _sha(plan_raw) != trusted_plan_sha256:
        raise RuntimeExecutionError("execution plan differs from its external trust root")
    policy = _json_bytes(policy_raw, "policy")
    observation = _json_bytes(observation_raw, "observation")
    decision_receipt = _json_bytes(decision_raw, "decision receipt")
    plan = _json_bytes(plan_raw, "execution plan")
    validate_execution_plan(plan)
    if plan.get("policy_id") != policy.get("policy_id"):
        raise RuntimeExecutionError("execution plan policy identity mismatch")
    if decision_receipt.get("runtime_policy_sha256") != _sha(policy_raw) \
      or decision_receipt.get("observation_sha256") != _sha(observation_raw):
        raise RuntimeExecutionError("decision receipt raw-file identities drifted")
    decision = _verified_decision(policy, observation, decision_receipt)
    work_dir = work_dir.absolute()
    if work_dir.exists() or work_dir.is_symlink():
        raise RuntimeExecutionError("runtime work directory must be new")
    work_dir.mkdir(parents=False, mode=0o700)
    action = decision["action"]
    sequence = 0
    before = after = None
    executed = False
    rollback_attempted = False
    rollback_succeeded = False
    outcome = "decision_requires_no_mutation"
    error: Optional[str] = None
    try:
        if action == "switch_to_dpdk":
            if decision.get("transition_permitted") is not True \
              or decision.get("selected_backend") != "dpdk":
                raise RuntimeExecutionError("DPDK switch is not authorized by the replayed decision")
            sequence += 1
            before = _run_operation(plan, "snapshot", work_dir, sequence)
            sequence += 1
            standby = _run_operation(plan, "health_dpdk", work_dir, sequence)
            if standby.get("healthy") is not True or standby.get("backend") != "dpdk":
                raise RuntimeExecutionError("DPDK standby health gate failed")
            sequence += 1
            _run_operation(plan, "start_dpdk", work_dir, sequence)
            executed = True
            sequence += 1
            started = _run_operation(plan, "health_dpdk", work_dir, sequence)
            if started.get("healthy") is not True or started.get("backend") != "dpdk":
                raise RuntimeExecutionError("DPDK did not become healthy")
            sequence += 1
            _run_operation(plan, "stop_xdp", work_dir, sequence)
            sequence += 1
            after = _run_operation(plan, "snapshot", work_dir, sequence)
            if after.get("active_backend") != "dpdk":
                raise RuntimeExecutionError("post-switch snapshot does not prove DPDK ownership")
            outcome = "switched_to_dpdk"
        elif action in {
            "keep_xdp", "keep_dpdk", "prepare_dpdk_fallback", "prepare_xdp_primary",
            "request_maintenance_dpdk_fallback", "stop_fail_closed",
        }:
            outcome = "decision_requires_no_automatic_mutation"
        else:
            raise RuntimeExecutionError("unsupported runtime action: " + str(action))
    except BaseException as caught:
        error = str(caught)
        if executed:
            rollback_attempted = True
            try:
                sequence += 1
                _run_operation(plan, "rollback", work_dir, sequence)
                sequence += 1
                health = _run_operation(plan, "health_xdp", work_dir, sequence)
                rollback_succeeded = health.get("healthy") is True and health.get("backend") == "native_af_xdp_zerocopy"
            except BaseException:
                rollback_succeeded = False
        outcome = "execution_failed_rolled_back" if rollback_succeeded else "execution_failed_recovery_required"
    result = {
        "schema_version": 1,
        "scope": RECEIPT_SCOPE,
        "action": action,
        "selected_backend": decision.get("selected_backend"),
        "transition_permitted": decision.get("transition_permitted"),
        "outcome": outcome,
        "mutations_performed": executed,
        "rollback_attempted": rollback_attempted,
        "rollback_succeeded": rollback_succeeded,
        "recovery_required": outcome == "execution_failed_recovery_required",
        "error": error,
        "runtime_policy_sha256": _sha(policy_raw),
        "observation_sha256": _sha(observation_raw),
        "decision_receipt_sha256": _sha(decision_raw),
        "execution_plan_sha256": _sha(plan_raw),
        "before_snapshot": before,
        "after_snapshot": after,
        "release_qualification": False,
        "final_pareto_ingestion_allowed": False,
    }
    result["receipt_sha256"] = _canonical(result)
    _safe_create(output_path, result)
    if result["recovery_required"]:
        raise RuntimeExecutionError("runtime transition failed and recovery is required")
    if error is not None:
        raise RuntimeExecutionError(error)
    return result
