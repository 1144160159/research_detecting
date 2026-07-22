from __future__ import annotations

import unittest

from analyze_strict_v4_lcb_tail_aware_pilot import analyze
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_lcb_tail_aware_pilot_protocol import create_protocol


METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")


def source_protocol() -> dict:
    scenarios = {f"suite_{index}": ["hard_a", "hard_b"] for index in range(7)}
    payload = {
        "schema_version": "strict_v4_tail_aware_pilot_protocol_v1",
        "pilot": {"scenarios": scenarios},
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


def row(suite: str, scenario: str, gain: float = 0.02) -> dict:
    reference = {
        "known_macro_f1": 0.8,
        "unknown_auroc": 0.6,
        "unknown_aupr": 0.5,
        "unknown_fpr95": 0.5,
        "oscr": 0.5,
    }
    candidate = {
        "known_macro_f1": 0.8,
        "unknown_auroc": 0.6 + gain,
        "unknown_aupr": 0.5 + gain,
        "unknown_fpr95": 0.5 - gain,
        "oscr": 0.5 + gain,
    }
    learned = {
        "schema_version": "tail_aware_lcb_pairwise_ranking_head_v1",
        "unknown_or_test_labels_used": False,
        "training_objective": "tail_weighted_monotone_pairwise",
        "confidence_z": 1.645,
        "minimum_metric_lcb_gain": 0.0,
        "minimum_aupr_lcb_gain": 0.0,
        "minimum_aupr_fold_gain": -0.05,
        "passes": True,
        "selected_alpha": 0.5,
        "development_selected_alpha": 0.5,
        "gate_checks": {
            "all_metric_means_above_minimum": True,
            "all_metric_lcbs_above_minimum": True,
            "aupr_lcb_above_minimum": True,
            "aupr_worst_fold_above_minimum": True,
        },
    }
    return {
        "suite": suite,
        "scenario": scenario,
        "seed": 191,
        "metrics": {
            "arguments": {
                "risk_selection": "nested_lcb_tail_aware_pairwise_pseudo_unknown_blend",
                "risk_policy_name": "strict_v4_lcb_tail_aware_pilot_seed191_v1",
                "pseudo_unknown_max_alpha": 0.5,
                "pseudo_unknown_min_fold_gain": -0.05,
                "boundary_hard_pseudo_fraction": 0.5,
                "boundary_interpolation": 0.5,
                "boundary_max_per_task": 512,
                "tail_aware_confidence_z": 1.645,
                "tail_aware_min_metric_lcb_gain": 0.0,
                "tail_aware_min_aupr_lcb_gain": 0.0,
                "tail_aware_min_aupr_fold_gain": -0.05,
            },
            "risk_selection_details": {
                "unknown_or_test_labels_used_for_selection": False,
                "pseudo_unknown_learned_blend": learned,
                "pseudo_unknown_robust_fold_gate": {
                    "passes": True,
                    "mean_gain_gate_passes": True,
                    "fold_stability_gate_passes": True,
                    "minimum_fold_metric_gain": 0.01,
                    "required_minimum_fold_gain": -0.05,
                },
                "pseudo_unknown_gate_passes": True,
            },
            "reports": {
                "pseudo_unknown_tail_aware_blend": candidate,
                "cauchy_modality_support_union": reference,
            },
            "selected_risk": "pseudo_unknown_tail_aware_blend",
            "split_metadata": {
                "split_fingerprint": f"{suite}-{scenario}-191"
            },
        },
    }


class LcbTailAwareProtocolTests(unittest.TestCase):
    def protocol(self) -> dict:
        return create_protocol(
            source_protocol(),
            source_file_sha256="source",
            implementation_sha256={"implementation": "sha"},
        )

    def test_protocol_freezes_disjoint_pilot_and_confirmation(self) -> None:
        protocol = self.protocol()
        self.assertEqual(protocol["pilot"]["development_seed"], 191)
        self.assertEqual(protocol["reserved_confirmation"]["seeds"], [197, 199, 211])
        self.assertEqual(protocol["pilot"]["expected_run_count"], 14)
        self.assertEqual(protocol["manifest_sha256"], canonical_hash(protocol))

    def test_analysis_passes_complete_positive_matrix(self) -> None:
        protocol = self.protocol()
        rows = [
            row(suite, scenario)
            for suite, scenarios in protocol["pilot"]["scenarios"].items()
            for scenario in scenarios
        ]
        result = analyze(protocol, rows)
        self.assertTrue(result["passes"])
        self.assertEqual(result["candidate_endpoint_selected_count"], 14)
        self.assertFalse(
            result["validation"]["unknown_or_test_labels_used_for_runtime_selection"]
        )

    def test_analysis_rejects_suite_regression(self) -> None:
        protocol = self.protocol()
        rows = [
            row(suite, scenario)
            for suite, scenarios in protocol["pilot"]["scenarios"].items()
            for scenario in scenarios
        ]
        rows[0] = row(rows[0]["suite"], rows[0]["scenario"], gain=-0.04)
        result = analyze(protocol, rows)
        self.assertFalse(result["passes"])
        self.assertFalse(result["checks"]["minimum_suite_metric_gain"])

    def test_analysis_rejects_runtime_parameter_drift(self) -> None:
        protocol = self.protocol()
        rows = [
            row(suite, scenario)
            for suite, scenarios in protocol["pilot"]["scenarios"].items()
            for scenario in scenarios
        ]
        rows[0]["metrics"]["arguments"]["pseudo_unknown_max_alpha"] = 0.75
        with self.assertRaisesRegex(ValueError, "frozen argument mismatch"):
            analyze(protocol, rows)

    def test_analysis_rejects_endpoint_gate_inconsistency(self) -> None:
        protocol = self.protocol()
        rows = [
            row(suite, scenario)
            for suite, scenarios in protocol["pilot"]["scenarios"].items()
            for scenario in scenarios
        ]
        rows[0]["metrics"]["selected_risk"] = "cauchy_modality_support_union"
        with self.assertRaisesRegex(ValueError, "selected endpoint"):
            analyze(protocol, rows)


if __name__ == "__main__":
    unittest.main()
