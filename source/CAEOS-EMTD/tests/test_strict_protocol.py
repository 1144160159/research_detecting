from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from caeos.data import prepare_tabular_open_set


class StrictOpenSetProtocolTest(unittest.TestCase):
    @staticmethod
    def write_dataset(
        path: Path,
        unknown_label: str,
        unknown_values: list[tuple[float, float]],
    ) -> None:
        rows = []
        for index in range(18):
            rows.append(
                {
                    "first": float(index),
                    "second": float(index + 100),
                    "Label": "benign",
                }
            )
            rows.append(
                {
                    "first": float(index + 1000),
                    "second": float(index + 1100),
                    "Label": "known_attack",
                }
            )

        # This conflict is entirely inside the known protocol and must be removed.
        rows.extend(
            [
                {"first": 9000.0, "second": 9001.0, "Label": "benign"},
                {
                    "first": 9000.0,
                    "second": 9001.0,
                    "Label": "known_attack",
                },
            ]
        )
        rows.extend(
            {
                "first": first,
                "second": second,
                "Label": unknown_label,
            }
            for first, second in unknown_values
        )
        pd.DataFrame(rows).to_csv(path, index=False)

    @staticmethod
    def known_split(bundle, split_name: str) -> tuple[np.ndarray, ...]:
        split = getattr(bundle, split_name)
        known = ~split.is_unknown.numpy()
        return (
            *(view.numpy()[known] for view in split.views),
            split.quality.numpy()[known],
            split.labels.numpy()[known],
        )

    def test_unknown_labels_and_fingerprints_do_not_change_known_protocol(self):
        config = {
            "label_column": "Label",
            "drop_cross_label_fingerprints": True,
            "modalities": {
                "first_view": ["first"],
                "second_view": ["second"],
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first_csv = root / "first.csv"
            second_csv = root / "second.csv"

            # The first unknown set collides with retained known fingerprints. The
            # second changes both the unknown label and all unknown fingerprints.
            self.write_dataset(
                first_csv,
                "unknown_a",
                [(0.0, 100.0), (1000.0, 1100.0), (20000.0, 20001.0)],
            )
            self.write_dataset(
                second_csv,
                "unknown_b",
                [(30000.0, 30001.0), (30002.0, 30003.0), (30004.0, 30005.0)],
            )

            first = prepare_tabular_open_set(
                str(first_csv),
                config,
                ["unknown_a"],
                "benign",
                max_per_class=100,
                chunksize=7,
                seed=23,
                split_strategy="fingerprint_grouped",
            )
            second = prepare_tabular_open_set(
                str(second_csv),
                config,
                ["unknown_b"],
                "benign",
                max_per_class=100,
                chunksize=7,
                seed=23,
                split_strategy="fingerprint_grouped",
            )

        self.assertEqual(first.class_names, second.class_names)
        self.assertEqual(first.preprocessing, second.preprocessing)
        for split_name in ("train", "validation", "test"):
            for left, right in zip(
                self.known_split(first, split_name),
                self.known_split(second, split_name),
            ):
                np.testing.assert_array_equal(left, right)

        first_filter = first.split_metadata["cross_label_fingerprint_filter"]
        second_filter = second.split_metadata["cross_label_fingerprint_filter"]
        self.assertEqual(first_filter, second_filter)
        self.assertEqual(first_filter["scope"], "known_only")
        self.assertFalse(first_filter["unknown_labels_used"])
        self.assertEqual(first_filter["conflicting_fingerprint_groups"], 1)
        self.assertEqual(first_filter["removed_rows"], 2)
        self.assertEqual(int(first.test.is_unknown.sum()), 3)
        self.assertEqual(int(second.test.is_unknown.sum()), 3)

        first_fingerprint = first.split_metadata["split_fingerprint"]
        second_fingerprint = second.split_metadata["split_fingerprint"]
        self.assertEqual(
            first_fingerprint["train"], second_fingerprint["train"]
        )
        self.assertEqual(
            first_fingerprint["validation"],
            second_fingerprint["validation"],
        )
        self.assertNotEqual(first_fingerprint["test"], second_fingerprint["test"])
        self.assertNotEqual(
            first_fingerprint["combined"], second_fingerprint["combined"]
        )


if __name__ == "__main__":
    unittest.main()
