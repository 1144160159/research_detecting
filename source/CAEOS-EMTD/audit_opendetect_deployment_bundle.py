from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from capture_opendetect_deployment_bundle import views
from create_strict_v4_external_confirmation_protocol import file_hash


def checked(
    root: Path,
    manifest: dict[str, Any],
    file_key: str,
    hash_key: str,
) -> Path:
    path = root / str(manifest[file_key])
    if not path.is_file() or file_hash(path) != manifest[hash_key]:
        raise ValueError(f"OpenDetect capture file mismatch: {path.name}")
    return path


def audit(capture_dir: Path) -> dict[str, Any]:
    capture_dir = capture_dir.resolve()
    manifest_path = capture_dir / "capture_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        manifest.get("schema_version")
        != "strict_v4_opendetect_deployment_capture_v1"
    ):
        raise ValueError("unsupported OpenDetect capture schema")
    artifact = checked(
        capture_dir,
        manifest,
        "deployment_artifact",
        "deployment_artifact_sha256",
    )
    inputs = checked(
        capture_dir,
        manifest,
        "processed_benchmark_inputs",
        "processed_benchmark_inputs_sha256",
    )
    expected_path = checked(
        capture_dir,
        manifest,
        "processed_benchmark_expected_outputs",
        "processed_benchmark_expected_outputs_sha256",
    )
    equivalence_path = checked(
        capture_dir, manifest, "equivalence", "equivalence_sha256"
    )
    equivalence = json.loads(equivalence_path.read_text(encoding="utf-8"))
    if (
        equivalence != manifest["source_equivalence"]
        or equivalence.get("passes") is not True
    ):
        raise ValueError("OpenDetect source equivalence failed")
    bundle = joblib.load(artifact)
    if bundle.evidence() != manifest["deployment_evidence"]:
        raise ValueError("OpenDetect deployment evidence mismatch")
    evidence = bundle.evidence()
    if (
        evidence.get(
            "unknown_or_test_labels_used_for_model_or_threshold_fitting"
        )
        is not False
        or evidence.get("contains_validation_labels") is not False
        or evidence.get("contains_test_labels") is not False
    ):
        raise ValueError("OpenDetect deployment disclosure failed")
    input_views = views(inputs)
    first = bundle.predict_views(input_views)
    second = bundle.predict_views(input_views)
    with np.load(expected_path, allow_pickle=False) as payload:
        expected = {name: np.asarray(payload[name]) for name in payload.files}
    names = (
        "closed_set_index",
        "probability",
        "risk",
        "rejected",
    )
    for name in names:
        if not np.array_equal(first[name], expected[name]):
            raise ValueError(f"OpenDetect replay differs for {name}")
        if not np.array_equal(first[name], second[name]):
            raise ValueError(f"OpenDetect repeated replay differs for {name}")
    if not np.array_equal(
        first["rejected"],
        first["risk"] > bundle.selected_threshold,
    ):
        raise ValueError("OpenDetect rejection threshold rule failed")
    return {
        "schema_version": (
            "strict_v4_opendetect_deployment_independent_audit_v1"
        ),
        "capture_manifest_sha256": file_hash(manifest_path),
        "deployment_artifact_sha256": file_hash(artifact),
        "benchmark_row_count": len(first["risk"]),
        "checked_outputs": list(names),
        "exact_replay_passes": True,
        "repeated_replay_passes": True,
        "threshold_rule_passes": True,
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
    result = audit(args.capture_dir)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
