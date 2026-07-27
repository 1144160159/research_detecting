from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def validate_protocol(protocol: Dict[str, Any]) -> None:
    identities = {
        (str(item["scenario"]), int(item["training_seed"]))
        for item in protocol.get("source_model_pairs", [])
    }
    if (
        protocol.get("schema_version")
        != "strict_v4_mdr_parrot_safety_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("selected_algorithm") != "mdr_caeos_v1"
        or int(protocol.get("source_model_pair_count", -1)) != 30
        or len(identities) != 30
        or int(protocol.get("capture_count", -1)) != 320
    ):
        raise ValueError("invalid MDR PARROT protocol")


def validate_deployment(
    path: Path, source: Dict[str, Any], protocol: Dict[str, Any]
) -> bool:
    if not path.exists():
        return False
    value = load(path)
    artifact = path.parent / str(value.get("deployment_artifact", ""))
    if (
        value.get("schema_version")
        != "strict_v4_mdr_parrot_deployment_capture_v1"
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("state") != "complete"
        or value.get("scenario") != source["scenario"]
        or int(value.get("training_seed", -1))
        != int(source["training_seed"])
        or float(value.get("weight", -1.0))
        != float(protocol["mdr_policy"]["augmentation_weight"])
        or value.get("source_split_fingerprint")
        != source["source_split_fingerprint"]
        or value.get("serialization_roundtrip", {}).get("passes")
        is not True
        or not artifact.is_file()
        or file_hash(artifact) != value.get("deployment_artifact_sha256")
    ):
        raise ValueError(f"invalid existing MDR PARROT deployment: {path}")
    return True


def validate_metrics(
    path: Path, source: Dict[str, Any], protocol: Dict[str, Any]
) -> bool:
    if not path.exists():
        return False
    value = load(path)
    if (
        value.get("schema_version")
        != "strict_v4_mdr_parrot_model_pair_metrics_v1"
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("state") != "complete"
        or value.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or value.get("source", {}).get("scenario") != source["scenario"]
        or int(value.get("source", {}).get("training_seed", -1))
        != int(source["training_seed"])
        or int(value.get("capture_count", -1)) != 320
        or int(value.get("failure_count", -1)) != 0
        or value.get(
            "parrot_features_or_labels_used_for_fit_selection_calibration_"
            "or_threshold"
        )
        is not False
    ):
        raise ValueError(f"invalid existing MDR PARROT metrics: {path}")
    return True


def run_command(command: list[str], log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        subprocess.run(
            command,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )


def run(
    protocol: Dict[str, Any],
    protocol_path: Path,
    project_root: Path,
    run_root: Path,
    workers: int,
) -> None:
    validate_protocol(protocol)
    for relative, expected in protocol["implementation_sha256"].items():
        if file_hash(project_root / relative) != expected:
            raise ValueError(
                f"MDR PARROT implementation SHA mismatch: {relative}"
            )
    if int(workers) < 1:
        raise ValueError("MDR PARROT capture workers must be positive")

    def capture_source(index: int, source: Dict[str, Any]) -> str:
        provenance = Path(source["candidate_source_root"]) / "provenance.json"
        if (
            file_hash(provenance)
            != source["candidate_source_provenance_sha256"]
            or file_hash(Path(source["csv"])) != source["csv_sha256"]
            or file_hash(Path(source["config"])) != source["config_sha256"]
            or file_hash(Path(source["opendetect_runtime"]))
            != source["opendetect_runtime_sha256"]
        ):
            raise ValueError("MDR PARROT frozen source identity drifted")
        deployment_dir = (
            run_root
            / "deployments"
            / source["scenario"]
            / f"seed{int(source['training_seed'])}"
        )
        manifest_path = deployment_dir / "capture_manifest.json"
        if validate_deployment(manifest_path, source, protocol):
            return (
                f"retained deployment {index}/30 {source['scenario']}/"
                f"seed{source['training_seed']}"
            )
        if deployment_dir.exists() and any(deployment_dir.iterdir()):
            raise ValueError(
                f"partial MDR PARROT deployment exists: {deployment_dir}"
            )
        command = [
            sys.executable,
            str(project_root / "capture_mdr_parrot_deployment_bundle.py"),
            "--clean-trainer",
            str(project_root / "train_hybrid_open_set.py"),
            "--robust-trainer",
            str(project_root / "train_mdr_caeos_open_set.py"),
            "--capture-dir",
            str(deployment_dir),
            "--suite",
            "ustc_tfc2016",
            "--scenario",
            str(source["scenario"]),
            "--weight",
            str(protocol["mdr_policy"]["augmentation_weight"]),
            "--sample-fraction",
            str(protocol["mdr_policy"]["sample_fraction"]),
            "--training-seed",
            str(source["training_seed"]),
            "--augmentation-seed",
            str(source["augmentation_seed"]),
            "--health-quantile",
            str(protocol["mdr_policy"]["health_quantile"]),
            "--validation-corruption-seed",
            str(source["validation_corruption_seed"]),
            "--source-config",
            str(source["config"]),
            "--",
            *source["base_trainer_arguments"],
        ]
        run_command(command, deployment_dir / "capture.log")
        validate_deployment(manifest_path, source, protocol)
        return (
            f"completed deployment {index}/30 {source['scenario']}/"
            f"seed{source['training_seed']}"
        )

    with ThreadPoolExecutor(max_workers=int(workers)) as executor:
        futures = {
            executor.submit(capture_source, index, source): index
            for index, source in enumerate(
                protocol["source_model_pairs"], start=1
            )
        }
        for future in as_completed(futures):
            print(future.result(), flush=True)

    for index, source in enumerate(protocol["source_model_pairs"], start=1):
        deployment_dir = (
            run_root
            / "deployments"
            / source["scenario"]
            / f"seed{int(source['training_seed'])}"
        )
        output = (
            run_root
            / "evaluations"
            / source["scenario"]
            / f"seed{int(source['training_seed'])}"
            / "model_pair_metrics.json"
        )
        if validate_metrics(output, source, protocol):
            print(
                f"retained evaluation {index}/30 {source['scenario']}/"
                f"seed{source['training_seed']}",
                flush=True,
            )
            continue
        if output.parent.exists() and any(output.parent.iterdir()):
            raise ValueError(
                f"partial MDR PARROT evaluation exists: {output.parent}"
            )
        command = [
            sys.executable,
            str(project_root / "evaluate_mdr_parrot_capture.py"),
            "--protocol",
            str(protocol_path),
            "--scenario",
            str(source["scenario"]),
            "--training-seed",
            str(source["training_seed"]),
            "--deployment-dir",
            str(deployment_dir),
            "--output",
            str(output),
        ]
        run_command(command, output.with_suffix(".log"))
        validate_metrics(output, source, protocol)
        print(
            f"completed evaluation {index}/30 {source['scenario']}/"
            f"seed{source['training_seed']}",
            flush=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    protocol_path = args.protocol.resolve()
    run_root = args.run_root.resolve()
    run_root.mkdir(parents=True, exist_ok=True)
    run(
        load(protocol_path),
        protocol_path,
        args.project_root.resolve(),
        run_root,
        args.workers,
    )


if __name__ == "__main__":
    main()
