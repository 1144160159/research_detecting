from __future__ import annotations

import unittest

import numpy as np

from caeos.hybrid import ConflictAwareHybridClassifier
from caeos.hybrid_open_set import (
    ClassConditionalDiagonalDistance,
    hybrid_open_set_components,
)
from train_hybrid_open_set import (
    compose_structural_inputs,
    structural_support_risk_name,
    structural_support_risk_pairs,
)


class StructuralScopeTest(unittest.TestCase):
    def test_scope_composition_separates_model_and_support_features(self):
        raw = [np.ones((4, 2)), np.full((4, 3), 2.0)]
        structural = np.full((4, 8), 3.0)

        full_views, full_support, full_count = compose_structural_inputs(
            raw, structural, "full"
        )
        self.assertEqual(len(full_views), 3)
        self.assertEqual(full_support.shape, (4, 13))
        self.assertIsNone(full_count)

        evidence_views, evidence_support, evidence_count = compose_structural_inputs(
            raw, structural, "evidence"
        )
        self.assertEqual(len(evidence_views), 3)
        self.assertEqual(evidence_support.shape, (4, 5))
        self.assertEqual(evidence_count, 2)

        support_views, support_values, support_count = compose_structural_inputs(
            raw, structural, "support"
        )
        self.assertEqual(len(support_views), 2)
        self.assertEqual(support_values.shape, (4, 13))
        self.assertIsNone(support_count)

    def test_evidence_only_view_does_not_change_global_probability(self):
        rng = np.random.RandomState(17)
        train_raw = [rng.normal(size=(80, 2)), rng.normal(size=(80, 3))]
        validation_raw = [rng.normal(size=(30, 2)), rng.normal(size=(30, 3))]
        train_labels = (train_raw[0][:, 0] + train_raw[1][:, 0] > 0).astype(int)
        validation_labels = (
            validation_raw[0][:, 0] + validation_raw[1][:, 0] > 0
        ).astype(int)
        train_auxiliary = rng.normal(size=(80, 4))
        validation_auxiliary = rng.normal(size=(30, 4))
        model = ConflictAwareHybridClassifier(
            estimators=8,
            seed=17,
            jobs=1,
            global_view_count=2,
        )
        model.fit(
            [*train_raw, train_auxiliary],
            train_labels,
            [*validation_raw, validation_auxiliary],
            validation_labels,
        )
        original = model._global_probability([*validation_raw, validation_auxiliary])
        changed = model._global_probability(
            [*validation_raw, validation_auxiliary + 1000.0]
        )
        np.testing.assert_allclose(original, changed)

        raw_values = np.concatenate(train_raw, axis=1)
        distance = ClassConditionalDiagonalDistance()
        distance.fit(raw_values, train_labels)
        components, probability = hybrid_open_set_components(
            model,
            [*validation_raw, validation_auxiliary],
            distance,
            np.concatenate(validation_raw, axis=1),
        )
        self.assertEqual(probability.shape, (30, 2))
        self.assertEqual(components["distance"].shape, (30,))

    def test_zero_weight_is_independent_of_structural_values(self):
        rng = np.random.RandomState(23)
        train_views = [rng.normal(size=(60, 2)), rng.normal(size=(60, 3))]
        validation_views = [rng.normal(size=(20, 2)), rng.normal(size=(20, 3))]
        test_views = [rng.normal(size=(25, 2)), rng.normal(size=(25, 3))]
        labels = np.asarray([0] * 30 + [1] * 30)
        train_structural = rng.normal(size=(60, 8))
        validation_structural = rng.normal(size=(20, 8))
        test_structural = rng.normal(size=(25, 8))
        first = structural_support_risk_pairs(
            train_views,
            labels,
            validation_views,
            test_views,
            train_structural,
            validation_structural,
            test_structural,
            (0.0,),
            anchor_index=0,
            anchor_weight=0.15,
        )[structural_support_risk_name(0.0)]
        second = structural_support_risk_pairs(
            train_views,
            labels,
            validation_views,
            test_views,
            train_structural + 1000.0,
            validation_structural - 1000.0,
            test_structural + 500.0,
            (0.0,),
            anchor_index=0,
            anchor_weight=0.15,
        )[structural_support_risk_name(0.0)]
        np.testing.assert_allclose(first[0], second[0])
        np.testing.assert_allclose(first[1], second[1])


if __name__ == "__main__":
    unittest.main()
