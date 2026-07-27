from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np

try:
    import resource
except ImportError:  # pragma: no cover - formal execution is Linux-only.
    resource = None

from caeos.pairwise_deployment import PairwiseDeploymentBundle
from capture_pairwise_runtime import (
    build_runtime,
    file_hash,
    parse_arguments,
    run_and_capture,
)


def build_deployment_bundle(local: dict[str, object]) -> PairwiseDeploymentBundle:
    trainer_args = local["args"]
    data_bundle = local["bundle"]
    runtime = build_runtime(local)
    config_path = Path(trainer_args.config).resolve()
    preprocessing = data_bundle.preprocessing
    selected_threshold = float(local["thresholds"][runtime.selected_risk])
    return PairwiseDeploymentBundle(
        runtime=runtime,
        modality_names=tuple(data_bundle.modality_names),
        modalities={
            str(name): tuple(columns)
            for name, columns in preprocessing["modalities"].items()
        },
        processor_states={
            str(name): {
                key: list(values)
                for key, values in state.items()
            }
            for name, state in preprocessing["processors"].items()
        },
        class_names=tuple(data_bundle.class_names),
        benign_index=int(data_bundle.benign_index),
        selected_threshold=selected_threshold,
        risk_policy_name=str(trainer_args.risk_policy_name),
        source_config_sha256=file_hash(config_path),
    )


def main() -> None:
    args, trainer_arguments = parse_arguments()
    trainer = args.trainer.resolve()
    if not trainer.is_file():
        raise FileNotFoundError(trainer)
    capture_dir = args.capture_dir.resolve()
    capture_dir.mkdir(parents=True, exist_ok=True)
    captured, phase_timings, capture_wall_seconds = run_and_capture(
        str(trainer), trainer_arguments
    )
    if not captured:
        raise RuntimeError("pairwise trainer main locals were not captured")

    deployment = build_deployment_bundle(captured)
    raw_test_views = [
        np.asarray(view) for view in captured["raw_test_views"]
    ]
    raw_validation_views = [
        np.asarray(view) for view in captured["raw_validation_views"]
    ]
    expected = deployment.runtime.predict(raw_test_views)
    replay = deployment.predict_views(raw_test_views)
    evidence_package = captured["evidence_package"]
    expected_rejected = np.asarray(evidence_package["test_rejected"], dtype=bool)
    equivalence = {
        "schema_version": "strict_v4_pairwise_deployment_equivalence_v2",
        "closed_set_prediction_array_equal": bool(
            np.array_equal(
                replay["closed_set_index"], expected["prediction"]
            )
        ),
        "risk_array_equal": bool(np.array_equal(replay["risk"], expected["risk"])),
        "rejection_array_equal": bool(
            np.array_equal(replay["rejected"], expected_rejected)
        ),
        "selected_threshold_equal": bool(
            deployment.selected_threshold
            == float(captured["selected_threshold"])
        ),
        "test_count": int(len(replay["risk"])),
        "unknown_or_test_labels_used_for_bundle_fitting_or_selection": False,
    }
    equivalence["passes"] = all(
        value is True
        for key, value in equivalence.items()
        if key.endswith("_equal")
    )
    if not equivalence["passes"]:
        raise RuntimeError(f"deployment equivalence failed: {equivalence}")

    artifact = capture_dir / "pairwise_deployment_bundle.joblib"
    joblib.dump(deployment, artifact, compress=3)
    restored = joblib.load(artifact)
    restored_replay = restored.predict_views(raw_test_views)
    roundtrip = {
        "closed_set_prediction_array_equal": bool(
            np.array_equal(
                restored_replay["closed_set_index"],
                replay["closed_set_index"],
            )
        ),
        "risk_array_equal": bool(
            np.array_equal(restored_replay["risk"], replay["risk"])
        ),
        "rejection_array_equal": bool(
            np.array_equal(restored_replay["rejected"], replay["rejected"])
        ),
    }
    roundtrip["passes"] = all(roundtrip.values())
    if not roundtrip["passes"]:
        raise RuntimeError(f"deployment serialization roundtrip failed: {roundtrip}")

    benchmark_inputs = capture_dir / "processed_benchmark_inputs.npz"
    np.savez_compressed(
        benchmark_inputs,
        **{
            f"view_{index}": view
            for index, view in enumerate(raw_test_views)
        },
    )
    benchmark_outputs = capture_dir / "processed_benchmark_expected_outputs.npz"
    np.savez_compressed(
        benchmark_outputs,
        closed_set_index=replay["closed_set_index"],
        probability=replay["probability"],
        risk=replay["risk"],
        rejected=replay["rejected"],
    )
    validation_inputs = capture_dir / "processed_validation_inputs.npz"
    np.savez_compressed(
        validation_inputs,
        **{
            f"view_{index}": view
            for index, view in enumerate(raw_validation_views)
        },
    )
    validation_output = deployment.predict_views(raw_validation_views)
    validation_outputs = (
        capture_dir / "processed_validation_expected_outputs.npz"
    )
    np.savez_compressed(
        validation_outputs,
        closed_set_index=validation_output["closed_set_index"],
        probability=validation_output["probability"],
        risk=validation_output["risk"],
        rejected=validation_output["rejected"],
    )
    equivalence_path = capture_dir / "equivalence.json"
    equivalence_path.write_text(
        json.dumps(equivalence, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema_version": "strict_v4_pairwise_deployment_capture_v3",
        "trainer": str(trainer),
        "trainer_sha256": file_hash(trainer),
        "trainer_arguments": trainer_arguments,
        "capture_wall_seconds": capture_wall_seconds,
        "phase_timings": phase_timings,
        "peak_gpu_memory_mb": 0.0,
        "peak_host_rss_mb": (
            float(
                resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                / 1024.0
            )
            if resource is not None
            else None
        ),
        "deployment_artifact": artifact.name,
        "deployment_artifact_sha256": file_hash(artifact),
        "deployment_artifact_bytes": artifact.stat().st_size,
        "processed_benchmark_inputs": benchmark_inputs.name,
        "processed_benchmark_inputs_sha256": file_hash(benchmark_inputs),
        "processed_benchmark_inputs_contain_labels": False,
        "processed_benchmark_expected_outputs": benchmark_outputs.name,
        "processed_benchmark_expected_outputs_sha256": file_hash(
            benchmark_outputs
        ),
        "processed_benchmark_expected_outputs_contain_ground_truth": False,
        "processed_validation_inputs": validation_inputs.name,
        "processed_validation_inputs_sha256": file_hash(validation_inputs),
        "processed_validation_inputs_contain_labels": False,
        "processed_validation_expected_outputs": validation_outputs.name,
        "processed_validation_expected_outputs_sha256": file_hash(
            validation_outputs
        ),
        "processed_validation_expected_outputs_contain_labels": False,
        "equivalence": equivalence_path.name,
        "equivalence_sha256": file_hash(equivalence_path),
        "deployment_evidence": deployment.evidence(),
        "source_equivalence": equivalence,
        "serialization_roundtrip": roundtrip,
        "trainer_metrics_file_generated_as_unmodified_side_effect": bool(
            (Path(captured["args"].output_dir) / "metrics.json").is_file()
        ),
        "metric_values_consumed_for_bundle_design_or_selection": False,
        "formal_model_metrics_admitted": 0,
        "storage_policy": "gpu_private_do_not_publish",
    }
    (capture_dir / "capture_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
