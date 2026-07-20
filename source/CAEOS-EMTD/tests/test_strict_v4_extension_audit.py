from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from audit_strict_v4_extension_datasets import audit_dataset


class StrictV4ExtensionAuditTests(unittest.TestCase):
    def test_group_supported_dataset_is_strict(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv_path = root / "data.csv"
            config = root / "config.json"
            pd.DataFrame(
                {
                    "label": ["benign"] * 3 + ["attack"] * 3,
                    "group": ["b1", "b2", "b3", "a1", "a2", "a3"],
                }
            ).to_csv(csv_path, index=False)
            config.write_text(
                json.dumps({"label_column": "label", "group_column": "group"}),
                encoding="utf-8",
            )
            report = audit_dataset(
                "test", csv_path, config, "benign", ["attack"], chunksize=2
            )
            self.assertTrue(report["strict_group_generalization_eligible"])
            self.assertEqual(report["recommended_split"], "capture_grouped")

    def test_single_group_attack_is_separate_tier(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv_path = root / "data.csv"
            config = root / "config.json"
            pd.DataFrame(
                {
                    "label": ["benign"] * 3 + ["attack"] * 3,
                    "group": ["b1", "b2", "b3", "a1", "a1", "a1"],
                }
            ).to_csv(csv_path, index=False)
            config.write_text(
                json.dumps({"label_column": "label", "group_column": "group"}),
                encoding="utf-8",
            )
            report = audit_dataset(
                "test", csv_path, config, "benign", ["attack"], chunksize=2
            )
            self.assertFalse(report["strict_group_generalization_eligible"])
            self.assertEqual(report["evidence_tier"], "fingerprint_isolated_extension")


if __name__ == "__main__":
    unittest.main()
