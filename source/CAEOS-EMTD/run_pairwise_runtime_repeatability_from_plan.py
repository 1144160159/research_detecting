from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Replay one frozen efficiency capture as a non-formal repeatability diagnostic"
    )
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    block = next(
        item
        for item in plan["inference_blocks"]
        if item["suite"] == args.suite and item["scenario"] == args.scenario
    )
    step = next(item for item in block["steps"] if item["role"] == "candidate_inference_capture")
    command = [str(value) for value in step["command"]]
    if not command[1].endswith("capture_pairwise_runtime.py"):
        raise ValueError("frozen step is not a Pairwise runtime capture")
    command[1] = str((args.project_root / "diagnose_pairwise_runtime_repeatability.py").resolve())
    capture_index = command.index("--capture-dir")
    command[capture_index] = "--output"
    command[capture_index + 1] = str(args.output.resolve())
    delimiter = command.index("--")
    trainer_output_index = command.index("--output-dir", delimiter)
    diagnostic_run = args.output.parent / f"{args.suite}_{args.scenario}_trainer"
    command[trainer_output_index + 1] = str(diagnostic_run.resolve())

    args.output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(command, cwd=args.project_root, check=True)


if __name__ == "__main__":
    main()
