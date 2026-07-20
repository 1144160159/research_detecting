from __future__ import annotations

import json
import tempfile
from pathlib import Path
import unittest

import numpy as np

from analyze_strict_v4_conflict_metrics import (
    conflict_metric_vectors,
    logistic_likelihood_gain,
    scenario_analysis,
)
from create_strict_v4_conflict_metric_protocol import (
    create_protocol,
    freeze_or_validate,
)


class ConflictMetricAnalysisTests(unittest.TestCase):
    def test_identical_views_have_zero_disagreement(self) -> None:
        probability = np.asarray([[[0.8, 0.2], [0.8, 0.2], [0.8, 0.2]]])
        evidence = 0.7 * probability
        reliability = np.asarray([[0.8, 0.9, 1.0]])
        result = conflict_metric_vectors(probability, evidence, reliability)
        for name in (
            "d1_label_disagreement",
            "d2_cosine_distance",
            "d3_jensen_shannon",
            "d4_symmetric_kl",
        ):
            self.assertAlmostEqual(float(result[name][0]), 0.0)
        # DS off-diagonal mass also measures within-opinion ambiguity.
        self.assertGreater(result["d5_raw_ds_conflict"][0], 0.0)
        self.assertGreater(result["d6_conditional_ds_conflict"][0], 0.0)

    def test_conditional_conflict_decouples_committed_mass(self) -> None:
        probability = np.asarray(
            [
                [[0.9, 0.1], [0.1, 0.9]],
                [[0.9, 0.1], [0.1, 0.9]],
            ]
        )
        evidence = probability * np.asarray([[[0.1], [0.1]], [[0.9], [0.9]]])
        reliability = np.ones((2, 2))
        result = conflict_metric_vectors(probability, evidence, reliability)
        self.assertLess(
            result["d5_raw_ds_conflict"][0],
            result["d5_raw_ds_conflict"][1],
        )
        self.assertAlmostEqual(
            result["d6_conditional_ds_conflict"][0],
            result["d6_conditional_ds_conflict"][1],
        )

    def test_divergences_are_finite_with_zero_probabilities(self) -> None:
        probability = np.asarray([[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]])
        evidence = 0.9 * probability
        reliability = np.ones((1, 2))
        result = conflict_metric_vectors(probability, evidence, reliability)
        self.assertTrue(
            all(np.isfinite(value).all() for value in result.values())
        )
        self.assertGreater(result["d3_jensen_shannon"][0], 0.99)

    def test_scenario_analysis_detects_conflict_signal(self) -> None:
        probability = np.asarray(
            [
                [[0.9, 0.1], [0.85, 0.15]],
                [[0.8, 0.2], [0.75, 0.25]],
                [[0.9, 0.1], [0.1, 0.9]],
                [[0.85, 0.15], [0.15, 0.85]],
            ]
        )
        evidence = 0.8 * probability
        reliability = np.ones((4, 2))
        uncertainty = np.full((4, 2), 0.2)
        unknown = np.asarray([False, False, True, True])
        result = scenario_analysis(
            probability, evidence, reliability, uncertainty, unknown
        )
        self.assertEqual(result["d1_label_disagreement"]["unknown_auroc"], 1.0)
        self.assertGreater(
            result["d6_conditional_ds_conflict"]["unknown_auroc"], 0.9
        )

    def test_logistic_gain_is_positive_for_independent_signal(self) -> None:
        rng = np.random.default_rng(7)
        unknown = np.repeat([0, 1], 100)
        uncertainty = rng.normal(size=200)
        metric = unknown + rng.normal(scale=0.1, size=200)
        result = logistic_likelihood_gain(uncertainty, metric, unknown)
        self.assertGreater(result["log_likelihood_gain"], 0.1)
        self.assertGreater(result["metric_coefficient"], 0)
        self.assertLess(result["likelihood_ratio_pvalue"], 0.05)

    def test_protocol_freeze_and_source_drift_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in (
                "create_strict_v4_conflict_metric_protocol.py",
                "analyze_strict_v4_conflict_metrics.py",
                "scripts/run_strict_v4_conflict_metric_analysis.sh",
            ):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(name + "\n", encoding="ascii")
            run_root = root / "runs"
            for index in range(102):
                scenario = run_root / ("suite%d" % (index % 7)) / (
                    "scenario%d_seed7" % index
                )
                scenario.mkdir(parents=True)
                np.savez_compressed(scenario / "evidence_package.npz", value=[index])
                np.savez_compressed(scenario / "scores.npz", value=[index])
                (scenario / "metrics.json").write_text(
                    json.dumps({"index": index}), encoding="ascii"
                )
            protocol = create_protocol(root, run_root, 0)
            output = root / "result" / "protocol_manifest.json"
            freeze_or_validate(output, protocol, 0)
            self.assertEqual(protocol["expected_scenarios"], 102)
            (run_root / "suite0" / "scenario0_seed7" / "metrics.json").write_text(
                '{"changed":true}', encoding="ascii"
            )
            changed = create_protocol(root, run_root, 0)
            with self.assertRaisesRegex(ValueError, "differs from current evidence"):
                freeze_or_validate(output, changed, 0)


if __name__ == "__main__":
    unittest.main()
