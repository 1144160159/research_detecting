"""Hash-bound state-snapshot executor for three-tier capture failover."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from hft_mgbs.capture_runtime_decision import SHA256_RE
from hft_mgbs.capture_runtime_executor import (
    RuntimeExecutionError,
    _canonical,
    _json_bytes,
    _safe_create,
    _sha,
    _stable,
    _validate_operation,
)
from hft_mgbs.capture_runtime_failover import (
    BACKENDS,
    NO_BACKEND,
    RECEIPT_SCOPE as DECISION_RECEIPT_SCOPE,
    evaluate_failover_decision,
)


PLAN_SCOPE = "hft_mgbs_capture_runtime_failover_execution_plan_v2"
EXECUTION_RECEIPT_SCOPE = "hft_mgbs_capture_runtime_failover_execution_receipt_v2"
TOPOLOGIES = frozenset(
    (
        "new_nic_with_dedicated_bcm57810_fallback",
        "dedicated_backend_adapters",
    )
)
OPERATIONS = frozenset(
    (
        "snapshot",
        "health_native_af_xdp_zerocopy",
        "health_dpdk",
        "health_current_tpacket_v3_bcm57810",
        "start_native_af_xdp_zerocopy",
        "start_dpdk",
        "start_current_tpacket_v3_bcm57810",
        "stop_native_af_xdp_zerocopy",
        "stop_dpdk",
        "stop_current_tpacket_v3_bcm57810",
        "rollback",
    )
)


def validate_failover_execution_plan(plan: Mapping[str, Any]) -> None:
    if set(plan) != {"schema_version", "scope", "policy_id", "topology", "operations"}:
        raise RuntimeExecutionError("failover execution plan envelope is not exact")
    if plan.get("schema_version") != 2 or plan.get("scope") != PLAN_SCOPE:
        raise RuntimeExecutionError("failover execution plan identity is invalid")
    if plan.get("topology") not in TOPOLOGIES:
        raise RuntimeExecutionError("failover execution requires dedicated adapters")
    operations = plan.get("operations")
    if not isinstance(operations, Mapping) or set(operations) != OPERATIONS:
        raise RuntimeExecutionError("failover execution plan operations are not exact")
    for name, operation in operations.items():
        _validate_operation(name, operation)


def _expand(value: str, variables: Mapping[str, str]) -> str:
    result = value
    for name, replacement in variables.items():
        result = result.replace("{" + name + "}", replacement)
    if "{" in result or "}" in result:
        raise RuntimeExecutionError("unresolved operation placeholder")
    return result


def _run(
    plan: Mapping[str, Any], name: str, work_dir: Path, sequence: int, evidence: bool
) -> Optional[Dict[str, Any]]:
    operation = plan["operations"][name]
    output = work_dir / "{:02d}-{}.json".format(sequence, name)
    variables = {"output": str(output), "work_dir": str(work_dir)}
    argv = [_expand(item, variables) for item in operation["argv"]]
    identities = [(Path(argv[0]), operation["executable_sha256"])] + [
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
                name,
                completed.returncode,
                completed.stderr.decode("utf-8", errors="replace")[-2048:],
            )
        )
    for path, digest in identities:
        if _sha(_stable(path, 256 * 1024 * 1024)) != digest:
            raise RuntimeExecutionError("operation identity drifted after {}: {}".format(name, path))
    if evidence:
        if not output.is_file() or output.is_symlink():
            raise RuntimeExecutionError("operation {} omitted its evidence".format(name))
        return _json_bytes(_stable(output), name)
    if output.exists() or output.is_symlink():
        raise RuntimeExecutionError("mutation operation wrote an unexpected evidence file")
    return None


def _replay(
    policy: Mapping[str, Any], observation: Mapping[str, Any], receipt: Mapping[str, Any]
) -> Mapping[str, Any]:
    if receipt.get("receipt_scope") != DECISION_RECEIPT_SCOPE:
        raise RuntimeExecutionError("failover decision receipt scope is invalid")
    when = receipt.get("decision_at_utc")
    if not isinstance(when, str):
        raise RuntimeExecutionError("failover decision timestamp is missing")
    from datetime import datetime

    now = datetime.fromisoformat(when.replace("Z", "+00:00"))
    recomputed = evaluate_failover_decision(policy, observation, now=now)
    for key, value in recomputed.items():
        if receipt.get(key) != value:
            raise RuntimeExecutionError("failover decision receipt differs from replay: " + key)
    return recomputed


def execute_failover_transition(
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
    if authorization != "I_AUTHORIZE_CAPTURE_RUNTIME_FAILOVER_V2":
        raise RuntimeExecutionError("exact failover execution authorization is required")
    if SHA256_RE.fullmatch(trusted_plan_sha256) is None:
        raise RuntimeExecutionError("trusted failover execution-plan SHA-256 is invalid")
    policy_raw = _stable(policy_path)
    observation_raw = _stable(observation_path)
    decision_raw = _stable(decision_receipt_path)
    plan_raw = _stable(execution_plan_path)
    if _sha(plan_raw) != trusted_plan_sha256:
        raise RuntimeExecutionError("failover execution plan differs from its trust root")
    policy = _json_bytes(policy_raw, "policy")
    observation = _json_bytes(observation_raw, "observation")
    receipt = _json_bytes(decision_raw, "decision receipt")
    plan = _json_bytes(plan_raw, "execution plan")
    validate_failover_execution_plan(plan)
    if plan.get("policy_id") != policy.get("policy_id"):
        raise RuntimeExecutionError("failover plan policy identity mismatch")
    if receipt.get("runtime_policy_sha256") != _sha(policy_raw) \
      or receipt.get("observation_sha256") != _sha(observation_raw):
        raise RuntimeExecutionError("failover decision raw identities drifted")
    decision = _replay(policy, observation, receipt)

    work_dir = work_dir.absolute()
    if work_dir.exists() or work_dir.is_symlink():
        raise RuntimeExecutionError("failover work directory must be new")
    work_dir.mkdir(parents=False, mode=0o700)
    action = str(decision["action"])
    selected = decision.get("selected_backend")
    before = after = None
    sequence = 0
    started = False
    rollback_attempted = False
    rollback_succeeded = False
    error: Optional[str] = None
    outcome = "decision_requires_no_automatic_mutation"
    try:
        if action.startswith("switch_to_"):
            if decision.get("transition_permitted") is not True or selected not in BACKENDS:
                raise RuntimeExecutionError("transition is not permitted by the replayed decision")
            sequence += 1
            before = _run(plan, "snapshot", work_dir, sequence, True)
            source = decision.get("current_backend")
            if before.get("active_backend") != source:
                raise RuntimeExecutionError("pre-switch snapshot differs from decision state")
            sequence += 1
            health = _run(plan, "health_" + selected, work_dir, sequence, True)
            if health.get("backend") != selected or health.get("healthy") is not True:
                raise RuntimeExecutionError("target backend preflight failed")
            sequence += 1
            _run(plan, "start_" + selected, work_dir, sequence, False)
            started = True
            sequence += 1
            health = _run(plan, "health_" + selected, work_dir, sequence, True)
            if health.get("backend") != selected or health.get("healthy") is not True:
                raise RuntimeExecutionError("target backend did not become healthy")
            if source != NO_BACKEND:
                sequence += 1
                _run(plan, "stop_" + str(source), work_dir, sequence, False)
            sequence += 1
            after = _run(plan, "snapshot", work_dir, sequence, True)
            if after.get("active_backend") != selected:
                raise RuntimeExecutionError("post-switch snapshot does not prove target ownership")
            outcome = "switched_to_" + selected
        elif action.startswith(("keep_", "prepare_", "request_maintenance_")) \
          or action == "stop_fail_closed":
            outcome = "decision_requires_no_automatic_mutation"
        else:
            raise RuntimeExecutionError("unsupported failover action: " + action)
    except BaseException as caught:
        error = str(caught)
        if started:
            rollback_attempted = True
            try:
                sequence += 1
                _run(plan, "rollback", work_dir, sequence, False)
                sequence += 1
                restored = _run(plan, "snapshot", work_dir, sequence, True)
                rollback_succeeded = before is not None and restored.get("active_backend") == before.get("active_backend")
            except BaseException:
                rollback_succeeded = False
        outcome = "execution_failed_rolled_back" if rollback_succeeded else "execution_failed_recovery_required"

    result = {
        "schema_version": 2,
        "scope": EXECUTION_RECEIPT_SCOPE,
        "action": action,
        "current_backend": decision.get("current_backend"),
        "selected_backend": selected,
        "degraded_mode": decision.get("degraded_mode"),
        "production_sla_qualified": False,
        "transition_permitted": decision.get("transition_permitted"),
        "outcome": outcome,
        "mutations_performed": started,
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
    if error is not None:
        raise RuntimeExecutionError(error)
    return result
