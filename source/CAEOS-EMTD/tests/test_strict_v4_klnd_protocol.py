from __future__ import annotations

import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_klnd_expansion_gate import create_gate
from run_strict_v4_klnd_matrix import git_blob_sha256, select_pilot_scenarios


class StrictV4KLNDProtocolTests(unittest.TestCase):
    def coverage(self) -> dict:
        return {
            "schema_version": "strict_v4_coverage_manifest_v2",
            "manifest_sha256": "a" * 64,
            "scenario_registry": {
                "suite_%d" % index: {
                    "scenarios": ["one", "two", "three", "four"]
                }
                for index in range(7)
            },
        }

    def protocol(self) -> dict:
        value = {
            "schema_version": "strict_v4_mlp_klnd_protocol_v1",
            "mode": "pilot",
            "expected_runs": 14,
            "class_center_data": (
                "correctly_classified_known_training_logits_only"
            ),
            "native_threshold_data": (
                "correctly_classified_known_validation_logits_only"
            ),
            "ood_parameter_sweep": False,
        }
        value["manifest_sha256"] = canonical_hash(value)
        return value

    def test_pilot_selection_is_deterministic_and_has_two_per_suite(self) -> None:
        first = select_pilot_scenarios(self.coverage())
        second = select_pilot_scenarios(self.coverage())
        self.assertEqual(first, second)
        self.assertEqual(len(first), 7)
        self.assertTrue(all(len(set(items)) == 2 for items in first.values()))

    def test_gate_freezes_before_results(self) -> None:
        gate = create_gate(self.protocol(), observed_metrics=0)
        self.assertEqual(
            gate["candidate_variants"], ["klnd1", "klnd2", "klnd3"]
        )
        self.assertEqual(gate["manifest_sha256"], canonical_hash(gate))
        self.assertEqual(gate["pilot_metrics_observed_at_freeze"], 0)

    def test_gate_rejects_observed_results(self) -> None:
        with self.assertRaisesRegex(ValueError, "before every pilot result"):
            create_gate(self.protocol(), observed_metrics=1)

    def test_gate_rejects_unknown_sweep(self) -> None:
        protocol = self.protocol()
        protocol["ood_parameter_sweep"] = True
        protocol["manifest_sha256"] = canonical_hash(protocol)
        with self.assertRaisesRegex(ValueError, "forbids OOD"):
            create_gate(protocol, observed_metrics=0)

    def test_official_file_identity_uses_git_blob_bytes(self) -> None:
        payload = b"line one\nline two\n"
        with patch(
            "run_strict_v4_klnd_matrix.subprocess.run"
        ) as completed:
            completed.return_value.stdout = payload
            observed = git_blob_sha256(Path("/repository"), "file.ipynb")
        self.assertEqual(observed, hashlib.sha256(payload).hexdigest())
        self.assertEqual(
            completed.call_args[0][0],
            [
                "git",
                "-C",
                str(Path("/repository")),
                "show",
                "HEAD:file.ipynb",
            ],
        )


if __name__ == "__main__":
    unittest.main()
