from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import torch

from caeos.data import prepare_tabular_open_set
from caeos.open_detect import OpenDetectClassifier, open_detect_risk
from caeos.open_detect_runtime import OpenDetectRuntime


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_checkpoint(path: Path) -> dict[str, Any]:
    try:
        return torch.load(path, map_location="cpu", weights_only=False)
    except TypeError:
        return torch.load(path, map_location="cpu")


def same_device_shadow(
    checkpoint: dict[str, Any], views: list[np.ndarray], device_name: str
) -> dict[str, np.ndarray]:
    arguments = checkpoint["arguments"]
    model = OpenDetectClassifier(
        list(checkpoint["input_dims"]),
        len(checkpoint["class_names"]),
        int(arguments["hidden_dim"]),
        int(arguments["embedding_dim"]),
        float(arguments["dropout"]),
        float(arguments["temperature"]),
        float(arguments["open_detect_generative_weight"]),
    )
    model.load_state_dict(checkpoint["model_state"], strict=True)
    model.to(torch.device(device_name)).eval()
    tensors = [torch.from_numpy(np.asarray(view, dtype=np.float32)).to(device_name) for view in views]
    with torch.inference_mode():
        logits = model(tensors)["logits"].detach().cpu().numpy()
    return {
        "prediction": np.asarray(logits.argmax(axis=1), dtype=np.int64),
        "risk": np.asarray(open_detect_risk(logits), dtype=np.float64),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture a frozen OpenDetect runtime")
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--absolute-tolerance", type=float, default=1e-5)
    parser.add_argument(
        "--equivalence-mode",
        choices=("source_scores", "same_device_shadow"),
        default="source_scores",
    )
    args = parser.parse_args()
    source = args.source_run.resolve()
    paths = {name: source / name for name in ("metrics.json", "scores.npz", "model.pt")}
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing OpenDetect artifacts: " + ", ".join(missing))
    metrics = json.loads(paths["metrics.json"].read_text(encoding="utf-8"))
    checkpoint = load_checkpoint(paths["model.pt"])
    arguments = checkpoint["arguments"]
    if metrics.get("model") != "opendetect" or arguments.get("model") != "opendetect":
        raise ValueError("source run is not frozen OpenDetect")
    config_path = Path(str(arguments["config"]))
    if not config_path.is_absolute():
        config_path = Path.cwd() / config_path
    config = json.loads(config_path.read_text(encoding="utf-8"))
    unknown_classes = [value.strip() for value in arguments["unknown_classes"].split(",") if value.strip()]
    bundle = prepare_tabular_open_set(
        str(arguments["csv"]),
        config,
        unknown_classes,
        str(arguments["benign_class"]),
        int(arguments["max_per_class"]),
        int(arguments["chunksize"]),
        int(arguments["seed"]),
        str(arguments["split_strategy"]),
    )
    if bundle.split_metadata != metrics.get("split_metadata"):
        raise ValueError("reconstructed OpenDetect split differs from source")
    if bundle.class_names != list(checkpoint["class_names"]):
        raise ValueError("reconstructed OpenDetect classes differ from checkpoint")
    views = [view.numpy() for view in bundle.test.views]
    runtime = OpenDetectRuntime.from_checkpoint(checkpoint, args.device)
    output = runtime.predict(views)
    with np.load(paths["scores.npz"], allow_pickle=False) as scores:
        source_prediction = np.asarray(scores["prediction_opendetect"])
        source_risk = np.asarray(scores["test_opendetect"])
    if args.equivalence_mode == "same_device_shadow":
        reference = same_device_shadow(checkpoint, views, args.device)
        expected_prediction = reference["prediction"]
        expected_risk = reference["risk"]
    else:
        expected_prediction = source_prediction
        expected_risk = source_risk
    prediction_equal = np.array_equal(output["prediction"], expected_prediction)
    risk_max_abs = float(np.max(np.abs(output["risk"] - expected_risk)))
    equivalence = {
        "schema_version": "strict_v4_opendetect_runtime_equivalence_v1",
        "prediction_array_equal": prediction_equal,
        "risk_max_absolute_difference": risk_max_abs,
        "absolute_tolerance": float(args.absolute_tolerance),
        "equivalence_mode": (
            "runtime_vs_uninstrumented_same_device_shadow"
            if args.equivalence_mode == "same_device_shadow"
            else "runtime_vs_source_score_archive"
        ),
        "passes": bool(prediction_equal and risk_max_abs <= args.absolute_tolerance),
        "test_count": int(len(expected_prediction)),
        "device": args.device,
        "source_score_diagnostic": {
            "prediction_array_equal": bool(
                np.array_equal(output["prediction"], source_prediction)
            ),
            "risk_max_absolute_difference": float(
                np.max(np.abs(output["risk"] - source_risk))
            ),
            "is_formal_equivalence_reference": args.equivalence_mode
            == "source_scores",
        },
        "unknown_or_test_labels_used_for_runtime_fitting_or_selection": False,
    }
    if not equivalence["passes"]:
        raise RuntimeError(f"OpenDetect runtime equivalence failed: {equivalence}")
    capture = args.capture_dir.resolve()
    capture.mkdir(parents=True, exist_ok=True)
    artifact = capture / "opendetect_runtime.joblib"
    joblib.dump(runtime, artifact, compress=3)
    inputs = capture / "benchmark_inputs.npz"
    np.savez_compressed(inputs, **{f"view_{index}": view for index, view in enumerate(views)})
    manifest = {
        "schema_version": "strict_v4_opendetect_runtime_capture_v1",
        "source_run": str(source),
        "source_artifact_sha256": {name: file_hash(path) for name, path in paths.items()},
        "deployment_artifact": artifact.name,
        "deployment_artifact_sha256": file_hash(artifact),
        "deployment_artifact_bytes": artifact.stat().st_size,
        "benchmark_inputs": inputs.name,
        "benchmark_inputs_sha256": file_hash(inputs),
        "benchmark_inputs_contain_labels": False,
        "runtime_evidence": runtime.evidence(),
        "equivalence": equivalence,
    }
    (capture / "equivalence.json").write_text(json.dumps(equivalence, indent=2) + "\n", encoding="utf-8")
    (capture / "capture_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
