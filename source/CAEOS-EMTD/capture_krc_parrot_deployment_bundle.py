from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Dict

import joblib
import numpy as np

from caeos.krc_deployment import KRCDeploymentBundle
from capture_mdr_parrot_deployment_bundle import source_benign_metrics
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
import train_hybrid_open_set as trainer


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def trainer_namespace(arguments: list[str], project_root: Path):
    original = sys.argv[:]
    try:
        sys.argv = ["train_hybrid_open_set.py", *arguments]
        args = trainer.parse_arguments()
    finally:
        sys.argv = original
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = project_root / config_path
    with config_path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    unknown = [
        value.strip()
        for value in str(args.unknown_classes).split(",")
        if value.strip()
    ]
    bundle = trainer.prepare_tabular_open_set(
        args.csv,
        config,
        unknown,
        args.benign_class,
        args.max_per_class,
        args.chunksize,
        args.seed,
        split_strategy=args.split_strategy,
    )
    return args, config_path.resolve(), bundle


def capture(
    *,
    source_capture_dir: Path,
    project_root: Path,
    output_dir: Path,
) -> Dict[str, Any]:
    manifest_path = source_capture_dir / "capture_manifest.json"
    execution_path = source_capture_dir / "capture_execution.json"
    manifest = load(manifest_path)
    execution = load(execution_path)
    runtime_path = source_capture_dir / str(manifest.get("runtime_artifact", ""))
    inputs_path = source_capture_dir / str(manifest.get("evaluation_inputs", ""))
    if (
        manifest.get("schema_version")
        != "strict_v4_krc_csr_runtime_capture_v1"
        or manifest.get("manifest_sha256") != canonical_hash(manifest)
        or manifest.get("state") != "complete"
        or manifest.get("algorithm") != "krc_csr_caeos_v1"
        or manifest.get("roundtrip", {}).get("passes") is not True
        or execution.get("schema_version")
        != "strict_v4_krc_csr_capture_execution_v1"
        or execution.get("manifest_sha256") != canonical_hash(execution)
        or execution.get("capture_manifest_file_sha256")
        != file_hash(manifest_path)
        or file_hash(runtime_path) != manifest.get("runtime_artifact_sha256")
        or file_hash(inputs_path) != manifest.get("evaluation_inputs_sha256")
    ):
        raise ValueError("invalid frozen KRC confirmation capture")
    args, config_path, data = trainer_namespace(
        list(manifest["clean_trainer_arguments"]), project_root
    )
    preprocessing = data.preprocessing
    runtime = joblib.load(runtime_path)
    split = manifest["split_fingerprint"]
    split_fingerprint = str(
        split["combined"] if isinstance(split, dict) else split
    )
    deployment = KRCDeploymentBundle(
        runtime=runtime,
        modality_names=tuple(data.modality_names),
        modalities={
            str(name): tuple(columns)
            for name, columns in preprocessing["modalities"].items()
        },
        processor_states={
            str(name): {
                key: list(values) for key, values in state.items()
            }
            for name, state in preprocessing["processors"].items()
        },
        class_names=tuple(data.class_names),
        benign_index=int(data.benign_index),
        selected_threshold=float(runtime.clean_threshold),
        risk_policy_name=str(args.risk_policy_name),
        source_config_sha256=file_hash(config_path),
        source_split_fingerprint=split_fingerprint,
        source_capture_manifest_sha256=manifest["manifest_sha256"],
    )
    if deployment.evidence()["feature_count"] != 56:
        raise ValueError("KRC PARROT deployment requires 56 features")
    prepared_views = [np.asarray(view) for view in trainer.views(data.test)]
    with np.load(inputs_path, allow_pickle=False) as archive:
        frozen_views = [
            np.asarray(archive[f"view_{index}"])
            for index in range(len(prepared_views))
        ]
        labels = np.asarray(archive["test_labels"], dtype=np.int64)
        unknown = np.asarray(archive["test_unknown"], dtype=bool)
    preprocessing_replay = {
        "view_count": len(prepared_views),
        "all_view_arrays_equal": bool(
            len(prepared_views) == len(frozen_views)
            and all(
                np.array_equal(left, right)
                for left, right in zip(prepared_views, frozen_views)
            )
        ),
    }
    if not preprocessing_replay["all_view_arrays_equal"]:
        raise ValueError("reconstructed preprocessing does not match KRC inputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = output_dir / "krc_deployment_bundle.joblib"
    joblib.dump(deployment, artifact, compress=3)
    restored = joblib.load(artifact)
    before = runtime.predict(frozen_views)
    after = restored.predict_views(frozen_views)
    roundtrip = {
        "prediction_array_equal": bool(
            np.array_equal(before["prediction"], after["closed_set_index"])
        ),
        "risk_max_absolute_difference": float(
            np.max(np.abs(before["risk"] - after["risk"]))
        ),
        "probability_max_absolute_difference": float(
            np.max(np.abs(before["probability"] - after["probability"]))
        ),
    }
    roundtrip["passes"] = bool(
        roundtrip["prediction_array_equal"]
        and roundtrip["risk_max_absolute_difference"] <= 1e-12
        and roundtrip["probability_max_absolute_difference"] <= 1e-12
    )
    if not roundtrip["passes"]:
        raise ValueError("KRC deployment serialization roundtrip failed")
    benign = (~unknown) & (labels == deployment.benign_index)
    if not np.any(benign):
        raise ValueError("source-domain benign reference is empty")
    source_output = restored.predict_views(
        [view[benign] for view in frozen_views]
    )
    source_output["prediction"] = source_output["closed_set_index"]
    source_output["threshold"] = np.full(
        len(source_output["risk"]), deployment.selected_threshold
    )
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_parrot_deployment_capture_v1",
        "state": "complete",
        "algorithm": "krc_csr_caeos_v1",
        "suite": manifest["task"]["suite"],
        "scenario": manifest["task"]["scenario"],
        "training_seed": int(manifest["training_seed"]),
        "source_capture_dir": str(source_capture_dir.resolve()),
        "source_capture_manifest_file_sha256": file_hash(manifest_path),
        "source_capture_execution_file_sha256": file_hash(execution_path),
        "source_runtime_artifact_sha256": file_hash(runtime_path),
        "source_evaluation_inputs_sha256": file_hash(inputs_path),
        "source_split_fingerprint": split_fingerprint,
        "source_config_sha256": file_hash(config_path),
        "deployment_artifact": artifact.name,
        "deployment_artifact_sha256": file_hash(artifact),
        "deployment_artifact_bytes": artifact.stat().st_size,
        "deployment_evidence": deployment.evidence(),
        "preprocessing_replay": preprocessing_replay,
        "serialization_roundtrip": roundtrip,
        "source_benign_reference": source_benign_metrics(
            source_output, deployment.benign_index
        ),
        "source_benign_labels_used_for_final_reference_only": True,
        "model_refit_performed": False,
        "parrot_used_for_fit_selection_calibration_or_threshold": False,
        "payload_decryption_used": False,
    }
    value["manifest_sha256"] = canonical_hash(value)
    (output_dir / "capture_manifest.json").write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-capture-dir", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    value = capture(
        source_capture_dir=args.source_capture_dir.resolve(),
        project_root=args.project_root.resolve(),
        output_dir=args.output_dir.resolve(),
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
