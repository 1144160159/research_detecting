import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import collect_mendeley_dataset as collector


def fixture_files():
    return [
        {
            "filename": "events.csv",
            "id": "file-id",
            "size": 3,
            "content_details": {
                "size": 3,
                "sha256_hash": "a" * 64,
                "download_url": "https://data.mendeley.test/events.csv",
                "content_type": "text/csv",
            },
        }
    ]


class MendeleyCollectorTests(unittest.TestCase):
    def test_normalizes_size_sha256_and_download_url(self):
        files = collector.normalize_files(fixture_files())
        self.assertEqual(files[0]["name"], "events.csv")
        self.assertEqual(files[0]["size"], 3)
        self.assertEqual(files[0]["sha256"], "a" * 64)

    def test_rejects_missing_hash_and_path_traversal(self):
        missing_hash = fixture_files()
        missing_hash[0]["content_details"]["sha256_hash"] = ""
        with self.assertRaisesRegex(ValueError, "sha256_hash"):
            collector.normalize_files(missing_hash)

        traversal = fixture_files()
        traversal[0]["filename"] = "../events.csv"
        with self.assertRaisesRegex(ValueError, "Unsafe Mendeley filename"):
            collector.normalize_files(traversal)

    def test_metadata_only_writes_complete_state(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "gpu-root"
            argv = [
                "collect_mendeley_dataset.py",
                "--dataset-id",
                "fixture",
                "--version",
                "3",
                "--root",
                str(root),
                "--expected-files",
                "1",
                "--expected-bytes",
                "3",
                "--metadata-only",
            ]
            with mock.patch.object(sys, "argv", argv), mock.patch.object(
                collector, "fetch_files", return_value=fixture_files()
            ):
                self.assertEqual(collector.main(), 0)

            state = json.loads(
                (root / "manifests" / "collection_state.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertTrue(state["complete"])
            self.assertEqual(state["dataset_id"], "fixture")
            self.assertEqual(state["version"], 3)
            self.assertEqual(state["selection_size_bytes"], 3)
            self.assertEqual(state["files"]["events.csv"]["status"], "metadata_only")
            self.assertEqual(list((root / "raw").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
