from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_postselection_corruption import build_tasks, task_key
from summarize_strict_v4_corruption_progress import record_hash, summarize


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def make_inputs(root: Path) -> tuple[Path, Path, Path]:
    coverage = {
        "manifest_sha256": "a" * 64,
        "scenario_registry": {
            "suite_a": {"scenarios": ["attack_a", "attack_b"]}
        },
    }
    protocol = {
        "schema_version": "strict_v4_postselection_corruption_protocol_v1",
        "status": "frozen_post_selection_before_corruption_results",
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "sentinel_severity_screen": {
            "sentinel_scenarios": {"suite_a": "attack_a"}
        },
        "corruption_definitions": {
            "families": {"row_missing": [0.1, 0.3]}
        },
        "full102_confirmation": {
            "corruption_families": ["row_missing"],
            "fixed_severity": {"row_missing": 0.3},
        },
        "total_expected_corruption_runs": 8,
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    protocol_path = root / "protocol.json"
    coverage_path = root / "coverage.json"
    output_root = root / "runs"
    write_json(protocol_path, protocol)
    write_json(coverage_path, coverage)
    return protocol_path, coverage_path, output_root


class CorruptionProgressTests(unittest.TestCase):
    def test_reports_completed_started_and_remaining(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            protocol_path, coverage_path, output_root = make_inputs(root)
            protocol = json.loads(protocol_path.read_text())
            coverage = json.loads(coverage_path.read_text())
            first, second = build_tasks(protocol, coverage)[:2]

            first_root = output_root / task_key(first)
            record = {
                "schema_version": (
                    "strict_v4_postselection_corruption_run_v1"
                ),
                "task": asdict(first),
                "validation_passes": True,
                "unknown_or_test_labels_used_for_generation_fitting_or_selection": (
                    False
                ),
            }
            record["record_sha256"] = record_hash(record)
            write_json(first_root / "corruption_metrics.json", record)
            write_json(
                first_root
                / first.suite
                / f"{first.scenario}_seed7"
                / "provenance.json",
                {},
            )
            second_root = output_root / task_key(second)
            write_json(
                second_root
                / second.suite
                / f"{second.scenario}_seed7"
                / "provenance.json",
                {},
            )

            result = summarize(
                protocol_path, coverage_path, output_root
            )

        self.assertEqual(result["expected"], 8)
        self.assertEqual(result["completed"], 1)
        self.assertEqual(result["started_not_completed"], 1)
        self.assertEqual(result["remaining_including_started"], 7)
        self.assertFalse(result["effect_metrics_read"])
        self.assertEqual(
            result["record_sha256"], record_hash(result)
        )

    def test_rejects_tampered_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            protocol_path, coverage_path, output_root = make_inputs(root)
            protocol = json.loads(protocol_path.read_text())
            coverage = json.loads(coverage_path.read_text())
            task = build_tasks(protocol, coverage)[0]
            write_json(
                output_root / task_key(task) / "corruption_metrics.json",
                {
                    "schema_version": (
                        "strict_v4_postselection_corruption_run_v1"
                    ),
                    "task": asdict(task),
                    "record_sha256": "0" * 64,
                    "validation_passes": True,
                    "unknown_or_test_labels_used_for_generation_fitting_or_selection": (
                        False
                    ),
                },
            )
            with self.assertRaisesRegex(ValueError, "SHA mismatch"):
                summarize(protocol_path, coverage_path, output_root)


if __name__ == "__main__":
    unittest.main()
