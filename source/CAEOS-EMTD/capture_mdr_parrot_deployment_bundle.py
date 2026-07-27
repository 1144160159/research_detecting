from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np

import capture_mdr_caeos_runtime as base_capture
from caeos.mdr_deployment import MDRDeploymentBundle
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


def source_benign_metrics(
    output: Dict[str, np.ndarray], benign_index: int
) -> Dict[str, Any]:
    prediction = np.asarray(output["prediction"], dtype=np.int64)
    risk = np.asarray(output["risk"], dtype=np.float64)
    threshold = np.asarray(output["threshold"], dtype=np.float64)
    if (
        prediction.ndim != 1
        or risk.shape != prediction.shape
        or threshold.shape != prediction.shape
        or not np.isfinite(risk).all()
        or not np.isfinite(threshold).all()
        or np.any(threshold <= 0.0)
        or not len(prediction)
    ):
        raise ValueError("invalid MDR source-benign output")
    return {
        "row_count": int(len(prediction)),
        "false_alert_rate": float(np.mean(prediction != int(benign_index))),
        "known_attack_assignment_rate": float(
            np.mean(
                (risk <= threshold)
                & (prediction != int(benign_index))
            )
        ),
        "reject_rate": float(np.mean(risk > threshold)),
        "normalized_risk_quantiles": {
            name: float(np.quantile(risk / threshold, quantile))
            for name, quantile in (
                ("p50", 0.50),
                ("p95", 0.95),
                ("p99", 0.99),
            )
        },
    }


