from __future__ import annotations

import unittest

import numpy as np

from evaluate_strict_v4_fine_balanced_xgboost_development import (
    ATTACK_PROBABILITY_VARIANTS,
    prepared_for_variant,
)
from strict_v4_cicids2017_attack_family import ATTACK_FAMILIES
from strict_v4_cic_iot2023_attack_family import (
    ATTACK_FAMILIES as CIC_IOT2023_ATTACK_FAMILIES,
    FINE_TO_FAMILY as CIC_IOT2023_FINE_TO_FAMILY,
)
from train_strict_v4_fine_balanced_xgboost_task_cuda import (
    attack_probability_variants,
    family_labels,
    fine_classes_for_family,
    split_counts,
)


class FineBalancedXGBoostCudaTests(unittest.TestCase):
    def test_each_attack_family_has_disjoint_fine_classes(self) -> None:
        observed = set()
        for family in ATTACK_FAMILIES:
            fine_classes = fine_classes_for_family(family)
            self.assertTrue(fine_classes)
            self.assertFalse(observed.intersection(fine_classes))
            observed.update(fine_classes)
        self.assertNotIn("Benign", observed)
        self.assertEqual(14, len(observed))

    def test_cic_iot2023_attack_family_taxonomy_is_complete(self) -> None:
        observed = set()
        for family in CIC_IOT2023_ATTACK_FAMILIES:
            fine_classes = fine_classes_for_family(
                family,
                taxonomy="cic_iot2023",
            )
            self.assertTrue(fine_classes)
            self.assertFalse(observed.intersection(fine_classes))
            observed.update(fine_classes)
        self.assertNotIn("Benign", observed)
        self.assertEqual(
            set(CIC_IOT2023_FINE_TO_FAMILY) - {"Benign"},
            observed,
        )
        self.assertEqual(32, len(observed))

    def test_attack_probability_variants_are_bounded(self) -> None:
        family = np.asarray(
            [[0.8, 0.2], [0.3, 0.7]], dtype=np.float64
        )
        binary = np.asarray([0.1, 0.6], dtype=np.float64)
        variants = attack_probability_variants(family, binary, 0)
        self.assertEqual(set(ATTACK_PROBABILITY_VARIANTS), set(variants))
        np.testing.assert_allclose(variants["family"], [0.2, 0.7])
        np.testing.assert_allclose(variants["binary"], binary)
        np.testing.assert_allclose(variants["maximum"], [0.2, 0.7])
        np.testing.assert_allclose(variants["noisy_or"], [0.28, 0.88])
        for values in variants.values():
            self.assertTrue(np.all((values >= 0.0) & (values <= 1.0)))

    def test_family_labels_preserve_unknown_and_put_benign_first(self) -> None:
        labels, names, benign_index = family_labels(
            np.asarray([0, 1, 2, -1]),
            [
                "Benign",
                "DDoS-SYN_Flood",
                "DDoS-UDP_Flood",
            ],
            CIC_IOT2023_FINE_TO_FAMILY,
        )
        self.assertEqual(["Benign", "DDoS"], names)
        self.assertEqual(0, benign_index)
        np.testing.assert_array_equal(labels, [0, 1, 1, -1])

    def test_split_counts_names_unknown_family(self) -> None:
        counts = split_counts(
            np.asarray([0, 1, -1]),
            np.asarray([False, False, True]),
            ["Benign", "Bot"],
            "DDoS",
        )
        self.assertEqual({"Benign": 1, "Bot": 1, "DDoS": 1}, counts)

    def test_evaluator_replaces_primary_attack_probability(self) -> None:
        arrays = {
            "validation_family_attack_probability": np.asarray([0.1]),
            "test_family_attack_probability": np.asarray([0.2]),
            "validation_attack_probability": np.asarray([0.9]),
            "test_attack_probability": np.asarray([0.8]),
        }
        source = {
            "Botnet": {
                "metrics": {"task": {"unknown_family": "Botnet"}},
                "arrays": arrays,
            }
        }
        prepared = prepared_for_variant(source, "family")
        np.testing.assert_allclose(
            prepared["Botnet"]["arrays"]["validation_attack_probability"],
            [0.1],
        )
        np.testing.assert_allclose(
            prepared["Botnet"]["arrays"]["test_attack_probability"],
            [0.2],
        )
        np.testing.assert_allclose(
            source["Botnet"]["arrays"]["validation_attack_probability"],
            [0.9],
        )


if __name__ == "__main__":
    unittest.main()
