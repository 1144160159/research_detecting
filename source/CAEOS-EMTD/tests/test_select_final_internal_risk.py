from __future__ import annotations

import unittest
from pathlib import Path

from select_final_internal_risk import (
    ENTROPY,
    FUSION,
    REFERENCE,
    build_selection,
    validate_manifest,
)


METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
    "known_acceptance_rate",
    "unknown_rejection_rate",
)


def report(value: float, fpr95: float) -> dict[str, float]:
    result = {metric: value for metric in METRICS}
    result["unknown_fpr95"] = fpr95
    return result


def confirmation(schema: str, candidate: str, reference: str, passes: bool) -> dict[str, object]:
    reference_report = report(0.5, 0.5)
    if reference == ENTROPY:
        reference_report = report(0.6, 0.4)
    candidate_report = report(0.6 if candidate == ENTROPY else 0.7, 0.4 if candidate == ENTROPY else 0.3)
    rows = []
    scenarios = tuple(f"scenario_{index}" for index in range(14))
    for scenario in scenarios:
        for seed in (67, 71):
            rows.append(
                {
                    "suite": "edge_iiot",
                    "scenario": scenario,
                    "seed": seed,
                    "candidate_selected": candidate,
                    "reference_selected": reference,
                    "candidate_report": candidate_report,
                    "reference_report": reference_report,
                    "split_fingerprint": f"{scenario}:{seed}",
                }
            )
    return {
        "schema_version": schema,
        "candidate_status_before_confirmation": "frozen_unconfirmed",
        "confirmation_status": "confirmed" if passes else "not_confirmed",
        "validation": {
            "paired_tasks": 28,
            "expected_seeds": [67, 71],
            "expected_scenarios": 14,
            "task_sets_identical": True,
            "split_fingerprints_identical": True,
            "candidate_selection_uses_unknown_or_test_labels": False,
            "candidate_was_frozen_before_confirmation": True,
        },
        "scenario_blocked_inference": {
            "decision": {"confirmatory_evidence_passes": passes}
        },
        "runs": rows,
    }


def manifest() -> dict[str, object]:
    return {
        "scope": {"scenario_count": 14, "confirmation_seeds": [67, 71]},
        "external_expert_fusion_role": "separate",
    }


class FinalInternalRiskSelectionTests(unittest.TestCase):
    def test_frozen_decision_manifest_hash_is_valid(self) -> None:
        frozen = validate_manifest(
            Path("selection/final_internal_risk_decision_manifest.json")
        )
        self.assertEqual("frozen_unconfirmed", frozen["status"])

    def test_rank_union_is_selected_when_all_gates_pass(self) -> None:
        entropy = confirmation("fixed_report_candidate_confirmation_v1", ENTROPY, REFERENCE, True)
        fusion = confirmation("entropy_cauchy_fusion_confirmation_v1", FUSION, ENTROPY, True)
        result = build_selection(entropy, fusion, manifest(), 500, 7)
        self.assertEqual(FUSION, result["selected_internal_risk"])
        self.assertTrue(result["decision_trace"]["rank_union_vs_reference_passes"])

    def test_entropy_and_reference_fallbacks_are_fixed(self) -> None:
        entropy = confirmation("fixed_report_candidate_confirmation_v1", ENTROPY, REFERENCE, True)
        fusion = confirmation("entropy_cauchy_fusion_confirmation_v1", FUSION, ENTROPY, False)
        result = build_selection(entropy, fusion, manifest(), 500, 7)
        self.assertEqual(ENTROPY, result["selected_internal_risk"])
        entropy["confirmation_status"] = "not_confirmed"
        entropy["scenario_blocked_inference"]["decision"]["confirmatory_evidence_passes"] = False
        result = build_selection(entropy, fusion, manifest(), 500, 7)
        self.assertEqual(REFERENCE, result["selected_internal_risk"])

    def test_mismatched_replay_is_rejected(self) -> None:
        entropy = confirmation("fixed_report_candidate_confirmation_v1", ENTROPY, REFERENCE, True)
        fusion = confirmation("entropy_cauchy_fusion_confirmation_v1", FUSION, ENTROPY, True)
        fusion["runs"][0]["reference_report"]["unknown_auroc"] = 0.1
        with self.assertRaisesRegex(ValueError, "entropy replay mismatch"):
            build_selection(entropy, fusion, manifest(), 500, 7)


if __name__ == "__main__":
    unittest.main()
