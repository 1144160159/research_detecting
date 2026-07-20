from __future__ import annotations

import argparse
import unittest
from unittest import mock

import numpy as np
import torch

from caeos.aegis import (
    AEGISClassifier,
    AEGISKNN,
    produce_pseudo_labels,
    supervised_contrastive_loss,
)
from run_aegis_baseline_matrix import MODEL, command_for
from run_neural_baseline_matrix import Experiment


class AEGISAdapterTests(unittest.TestCase):
    def test_matrix_command_preserves_registered_scenario_and_safe_defaults(self) -> None:
        experiment = Experiment(
            suite="cic_iot2023",
            scenario="ddos_icmp_fragmentation",
            unknown_classes="DDoS-ICMP_Fragmentation",
            model=MODEL,
            seed=7,
            output_dir="runs/aegis-smoke",
        )
        args = argparse.Namespace(epochs=0, patience=10)
        settings = (
            None,
            "cache.csv",
            "configs/cic_iot2023_strict.json",
            "Benign",
            "capture_grouped",
            1000,
        )
        with mock.patch(
            "run_aegis_baseline_matrix.suite_settings", return_value=settings
        ):
            command = command_for(experiment, args)

        self.assertIn("train_aegis_open_set.py", command)
        self.assertEqual(command[command.index("--unknown-classes") + 1], experiment.unknown_classes)
        self.assertEqual(command[command.index("--epochs") + 1], "50")
        self.assertEqual(command[command.index("--correction-start-epoch") + 1], "20")
        self.assertEqual(command[command.index("--split-strategy") + 1], "capture_grouped")
        self.assertEqual(command[command.index("--output-dir") + 1], experiment.output_dir)

    def test_model_preserves_batch_and_emits_official_embedding_width(self) -> None:
        model = AEGISClassifier((5, 7, 9), 4)
        result = model.forward_values(torch.randn(3, 21))
        self.assertEqual(tuple(result["logits"].shape), (3, 4))
        self.assertEqual(tuple(result["embedding"].shape), (3, 1024))
        self.assertEqual(tuple(result["detection_embedding"].shape), (3, 128))

    def test_contrastive_loss_is_finite_with_and_without_positive_pairs(self) -> None:
        values = torch.randn(4, 16, requires_grad=True)
        paired = supervised_contrastive_loss(
            values, torch.tensor([0, 0, 1, 1]), 0.07
        )
        singleton = supervised_contrastive_loss(
            values, torch.tensor([0, 1, 2, 3]), 0.07
        )
        self.assertTrue(torch.isfinite(paired))
        self.assertEqual(float(singleton.detach()), 0.0)
        (paired + singleton).backward()
        self.assertIsNotNone(values.grad)

    def test_pseudo_labels_and_knn_are_deterministic_and_nondegenerate(self) -> None:
        rng = np.random.default_rng(7)
        first = rng.normal(-1.0, 0.1, size=(20, 8))
        second = rng.normal(1.0, 0.1, size=(20, 8))
        values = np.vstack([first, second]).astype(np.float32)
        labels = np.array([0] * 20 + [1] * 20)
        pseudo = produce_pseudo_labels(
            values, labels, 2, prototypes=5, maximum_samples=20, seed=7
        )
        self.assertGreaterEqual(float((pseudo == labels).mean()), 0.95)
        detector = AEGISKNN(5).fit(values)
        known = detector.score(values[:4])
        far = detector.score(np.full((4, 8), 10.0, dtype=np.float32))
        self.assertGreater(float(far.mean()), float(known.mean()))


if __name__ == "__main__":
    unittest.main()
