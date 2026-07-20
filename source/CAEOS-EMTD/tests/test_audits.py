import unittest

import pandas as pd

from audit_dataset_fingerprints import duplicate_summary


class DatasetAuditTest(unittest.TestCase):
    def test_missing_optional_modality_is_reported(self):
        frame = pd.DataFrame({"Label": ["A", "B"]})
        report = duplicate_summary(frame, "Label", [])
        self.assertFalse(report["available"])
        self.assertIn("no feature columns", report["reason"])

    def test_configured_modality_reports_duplicates(self):
        frame = pd.DataFrame(
            {"Label": ["A", "A", "B"], "feature": [1.0, 1.0, 2.0]}
        )
        report = duplicate_summary(frame, "Label", ["feature"])
        self.assertTrue(report["available"])
        self.assertEqual(report["duplicate_rows"], 1)


if __name__ == "__main__":
    unittest.main()
