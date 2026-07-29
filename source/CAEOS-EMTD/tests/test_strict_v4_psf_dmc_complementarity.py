from __future__ import annotations

import unittest

import numpy as np

from evaluate_strict_v4_psf_dmc_complementarity import (
    fusion_candidates,
    noisy_or,
    paired_signature_rows,
    select_by_validation,
)


class PsfDmcComplementarityTests(unittest.TestCase):
    def test_noisy_or_is_bounded_and_dominates_inputs(self) -> None:
        left = np.asarray([0.1, 0.7])
        right = np.asarray([0.4, 0.2])
        fused = noisy_or(left, right)
        self.assertTrue(np.all(fused >= left))
        self.assertTrue(np.all(fused >= right))
        self.assertTrue(np.all(fused <= 1.0))

    def test_candidate_space_is_frozen(self) -> None:
        values = np.asarray([0.1, 0.8])
        names = [name for name, _ in fusion_candidates(values, values)]
        self.assertEqual(
            [
                "psf_only",
                "dmc_only",
                "convex_psf_0p25",
                "convex_psf_0p50",
                "convex_psf_0p75",
                "maximum",
                "noisy_or",
            ],
            names,
        )

    def test_selection_uses_validation_attack_recall(self) -> None:
        labels = np.asarray([0] * 100 + [1] * 20)
        weak = np.asarray([0.01] * 100 + [0.01] * 20)
        strong = np.asarray([0.01] * 100 + [0.99] * 20)
        name, selected, summaries = select_by_validation(
            [("weak", weak), ("strong", strong)],
            labels,
            benign_index=0,
        )
        self.assertEqual("strong", name)
        self.assertEqual(1.0, selected["known_attack_recall"])
        self.assertEqual(2, len(summaries))

    def test_signature_pairing_preserves_duplicate_multiplicity(self) -> None:
        left, right, identities = paired_signature_rows(
            np.asarray(["b", "a", "a", "left-only"]),
            np.asarray(["a", "b", "a", "a", "right-only"]),
        )
        np.testing.assert_array_equal(left, [1, 2, 0])
        np.testing.assert_array_equal(right, [0, 2, 1])
        self.assertEqual(["a:0", "a:1", "b:0"], identities)


if __name__ == "__main__":
    unittest.main()
