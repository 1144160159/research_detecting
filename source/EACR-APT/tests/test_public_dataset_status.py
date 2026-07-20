import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.public_dataset_status import dataset_status, entry_status, file_entries


class PublicDatasetStatusTests(unittest.TestCase):
    def test_file_entries_accepts_legacy_mapping_and_current_list(self):
        self.assertEqual(file_entries({"a": {"status": "verified"}}), [{"status": "verified"}])
        self.assertEqual(file_entries([{"complete": True}]), [{"complete": True}])
        self.assertEqual(file_entries("invalid"), [])
        self.assertEqual(entry_status({"sha256": "abc", "bytes": 7}), "verified")
        self.assertEqual(entry_status({"status": "complete"}), "verified")

    def test_list_shaped_state_is_summarized(self):
        with tempfile.TemporaryDirectory() as directory:
            dataset = Path(directory) / "dataset"
            manifest_dir = dataset / "manifests"
            manifest_dir.mkdir(parents=True)
            (manifest_dir / "collection_state.json").write_text(
                json.dumps(
                    {
                        "complete": False,
                        "expected_file_count": 2,
                        "expected_bytes": 30,
                        "files": [
                            {"complete": True, "expected_bytes": 10},
                            {"complete": False, "expected_bytes": 20},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with patch("scripts.public_dataset_status.disk_bytes", return_value=42):
                result = dataset_status(dataset)
            self.assertEqual(result["status_counts"], {"pending": 1, "verified": 1})
            self.assertEqual(result["verified_bytes"], 10)
            self.assertEqual(result["expected_file_count"], 2)
            self.assertEqual(result["expected_size_bytes"], 30)


if __name__ == "__main__":
    unittest.main()
