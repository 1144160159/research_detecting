from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
    "known_acceptance_rate",
    "unknown_rejection_rate",
)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the CAEOS two-dataset minimal open-set reproduction."
    )
    parser.add_argument("--mal-csv", type=Path, required=True)
    parser.add_argument("--hikari-csv", type=Path, required=True)
    parser.add_argument("--mode", choices=("smoke", "paper"), default="smoke")
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--reuse", action="store_true")
    parser.add_argument(
        "--hash-inputs",
        action="store_true",
        help="Hash the source CSV files; recommended for a paper-mode archive.",
    )
    return parser.parse_args()


def build_runs(
    protocol: dict[str, Any],
    mode: str,
    csv_paths: dict[str, Path],
    output_root: Path,
) -> list[dict[str, Any]]:
    mode_config = protocol["modes"][mode]
    runs: list[dict[str, Any]] = []
    for dataset_name, dataset in protocol["datasets"].items():
        csv_path = csv_paths[dataset["csv_argument"]]
        for seed in mode_config["seeds"]:
            for profile_name, profile in protocol["risk_profiles"].items():
                output_dir = (
                    output_root / mode / dataset_name / f"seed{seed}" / profile_name
                )
                runs.append(
                    {
                        "dataset": dataset_name,
                        "csv": csv_path,
                        "config": dataset["config"],
                        "unknown_classes": dataset["unknown_classes"],
                        "benign_class": dataset["benign_class"],
                        "max_per_class": dataset["max_per_class"][mode],
                        "seed": seed,
                        "estimators": mode_config["estimators"],
                        "profile": profile_name,
                        "risk_selection": profile["risk_selection"],
                        "fixed_risk_name": profile.get("fixed_risk_name"),
                        "output_dir": output_dir,
                    }
                )
    return runs


def command_for(
    run: dict[str, Any],
    protocol: dict[str, Any],
    project_root: Path,
    python: str,
) -> list[str]:
    shared = protocol["shared"]
    command = [
        python,
        str(project_root / "train_hybrid_open_set.py"),
        "--csv",
        str(run["csv"]),
        "--config",
        str(project_root / run["config"]),
        "--unknown-classes",
        run["unknown_classes"],
        "--benign-class",
        run["benign_class"],
        "--max-per-class",
        str(run["max_per_class"]),
        "--estimators",
        str(run["estimators"]),
        "--jobs",
        str(shared["jobs"]),
        "--global-max-features",
        str(shared["global_max_features"]),
        "--known-acceptance",
        str(shared["known_acceptance"]),
        "--split-strategy",
        shared["split_strategy"],
        "--risk-selection",
        run["risk_selection"],
        "--seed",
        str(run["seed"]),
        "--output-dir",
        str(run["output_dir"]),
    ]
    if run["fixed_risk_name"]:
        command.extend(["--fixed-risk-name", run["fixed_risk_name"]])
    return command


def output_record(run: dict[str, Any], required: list[str]) -> dict[str, Any]:
    files = {name: run["output_dir"] / name for name in required}
    missing = [name for name, path in files.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            f"{run['output_dir']} is missing required outputs: {missing}"
        )
    metrics = load_json(files["metrics.json"])
    report = metrics.get("selected_report", {})
    return {
        "dataset": run["dataset"],
        "seed": run["seed"],
        "profile": run["profile"],
        "selected_risk": metrics.get("selected_risk"),
        "metrics": {name: report.get(name) for name in METRICS},
        "output_sha256": {name: file_hash(path) for name, path in files.items()},
    }


def main() -> None:
    args = parse_arguments()
    project_root = Path(__file__).resolve().parents[1]
    protocol_path = Path(__file__).with_name("minimal_open_set_profile.json")
    environment_path = Path(__file__).with_name("environment-gpu-cu121.json")
    protocol = load_json(protocol_path)
    if protocol.get("schema_version") != "caeos_minimal_open_set_repro_v1":
        raise ValueError("unexpected minimal reproduction protocol schema")

    csv_paths = {"mal_csv": args.mal_csv, "hikari_csv": args.hikari_csv}
    missing_inputs = [str(path) for path in csv_paths.values() if not path.is_file()]
    if missing_inputs:
        raise FileNotFoundError(f"missing input CSV files: {missing_inputs}")

    runs = build_runs(protocol, args.mode, csv_paths, args.output_root.resolve())
    commands = [
        command_for(run, protocol, project_root, args.python) for run in runs
    ]
    input_identity: dict[str, Any] = {}
    for name, path in csv_paths.items():
        stat = path.stat()
        input_identity[name] = {
            "path": str(path.resolve()),
            "size_bytes": stat.st_size,
            "sha256": file_hash(path) if args.hash_inputs else None,
        }

    manifest: dict[str, Any] = {
        "schema_version": "caeos_minimal_open_set_repro_manifest_v1",
        "mode": args.mode,
        "scientific_evidence": protocol["modes"][args.mode]["scientific_evidence"],
        "dry_run": args.dry_run,
        "python": {
            "executable": args.python,
            "controller_version": platform.python_version(),
        },
        "source_sha256": {
            "protocol": file_hash(protocol_path),
            "environment": file_hash(environment_path),
            "trainer": file_hash(project_root / "train_hybrid_open_set.py"),
            "mal_tls_config": file_hash(project_root / "configs/mal_tls2023.json"),
            "hikari_config": file_hash(project_root / "configs/hikari2021.json"),
        },
        "inputs": input_identity,
        "commands": commands,
        "results": [],
        "claim_boundary": protocol["claim_boundary"][args.mode],
    }

    if not args.dry_run:
        required = protocol["required_outputs"]
        for run, command in zip(runs, commands):
            metrics_path = run["output_dir"] / "metrics.json"
            if metrics_path.exists() and not args.reuse:
                raise FileExistsError(
                    f"{metrics_path} exists; use --reuse or a new output root"
                )
            if not metrics_path.exists():
                run["output_dir"].mkdir(parents=True, exist_ok=True)
                subprocess.run(command, cwd=project_root, check=True)
            manifest["results"].append(output_record(run, required))

    manifest["canonical_sha256"] = canonical_hash(manifest)
    args.output_root.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output_root / f"manifest_{args.mode}.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"manifest": str(manifest_path), **manifest}, indent=2))


if __name__ == "__main__":
    main()
