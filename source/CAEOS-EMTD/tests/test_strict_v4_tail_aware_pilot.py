from __future__ import annotations

import copy
import unittest

from analyze_strict_v4_tail_aware_pilot import analyze
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_tail_aware_pilot_protocol import create_protocol


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


def metrics(gain: float = 0.05, selected: bool = True) -> dict:
    reference = {
        "known_macro_f1": 0.8,
        "unknown_auroc": 0.7,
        "unknown_aupr": 0.6,
        "unknown_fpr95": 0.5,
        "oscr": 0.65,
    }
    candidate = {
        **reference,
        "unknown_auroc": reference["unknown_auroc"] + gain,
        "unknown_aupr": reference["unknown_aupr"] + gain,
        "unknown_fpr95": reference["unknown_fpr95"] - gain,
        "oscr": reference["oscr"] + gain,
    }
    return {
        "arguments": {
            "risk_selection": "nested_tail_aware_pairwise_pseudo_unknown_blend"
        },
        "selected_risk": (
            "pseudo_unknown_tail_aware_blend"
            if selected
            else "cauchy_modality_support_union"
        ),
        "risk_selection_details": {
            "unknown_or_test_labels_used_for_selection": False,
            "pseudo_unknown_learned_blend": {
                "schema_version": "tail_aware_pairwise_ranking_head_v1",
                "unknown_or_test_labels_used": False,
            },
        },
        "reports": {
            "cauchy_modality_support_union": reference,
            "pseudo_unknown_tail_aware_blend": candidate,
        },
        "split_metadata": {"split_fingerprint": "same"},
    }


class StrictV4TailAwarePilotTests(unittest.TestCase):
    def protocol(self) -> dict:
        return create_protocol(
            raw_fusion(),
            raw_fusion_sha256="raw",
            implementation_sha256={"implementation": "sha"},
        )

    def test_protocol_freezes_two_hard_scenes_per_suite(self) -> None:
        protocol = self.protocol()
        self.assertEqual(protocol["pilot"]["expected_run_count"], 14)
        self.assertEqual(len(protocol["pilot"]["scenarios"]), 7)
        self.assertEqual(protocol["reserved_confirmation"]["seeds"], [157, 163, 167])
        self.assertEqual(protocol["manifest_sha256"], canonical_hash(protocol))

    def test_positive_pilot_freezes_candidate(self) -> None:
        protocol = self.protocol()
        rows = []
        for suite, scenarios in protocol["pilot"]["scenarios"].items():
            for scenario in scenarios:
                rows.append(
                    {"suite": suite, "scenario": scenario, "seed": 7, "metrics": metrics()}
                )
        result = analyze(protocol, rows)
        self.assertTrue(result["passes"])
        self.assertEqual(result["decision"], "freeze_for_new_seed_confirmation")

    def test_runtime_leakage_fails_closed(self) -> None:
        protocol = self.protocol()
        rows = []
        for suite, scenarios in protocol["pilot"]["scenarios"].items():
            for scenario in scenarios:
                rows.append(
                    {"suite": suite, "scenario": scenario, "seed": 7, "metrics": metrics()}
                )
        rows[0] = copy.deepcopy(rows[0])
        rows[0]["metrics"]["risk_selection_details"][
            "unknown_or_test_labels_used_for_selection"
        ] = True
        with self.assertRaisesRegex(ValueError, "leakage"):
            analyze(protocol, rows)


if __name__ == "__main__":
    unittest.main()
