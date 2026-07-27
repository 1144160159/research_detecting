from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_file_hash(
    capture_dir: Path,
    manifest: dict[str, Any],
    file_key: str,
    hash_key: str,
) -> Path:
    path = capture_dir / str(manifest[file_key])
    if not path.is_file():
        raise FileNotFoundError(path)
    actual = file_hash(path)
    expected = str(manifest[hash_key])
    if actual != expected:
        raise ValueError(f"{path.name} SHA-256 mismatch: {actual} != {expected}")
    return path


def audit_capture(capture_dir: Path) -> dict[str, Any]:
    capture_dir = capture_dir.resolve()
    manifest_path = capture_dir / "capture_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["schema_version"] not in {
        "strict_v4_pairwise_deployment_capture_v2",
        "strict_v4_pairwise_deployment_capture_v3",
    }:
        raise ValueError("unsupported deployment capture schema")

    artifact = _require_file_hash(
        capture_dir,
        manifest,
        "deployment_artifact",
        "deployment_artifact_sha256",
    )
    inputs_path = _require_file_hash(
        capture_dir,
        manifest,
        "processed_benchmark_inputs",
        "processed_benchmark_inputs_sha256",
    )
    outputs_path = _require_file_hash(
        capture_dir,
        manifest,
        "processed_benchmark_expected_outputs",
        "processed_benchmark_expected_outputs_sha256",
    )
    equivalence_path = _require_file_hash(
        capture_dir, manifest, "equivalence", "equivalence_sha256"
    )

    equivalence = json.loads(equivalence_path.read_text(encoding="utf-8"))
    if equivalence != manifest["source_equivalence"]:
        raise ValueError("equivalence file differs from capture manifest")
    if not equivalence.get("passes"):
        raise ValueError("source equivalence did not pass")

    bundle = joblib.load(artifact)
    evidence = bundle.evidence()
    if evidence != manifest["deployment_evidence"]:
        raise ValueError("loaded bundle evidence differs from capture manifest")
    required_evidence = {
        "unknown_or_test_labels_used_for_preprocessing_selection_or_threshold": False,
        "contains_raw_input_rows": False,
        "contains_fitted_nonparametric_reference_vectors": True,
        "contains_fitted_class_conditional_state": True,
        "contains_validation_labels": False,
        "contains_test_labels": False,
        "storage_policy": "gpu_private_do_not_publish",
    }
    for key, expected in required_evidence.items():
        if evidence.get(key) != expected:
            raise ValueError(f"deployment evidence {key} is not {expected!r}")
    if manifest.get("storage_policy") != "gpu_private_do_not_publish":
        raise ValueError("capture is not marked GPU-private")
    if manifest.get("formal_model_metrics_admitted") != 0:
        raise ValueError("capture improperly admits formal metrics")
    if manifest.get("processed_benchmark_inputs_contain_labels") is not False:
        raise ValueError("benchmark inputs are not declared label-free")
    if (
        manifest.get("processed_benchmark_expected_outputs_contain_ground_truth")
        is not False
    ):
        raise ValueError("benchmark outputs are not declared ground-truth-free")

    with np.load(inputs_path, allow_pickle=False) as payload:
        if any(not name.startswith("view_") for name in payload.files):
            raise ValueError("benchmark input contains an invalid view name")
        names = sorted(
            payload.files, key=lambda name: int(name[len("view_") :])
        )
        if names != [f"view_{index}" for index in range(len(names))]:
            raise ValueError("benchmark input view numbering is not contiguous")
        views = [np.asarray(payload[name]) for name in names]
    with np.load(outputs_path, allow_pickle=False) as payload:
        expected_outputs = {
            name: np.asarray(payload[name]) for name in payload.files
        }

    first = bundle.predict_views(views)
    second = bundle.predict_views(views)
    checked_outputs = (
        "closed_set_index",
        "probability",
        "risk",
        "rejected",
    )
    for name in checked_outputs:
        if name not in expected_outputs:
            raise ValueError(f"missing expected benchmark output: {name}")
        if not np.array_equal(first[name], expected_outputs[name]):
            raise ValueError(f"serialized replay differs for {name}")
        if not np.array_equal(first[name], second[name]):
            raise ValueError(f"repeated replay is not exact for {name}")
    threshold_rejected = first["risk"] > float(bundle.selected_threshold)
    if not np.array_equal(first["rejected"], threshold_rejected):
        raise ValueError("rejection output does not equal risk > threshold")

    validation_row_count = None
    validation_replay_passes = None
    if manifest["schema_version"].endswith("_v3"):
        validation_inputs_path = _require_file_hash(
            capture_dir,
            manifest,
            "processed_validation_inputs",
            "processed_validation_inputs_sha256",
        )
        validation_outputs_path = _require_file_hash(
            capture_dir,
            manifest,
            "processed_validation_expected_outputs",
            "processed_validation_expected_outputs_sha256",
        )
        if manifest.get("processed_validation_inputs_contain_labels") is not False:
            raise ValueError("validation replay inputs are not declared label-free")
        if (
            manifest.get("processed_validation_expected_outputs_contain_labels")
            is not False
        ):
            raise ValueError("validation replay outputs are not declared label-free")
        with np.load(validation_inputs_path, allow_pickle=False) as payload:
            names = sorted(
                payload.files, key=lambda name: int(name[len("view_") :])
            )
            validation_views = [np.asarray(payload[name]) for name in names]
        with np.load(validation_outputs_path, allow_pickle=False) as payload:
            validation_expected = {
                name: np.asarray(payload[name]) for name in payload.files
            }
        validation_actual = bundle.predict_views(validation_views)
        for name in checked_outputs:
            if not np.array_equal(
                validation_actual[name], validation_expected[name]
            ):
                raise ValueError(f"validation replay differs for {name}")
        validation_row_count = len(validation_actual["risk"])
        validation_replay_passes = True

    return {
        "schema_version": "strict_v4_pairwise_deployment_independent_audit_v1",
        "capture_manifest_sha256": file_hash(manifest_path),
        "deployment_artifact_sha256": file_hash(artifact),
        "feature_schema_sha256": bundle.feature_schema_sha256,
        "feature_count": len(bundle.feature_columns),
        "modality_count": len(bundle.modality_names),
        "class_count": len(bundle.class_names),
        "benchmark_row_count": len(first["risk"]),
        "validation_row_count": validation_row_count,
        "checked_outputs": list(checked_outputs),
        "exact_replay_passes": True,
        "repeated_replay_passes": True,
        "threshold_rule_passes": True,
        "validation_replay_passes": validation_replay_passes,
        "evidence_disclosure_passes": True,
        "formal_model_metrics_admitted": 0,
        "storage_policy": "gpu_private_do_not_publish",
        "passes": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit_capture(args.capture_dir)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
