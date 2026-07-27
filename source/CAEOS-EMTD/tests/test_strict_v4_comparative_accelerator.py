from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from accelerate_strict_v4_comparative_corruption import (
    block_path,
    contiguous_completed,
    select_pending_indices,
    validate_block,
    validate_block_with_retry,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash


def protocol_fixture(count: int = 6) -> dict:
    sources = [
        {
            "suite": "suite",
            "scenario": f"scenario_{index}",
            "seed": 137,
            "split_fingerprint": f"split_{index}",
        }
        for index in range(count)
    ]
    value = {
        "schema_version": "strict_v4_comparative_corruption_protocol_v2",
        "source_registry": sources,
        "corruption_conditions": {"families": ["a", "b"]},
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def write_valid_block(
    root: Path,
    protocol: dict,
    source_index: int,
) -> Path:
    source = protocol["source_registry"][source_index]
    value = {
        "schema_version": "strict_v4_comparative_corruption_block_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "suite": source["suite"],
        "scenario": source["scenario"],
        "seed": source["seed"],
        "source_split_fingerprint": source["split_fingerprint"],
        "candidate_comparator_input_arrays_equal": True,
        "unknown_or_test_labels_used_for_fitting_selection_or_corruption_generation": False,
        "conditions": [{"family": "a"}, {"family": "b"}],
    }
    value["manifest_sha256"] = canonical_hash(value)
    path = block_path(root, source) / "paired_corruption.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


class ComparativeAcceleratorTests(unittest.TestCase):
    def test_valid_block_is_recomputed(self) -> None:
        protocol = protocol_fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = write_valid_block(root, protocol, 0)
            value = validate_block(
                path,
                protocol,
                protocol["source_registry"][0],
            )
            self.assertEqual(value["manifest_sha256"], canonical_hash(value))

    def test_tampered_block_is_rejected(self) -> None:
        protocol = protocol_fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = write_valid_block(root, protocol, 0)
            value = json.loads(path.read_text(encoding="utf-8"))
            value["scenario"] = "wrong"
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "validation failed"):
                validate_block(
                    path,
                    protocol,
                    protocol["source_registry"][0],
                )

    def test_retry_validator_reads_complete_block(self) -> None:
        protocol = protocol_fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = write_valid_block(root, protocol, 0)
            value = validate_block_with_retry(
                path,
                protocol,
                protocol["source_registry"][0],
                attempts=1,
                delay_seconds=0.0,
            )
            self.assertEqual(value["scenario"], "scenario_0")

    def test_contiguous_frontier_stops_at_first_gap(self) -> None:
        protocol = protocol_fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_valid_block(root, protocol, 0)
            write_valid_block(root, protocol, 1)
            write_valid_block(root, protocol, 3)
            self.assertEqual(contiguous_completed(protocol, root), 2)

    def test_pending_indices_are_reverse_and_skip_completed(self) -> None:
        protocol = protocol_fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_valid_block(root, protocol, 0)
            write_valid_block(root, protocol, 5)
            frontier, indices = select_pending_indices(
                protocol,
                root,
                minimum_source_index=3,
                minimum_frontier_gap=2,
                max_tasks=None,
            )
            self.assertEqual(frontier, 1)
            self.assertEqual(indices, [4, 3])

    def test_frontier_gap_is_fail_closed(self) -> None:
        protocol = protocol_fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_valid_block(root, protocol, 0)
            write_valid_block(root, protocol, 1)
            with self.assertRaisesRegex(ValueError, "frontier gap"):
                select_pending_indices(
                    protocol,
                    root,
                    minimum_source_index=3,
                    minimum_frontier_gap=2,
                    max_tasks=None,
                )

    def test_executor_only_replaces_candidate_output_directory(self) -> None:
        root = Path(__file__).resolve().parents[1]
        source = (
            root / "accelerate_strict_v4_comparative_corruption.py"
        ).read_text(encoding="utf-8")
        self.assertEqual(source.count("replace_option("), 1)
        self.assertIn('"--output-dir"', source)
        self.assertIn(
            '"changes_training_or_evaluation_arguments_other_than_output_dir": False',
            source,
        )
        self.assertIn(
            '"parallel_results_require_original_block_manifest_validation": True',
            source,
        )


if __name__ == "__main__":
    unittest.main()
