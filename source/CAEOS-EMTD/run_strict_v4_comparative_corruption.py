from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash
from create_strict_v4_final_efficiency_execution_plan_v2 import replace_option


def provenance_arguments(path: Path, suite: str, scenario: str, seed: int) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    task = payload.get("task", {})
    command = payload.get("command")
    if task.get("suite") != suite or task.get("scenario") != scenario or int(task.get("seed", -1)) != seed:
        raise ValueError(f"candidate provenance identity mismatch: {path}")
    if not isinstance(command, list) or len(command) < 3 or Path(str(command[1])).name != "train_hybrid_open_set.py":
        raise ValueError(f"candidate provenance command is invalid: {path}")
    return [str(value) for value in command[2:]]


def run(command: list[str], cwd: Path, log: Path) -> None:
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as handle:
        subprocess.run(command, cwd=cwd, check=True, stdout=handle, stderr=subprocess.STDOUT)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    if protocol.get("schema_version") != "strict_v4_comparative_corruption_protocol_v1" or protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("comparative corruption protocol validation failed")
    implementations = protocol["implementation_sha256"]
    active_paths = {
        "candidate_trainer": args.project_root / "train_hybrid_open_set.py",
        "candidate_runtime": args.project_root / "caeos" / "pairwise_runtime.py",
        "candidate_capture": args.project_root / "capture_pairwise_runtime.py",
        "comparator_runtime": args.project_root / "caeos" / "open_detect_runtime.py",
        "comparator_capture": args.project_root / "capture_opendetect_runtime.py",
        "evaluator": args.project_root / "evaluate_strict_v4_comparative_corruption.py",
        "runner": Path(__file__),
    }
    for name, path in active_paths.items():
        if file_hash(path) != implementations[name]:
            raise ValueError(f"active comparative corruption implementation SHA mismatch: {name}")
    root = args.output_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    lock = root / "runner.lock.d"
    try:
        lock.mkdir()
    except FileExistsError:
        raise RuntimeError("comparative corruption runner is already active")
    completed = 0
    try:
        for source in protocol["source_registry"]:
            suite, scenario, seed = source["suite"], source["scenario"], int(source["seed"])
            block = root / "blocks" / suite / scenario / f"seed{seed}"
            candidate_capture = block / "candidate_capture"
            comparator_capture = block / "comparator_capture"
            output = block / "paired_corruption.json"
            if output.is_file():
                payload = json.loads(output.read_text(encoding="utf-8"))
                if (
                    payload.get("schema_version")
                    != "strict_v4_comparative_corruption_block_v1"
                    or payload.get("manifest_sha256") != canonical_hash(payload)
                    or payload.get("protocol_manifest_sha256")
                    != protocol["manifest_sha256"]
                    or payload.get("suite") != suite
                    or payload.get("scenario") != scenario
                    or int(payload.get("seed", -1)) != seed
                    or payload.get("candidate_comparator_input_arrays_equal") is not True
                    or payload.get(
                        "unknown_or_test_labels_used_for_fitting_selection_or_corruption_generation"
                    )
                    is not False
                    or {
                        item.get("family") for item in payload.get("conditions", [])
                    }
                    != set(protocol["corruption_conditions"]["families"])
                ):
                    raise ValueError(f"paired corruption resume validation failed: {output}")
                completed += 1
                continue
            candidate_root = Path(source["candidate_root"])
            comparator_root = Path(source["comparator_root"])
            if not (candidate_capture / "capture_manifest.json").is_file():
                trainer_args = provenance_arguments(
                    candidate_root / "provenance.json", suite, scenario, seed
                )
                trainer_args = replace_option(
                    trainer_args, "--output-dir", str(block / "candidate_refit")
                )
                run(
                    [
                        sys.executable,
                        "capture_pairwise_runtime.py",
                        "--trainer",
                        "train_hybrid_open_set.py",
                        "--capture-dir",
                        str(candidate_capture),
                        "--",
                        *trainer_args,
                    ],
                    args.project_root,
                    block / "candidate_capture.log",
                )
            if not (comparator_capture / "capture_manifest.json").is_file():
                run(
                    [
                        sys.executable,
                        "capture_opendetect_runtime.py",
                        "--source-run",
                        str(comparator_root),
                        "--capture-dir",
                        str(comparator_capture),
                        "--device",
                        "cpu",
                        "--absolute-tolerance",
                        "1e-12",
                        "--equivalence-mode",
                        "same_device_shadow",
                    ],
                    args.project_root,
                    block / "comparator_capture.log",
                )
            run(
                [
                    sys.executable,
                    "evaluate_strict_v4_comparative_corruption.py",
                    "--protocol",
                    str(args.protocol.resolve()),
                    "--suite",
                    suite,
                    "--scenario",
                    scenario,
                    "--seed",
                    str(seed),
                    "--candidate-capture",
                    str(candidate_capture),
                    "--comparator-capture",
                    str(comparator_capture),
                    "--output",
                    str(output),
                ],
                args.project_root,
                block / "evaluation.log",
            )
            completed += 1
            print(f"completed={completed}/306 suite={suite} scenario={scenario} seed={seed}", flush=True)
        if completed != 306:
            raise RuntimeError("comparative corruption runtime capture matrix is incomplete")
        (root / "execution_complete").touch()
    finally:
        lock.rmdir()


if __name__ == "__main__":
    main()
