from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from create_strict_v4_krc_external_malicious_input_protocol import (
    build_tasks,
    config_columns,
    derive_seed,
    verify_zero_outputs,
)
from external_dataset_protocol_utils import file_hash


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


class KrcExternalInputProtocolTest(unittest.TestCase):
    def test_derive_seed_is_deterministic_and_purpose_separated(self) -> None:
        first = derive_seed("a" * 64, "D", "A", 223, "split")
        second = derive_seed("a" * 64, "D", "A", 223, "split")
        other = derive_seed("a" * 64, "D", "A", 223, "augmentation")
        self.assertEqual(first, second)
        self.assertNotEqual(first, other)
        self.assertGreaterEqual(first, 0)
        self.assertLess(first, 2**31)

    def test_config_columns_preserves_modality_then_identity_order(
        self,
    ) -> None:
        config = {
            "modalities": {"m1": ["a", "b"], "m2": ["c"]},
            "group_column": "group",
            "label_column": "label",
        }
        self.assertEqual(
            config_columns(config), ["a", "b", "c", "group", "label"]
        )
        config["modalities"]["m2"] = ["a"]
        with self.assertRaisesRegex(ValueError, "not unique"):
            config_columns(config)

    def test_builds_exact_96_task_universe_from_frozen_manifests(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            data = root / "data"
            configs = {
                "LSNM2024": (
                    project / "configs/lsnm2024_external.json",
                    "normal",
                    [f"attack_{index:02d}" for index in range(15)],
                ),
                "CICDDoS2019": (
                    project / "configs/cicids2017_strict.json",
                    "BENIGN",
                    [
                        *[f"ddos_{index:02d}" for index in range(15)],
                        "UDPLag",
                        "WebDDoS",
                    ],
                ),
            }
            summary = {"datasets": {}}
            readiness = {"external_prepared": {}}
            for dataset, (config_path, benign, attacks) in configs.items():
                config = {
                    "modalities": {"m1": ["feature"]},
                    "group_column": "Flow_Group",
                    "label_column": (
                        "Attack" if dataset == "LSNM2024" else "Label"
                    ),
                }
                write_json(config_path, config)
                manifest = {
                    "schema_version": (
                        "gpu_external_prepared_dataset_manifest_v1"
                    ),
                    "dataset": dataset,
                    "passed": True,
                    "files": {},
                }
                seed_checks = {}
                labels = [benign, *attacks]
                for seed in (223, 227, 229):
                    dataset_root = data / dataset
                    csv_path = dataset_root / f"seed{seed}.csv"
                    csv_path.parent.mkdir(parents=True, exist_ok=True)
                    csv_path.write_text(
                        "feature,Flow_Group,label\n1,g,x\n",
                        encoding="utf-8",
                    )
                    sidecar = {
                        "schema_version": "gpu_external_prepared_seed_v1",
                        "dataset": dataset,
                        "seed": seed,
                        "passed": True,
                        "columns": config_columns(config),
                        "csv_sha256": file_hash(csv_path),
                        "rows": len(labels) * 3,
                        "label_counts": {
                            label: 3 for label in labels
                        },
                        "groups_per_label": {
                            label: 3 for label in labels
                        },
                        "provenance": {
                            "config_sha256": file_hash(config_path)
                        },
                    }
                    manifest["files"][str(seed)] = sidecar
                    write_json(Path(f"{csv_path}.json"), sidecar)
                    seed_checks[str(seed)] = {
                        "passes": True,
                        "rows": len(labels) * 3,
                    }
                manifest_path = data / dataset / "manifest.json"
                write_json(manifest_path, manifest)
                summary["datasets"][dataset] = {
                    "manifest_sha256": file_hash(manifest_path)
                }
                readiness["external_prepared"][dataset] = {
                    "manifest_file_sha256": file_hash(manifest_path),
                    "passes": True,
                    "seed_checks": seed_checks,
                }

            downstream = {
                "manifest_sha256": "b" * 64,
                "fresh_external_malicious": {
                    "datasets": ["LSNM2024", "CICDDoS2019"],
                    "training_seeds": [223, 227, 229],
                },
            }
            tasks, registry = build_tasks(
                project_root=project,
                data_root=data,
                downstream_design=downstream,
                preparation_summary=summary,
                readiness=readiness,
            )
            identities = {
                (
                    task["dataset"],
                    task["unknown_attack_family"],
                    task["training_seed"],
                )
                for task in tasks
            }
            self.assertEqual(len(tasks), 96)
            self.assertEqual(len(identities), 96)
            self.assertEqual(
                registry["LSNM2024"]["attack_family_count"], 15
            )
            self.assertEqual(
                registry["CICDDoS2019"]["attack_family_count"], 17
            )

    def test_zero_output_gate_rejects_existing_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertTrue(
                all(value == 0 for value in verify_zero_outputs(root).values())
            )
            metrics = root / "task/candidate_metrics.json"
            metrics.parent.mkdir(parents=True)
            metrics.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "zero-result"):
                verify_zero_outputs(root)


if __name__ == "__main__":
    unittest.main()
