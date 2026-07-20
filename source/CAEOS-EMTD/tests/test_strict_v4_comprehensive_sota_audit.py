from __future__ import annotations

import unittest

from audit_strict_v4_comprehensive_sota import audit
from create_strict_v4_external_confirmation_protocol import canonical_hash


def inputs():
    summary = {
        "schema_version": "strict_v4_full103_coverage_summary_v1",
        "validation": {
            "passes": True,
            "scenario_count": 102,
            "dataset_count": 7,
            "method_count": 22,
            "independent_baseline_run_checks": 204,
            "split_fingerprints_identical": True,
        },
        "overall": [
            {
                "method": "caeos_domain_safe_router",
                "known_macro_f1": 0.8,
                "unknown_auroc": 0.9,
                "unknown_aupr": 0.8,
                "unknown_fpr95": 0.2,
                "oscr": 0.85,
            },
            {
                "method": "opendetect",
                "known_macro_f1": 0.7,
                "unknown_auroc": 0.8,
                "unknown_aupr": 0.7,
                "unknown_fpr95": 0.3,
                "oscr": 0.75,
            },
        ],
    }
    tournament = {
        "schema_version": "strict_v4_self_algorithm_tournament_protocol_v1",
        "external_confirmation_branch": {
            "incumbent_wins": {"seeds": [137, 139, 149]},
            "tail_challenger_wins": {"fresh_seeds": [173, 179, 181]},
        },
    }
    tournament["manifest_sha256"] = canonical_hash(tournament)
    posthoc_overall = list(summary["overall"])
    for index in range(23):
        method = ("react_energy", "dice", "she")[index] if index < 3 else "extra_%02d" % index
        posthoc_overall.append(
            {
                "method": method,
                "known_macro_f1": 0.6,
                "unknown_auroc": 0.6,
                "unknown_aupr": 0.5,
                "unknown_fpr95": 0.5,
                "oscr": 0.5,
            }
        )
    full_summary_sha256 = "synthetic-full-summary-sha256"
    posthoc = {
        "schema_version": "strict_v4_posthoc_ood_25method_screen_v1",
        "status": "complete",
        "method_count": 25,
        "added_methods": ["react_energy", "dice", "she"],
        "overall": posthoc_overall,
        "validation": {
            "passes": True,
            "scenario_count": 102,
            "method_count": 3,
            "report_count": 306,
            "artifact_checks": 306,
            "split_fingerprints_identical": True,
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
        },
        "comparator_decision": {
            "selected_comparator": "opendetect",
            "existing_opendetect_protocol_remains_valid": True,
        },
        "existing_summary_sha256": full_summary_sha256,
    }
    posthoc_summary_sha256 = "synthetic-posthoc-summary-sha256"
    extended = {
        "schema_version": "strict_v4_sirc_residual_26method_screen_v1",
        "status": "complete",
        "method_count": 26,
        "added_method": "sirc_msp_residual",
        "overall": posthoc_overall
        + [
            {
                "method": "sirc_msp_residual",
                "known_macro_f1": 0.65,
                "unknown_auroc": 0.65,
                "unknown_aupr": 0.55,
                "unknown_fpr95": 0.48,
                "oscr": 0.55,
            }
        ],
        "validation": {
            "passes": True,
            "scenario_count": 102,
            "report_count": 102,
            "failure_count": 0,
            "split_fingerprint_pair_checks": 102,
            "source_provenance_checks": 102,
            "no_leak_checks": 102,
            "expanded_method": "sirc_msp_residual",
            "incidental_method_excluded_from_26method_table": "sirc_msp_l1",
        },
        "comparator_decision": {
            "selected_comparator": "opendetect",
            "comparator_changed": False,
        },
        "full_protocol_manifest_sha256": "a" * 64,
        "pilot_expansion_gate_manifest_sha256": "b" * 64,
        "pilot_analysis_sha256": "c" * 64,
        "existing_25method_summary_sha256": posthoc_summary_sha256,
    }
    extended_summary_sha256 = "synthetic-extended-summary-sha256"
    mandatory = {
        "schema_version": "strict_v4_mandatory_scores_28method_screen_v1",
        "status": "complete",
        "method_count": 28,
        "added_methods": ["shannon_entropy", "prototype_distance"],
        "overall": extended["overall"]
        + [
            {
                "method": "shannon_entropy",
                "known_macro_f1": 0.6,
                "unknown_auroc": 0.61,
                "unknown_aupr": 0.51,
                "unknown_fpr95": 0.49,
                "oscr": 0.51,
            },
            {
                "method": "prototype_distance",
                "known_macro_f1": 0.6,
                "unknown_auroc": 0.62,
                "unknown_aupr": 0.52,
                "unknown_fpr95": 0.48,
                "oscr": 0.52,
            },
        ],
        "validation": {
            "passes": True,
            "scenario_count": 102,
            "report_count": 204,
            "failure_count": 0,
            "split_fingerprint_pair_checks": 102,
            "source_provenance_checks": 102,
            "no_leak_checks": 102,
            "nondegenerate_score_checks": 102,
        },
        "comparator_decision": {
            "selected_comparator": "opendetect",
            "previous_comparator": "opendetect",
            "comparator_changed": False,
        },
        "protocol_manifest_sha256": "d" * 64,
        "existing_26method_summary_sha256": extended_summary_sha256,
    }
    mandatory_summary_sha256 = "synthetic-mandatory-summary-sha256"
    mahalanobis_summary = {
        "schema_version": "strict_v4_mahalanobis_pp_29method_screen_v1",
        "status": "complete",
        "method_count": 29,
        "added_methods": ["mahalanobis_pp"],
        "overall": mandatory["overall"]
        + [
            {
                "method": "mahalanobis_pp",
                "known_macro_f1": 0.66,
                "unknown_auroc": 0.72,
                "unknown_aupr": 0.62,
                "unknown_fpr95": 0.42,
                "oscr": 0.62,
            }
        ],
        "validation": {
            "passes": True,
            "scenario_count": 102,
            "artifact_checks": 612,
            "split_fingerprint_checks": 102,
            "failure_count": 0,
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
        },
        "comparator_decision": {
            "selected_comparator": "opendetect",
            "existing_opendetect_protocol_remains_valid": True,
        },
        "protocol_manifest_sha256": "9" * 64,
        "existing_28method_summary_sha256": mandatory_summary_sha256,
    }
    mahalanobis_summary_sha256 = "synthetic-mahalanobis-summary-sha256"
    excel_summary = {
        "schema_version": "strict_v4_excel_30method_screen_v1",
        "status": "complete",
        "method_count": 30,
        "added_methods": ["excel"],
        "overall": mahalanobis_summary["overall"]
        + [
            {
                "method": "excel",
                "known_macro_f1": 0.66,
                "unknown_auroc": 0.71,
                "unknown_aupr": 0.61,
                "unknown_fpr95": 0.43,
                "oscr": 0.61,
            }
        ],
        "validation": {
            "passes": True,
            "scenario_count": 102,
            "artifact_checks": 612,
            "split_fingerprint_checks": 102,
            "failure_count": 0,
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
        },
        "comparator_decision": {
            "selected_comparator": "opendetect",
            "existing_opendetect_protocol_remains_valid": True,
        },
        "protocol_manifest_sha256": "8" * 64,
        "existing_29method_summary_sha256": mahalanobis_summary_sha256,
    }
    doc_protocol = {
        "schema_version": "strict_v4_mlp_doc_fixed_protocol_v1",
        "mode": "pilot",
        "expected_runs": 14,
        "fit_data": "known_training_embeddings_and_labels_only",
        "ood_parameter_sweep": False,
        "alpha": 3.0,
        "minimum_class_threshold": 0.5,
    }
    doc_protocol["manifest_sha256"] = canonical_hash(doc_protocol)
    doc_gate = {
        "schema_version": "strict_v4_mlp_doc_fixed_expansion_gate_v1",
        "pilot_metrics_observed_at_freeze": 0,
        "pilot_protocol_manifest_sha256": doc_protocol["manifest_sha256"],
    }
    doc_gate["manifest_sha256"] = canonical_hash(doc_gate)
    doc_analysis = {
        "schema_version": "strict_v4_mlp_doc_fixed_pilot_analysis_v1",
        "pilot_protocol_manifest_sha256": doc_protocol["manifest_sha256"],
        "expansion_gate_manifest_sha256": doc_gate["manifest_sha256"],
        "validation": {
            "passes": True,
            "scenario_count": 14,
            "failure_count": 0,
            "split_fingerprint_checks": 14,
            "no_leak_checks": 14,
            "optimization_checks": 14,
            "threshold_range_checks": 14,
        },
        "overall": [
            {"method": "opendetect", "mean_unknown_metric_rank": 1.0},
            {"method": "mlp_energy", "mean_unknown_metric_rank": 2.0},
            {"method": "mlp_msp", "mean_unknown_metric_rank": 3.25},
            {"method": "doc_fixed", "mean_unknown_metric_rank": 3.75},
        ],
        "expansion_checks": {
            "pilot_runs_complete": True,
            "split_integrity": True,
            "known_f1_tolerance": True,
            "optimization_integrity": True,
            "nondegenerate_score": True,
            "top_two_rank": False,
            "metric_breadth": False,
            "overall_gain": False,
            "suite_robustness": False,
        },
        "decision": {"expand_doc_fixed_to_full102": False},
    }
    training_protocol = {
        "schema_version": "strict_v4_external_training_pilot_protocol_v1",
        "status": "frozen_before_pilot_results",
        "coverage_manifest_sha256": "e" * 64,
        "seed": 7,
        "methods": ["closr", "cade", "sieve"],
        "expected_scenarios": 14,
        "expected_runs": 42,
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
        "pilot_metrics_observed_at_freeze": 0,
    }
    training_protocol["manifest_sha256"] = canonical_hash(training_protocol)
    training_gate = {
        "schema_version": "strict_v4_external_training_pilot_expansion_gate_v1",
        "pilot_protocol_manifest_sha256": training_protocol["manifest_sha256"],
        "pilot_metrics_observed_at_freeze": 0,
        "candidates": ["closr", "cade", "sieve"],
    }
    training_gate["manifest_sha256"] = canonical_hash(training_gate)
    negative_checks = {
        "pilot_runs_complete": True,
        "split_and_leakage_integrity": True,
        "known_f1_tolerance": True,
        "top_two_rank": False,
        "metric_breadth": False,
        "overall_gain": False,
        "suite_robustness": False,
    }
    training_analysis = {
        "schema_version": "strict_v4_external_training_pilot_analysis_v1",
        "status": "complete",
        "pilot_protocol_manifest_sha256": training_protocol["manifest_sha256"],
        "expansion_gate_manifest_sha256": training_gate["manifest_sha256"],
        "candidate_decisions": {
            method: {"checks": dict(negative_checks), "expand_to_full102": False}
            for method in ("closr", "cade", "sieve")
        },
        "expand_to_full102": [],
        "validation": {
            "passes": True,
            "scenario_count": 14,
            "method_run_count": 42,
            "failure_count": 0,
            "split_fingerprint_checks": 14,
            "no_leak_checks": 14,
        },
    }
    complementary_protocol = {
        "schema_version": "strict_v4_complementary_training_pilot_protocol_v1",
        "status": "frozen_before_pilot_results",
        "coverage_manifest_sha256": "f" * 64,
        "seed": 7,
        "methods": ["arpl", "palm", "ronetc", "foss"],
        "expected_scenarios": 14,
        "expected_runs": 56,
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
        "pilot_metrics_observed_at_freeze": 0,
    }
    complementary_protocol["manifest_sha256"] = canonical_hash(
        complementary_protocol
    )
    complementary_gate = {
        "schema_version": "strict_v4_complementary_training_pilot_expansion_gate_v1",
        "pilot_protocol_manifest_sha256": complementary_protocol["manifest_sha256"],
        "pilot_metrics_observed_at_freeze": 0,
        "candidates": ["arpl", "palm", "ronetc", "foss"],
    }
    complementary_gate["manifest_sha256"] = canonical_hash(complementary_gate)
    complementary_analysis = {
        "schema_version": "strict_v4_complementary_training_pilot_analysis_v1",
        "status": "complete",
        "pilot_protocol_manifest_sha256": complementary_protocol["manifest_sha256"],
        "expansion_gate_manifest_sha256": complementary_gate["manifest_sha256"],
        "candidate_decisions": {
            method: {"checks": dict(negative_checks), "expand_to_full102": False}
            for method in ("arpl", "palm", "ronetc", "foss")
        },
        "expand_to_full102": [],
        "validation": {
            "passes": True,
            "scenario_count": 14,
            "method_run_count": 56,
            "failure_count": 0,
            "split_fingerprint_checks": 14,
            "no_leak_checks": 14,
        },
    }
    aegis_protocol = {
        "schema_version": "strict_v4_aegis_training_pilot_protocol_v1",
        "status": "frozen_before_pilot_results",
        "coverage_manifest_sha256": "1" * 64,
        "seed": 7,
        "methods": ["aegis_clean_adapter"],
        "expected_scenarios": 14,
        "expected_runs": 14,
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
        "smoke_evidence": {"status": "pass"},
        "pilot_metrics_observed_at_freeze": 0,
    }
    aegis_protocol["manifest_sha256"] = canonical_hash(aegis_protocol)
    aegis_gate = {
        "schema_version": "strict_v4_aegis_training_pilot_expansion_gate_v1",
        "pilot_protocol_manifest_sha256": aegis_protocol["manifest_sha256"],
        "pilot_metrics_observed_at_freeze": 0,
        "candidates": ["aegis_clean_adapter"],
    }
    aegis_gate["manifest_sha256"] = canonical_hash(aegis_gate)
    aegis_analysis = {
        "schema_version": "strict_v4_aegis_training_pilot_analysis_v1",
        "status": "complete",
        "pilot_protocol_manifest_sha256": aegis_protocol["manifest_sha256"],
        "expansion_gate_manifest_sha256": aegis_gate["manifest_sha256"],
        "candidate_decisions": {
            "aegis_clean_adapter": {
                "checks": dict(negative_checks),
                "expand_to_full102": False,
            }
        },
        "expand_to_full102": [],
        "validation": {
            "passes": True,
            "scenario_count": 14,
            "method_run_count": 14,
            "failure_count": 0,
            "split_fingerprint_checks": 14,
            "no_leak_checks": 14,
        },
    }
    final = {
        "schema_version": "strict_v4_optimal_self_algorithm_decision_v1",
        "tournament_protocol_manifest_sha256": tournament["manifest_sha256"],
        "incumbent_algorithm": "caeos_domain_safe_router",
        "selected_algorithm": "caeos_domain_safe_router",
        "tail_challenger_confirmation_passes": False,
        "tail_vs_incumbent_replacement_gate_passes": False,
        "external_confirmation_seeds": [137, 139, 149],
    }
    final["manifest_sha256"] = canonical_hash(final)
    router = {
        "schema_version": "strict_v4_domain_safe_router_confirmation_v1",
        "decision": {"passes": True},
    }
    external = {
        "schema_version": "strict_v4_external_comparator_confirmation_v1",
        "selected_algorithm": "caeos_domain_safe_router",
        "candidate_validation": {"seeds": [137, 139, 149]},
        "decision": {"passes": True},
    }
    doh = {
        "schema_version": "strict_v4_doh_extension_screen_v1",
        "validation": {"passes": True, "scenario_count": 3},
        "selection_policy": "descriptive_only_no_method_selected_on_doh_test_results",
        "full_sota_claim_allowed": False,
    }
    metrics = (
        "known_macro_f1",
        "unknown_auroc",
        "unknown_aupr",
        "unknown_fpr95",
        "oscr",
        "known_ece",
    )
    attention_protocol = {
        "schema_version": "strict_v4_attention_fusion_protocol_v1",
        "expected_scenarios": 102,
    }
    attention_protocol["manifest_sha256"] = canonical_hash(attention_protocol)
    attention_analysis = {
        "schema_version": "strict_v4_attention_fusion_analysis_v1",
        "status": "complete",
        "protocol_manifest_sha256": attention_protocol["manifest_sha256"],
        "scenario_count": 102,
        "source_integrity_checks": 306,
        "test_truth_isolated_from_evidence_package": True,
        "aggregate": {
            "entropy_conditioned_learnable_attention": {
                metric: {"mean": 0.5} for metric in metrics
            },
            "caeos_reliability_fusion": {
                metric: {"mean": 0.6} for metric in metrics
            },
        },
    }
    fusion_methods = [
        "f2_probability_average",
        "f3_entropy_conditioned_attention",
        "f4_edl_evidence_sum",
        "f5_reliability_gate",
        "f6_standard_ds_fusion",
        "f9_caeos_final_probability",
    ]
    fusion_protocol = {
        "schema_version": "strict_v4_fusion_operator_protocol_v2",
        "methods": fusion_methods,
    }
    fusion_protocol["manifest_sha256"] = canonical_hash(fusion_protocol)
    fusion_analysis = {
        "schema_version": "strict_v4_fusion_operator_analysis_v2",
        "status": "complete",
        "protocol_manifest_sha256": fusion_protocol["manifest_sha256"],
        "scenario_count": 102,
        "source_integrity_checks": 306,
        "test_truth_isolated_from_evidence_package": True,
        "pollution_claim_allowed": False,
        "aggregate": {
            method: {
                metric: {
                    "mean": (
                        0.5
                        if method == "f3_entropy_conditioned_attention"
                        else 0.6 if method == "f5_reliability_gate" else 0.7
                    )
                }
                for metric in metrics
            }
            for method in fusion_methods
        },
    }
    return (
        summary,
        posthoc,
        extended,
        mandatory,
        doc_protocol,
        doc_gate,
        doc_analysis,
        training_protocol,
        training_gate,
        training_analysis,
        complementary_protocol,
        complementary_gate,
        complementary_analysis,
        aegis_protocol,
        aegis_gate,
        aegis_analysis,
        final,
        router,
        external,
        doh,
        tournament,
        full_summary_sha256,
        posthoc_summary_sha256,
        extended_summary_sha256,
        fusion_protocol,
        fusion_analysis,
        attention_protocol,
        attention_analysis,
        mahalanobis_summary,
        mandatory_summary_sha256,
        excel_summary,
        mahalanobis_summary_sha256,
    )


