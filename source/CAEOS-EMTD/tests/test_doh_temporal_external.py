from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from create_doh_temporal_external_protocol import canonical_hash
from summarize_doh_temporal_external import METRICS, summarize


class DoHTemporalExternalSummaryTest(unittest.TestCase):
    def test_summary_orients_fpr95_and_checks_identical_splits(self):
        protocol = {
            "schema_version": "doh_temporal_external_protocol_v1",
            "experiment": {"seeds": [223]},
            "pilot_gate": {"minimum_nonnegative_mean_metric_count": 4},
            "claim_boundary": {"supported": "temporal"},
        }
        protocol["manifest_sha256"] = canonical_hash(protocol)
        split = {
            "strategy": "temporal_capture_grouped",
            "group_overlap": {"train_validation": 0, "train_test": 0, "validation_test": 0},
            "per_class_time_ranges": {
                "benign": {
                    "train": {"maximum": "2020-01-01"},
                    "validation": {"minimum": "2020-01-02", "maximum": "2020-01-02"},
                    "test": {"minimum": "2020-01-03"},
                }
            },
            "split_fingerprint": {"combined": "abc"},
        }
        candidate = {metric: 0.8 for metric in METRICS}
        comparator = {metric: 0.7 for metric in METRICS}
        candidate["unknown_fpr95"] = 0.2
        comparator["unknown_fpr95"] = 0.3
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for suffix, payload in (
                ("pairwise", {"seed": 223, "split_metadata": split, "selected_report": candidate}),
                ("opendetect", {"seed": 223, "split_metadata": split, "reports": {"opendetect": comparator}}),
            ):
                target = root / f"seed223_{suffix}"
                target.mkdir()
                (target / "metrics.json").write_text(json.dumps(payload), encoding="utf-8")
            result = summarize(protocol, root)
        self.assertEqual(result["run_count"], 2)
        self.assertTrue(result["pilot_gate_passes"])
        self.assertAlmostEqual(result["mean_oriented_difference"]["unknown_fpr95"], 0.1)


if __name__ == "__main__":
    unittest.main()
