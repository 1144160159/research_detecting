import unittest

from summarize_strict_v4_mahalanobis_pp_pilot import analyze, oriented_gain


SUITES = ("a", "b", "c", "d", "e", "f", "g")


def report(value: float) -> dict[str, float]:
    return {
        "known_macro_f1": 0.8,
        "unknown_auroc": value,
        "unknown_aupr": value,
        "unknown_fpr95": 1.0 - value,
        "oscr": value,
    }


def protocol() -> dict[str, object]:
    return {
        "expected_scenarios": 14,
        "expansion_gate": {
            "failure_count": 0,
            "known_f1_max_absolute_difference_from_source_mlp": 1e-12,
            "four_unknown_metric_oriented_mean_gain_vs_mahalanobis_minimum": 0.0,
            "suite_nonnegative_gain_count_vs_mahalanobis_minimum": 5,
            "mean_unknown_metric_rank_among_three_maximum": 2.0,
        },
    }


class StrictV4MahalanobisPlusPlusSummaryTests(unittest.TestCase):
    def test_oriented_gain_reverses_fpr95(self) -> None:
        self.assertAlmostEqual(oriented_gain(report(0.8), report(0.7)), 0.1)

    def test_positive_consistent_pilot_passes_expansion_gate(self) -> None:
        blocks = {
            f"{suite}/scenario_{index}": {
                "mahalanobis_pp": report(0.8),
                "mlp_mahalanobis": report(0.7),
                "opendetect": report(0.75),
            }
            for suite in SUITES
            for index in (1, 2)
        }
        result = analyze(protocol(), blocks)
        self.assertTrue(result["decision"]["expand_to_full102"])
        self.assertAlmostEqual(
            result["mahalanobis_pp_vs_mahalanobis_four_metric_mean_gain"], 0.1
        )

    def test_suite_regressions_close_expansion_gate(self) -> None:
        blocks = {}
        for position, suite in enumerate(SUITES):
            candidate = 0.8 if position < 4 else 0.6
            for index in (1, 2):
                blocks[f"{suite}/scenario_{index}"] = {
                    "mahalanobis_pp": report(candidate),
                    "mlp_mahalanobis": report(0.7),
                    "opendetect": report(0.75),
                }
        result = analyze(protocol(), blocks)
        self.assertFalse(result["expansion_checks"]["suite_robustness"])
        self.assertFalse(result["decision"]["expand_to_full102"])


if __name__ == "__main__":
    unittest.main()
