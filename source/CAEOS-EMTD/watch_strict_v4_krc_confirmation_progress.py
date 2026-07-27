from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import time
from typing import Any, Dict, Optional

from audit_krc_csr_confirmation_progress import audit
from create_strict_v4_external_confirmation_protocol import canonical_hash


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def atomic_checkpoint_count(
    captures: int,
    timings: int,
    evaluations: int,
    *,
    conditions_per_capture: int = 6,
    checkpoint_stride: int = 4,
    frozen_total: int = 306,
) -> Optional[int]:
    if min(captures, timings, evaluations) < 0:
        raise ValueError("progress counts must be nonnegative")
    if (
        captures == 0
        or captures > frozen_total
        or captures != timings
        or evaluations != captures * conditions_per_capture
        or (
            captures % checkpoint_stride != 0
            and captures != frozen_total
        )
    ):
        return None
    return captures


def count_outputs(run_root: Path) -> Dict[str, int]:
    return {
        "captures": len(
            list((run_root / "captures").rglob("capture_manifest.json"))
        ),
        "timings": len(
            list((run_root / "captures").rglob("capture_execution.json"))
        ),
        "evaluations": len(
            list((run_root / "evaluations").rglob("evaluation.json"))
        ),
    }


def validate_existing(path: Path, expected_count: int) -> bool:
    if not path.exists():
        return False
    value = load_json(path)
    observed = value.get("observed_totals", {})
    if (
        value.get("schema_version")
        != "strict_v4_krc_csr_confirmation_progress_audit_v1"
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("passes") is not True
        or int(observed.get("captures", -1)) != expected_count
        or int(observed.get("capture_executions", -1)) != expected_count
        or int(observed.get("evaluations", -1)) != expected_count * 6
    ):
        raise ValueError(f"invalid existing KRC progress checkpoint: {path}")
    return True


def append_state(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with path.open("a", encoding="utf-8") as stream:
        stream.write(f"{stamp} {message}\n")


def freeze_checkpoint(
    protocol_path: Path,
    run_root: Path,
    output_root: Path,
    count: int,
) -> Dict[str, Any]:
    output = output_root / f"progress_{count:03d}.json"
    if validate_existing(output, count):
        return load_json(output)
    output_root.mkdir(parents=True, exist_ok=True)
    staging = output_root / f".progress_{count:03d}.{os.getpid()}.tmp"
    evidence = audit(protocol_path, run_root, staging)
    evidence["output_path"] = output.resolve().as_posix()
    evidence["manifest_sha256"] = canonical_hash(evidence)
    staging.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(staging, output)
    validate_existing(output, count)
    return evidence


def watch(
    protocol_path: Path,
    run_root: Path,
    output_root: Path,
    state_path: Path,
    *,
    poll_seconds: int,
    once: bool,
) -> None:
    lock = output_root / "progress_watcher.lock.d"
    output_root.mkdir(parents=True, exist_ok=True)
    try:
        lock.mkdir()
    except FileExistsError:
        append_state(state_path, "progress watcher already active")
        return
    previous_sigterm = signal.getsignal(signal.SIGTERM)

    def stop_on_sigterm(signum, frame):
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, stop_on_sigterm)
    try:
        append_state(state_path, "waiting for atomic KRC checkpoints")
        while True:
            counts = count_outputs(run_root)
            candidate = atomic_checkpoint_count(
                counts["captures"],
                counts["timings"],
                counts["evaluations"],
            )
            if candidate is not None:
                output = output_root / f"progress_{candidate:03d}.json"
                if not output.exists():
                    try:
                        evidence = freeze_checkpoint(
                            protocol_path,
                            run_root,
                            output_root,
                            candidate,
                        )
                        append_state(
                            state_path,
                            (
                                f"froze progress_{candidate:03d} "
                                f"{evidence['manifest_sha256']}"
                            ),
                        )
                    except Exception as error:
                        append_state(
                            state_path,
                            (
                                f"deferred progress_{candidate:03d} "
                                f"{type(error).__name__}: {error}"
                            ),
                        )
                        if once:
                            raise
                else:
                    validate_existing(output, candidate)
                if candidate == 306:
                    append_state(state_path, "final KRC checkpoint observed")
                    return
            if once:
                return
            time.sleep(int(poll_seconds))
    finally:
        signal.signal(signal.SIGTERM, previous_sigterm)
        lock.rmdir()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--poll-seconds", type=int, default=300)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if args.poll_seconds < 10:
        raise ValueError("poll interval must be at least 10 seconds")
    watch(
        args.protocol.resolve(),
        args.run_root.resolve(),
        args.output_root.resolve(),
        args.state.resolve(),
        poll_seconds=args.poll_seconds,
        once=args.once,
    )


if __name__ == "__main__":
    main()
