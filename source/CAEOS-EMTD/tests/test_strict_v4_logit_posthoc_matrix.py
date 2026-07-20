import unittest

from run_strict_v4_logit_posthoc_matrix import select_pilot_scenarios, without_suffix


class StrictV4LogitPosthocMatrixTests(unittest.TestCase):
    def test_pilot_selection_is_deterministic_and_two_per_suite(self) -> None:
        coverage = {
            "schema_version": "strict_v4_coverage_manifest_v2",
            "manifest_sha256": "a" * 64,
            "scenario_registry": {
                f"suite_{index}": {
                    "count": 4,
                    "scenarios": ["a", "b", "c", "d"],
                }
                for index in range(7)
            },
        }
        first = select_pilot_scenarios(coverage)
        second = select_pilot_scenarios(coverage)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 7)
        self.assertTrue(all(len(set(items)) == 2 for items in first.values()))

    def test_suffix_removal_fails_closed(self) -> None:
        self.assertEqual(without_suffix("run_mlp", "_mlp"), "run")
        with self.assertRaises(ValueError):
            without_suffix("run", "_mlp")


if __name__ == "__main__":
    unittest.main()
