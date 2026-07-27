from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from create_parrot2025_full_no_decryption_feature_protocol import (
    capture_id,
    full_capture_inventory,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash
from run_parrot2025_full_no_decryption_feature_extraction import completed_shard


class Parrot2025FullNoDecryptionFeatureTests(unittest.TestCase):
    def test_capture_id_is_stable_and_path_sensitive(self) -> None:
        member = "PARROT2025_mitmproxy/app_1.pcap"
        self.assertEqual(capture_id(member), capture_id(member))
        self.assertNotEqual(capture_id(member), capture_id(member.upper()))
        self.assertEqual(len(capture_id(member)), 20)

    def test_full_inventory_requires_80_apps_with_four_captures(self) -> None:
        pairs = []
        for app_index in range(80):
            for capture_index in range(4):
                member = f"PARROT2025_mitmproxy/app{app_index}_{capture_index}.pcap"
                pairs.append(
                    {
                        "app": f"app{app_index}",
                        "pcap": member,
                        "pcap_size_bytes": 10,
                        "pcap_crc32": "00000000",
                        "pcap_header": {"linktype": 276},
                    }
                )
        inventory = full_capture_inventory({"capture_pairs": pairs}, 276)
        self.assertEqual(len(inventory), 320)
        self.assertEqual(len({item["application"] for item in inventory}), 80)

    def test_resume_accepts_only_hash_bound_canonical_shard(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            capture = {
                "capture_id": "abc",
                "application": "app",
                "member": "PARROT2025_mitmproxy/app.pcap",
                "size_bytes": 1,
                "crc32": "00000000",
                "linktype": 276,
            }
            protocol = {
                "manifest_sha256": "protocol",
                "feature_columns": ["x"],
                "metadata_columns": [
                    "CaptureGroup",
                    "Application",
                    "ReferenceRole",
                ],
            }
            frame = pd.DataFrame(
                {
                    "x": [1.0],
                    "CaptureGroup": [capture["member"]],
                    "Application": [capture["application"]],
                    "ReferenceRole": ["benign_external_safety_only"],
                }
            )
            csv_path = root / "features.csv"
            frame.to_csv(csv_path, index=False)
            manifest = {
                "schema_version": "parrot2025_no_decryption_feature_shard_v1",
                "protocol_manifest_sha256": protocol["manifest_sha256"],
                "capture": capture,
                "features_csv_sha256": file_hash(csv_path),
                "flow_row_count": 1,
            }
            manifest["manifest_sha256"] = canonical_hash(manifest)
            (root / "manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            self.assertTrue(
                completed_shard(
                    protocol=protocol, capture=capture, shard_root=root
                )
            )
            csv_path.write_text("tampered\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                completed_shard(
                    protocol=protocol, capture=capture, shard_root=root
                )


if __name__ == "__main__":
    unittest.main()
