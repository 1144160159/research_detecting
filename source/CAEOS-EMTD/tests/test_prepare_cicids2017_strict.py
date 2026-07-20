import csv
import json
import tempfile
import unittest
from pathlib import Path

from prepare_cicids2017_strict import (
    FEATURE_COLUMNS,
    IDENTITY_COLUMNS,
    build_dataset,
    normalize_label,
)


class PrepareCicids2017StrictTest(unittest.TestCase):
    def test_normalize_label_repairs_web_attack_names(self):
        self.assertEqual(normalize_label(" BENIGN "), "Benign")
        self.assertEqual(
            normalize_label("Web Attack \ufffd Brute Force"),
            "Web Attack - Brute Force",
        )
        self.assertEqual(
            normalize_label("Web Attack ? Sql Injection"),
            "Web Attack - Sql Injection",
        )
        self.assertEqual(normalize_label("  "), "")

    def test_build_dataset_skips_blank_labels_and_freezes_groups(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "capture.csv"
            header = list(dict.fromkeys([*IDENTITY_COLUMNS, *FEATURE_COLUMNS, "Label"]))
            first = {column: str(index + 1) for index, column in enumerate(header)}
            first.update(
                {
                    "Source IP": "10.0.0.1",
                    "Source Port": "1234",
                    "Destination IP": "10.0.0.2",
                    "Destination Port": "80",
                    "Protocol": "6",
                    "Timestamp": "07/07/2017 10:30:15",
                    "Label": "BENIGN",
                }
            )
            reverse = dict(first)
            reverse.update(
                {
                    "Source IP": "10.0.0.2",
                    "Source Port": "80",
                    "Destination IP": "10.0.0.1",
                    "Destination Port": "1234",
                    "Timestamp": "07/07/2017 10:30:15",
                    "Label": "Web Attack \ufffd XSS",
                }
            )
            blank = dict(first)
            blank["Label"] = ""
            with source.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=header)
                writer.writeheader()
                writer.writerows((first, reverse, blank))

            output = root / "strict.csv"
            report = build_dataset(str(root), str(output))
            with output.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))

            self.assertEqual(report["rows"], 2)
            self.assertEqual(report["skipped_blank_labels"], 1)
            self.assertEqual(report["undeclared_attack_labels"], [])
            self.assertEqual({row["Label"] for row in rows}, {"Benign", "Web Attack - XSS"})
            self.assertEqual(rows[0]["Flow_Group"], rows[1]["Flow_Group"])
            self.assertNotIn("Benign", rows[0]["Flow_Group"])
            metadata = json.loads(
                output.with_suffix(".csv.json").read_text(encoding="utf-8")
            )
            self.assertEqual(metadata["output_sha256"], report["output_sha256"])


if __name__ == "__main__":
    unittest.main()
