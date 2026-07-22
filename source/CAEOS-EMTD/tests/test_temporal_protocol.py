from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from caeos.data import prepare_tabular_open_set
from prepare_dohbrw2020 import capture_time


class TemporalCaptureProtocolTest(unittest.TestCase):
    def test_doh_filename_timestamps_are_normalized(self):
        self.assertEqual(
            capture_time(Path("dns2tcp_doh4_2020-04-01T20:27:54.299414.csv")),
            "2020-04-01T20:27:54.299414",
        )
        self.assertEqual(
            capture_time(Path("dump_00004_20200113132407.77383d.csv")),
            "2020-01-13T13:24:07",
        )
        self.assertIsNone(capture_time(Path("dump.e022b7.csv")))

    def test_temporal_groups_are_disjoint_and_unknown_does_not_set_boundaries(self):
        rows = []
        for label, offset in (("benign", 0.0), ("known_attack", 100.0)):
            for capture_index in range(10):
                for row_index in range(2):
                    rows.append(
                        {
                            "feature": offset + capture_index + row_index / 10.0,
                            "Label": label,
                            "CaptureId": f"{label}-{capture_index}",
                            "CaptureTime": f"2020-01-{capture_index + 1:02d}T00:00:00",
                        }
                    )
        for capture_index in range(3):
            rows.append(
                {
                    "feature": 1000.0 + capture_index,
                    "Label": "future_unknown",
                    "CaptureId": f"unknown-{capture_index}",
                    "CaptureTime": f"2030-01-{capture_index + 1:02d}T00:00:00",
                }
            )

        config = {
            "label_column": "Label",
            "group_column": "CaptureId",
            "time_column": "CaptureTime",
            "modalities": {"flow": ["feature"]},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "temporal.csv"
            pd.DataFrame(rows).to_csv(path, index=False)
            bundle = prepare_tabular_open_set(
                str(path),
                config,
                ["future_unknown"],
                "benign",
                max_per_class=100,
                chunksize=11,
                seed=7,
                split_strategy="temporal_capture_grouped",
            )

        metadata = bundle.split_metadata
        self.assertEqual(metadata["strategy"], "temporal_capture_grouped")
        self.assertEqual(metadata["group_overlap"], {
            "train_validation": 0,
            "train_test": 0,
            "validation_test": 0,
        })
        for label in ("benign", "known_attack"):
            self.assertEqual(
                metadata["per_class_groups"][label],
                {"train": 7, "validation": 1, "test": 2},
            )
            ranges = metadata["per_class_time_ranges"][label]
            self.assertLessEqual(ranges["train"]["maximum"], ranges["validation"]["minimum"])
            self.assertLessEqual(ranges["validation"]["maximum"], ranges["test"]["minimum"])
        self.assertNotIn("future_unknown", metadata["per_class_groups"])
        self.assertEqual(int(bundle.test.is_unknown.sum()), 3)
        self.assertEqual(int(bundle.train.is_unknown.sum()), 0)
        self.assertEqual(int(bundle.validation.is_unknown.sum()), 0)
        np.testing.assert_allclose(bundle.preprocessing["processors"]["flow"]["mean"], [53.05])


if __name__ == "__main__":
    unittest.main()
