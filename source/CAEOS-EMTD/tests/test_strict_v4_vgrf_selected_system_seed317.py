from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from run_strict_v4_vgrf_selected_system_seed317 import (
    RISK_POLICY,
    replay_command,
    seed317_records,
    validate_source_inputs,
)


def canonical(value: dict) -> dict:
    value["manifest_sha256"] = canonical_hash(value)
    return value


class VGRFSelectedSystemSeed317Tests(unittest.TestCase):
    def test_replay_command_changes_only_runtime_identity(self) -> None:
        source = {
            "command": [
                "/old/python",
                "train_hybrid_open_set.py",
                "--seed",
                "311",
                "--output-dir",
                "/old/output",
                "--risk-policy-name",
                "old_policy",
                "--estimators",
                "80",
            ]
        }
        with patch(
            "run_strict_v4_vgrf_selected_system_seed317.sys.executable",
            "/active/python",
        ):
            command = replay_command(
                source,
                seed=317,
                output_dir=Path("/new/output"),
                risk_policy=RISK_POLICY,
            )
        self.assertEqual(command[0], "/active/python")
        self.assertEqual(
            command[command.index("--seed") + 1], "317"
        )
        self.assertEqual(
            command[command.index("--risk-policy-name") + 1],
            RISK_POLICY,
        )
        self.assertEqual(
            command[command.index("--estimators") + 1], "80"
        )

    def test_missing_command_flag_fails_closed(self) -> None:
        source = {
            "command": [
                "/old/python",
                "train.py",
                "--seed",
                "311",
            ]
        }
        with self.assertRaisesRegex(ValueError, "--output-dir"):
            replay_command(
                source,
                seed=317,
                output_dir=Path("/new/output"),
            )

    def test_seed317_registry_requires_102_unique_records(self) -> None:
        records = [
            {
                "suite": "suite",
                "scenario": f"scenario_{index}",
                "seed": 317,
                "source_mode": "preregistered_seed317_execution",
            }
            for index in range(102)
        ]
        protocol = canonical(
            {
                "schema_version": (
                    "strict_v4_vgrf_selected_system_execution_protocol_v1"
                ),
                "selected_algorithm": (
                    "caeos_validation_gated_class_conditional_"
                    "reliability_fusion"
                ),
                "source_registry": records,
            }
        )
        self.assertEqual(len(seed317_records(protocol)), 102)
        protocol["source_registry"][-1] = dict(
            protocol["source_registry"][0]
        )
        protocol["manifest_sha256"] = canonical_hash(protocol)
        with self.assertRaisesRegex(ValueError, "102 unique"):
            seed317_records(protocol)

    def test_source_input_hash_tamper_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            paths = {
                "csv": project / "data.csv",
                "config": project / "config.json",
                "source_provenance": project / "pairwise.json",
                "opendetect_source_provenance": project / "open.json",
            }
            for name, path in paths.items():
                path.write_text(
                    json.dumps({"name": name}), encoding="utf-8"
                )
            record = {
                "source_inputs": {
                    "csv": str(paths["csv"]),
                    "csv_sha256": file_hash(paths["csv"]),
                    "config": str(paths["config"]),
                    "config_sha256": file_hash(paths["config"]),
                    "source_provenance": str(
                        paths["source_provenance"]
                    ),
                    "source_provenance_sha256": file_hash(
                        paths["source_provenance"]
                    ),
                    "opendetect_source_provenance": str(
                        paths["opendetect_source_provenance"]
                    ),
                    "opendetect_source_provenance_sha256": file_hash(
                        paths["opendetect_source_provenance"]
                    ),
                }
            }
            paths["csv"].write_text("tampered", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SHA mismatch"):
                validate_source_inputs(project, record)


if __name__ == "__main__":
    unittest.main()
