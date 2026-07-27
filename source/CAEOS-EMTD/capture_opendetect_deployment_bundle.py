from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import torch

from caeos.open_detect import OpenDetectClassifier
from caeos.opendetect_deployment import OpenDetectDeploymentBundle
from create_strict_v4_external_confirmation_protocol import file_hash


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def views(path: Path) -> list[np.ndarray]:
    with np.load(path, allow_pickle=False) as payload:
        names = sorted(
            payload.files,
            key=lambda name: int(name[len("view_") :]),
        )
        if names != [f"view_{index}" for index in range(len(names))]:
            raise ValueError("OpenDetect input views are not contiguous")
        output = [np.asarray(payload[name]) for name in names]
    if not output or len({len(value) for value in output}) != 1:
        raise ValueError("OpenDetect input views are empty or misaligned")
    return output


def restore_bundle(
    source_run_dir: Path,
    pairwise_capture_dir: Path,
) -> tuple[OpenDetectDeploymentBundle, list[np.ndarray], dict[str, Any]]:
    source_run_dir = source_run_dir.resolve()
    pairwise_capture_dir = pairwise_capture_dir.resolve()
    source_paths = {
        name: source_run_dir / name
        for name in (
            "metrics.json",
            "scores.npz",
            "provenance.json",
            "model.pt",
        )
    }
    missing = [str(path) for path in source_paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "OpenDetect source artifacts are incomplete: " + ", ".join(missing)
        )
    metrics = load(source_paths["metrics.json"])
    provenance = load(source_paths["provenance.json"])
    if (
        metrics.get("model") != "opendetect"
        or metrics.get("selection_evidence", {}).get(
            "unknown_or_test_labels_used_for_fitting_or_selection"
        )
        is not False
    ):
        raise ValueError("OpenDetect source identity or leakage failure")
    try:
        checkpoint = torch.load(
            source_paths["model.pt"],
            map_location="cpu",
            weights_only=False,
        )
    except TypeError:
        checkpoint = torch.load(source_paths["model.pt"], map_location="cpu")
    arguments = checkpoint["arguments"]
    if arguments.get("model") != "opendetect":
        raise ValueError("OpenDetect checkpoint model identity mismatch")
    input_dims = tuple(int(value) for value in checkpoint["input_dims"])
    class_names = tuple(str(value) for value in checkpoint["class_names"])
    model = OpenDetectClassifier(
        input_dims,
        len(class_names),
        int(arguments["hidden_dim"]),
        int(arguments["embedding_dim"]),
        float(arguments["dropout"]),
        float(arguments["temperature"]),
        float(arguments["open_detect_generative_weight"]),
    )
    model.load_state_dict(checkpoint["model_state"], strict=True)
    config_path = Path(str(arguments["config"]))
    if not config_path.is_absolute():
        command_config = provenance.get("inputs", {}).get("config", {}).get(
            "path"
        )
        config_path = Path(command_config) if command_config else config_path
    if not config_path.is_file():
        raise FileNotFoundError(config_path)
    threshold = float(metrics["validation_thresholds"]["opendetect"])
    bundle = OpenDetectDeploymentBundle(
        model=model,
        class_names=class_names,
        input_dims=input_dims,
        selected_threshold=threshold,
        source_model_sha256=file_hash(source_paths["model.pt"]),
        source_config_sha256=file_hash(config_path),
    )
    pairwise_manifest = load(pairwise_capture_dir / "capture_manifest.json")
    if (
        pairwise_manifest.get("schema_version")
        != "strict_v4_pairwise_deployment_capture_v3"
        or pairwise_manifest.get("source_equivalence", {}).get("passes")
        is not True
    ):
        raise ValueError("auditable Pairwise capture v3 is required")
    input_path = pairwise_capture_dir / pairwise_manifest[
        "processed_benchmark_inputs"
    ]
    if (
        not input_path.is_file()
        or file_hash(input_path)
        != pairwise_manifest["processed_benchmark_inputs_sha256"]
    ):
        raise ValueError("Pairwise benchmark input SHA mismatch")
    input_views = views(input_path)
    if len(input_views) != len(input_dims) or any(
        view.shape[1] != width
        for view, width in zip(input_views, input_dims)
    ):
        raise ValueError("OpenDetect and Pairwise feature shapes differ")
    if len(input_views[0]) != int(metrics["split_sizes"]["test"]):
        raise ValueError("OpenDetect and Pairwise test row counts differ")
    return bundle, input_views, {
        "metrics": metrics,
        "source_paths": source_paths,
        "pairwise_manifest": pairwise_manifest,
    }


