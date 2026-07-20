from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

from run_nested_gate_matrix import build_run_provenance, freeze_or_validate_provenance
from run_neural_baseline_matrix import (
    Experiment,
    build_experiments,
    parse_arguments,
    suite_settings,
    write_manifest,
)


MODEL = "aegis_clean_adapter"


def command_for(experiment: Experiment, args: argparse.Namespace) -> list[str]:
    _, csv_path, config, benign, split, maximum = suite_settings(
        experiment.suite, args, experiment.seed
    )
    epochs = args.epochs if args.epochs > 0 else 50
    return [
        sys.executable,
        "train_aegis_open_set.py",
        "--csv",
        csv_path,
        "--config",
        config,
        "--unknown-classes",
        experiment.unknown_classes,
        "--benign-class",
        benign,
        "--split-strategy",
        split,
        "--max-per-class",
        str(maximum),
        "--epochs",
        str(epochs),
        "--correction-start-epoch",
        "20",
        "--patience",
        str(args.patience),
        "--batch-size",
        "128",
        "--num-workers",
        "4",
        "--seed",
        str(experiment.seed),
        "--output-dir",
        experiment.output_dir,
    ]


def run_one(experiment: Experiment, args: argparse.Namespace) -> dict[str, object]:
    output_dir = Path(experiment.output_dir)
    metrics_path = output_dir / "metrics.json"
    scores_path = output_dir / "scores.npz"
    output_dir.mkdir(parents=True, exist_ok=True)
    command = command_for(experiment, args)
    provenance = build_run_provenance(experiment, command)
    if freeze_or_validate_provenance(
        output_dir, provenance, (metrics_path, scores_path)
    ):
        return {
            **asdict(experiment),
            "status": "skipped",
            "elapsed_seconds": 0.0,
            "command": command,
            "parameter_fingerprint": provenance["parameter_fingerprint"],
        }
    started = time.perf_counter()
    with (output_dir / "run.log").open("w", encoding="utf-8") as log:
        completed = subprocess.run(
            command,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    elapsed = time.perf_counter() - started
    status = (
        "completed"
        if completed.returncode == 0 and metrics_path.exists() and scores_path.exists()
        else "failed"
    )
    if status == "failed":
        (output_dir / "failure.json").write_text(
            json.dumps(
                {"return_code": completed.returncode, "command": command}, indent=2
            )
            + "\n",
            encoding="utf-8",
        )
    return {
        **asdict(experiment),
        "status": status,
        "return_code": completed.returncode,
        "elapsed_seconds": elapsed,
        "command": command,
        "parameter_fingerprint": provenance["parameter_fingerprint"],
    }


def main() -> None:
    args = parse_arguments()
    args.models = "mlp"
    base = build_experiments(args)
    args.models = MODEL
    experiments = [
        Experiment(
            experiment.suite,
            experiment.scenario,
            experiment.unknown_classes,
            MODEL,
            experiment.seed,
            str(
                Path(args.output_root)
                / experiment.suite
                / f"{experiment.scenario}_seed{experiment.seed}_{MODEL}"
            ),
        )
        for experiment in base
    ]
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    results = []
    write_manifest(output_root, args, experiments, results, "running")
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(run_one, experiment, args): experiment
            for experiment in experiments
        }
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            write_manifest(output_root, args, experiments, results, "running")
            print(
                "%s: %s/%s model=%s seed=%s elapsed=%.1fs"
                % (
                    result["status"],
                    result["suite"],
                    result["scenario"],
                    result["model"],
                    result["seed"],
                    result["elapsed_seconds"],
                ),
                flush=True,
            )
    manifest = write_manifest(output_root, args, experiments, results, "complete")
    if manifest["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
