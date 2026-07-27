from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_result(path: Path, source: dict[str, Any]) -> None:
    metrics = load_json(path / "metrics.json")
    if (
        metrics.get("schema_version") != "strict_v4_vos_metrics_v1"
        or metrics.get("model") != "vos"
        or metrics.get("method") != "vos_energy"
        or int(metrics.get("seed", -1)) != int(source["seed"])
        or metrics["split_metadata"]["split_fingerprint"]["combined"]
        != source["split_fingerprint"]
        or metrics.get("selection_evidence", {}).get(
            "unknown_or_test_labels_used_for_fitting_or_selection"
        )
        is not False
    ):
        raise ValueError(f"VOS result validation failed: {path}")
    for name in ("scores.npz", "model.pt", "provenance.json"):
        if not (path / name).is_file():
            raise FileNotFoundError(f"VOS result artifact missing: {path / name}")


def command_for(
    protocol: dict[str, Any], source: dict[str, Any], output: Path
) -> list[str]:
    frozen = protocol["frozen_hyperparameters"]
    training = source["training_source"]
    command = [
        sys.executable,
        "train_vos_open_set.py",
        "--csv",
        str(training["csv"]),
        "--config",
        str(training["config"]),
        "--unknown-classes",
        str(training["unknown_classes"]),
        "--benign-class",
        str(training["benign_class"]),
        "--split-strategy",
        str(training["split_strategy"]),
        "--max-per-class",
        str(training["max_per_class"]),
        "--chunksize",
        str(training["chunksize"]),
        "--seed",
        str(source["seed"]),
        "--output-dir",
        str(output),
        "--device",
        "cuda",
        "--num-workers",
        "4",
    ]
    option_names = {
        "epochs": "--epochs",
        "start_epoch": "--start-epoch",
        "batch_size": "--batch-size",
        "hidden_dim": "--hidden-dim",
        "embedding_dim": "--embedding-dim",
        "dropout": "--dropout",
        "learning_rate": "--learning-rate",
        "weight_decay": "--weight-decay",
        "queue_size": "--queue-size",
        "sample_from": "--sample-from",
        "select": "--select",
        "covariance_ridge": "--covariance-ridge",
        "outlier_loss_weight": "--outlier-loss-weight",
        "known_acceptance": "--known-acceptance",
        "sampling": "--sampling",
    }
    for name, option in option_names.items():
        command.extend([option, str(frozen[name])])
    return command


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    args = parser.parse_args()
    protocol = load_json(args.protocol)
    if (
        protocol.get("schema_version") != "strict_v4_vos_pilot_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("VOS matrix protocol validation failed")
    active = {
        "caeos/vos.py": args.project_root / "caeos" / "vos.py",
        "train_vos_open_set.py": args.project_root / "train_vos_open_set.py",
        "run_strict_v4_vos_matrix.py": Path(__file__),
    }
    for name, path in active.items():
        if file_hash(path) != protocol["implementation_sha256"][name]:
            raise ValueError(f"VOS active implementation SHA mismatch: {name}")
    args.output_root.mkdir(parents=True, exist_ok=True)
    lock = args.output_root / "runner.lock.d"
    try:
        lock.mkdir()
    except FileExistsError:
        raise RuntimeError("VOS matrix runner is already active")
    completed = 0
    try:
        for source in protocol["source_registry"]:
            for name in ("mlp", "comparator"):
                path = Path(source[f"{name}_metrics"])
                if file_hash(path) != source[f"{name}_metrics_sha256"]:
                    raise ValueError(f"VOS frozen source SHA mismatch: {path}")
            output = (
                args.output_root
                / source["suite"]
                / f"{source['scenario']}_seed{source['seed']}_vos"
            )
            if (output / "metrics.json").is_file():
                validate_result(output, source)
                completed += 1
                continue
            output.mkdir(parents=True, exist_ok=True)
            command = command_for(protocol, source, output.resolve())
            provenance = {
                "schema_version": "strict_v4_vos_provenance_v1",
                "protocol_manifest_sha256": protocol["manifest_sha256"],
                "task": {
                    "suite": source["suite"],
                    "scenario": source["scenario"],
                    "seed": source["seed"],
                },
                "command": command,
                "source_split_fingerprint": source["split_fingerprint"],
                "unknown_or_test_labels_used_for_fitting_or_selection": False,
            }
            (output / "provenance.json").write_text(
                json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with (output / "run.log").open("a", encoding="utf-8") as log:
                try:
                    subprocess.run(
                        command,
                        cwd=args.project_root,
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        check=True,
                    )
                except subprocess.CalledProcessError as error:
                    (output / "failure.json").write_text(
                        json.dumps(
                            {"returncode": error.returncode, "command": command},
                            indent=2,
                        )
                        + "\n",
                        encoding="utf-8",
                    )
                    raise
            validate_result(output, source)
            completed += 1
            print(
                f"vos_completed={completed}/{len(protocol['source_registry'])}",
                flush=True,
            )
        if completed != int(protocol["expected_runs"]):
            raise RuntimeError("VOS matrix is incomplete")
        (args.output_root / "execution_complete").touch()
    finally:
        lock.rmdir()


if __name__ == "__main__":
    main()
