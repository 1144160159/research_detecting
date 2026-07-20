from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from run_nested_gate_matrix import HIKARI_SCENARIOS


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run HIKARI nested neural gate matrix")
    parser.add_argument("--seeds", default="7,11,19")
    parser.add_argument("--scenarios", default="all")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--epochs", type=int, default=35)
    parser.add_argument("--patience", type=int, default=7)
    parser.add_argument("--max-per-class", type=int, default=2000)
    parser.add_argument("--minimum-neural-gain", type=float, default=0.0)
    parser.add_argument(
        "--candidate-model", choices=("mlp", "closr", "opendetect"), default="mlp"
    )
    parser.add_argument(
        "--csv",
        default="/opt/data/private/wangwt/ParkAttackKE/datasets/HIKARI2021/HIKARI2021_model.csv",
    )
    parser.add_argument(
        "--gate-root", default="runs/nested_conflict_gate_confirmation/hikari"
    )
    parser.add_argument(
        "--neural-root", default="results/neural_baseline_hikari_confirmation/hikari"
    )
    parser.add_argument("--output-root", default="runs/nested_neural_gate_hikari")
    return parser.parse_args()


def command_for(scenario: str, unknown: str, seed: int, args: argparse.Namespace):
    output_dir = Path(args.output_root) / f"{scenario}_seed{seed}"
    command = [
        sys.executable,
        "train_nested_neural_gate.py",
        "--csv",
        args.csv,
        "--config",
        "configs/hikari2021.json",
        "--unknown-classes",
        unknown,
        "--benign-class",
        "Benign",
        "--split-strategy",
        "fingerprint_grouped",
        "--max-per-class",
        str(args.max_per_class),
        "--epochs",
        str(args.epochs),
        "--patience",
        str(args.patience),
        "--minimum-neural-gain",
        str(args.minimum_neural_gain),
        "--candidate-model",
        args.candidate_model,
        "--seed",
        str(seed),
        "--gate-metrics",
        str(Path(args.gate_root) / f"{scenario}_seed{seed}" / "metrics.json"),
        "--neural-metrics",
        str(Path(args.neural_root) / f"{scenario}_seed{seed}_{args.candidate_model}" / "metrics.json"),
        "--output-dir",
        str(output_dir),
    ]
    if args.candidate_model == "closr":
        command.extend(
            [
                "--hidden-dim", "1024",
                "--embedding-dim", "64",
                "--learning-rate", "1e-5",
                "--weight-decay", "0.0403709",
                "--batch-size", "4096",
                "--closr-depth", "3",
                "--closr-margin", "1",
                "--closr-alpha", "0.5",
            ]
        )
    elif args.candidate_model == "opendetect":
        command.extend(
            [
                "--hidden-dim", "256",
                "--embedding-dim", "128",
                "--learning-rate", "1e-3",
                "--weight-decay", "0",
                "--batch-size", "128",
                "--open-detect-temperature", "1",
                "--open-detect-generative-weight", "0.005",
                "--open-detect-reset-epochs", "50,80",
            ]
        )
    return output_dir, command


def run_one(scenario: str, unknown: str, seed: int, args: argparse.Namespace):
    output_dir, command = command_for(scenario, unknown, seed, args)
    metrics_path = output_dir / "metrics.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    if metrics_path.exists():
        return {"scenario": scenario, "seed": seed, "status": "skipped", "elapsed_seconds": 0.0}
    started = time.perf_counter()
    with (output_dir / "run.log").open("w", encoding="utf-8") as log:
        completed = subprocess.run(
            command, stdout=log, stderr=subprocess.STDOUT, text=True, check=False
        )
    elapsed = time.perf_counter() - started
    status = "completed" if completed.returncode == 0 and metrics_path.exists() else "failed"
    return {
        "scenario": scenario,
        "seed": seed,
        "status": status,
        "return_code": completed.returncode,
        "elapsed_seconds": elapsed,
    }


def main() -> None:
    args = parse_arguments()
    requested = None if args.scenarios == "all" else set(args.scenarios.split(","))
    seeds = [int(value) for value in args.seeds.split(",") if value.strip()]
    experiments = [
        (scenario, unknown, seed)
        for scenario, unknown in HIKARI_SCENARIOS.items()
        if requested is None or scenario in requested
        for seed in seeds
    ]
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(run_one, scenario, unknown, seed, args): (scenario, seed)
            for scenario, unknown, seed in experiments
        }
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(
                "%s: %s seed=%d elapsed=%.1fs"
                % (
                    result["status"],
                    result["scenario"],
                    result["seed"],
                    result["elapsed_seconds"],
                ),
                flush=True,
            )
    manifest = {
        "arguments": vars(args),
        "number_of_experiments": len(experiments),
        "completed": sum(result["status"] == "completed" for result in results),
        "skipped": sum(result["status"] == "skipped" for result in results),
        "failed": sum(result["status"] == "failed" for result in results),
        "runs": sorted(results, key=lambda value: (value["scenario"], value["seed"])),
    }
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    with (output_root / "manifest.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
    if manifest["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
