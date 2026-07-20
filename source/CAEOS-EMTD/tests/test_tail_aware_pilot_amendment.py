from __future__ import annotations

import copy
import unittest

from amend_strict_v4_tail_aware_pilot_protocol import amend
from create_strict_v4_external_confirmation_protocol import canonical_hash


def protocol() -> dict:
    payload = {
        "schema_version": "strict_v4_tail_aware_pilot_protocol_v1",
        "status": "frozen_before_pilot",
        "implementation_sha256": {
            "caeos/tail_aware_ranking.py": "old-tail",
            "train_hybrid_open_set.py": "old-train",
            "run_nested_gate_matrix.py": "same-matrix",
        },
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


class TailAwarePilotAmendmentTests(unittest.TestCase):
    def test_report_only_failure_can_be_refrozen(self) -> None:
        original = protocol()
        revised, record = amend(
            original,
            current_hashes={
                "caeos/tail_aware_ranking.py": "new-tail",
                "train_hybrid_open_set.py": "new-train",
                "run_nested_gate_matrix.py": "same-matrix",
            },
            failure_logs={
                "ransomware_seed7": b"selected_alpha\nKeyError: '0.5'\n",
                "uploading_seed7": b"selected_alpha\nKeyError: '0.5'\n",
            },
        )
        self.assertEqual(revised["manifest_sha256"], canonical_hash(revised))
        self.assertEqual(
            revised["protocol_revision"]["supersedes_manifest_sha256"],
            original["manifest_sha256"],
        )
        self.assertFalse(record["algorithm_hyperparameter_scenario_or_seed_changed"])
        self.assertFalse(record["metrics_scores_or_evidence_produced"])

    def test_unexpected_source_change_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "unauthorized"):
            amend(
                protocol(),
                current_hashes={
                    "caeos/tail_aware_ranking.py": "new-tail",
                    "train_hybrid_open_set.py": "new-train",
                    "run_nested_gate_matrix.py": "changed-matrix",
                },
                failure_logs={
                    "a": b"selected_alpha\nKeyError: '0.5'\n",
                    "b": b"selected_alpha\nKeyError: '0.5'\n",
                },
            )

    def test_protocol_sha_mismatch_fails_closed(self) -> None:
        value = copy.deepcopy(protocol())
        value["status"] = "changed"
        with self.assertRaisesRegex(ValueError, "SHA"):
            amend(
                value,
                current_hashes=value["implementation_sha256"],
                failure_logs={
                    "a": b"selected_alpha\nKeyError: '0.5'\n",
                    "b": b"selected_alpha\nKeyError: '0.5'\n",
                },
            )


if __name__ == "__main__":
    unittest.main()
