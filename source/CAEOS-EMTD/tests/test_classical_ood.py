from __future__ import annotations

import unittest
from argparse import Namespace

import numpy as np

from run_neural_baseline_matrix import build_experiments, command_for
from train_classical_ood import balanced_subsample_indices, detector_risks


class ClassicalOodTest(unittest.TestCase):
    def matrix_arguments(self) -> Namespace:
        return Namespace(
            suite="extended",
            scenarios="fingerprinting,bot,zeus",
            models="classical_ood",
            seeds="7",
            workers=1,
            epochs=0,
            patience=10,
            doh_max_per_class=100,
            mal_max_per_class=100,
            hikari_max_per_class=100,
            nf_unsw_max_per_class=100,
            cicids2017_max_per_class=100,
            edge_iiot_max_per_class=100,
            nf_cse_max_per_class=100,
            ustc_max_per_class=100,
            doh_csv="doh.csv",
            mal_csv="mal.csv",
            hikari_csv="hikari.csv",
            nf_unsw_csv="nf_unsw.csv",
            nf_unsw_cache_dir="",
            cicids2017_csv="cicids.csv",
            cicids2017_cache_dir="",
            edge_iiot_csv="edge.csv",
            edge_iiot_cache_dir="",
            nf_cse_csv="nf_cse.csv",
            nf_cse_cache_dir="",
            ustc_csv="ustc.csv",
            ustc_cache_dir="",
            output_root="runs/classical",
        )

    def test_balanced_subsample_is_deterministic_and_covers_classes(self) -> None:
        labels = np.repeat(np.arange(4), 20)
        first = balanced_subsample_indices(labels, 24, 7)
        second = balanced_subsample_indices(labels, 24, 7)
        np.testing.assert_array_equal(first, second)
        self.assertEqual(24, len(first))
        self.assertEqual({0, 1, 2, 3}, set(labels[first]))
        self.assertEqual([6, 6, 6, 6], np.bincount(labels[first]).tolist())

    def test_four_detectors_emit_finite_aligned_risks(self) -> None:
        rng = np.random.default_rng(11)
        fit = rng.normal(size=(80, 6))
        validation = rng.normal(size=(20, 6))
        test = np.concatenate(
            [rng.normal(size=(20, 6)), rng.normal(loc=5.0, size=(10, 6))]
        )
        args = Namespace(
            isolation_trees=20,
            seed=7,
            ocsvm_nu=0.05,
            lof_neighbors=10,
            pca_components=3,
        )
        risks, models, timings = detector_risks(fit, validation, test, args)
        self.assertEqual(
            {
                "isolation_forest",
                "one_class_svm",
                "local_outlier_factor",
                "pca_reconstruction",
            },
            set(risks),
        )
        self.assertEqual(set(risks), set(models))
        self.assertEqual(set(risks), set(timings))
        for validation_risk, test_risk in risks.values():
            self.assertEqual((20,), validation_risk.shape)
            self.assertEqual((30,), test_risk.shape)
            self.assertTrue(np.isfinite(validation_risk).all())
            self.assertTrue(np.isfinite(test_risk).all())
            self.assertGreater(test_risk[-10:].mean(), test_risk[:20].mean())

    def test_matrix_runs_one_shared_job_for_four_reports(self) -> None:
        args = self.matrix_arguments()
        experiments = build_experiments(args)
        self.assertEqual(3, len(experiments))
        for experiment in experiments:
            command = command_for(experiment, args)
            self.assertEqual("train_classical_ood.py", command[1])
            self.assertEqual(
                "5000", command[command.index("--detector-max-samples") + 1]
            )
            self.assertEqual("0.05", command[command.index("--ocsvm-nu") + 1])

if __name__ == "__main__":
    unittest.main()
