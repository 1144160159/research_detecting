from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
MODULE_PATH = ROOT / "repair_caeos_sample_id_collisions.py"
SPEC = importlib.util.spec_from_file_location("repair_sample_ids", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SampleIdCollisionRepairTest(unittest.TestCase):
    def test_repair_preserves_rows_labels_features_and_backups(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data_root = root / "datasets"
            dataset_id = "toy"
            dataset_dir = data_root / dataset_id
            control = data_root / "_control"
            dataset_dir.mkdir(parents=True)
            control.mkdir()
            csv_path = dataset_dir / "Benign.csv"
            duplicate_id = "11" * 32
            unique_id = "22" * 32
            fieldnames = [
                "schema_version",
                "dataset_id",
                "dataset_role",
                "sample_id",
                "capture_id",
                "traffic_class",
                "attack_category",
                "binary_label",
                "packet_count",
                "payload_b64",
            ]
            rows = [
                ["v1", dataset_id, "test", duplicate_id, "aa" * 32, "Benign", "Benign", "0", "1", "A" * 200_000],
                ["v1", dataset_id, "test", duplicate_id, "aa" * 32, "Benign", "Benign", "0", "2", "B"],
                ["v1", dataset_id, "test", unique_id, "bb" * 32, "Benign", "Benign", "0", "3", "C"],
            ]
            with csv_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle, lineterminator="\n")
                writer.writerow(fieldnames)
                writer.writerows(rows)

            manifest = {
                "class_csvs": [
                    {
                        "attack_category": "Benign",
                        "path": str(csv_path),
                        "rows": len(rows),
                        "sha256": file_sha256(csv_path),
                        "size_bytes": csv_path.stat().st_size,
                    }
                ],
                "complete": True,
                "dataset_id": dataset_id,
                "row_count": len(rows),
                "schema_version": "test",
            }
            manifest["manifest_sha256"] = MODULE.canonical_json_hash(manifest)
            manifest_path = dataset_dir / "dataset.manifest.json"
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            completion = {
                "all_complete": True,
                "datasets": [manifest],
                "schema_version": "test",
            }
            completion["completion_sha256"] = MODULE.canonical_json_hash(completion)
            completion_path = control / "completion.toy.json"
            completion_path.write_text(
                json.dumps(completion, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            scratch = root / "scratch"
            partition = scratch / "partitions" / "class-0000" / "shard-0000"
            partition.mkdir(parents=True)
            record = struct.Struct("!32s32s32s32s")
            with (partition / "identity-0000.bin").open("wb") as handle:
                handle.write(record.pack(bytes.fromhex(duplicate_id), b"l" * 32, b"c" * 32, b"x" * 32))
                handle.write(record.pack(bytes.fromhex(duplicate_id), b"l" * 32, b"c" * 32, b"y" * 32))
                handle.write(record.pack(bytes.fromhex(unique_id), b"l" * 32, b"d" * 32, b"z" * 32))

            diagnosis_path = root / "diagnosis.json"
            diagnosis_path.write_text(
                json.dumps({"duplicate_keys": 1, "duplicate_rows_after_first": 1}),
                encoding="utf-8",
            )
            audit_path = root / "audit.json"
            audit_path.write_text("{}\n", encoding="utf-8")
            repair_root = control / "sample_id_repairs" / dataset_id

            receipt = MODULE.repair_dataset(
                manifest_path,
                completion_path,
                scratch,
                diagnosis_path,
                audit_path,
                repair_root,
                dataset_id,
                "tx1",
            )

            backup_dir = Path(receipt["backup_dataset_path"])
            self.assertTrue(backup_dir.is_dir())
            self.assertTrue(Path(receipt["backup_completion_path"]).is_file())
            with (dataset_dir / "Benign.csv").open("r", encoding="utf-8", newline="") as handle:
                repaired_rows = list(csv.DictReader(handle))
            with (backup_dir / "Benign.csv").open("r", encoding="utf-8", newline="") as handle:
                original_rows = list(csv.DictReader(handle))

            self.assertEqual(len(repaired_rows), len(original_rows))
            self.assertEqual(len({row["sample_id"] for row in repaired_rows}), 3)
            self.assertEqual(repaired_rows[2]["sample_id"], unique_id)
            for repaired, original in zip(repaired_rows, original_rows):
                repaired_without_id = dict(repaired)
                original_without_id = dict(original)
                repaired_without_id.pop("sample_id")
                original_without_id.pop("sample_id")
                self.assertEqual(repaired_without_id, original_without_id)

            mapping_path = repair_root / "tx1" / "sample_id_mapping.jsonl"
            self.assertEqual(len(mapping_path.read_text("utf-8").splitlines()), 2)
            new_manifest = json.loads(manifest_path.read_text("utf-8"))
            self.assertEqual(new_manifest["identity_repair"]["rows_deleted"], 0)
            self.assertFalse(new_manifest["identity_repair"]["feature_columns_modified"])
            self.assertFalse(new_manifest["identity_repair"]["label_columns_modified"])
            MODULE.verified_embedded_hash(new_manifest, "manifest_sha256")
            MODULE.verified_embedded_hash(
                json.loads(completion_path.read_text("utf-8")), "completion_sha256"
            )


if __name__ == "__main__":
    unittest.main()
