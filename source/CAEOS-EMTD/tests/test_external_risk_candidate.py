from __future__ import annotations

import unittest

from select_strict_v4_external_risk_candidate import candidate_score, canonical_hash


class ExternalRiskCandidateTest(unittest.TestCase):
    def test_canonical_hash_ignores_embedded_hash(self) -> None:
        payload = {"schema_version": "x", "value": 3}
        digest = canonical_hash(payload)
        payload["manifest_sha256"] = "not-the-digest"
        self.assertEqual(canonical_hash(payload), digest)

    def test_candidate_score_uses_worst_suite_metric_first(self) -> None:
        metrics = {
            name: {"oriented_mean_delta": value}
            for name, value in {
                "unknown_auroc": 0.4,
                "unknown_aupr": 0.3,
                "unknown_fpr95": 0.2,
                "oscr": 0.1,
            }.items()
        }
        method = {
            "mean_delta_vs_gate": 0.4,
            "metrics": metrics,
        }
        payload = {
            "overall": {"methods": {"rank_union": method}},
            "by_suite": {
                "cic_ton_iot": {"methods": {"rank_union": {"metrics": metrics}}},
                "cic_iot2023": {"methods": {"rank_union": {"metrics": metrics}}},
            },
        }
        score = candidate_score(payload, "rank_union")
        for observed, expected in zip(score, (0.1, 0.4, 1.0)):
            self.assertAlmostEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
