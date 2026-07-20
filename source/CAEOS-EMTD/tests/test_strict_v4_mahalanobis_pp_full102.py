import unittest

from summarize_strict_v4_mahalanobis_pp_full102 import merge_and_decide


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


class StrictV4MahalanobisPlusPlusFull102Tests(unittest.TestCase):
    def existing(self) -> dict[str, object]:
        rows = [row("caeos_pairwise", 0.8), row("opendetect", 0.7)]
        return {"overall": rows, "by_suite": {"edge": rows}}

    def test_strong_mahalanobis_pp_invalidates_opendetect_only_protocol(self) -> None:
        blocks = {
            "edge/a": {"mahalanobis_pp": report(0.9)},
            "edge/b": {"mahalanobis_pp": report(0.9)},
        }
        overall, _, decision = merge_and_decide(self.existing(), blocks)
        self.assertEqual(len(overall), 3)
        self.assertEqual(decision["selected_comparator"], "mahalanobis_pp")
        self.assertFalse(decision["existing_opendetect_protocol_remains_valid"])

    def test_weak_mahalanobis_pp_retains_opendetect(self) -> None:
        blocks = {
            "edge/a": {"mahalanobis_pp": report(0.6)},
            "edge/b": {"mahalanobis_pp": report(0.6)},
        }
        _, _, decision = merge_and_decide(self.existing(), blocks)
        self.assertEqual(decision["selected_comparator"], "opendetect")
        self.assertTrue(decision["existing_opendetect_protocol_remains_valid"])


if __name__ == "__main__":
    unittest.main()
