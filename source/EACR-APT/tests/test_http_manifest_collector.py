import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import collect_http_manifest as collector


class HttpManifestCollectorTests(unittest.TestCase):
    def test_resolves_apache_index_and_enforces_totals(self):
        page = """
        <a href="../">../</a>
        <a href="one.json.bz2">one.json.bz2</a>  25-Mar-2022 14:59  11
        <a href="two.json.bz2">two.json.bz2</a>  25-Mar-2022 15:00  13
        """
        manifest = {
            "schema_version": 1,
            "dataset_id": "fixture",
            "expected_files": 2,
            "expected_bytes": 24,
            "apache_indexes": [
                {
                    "url": "https://example.test/data/",
                    "path_prefix": "system/json",
                    "include_regex": r"\.json\.bz2$",
                    "expected_files": 2,
                    "expected_bytes": 24,
                }
            ],
        }
        resolved = collector.resolve_manifest(
            manifest, fetcher=lambda _url, _proxy: page
        )
        self.assertEqual(resolved["expected_bytes"], 24)
        self.assertEqual(
            [item["name"] for item in resolved["files"]],
            ["system/json/one.json.bz2", "system/json/two.json.bz2"],
        )

        manifest["expected_bytes"] = 25
        with self.assertRaisesRegex(ValueError, "Manifest invariant failed"):
            collector.resolve_manifest(manifest, fetcher=lambda _url, _proxy: page)

    def test_rejects_path_traversal(self):
        manifest = {
            "schema_version": 1,
            "dataset_id": "fixture",
            "files": [
                {
                    "name": "../escape.zip",
                    "url": "https://example.test/escape.zip",
                    "expected_bytes": 1,
                }
            ],
        }
        with self.assertRaisesRegex(ValueError, "Unsafe manifest filename"):
            collector.resolve_manifest(manifest)

    def test_socks_proxy_uses_resumable_curl_without_shell(self):
        command = collector.download_command(
            "https://example.test/file.zip",
            Path("/gpu/raw/file.zip"),
            connections=8,
            proxy="socks5h://127.0.0.1:9999",
        )
        self.assertEqual(command[0], "curl")
        self.assertIn("--continue-at", command)
        self.assertIn("socks5h://127.0.0.1:9999", command)
        self.assertNotIn("shell=True", command)

    def test_metadata_only_writes_complete_state_without_payload(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            manifest_path = base / "fixture.json"
            root = base / "gpu-root"
            manifest_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "dataset_id": "fixture",
                        "expected_files": 1,
                        "expected_bytes": 7,
                        "files": [
                            {
                                "name": "payload.zip",
                                "url": "https://example.test/payload.zip",
                                "expected_bytes": 7,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            argv = [
                "collect_http_manifest.py",
                "--manifest",
                str(manifest_path),
                "--root",
                str(root),
                "--metadata-only",
            ]
            with mock.patch.object(sys, "argv", argv):
                self.assertEqual(collector.main(), 0)

            state = json.loads(
                (root / "manifests" / "collection_state.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertTrue(state["complete"])
            self.assertEqual(state["selection_size_bytes"], 7)
            self.assertEqual(state["files"]["payload.zip"]["status"], "metadata_only")
            self.assertEqual(list((root / "raw").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
