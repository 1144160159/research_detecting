from argparse import Namespace
import unittest

import numpy as np

from caeos.scale import (
    OFFICIAL_PERCENTILE,
    SCALECalibrator,
    scale_activations,
    scale_factors,
)
from run_neural_baseline_matrix import build_experiments, command_for


class SCALEFormulaTests(unittest.TestCase):
    def test_formula_uses_top_mass_but_scales_every_activation(self):
        activations = np.asarray([[1.0, 2.0, 3.0, 4.0]])
        expected_factor = np.exp(10.0 / 7.0)

        factors = scale_factors(activations, percentile=50.0)
        scaled = scale_activations(activations, percentile=50.0)

        np.testing.assert_allclose(factors, [expected_factor])
        np.testing.assert_allclose(scaled, activations * expected_factor)
        self.assertGreater(scaled[0, 0], 0.0)
        np.testing.assert_array_equal(activations, [[1.0, 2.0, 3.0, 4.0]])

    def test_zero_percentile_has_official_exp_one_multiplier(self):
        activations = np.asarray([[0.5, 1.5, 2.0]])
        np.testing.assert_allclose(
            scale_factors(activations, percentile=0.0), [np.e]
        )

    def test_low_dimension_keeps_at_least_one_top_activation(self):
        activations = np.asarray([[1.0, 1.0]])
        np.testing.assert_allclose(
            scale_factors(activations, percentile=85.0), [np.exp(2.0)]
        )

    def test_zero_mass_is_neutral_and_gelu_negatives_are_rectified(self):
        activations = np.asarray([[0.0, 0.0], [-2.0, 2.0]])
        factors = scale_factors(activations, percentile=50.0)
        scaled = scale_activations(activations, percentile=50.0)

        np.testing.assert_allclose(factors, [1.0, np.e])
        np.testing.assert_allclose(scaled, [[0.0, 0.0], [0.0, 2.0 * np.e]])
        with self.assertRaisesRegex(ValueError, "non-negative"):
            scale_activations(
                activations, percentile=50.0, rectify_negative=False
            )

    def test_undefined_and_nonfinite_inputs_are_rejected(self):
        with self.assertRaisesRegex(ValueError, r"\[0, 100\)"):
            scale_factors(np.ones((1, 4)), percentile=100.0)
        with self.assertRaisesRegex(ValueError, "finite"):
            scale_factors(np.asarray([[1.0, np.nan]]), percentile=50.0)


class SCALECalibratorTests(unittest.TestCase):
    def test_scaled_logits_energy_and_prediction_match_formula(self):
        activations = np.asarray([[2.0, 1.0], [1.0, 2.0]])
        labels = np.asarray([0, 1])
        weight = np.eye(2)
        calibrator = SCALECalibrator(percentile=0.0, rectify_negative=False)
        calibrator.fit(activations, labels, weight)

        expected_logits = np.e * activations
        maximum = expected_logits.max(axis=1)
        expected_risk = -(
            maximum
            + np.log(np.exp(expected_logits - maximum[:, None]).sum(axis=1))
        )

        np.testing.assert_allclose(calibrator.logits(activations), expected_logits)
        np.testing.assert_allclose(calibrator.score(activations), expected_risk)
        np.testing.assert_array_equal(calibrator.predict(activations), labels)

    def test_positive_scaling_preserves_bias_free_logit_order(self):
        activations = np.asarray([[1.0, 4.0, 2.0], [3.0, 1.0, 2.0]])
        labels = np.asarray([0, 1])
        weight = np.asarray([[2.0, 0.0, 1.0], [0.0, 1.5, 0.5]])
        original_prediction = (activations @ weight.T).argmax(axis=1)
        calibrator = SCALECalibrator(percentile=50.0, rectify_negative=False)
        calibrator.fit(activations, labels, weight)

        np.testing.assert_array_equal(
            calibrator.predict(activations), original_prediction
        )

    def test_optional_percentile_search_uses_known_validation_only(self):
        activations = np.asarray([[1.0, 1.0]])
        labels = np.asarray([0])
        weight = np.asarray([[1.0, 0.0], [0.0, 0.0]])
        bias = np.asarray([-3.0, 0.0])
        calibrator = SCALECalibrator(
            percentile_candidates=(0.0, 50.0),
            rectify_negative=False,
        )
        calibrator.fit(activations, labels, weight, bias)

        self.assertEqual(calibrator.percentile, 50.0)
        evidence = calibrator.evidence()
        self.assertEqual(evidence["fit_split"], "known_only_validation")
        self.assertFalse(evidence["unknown_or_test_labels_used"])
        self.assertFalse(evidence["auxiliary_ood_used"])
        self.assertEqual(
            evidence["percentile_source"],
            "selected_on_known_validation_accuracy_then_nll",
        )
        self.assertEqual(evidence["validation_embedding_count"], 1)

    def test_default_evidence_distinguishes_paper_default_and_adaptation(self):
        activations = np.asarray([[1.0, -0.1], [0.2, 1.0]])
        labels = np.asarray([0, 1])
        calibrator = SCALECalibrator()
        calibrator.fit(activations, labels, np.eye(2))
        evidence = calibrator.evidence()

        self.assertEqual(evidence["official_default_percentile"], 85.0)
        self.assertEqual(evidence["selected_percentile"], OFFICIAL_PERCENTILE)
        self.assertEqual(
            evidence["percentile_source"],
            "fixed_paper_default_without_ood_sweep",
        )
        self.assertEqual(
            evidence["adaptation"]["activation_policy"],
            "relu_clamp_for_gelu_penultimate",
        )
        self.assertEqual(
            evidence["adaptation"]["risk_orientation"],
            "negative_energy_larger_is_more_unknown",
        )

    def test_fit_and_inference_contract_validation(self):
        calibrator = SCALECalibrator()
        with self.assertRaisesRegex(RuntimeError, "not been fitted"):
            calibrator.score(np.ones((1, 2)))
        with self.assertRaisesRegex(ValueError, "integers"):
            calibrator.fit(
                np.ones((2, 2)),
                np.asarray([0.0, 1.0]),
                np.eye(2),
            )
        calibrator.fit(
            np.ones((2, 2)), np.asarray([0, 1]), np.eye(2)
        )
        with self.assertRaisesRegex(ValueError, "dimensions differ"):
            calibrator.score(np.ones((1, 3)))

    def test_mlp_matrix_freezes_modern_postprocessor_defaults(self):
        args = Namespace(
            suite="hikari",
            scenarios="probing",
            models="mlp",
            seeds="7",
            workers=1,
            epochs=0,
            patience=10,
            doh_max_per_class=20,
            mal_max_per_class=20,
            hikari_max_per_class=20,
            doh_csv="doh.csv",
            mal_csv="mal.csv",
            hikari_csv="hikari.csv",
            output_root="runs/test",
        )
        experiment = build_experiments(args)[0]
        command = command_for(experiment, args)

        self.assertEqual(command[command.index("--nci-alpha") + 1], "0.0001")
        self.assertEqual(command[command.index("--cea-percentile") + 1], "99.9")
        self.assertEqual(command[command.index("--scale-percentile") + 1], "85")
        self.assertEqual(command[command.index("--scale-temperature") + 1], "1")


if __name__ == "__main__":
    unittest.main()
