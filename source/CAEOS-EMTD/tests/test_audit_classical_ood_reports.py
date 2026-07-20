from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from audit_classical_ood_reports import METHODS, REPORT_METRICS, build_audit


def write_run(
    root: Path, corrupt: bool = False, threshold: float = 0.5
) -> None:
    run = root / "edge_iiot" / "fingerprinting_seed7_classical_ood"
    run.mkdir(parents=True)
    report = {metric: 0.5 for metric in REPORT_METRICS}
    payload = {
        "model": "classical_ood",
        "reports": {method: report for method in METHODS},
        "validation_thresholds": {method: threshold for method in METHODS},
        "selection_evidence": {
            "unknown_or_test_labels_used_for_training": False,
            "unknown_or_test_labels_used_for_thresholds": False,
            "detector_subsample_is_class_balanced": True,
        },
        "training_seconds": 2.0,
        "training_seconds_by_component": {
            "known_classifier": 1.0,
            **{method: 0.25 for method in METHODS},
        },
        "resource_usage_by_report": {
            method: {"training_seconds": 1.25} for method in METHODS
        },
    }
    if corrupt:
        payload["training_seconds"] = {"known_classifier": 1.0}
    (run / "metrics.json").write_text(json.dumps(payload), encoding="utf-8")
    (run / "provenance.json").write_text("{}", encoding="utf-8")
    (run / "model.pkl").write_bytes(b"model")
    validation_size, test_size = 4, 6
    arrays = {
        "validation_labels": np.arange(validation_size),
        "test_labels": np.arange(test_size),
        "test_unknown": np.zeros(test_size, dtype=bool),
        "test_prediction": np.arange(test_size),
    }
    for method in METHODS:
        arrays[f"validation_{method}"] = np.linspace(0, 1, validation_size)
        arrays[f"test_{method}"] = np.linspace(0, 1, test_size)
    np.savez_compressed(run / "scores.npz", **arrays)


class ClassicalOodReportAuditTests(unittest.TestCase):
    def test_complete_report_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_run(root)
            report = build_audit(root, expected_runs=1)
        self.assertEqual("complete", report["state"])
        self.assertEqual(4, report["expected_method_evaluations"])

    def test_non_scalar_training_time_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_run(root, corrupt=True)
            report = build_audit(root, expected_runs=1)
        self.assertEqual("invalid", report["state"])
        self.assertTrue(any("non-negative scalar" in issue for issue in report["issues"]))

    def test_negative_finite_detection_threshold_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_run(root, threshold=-0.125)
            report = build_audit(root, expected_runs=1)
        self.assertEqual("complete", report["state"])

    def test_nonfinite_detection_threshold_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_run(root, threshold=float("inf"))
            report = build_audit(root, expected_runs=1)
        self.assertEqual("invalid", report["state"])
        self.assertTrue(any("validation threshold" in issue for issue in report["issues"]))


if __name__ == "__main__":
    unittest.main()
