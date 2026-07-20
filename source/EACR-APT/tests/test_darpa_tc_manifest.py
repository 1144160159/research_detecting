import json
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from scripts.collect_http_manifest import resolve_manifest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = (
    PROJECT_ROOT / "configs" / "http_manifests" / "darpa_tc_e3_json.json"
)
CORE_MANIFEST_PATH = (
    PROJECT_ROOT / "configs" / "http_manifests" / "darpa_tc_e3_mixed_core.json"
)
THEIA_JSON_CORE_PATH = (
    PROJECT_ROOT
    / "configs"
    / "http_manifests"
    / "darpa_tc_e3_theia6r_json_core.json"
)


class DarpaTcE3ManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_manifest_totals_and_generic_collector_compatibility(self):
        resolved = resolve_manifest(self.manifest)
        self.assertEqual(resolved["expected_files"], 9)
        self.assertEqual(resolved["expected_bytes"], 43_028_712_331)
        self.assertEqual(
            sum(item["expected_bytes"] for item in resolved["files"]),
            resolved["expected_bytes"],
        )

    def test_selects_unique_json_archives_without_bin_duplicates(self):
        files = self.manifest["files"]
        names = [item["name"] for item in files]
        drive_ids = [item["google_drive_id"] for item in files]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(len(drive_ids), len(set(drive_ids)))
        self.assertTrue(all(name.endswith(".json.tar.gz") for name in names))
        self.assertFalse(any(".bin." in name for name in names))

    def test_all_json_archives_are_deferred_extended_representations(self):
        self.assertEqual(self.manifest["collection_status"], "deferred_after_core_representation_switch")
        self.assertTrue(
            all(item["selection_tier"] == "extended" for item in self.manifest["files"])
        )
        self.assertEqual(self.manifest["extended_expected_files"], 9)
        self.assertEqual(self.manifest["extended_expected_bytes"], 43_028_712_331)

    def test_legacy_json_launcher_requires_explicit_extended_opt_in(self):
        launcher = PROJECT_ROOT / "scripts" / "collect_darpa_tc_e3.sh"
        text = launcher.read_text(encoding="utf-8")
        self.assertIn("EACR_ENABLE_DARPA_TC_EXTENDED_JSON", text)
        self.assertIn("extended queue is deferred", text)

    def test_urls_bind_to_declared_google_drive_ids(self):
        for item in self.manifest["files"]:
            parsed = urlparse(item["url"])
            query = parse_qs(parsed.query)
            self.assertEqual(parsed.hostname, "drive.usercontent.google.com")
            self.assertEqual(query["id"], [item["google_drive_id"]])
            self.assertEqual(query["export"], ["download"])
            self.assertEqual(query["confirm"], ["t"])
            self.assertEqual(item["magic_hex"], "1f8b08")


class DarpaTcE3MixedCoreManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(CORE_MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_mixed_core_totals_and_generic_collector_compatibility(self):
        resolved = resolve_manifest(self.manifest)
        self.assertEqual(resolved["expected_files"], 4)
        self.assertEqual(resolved["expected_bytes"], 3_334_542_889)
        self.assertEqual(
            sum(item["expected_bytes"] for item in resolved["files"]),
            resolved["expected_bytes"],
        )

    def test_admits_exactly_one_official_representation_per_run(self):
        files = self.manifest["files"]
        runs = [item["canonical_run"] for item in files]
        self.assertEqual(len(runs), len(set(runs)))
        self.assertEqual(
            {item["canonical_run"]: item["source_format"] for item in files},
            {
                "cadets_official": "cdm_json_tar_gz",
                "cadets_2": "cdm_json_tar_gz",
                "theia_6r": "cdm_json_tar_gz",
                "trace_1": "cdm_avro_binary_tar_gz",
            },
        )
        self.assertEqual(
            self.manifest["duplicate_representation_policy"],
            "forbid_json_and_bin_for_the_same_run",
        )

    def test_binary_core_has_official_json_conversion_metadata(self):
        conversion = self.manifest["binary_to_json_conversion"]
        self.assertTrue(conversion["supported"])
        self.assertEqual(conversion["official_tool_name"], "ta3-java-consumer")
        self.assertEqual(
            conversion["official_tool_google_drive_id"],
            "1Yg_487Ynr9gV3oRy3KmS2tOj8RNomVY6",
        )
        binary = [
            item
            for item in self.manifest["files"]
            if item["source_format"] == "cdm_avro_binary_tar_gz"
        ]
        self.assertEqual(len(binary), 1)
        self.assertTrue(
            all(item["json_conversion"] == "official_ta3_java_consumer" for item in binary)
        )

    def test_theia_json_fallback_is_a_single_run_manifest(self):
        manifest = json.loads(THEIA_JSON_CORE_PATH.read_text(encoding="utf-8"))
        resolved = resolve_manifest(manifest)
        self.assertEqual(resolved["expected_files"], 1)
        self.assertEqual(resolved["expected_bytes"], 1_546_028_723)
        item = manifest["files"][0]
        self.assertEqual(item["canonical_run"], "theia_6r")
        self.assertEqual(item["google_drive_id"], "1Kadc6CUTb4opVSDE4x6RFFnEy0P1cRp0")
        self.assertEqual(item["source_format"], "cdm_json_tar_gz")


if __name__ == "__main__":
    unittest.main()
