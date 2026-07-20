from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from evaluate_dual_path_robustness import evaluate_pair


def write_run(
    root: Path,
    fingerprint: str,
    augmented: bool,
    prediction: np.ndarray,
    missing: np.ndarray | None = None,
    view_missing: np.ndarray | None = None,
) -> None:
    root.mkdir(parents=True)
    labels = np.asarray([0, 1, -1, -1])
    unknown = labels == -1
    risk = np.asarray([0.1, 0.2, 0.8, 0.9])
    threshold = 0.5
    metrics = {
        "model": "robust" if augmented else "clean",
        "split_metadata": {"split_fingerprint": {"combined": fingerprint}},
        "corruption_protocol": {
            "test_corruption": {
                "kind": "field_missing",
                "modality": 1,
                "severity": 0.5,
                "seed": 7,
                "affected_entries": 10,
            }
        },
        "validation_thresholds": {"cauchy_modality_support_union": threshold},
        "reports": {
            "cauchy_modality_support_union": {
                "known_accuracy": 1.0,
                "known_macro_f1": 1.0,
                "unknown_auroc": 1.0,
                "unknown_aupr": 1.0,
                "unknown_fpr95": 0.0,
                "unknown_f1": 1.0,
                "oscr": 1.0,
                "known_acceptance_rate": 1.0,
                "unknown_rejection_rate": 1.0,
                "mean_known_risk": 0.15,
                "mean_unknown_risk": 0.85,
            }
        },
    }
    if augmented:
        metrics["training_augmentation"] = {
            "enabled": True,
            "unknown_or_test_labels_used": False,
        }
    (root / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
    scores = {
        "test_labels": labels,
        "test_unknown": unknown,
        "test_prediction": prediction,
        "test_cauchy_modality_support_union": risk,
    }
    if missing is not None:
        scores["test_any_missing"] = missing
    if view_missing is not None:
        scores["test_view_missing"] = view_missing
    np.savez(root / "scores.npz", **scores)


class DualPathRobustnessTests(unittest.TestCase):
    def test_clean_detector_ranking_and_robust_prediction_are_combined(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            detector = root / "detector"
            classifier = root / "classifier"
            write_run(detector, "a" * 64, False, np.asarray([1, 0, 0, 0]))
            write_run(classifier, "a" * 64, True, np.asarray([0, 1, 0, 0]))
            result = evaluate_pair(detector, classifier)
            self.assertEqual(result["dual_path_report"]["known_macro_f1"], 1.0)
            self.assertTrue(result["detector_ranking_metrics_exactly_preserved"])

    def test_fingerprint_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            detector = root / "detector"
            classifier = root / "classifier"
            write_run(detector, "a" * 64, False, np.asarray([0, 1, 0, 0]))
            write_run(classifier, "b" * 64, True, np.asarray([0, 1, 0, 0]))
            with self.assertRaisesRegex(ValueError, "split fingerprints differ"):
                evaluate_pair(detector, classifier)

    def test_legacy_clean_detector_without_corruption_metadata_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            detector = root / "detector"
            classifier = root / "classifier"
            write_run(detector, "a" * 64, False, np.asarray([0, 1, 0, 0]))
            write_run(classifier, "a" * 64, True, np.asarray([0, 1, 0, 0]))
            detector_metrics = json.loads(
                (detector / "metrics.json").read_text(encoding="utf-8")
            )
            detector_metrics.pop("corruption_protocol")
            (detector / "metrics.json").write_text(
                json.dumps(detector_metrics), encoding="utf-8"
            )
            classifier_metrics = json.loads(
                (classifier / "metrics.json").read_text(encoding="utf-8")
            )
            classifier_metrics["corruption_protocol"]["test_corruption"] = {
                "kind": "none",
                "modality": None,
                "severity": 0.0,
                "seed": 7,
                "affected_entries": 0,
            }
            (classifier / "metrics.json").write_text(
                json.dumps(classifier_metrics), encoding="utf-8"
            )
            result = evaluate_pair(detector, classifier)
            self.assertEqual(result["test_corruption"]["kind"], "none")

    def test_missingness_routing_uses_clean_prediction_for_clean_samples(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            detector = root / "detector"
            classifier = root / "classifier"
            write_run(detector, "a" * 64, False, np.asarray([0, 0, 0, 0]))
            write_run(
                classifier,
                "a" * 64,
                True,
                np.asarray([1, 1, 0, 0]),
                missing=np.asarray([False, True, True, True]),
            )
            result = evaluate_pair(
                detector, classifier, prediction_routing="missingness"
            )
            self.assertEqual(
                result["decision_architecture"]["routed_sample_count"], 3
            )
            self.assertEqual(result["dual_path_report"]["known_macro_f1"], 1.0)

    def test_selective_routing_uses_only_requested_modality(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            detector = root / "detector"
            classifier = root / "classifier"
            view_missing = np.asarray(
                [
                    [True, False, False],
                    [False, True, False],
                    [False, False, False],
                    [False, False, False],
                ]
            )
            write_run(detector, "a" * 64, False, np.asarray([0, 0, 0, 0]))
            write_run(
                classifier,
                "a" * 64,
                True,
                np.asarray([1, 1, 0, 0]),
                missing=view_missing.any(axis=1),
                view_missing=view_missing,
            )
            result = evaluate_pair(
                detector,
                classifier,
                prediction_routing="missingness",
                routing_modalities=(1,),
            )
            self.assertEqual(
                result["decision_architecture"]["routed_sample_count"], 1
            )
            self.assertEqual(
                result["decision_architecture"]["routing_modalities"], [1]
            )
            self.assertEqual(result["dual_path_report"]["known_macro_f1"], 1.0)


if __name__ == "__main__":
    unittest.main()
