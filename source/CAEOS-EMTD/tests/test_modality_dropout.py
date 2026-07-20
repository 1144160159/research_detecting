from __future__ import annotations

import unittest

import numpy as np

from caeos.modality_dropout import (
    ModalityDropoutHybridClassifier,
    build_weighted_modality_dropout_training,
)


class ModalityDropoutTests(unittest.TestCase):
    def test_balanced_missing_blocks_and_weights(self) -> None:
        views = [np.ones((6, 2)), np.full((6, 3), 2.0), np.full((6, 1), 3.0)]
        labels = np.arange(6) % 2
        augmented, augmented_labels, weights, metadata = (
            build_weighted_modality_dropout_training(
                views, labels, copies=1, augmentation_weight=0.75
            )
        )
        self.assertEqual([value.shape[0] for value in augmented], [24, 24, 24])
        np.testing.assert_array_equal(augmented_labels, np.tile(labels, 4))
        self.assertTrue(np.all(augmented[0][6:12] == 0.0))
        self.assertTrue(np.all(augmented[1][12:18] == 0.0))
        self.assertTrue(np.all(augmented[2][18:24] == 0.0))
        self.assertAlmostEqual(weights[:6].sum(), 6.0)
        self.assertAlmostEqual(weights[6:].sum(), 4.5)
        self.assertEqual(metadata["augmented_rows"], 18)
        self.assertFalse(metadata["unknown_or_test_labels_used"])

    def test_zero_copies_is_clean_identity(self) -> None:
        views = [np.arange(12).reshape(6, 2), np.ones((6, 1))]
        labels = np.arange(6) % 2
        augmented, augmented_labels, weights, metadata = (
            build_weighted_modality_dropout_training(views, labels, 0, 1.0)
        )
        for original, result in zip(views, augmented):
            np.testing.assert_array_equal(original, result)
        np.testing.assert_array_equal(labels, augmented_labels)
        np.testing.assert_array_equal(weights, np.ones(6))
        self.assertFalse(metadata["enabled"])

    def test_field_dropout_is_deterministic_and_distributed_across_views(self) -> None:
        views = [np.ones((20, 4)), np.full((20, 3), 2.0)]
        labels = np.arange(20) % 2
        first = build_weighted_modality_dropout_training(
            views,
            labels,
            copies=0,
            augmentation_weight=0.5,
            field_dropout_severities=(0.25, 0.5, 0.75),
            seed=19,
        )
        second = build_weighted_modality_dropout_training(
            views,
            labels,
            copies=0,
            augmentation_weight=0.5,
            field_dropout_severities=(0.25, 0.5, 0.75),
            seed=19,
        )
        for left, right in zip(first[0], second[0]):
            np.testing.assert_array_equal(left, right)
        self.assertEqual(first[3]["augmentation_block_count"], 6)
        self.assertEqual(first[3]["augmented_rows"], 120)
        self.assertAlmostEqual(first[2][20:].sum(), 10.0)
        self.assertGreater(sum(first[3]["affected_entries_by_block"].values()), 0)

    def test_classifier_preserves_clean_specialist_training(self) -> None:
        rng = np.random.RandomState(17)
        labels = np.arange(180) % 3
        first = rng.normal(labels[:, None], 0.4, size=(180, 4))
        second = rng.normal(labels[:, None], 0.4, size=(180, 3))
        model = ModalityDropoutHybridClassifier(
            estimators=10,
            seed=17,
            jobs=1,
            modality_dropout_copies=1,
            modality_dropout_weight=1.0,
        )
        model.fit(
            [first[:120], second[:120]],
            labels[:120],
            [first[120:150], second[120:150]],
            labels[120:150],
        )
        clean = model.predict_proba([first[150:], second[150:]])
        missing = model.predict_proba([first[150:], np.zeros_like(second[150:])])
        self.assertEqual(clean.shape, (30, 3))
        self.assertEqual(missing.shape, (30, 3))
        self.assertTrue(np.allclose(clean.sum(axis=1), 1.0))
        self.assertTrue(np.allclose(missing.sum(axis=1), 1.0))
        self.assertTrue(model.augmentation_metadata["enabled"])
        self.assertEqual(len(model.view_models), 2)

    def test_validation_corruption_evidence_uses_known_validation_only(self) -> None:
        rng = np.random.RandomState(23)
        labels = np.arange(150) % 3
        first = rng.normal(labels[:, None], 0.5, size=(150, 4))
        second = rng.normal(labels[:, None], 0.5, size=(150, 3))
        model = ModalityDropoutHybridClassifier(
            estimators=10,
            seed=23,
            jobs=1,
            modality_dropout_copies=0,
            field_dropout_severities=(0.25, 0.5),
        )
        model.fit(
            [first[:90], second[:90]],
            labels[:90],
            [first[90:120], second[90:120]],
            labels[90:120],
        )
        evidence = model.validation_scores["field_dropout_validation"]
        self.assertEqual(len(evidence["scores"]), 4)
        self.assertTrue(evidence["uses_known_validation_labels_only"])
        self.assertFalse(evidence["unknown_or_test_labels_used"])
        self.assertIsNotNone(evidence["minimax_objective"])
        self.assertIn("clean_delta_from_baseline", model.validation_scores)

    def test_invalid_settings_are_rejected(self) -> None:
        views = [np.ones((3, 1)), np.ones((3, 1))]
        labels = np.arange(3)
        with self.assertRaises(ValueError):
            build_weighted_modality_dropout_training(views, labels, -1, 1.0)
        with self.assertRaises(ValueError):
            build_weighted_modality_dropout_training(views, labels, 1, -0.1)
        with self.assertRaises(ValueError):
            build_weighted_modality_dropout_training(
                views, labels, 0, 1.0, field_dropout_severities=(1.0,)
            )


if __name__ == "__main__":
    unittest.main()
