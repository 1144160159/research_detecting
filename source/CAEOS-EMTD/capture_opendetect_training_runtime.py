from __future__ import annotations

import argparse
import json
from pathlib import Path
import runpy
import sys
import time
from types import FrameType
from typing import Any

try:
    import resource
except ImportError:  # pragma: no cover - formal execution is Linux-only.
    resource = None

import joblib
import numpy as np
import torch

from caeos.open_detect import open_detect_risk
from caeos.open_detect_runtime import OpenDetectRuntime
from capture_opendetect_runtime import file_hash, load_checkpoint


def parse_arguments() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description="Run the unchanged OpenDetect trainer with phase instrumentation"
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


def run_and_capture(
    trainer_file: str, trainer_arguments: list[str]
) -> tuple[dict[str, Any], dict[str, float], float]:
    namespace = runpy.run_path(
        trainer_file, run_name="strict_v4_opendetect_training_capture_module"
    )
    main_function = namespace["main"]
    globals_ = main_function.__globals__
    captured: dict[str, Any] = {}
    timings = {
        "feature_preparation_seconds": 0.0,
        "training_seconds": 0.0,
        "calibration_seconds": 0.0,
    }
    original_prepare = globals_["prepare_tabular_open_set"]
    original_train = globals_["train"]

    def timed_prepare(*args: Any, **kwargs: Any) -> Any:
        started = time.perf_counter()
        try:
            return original_prepare(*args, **kwargs)
        finally:
            timings["feature_preparation_seconds"] += time.perf_counter() - started

    def timed_train(*args: Any, **kwargs: Any) -> Any:
        started = time.perf_counter()
        try:
            return original_train(*args, **kwargs)
        finally:
            timings["training_seconds"] += time.perf_counter() - started

    globals_["prepare_tabular_open_set"] = timed_prepare
    globals_["train"] = timed_train

    def trace(frame: FrameType, event: str, arg: object):
        if frame.f_code is main_function.__code__:
            if event == "return":
                captured.update(frame.f_locals.copy())
            return trace
        return None

    original_argv = sys.argv[:]
    wall_started = time.perf_counter()
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
    try:
        sys.argv = [trainer_file, *trainer_arguments]
        sys.settrace(trace)
        main_function()
    finally:
        sys.settrace(None)
        sys.argv = original_argv
        globals_["prepare_tabular_open_set"] = original_prepare
        globals_["train"] = original_train
    wall_seconds = time.perf_counter() - wall_started
    if not captured:
        raise RuntimeError("OpenDetect trainer main locals were not captured")
    if captured["args"].model != "opendetect":
        raise ValueError("training capture only supports OpenDetect")
    calibration_started = time.perf_counter()
    np.quantile(
        np.asarray(captured["validation_risk"], dtype=np.float64),
        float(captured["args"].known_acceptance),
    )
    timings["calibration_seconds"] = time.perf_counter() - calibration_started
    timings["total_fit_seconds"] = sum(timings.values())
    return captured, timings, wall_seconds


def build_equivalence(
    observed: dict[str, np.ndarray],
    shadow: dict[str, np.ndarray],
    source: dict[str, np.ndarray],
    device_name: str,
) -> dict[str, Any]:
    prediction_equal = np.array_equal(observed["prediction"], shadow["prediction"])
    risk_max_abs = float(np.max(np.abs(observed["risk"] - shadow["risk"])))
    source_prediction_equal = np.array_equal(
        observed["prediction"], source["prediction"]
    )
    source_risk_max_abs = float(
        np.max(np.abs(observed["risk"] - source["risk"]))
    )
    return {
        "schema_version": "strict_v4_opendetect_runtime_equivalence_v2",
        "prediction_array_equal": prediction_equal,
        "risk_max_absolute_difference": risk_max_abs,
        "absolute_tolerance": 1e-12,
        "equivalence_mode": "runtime_vs_uninstrumented_same_device_shadow",
        "passes": bool(prediction_equal and risk_max_abs <= 1e-12),
        "test_count": int(len(shadow["prediction"])),
        "device": device_name,
        "source_score_diagnostic": {
            "is_formal_equivalence_reference": False,
            "prediction_array_equal": source_prediction_equal,
            "risk_max_absolute_difference": source_risk_max_abs,
        },
        "unknown_or_test_labels_used_for_runtime_fitting_or_selection": False,
    }


def main() -> None:
    args, trainer_arguments = parse_arguments()
    trainer = args.trainer.resolve()
    capture = args.capture_dir.resolve()
    if not trainer.is_file():
        raise FileNotFoundError(trainer)
    capture.mkdir(parents=True, exist_ok=True)
    captured, phase_timings, wall_seconds = run_and_capture(
        str(trainer), trainer_arguments
    )
    output_dir = Path(captured["args"].output_dir).resolve()
    checkpoint_path = output_dir / "model.pt"
    metrics_path = output_dir / "metrics.json"
    if not checkpoint_path.is_file() or not metrics_path.is_file():
        raise FileNotFoundError("instrumented OpenDetect trainer did not save its artifacts")
    checkpoint = load_checkpoint(checkpoint_path)
    device_name = str(captured["device"])
    runtime = OpenDetectRuntime.from_checkpoint(checkpoint, device_name)
    views = [view.numpy() for view in captured["bundle"].test.views]
    observed = runtime.predict(views)
    shadow_runtime = OpenDetectRuntime.from_checkpoint(checkpoint, device_name)
    shadow = shadow_runtime.predict(views)
    reference_logits = np.asarray(captured["test"]["logits"])
    reference_prediction = reference_logits.argmax(axis=1)
    reference_risk = open_detect_risk(reference_logits)
    equivalence = build_equivalence(
        observed,
        shadow,
        {"prediction": reference_prediction, "risk": reference_risk},
        device_name,
    )
    if not equivalence["passes"]:
        raise RuntimeError(f"OpenDetect training runtime equivalence failed: {equivalence}")

    artifact = capture / "opendetect_runtime.joblib"
    inputs = capture / "benchmark_inputs.npz"
    joblib.dump(runtime, artifact, compress=3)
    np.savez_compressed(
        inputs, **{f"view_{index}": view for index, view in enumerate(views)}
    )
    peak_gpu = (
        float(torch.cuda.max_memory_allocated() / (1024**2))
        if torch.cuda.is_available()
        else 0.0
    )
    peak_host_rss = (
        float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0)
        if resource is not None
        else None
    )
    manifest = {
        "schema_version": "strict_v4_opendetect_training_runtime_capture_v2",
        "trainer": str(trainer),
        "trainer_sha256": file_hash(trainer),
        "trainer_arguments": trainer_arguments,
        "capture_wall_seconds": wall_seconds,
        "phase_timings": phase_timings,
        "trainable_parameters": int(
            sum(parameter.numel() for parameter in runtime.model.parameters())
        ),
        "peak_gpu_memory_mb": peak_gpu,
        "peak_host_rss_mb": peak_host_rss,
        "deployment_artifact": artifact.name,
        "deployment_artifact_sha256": file_hash(artifact),
        "deployment_artifact_bytes": artifact.stat().st_size,
        "benchmark_inputs": inputs.name,
        "benchmark_inputs_sha256": file_hash(inputs),
        "benchmark_inputs_contain_labels": False,
        "runtime_evidence": runtime.evidence(),
        "equivalence": equivalence,
    }
    (capture / "equivalence.json").write_text(
        json.dumps(equivalence, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (capture / "capture_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
