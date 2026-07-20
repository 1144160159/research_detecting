from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from select_strict_v4_external_risk_candidate import canonical_hash


IMPLEMENTATIONS = (
    "run_neural_baseline_matrix.py",
    "train_neural_open_set.py",
    "train_classical_ood.py",
    "caeos/open_detect.py",
    "scripts/run_strict_v4_full103_baselines_seed7.sh",
)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--coverage-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    coverage = json.loads(args.coverage_manifest.read_text(encoding="utf-8"))
    if coverage.get("schema_version") != "strict_v4_coverage_manifest_v2":
        raise ValueError("unexpected strict-v4 coverage manifest schema")
    if coverage.get("manifest_sha256") != canonical_hash(coverage):
        raise ValueError("full103 coverage manifest SHA mismatch")
    if coverage.get("scenario_inference_units") != 102:
        raise ValueError("baseline expansion requires all 102 feasible scenarios")

    payload: dict[str, Any] = {
        "schema_version": "strict_v4_baseline_manifest_v2",
        "status": "frozen_before_baseline_results",
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "seed": 7,
        "datasets": 7,
        "scenario_inference_units": 102,
        "run_models": ["opendetect", "classical_ood"],
        "reported_methods": [
            "opendetect",
            "isolation_forest",
            "one_class_svm",
            "local_outlier_factor",
            "pca_reconstruction",
        ],
        "expected_run_directories": 204,
        "expected_method_evaluations": 510,
        "protocol": {
            "opendetect_epochs": 100,
            "known_acceptance": 0.95,
            "classical_detector_max_samples": 5000,
            "isolation_trees": 200,
            "ocsvm_nu": 0.05,
            "lof_neighbors": 20,
            "pca_components": 64,
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
        },
        "cache_artifacts": coverage["cache_artifacts"],
        "implementation_sha256": {
            relative: file_hash(project_root / relative)
            for relative in IMPLEMENTATIONS
        },
        "evidence_boundary": {
            "single_seed_coverage_only": True,
            "full_sota_requires_multi_seed_confirmation": True,
        },
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
