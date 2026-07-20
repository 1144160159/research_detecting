from argparse import Namespace
import unittest

import numpy as np

from caeos.neural_open_set import CEACalibrator, NCICalibrator
from run_neural_baseline_matrix import build_experiments, command_for


class NCICEATests(unittest.TestCase):
    def test_nci_matches_official_centered_alignment_and_l1_formula(self):
        train = np.asarray([[1.0, 1.0], [3.0, 1.0]])
        weight = np.asarray([[2.0, 0.0], [0.0, 3.0]])
        embeddings = np.asarray([[3.0, 1.0], [2.0, 3.0]])
        logits = np.asarray([[4.0, 0.0], [0.0, 5.0]])

        calibrator = NCICalibrator(alpha=0.1)
        calibrator.fit(train, weight)

        np.testing.assert_allclose(
            calibrator.knownness(embeddings, logits),
            np.asarray([2.4, 3.5]),
        )
        np.testing.assert_allclose(
            calibrator.score(embeddings, logits),
            np.asarray([-2.4, -3.5]),
        )
        self.assertEqual(calibrator.evidence()["fit_split"], "known_only_train")
        self.assertFalse(calibrator.evidence()["unknown_or_test_labels_used"])

    def test_nci_is_finite_at_training_mean(self):
        calibrator = NCICalibrator(alpha=0.1)
        calibrator.fit(
            np.asarray([[1.0, 1.0], [3.0, 1.0]]),
            np.eye(2),
        )
        risk = calibrator.score(
            np.asarray([[2.0, 1.0]]), np.asarray([[1.0, 0.0]])
        )
        np.testing.assert_allclose(risk, np.asarray([-0.3]))

    def test_cea_matches_official_validation_threshold_and_scale_formula(self):
        embeddings = np.asarray([[0.0, 1.0], [2.0, 3.0]])
        base_risk = np.asarray([-2.0, -4.0])
        calibrator = CEACalibrator(
            percentile=50.0,
            addition_coefficient=10.0,
            threshold_caution_coefficient=1.0,
        )

        calibrator.fit(embeddings, base_risk)

        expected_added_mean = np.sqrt(2.5) / 2.0
        expected_coefficient = 10.0 * 3.0 / (expected_added_mean + 0.1)
        self.assertAlmostEqual(calibrator.threshold, 1.5)
        self.assertAlmostEqual(calibrator.coefficient, expected_coefficient)
        np.testing.assert_allclose(
            calibrator.score(embeddings, base_risk),
            base_risk
            + expected_coefficient * np.asarray([0.0, np.sqrt(2.5)]),
        )
        self.assertEqual(
            calibrator.evidence()["fit_split"], "known_only_validation"
        )
        self.assertFalse(calibrator.evidence()["unknown_or_test_labels_used"])

    def test_cea_only_adds_risk_above_the_fitted_activation_threshold(self):
        calibrator = CEACalibrator(
            percentile=100.0,
            addition_coefficient=1.0,
            threshold_caution_coefficient=1.0,
        )
        calibrator.fit(np.asarray([[0.0, 1.0], [1.0, 2.0]]), np.ones(2))
        score = calibrator.score(
            np.asarray([[2.0, 2.0], [5.0, 2.0]]), np.zeros(2)
        )
        self.assertEqual(score[0], 0.0)
        self.assertGreater(score[1], score[0])

    def test_matrix_freezes_official_nci_and_cea_defaults(self):
        args = Namespace(
            suite="hikari",
            scenarios="probing",
            models="nci,nci_cea,energy_cea",
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
        commands = {
            experiment.model: command_for(experiment, args)
            for experiment in build_experiments(args)
        }

        self.assertEqual(
            commands["nci"][commands["nci"].index("--nci-alpha") + 1],
            "0.0001",
        )
        for model in ("energy_cea", "nci_cea"):
            command = commands[model]
            self.assertEqual(command[command.index("--cea-percentile") + 1], "99.9")
            self.assertEqual(
                command[command.index("--cea-addition-coefficient") + 1], "10"
            )
            self.assertEqual(
                command[
                    command.index("--cea-threshold-caution-coefficient") + 1
                ],
                "1.1",
            )
            self.assertEqual(command[command.index("--epochs") + 1], "35")


if __name__ == "__main__":
    unittest.main()
