from __future__ import annotations

import copy
import tempfile
from pathlib import Path
import unittest

from create_strict_v4_aegis_training_pilot_protocol import (
    METHODS,
    create_gate,
    create_protocol,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_external_training_pilot_protocol import SELECTED_SCENARIOS


class AEGISTrainingPilotProtocolTests(unittest.TestCase):
    def coverage(self) -> dict:
        value = {
            "schema_version": "strict_v4_coverage_manifest_v2",
            "scenario_registry": {
                suite: {"scenarios": list(scenarios)}
                for suite, scenarios in SELECTED_SCENARIOS.items()
            },
        }
        value["manifest_sha256"] = canonical_hash(value)
        return value

    def project(self, root: Path) -> None:
        (root / "caeos").mkdir()
        for name in (
            "run_aegis_baseline_matrix.py",
            "train_aegis_open_set.py",
            "caeos/aegis.py",
        ):
            (root / name).write_text(name + "\n", encoding="ascii")

    def test_protocol_and_gate_are_canonical_and_zero_result_frozen(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.project(root)
            protocol = create_protocol(self.coverage(), root, 0)
            gate = create_gate(protocol)
        self.assertEqual(protocol["manifest_sha256"], canonical_hash(protocol))
        self.assertEqual(gate["manifest_sha256"], canonical_hash(gate))
        self.assertEqual(protocol["expected_runs"], 14)
        self.assertEqual(tuple(protocol["methods"]), METHODS)
        self.assertFalse(protocol["unknown_or_test_labels_used_for_fitting_or_selection"])
        self.assertEqual(gate["pilot_protocol_manifest_sha256"], protocol["manifest_sha256"])

    def test_protocol_rejects_observed_results(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.project(root)
            with self.assertRaisesRegex(ValueError, "zero results"):
                create_protocol(self.coverage(), root, 1)

    def test_gate_rejects_protocol_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.project(root)
            protocol = create_protocol(self.coverage(), root, 0)
            tampered = copy.deepcopy(protocol)
            tampered["seed"] = 11
            with self.assertRaisesRegex(ValueError, "SHA mismatch"):
                create_gate(tampered)


if __name__ == "__main__":
    unittest.main()
