from __future__ import annotations

import argparse
import json
import runpy
import sys
import time
from pathlib import Path
from types import FrameType
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
from sklearn.metrics import f1_score

from caeos.mdr_fusion import KnownOnlyHealthCalibration
from caeos.mdr_runtime import MDRRuntime
from capture_pairwise_runtime import (
    build_runtime,
    file_hash,
    run_and_capture,
)
from create_strict_v4_mdr_caeos_design import FAMILIES, FIXED_SEVERITY
from train_hybrid_open_set import apply_test_corruption


def replace_option(arguments: List[str], option: str, value: str) -> None:
    if option not in arguments:
        arguments.extend([option, value])
        return
    index = arguments.index(option)
    if index + 1 >= len(arguments):
        raise ValueError(f"{option} requires a value")
    arguments[index + 1] = value


def run_nested_base_capture(
    trainer_file: str, trainer_arguments: List[str]
) -> Tuple[Dict[str, Any], float]:
    namespace = runpy.run_path(
        trainer_file, run_name="strict_v4_mdr_nested_capture_module"
    )
    wrapper_main = namespace["main"]
    base_main = wrapper_main.__globals__["base"].main
    captured: Dict[str, Any] = {}

    def trace(frame: FrameType, event: str, arg: object):
        if frame.f_code is base_main.__code__:
            if event == "return":
                captured.update(frame.f_locals.copy())
            return trace
        return None

    original_argv = sys.argv[:]
    started = time.perf_counter()
    try:
        sys.argv = [trainer_file, *trainer_arguments]
        sys.settrace(trace)
        wrapper_main()
    finally:
        sys.settrace(None)
        sys.argv = original_argv
    if not captured:
        raise RuntimeError("MDR wrapper did not expose base trainer locals")
    return captured, time.perf_counter() - started


