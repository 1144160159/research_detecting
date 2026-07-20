from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from audit_strict_v4_running_confirmations import (
    audit_mlp_root,
    audit_root,
    expected_identities,
    validate_protocol,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash


def coverage():
    return {
        "scenario_registry": {
            "suite": {"scenarios": ["attack_a", "attack_b"]}
        }
    }


def write_run(root: Path, leakage: bool = False) -> None:
    run = root / "suite" / "attack_a_seed7"
    run.mkdir(parents=True)
    metrics = {
        "seed": 7,
        "risk_policy": "policy",
        "risk_selection": "selection",
        "risk_selection_details": {
            "unknown_or_test_labels_used_for_selection": leakage
        },
        "selected_risk": "risk",
        "selected_report": {},
        "reports": {"risk": {}},
        "split_metadata": {"split_fingerprint": {"combined": "abc"}},
    }
    (run / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
    (run / "provenance.json").write_text(
        json.dumps({"split_fingerprint": {"combined": "abc"}}), encoding="utf-8"
    )
    (run / "scores.npz").write_bytes(b"scores")
    (run / "evidence_package.npz").write_bytes(b"evidence")


def write_mlp_run(
    root: Path, leakage: bool = False, report: str = "openmax"
) -> None:
    run = root / "suite" / "attack_a_seed7_mlp"
    run.mkdir(parents=True)
    metrics = {
        "seed": 7,
        "model": "mlp",
        "reports": {report: {}},
        "selection_evidence": {
            "unknown_or_test_labels_used_for_fitting_or_selection": leakage
        },
        "split_metadata": {"split_fingerprint": {"combined": "abc"}},
    }
    (run / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
    (run / "provenance.json").write_text(
        json.dumps({"split_fingerprint": {"combined": "abc"}}), encoding="utf-8"
    )
    (run / "scores.npz").write_bytes(b"scores")
    (run / "model.pt").write_bytes(b"model")


class StrictV4RunningConfirmationHealthTests(unittest.TestCase):
    def test_partial_valid_matrix_passes_health(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_run(root)
            result = audit_root(root, coverage(), (7,), "policy", "selection")
            self.assertTrue(result["validation"]["passes"])
            self.assertEqual(result["validation"]["completed_runs"], 1)
            self.assertEqual(result["validation"]["remaining_runs"], 1)

    def test_leakage_guard_fails_health(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_run(root, leakage=True)
            result = audit_root(root, coverage(), (7,), "policy", "selection")
            self.assertFalse(result["validation"]["passes"])
            self.assertIn("leakage", result["report_errors"][0])

    def test_expected_identities_expand_scenarios_by_seed(self):
        identities = expected_identities(coverage(), (7, 11))
        self.assertEqual(len(identities), 4)

    def test_partial_valid_mlp_matrix_passes_health(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_mlp_run(root)
            result = audit_mlp_root(root, coverage(), (7,))
            self.assertTrue(result["validation"]["passes"])
            self.assertEqual(result["validation"]["completed_runs"], 1)
            self.assertEqual(result["validation"]["remaining_runs"], 1)
            self.assertEqual(result["required_report_counts"]["openmax"], 1)

    def test_mlp_missing_openmax_or_leakage_fails_health(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_mlp_run(root, leakage=True, report="msp")
            result = audit_mlp_root(root, coverage(), (7,))
            self.assertFalse(result["validation"]["passes"])
            self.assertEqual(result["validation"]["report_error_count"], 2)

    def test_nested_coverage_binding_is_accepted(self):
        protocol = {
            "schema_version": "tail_schema",
            "bindings": {"coverage_manifest_sha256": "coverage_sha"},
        }
        protocol["manifest_sha256"] = canonical_hash(protocol)
        checks = validate_protocol(protocol, "tail_schema", "coverage_sha")
        self.assertTrue(all(checks.values()))


if __name__ == "__main__":
    unittest.main()