def capture(
    source_run_dir: Path,
    pairwise_capture_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    bundle, input_views, context = restore_bundle(
        source_run_dir, pairwise_capture_dir
    )
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    actual = bundle.predict_views(input_views)
    scores_path = context["source_paths"]["scores.npz"]
    with np.load(scores_path, allow_pickle=False) as scores:
        source_prediction = np.asarray(
            scores["prediction_opendetect"], dtype=np.int64
        )
        source_risk = np.asarray(
            scores["test_opendetect"], dtype=np.float64
        )
    source_rejected = source_risk > bundle.selected_threshold
    equivalence = {
        "schema_version": (
            "strict_v4_opendetect_deployment_equivalence_v1"
        ),
        "closed_set_prediction_array_equal": bool(
            np.array_equal(actual["closed_set_index"], source_prediction)
        ),
        "risk_max_absolute_difference": float(
            np.max(np.abs(actual["risk"] - source_risk))
        ),
        "risk_tolerance": 1e-12,
        "risk_within_tolerance": bool(
            np.max(np.abs(actual["risk"] - source_risk)) <= 1e-12
        ),
        "rejection_array_equal": bool(
            np.array_equal(actual["rejected"], source_rejected)
        ),
        "probability_source_status": (
            "not_archived_by_source_trainer_checked_by_serialization_roundtrip"
        ),
        "unknown_or_test_labels_used_for_capture_or_prediction": False,
    }
    equivalence["passes"] = all(
        (
            equivalence["closed_set_prediction_array_equal"],
            equivalence["risk_within_tolerance"],
            equivalence["rejection_array_equal"],
        )
    )
    if not equivalence["passes"]:
        raise RuntimeError(f"OpenDetect source equivalence failed: {equivalence}")

    artifact_path = output_dir / "opendetect_deployment_bundle.joblib"
    bundle.model = bundle.model.cpu().eval()
    joblib.dump(bundle, artifact_path, compress=3)
    input_path = output_dir / "processed_benchmark_inputs.npz"
    np.savez_compressed(
        input_path,
        **{
            f"view_{index}": value
            for index, value in enumerate(input_views)
        },
    )
    expected_path = output_dir / "processed_benchmark_expected_outputs.npz"
    np.savez_compressed(expected_path, **actual)
    equivalence_path = output_dir / "equivalence.json"
    equivalence_path.write_text(
        json.dumps(equivalence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    restored = joblib.load(artifact_path)
    replay = restored.predict_views(input_views)
    roundtrip = {
        name: bool(np.array_equal(replay[name], actual[name]))
        for name in (
            "closed_set_index",
            "probability",
            "risk",
            "rejected",
        )
    }
    roundtrip["passes"] = all(roundtrip.values())
    if not roundtrip["passes"]:
        raise RuntimeError("OpenDetect serialization roundtrip failed")
    source_hashes = {
        name: file_hash(path)
        for name, path in context["source_paths"].items()
    }
    manifest = {
        "schema_version": (
            "strict_v4_opendetect_deployment_capture_v1"
        ),
        "deployment_artifact": artifact_path.name,
        "deployment_artifact_sha256": file_hash(artifact_path),
        "deployment_artifact_bytes": artifact_path.stat().st_size,
        "processed_benchmark_inputs": input_path.name,
        "processed_benchmark_inputs_sha256": file_hash(input_path),
        "processed_benchmark_inputs_contain_labels": False,
        "processed_benchmark_expected_outputs": expected_path.name,
        "processed_benchmark_expected_outputs_sha256": file_hash(
            expected_path
        ),
        "processed_benchmark_expected_outputs_contain_ground_truth": False,
        "equivalence": equivalence_path.name,
        "equivalence_sha256": file_hash(equivalence_path),
        "source_equivalence": equivalence,
        "serialization_roundtrip": roundtrip,
        "deployment_evidence": bundle.evidence(),
        "source_file_sha256": source_hashes,
        "source_pairwise_capture_manifest_sha256": file_hash(
            pairwise_capture_dir / "capture_manifest.json"
        ),
        "formal_model_metrics_admitted": 0,
        "storage_policy": "gpu_private_do_not_publish",
    }
    manifest_path = output_dir / "capture_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-run-dir", type=Path, required=True)
    parser.add_argument("--pairwise-capture-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = capture(
        args.source_run_dir,
        args.pairwise_capture_dir,
        args.output_dir,
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