def validation_profile(
    clean_local: Dict[str, Any],
    robust_local: Dict[str, Any],
    clean_runtime,
    robust_runtime,
    corruption_seed: int,
) -> Dict[str, Any]:
    labels = np.asarray(
        robust_local["bundle"].validation.labels.numpy(), dtype=np.int64
    )
    if not np.array_equal(
        labels, clean_local["bundle"].validation.labels.numpy()
    ):
        raise ValueError("clean and robust known-validation labels differ")
    clean_views = [
        np.asarray(view) for view in clean_local["raw_validation_views"]
    ]
    robust_views = [
        np.asarray(view) for view in robust_local["raw_validation_views"]
    ]
    if any(
        not np.array_equal(left, right)
        for left, right in zip(clean_views, robust_views)
    ):
        raise ValueError("clean and robust known-validation views differ")
    clean_prediction = clean_runtime.predict(clean_views)["prediction"]
    robust_prediction = robust_runtime.predict(robust_views)["prediction"]
    clean_f1 = float(
        f1_score(labels, clean_prediction, average="macro", zero_division=0)
    )
    robust_clean_f1 = float(
        f1_score(labels, robust_prediction, average="macro", zero_division=0)
    )
    records = []
    for family_index, family in enumerate(FAMILIES):
        for modality in range(len(robust_views)):
            seed = (
                int(corruption_seed)
                + 1009 * (family_index + 1)
                + 9176 * (modality + 1)
            )
            corrupted, metadata = apply_test_corruption(
                robust_views,
                robust_local["raw_train_views"],
                family,
                modality,
                FIXED_SEVERITY[family],
                seed,
            )
            prediction = robust_runtime.predict(corrupted)["prediction"]
            score = float(
                f1_score(
                    labels,
                    prediction,
                    average="macro",
                    zero_division=0,
                )
            )
            records.append(
                {
                    "family": family,
                    "modality": int(modality),
                    "severity": float(FIXED_SEVERITY[family]),
                    "seed": int(seed),
                    "known_validation_macro_f1": score,
                    "affected_entries": int(metadata["affected_entries"]),
                }
            )
    values = np.asarray(
        [record["known_validation_macro_f1"] for record in records],
        dtype=np.float64,
    )
    return {
        "schema_version": "strict_v4_mdr_known_validation_profile_v1",
        "clean_pairwise_macro_f1": clean_f1,
        "robust_clean_macro_f1": robust_clean_f1,
        "clean_delta": robust_clean_f1 - clean_f1,
        "corrupted_mean_macro_f1": float(values.mean()),
        "corrupted_minimum_macro_f1": float(values.min()),
        "corrupted_minimax_macro_f1": float(
            0.5 * values.mean() + 0.5 * values.min()
        ),
        "record_count": len(records),
        "records": records,
        "known_validation_labels_used": True,
        "unknown_or_test_labels_used": False,
    }


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
    capture_dir.mkdir(parents=True, exist_ok=True)
    clean_dir = capture_dir / "clean_run"
    robust_dir = capture_dir / "robust_run"
    clean_arguments = list(base_arguments)
    replace_option(clean_arguments, "--seed", str(training_seed))
    replace_option(clean_arguments, "--output-dir", str(clean_dir))
    replace_option(clean_arguments, "--test-corruption-kind", "none")
    replace_option(clean_arguments, "--test-corruption-modality", "0")
    replace_option(clean_arguments, "--test-corruption-severity", "0.0")
    replace_option(
        clean_arguments, "--test-corruption-seed", str(validation_corruption_seed)
    )
    clean_local, clean_timings, clean_wall = run_and_capture(
        str(clean_trainer), clean_arguments
    )

    robust_arguments = list(clean_arguments)
    replace_option(robust_arguments, "--output-dir", str(robust_dir))
    robust_arguments.extend(
        [
            "--mdr-augmentation-weight",
            str(weight),
            "--mdr-sample-fraction",
            str(sample_fraction),
            "--mdr-augmentation-seed",
            str(augmentation_seed),
            "--mdr-health-quantile",
            str(health_quantile),
        ]
    )
    robust_local, robust_wall = run_nested_base_capture(
        str(robust_trainer), robust_arguments
    )

    clean_metrics = json.loads(
        (clean_dir / "metrics.json").read_text(encoding="utf-8")
    )
    robust_metrics = json.loads(
        (robust_dir / "metrics.json").read_text(encoding="utf-8")
    )
    if (
        clean_metrics["split_metadata"]["split_fingerprint"]
        != robust_metrics["split_metadata"]["split_fingerprint"]
    ):
        raise ValueError("clean and robust split fingerprints differ")
    clean_runtime = build_runtime(clean_local)
    robust_runtime = build_runtime(robust_local)
    calibration = KnownOnlyHealthCalibration.fit(
        {
            "final_probability": clean_local["validation_evidence"][
                "final_probability"
            ],
            "local_conflict": clean_local["validation_evidence"][
                "local_conflict"
            ],
        },
        {
            "final_probability": robust_local["validation_evidence"][
                "final_probability"
            ],
            "local_conflict": robust_local["validation_evidence"][
                "local_conflict"
            ],
        },
        clean_local["validation_selected_risk"],
        robust_local["validation_selected_risk"],
        robust_local["validation_missing_risk"],
        quantile=health_quantile,
    )
    scales = []
    for view in robust_local["raw_train_views"]:
        scale = np.std(np.asarray(view), axis=0)
        scales.append(
            np.where(np.isfinite(scale) & (scale > 1e-12), scale, 1.0)
        )
    runtime = MDRRuntime(
        clean_runtime=clean_runtime,
        robust_runtime=robust_runtime,
        health_calibration=calibration,
        missing_fraction_thresholds=np.asarray(
            robust_local["missing_thresholds"], dtype=np.float64
        ),
        training_feature_scales=scales,
        clean_threshold=float(clean_local["selected_threshold"]),
        augmentation_weight=float(weight),
        training_seed=int(training_seed),
        augmentation_seed=int(augmentation_seed),
    )
    profile = validation_profile(
        clean_local,
        robust_local,
        clean_runtime,
        robust_runtime,
        validation_corruption_seed,
    )
    artifact = capture_dir / "mdr_runtime.joblib"
    joblib.dump(runtime, artifact, compress=3)
    loaded = joblib.load(artifact)
    source_output = runtime.predict(robust_local["raw_test_views"])
    loaded_output = loaded.predict(robust_local["raw_test_views"])
    roundtrip = {
        "prediction_array_equal": bool(
            np.array_equal(
                source_output["prediction"], loaded_output["prediction"]
            )
        ),
        "risk_max_absolute_difference": float(
            np.max(
                np.abs(source_output["risk"] - loaded_output["risk"])
            )
        ),
        "probability_max_absolute_difference": float(
            np.max(
                np.abs(
                    source_output["probability"]
                    - loaded_output["probability"]
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
        raise RuntimeError("MDR runtime serialization roundtrip failed")
    inputs = capture_dir / "evaluation_inputs.npz"
    np.savez_compressed(
        inputs,
        **{
            **{
                f"view_{index}": np.asarray(view)
                for index, view in enumerate(robust_local["raw_test_views"])
            },
            "test_labels": np.asarray(
                robust_local["test_labels"], dtype=np.int64
            ),
            "test_unknown": np.asarray(
                robust_local["test_unknown"], dtype=bool
            ),
        },
    )
    manifest = {
        "schema_version": "strict_v4_mdr_caeos_runtime_capture_v1",
        "state": "complete",
        "algorithm": "mdr_caeos_v1",
        "task": {"suite": suite, "scenario": scenario},
        "weight": float(weight),
        "sample_fraction": float(sample_fraction),
        "training_seed": int(training_seed),
        "augmentation_seed": int(augmentation_seed),
        "health_quantile": float(health_quantile),
        "clean_trainer_sha256": file_hash(clean_trainer),
        "robust_trainer_sha256": file_hash(robust_trainer),
        "clean_trainer_arguments": clean_arguments,
        "robust_trainer_arguments": robust_arguments,
        "clean_phase_timings": clean_timings,
        "clean_capture_wall_seconds": float(clean_wall),
        "robust_capture_wall_seconds": float(robust_wall),
        "split_fingerprint": clean_metrics["split_metadata"][
            "split_fingerprint"
        ],
        "runtime_artifact": artifact.name,
        "runtime_artifact_sha256": file_hash(artifact),
        "runtime_artifact_bytes": artifact.stat().st_size,
        "evaluation_inputs": inputs.name,
        "evaluation_inputs_sha256": file_hash(inputs),
        "evaluation_inputs_contain_test_labels_for_evaluation_only": True,
        "runtime_evidence": runtime.evidence(),
        "known_validation_profile": profile,
        "roundtrip": roundtrip,
        "unknown_or_test_labels_used_for_training_selection_or_calibration": False,
    }
    (capture_dir / "capture_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


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
    manifest = capture(
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
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