def capture(
    *,
    clean_trainer: Path,
    robust_trainer: Path,
    capture_dir: Path,
    base_arguments: List[str],
    suite: str,
    scenario: str,
    weight: float,
    sample_fraction: float,
    training_seed: int,
    augmentation_seed: int,
    health_quantile: float,
    validation_corruption_seed: int,
    source_config: Path,
) -> Dict[str, Any]:
    held: Dict[str, Dict[str, Any]] = {}
    original_clean = base_capture.run_and_capture
    original_robust = base_capture.run_nested_base_capture

    def wrapped_clean(*args, **kwargs):
        result = original_clean(*args, **kwargs)
        held["clean"] = result[0]
        return result

    def wrapped_robust(*args, **kwargs):
        result = original_robust(*args, **kwargs)
        held["robust"] = result[0]
        return result

    base_capture.run_and_capture = wrapped_clean
    base_capture.run_nested_base_capture = wrapped_robust
    try:
        base_manifest = base_capture.capture(
            clean_trainer,
            robust_trainer,
            capture_dir,
            base_arguments,
            suite=suite,
            scenario=scenario,
            weight=weight,
            sample_fraction=sample_fraction,
            training_seed=training_seed,
            augmentation_seed=augmentation_seed,
            health_quantile=health_quantile,
            validation_corruption_seed=validation_corruption_seed,
        )
    finally:
        base_capture.run_and_capture = original_clean
        base_capture.run_nested_base_capture = original_robust
    if set(held) != {"clean", "robust"}:
        raise RuntimeError("MDR deployment capture locals are incomplete")
    clean_bundle = held["clean"]["bundle"]
    robust_bundle = held["robust"]["bundle"]
    if (
        clean_bundle.preprocessing != robust_bundle.preprocessing
        or list(clean_bundle.modality_names)
        != list(robust_bundle.modality_names)
        or list(clean_bundle.class_names) != list(robust_bundle.class_names)
        or int(clean_bundle.benign_index) != int(robust_bundle.benign_index)
    ):
        raise ValueError("clean and robust MDR deployment metadata differ")
    preprocessing = robust_bundle.preprocessing
    modality_names = tuple(robust_bundle.modality_names)
    modalities = {
        name: tuple(preprocessing["modalities"][name])
        for name in modality_names
    }
    processor_states = {
        name: dict(preprocessing["processors"][name])
        for name in modality_names
    }
    runtime_path = capture_dir / base_manifest["runtime_artifact"]
    runtime = joblib.load(runtime_path)
    split_value = base_manifest["split_fingerprint"]
    split_fingerprint = str(
        split_value["combined"]
        if isinstance(split_value, dict)
        else split_value
    )
    bundle = MDRDeploymentBundle(
        runtime=runtime,
        modality_names=modality_names,
        modalities=modalities,
        processor_states=processor_states,
        class_names=tuple(robust_bundle.class_names),
        benign_index=int(robust_bundle.benign_index),
        source_config_sha256=file_hash(source_config),
        source_split_fingerprint=split_fingerprint,
    )
    if bundle.evidence()["feature_count"] != 56:
        raise ValueError("MDR PARROT deployment requires 56 features")
    artifact = capture_dir / "mdr_deployment_bundle.joblib"
    joblib.dump(bundle, artifact, compress=3)
    restored = joblib.load(artifact)
    inputs_path = capture_dir / base_manifest["evaluation_inputs"]
    with np.load(inputs_path, allow_pickle=False) as payload:
        view_names = sorted(
            (name for name in payload.files if name.startswith("view_")),
            key=lambda name: int(name.rsplit("_", 1)[1]),
        )
        views = [np.asarray(payload[name]) for name in view_names]
        labels = np.asarray(payload["test_labels"], dtype=np.int64)
        unknown = np.asarray(payload["test_unknown"], dtype=bool)
    original_output = runtime.predict(views)
    restored_output = restored.predict_views(views)
    roundtrip = {
        "prediction_array_equal": bool(
            np.array_equal(
                original_output["prediction"],
                restored_output["prediction"],
            )
        ),
        "risk_max_absolute_difference": float(
            np.max(
                np.abs(
                    original_output["risk"] - restored_output["risk"]
                )
            )
        ),
        "probability_max_absolute_difference": float(
            np.max(
                np.abs(
                    original_output["probability"]
                    - restored_output["probability"]
                )
            )
        ),
    }
    roundtrip["passes"] = bool(
        roundtrip["prediction_array_equal"]
        and roundtrip["risk_max_absolute_difference"] <= 1e-12
        and roundtrip["probability_max_absolute_difference"] <= 1e-12
    )
    if not roundtrip["passes"]:
        raise RuntimeError("MDR deployment serialization roundtrip failed")
    benign_mask = (~unknown) & (labels == bundle.benign_index)
    if not np.any(benign_mask):
        raise ValueError("source-domain benign reference is empty")
    source_metrics = source_benign_metrics(
        restored.predict_views([view[benign_mask] for view in views]),
        bundle.benign_index,
    )
    base_manifest_path = capture_dir / "base_capture_manifest.json"
    (capture_dir / "capture_manifest.json").replace(base_manifest_path)
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_parrot_deployment_capture_v1",
        "state": "complete",
        "algorithm": "mdr_caeos_v1",
        "suite": suite,
        "scenario": scenario,
        "training_seed": int(training_seed),
        "augmentation_seed": int(augmentation_seed),
        "weight": float(weight),
        "deployment_artifact": artifact.name,
        "deployment_artifact_sha256": file_hash(artifact),
        "deployment_artifact_bytes": artifact.stat().st_size,
        "base_runtime_artifact": base_manifest["runtime_artifact"],
        "base_runtime_artifact_sha256": base_manifest[
            "runtime_artifact_sha256"
        ],
        "base_capture_manifest": base_manifest_path.name,
        "base_capture_manifest_sha256": file_hash(base_manifest_path),
        "evaluation_inputs": base_manifest["evaluation_inputs"],
        "evaluation_inputs_sha256": base_manifest[
            "evaluation_inputs_sha256"
        ],
        "source_config_sha256": file_hash(source_config),
        "source_split_fingerprint": split_fingerprint,
        "deployment_evidence": bundle.evidence(),
        "serialization_roundtrip": roundtrip,
        "source_benign_reference": source_metrics,
        "source_benign_labels_used_for_final_reference_only": True,
        "parrot_labels_used_for_fit_selection_calibration_or_threshold": False,
        "formal_parrot_metric_count_at_capture": 0,
        "storage_policy": "gpu_private_do_not_publish",
    }
    value["manifest_sha256"] = canonical_hash(value)
    (capture_dir / "capture_manifest.json").write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean-trainer", type=Path, required=True)
    parser.add_argument("--robust-trainer", type=Path, required=True)
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--weight", type=float, required=True)
    parser.add_argument("--sample-fraction", type=float, required=True)
    parser.add_argument("--training-seed", type=int, required=True)
    parser.add_argument("--augmentation-seed", type=int, required=True)
    parser.add_argument("--health-quantile", type=float, required=True)
    parser.add_argument(
        "--validation-corruption-seed", type=int, required=True
    )
    parser.add_argument("--source-config", type=Path, required=True)
    parser.add_argument("trainer_arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    trainer_arguments = list(args.trainer_arguments)
    if trainer_arguments and trainer_arguments[0] == "--":
        trainer_arguments = trainer_arguments[1:]
    if not trainer_arguments:
        raise ValueError("trainer arguments are required after --")
    value = capture(
        clean_trainer=args.clean_trainer,
        robust_trainer=args.robust_trainer,
        capture_dir=args.capture_dir,
        base_arguments=trainer_arguments,
        suite=args.suite,
        scenario=args.scenario,
        weight=args.weight,
        sample_fraction=args.sample_fraction,
        training_seed=args.training_seed,
        augmentation_seed=args.augmentation_seed,
        health_quantile=args.health_quantile,
        validation_corruption_seed=args.validation_corruption_seed,
        source_config=args.source_config,
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
