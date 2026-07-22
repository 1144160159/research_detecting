from __future__ import annotations

import argparse
from pathlib import Path
import tempfile
import unittest

import numpy as np

from evaluate_conflict_topology_copula import evaluate


class ConflictTopologyEvaluatorTests(unittest.TestCase):
    def _write_inputs(self, root: Path, unknown: np.ndarray) -> tuple[Path, Path]:
        rng = np.random.RandomState(29)
        validation_count, test_count, views, classes = 60, 24, 3, 3

        def probability(count, shape):
            raw = rng.uniform(0.05, 1.0, size=(count, *shape))
            return raw / raw.sum(axis=-1, keepdims=True)

        def conflict(count):
            raw = rng.uniform(0.0, 0.7, size=(count, views, views))
            raw = 0.5 * (raw + raw.transpose(0, 2, 1))
            raw[:, np.arange(views), np.arange(views)] = 0.0
            return raw

        evidence = root / "evidence.npz"
        np.savez_compressed(
            evidence,
            validation_view_probability=probability(validation_count, (views, classes)),
            test_view_probability=probability(test_count, (views, classes)),
            validation_view_reliability=rng.uniform(0.2, 1.0, (validation_count, views)),
            test_view_reliability=rng.uniform(0.2, 1.0, (test_count, views)),
            validation_pairwise_conflict=conflict(validation_count),
            test_pairwise_conflict=conflict(test_count),
            validation_global_probability=probability(validation_count, (classes,)),
            test_global_probability=probability(test_count, (classes,)),
            validation_view_fused_probability=probability(validation_count, (classes,)),
            test_view_fused_probability=probability(test_count, (classes,)),
            validation_selected_risk=rng.uniform(0.0, 1.0, validation_count),
            test_selected_risk=rng.uniform(0.0, 1.0, test_count),
            selected_risk_name=np.asarray("cauchy_modality_support_union"),
        )
        scores = root / "scores.npz"
        np.savez_compressed(
            scores,
            validation_labels=np.repeat(np.arange(classes), validation_count // classes),
            test_labels=np.tile(np.arange(classes), test_count // classes),
            test_unknown=unknown,
            test_prediction=np.tile(np.arange(classes), test_count // classes),
        )
        return evidence, scores

    @staticmethod
    def _args(evidence: Path, scores: Path, output: Path) -> argparse.Namespace:
        return argparse.Namespace(
            evidence_package=evidence,
            scores=scores,
            output_dir=output,
            protocol_manifest_sha256="a" * 64,
            suite="synthetic",
            scenario="held_out",
            seed=7,
            alpha=0.25,
            calibration_fraction=0.4,
            split_seed=229,
            known_rejection_quantile=0.95,
        )

    def test_test_labels_do_not_change_candidate_risk(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            unknown_a = np.asarray([False, True] * 12)
            evidence, scores_a = self._write_inputs(root, unknown_a)
            first = evaluate(self._args(evidence, scores_a, root / "first"))
            with np.load(root / "first" / "scores.npz") as saved:
                first_risk = saved["test_candidate_risk"].copy()

            unknown_b = ~unknown_a
            _, scores_b = self._write_inputs(root, unknown_b)
            second = evaluate(self._args(evidence, scores_b, root / "second"))
            with np.load(root / "second" / "scores.npz") as saved:
                second_risk = saved["test_candidate_risk"].copy()

            np.testing.assert_allclose(first_risk, second_risk, atol=0.0, rtol=0.0)
            self.assertTrue(first["diagnostics"]["prediction_array_equal"])
            self.assertTrue(second["diagnostics"]["prediction_array_equal"])
            self.assertEqual(
                first["diagnostics"]["known_macro_f1_absolute_difference"], 0.0
            )


if __name__ == "__main__":
    unittest.main()
