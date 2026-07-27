from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash
from watch_strict_v4_pug_confirmation import busy_processes, process_snapshot


def process_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def acquire_process_lock(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    pid_path = path / "pid"
    try:
        path.mkdir()
    except FileExistsError:
        try:
            existing_pid = int(pid_path.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            existing_pid = -1
        if existing_pid > 0 and process_exists(existing_pid):
            raise RuntimeError("PUG deployment watcher is already active")
        try:
            pid_path.unlink()
        except FileNotFoundError:
            pass
        path.rmdir()
        path.mkdir()
    pid_path.write_text(str(os.getpid()) + "\n", encoding="utf-8")
    return path


def release_process_lock(path: Path) -> None:
    try:
        (path / "pid").unlink()
    except FileNotFoundError:
        pass
    try:
        path.rmdir()
    except FileNotFoundError:
        pass


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as destination:
        destination.write(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)


def validate_staging(staging: Path, manifest: dict[str, Any]) -> None:
    if (
        manifest.get("schema_version") != "strict_v4_pug_staging_manifest_v1"
        or manifest.get("manifest_sha256") != canonical_hash(manifest)
    ):
        raise ValueError("canonical PUG staging manifest required")
    deployer = manifest["deployer"]
    if file_hash(staging / deployer["path"]) != deployer["file_sha256"]:
        raise ValueError("staged deployer drifted")
    protocol_record = manifest["execution_protocol"]
    protocol_path = staging / protocol_record["path"]
    protocol = load(protocol_path)
    if (
        file_hash(protocol_path) != protocol_record["file_sha256"]
        or protocol.get("manifest_sha256")
        != protocol_record["canonical_sha256"]
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("staged execution protocol drifted")
    for group in ("install_files", "verify_only_files"):
        for relative, expected in manifest[group].items():
            path = staging / relative
            if not path.is_file() or file_hash(path) != expected:
                raise ValueError(f"staged file drifted: {relative}")


def verify_main_dependencies(root: Path, manifest: dict[str, Any]) -> None:
    for relative, expected in manifest["verify_only_files"].items():
        path = root / relative
        if not path.is_file() or file_hash(path) != expected:
            raise ValueError(f"main dependency drifted: {relative}")
    trainer = root / "train_hybrid_open_set.py"
    current = file_hash(trainer)
    allowed = {
        manifest["admission"]["expected_current_main_trainer_sha256"],
        manifest["admission"]["target_trainer_sha256"],
    }
    if current not in allowed:
        raise ValueError("unexpected main trainer drift")


def terminal_krc_ready(root: Path) -> bool:
    result = root / "results/strict_v4_krc_csr_confirmation_v1"
    summary_path = result / "summary.json"
    audit_path = result / "audit.json"
    if not summary_path.is_file() or not audit_path.is_file():
        return False
    try:
        summary = load(summary_path)
        audit = load(audit_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    return (
        summary.get("schema_version")
        == "strict_v4_krc_csr_confirmation_summary_v1"
        and summary.get("state") == "complete"
        and summary.get("manifest_sha256") == canonical_hash(summary)
        and audit.get("schema_version")
        == "strict_v4_krc_csr_confirmation_audit_v1"
        and audit.get("state") == "complete"
        and audit.get("manifest_sha256") == canonical_hash(audit)
        and audit.get("summary_manifest_sha256")
        == summary.get("manifest_sha256")
    )


def install(staging: Path, root: Path, manifest: dict[str, Any]) -> None:
    temporary_paths = []
    for relative, expected in manifest["install_files"].items():
        source = staging / relative
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + ".pug-next")
        shutil.copyfile(source, temporary)
        if file_hash(temporary) != expected:
            raise ValueError(f"temporary install verification failed: {relative}")
        temporary_paths.append((temporary, target, expected))
    for temporary, target, _expected in temporary_paths:
        os.replace(temporary, target)
    for _temporary, target, expected in temporary_paths:
        if file_hash(target) != expected:
            raise ValueError(f"installed file verification failed: {target}")

    protocol_record = manifest["execution_protocol"]
    source_protocol = staging / protocol_record["path"]
    target_protocol = root / protocol_record["path"]
    target_protocol.parent.mkdir(parents=True, exist_ok=True)
    temporary_protocol = target_protocol.with_name(
        target_protocol.name + ".pug-next"
    )
    shutil.copyfile(source_protocol, temporary_protocol)
    if file_hash(temporary_protocol) != protocol_record["file_sha256"]:
        raise ValueError("temporary protocol verification failed")
    os.replace(temporary_protocol, target_protocol)


def launch_watcher(root: Path, result_root: Path) -> int:
    log = result_root / "deployment_watcher.nohup.log"
    state = result_root / "watcher_state.json"
    with log.open("ab") as destination:
        process = subprocess.Popen(
            [
                "/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python",
                str(root / "watch_strict_v4_pug_confirmation.py"),
                "--project-root",
                str(root),
                "--state",
                str(state),
            ],
            cwd=root,
            env={
                **os.environ,
                "PYTHONPATH": (
                    ".:/opt/data/private/wangwt/anaconda3/envs/py3.9/"
                    "lib/python3.9/site-packages"
                ),
            },
            stdin=subprocess.DEVNULL,
            stdout=destination,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    return process.pid


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--staging-root", type=Path, required=True)
    parser.add_argument("--poll-seconds", type=int, default=300)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--no-install", action="store_true")
    args = parser.parse_args()
    root = args.project_root.resolve()
    staging = args.staging_root.resolve()
    try:
        lock_path = acquire_process_lock(staging / "deployment.lock.d")
    except RuntimeError as error:
        print(json.dumps({"state": "already_active", "error": str(error)}))
        return
    manifest_path = staging / "staging_manifest.json"
    manifest = load(manifest_path)
    validate_staging(staging, manifest)
    state_path = staging / "deployment_state.json"
    idle_count = 0
    while True:
        krc_ready = terminal_krc_ready(root)
        busy = busy_processes(process_snapshot())
        idle_count = idle_count + 1 if krc_ready and not busy else 0
        required = int(
            manifest["admission"]["resource_idle_consecutive_polls"]
        )
        state: dict[str, Any] = {
            "state": (
                "waiting_for_krc_terminal"
                if not krc_ready
                else "waiting_for_resources"
                if busy
                else "resources_idle"
            ),
            "krc_terminal_ready": krc_ready,
            "busy_process_count": len(busy),
            "idle_consecutive_polls": idle_count,
            "required_idle_consecutive_polls": required,
            "installed": False,
            "watcher_launched": False,
        }
        if krc_ready and not busy and idle_count >= required and not args.no_install:
            verify_main_dependencies(root, manifest)
            install(staging, root, manifest)
            result_root = (
                root / "results/strict_v4_pug_confirmation_v1"
            )
            watcher_pid = launch_watcher(root, result_root)
            state.update(
                {
                    "state": "installed_and_watcher_launched",
                    "installed": True,
                    "watcher_launched": True,
                    "watcher_pid": watcher_pid,
                }
            )
        atomic_json(state_path, state)
        print(json.dumps(state, sort_keys=True), flush=True)
        if args.once or state["watcher_launched"]:
            release_process_lock(lock_path)
            return
        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    main()
