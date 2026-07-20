from __future__ import annotations

import unittest

from summarize_sota_decision import METRICS, build_decision


def scope() -> dict[str, object]:
    methods = {}
    for method, baseline in (("a", 0.7), ("b", 0.6)):
        metrics = {}
        for metric in METRICS:
            lower = metric == "unknown_fpr95"
            gate = 0.2 if lower else 0.8
            base = 0.3 if lower else baseline
            metrics[metric] = {
                "gate_scenario_mean": gate,
                "baseline_scenario_mean": base,
                "paired_inference": {
                    "mean_delta": 0.1 if method == "a" else 0.2,
                    "wins": 14,
                    "ties": 0,
                    "losses": 0,
                    "bootstrap_95_ci": {"lower": 0.01, "upper": 0.3},
                    "wilcoxon": {"holm_adjusted_p_value": 0.01},
                },
            }
        methods[method] = {"metrics": metrics}
    return {"scope": "global", "scenario_inference_units": 14, "methods": methods}


class SotaDecisionTest(unittest.TestCase):
    def test_rank_and_confirmation_are_separate(self) -> None:
        item = scope()
        report = {"schema_version": "strict_v2", "global": item, "by_suite": {"edge": item}}
        result = build_decision(report)
        self.assertTrue(result["global"]["all_metrics_mean_rank_one"])
        self.assertTrue(result["global"]["all_primary_strongest_comparisons_confirmed"])
        self.assertTrue(result["global"]["all_metrics_strongest_comparisons_confirmed"])
        self.assertTrue(result["claim_gate"]["full_sota_claim_allowed"])
        self.assertEqual(
            result["claim_gate"]["highest_supported_claim"],
            "comprehensive_confirmed_sota",
        )
        self.assertEqual(
            result["global"]["metrics"]["unknown_auroc"]["strongest_baseline"],
            "a",
        )

    def test_non_significant_rank_one_is_not_confirmed(self) -> None:
        item = scope()
        item["methods"]["a"]["metrics"]["unknown_auroc"]["paired_inference"][
            "wilcoxon"
        ]["holm_adjusted_p_value"] = 0.2
        report = {"schema_version": "strict_v2", "global": item, "by_suite": {}}
        result = build_decision(report)
        metric = result["global"]["metrics"]["unknown_auroc"]
        self.assertEqual(metric["caeos_rank_among_all_methods"], 1)
        self.assertFalse(metric["confirmed_better_than_strongest"])
        self.assertFalse(result["claim_gate"]["full_sota_claim_allowed"])
        self.assertEqual(
            result["claim_gate"]["highest_supported_claim"],
            "global_primary_mean_sota_only",
        )

    def test_missing_suite_results_fail_closed(self) -> None:
        item = scope()
        report = {"schema_version": "strict_v2", "global": item, "by_suite": {}}
        result = build_decision(report)
        gates = result["claim_gate"]["gates"]
        self.assertFalse(gates["cross_suite_primary_mean_rank_one"])
        self.assertFalse(gates["cross_suite_all_metrics_confirmed"])
        self.assertFalse(result["claim_gate"]["full_sota_claim_allowed"])
        self.assertEqual(
            result["claim_gate"]["highest_supported_claim"],
            "global_confirmed_primary_sota",
        )

    def test_suite_significance_is_reported_but_not_an_impossible_full_gate(self) -> None:
        global_item = scope()
        suite_item = scope()
        suite_item["methods"]["a"]["metrics"]["unknown_auroc"][
            "paired_inference"
        ]["wilcoxon"]["holm_adjusted_p_value"] = 0.2
        report = {
            "schema_version": "strict_v2",
            "global": global_item,
            "by_suite": {"small_suite": suite_item},
        }
        result = build_decision(report)
        gates = result["claim_gate"]["gates"]
        self.assertFalse(gates["cross_suite_all_metrics_confirmed"])
        self.assertTrue(gates["cross_suite_all_metrics_mean_rank_one"])
        self.assertTrue(result["claim_gate"]["full_sota_claim_allowed"])
        self.assertEqual(
            result["claim_gate"]["confirmatory_scope"],
            "global_scenario_blocked_family",
        )


if __name__ == "__main__":
    unittest.main()
