from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def canonical_hash(payload: dict[str, Any]) -> str:
    body = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def verify_canonical(payload: dict[str, Any], label: str) -> None:
    declared = payload.get("manifest_sha256")
    body = dict(payload)
    body.pop("manifest_sha256", None)
    if not isinstance(declared, str) or canonical_hash(body) != declared:
        raise ValueError(f"{label} canonical mismatch")


def atomic_write(path: Path, payload: dict[str, Any]) -> None:
    payload["manifest_sha256"] = canonical_hash(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def process_command(pid: int) -> list[str]:
    raw = Path(f"/proc/{pid}/cmdline").read_bytes()
    return [
        value.decode("utf-8")
        for value in raw.split(b"\0")
        if value
    ]


def process_state(pid: int) -> Optional[str]:
    try:
        fields = Path(f"/proc/{pid}/stat").read_text(
            encoding="utf-8"
        ).split()
    except FileNotFoundError:
        return None
    return fields[2] if len(fields) >= 3 else None


def process_group_members(group_id: int) -> list[int]:
    members = []
    for stat_path in Path("/proc").glob("[0-9]*/stat"):
        try:
            fields = stat_path.read_text(encoding="ascii").split()
            pid = int(fields[0])
            process_group = int(fields[4])
        except (OSError, ValueError, IndexError):
            continue
        if process_group == group_id and pid != group_id:
            members.append(pid)
    return sorted(members)


def replace_workers(command: list[str], workers: int) -> list[str]:
    updated = list(command)
    if "--workers" in updated:
        index = updated.index("--workers")
        if index + 1 >= len(updated):
            raise ValueError("--workers has no value")
        updated[index + 1] = str(workers)
    else:
        updated.extend(["--workers", str(workers)])
    return updated


def capture_dir_from_command(command: list[str]) -> Path:
    try:
        index = command.index("--capture-dir")
    except ValueError as exc:
        raise ValueError("child command has no --capture-dir") from exc
    if index + 1 >= len(command):
        raise ValueError("--capture-dir has no value")
    return Path(command[index + 1]).resolve()


def capture_is_complete(capture_dir: Path) -> bool:
    manifest_path = capture_dir / "capture_manifest.json"
    execution_path = capture_dir / "capture_execution.json"
    if not manifest_path.is_file() or not execution_path.is_file():
        return False
    manifest = load(manifest_path)
    execution = load(execution_path)
    verify_canonical(execution, "capture execution")
    return (
        manifest.get("schema_version")
        == "strict_v4_csr_caeos_runtime_capture_v1"
        and
        manifest.get("state") == "complete"
        and execution.get("schema_version")
        == "strict_v4_rrc_csr_base_capture_execution_v1"
        and execution.get("state") == "complete"
        and execution.get("capture_manifest_file_sha256")
        == file_hash(manifest_path)
    )


def state_payload(
    *,
    status: str,
    parent_pid: int,
    child_pid: int,
    capture_dir: Path,
    target_workers: int,
    old_command: list[str],
    new_command: list[str],
    new_pid: Optional[int] = None,
    detail: Optional[str] = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": "strict_v4_rrc_boundary_reschedule_state_v1",
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "old_parent_pid": parent_pid,
        "boundary_child_pid": child_pid,
        "boundary_capture_dir": str(capture_dir),
        "target_workers": target_workers,
        "old_command": old_command,
        "new_command": new_command,
        "new_pid": new_pid,
    }
    if detail is not None:
        payload["detail"] = detail
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--parent-pid", type=int, required=True)
    parser.add_argument("--child-pid", type=int, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--poll-seconds", type=int, default=30)
    parser.add_argument("--timeout-seconds", type=int, default=7200)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    parent_pid = int(args.parent_pid)
    child_pid = int(args.child_pid)
    if os.getpgid(parent_pid) != parent_pid:
        raise ValueError("old RRC parent must be its process-group leader")
    if os.getpgid(child_pid) != parent_pid:
        raise ValueError("boundary child must belong to the old RRC group")
    old_command = process_command(parent_pid)
    child_command = process_command(child_pid)
    capture_dir = capture_dir_from_command(child_command)
    expected_run_root = (
        project_root / "runs/strict_v4_rrc_csr_confirmation_v1"
    ).resolve()
    if expected_run_root not in capture_dir.parents:
        raise ValueError("boundary capture is outside the expected RRC run root")
    protocol_path = (
        project_root / "results/strict_v4_rrc_csr_confirmation_v1/protocol.json"
    )
    protocol = load(protocol_path)
    verify_canonical(protocol, "RRC protocol")
    target_workers = int(protocol["resource_contract"]["outer_workers"])
    if target_workers != 4:
        raise ValueError("unexpected frozen RRC outer worker count")
    new_command = replace_workers(old_command, target_workers)
    os.kill(parent_pid, signal.SIGSTOP)
    initial = state_payload(
        status="parent_stopped_waiting_for_boundary_child",
        parent_pid=parent_pid,
        child_pid=child_pid,
        capture_dir=capture_dir,
        target_workers=target_workers,
        old_command=old_command,
        new_command=new_command,
    )
    atomic_write(args.state, initial)
    deadline = time.monotonic() + int(args.timeout_seconds)
    while True:
        child_state = process_state(child_pid)
        if child_state is None or child_state == "Z":
            break
        if time.monotonic() >= deadline:
            os.kill(parent_pid, signal.SIGCONT)
            failed = state_payload(
                status="timeout_old_parent_resumed",
                parent_pid=parent_pid,
                child_pid=child_pid,
                capture_dir=capture_dir,
                target_workers=target_workers,
                old_command=old_command,
                new_command=new_command,
                detail="boundary child did not finish before timeout",
            )
            atomic_write(args.state, failed)
            raise TimeoutError("boundary child did not finish")
        time.sleep(max(1, int(args.poll_seconds)))

    os.kill(parent_pid, signal.SIGCONT)
    certificate_deadline = time.monotonic() + 120
    while not capture_is_complete(capture_dir):
        if process_state(parent_pid) is None:
            failed = state_payload(
                status="old_parent_exited_before_boundary_certificate",
                parent_pid=parent_pid,
                child_pid=child_pid,
                capture_dir=capture_dir,
                target_workers=target_workers,
                old_command=old_command,
                new_command=new_command,
            )
            atomic_write(args.state, failed)
            raise RuntimeError("old parent exited before boundary certificate")
        if time.monotonic() >= certificate_deadline:
            failed = state_payload(
                status="boundary_certificate_timeout_old_parent_running",
                parent_pid=parent_pid,
                child_pid=child_pid,
                capture_dir=capture_dir,
                target_workers=target_workers,
                old_command=old_command,
                new_command=new_command,
                detail="parent did not finalize capture execution certificate",
            )
            atomic_write(args.state, failed)
            raise TimeoutError("boundary certificate was not finalized")
        time.sleep(0.05)

    os.kill(parent_pid, signal.SIGSTOP)
    time.sleep(0.1)
    group_members = process_group_members(parent_pid)
    if group_members:
        os.kill(parent_pid, signal.SIGCONT)
        failed = state_payload(
            status="boundary_advanced_new_child_old_parent_resumed",
            parent_pid=parent_pid,
            child_pid=child_pid,
            capture_dir=capture_dir,
            target_workers=target_workers,
            old_command=old_command,
            new_command=new_command,
            detail=f"new process-group members already started: {group_members}",
        )
        atomic_write(args.state, failed)
        raise RuntimeError("old parent advanced beyond the safe task boundary")

    os.kill(parent_pid, signal.SIGTERM)
    os.kill(parent_pid, signal.SIGCONT)
    for _ in range(60):
        if process_state(parent_pid) is None:
            break
        time.sleep(1)
    if process_state(parent_pid) is not None:
        failed = state_payload(
            status="old_parent_did_not_terminate",
            parent_pid=parent_pid,
            child_pid=child_pid,
            capture_dir=capture_dir,
            target_workers=target_workers,
            old_command=old_command,
            new_command=new_command,
        )
        atomic_write(args.state, failed)
        raise RuntimeError("old RRC parent did not terminate")

    args.log.parent.mkdir(parents=True, exist_ok=True)
    with args.log.open("ab", buffering=0) as log:
        process = subprocess.Popen(
            new_command,
            cwd=project_root,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    complete = state_payload(
        status="rescheduled_at_canonical_task_boundary",
        parent_pid=parent_pid,
        child_pid=child_pid,
        capture_dir=capture_dir,
        target_workers=target_workers,
        old_command=old_command,
        new_command=new_command,
        new_pid=process.pid,
    )
    atomic_write(args.state, complete)
    print(json.dumps(complete, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
