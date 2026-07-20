from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from prepare_stratified_cache import build_cache


class StratifiedCacheTest(unittest.TestCase):
    def test_cache_is_bounded_and_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.csv"
            config = root / "config.json"
            rows = []
            for label in ("a", "b"):
                for index in range(8):
                    rows.append({"f1": index, "f2": index * 2, "label": label})
            pd.DataFrame(rows).to_csv(source, index=False)
            config.write_text(
                json.dumps(
                    {
                        "label_column": "label",
                        "modalities": {"one": ["f1"], "two": ["f2"]},
                    }
                ),
                encoding="utf-8",
            )
            first = root / "first.csv"
            second = root / "second.csv"
            first_report = build_cache(
                str(source), str(config), 3, 4, 7, str(first)
            )
            second_report = build_cache(
                str(source), str(config), 3, 4, 7, str(second)
            )
        self.assertEqual(first_report["rows"], 6)
        self.assertEqual(first_report["per_class"], {"a": 3, "b": 3})
        self.assertEqual(
            first_report["output_sha256"], second_report["output_sha256"]
        )


if __name__ == "__main__":
    unittest.main()
