from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from diagnose_mdr_caeos_known_validation_failure import (
    _load_allowlisted_arrays,
    diagnose_capture,
)


def write_capture(root: Path) -> Path:
    clean_dir = root / "clean_run"
    robust_dir = root / "robust_run"
    clean_dir.mkdir(parents=True)
    robust_dir.mkdir(parents=True)
    clean_probability = np.asarray(
        [[0.9, 0.1], [0.8, 0.2], [0.6, 0.4], [0.1, 0.9]]
    )
    robust_probability = np.asarray(
        [[0.9, 0.1], [0.2, 0.8], [0.3, 0.7], [0.1, 0.9]]
    )
    np.savez(
        clean_dir / "evidence_package.npz",
        validation_final_probability=clean_probability,
        validation_local_conflict=np.asarray(
            [[0.1], [0.8], [0.2], [0.1]]
        ),
        test_final_probability=np.asarray([[0.0, 1.0]]),
    )
    np.savez(
        robust_dir / "evidence_package.npz",
        validation_final_probability=robust_probability,
        test_final_probability=np.asarray([[1.0, 0.0]]),
    )
    np.savez(
        robust_dir / "scores.npz",
        validation_labels=np.asarray([0, 0, 1, 1]),
        validation_any_missing=np.asarray([False, False, True, False]),
        test_labels=np.asarray([1]),
    )
    capture = {
        "schema_version": "strict_v4_mdr_caeos_runtime_capture_v1",
        "state": "complete",
        "weight": 0.25,
        "task": {"suite": "suite", "scenario": "scenario"},
        "roundtrip": {"passes": True},
        "unknown_or_test_labels_used_for_training_selection_or_calibration": (
            False
        ),
        "runtime_evidence": {
            "algorithm": "mdr_caeos_v1",
            "contains_test_ground_truth": False,
            "unknown_or_test_labels_used_for_runtime_fitting_or_selection": (
                False
            ),
            "health_calibration": {
                "conflict_threshold": 0.5,
                "disagreement_threshold": 1.0,
                "unknown_or_test_labels_used": False,
            },
        },
        "known_validation_profile": {
            "clean_pairwise_macro_f1": 0.7333333333333334,
            "robust_clean_macro_f1": 0.7333333333333334,
        },
    }
    path = root / "capture_manifest.json"
    path.write_text(json.dumps(capture), encoding="utf-8")
    return path


def test_diagnosis_uses_only_validation_arrays(tmp_path: Path) -> None:
    row = diagnose_capture(write_capture(tmp_path), "unused")
    assert row["active_count"] == 2
    assert row["changed_prediction_count"] == 2
    assert row["corrected_count"] == 1
    assert row["harmed_count"] == 1
    assert row["net_correctness_change_count"] == 0
    assert row["routed_clean_delta"] == pytest.approx(0.0)


def test_allowlist_rejects_test_array_request(tmp_path: Path) -> None:
    path = tmp_path / "arrays.npz"
    np.savez(path, test_labels=np.asarray([1]))
    with pytest.raises(ValueError, match="cannot read test arrays"):
        _load_allowlisted_arrays(path, ("test_labels",))
