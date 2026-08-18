from __future__ import annotations

import importlib.util
import unittest

import numpy as np

from train_strict_v4_dual_metric_contrastive_task_cuda import (
    apply_statistic_modality_dropout,
    attack_probability_variants,
    evaluation_statistics_for_dropout,
    leave_one_family_margin_loss,
    pseudo_family_for_step,
    supervised_contrastive_loss,
)


TORCH_AVAILABLE = importlib.util.find_spec("torch") is not None


class DualMetricContrastiveCudaTests(unittest.TestCase):
    def test_pseudo_family_rotation_is_deterministic(self) -> None:
        attack_classes = [1, 2, 4]
        self.assertEqual(1, pseudo_family_for_step(attack_classes, 0, 0))
        self.assertEqual(2, pseudo_family_for_step(attack_classes, 0, 1))
        self.assertEqual(4, pseudo_family_for_step(attack_classes, 1, 1))
        self.assertEqual(1, pseudo_family_for_step(attack_classes, 2, 1))

    def test_pseudo_family_requires_attack_class(self) -> None:
        with self.assertRaises(ValueError):
            pseudo_family_for_step([], 0, 0)

    def test_attack_probability_variants_are_bounded(self) -> None:
        family = np.asarray(
            [[0.8, 0.2], [0.3, 0.7]], dtype=np.float64
        )
        attack = np.asarray([0.1, 0.6], dtype=np.float64)
        variants = attack_probability_variants(family, attack, 0)
        self.assertEqual(
            {"attack_head", "family", "maximum", "noisy_or"},
            set(variants),
        )
        np.testing.assert_allclose(variants["family"], [0.2, 0.7])
        np.testing.assert_allclose(variants["maximum"], [0.2, 0.7])
        np.testing.assert_allclose(variants["noisy_or"], [0.28, 0.88])
        for values in variants.values():
            self.assertTrue(np.all((values >= 0.0) & (values <= 1.0)))

    @unittest.skipUnless(TORCH_AVAILABLE, "torch is unavailable")
    def test_contrastive_and_margin_losses_are_finite(self) -> None:
        import torch

        embeddings = torch.tensor(
            [
                [1.0, 0.0],
                [0.9, 0.1],
                [0.0, 1.0],
                [0.1, 0.9],
            ]
        )
        labels = torch.tensor([0, 0, 1, 1])
        contrastive = supervised_contrastive_loss(
            torch, embeddings, labels, 0.12
        )
        self.assertTrue(torch.isfinite(contrastive))
        self.assertGreaterEqual(float(contrastive), 0.0)
        cosine = torch.tensor(
            [
                [0.8, 0.1],
                [0.7, 0.2],
                [0.1, 0.9],
                [0.2, 0.8],
            ]
        )
        margin = leave_one_family_margin_loss(
            torch,
            cosine,
            labels,
            pseudo_family=1,
            known_margin=0.35,
            pseudo_unknown_margin=0.15,
        )
        self.assertTrue(torch.isfinite(margin))
        self.assertGreaterEqual(float(margin), 0.0)

    @unittest.skipUnless(TORCH_AVAILABLE, "torch is unavailable")
    def test_statistic_modality_dropout_boundaries(self) -> None:
        import torch

        statistics = torch.ones((4, 3))
        self.assertIs(
            statistics,
            apply_statistic_modality_dropout(torch, statistics, 0.0),
        )
        self.assertTrue(
            torch.equal(
                torch.zeros_like(statistics),
                apply_statistic_modality_dropout(torch, statistics, 1.0),
            )
        )
        with self.assertRaises(ValueError):
            apply_statistic_modality_dropout(torch, statistics, -0.1)
        with self.assertRaises(ValueError):
            apply_statistic_modality_dropout(torch, statistics, 1.1)

    @unittest.skipUnless(TORCH_AVAILABLE, "torch is unavailable")
    def test_sequence_only_evaluation_zeros_statistics(self) -> None:
        import torch

        statistics = torch.ones((4, 3))
        self.assertIs(
            statistics,
            evaluation_statistics_for_dropout(torch, statistics, 0.5),
        )
        self.assertTrue(
            torch.equal(
                torch.zeros_like(statistics),
                evaluation_statistics_for_dropout(torch, statistics, 1.0),
            )
        )


if __name__ == "__main__":
    unittest.main()
