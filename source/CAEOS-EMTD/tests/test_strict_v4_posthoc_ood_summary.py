import unittest

from summarize_strict_v4_posthoc_ood import merged_tables


def row(method: str, value: float) -> dict[str, object]:
    return {
        "method": method,
        "known_macro_f1": value,
        "unknown_auroc": value,
        "unknown_aupr": value,
        "unknown_fpr95": 1.0 - value,
        "oscr": value,
        "metric_ranks": {},
        "mean_unknown_metric_rank": 0.0,
    }


def report(value: float) -> dict[str, float]:
    return {
        "known_macro_f1": value,
        "unknown_auroc": value,
        "unknown_aupr": value,
        "unknown_fpr95": 1.0 - value,
        "oscr": value,
    }


class StrictV4PosthocOODSummaryTests(unittest.TestCase):
    def test_merged_tables_rerank_existing_and_posthoc_methods(self) -> None:
        existing = {
            "overall": [row("opendetect", 0.7), row("caeos_pairwise", 0.8)],
            "by_suite": {
                "edge": [row("opendetect", 0.7), row("caeos_pairwise", 0.8)]
            },
        }
        blocks = {
            "edge/a": {
                "react_energy": report(0.6),
                "dice": report(0.9),
                "she": report(0.5),
            },
            "edge/b": {
                "react_energy": report(0.6),
                "dice": report(0.9),
                "she": report(0.5),
            },
        }
        overall, by_suite = merged_tables(existing, blocks)
        self.assertEqual(overall[0]["method"], "dice")
        self.assertEqual(by_suite["edge"][0]["method"], "dice")
        self.assertEqual(len(overall), 5)


if __name__ == "__main__":
    unittest.main()
