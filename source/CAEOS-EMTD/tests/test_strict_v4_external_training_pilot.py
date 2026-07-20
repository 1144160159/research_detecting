from __future__ import annotations

import copy
import tempfile
from pathlib import Path
import unittest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_external_training_pilot_protocol import (
    METHODS,
    SELECTED_SCENARIOS,
    create_gate,
    create_protocol,
)
from summarize_strict_v4_external_training_pilot import no_test_label_fit, report


class ExternalTrainingPilotProtocolTests(unittest.TestCase):
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
        for name in (
            "run_neural_baseline_matrix.py",
            "train_neural_open_set.py",
            "train_sieve_open_set.py",
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
        self.assertEqual(protocol["expected_runs"], 42)
        self.assertEqual(tuple(protocol["methods"]), METHODS)
        self.assertFalse(protocol["unknown_or_test_labels_used_for_fitting_or_selection"])
        self.assertEqual(gate["pilot_protocol_manifest_sha256"], protocol["manifest_sha256"])

    def test_protocol_rejects_observed_results(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.project(root)
            with self.assertRaisesRegex(ValueError, "zero results"):
                create_protocol(self.coverage(), root, 1)

    def test_protocol_rejects_scenario_outside_registry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.project(root)
            coverage = self.coverage()
            coverage["scenario_registry"]["cicids2017"]["scenarios"] = ["dos_hulk"]
            coverage["manifest_sha256"] = canonical_hash(coverage)
            with self.assertRaisesRegex(ValueError, "outside coverage"):
                create_protocol(coverage, root, 0)

    def test_gate_rejects_protocol_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.project(root)
            protocol = create_protocol(self.coverage(), root, 0)
            tampered = copy.deepcopy(protocol)
            tampered["seed"] = 11
            with self.assertRaisesRegex(ValueError, "SHA mismatch"):
                create_gate(tampered)

    def test_sieve_legacy_provenance_is_accepted_without_backfill(self) -> None:
        protocol = {
            "fit_data": "known_training_only",
            "checkpoint_and_threshold_data": "known_validation_only",
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
        }
        payload = {
            "implementation": (
                "preprocessing and checkpoint selection use training statistics "
                "and known validation only"
            ),
            "source_reference": {
                "adapter_repairs": [
                    "select checkpoints on known validation instead of the test set",
                    "fit preprocessing on training data only",
                ]
            },
            "reports": {"sieve": {}},
            "validation_thresholds": {"sieve": 0.5},
        }
        self.assertTrue(no_test_label_fit(payload, "sieve", protocol))
        payload["source_reference"]["adapter_repairs"].remove(
            "select checkpoints on known validation instead of the test set"
        )
        self.assertFalse(no_test_label_fit(payload, "sieve", protocol))

    def test_palm_protocol_name_resolves_adapter_report_alias(self) -> None:
        expected = {
            "known_macro_f1": 0.9,
            "unknown_auroc": 0.8,
            "unknown_aupr": 0.7,
            "unknown_fpr95": 0.2,
            "oscr": 0.6,
        }
        payload = {"reports": {"palm_ssd_plus": expected}}
        self.assertEqual(report(payload, "palm", Path("metrics.json")), expected)


if __name__ == "__main__":
    unittest.main()
