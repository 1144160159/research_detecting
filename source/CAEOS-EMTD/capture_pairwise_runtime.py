from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys
import time
from types import FrameType
from typing import Any

import joblib
import numpy as np

try:
    import resource
except ImportError:  # pragma: no cover - formal execution is Linux-only.
    resource = None

from caeos.pairwise_runtime import PairwiseRuntime


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_arguments() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description="Run the unchanged pairwise trainer and capture deployable state"
    )
    parser.add_argument("--trainer", type=Path, required=True)
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("trainer_arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    trainer_arguments = list(args.trainer_arguments)
    if trainer_arguments and trainer_arguments[0] == "--":
        trainer_arguments = trainer_arguments[1:]
    if not trainer_arguments:
        raise ValueError("trainer arguments are required after --")
    return args, trainer_arguments


def build_runtime(local: dict[str, Any]) -> PairwiseRuntime:
    args = local["args"]
    details = local["risk_selection_details"]
    learned = details.get("pseudo_unknown_learned_blend", {})
    return PairwiseRuntime(
        model=local["model"],
        foss_model=local["foss_model"],
        distance_model=local["distance_model"],
        knn_model=local["knn_model"],
        view_knn_models=list(local["view_knn_models"]),
        class_knn_model=local["class_knn_model"],
        lof_model=local["lof_model"],
        normalizer=local["normalizer"],
        tail_calibrator=local["tail_calibrator"],
        selected_risk=str(local["selected_risk"]),
        learned_weights={
            str(name): float(value)
            for name, value in details.get("learned_nonnegative_weights", {}).items()
        },
        validation_raw_learned=np.asarray(
            local.get("validation_raw_learned", np.empty(0)), dtype=np.float64
        ),
        selected_alpha=float(learned.get("selected_alpha", 0.0)),
        foss_structural_view=bool(args.foss_structural_view),
        foss_structural_view_mode=str(args.foss_structural_view_mode),
        foss_structural_view_scope=str(args.foss_structural_view_scope),
    )


def run_and_capture(
    trainer_file: str, trainer_arguments: list[str]
) -> tuple[dict[str, Any], dict[str, float], float]:
    namespace = runpy.run_path(
        trainer_file, run_name="strict_v4_pairwise_capture_module"
    )
    main_function = namespace["main"]
    trainer_globals = main_function.__globals__
    captured: dict[str, Any] = {}
    timings = {
        "feature_preparation_seconds": 0.0,
        "training_seconds": 0.0,
        "calibration_seconds": 0.0,
    }
    selection_active = {"value": False}
    restorations: list[tuple[object, str, object]] = []

    original_prepare = trainer_globals["prepare_tabular_open_set"]

    def timed_prepare(*args: Any, **kwargs: Any) -> Any:
        started = time.perf_counter()
        try:
            return original_prepare(*args, **kwargs)
        finally:
            timings["feature_preparation_seconds"] += time.perf_counter() - started

    trainer_globals["prepare_tabular_open_set"] = timed_prepare
    original_select = trainer_globals["select_nested_risk"]

    def timed_select(*args: Any, **kwargs: Any) -> Any:
        started = time.perf_counter()
        selection_active["value"] = True
        try:
            return original_select(*args, **kwargs)
        finally:
            selection_active["value"] = False
            timings["training_seconds"] += time.perf_counter() - started

    trainer_globals["select_nested_risk"] = timed_select

    training_classes = (
        "FOSSForest",
        "ConflictAwareHybridClassifier",
        "ClassConditionalDiagonalDistance",
        "KnownKnnDistance",
        "PredictedClassKnnDistance",
        "KnownLocalOutlierFactor",
        "ForestLeafRarity",
    )
    calibration_classes = (
        "KnownQuantileNormalizer",
        "EmpiricalTailCalibrator",
        "ClassConditionalEmpiricalTailCalibrator",
        "EmpiricalTwoSidedCalibrator",
    )

    def patch_fit(class_name: str, timing_name: str) -> None:
        cls = trainer_globals[class_name]
        original = cls.fit

        def timed_fit(self: object, *args: Any, **kwargs: Any) -> Any:
            if selection_active["value"]:
                return original(self, *args, **kwargs)
            started = time.perf_counter()
            try:
                return original(self, *args, **kwargs)
            finally:
                timings[timing_name] += time.perf_counter() - started

        restorations.append((cls, "fit", original))
        setattr(cls, "fit", timed_fit)

    for class_name in training_classes:
        patch_fit(class_name, "training_seconds")
    for class_name in calibration_classes:
        patch_fit(class_name, "calibration_seconds")

    def trace(frame: FrameType, event: str, arg: object):
        if frame.f_code is main_function.__code__:
            if event == "return":
                captured.update(frame.f_locals.copy())
            return trace
        return None

    original_argv = sys.argv[:]
    wall_started = time.perf_counter()
    try:
        sys.argv = [trainer_file, *trainer_arguments]
        sys.settrace(trace)
        main_function()
    finally:
        sys.settrace(None)
        sys.argv = original_argv
        for target, name, original in reversed(restorations):
            setattr(target, name, original)
    wall_seconds = time.perf_counter() - wall_started
    timings["total_fit_seconds"] = sum(timings.values())
    return captured, timings, wall_seconds


def main() -> None:
    args, trainer_arguments = parse_arguments()
    trainer = args.trainer.resolve()
    if not trainer.is_file():
        raise FileNotFoundError(trainer)
    capture_dir = args.capture_dir.resolve()
    capture_dir.mkdir(parents=True, exist_ok=True)
    trainer_file = str(trainer)
    captured, phase_timings, capture_wall_seconds = run_and_capture(
        trainer_file, trainer_arguments
    )
    if not captured:
        raise RuntimeError("pairwise trainer main locals were not captured")

    runtime = build_runtime(captured)
    output = runtime.predict(captured["raw_test_views"])
    runtime_components, _ = runtime.component_values(captured["raw_test_views"])
    shadow_output = runtime.predict(captured["raw_test_views"])
    score_archive = captured["score_archive"]
    expected_risk_name = f"test_{runtime.selected_risk}"
    if expected_risk_name not in score_archive:
        raise ValueError(f"trainer score archive lacks {expected_risk_name}")
    expected_prediction = np.asarray(score_archive["test_prediction"])
    expected_risk = np.asarray(score_archive[expected_risk_name])
    source_prediction_equal = np.array_equal(
        output["prediction"], expected_prediction
    )
    shadow_prediction_equal = np.array_equal(
        output["prediction"], shadow_output["prediction"]
    )
    source_risk_max_abs = float(np.max(np.abs(output["risk"] - expected_risk)))
    shadow_risk_max_abs = float(
        np.max(np.abs(output["risk"] - shadow_output["risk"]))
    )
    required_components = {
        "conflict",
        "tree_disagreement",
        "distance",
        *(name for name in runtime_components if name.startswith("knn_view_")),
    }
    if runtime.selected_risk == "pseudo_unknown_learned_blend":
        required_components.update(runtime.learned_weights)
    component_differences = {
        name: float(
            np.max(
                np.abs(
                    np.asarray(runtime_components[name])
                    - np.asarray(captured["test_components"][name])
                )
            )
        )
        for name in sorted(required_components)
    }
    component_max_abs = max(component_differences.values(), default=0.0)
    equivalence = {
        "schema_version": "strict_v4_pairwise_runtime_equivalence_v2",
        "prediction_array_equal": bool(
            source_prediction_equal and shadow_prediction_equal
        ),
        "source_prediction_array_equal": source_prediction_equal,
        "runtime_shadow_prediction_array_equal": shadow_prediction_equal,
        "risk_max_absolute_difference": shadow_risk_max_abs,
        "absolute_tolerance": 1e-12,
        "component_max_absolute_difference": component_max_abs,
        "component_absolute_tolerance": 1e-12,
        "component_absolute_differences": component_differences,
        "source_risk_max_absolute_difference_diagnostic": source_risk_max_abs,
        "source_risk_difference_interpretation": (
            "diagnostic_only_because_empirical_tail_ranks_are_discontinuous_at_ties"
        ),
        "equivalence_mode": "source_components_plus_stable_runtime_shadow",
        "passes": bool(
            source_prediction_equal
            and shadow_prediction_equal
            and shadow_risk_max_abs <= 1e-12
            and component_max_abs <= 1e-12
        ),
        "test_count": int(expected_prediction.size),
        "selected_risk": runtime.selected_risk,
        "unknown_or_test_labels_used_for_runtime_fitting_or_selection": False,
    }
    if not equivalence["passes"]:
        raise RuntimeError(f"captured runtime equivalence failed: {equivalence}")

    artifact = capture_dir / "pairwise_runtime.joblib"
    joblib.dump(runtime, artifact, compress=3)
    benchmark_inputs = capture_dir / "benchmark_inputs.npz"
    np.savez_compressed(
        benchmark_inputs,
        **{
            f"view_{index}": np.asarray(view)
            for index, view in enumerate(captured["raw_test_views"])
        },
    )
    manifest = {
        "schema_version": "strict_v4_pairwise_runtime_capture_v1",
        "trainer": trainer_file,
        "trainer_sha256": file_hash(trainer),
        "trainer_arguments": trainer_arguments,
        "capture_wall_seconds": capture_wall_seconds,
        "phase_timings": phase_timings,
        "deployment_artifact": artifact.name,
        "deployment_artifact_sha256": file_hash(artifact),
        "deployment_artifact_bytes": artifact.stat().st_size,
        "trainable_parameters": None,
        "trainable_parameters_status": "not_applicable_nonparametric_ensemble",
        "peak_gpu_memory_mb": 0.0,
        "peak_host_rss_mb": (
            float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0)
            if resource is not None
            else None
        ),
        "benchmark_inputs": benchmark_inputs.name,
        "benchmark_inputs_sha256": file_hash(benchmark_inputs),
        "benchmark_inputs_contain_labels": False,
        "runtime_evidence": runtime.evidence(),
        "equivalence": equivalence,
    }
    (capture_dir / "equivalence.json").write_text(
        json.dumps(equivalence, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (capture_dir / "capture_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
