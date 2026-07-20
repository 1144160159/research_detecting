from __future__ import annotations

import unittest

from confirm_strict_v4_tail_aware import confirmation_decision
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_tail_aware_confirmation_protocol import create_protocol
from create_strict_v4_tail_aware_pilot_protocol import create_protocol as create_pilot


def raw_fusion() -> dict:
    runs = []
    for suite_index in range(7):
        suite = f"suite_{suite_index}"
        for scenario_index in range(15 if suite_index < 4 else 14):
            runs.append(
                {
                    "suite": suite,
                    "task": f"attack_{scenario_index}_seed7",
                    "gate_report": {
                        "unknown_auroc": 1.0 - scenario_index / 100.0,
                        "unknown_aupr": 1.0 - scenario_index / 90.0,
                        "unknown_fpr95": scenario_index / 20.0,
                        "oscr": 1.0 - scenario_index / 80.0,
                    },
                    "audit": {
                        "split_fingerprints_identical": True,
                        "caeos_unknown_or_test_labels_used_for_selection": False,
                    },
                }
            )
    return {"runs": runs}


class StrictV4TailAwareConfirmationTests(unittest.TestCase):
    def protocol(self) -> dict:
        coverage = {
            "schema_version": "strict_v4_coverage_manifest_v2",
            "datasets": 7,
            "scenario_registry": {
                f"suite_{suite}": {
                    "scenarios": [
                        f"attack_{index}"
                        for index in range(15 if suite < 4 else 14)
                    ]
                }
                for suite in range(7)
            },
        }
        coverage["manifest_sha256"] = canonical_hash(coverage)
        pilot = create_pilot(
            raw_fusion(),
            raw_fusion_sha256="raw",
            implementation_sha256={"implementation": "sha"},
        )
        analysis = {
            "schema_version": "strict_v4_tail_aware_pilot_analysis_v1",
            "passes": True,
            "decision": "freeze_for_new_seed_confirmation",
            "protocol_manifest_sha256": pilot["manifest_sha256"],
        }
        return create_protocol(
            coverage,
            pilot,
            analysis,
            coverage_sha256="coverage-file",
            pilot_protocol_sha256="pilot-file",
            pilot_analysis_sha256="analysis-file",
            implementation_sha256={"implementation": "sha"},
        )

    def test_protocol_freezes_full_new_seed_scope(self) -> None:
        protocol = self.protocol()
        self.assertEqual(protocol["confirmation"]["seeds"], [157, 163, 167])
        self.assertEqual(protocol["confirmation"]["expected_scenario_count"], 102)
        self.assertEqual(protocol["confirmation"]["expected_run_count"], 306)
        self.assertEqual(protocol["candidate"]["runtime_minimum_fold_gain"], -1.0)
        self.assertEqual(protocol["manifest_sha256"], canonical_hash(protocol))

    def test_confirmation_gate_requires_every_metric_and_suite(self) -> None:
        metric = {
            "oriented_mean_improvement": 0.1,
            "bootstrap_95_ci": {"lower": 0.01},
            "wilcoxon": {"holm_adjusted_p_value": 0.01},
        }
        inference = {
            "metrics": {
                "known_macro_f1": {"raw_mean_delta": 0.0},
                **{
                    name: dict(metric)
                    for name in ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
                },
            }
        }
        gains = {
            "suite": {
                name: 0.01
                for name in ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
            }
        }
        self.assertTrue(confirmation_decision(inference, gains, 1)["passes"])
        gains["suite"]["unknown_aupr"] = -0.001
        self.assertFalse(confirmation_decision(inference, gains, 1)["passes"])


if __name__ == "__main__":
    unittest.main()
