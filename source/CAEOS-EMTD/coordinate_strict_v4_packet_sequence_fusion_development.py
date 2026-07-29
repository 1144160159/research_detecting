from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path
from typing import Any

import numpy as np

from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)


def write_state(path: Path, state: str, **values: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": "strict_v4_packet_sequence_fusion_coordinator_v1",
        "state": state,
        "updated_unix_seconds": time.time(),
        **values,
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    atomic_json(path, payload)
    return payload


def dataset_is_ready(dataset_path: Path) -> tuple[bool, str]:
    metadata_path = dataset_path.with_suffix(dataset_path.suffix + ".json")
    if not dataset_path.is_file() or not metadata_path.is_file():
        return False, "dataset_or_metadata_missing"
    try:
        metadata = load_canonical(metadata_path, "packet-sequence dataset metadata")
    except (ValueError, json.JSONDecodeError, OSError) as error:
        return False, f"metadata_invalid:{type(error).__name__}"
    if metadata.get("state") not in {
        "complete_remote_pcap_sequence_materialization",
        "complete_remote_packet_sequence_statistic_augmentation",
    }:
        return False, f"metadata_state:{metadata.get('state')}"
    if file_hash(dataset_path) != metadata.get("dataset", {}).get("output_sha256"):
        return False, "dataset_hash_mismatch"
    try:
        with np.load(dataset_path, allow_pickle=False) as source:
            families = sorted(
                str(value) for value in np.unique(source["families"])
            )
            if (
                source["packet_lengths"].shape
                != source["interarrival_us"].shape
                or source["packet_lengths"].shape != source["mask"].shape
            ):
                return False, "sequence_array_shape_mismatch"
            if (
                "flow_statistics" not in source.files
                or "flow_statistic_names" not in source.files
                or source["flow_statistics"].ndim != 2
                or source["flow_statistics"].shape[0]
                != source["packet_lengths"].shape[0]
                or source["flow_statistic_names"].shape[0]
                != source["flow_statistics"].shape[1]
            ):
                return False, "flow_statistics_missing_or_inconsistent"
    except (ValueError, KeyError, OSError) as error:
        return False, f"dataset_invalid:{type(error).__name__}"
    if "Benign" not in families or len(families) != 8:
        return False, f"family_coverage_incomplete:{','.join(families)}"
    return True, "ready"


def checked_run(command: list[str], cwd: Path) -> None:
    completed = subprocess.run(command, cwd=cwd, check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            f"command exited {completed.returncode}: {' '.join(command)}"
        )


def coordinate(args: argparse.Namespace) -> dict[str, Any]:
    project_root = args.project_root.resolve()
    dataset_path = args.sequence_dataset.resolve()
    result_root = args.result_root.resolve()
    run_root = args.run_root.resolve()
    state_path = args.state_output.resolve()
    result_root.mkdir(parents=True, exist_ok=True)
    deadline = time.time() + args.maximum_wait_seconds
    while True:
        ready, reason = dataset_is_ready(dataset_path)
        if ready:
            break
        if time.time() >= deadline:
            raise TimeoutError(f"sequence dataset did not become ready: {reason}")
        write_state(
            state_path,
            "waiting_for_sequence_dataset",
            readiness_reason=reason,
            sequence_dataset=str(dataset_path),
            confirmation_seeds_read_or_launched=False,
        )
        time.sleep(args.poll_seconds)
    protocol_path = result_root / "protocol.json"
    write_state(
        state_path,
        "freezing_development_protocol",
        sequence_dataset=str(dataset_path),
        protocol_path=str(protocol_path),
        confirmation_seeds_read_or_launched=False,
    )
    checked_run(
        [
            str(args.python.resolve()),
            str(project_root / "create_strict_v4_packet_sequence_fusion_protocol.py"),
            "--project-root",
            str(project_root),
            "--sequence-dataset",
            str(dataset_path),
            "--result-root",
            str(result_root),
            "--run-root",
            str(run_root),
            "--output",
            str(protocol_path),
            "--maximum-parallel-tasks",
            str(args.maximum_parallel_tasks),
        ],
        project_root,
    )
    write_state(
        state_path,
        "running_cuda_development_matrix",
        protocol_path=str(protocol_path),
        protocol_sha256=file_hash(protocol_path),
        confirmation_seeds_read_or_launched=False,
    )
    checked_run(
        [
            str(args.python.resolve()),
            str(project_root / "run_strict_v4_packet_sequence_fusion_development.py"),
            "--protocol",
            str(protocol_path),
            "--python",
            str(args.python.resolve()),
        ],
        project_root,
    )
    completion_path = result_root / "completion.json"
    development_path = result_root / "development.json"
    write_state(
        state_path,
        "evaluating_development_matrix",
        completion_path=str(completion_path),
        completion_sha256=file_hash(completion_path),
        confirmation_seeds_read_or_launched=False,
    )
    checked_run(
        [
            str(args.python.resolve()),
            str(
                project_root
                / "evaluate_strict_v4_packet_sequence_fusion_development.py"
            ),
            "--completion",
            str(completion_path),
            "--output",
            str(development_path),
        ],
        project_root,
    )
    development = load_canonical(
        development_path, "packet-sequence development result"
    )
    passed = bool(
        development.get("selected", {})
        .get("gates", {})
        .get("full_known_unknown_95_5_gate")
    )
    return write_state(
        state_path,
        (
            "development_full_gate_passed_confirmation_not_launched"
            if passed
            else "development_gate_not_met_confirmation_not_launched"
        ),
        protocol_path=str(protocol_path),
        completion_path=str(completion_path),
        development_path=str(development_path),
        development_sha256=file_hash(development_path),
        development_manifest_sha256=development["manifest_sha256"],
        full_gate_passed=passed,
        confirmation_seeds_read_or_launched=False,
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--sequence-dataset", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--state-output", type=Path, required=True)
    parser.add_argument("--maximum-parallel-tasks", type=int, default=4)
    parser.add_argument("--poll-seconds", type=float, default=30.0)
    parser.add_argument("--maximum-wait-seconds", type=float, default=21600.0)
    return parser.parse_args()


def main() -> None:
    state = coordinate(parse_arguments())
    print(json.dumps(state, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