def full102_expansion(group, pilot_protocol, pilot_analysis, methods):
    protocol = {
        "schema_version": "strict_v4_training_full102_expansion_protocol_v1",
        "status": "frozen_before_full102_results",
        "group": group,
        "pilot_protocol_manifest_sha256": pilot_protocol["manifest_sha256"],
        "pilot_analysis_sha256": canonical_hash(pilot_analysis),
        "methods": list(methods),
        "expected_scenarios": 102,
        "expected_runs": 102 * len(methods),
        "full102_metrics_observed_at_freeze": 0,
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    analysis = {
        "schema_version": "strict_v4_training_full102_expansion_analysis_v1",
        "status": "complete",
        "group": group,
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "methods": list(methods),
        "validation": {
            "passes": True,
            "scenario_count": 102,
            "method_run_count": 102 * len(methods),
            "expected_method_run_count": 102 * len(methods),
            "split_fingerprint_checks": 102,
            "no_leak_checks": 102,
            "failure_count": 0,
        },
    }
    return protocol, analysis


class StrictV4ComprehensiveSotaAuditTests(unittest.TestCase):
    def test_complete_evidence_allows_seven_dataset_claim_only(self) -> None:
        result = audit(*inputs())
        self.assertEqual(result["schema_version"], "strict_v4_comprehensive_sota_audit_v11")
        self.assertTrue(result["strict_v4_confirmed_external_sota_allowed"])
        self.assertFalse(result["eight_dataset_confirmed_sota_allowed"])
        self.assertEqual(
            result["claim_tier"],
            "confirmed_external_sota_7_datasets_102_scenarios",
        )

    def test_external_confirmation_failure_blocks_sota(self) -> None:
        values = list(inputs())
        external = values[18]
        external["decision"]["passes"] = False
        result = audit(*values)
        self.assertFalse(result["strict_v4_confirmed_external_sota_allowed"])

    def test_algorithm_selection_mismatch_fails_closed(self) -> None:
        values = list(inputs())
        router = values[17]
        router["decision"]["passes"] = False
        with self.assertRaisesRegex(ValueError, "contradicts"):
            audit(*values)

    def test_tail_branch_uses_fresh_external_seeds(self) -> None:
        values = list(inputs())
        final, external = values[16], values[18]
        final.update(
            {
                "selected_algorithm": "caeos_tail_aware_pairwise",
                "tail_challenger_confirmation_passes": True,
                "tail_vs_incumbent_replacement_gate_passes": True,
                "external_confirmation_seeds": [173, 179, 181],
            }
        )
        final["manifest_sha256"] = canonical_hash(final)
        external["selected_algorithm"] = "caeos_tail_aware_pairwise"
        external["candidate_validation"]["seeds"] = [173, 179, 181]
        result = audit(*values)
        self.assertTrue(result["strict_v4_confirmed_external_sota_allowed"])

    def test_missing_posthoc_method_blocks_comprehensive_sota(self) -> None:
        values = list(inputs())
        posthoc = values[1]
        posthoc["overall"] = posthoc["overall"][:-1]
        with self.assertRaisesRegex(ValueError, "25-method"):
            audit(*values)

    def test_posthoc_full_summary_sha_mismatch_blocks_comprehensive_sota(self) -> None:
        values = list(inputs())
        posthoc = values[1]
        posthoc["existing_summary_sha256"] = "wrong"
        with self.assertRaisesRegex(ValueError, "25-method"):
            audit(*values)

    def test_missing_sirc_method_blocks_comprehensive_sota(self) -> None:
        values = list(inputs())
        extended = values[2]
        extended["overall"] = extended["overall"][:-1]
        with self.assertRaisesRegex(ValueError, "26-method"):
            audit(*values)

    def test_missing_doc_no_leak_evidence_blocks_comprehensive_sota(self) -> None:
        values = list(inputs())
        doc_analysis = values[6]
        doc_analysis["validation"]["no_leak_checks"] = 13
        with self.assertRaisesRegex(ValueError, "DOC-Fixed"):
            audit(*values)

    def test_missing_mandatory_score_report_blocks_comprehensive_sota(self) -> None:
        values = list(inputs())
        mandatory = values[3]
        mandatory["validation"]["report_count"] = 203
        with self.assertRaisesRegex(ValueError, "28-method"):
            audit(*values)

    def test_missing_mahalanobis_pp_integrity_blocks_comprehensive_sota(self) -> None:
        values = list(inputs())
        mahalanobis = values[28]
        mahalanobis["validation"]["artifact_checks"] = 611
        with self.assertRaisesRegex(ValueError, "29-method Mahalanobis"):
            audit(*values)

    def test_missing_excel_integrity_blocks_comprehensive_sota(self) -> None:
        values = list(inputs())
        excel = values[30]
        excel["validation"]["split_fingerprint_checks"] = 101
        with self.assertRaisesRegex(ValueError, "30-method ExCeL"):
            audit(*values)

    def test_training_pilot_no_leak_evidence_is_required(self) -> None:
        values = list(inputs())
        training_analysis = values[9]
        training_analysis["validation"]["no_leak_checks"] = 13
        with self.assertRaisesRegex(ValueError, "external training baseline"):
            audit(*values)

    def test_training_candidate_requiring_full102_blocks_audit(self) -> None:
        values = list(inputs())
        training_analysis = values[9]
        training_analysis["candidate_decisions"]["closr"]["expand_to_full102"] = True
        training_analysis["expand_to_full102"] = ["closr"]
        with self.assertRaisesRegex(ValueError, "requires full102 expansion"):
            audit(*values)

    def test_complementary_training_pilot_is_required(self) -> None:
        values = list(inputs())
        complementary_analysis = values[12]
        complementary_analysis["validation"]["method_run_count"] = 55
        with self.assertRaisesRegex(ValueError, "complementary training baseline"):
            audit(*values)

    def test_complementary_candidate_requiring_full102_blocks_audit(self) -> None:
        values = list(inputs())
        complementary_analysis = values[12]
        complementary_analysis["candidate_decisions"]["palm"][
            "expand_to_full102"
        ] = True
        complementary_analysis["expand_to_full102"] = ["palm"]
        with self.assertRaisesRegex(ValueError, "requires full102 expansion"):
            audit(*values)

    def test_completed_complementary_full102_resolves_expansion_gate(self) -> None:
        values = list(inputs())
        protocol, analysis = values[10], values[12]
        analysis["candidate_decisions"]["palm"]["expand_to_full102"] = True
        analysis["expand_to_full102"] = ["palm"]
        expansion_protocol, expansion_analysis = full102_expansion(
            "complementary", protocol, analysis, ["palm"]
        )
        result = audit(
            *values,
            complementary_expansion_protocol=expansion_protocol,
            complementary_expansion_analysis=expansion_analysis,
        )
        self.assertTrue(result["strict_v4_confirmed_external_sota_allowed"])

    def test_tampered_complementary_full102_stays_blocked(self) -> None:
        values = list(inputs())
        protocol, analysis = values[10], values[12]
        analysis["candidate_decisions"]["palm"]["expand_to_full102"] = True
        analysis["expand_to_full102"] = ["palm"]
        expansion_protocol, expansion_analysis = full102_expansion(
            "complementary", protocol, analysis, ["palm"]
        )
        expansion_analysis["validation"]["no_leak_checks"] = 101
        with self.assertRaisesRegex(ValueError, "requires full102 expansion"):
            audit(
                *values,
                complementary_expansion_protocol=expansion_protocol,
                complementary_expansion_analysis=expansion_analysis,
            )

    def test_aegis_training_pilot_is_required(self) -> None:
        values = list(inputs())
        aegis_analysis = values[15]
        aegis_analysis["validation"]["no_leak_checks"] = 13
        with self.assertRaisesRegex(ValueError, "AEGIS training baseline"):
            audit(*values)

    def test_aegis_candidate_requiring_full102_blocks_audit(self) -> None:
        values = list(inputs())
        aegis_analysis = values[15]
        aegis_analysis["candidate_decisions"]["aegis_clean_adapter"][
            "expand_to_full102"
        ] = True
        aegis_analysis["expand_to_full102"] = ["aegis_clean_adapter"]
        with self.assertRaisesRegex(ValueError, "requires full102 expansion"):
            audit(*values)

    def test_fusion_operator_cross_analysis_mismatch_blocks_audit(self) -> None:
        values = list(inputs())
        fusion_analysis = values[25]
        fusion_analysis["aggregate"]["f5_reliability_gate"]["unknown_auroc"][
            "mean"
        ] += 0.01
        with self.assertRaisesRegex(ValueError, "fusion operator"):
            audit(*values)

    def test_completed_aegis_full102_resolves_expansion_gate(self) -> None:
        values = list(inputs())
        protocol, analysis = values[13], values[15]
        analysis["candidate_decisions"]["aegis_clean_adapter"][
            "expand_to_full102"
        ] = True
        analysis["expand_to_full102"] = ["aegis_clean_adapter"]
        expansion_protocol, expansion_analysis = full102_expansion(
            "aegis", protocol, analysis, ["aegis_clean_adapter"]
        )
        result = audit(
            *values,
            aegis_expansion_protocol=expansion_protocol,
            aegis_expansion_analysis=expansion_analysis,
        )
        self.assertTrue(result["strict_v4_confirmed_external_sota_allowed"])


if __name__ == "__main__":
    unittest.main()
