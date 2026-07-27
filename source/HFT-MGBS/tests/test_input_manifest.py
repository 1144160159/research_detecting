from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.evaluate_unsw_independent_holdout import (
    load_input_hash_evidence,
)
from scripts.freeze_input_manifest import referenced_paths, sha256_file


class InputManifestTest(unittest.TestCase):
    def test_referenced_paths_and_hash_evidence_cover_required_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            capture = root / "capture.pcap"
            capture.write_bytes(b"pcap")
            ground_truth = root / "gt.csv"
            ground_truth.write_text("gt", encoding="utf-8")
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "ground_truth_csv": str(ground_truth),
                        "samples": [{"path": str(capture)}],
                    }
                ),
                encoding="utf-8",
            )
            paths = referenced_paths([manifest])
            self.assertEqual(
                paths,
                sorted(
                    [
                        capture.resolve(),
                        ground_truth.resolve(),
                        manifest.resolve(),
                    ],
                    key=str,
                ),
            )
            hash_manifest = root / "hashes.json"
            payload = {
                "entries": [
                    {
                        "path": str(path.resolve()),
                        "sha256": sha256_file(path),
                    }
                    for path in paths
                ]
            }
            raw = json.dumps(payload).encode("utf-8")
            hash_manifest.write_bytes(raw)

            evidence = load_input_hash_evidence(
                hash_manifest, [manifest, ground_truth, capture]
            )

        self.assertTrue(evidence["all_required_paths_frozen"])
        self.assertEqual(evidence["required_path_count"], 3)
        self.assertEqual(
            evidence["sha256"], hashlib.sha256(raw).hexdigest()
        )

    def test_missing_required_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            hash_manifest = root / "hashes.json"
            hash_manifest.write_text('{"entries": []}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing required paths"):
                load_input_hash_evidence(
                    hash_manifest, [root / "missing.pcap"]
                )


if __name__ == "__main__":
    unittest.main()
