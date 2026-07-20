from __future__ import annotations

import unittest

from confirm_strict_v4_external_comparator import confirmation_decision


def inference(gain: float = 0.1) -> dict:
    metrics = {}
    for metric in (
        "known_macro_f1",
        "unknown_auroc",
        "unknown_aupr",
        "unknown_fpr95",
        "oscr",
    ):
        metrics[metric] = {
            "oriented_mean_improvement": gain,
            "bootstrap_95_ci": {"lower": 0.01},
            "wilcoxon": {"holm_adjusted_p_value": 0.01},
        }
    return {"metrics": metrics}


class StrictV4ExternalComparatorConfirmationTests(unittest.TestCase):
    def test_complete_external_advantage_passes(self) -> None:
        suites = {
            "suite": {
                metric: 0.01
                for metric in (
                    "unknown_auroc",
                    "unknown_aupr",
                    "unknown_fpr95",
                    "oscr",
                )
            }
        }
        self.assertTrue(confirmation_decision(inference(), suites)["passes"])

    def test_one_suite_regression_fails_closed(self) -> None:
        suites = {
            "suite": {
                "unknown_auroc": 0.01,
                "unknown_aupr": -0.001,
                "unknown_fpr95": 0.01,
                "oscr": 0.01,
            }
        }
        self.assertFalse(confirmation_decision(inference(), suites)["passes"])


if __name__ == "__main__":
    unittest.main()
