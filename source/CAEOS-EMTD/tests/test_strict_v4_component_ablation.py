import unittest

from summarize_strict_v4_component_ablation import (
    ABLATION_METHODS,
    REFERENCE_METHOD,
    REPORT_METRICS,
    compare_method,
)


def make_row(suite, reference_value, comparison_value):
    reports = {}
    for method in (REFERENCE_METHOD,) + ABLATION_METHODS:
        value = comparison_value if method == "baseline" else reference_value
        reports[method] = {metric: value for metric in REPORT_METRICS}
    reports["selected_pairwise_endpoint"] = {
        metric: reference_value for metric in REPORT_METRICS
    }
    return {"suite": suite, "scenario": suite + "_scenario", "reports": reports}


class StrictV4ComponentAblationTests(unittest.TestCase):
    def test_oriented_improvement_reverses_fpr95(self):
        rows = [make_row("a", 0.8, 0.7), make_row("b", 0.6, 0.5)]
        result = compare_method(rows, "baseline", 100, 17)
        self.assertAlmostEqual(
            result["metrics"]["unknown_auroc"]["oriented_mean_improvement"], 0.1
        )
        self.assertAlmostEqual(
            result["metrics"]["unknown_fpr95"]["oriented_mean_improvement"], -0.1
        )
        self.assertEqual(
            result["metrics"]["unknown_auroc"]["scenario_wins_ties_losses"]["wins"],
            2,
        )

    def test_selected_endpoint_ties_reference(self):
        rows = [make_row("a", 0.8, 0.7), make_row("b", 0.6, 0.5)]
        result = compare_method(rows, "selected_pairwise_endpoint", 100, 19)
        self.assertEqual(result["four_unknown_metric_oriented_mean"], 0.0)
        self.assertEqual(
            result["metrics"]["oscr"]["scenario_wins_ties_losses"]["ties"], 2
        )


if __name__ == "__main__":
    unittest.main()
