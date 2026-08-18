from __future__ import annotations

import unittest

import numpy as np

from strict_v4_pcap_multimodal_protocol import (
    encode_known_labels,
    family_mapping,
    select_pseudo_unknown_fine_labels,
    split_capture_groups,
)


class PcapMultimodalTaskProtocolTest(unittest.TestCase):
    def setUp(self) -> None:
        fine = []
        family = []
        groups = []
        for family_name, fine_names in {
            "Benign": ["Benign_Final"],
            "DDoS": ["DDoS-A", "DDoS-B"],
            "DoS": ["DoS-A", "DoS-B"],
            "Mirai": ["Mirai-A", "Mirai-B"],
        }.items():
            for fine_name in fine_names:
                for capture_index in range(4):
                    for _ in range(3):
                        fine.append(fine_name)
                        family.append(family_name)
                        groups.append(f"{fine_name}/capture{capture_index}.pcap")
        self.fine = np.asarray(fine)
        self.family = np.asarray(family)
        self.groups = np.asarray(groups)

    def test_family_holdout_and_capture_splits_are_disjoint(self) -> None:
        split = split_capture_groups(
            self.fine, self.family, self.groups, "Mirai", 283
        )
        masks = [
            split["train_mask"],
            split["validation_mask"],
            split["known_test_mask"],
            split["unknown_test_mask"],
        ]
        for first_index, first in enumerate(masks):
            for second in masks[first_index + 1 :]:
                self.assertFalse(np.any(first & second))
        self.assertTrue(np.all(self.family[split["unknown_test_mask"]] == "Mirai"))
        self.assertEqual(
            split["overlap"],
            {
                "train_validation": 0,
                "train_test": 0,
                "validation_test": 0,
                "unknown_known": 0,
            },
        )
        for fine_name, assignment in split["assignment"].items():
            expected_validation = 2 if fine_name == "Benign_Final" else 1
            expected_train = 1 if fine_name == "Benign_Final" else 2
            self.assertEqual(
                len(assignment["validation"]),
                expected_validation,
                fine_name,
            )
            self.assertEqual(len(assignment["test"]), 1, fine_name)
            self.assertEqual(
                len(assignment["train"]),
                expected_train,
                fine_name,
            )

    def test_known_mapping_is_benign_first_and_unknown_is_minus_one(self) -> None:
        names, mapping = family_mapping("DoS")
        self.assertEqual(names[0], "Benign")
        encoded = encode_known_labels(self.family, mapping, "DoS")
        self.assertTrue(np.all(encoded[self.family == "DoS"] == -1))
        self.assertTrue(np.all(encoded[self.family != "DoS"] >= 0))

    def test_pseudo_unknown_selection_is_known_only_and_per_family(
        self,
    ) -> None:
        outer_train = self.family != "DDoS"

        first = select_pseudo_unknown_fine_labels(
            self.fine,
            self.family,
            outer_train,
            unknown_family="DDoS",
            seed=283,
        )
        second = select_pseudo_unknown_fine_labels(
            self.fine,
            self.family,
            outer_train,
            unknown_family="DDoS",
            seed=283,
        )

        self.assertEqual(first, second)
        self.assertEqual(set(first), {"DoS", "Mirai"})
        self.assertIn(first["DoS"], {"DoS-A", "DoS-B"})
        self.assertIn(first["Mirai"], {"Mirai-A", "Mirai-B"})


if __name__ == "__main__":
    unittest.main()
