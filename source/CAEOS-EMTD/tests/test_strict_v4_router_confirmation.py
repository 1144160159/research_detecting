from __future__ import annotations

import unittest

from confirm_strict_v4_domain_safe_router import build_rows, confirmation_decision
from create_strict_v4_router_confirmation_manifest import parse_seeds


def inference(metric_gain: float = 0.1) -> dict:
    metrics = {}
    for metric in (
        "known_macro_f1",
        "unknown_auroc",
        "unknown_aupr",
        "unknown_fpr95",
        "oscr",
    ):
        gain = 0.0 if metric == "known_macro_f1" else metric_gain
        metrics[metric] = {
            "oriented_mean_improvement": gain,
            "raw_mean_delta": 0.0 if metric == "known_macro_f1" else gain,
            "bootstrap_95_ci": {"lower": 0.01 if gain else 0.0},
            "wilcoxon": {"holm_adjusted_p_value": None if not gain else 0.01},
        }
    return {"metrics": metrics}


class StrictV4RouterConfirmationTests(unittest.TestCase):
    def test_confirmation_seeds_are_unique_new_and_at_least_three(self) -> None:
        self.assertEqual(parse_seeds("149,137,139"), [137, 139, 149])
        for invalid in ("137,139", "137,137,139", "7,137,139"):
            with self.assertRaises(ValueError):
                parse_seeds(invalid)

    def test_strict_confirmation_gate_passes_complete_evidence(self) -> None:
        report = confirmation_decision(
            inference(), {"suite": {metric: 0.01 for metric in (
                "unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr"
            )}}
        )
        self.assertTrue(report["passes"])

    def test_suite_regression_fails_closed(self) -> None:
        values = {metric: 0.01 for metric in (
            "unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr"
        )}
        values["unknown_aupr"] = -1e-3
        report = confirmation_decision(inference(), {"suite": values})
        self.assertFalse(report["passes"])

    def test_raw_fusion_leakage_audit_is_required(self) -> None:
        report = {
            "known_macro_f1": 0.8,
            "unknown_auroc": 0.8,
            "unknown_aupr": 0.7,
            "unknown_fpr95": 0.2,
            "oscr": 0.75,
            "known_acceptance_rate": 0.95,
            "unknown_rejection_rate": 0.6,
        }
        runs = []
        for seed in (137, 139, 149):
            runs.append(
                {
                    "suite": "suite",
                    "task": f"attack_seed{seed}",
                    "gate_report": report,
                    "reports": {},
                    "audit": {
                        "split_fingerprints_identical": True,
                        "caeos_unknown_or_test_labels_used_for_selection": False,
                        "expert_unknown_or_test_labels_used_for_fitting_or_selection": False,
                        "fusion_calibration_split": "known_only_validation",
                        "test_labels_used_for_final_metrics_only": True,
                    },
                }
            )
        raw = {
            "overall": {"number_of_runs": 3},
            "selection_scope": {"seeds": [137, 139, 149]},
            "runs": runs,
        }
        coverage = {"scenario_registry": {"suite": {"scenarios": ["attack"]}}}
        router = {"routing": {"suite": {"method": "caeos_pairwise"}}}
        protocol = {"confirmation_seeds": [137, 139, 149]}
        rows, validation = build_rows(raw, coverage, router, protocol)
        self.assertEqual(len(rows), 3)
        self.assertEqual(validation["known_only_fusion_calibration_checks"], 3)
        raw["runs"][0]["audit"]["test_labels_used_for_final_metrics_only"] = False
        with self.assertRaisesRegex(ValueError, "leakage audit"):
            build_rows(raw, coverage, router, protocol)


if __name__ == "__main__":
    unittest.main()
