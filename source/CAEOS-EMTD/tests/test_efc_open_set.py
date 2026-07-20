from __future__ import annotations

import unittest
from argparse import Namespace
from importlib.util import find_spec

import numpy as np

from run_neural_baseline_matrix import build_experiments, command_for
from train_efc_open_set import EFC_UPSTREAM_COMMIT, energy_margin_risk


class EfcOpenSetTest(unittest.TestCase):
    def matrix_arguments(self) -> Namespace:
        return Namespace(
            suite="extended",
            scenarios="fingerprinting,bot,geodo",
            models="efc",
            seeds="7",
            workers=1,
            epochs=0,
            patience=10,
            doh_max_per_class=100,
            mal_max_per_class=100,
            hikari_max_per_class=100,
            nf_unsw_max_per_class=100,
            cicids2017_max_per_class=100,
            cic_iot2023_max_per_class=100,
            cic_ton_iot_max_per_class=100,
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
            cic_iot2023_csv="cic_iot2023.csv",
            cic_iot2023_cache_dir="",
            cic_ton_iot_csv="cic_ton_iot.csv",
            cic_ton_iot_cache_dir="",
            edge_iiot_csv="edge.csv",
            edge_iiot_cache_dir="",
            nf_cse_csv="nf_cse.csv",
            nf_cse_cache_dir="",
            ustc_csv="ustc.csv",
            ustc_cache_dir="",
            output_root="runs/efc",
            tao_stage1_adapter=False,
            tao_blood_estimators=50,
            efc_jobs=8,
        )

    def test_uses_predicted_class_energy_margin(self) -> None:
        class Estimator:
            def __init__(self, cutoff: float) -> None:
                self.cutoff_ = cutoff

        class Model:
            classes_ = np.asarray([0, 1, 2])
            estimators_ = [Estimator(10.0), Estimator(20.0), Estimator(30.0)]

        risk = energy_margin_risk(
            Model(),
            np.asarray([2, 0, 1]),
            np.asarray([35.0, 11.0, 22.0]),
        )
        np.testing.assert_allclose([5.0, 1.0, 2.0], risk)
        self.assertEqual(40, len(EFC_UPSTREAM_COMMIT))

    def test_rejects_binary_efc_model(self) -> None:
        class Estimator:
            cutoff_ = 1.0

        class Model:
            classes_ = np.asarray([0, 1])
            estimators_ = [Estimator()]

        with self.assertRaisesRegex(ValueError, "at least three known classes"):
            energy_margin_risk(
                Model(), np.asarray([0, 1]), np.asarray([1.0, 2.0])
            )

    def test_matrix_builds_pinned_efc_command(self) -> None:
        args = self.matrix_arguments()
        experiments = build_experiments(args)
        self.assertEqual(3, len(experiments))
        for experiment in experiments:
            command = command_for(experiment, args)
            self.assertEqual("train_efc_open_set.py", command[1])
            self.assertEqual("30", command[command.index("--n-bins") + 1])
            self.assertEqual("0.95", command[command.index("--known-acceptance") + 1])
            self.assertEqual("8", command[command.index("--jobs") + 1])

    @unittest.skipUnless(find_spec("efc"), "official EFC package is not installed")
    def test_official_extension_supports_threaded_parallel_prediction(self) -> None:
        from efc import EnergyBasedFlowClassifier
        from joblib import parallel_backend

        rng = np.random.default_rng(17)
        values = np.concatenate(
            [rng.normal(loc=float(label), size=(20, 4)) for label in range(3)]
        )
        labels = np.repeat(np.arange(3), 20)
        model = EnergyBasedFlowClassifier(n_bins=5, n_jobs=2)
        with parallel_backend("threading", n_jobs=2):
            model.fit(values, labels)
            prediction, energy = model.predict(values, return_energies=True)
        self.assertEqual((60,), prediction.shape)
        self.assertEqual((60,), energy.shape)
        self.assertTrue(np.isfinite(energy).all())


if __name__ == "__main__":
    unittest.main()
