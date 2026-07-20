from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from confirm_fixed_report_candidate import (
    load_confirmation_rows,
    validate_manifest,
)


METRICS = {
    "known_macro_f1": 0.9,
    "unknown_auroc": 0.8,
    "unknown_aupr": 0.7,
    "unknown_fpr95": 0.4,
    "oscr": 0.75,
    "known_acceptance_rate": 0.95,
    "unknown_rejection_rate": 0.5,
}
POLICY = "holdout_policy"
REFERENCE = "cauchy_modality_support_union"


def write_manifest(path: Path) -> dict[str, object]:
    core = {
        "schema_version": "edge_fixed_risk_candidate_manifest_v1",
        "status": "frozen_unconfirmed",
        "selected_candidate": "entropy",
        "selection_rule": {"primary": "auroc"},
        "development_seeds": [7, 11],
        "confirmation_seeds": [67, 71],
        "development_scenario_count": 2,
        "development_method_count": 3,
        "source_metrics_combined_sha256": "a" * 64,
        "candidate_runtime_selection_uses_unknown_or_test_labels": False,
        "development_candidate_screening_uses_test_unknown_labels": True,
        "confirmation_labels_must_remain_unseen_until_manifest_is_frozen": True,
    }
    digest = hashlib.sha256(
        json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    manifest = {**core, "manifest_sha256": digest}
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest


class ConfirmFixedReportCandidateTest(unittest.TestCase):
    def write_run(self, root: Path, scenario: str, seed: int) -> None:
        directory = root / "edge_iiot" / f"{scenario}_seed{seed}"
        directory.mkdir(parents=True)
        entropy = dict(METRICS)
        entropy["unknown_auroc"] += 0.05
        payload = {
            "risk_policy": POLICY,
            "selected_risk": REFERENCE,
            "selected_report": METRICS,
            "reports": {REFERENCE: METRICS, "entropy": entropy},
            "risk_selection_details": {
                "unknown_or_test_labels_used_for_selection": False,
            },
            "split_metadata": {
                "split_fingerprint": {"combined": f"{scenario}-{seed}"}
            },
        }
        (directory / "metrics.json").write_text(json.dumps(payload), encoding="utf-8")
        for name in ("scores.npz", "evidence_package.npz", "provenance.json"):
            (directory / name).touch()

    def test_manifest_hash_tampering_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "manifest.json"
            manifest = write_manifest(path)
            manifest["selected_candidate"] = "msp"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                validate_manifest(path)

    def test_complete_held_out_matrix_is_loaded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = root / "manifest.json"
            manifest = write_manifest(manifest_path)
            for scenario in ("a", "b"):
                for seed in (67, 71):
                    self.write_run(root, scenario, seed)
            rows, validation = load_confirmation_rows(
                root, manifest, 2, REFERENCE, POLICY
            )
            self.assertEqual(4, len(rows))
            self.assertTrue(validation["candidate_was_frozen_before_confirmation"])
            self.assertTrue(validation["candidate_report_extracted_from_same_model_run"])

    def test_missing_confirmation_seed_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = root / "manifest.json"
            manifest = write_manifest(manifest_path)
            self.write_run(root, "a", 67)
            self.write_run(root, "b", 67)
            self.write_run(root, "b", 71)
            with self.assertRaisesRegex(ValueError, "seed coverage mismatch"):
                load_confirmation_rows(root, manifest, 2, REFERENCE, POLICY)


if __name__ == "__main__":
    unittest.main()
