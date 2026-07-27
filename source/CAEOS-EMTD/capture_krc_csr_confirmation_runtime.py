from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np
from sklearn.metrics import f1_score, roc_auc_score

from caeos.krc_csr_runtime import KRCCSRRuntime
from capture_csr_caeos_runtime import capture_csr
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


def certificate(capture_dir: Path) -> Dict[str, Any]:
    evidence_path = capture_dir / "clean_run" / "evidence_package.npz"
    scores_path = capture_dir / "robust_run" / "scores.npz"
    with np.load(evidence_path, allow_pickle=False) as archive:
        probability = np.asarray(
            archive["validation_final_probability"], dtype=np.float64
        )
        risk = np.asarray(
            archive["validation_selected_risk"], dtype=np.float64
        )
    with np.load(scores_path, allow_pickle=False) as archive:
        labels = np.asarray(archive["validation_labels"], dtype=np.int64)
    selected = np.arange(len(labels), dtype=np.int64)[::2]
    prediction = probability[selected].argmax(axis=1)
    errors = prediction != labels[selected]
    macro_f1 = float(
        f1_score(
            labels[selected],
            prediction,
            average="macro",
            zero_division=0,
        )
    )
    error_auroc = (
        float(roc_auc_score(errors.astype(np.int64), risk[selected]))
        if len(np.unique(errors)) == 2
        else None
    )
    enabled = bool(
        macro_f1 >= 0.9
        and error_auroc is not None
        and error_auroc >= 0.7
    )
    return {
        "schema_version": "strict_v4_krc_csr_certificate_v1",
        "partition": {
            "rule": "even_indices_existing_csr_calibration_partition",
            "total_count": int(len(labels)),
            "calibration_count": int(len(selected)),
        },
        "calibration_known_macro_f1": macro_f1,
        "calibration_error_detection_auroc": error_auroc,
        "calibration_known_macro_f1_minimum": 0.9,
        "calibration_error_detection_auroc_minimum": 0.7,
        "routing_enabled": enabled,
        "test_arrays_read": [],
        "unknown_or_test_labels_used": False,
        "known_validation_labels_used": True,
    }


def krc_safety_profile(
    source: Dict[str, Any], certificate_value: Dict[str, Any]
) -> Dict[str, Any]:
    profile = dict(source["safety_profile"])
    profile["schema_version"] = (
        "strict_v4_krc_csr_known_validation_safety_profile_v1"
    )
    profile["certificate_routing_enabled"] = bool(
        certificate_value["routing_enabled"]
    )
    if not certificate_value["routing_enabled"]:
        profile.update(
            {
                "active_count": 0,
                "active_rate": 0.0,
                "missing_active_count": 0,
                "conflict_active_count": 0,
                "disagreement_active_count": 0,
                "clean_delta": 0.0,
                "prediction_array_equal_pairwise": True,
                "probability_max_absolute_difference": 0.0,
                "inactive_risk_max_absolute_difference": 0.0,
            }
        )
    return profile


def capture(
    clean_trainer: Path,
    robust_trainer: Path,
    capture_dir: Path,
    base_arguments: List[str],
    *,
    suite: str,
    scenario: str,
    weight: float,
    sample_fraction: float,
    training_seed: int,
    augmentation_seed: int,
    health_quantile: float,
    validation_corruption_seed: int,
) -> Dict[str, Any]:
    if float(weight) != 0.5:
        raise ValueError("KRC-CSR requires fixed augmentation weight 0.5")
    source = capture_csr(
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
    source_manifest_path = capture_dir / "csr_capture_manifest.json"
    source_manifest_path.write_text(
        json.dumps(source, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    source_artifact = capture_dir / source["runtime_artifact"]
    base_runtime = joblib.load(source_artifact)
    certificate_value = certificate(capture_dir)
    runtime = KRCCSRRuntime(
        base_runtime=base_runtime,
        routing_enabled=bool(certificate_value["routing_enabled"]),
        calibration_known_macro_f1=float(
            certificate_value["calibration_known_macro_f1"]
        ),
        calibration_error_detection_auroc=certificate_value[
            "calibration_error_detection_auroc"
        ],
    )
    artifact = capture_dir / "krc_csr_runtime.joblib"
    joblib.dump(runtime, artifact, compress=3)
    loaded = joblib.load(artifact)
    inputs_path = capture_dir / source["evaluation_inputs"]
    with np.load(inputs_path, allow_pickle=False) as archive:
        views = [
            np.asarray(archive[f"view_{index}"])
            for index in range(runtime.evidence()["modality_count"])
        ]
    before = runtime.predict(views)
    after = loaded.predict(views)
    roundtrip = {
        "prediction_array_equal": bool(
            np.array_equal(before["prediction"], after["prediction"])
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
        raise RuntimeError("KRC-CSR runtime serialization roundtrip failed")
    value = dict(source)
    value.update(
        {
            "schema_version": "strict_v4_krc_csr_runtime_capture_v1",
            "state": "complete",
            "algorithm": "krc_csr_caeos_v1",
            "runtime_revision": "known_only_reliability_certificate_v1",
            "source_csr_capture_manifest_file_sha256": file_hash(
                source_manifest_path
            ),
            "source_csr_runtime_artifact_sha256": file_hash(
                source_artifact
            ),
            "runtime_artifact": artifact.name,
            "runtime_artifact_sha256": file_hash(artifact),
            "runtime_artifact_bytes": artifact.stat().st_size,
            "runtime_evidence": runtime.evidence(),
            "known_only_certificate": certificate_value,
            "safety_profile": krc_safety_profile(
                source, certificate_value
            ),
            "roundtrip": roundtrip,
            "test_labels_read_for_certificate_or_roundtrip": False,
            "unknown_or_test_labels_used_for_training_selection_or_calibration": (
                False
            ),
        }
    )
    value["manifest_sha256"] = canonical_hash(value)
    (capture_dir / "capture_manifest.json").write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
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
    parser.add_argument("--sample-fraction", type=float, default=0.25)
    parser.add_argument("--training-seed", type=int, required=True)
    parser.add_argument("--augmentation-seed", type=int, required=True)
    parser.add_argument("--health-quantile", type=float, default=0.99)
    parser.add_argument("--validation-corruption-seed", type=int, required=True)
    parser.add_argument("trainer_arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    arguments = list(args.trainer_arguments)
    if arguments and arguments[0] == "--":
        arguments = arguments[1:]
    if not arguments:
        raise ValueError("base trainer arguments are required after --")
    value = capture(
        args.clean_trainer.resolve(),
        args.robust_trainer.resolve(),
        args.capture_dir.resolve(),
        arguments,
        suite=args.suite,
        scenario=args.scenario,
        weight=args.weight,
        sample_fraction=args.sample_fraction,
        training_seed=args.training_seed,
        augmentation_seed=args.augmentation_seed,
        health_quantile=args.health_quantile,
        validation_corruption_seed=args.validation_corruption_seed,
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
