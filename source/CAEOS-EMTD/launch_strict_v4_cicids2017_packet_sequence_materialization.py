from __future__ import annotations

import argparse
import ctypes
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from strict_v4_cicids2017_attack_family import atomic_json, canonical_hash, file_hash


def process_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        process_query_limited_information = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(
            process_query_limited_information, False, pid
        )
        if not handle:
            return False
        ctypes.windll.kernel32.CloseHandle(handle)
        return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def launch(args: argparse.Namespace) -> dict[str, Any]:
    project_root = args.project_root.resolve()
    state_path = args.state_output.resolve()
    if state_path.is_file():
        existing = json.loads(state_path.read_text(encoding="utf-8"))
        existing_pid = int(existing.get("pid", -1))
        if existing.get("state") == "launched" and process_is_alive(existing_pid):
            raise RuntimeError(f"materialization is already running as PID {existing_pid}")
    script = project_root / "prepare_strict_v4_cicids2017_packet_sequences.py"
    command = [
        str(args.python.resolve()),
        str(script),
        "--labels-dir",
        str(args.labels_dir.resolve()),
        "--pcap-dir",
        str(args.pcap_dir.resolve()),
        "--output",
        str(args.output.resolve()),
        "--audit-output",
        str(args.audit_output.resolve()),
        "--progress-output",
        str(args.progress_output.resolve()),
        "--seed",
        str(args.seed),
        "--maximum-per-family",
        str(args.maximum_per_family),
        "--sequence-length",
        str(args.sequence_length),
        "--minimum-packets",
        str(args.minimum_packets),
        "--offset-probe-packets",
        str(args.offset_probe_packets),
        "--offset-minimum-unique-matches",
        str(args.offset_minimum_unique_matches),
        "--pcap-workers",
        str(args.pcap_workers),
    ]
    args.log.resolve().parent.mkdir(parents=True, exist_ok=True)
    log_handle = args.log.resolve().open("ab", buffering=0)

    def lower_priority() -> None:
        os.nice(args.nice)

    process = subprocess.Popen(
        command,
        cwd=project_root,
        stdin=subprocess.DEVNULL,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        preexec_fn=lower_priority,
    )
    log_handle.close()
    state: dict[str, Any] = {
        "schema_version": "strict_v4_cicids2017_packet_sequence_launch_v1",
        "state": "launched",
        "pid": process.pid,
        "started_unix_seconds": time.time(),
        "command": command,
        "nice": args.nice,
        "log": str(args.log.resolve()),
        "progress_output": str(args.progress_output.resolve()),
        "expected_output": str(args.output.resolve()),
        "source": {
            "script": str(script),
            "script_sha256": file_hash(script),
        },
        "claim_boundary": {
            "data_materialization_only": True,
            "model_training": False,
            "gpu_execution_claim": False,
        },
    }
    state["manifest_sha256"] = canonical_hash(state)
    atomic_json(state_path, state)
    return state


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--labels-dir", type=Path, required=True)
    parser.add_argument("--pcap-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--audit-output", type=Path, required=True)
    parser.add_argument("--progress-output", type=Path, required=True)
    parser.add_argument("--state-output", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260728)
    parser.add_argument("--maximum-per-family", type=int, default=5000)
    parser.add_argument("--sequence-length", type=int, default=32)
    parser.add_argument("--minimum-packets", type=int, default=2)
    parser.add_argument("--offset-probe-packets", type=int, default=5_000_000)
    parser.add_argument("--offset-minimum-unique-matches", type=int, default=5)
    parser.add_argument("--pcap-workers", type=int, default=5)
    parser.add_argument("--nice", type=int, default=10)
    return parser.parse_args()


def main() -> None:
    state = launch(parse_arguments())
    print(json.dumps(state, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
