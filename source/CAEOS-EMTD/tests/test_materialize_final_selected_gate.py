from __future__ import annotations

import unittest

from materialize_final_selected_gate import ENTROPY, REFERENCE, rewrite_metrics


def source_metrics() -> dict[str, object]:
    report = {
        "known_macro_f1": 0.9,
        "unknown_auroc": 0.8,
        "unknown_aupr": 0.7,
        "unknown_fpr95": 0.4,
        "oscr": 0.75,
    }
    entropy = {**report, "unknown_auroc": 0.85}
    return {
        "seed": 7,
        "selected_risk": REFERENCE,
        "selected_report": report,
        "reports": {ENTROPY: entropy},
        "risk_selection": REFERENCE,
        "risk_policy": "source",
        "parameter_fingerprint": "a" * 64,
        "arguments": {"risk_selection": REFERENCE, "risk_policy": "source"},
    }


class MaterializeFinalSelectedGateTest(unittest.TestCase):
    def test_edge_entropy_rewrites_policy_and_report(self) -> None:
        result, fingerprint = rewrite_metrics(
            source_metrics(), "edge_iiot", ENTROPY, "b" * 64, "c" * 64
        )
        self.assertEqual(result["selected_risk"], ENTROPY)
        self.assertEqual(result["risk_selection"], ENTROPY)
        self.assertEqual(result["arguments"]["risk_selection"], ENTROPY)
        self.assertEqual(result["selected_report"]["unknown_auroc"], 0.85)
        self.assertEqual(len(fingerprint), 64)
        self.assertFalse(
            result["final_internal_risk_selection"][
                "unknown_or_test_labels_used_for_runtime_selection"
            ]
        )

    def test_non_edge_suite_keeps_its_confirmed_risk(self) -> None:
        source = source_metrics()
        result, _ = rewrite_metrics(
            source, "nf_cse", ENTROPY, "b" * 64, "c" * 64
        )
        self.assertEqual(result["selected_risk"], REFERENCE)
        self.assertEqual(result["risk_selection"], REFERENCE)
        self.assertEqual(result["arguments"]["risk_selection"], REFERENCE)
        self.assertIn(ENTROPY, result["risk_policy"])


if __name__ == "__main__":
    unittest.main()
