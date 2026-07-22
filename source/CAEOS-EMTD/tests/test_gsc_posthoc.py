from __future__ import annotations

import unittest

import numpy as np

from caeos.gsc_posthoc import (
    gradient_short_circuit_logits,
    gsc_risk,
    mask_diagnostics,
    masked_coordinate_count,
)


class GSCPosthocTests(unittest.TestCase):
    def test_first_order_update_equals_exact_linear_head_forward(self) -> None:
        embedding = np.asarray([[1.0, -2.0, 0.5, 3.0]])
        weight = np.asarray([[0.1, 4.0, 0.2, -0.3], [2.0, 0.1, -0.5, 0.4]])
        bias = np.asarray([0.3, -0.2])
        logits = embedding @ weight.T + bias
        corrected, selected = gradient_short_circuit_logits(
            embedding, logits, weight, mask_ratio=0.25
        )
        modified = embedding.copy()
        modified[0, selected[0]] = 0.0
        expected = modified @ weight.T + bias
        np.testing.assert_allclose(corrected, expected, atol=1e-12, rtol=0.0)
        self.assertEqual(selected.shape, (1, 1))

    def test_mask_is_predicted_class_fixed_for_linear_head(self) -> None:
        embedding = np.asarray([[1.0, 2.0, 3.0, 4.0], [4.0, 3.0, 2.0, 1.0]])
        weight = np.asarray([[5.0, 0.1, 0.2, 0.3], [-5.0, 0.1, 0.2, 0.3]])
        logits = np.asarray([[3.0, 1.0], [2.0, 0.0]])
        risk, selected = gsc_risk(embedding, logits, weight, mask_ratio=0.25)
        diagnostic = mask_diagnostics(selected, logits.argmax(axis=1))
        self.assertTrue(np.isfinite(risk).all())
        self.assertTrue(diagnostic["mask_is_fixed_within_predicted_class"])
        self.assertTrue(diagnostic["linear_head_degeneracy_observed"])
        np.testing.assert_array_equal(selected[0], selected[1])

    def test_mask_count_uses_paper_default_floor_with_minimum_one(self) -> None:
        self.assertEqual(masked_coordinate_count(64, 0.05), 3)
        self.assertEqual(masked_coordinate_count(8, 0.05), 1)
        with self.assertRaises(ValueError):
            masked_coordinate_count(64, 0.0)


if __name__ == "__main__":
    unittest.main()
