from __future__ import annotations

import copy
import hashlib
import tempfile
from pathlib import Path
import unittest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_training_full102_expansion_protocol import (
    create_protocol,
    freeze_or_validate_protocol,
)


class TrainingFull102ExpansionProtocolTests(unittest.TestCase):
    def coverage(self) -> dict:
        registry = {
            "suite_%d" % index: {
                "scenarios": ["scenario_%d_%d" % (index, item) for item in range(count)]
            }
            for index, count in enumerate((15, 15, 15, 15, 14, 14, 14))
        }
        value = {
            "schema_version": "strict_v4_coverage_manifest_v2",
            "scenario_registry": registry,
        }
        value["manifest_sha256"] = canonical_hash(value)
        return value

    def project(self, root: Path, names: tuple[str, ...]) -> dict[str, str]:
        hashes = {}
        for name in names:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(name + "\n", encoding="ascii")
            hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        return hashes

    def fixtures(self, root: Path, group: str) -> tuple[dict, dict]:
        if group == "complementary":
            schema = "strict_v4_complementary_training_pilot_protocol_v1"
            analysis_schema = "strict_v4_complementary_training_pilot_analysis_v1"
            method = "palm"
            names = (
                "run_neural_baseline_matrix.py",
                "train_neural_open_set.py",
                "train_foss_open_set.py",
            )
        else:
            schema = "strict_v4_aegis_training_pilot_protocol_v1"
            analysis_schema = "strict_v4_aegis_training_pilot_analysis_v1"
            method = "aegis_clean_adapter"
            names = (
                "run_aegis_baseline_matrix.py",
                "train_aegis_open_set.py",
                "caeos/aegis.py",
            )
        pilot = {
            "schema_version": schema,
            "implementation_sha256": self.project(root, names),
        }
        pilot["manifest_sha256"] = canonical_hash(pilot)
        analysis = {
            "schema_version": analysis_schema,
            "status": "complete",
            "pilot_protocol_manifest_sha256": pilot["manifest_sha256"],
            "candidate_decisions": {method: {"expand_to_full102": True}},
            "expand_to_full102": [method],
        }
        return pilot, analysis

    def test_complementary_protocol_is_zero_result_frozen_and_bound(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pilot, analysis = self.fixtures(root, "complementary")
            protocol = create_protocol(
                "complementary",
                self.coverage(),
                pilot,
                analysis,
                "a" * 64,
                root,
                0,
            )
        self.assertEqual(protocol["manifest_sha256"], canonical_hash(protocol))
        self.assertEqual(protocol["expected_scenarios"], 102)
        self.assertEqual(protocol["expected_runs"], 102)
        self.assertEqual(protocol["methods"], ["palm"])

    def test_aegis_protocol_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pilot, analysis = self.fixtures(root, "aegis")
            protocol = create_protocol(
                "aegis", self.coverage(), pilot, analysis, "b" * 64, root, 0
            )
        self.assertEqual(protocol["group"], "aegis")
        self.assertEqual(protocol["methods"], ["aegis_clean_adapter"])

    def test_protocol_rejects_nonzero_results_or_missing_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pilot, analysis = self.fixtures(root, "complementary")
            with self.assertRaisesRegex(ValueError, "zero results"):
                create_protocol(
                    "complementary",
                    self.coverage(),
                    pilot,
                    analysis,
                    "a" * 64,
                    root,
                    1,
                )
            analysis["expand_to_full102"] = []
            with self.assertRaisesRegex(ValueError, "does not require"):
                create_protocol(
                    "complementary",
                    self.coverage(),
                    pilot,
                    analysis,
                    "a" * 64,
                    root,
                    0,
                )

    def test_protocol_rejects_pilot_or_implementation_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pilot, analysis = self.fixtures(root, "aegis")
            tampered = copy.deepcopy(pilot)
            tampered["extra"] = True
            with self.assertRaisesRegex(ValueError, "protocol SHA"):
                create_protocol(
                    "aegis", self.coverage(), tampered, analysis, "b" * 64, root, 0
                )
            (root / "caeos/aegis.py").write_text("changed\n", encoding="ascii")
            with self.assertRaisesRegex(ValueError, "implementation changed"):
                create_protocol(
                    "aegis", self.coverage(), pilot, analysis, "b" * 64, root, 0
                )

    def test_existing_protocol_is_revalidated_against_current_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "protocol_manifest.json"
            expected = {"schema_version": "example", "manifest_sha256": "a" * 64}
            self.assertEqual(freeze_or_validate_protocol(path, expected, 0), expected)
            self.assertEqual(freeze_or_validate_protocol(path, expected, 9), expected)
            changed = dict(expected, manifest_sha256="b" * 64)
            with self.assertRaisesRegex(ValueError, "differs from current bound evidence"):
                freeze_or_validate_protocol(path, changed, 9)


if __name__ == "__main__":
    unittest.main()
