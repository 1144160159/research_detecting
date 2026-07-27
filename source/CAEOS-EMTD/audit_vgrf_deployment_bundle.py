from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from build_vgrf_deployment_bundle import file_hash


def _checked_path(
    root: Path,
    manifest: dict[str, Any],
    file_key: str,
    hash_key: str,
) -> Path:
    path = root / manifest[file_key]
    if not path.is_file() or file_hash(path) != manifest[hash_key]:
        raise ValueError(f"missing or hash-mismatched VGRF file: {path.name}")
    return path


def audit_capture(capture_dir: Path) -> dict[str, Any]:
    capture_dir = capture_dir.resolve()
    manifest_path = capture_dir / "capture_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") not in {
        "strict_v4_vgrf_deployment_capture_v1",
        "strict_v4_vgrf_deployment_capture_v2",
    }:
        raise ValueError("unsupported VGRF deployment capture schema")
    artifact = _checked_path(
        capture_dir,
        manifest,
        "deployment_artifact",
        "deployment_artifact_sha256",
    )
    inputs_path = _checked_path(
        capture_dir,
        manifest,
        "processed_benchmark_inputs",
        "processed_benchmark_inputs_sha256",
    )
    outputs_path = _checked_path(
        capture_dir,
        manifest,
        "processed_benchmark_expected_outputs",
        "processed_benchmark_expected_outputs_sha256",
    )
    equivalence_path = _checked_path(
        capture_dir, manifest, "equivalence", "equivalence_sha256"
    )
    equivalence = json.loads(equivalence_path.read_text(encoding="utf-8"))
    if equivalence != manifest["source_equivalence"]:
        raise ValueError("VGRF equivalence file differs from manifest")
    if equivalence.get("passes") is not True:
        raise ValueError("VGRF source equivalence failed")
    source_runtime_compatibility = None
    if manifest["schema_version"].endswith("_v2"):
        compatibility_path = _checked_path(
            capture_dir,
            manifest,
            "source_runtime_compatibility",
            "source_runtime_compatibility_sha256",
        )
        source_runtime_compatibility = json.loads(
            compatibility_path.read_text(encoding="utf-8")
        )
        if source_runtime_compatibility.get("gate_decision_equal") is not True:
            raise ValueError(
                "source and stable runtime VGRF gate decisions differ"
            )
        if (
            source_runtime_compatibility.get(
                "test_probability_array_equal"
            )
            is not True
        ):
            raise ValueError(
                "source and stable runtime VGRF probabilities differ"
            )

    bundle = joblib.load(artifact)
    evidence = bundle.evidence()
    if evidence != manifest["deployment_evidence"]:
        raise ValueError("loaded VGRF evidence differs from manifest")
    required = {
        "contains_raw_input_rows": False,
        "contains_fitted_nonparametric_reference_vectors": True,
        "contains_fitted_class_conditional_state": True,
        "contains_known_validation_aggregate_statistics": True,
        "contains_validation_labels": False,
        "contains_test_labels": False,
        "unknown_or_test_labels_used_for_reliability_gate_threshold_or_prediction": False,
        "storage_policy": "gpu_private_do_not_publish",
    }
    for key, expected in required.items():
        if evidence.get(key) != expected:
            raise ValueError(f"VGRF evidence {key} is not {expected!r}")
    if manifest.get("formal_model_metrics_admitted") != 0:
        raise ValueError("VGRF capture improperly admits model metrics")
    if manifest.get("formal_external_execution_admitted") is not False:
        raise ValueError("VGRF canary improperly admits external execution")
    if manifest["validation_source"].get(
        "validation_labels_stored_in_deployment_artifact"
    ) is not False:
        raise ValueError("VGRF artifact is declared to store validation labels")

    with np.load(inputs_path, allow_pickle=False) as inputs:
        names = sorted(
            inputs.files, key=lambda name: int(name[len("view_") :])
        )
        views = [np.asarray(inputs[name]) for name in names]
    with np.load(outputs_path, allow_pickle=False) as outputs:
        expected_outputs = {
            name: np.asarray(outputs[name]) for name in outputs.files
        }
    first = bundle.predict_views(views)
    second = bundle.predict_views(views)
    checked = (
        "closed_set_index",
        "probability",
        "risk",
        "rejected",
    )
    for name in checked:
        if not np.array_equal(first[name], expected_outputs[name]):
            raise ValueError(f"VGRF replay differs for {name}")
        if not np.array_equal(first[name], second[name]):
            raise ValueError(f"VGRF repeated replay differs for {name}")
    if not np.array_equal(
        first["rejected"], first["risk"] > bundle.selected_threshold
    ):
        raise ValueError("VGRF rejection does not equal risk > threshold")
    return {
        "schema_version": "strict_v4_vgrf_deployment_independent_audit_v1",
        "capture_manifest_sha256": file_hash(manifest_path),
        "deployment_artifact_sha256": file_hash(artifact),
        "feature_schema_sha256": evidence["feature_schema_sha256"],
        "feature_count": evidence["feature_count"],
        "class_count": evidence["class_count"],
        "validation_gate_enabled": evidence["validation_gate_enabled"],
        "benchmark_row_count": len(first["risk"]),
        "checked_outputs": list(checked),
        "exact_replay_passes": True,
        "repeated_replay_passes": True,
        "threshold_rule_passes": True,
        "evidence_disclosure_passes": True,
        "source_runtime_gate_decision_equal": (
            source_runtime_compatibility["gate_decision_equal"]
            if source_runtime_compatibility is not None
            else None
        ),
        "source_runtime_probability_equal": (
            source_runtime_compatibility["test_probability_array_equal"]
            if source_runtime_compatibility is not None
            else None
        ),
        "source_runtime_risk_max_absolute_difference": (
            source_runtime_compatibility[
                "test_risk_max_absolute_difference"
            ]
            if source_runtime_compatibility is not None
            else None
        ),
        "formal_model_metrics_admitted": 0,
        "formal_external_execution_admitted": False,
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
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
