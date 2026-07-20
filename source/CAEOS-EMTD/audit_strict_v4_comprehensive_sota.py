from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Optional

from create_strict_v4_external_confirmation_protocol import canonical_hash


UNKNOWN_METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
REPORT_METRICS = ("known_macro_f1",) + UNKNOWN_METRICS
POSTHOC_METHODS = {"react_energy", "dice", "she"}
EXTENDED_METHOD = "sirc_msp_residual"
EXTERNAL_TRAINING_METHODS = {"closr", "cade", "sieve"}
COMPLEMENTARY_TRAINING_METHODS = {"arpl", "palm", "ronetc", "foss"}
AEGIS_TRAINING_METHODS = {"aegis_clean_adapter"}
EXTERNAL_TRAINING_CHECKS = {
    "pilot_runs_complete",
    "split_and_leakage_integrity",
    "known_f1_tolerance",
    "top_two_rank",
    "metric_breadth",
    "overall_gain",
    "suite_robustness",
}


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _development_external_dominance(
    summary: dict[str, Any], selected_algorithm: str
) -> dict[str, Any]:
    rows = {row["method"]: row for row in summary["overall"]}
    if selected_algorithm not in rows:
        raise ValueError("selected algorithm is missing from the full summary")
    external = [row for name, row in rows.items() if not name.startswith("caeos_")]
    if not external:
        raise ValueError("full summary contains no external methods")
    selected = rows[selected_algorithm]
    checks = {}
    strongest = {}
    for metric in UNKNOWN_METRICS:
        if metric == "unknown_fpr95":
            competitor = min(external, key=lambda row: (row[metric], row["method"]))
            gain = competitor[metric] - selected[metric]
        else:
            competitor = max(external, key=lambda row: (row[metric], row["method"]))
            gain = selected[metric] - competitor[metric]
        checks[metric] = gain > 0.0
        strongest[metric] = {
            "method": competitor["method"],
            "selected_value": selected[metric],
            "competitor_value": competitor[metric],
            "oriented_gain": gain,
        }
    return {
        "passes": all(checks.values()),
        "metric_checks": checks,
        "strongest_external_by_metric": strongest,
    }


def _posthoc_screen_checks(
    summary: dict[str, Any],
    posthoc_summary: dict[str, Any],
    full_summary_sha256: str,
) -> dict[str, bool]:
    base_rows = {row["method"]: row for row in summary.get("overall", [])}
    posthoc_rows = {
        row["method"]: row for row in posthoc_summary.get("overall", [])
    }
    inherited_metrics_identical = bool(base_rows) and all(
        method in posthoc_rows
        and all(
            abs(float(row[metric]) - float(posthoc_rows[method][metric])) <= 1e-12
            for metric in REPORT_METRICS
        )
        for method, row in base_rows.items()
    )
    validation = posthoc_summary.get("validation", {})
    comparator = posthoc_summary.get("comparator_decision", {})
    return {
        "schema_is_25method_screen": posthoc_summary.get("schema_version")
        == "strict_v4_posthoc_ood_25method_screen_v1",
        "status_is_complete": posthoc_summary.get("status") == "complete",
        "method_count_is_25": posthoc_summary.get("method_count") == 25
        and len(posthoc_rows) == 25,
        "added_methods_are_react_dice_she": set(
            posthoc_summary.get("added_methods", [])
        )
        == POSTHOC_METHODS,
        "posthoc_validation_passes": validation.get("passes") is True,
        "posthoc_scenario_count_is_102": validation.get("scenario_count") == 102,
        "posthoc_report_count_is_306": validation.get("report_count") == 306,
        "posthoc_artifact_checks_is_306": validation.get("artifact_checks") == 306,
        "posthoc_split_fingerprints_identical": validation.get(
            "split_fingerprints_identical"
        )
        is True,
        "posthoc_has_no_test_label_fitting_or_selection": validation.get(
            "unknown_or_test_labels_used_for_fitting_or_selection"
        )
        is False,
        "base_method_metrics_are_inherited": inherited_metrics_identical,
        "posthoc_summary_binds_full_summary": posthoc_summary.get(
            "existing_summary_sha256"
        )
        == full_summary_sha256,
        "frozen_external_comparator_remains_opendetect": comparator.get(
            "selected_comparator"
        )
        == "opendetect"
        and comparator.get("existing_opendetect_protocol_remains_valid") is True,
    }


def _extended_screen_checks(
    posthoc_summary: dict[str, Any],
    extended_summary: dict[str, Any],
    posthoc_summary_sha256: str,
) -> dict[str, bool]:
    posthoc_rows = {row["method"]: row for row in posthoc_summary.get("overall", [])}
    extended_rows = {row["method"]: row for row in extended_summary.get("overall", [])}
    inherited_metrics_identical = bool(posthoc_rows) and all(
        method in extended_rows
        and all(
            abs(float(row[metric]) - float(extended_rows[method][metric])) <= 1e-12
            for metric in REPORT_METRICS
        )
        for method, row in posthoc_rows.items()
    )
    validation = extended_summary.get("validation", {})
    comparator = extended_summary.get("comparator_decision", {})
    return {
        "schema_is_26method_screen": extended_summary.get("schema_version")
        == "strict_v4_sirc_residual_26method_screen_v1",
        "status_is_complete": extended_summary.get("status") == "complete",
        "method_count_is_26": extended_summary.get("method_count") == 26
        and len(extended_rows) == 26,
        "added_method_is_sirc_msp_residual": extended_summary.get("added_method")
        == EXTENDED_METHOD
        and EXTENDED_METHOD in extended_rows,
        "sirc_validation_passes": validation.get("passes") is True,
        "sirc_scenario_and_report_counts_are_102": validation.get("scenario_count") == 102
        and validation.get("report_count") == 102,
        "sirc_failure_count_is_zero": validation.get("failure_count") == 0,
        "sirc_split_provenance_and_no_leak_checks_are_102": validation.get(
            "split_fingerprint_pair_checks"
        )
        == 102
        and validation.get("source_provenance_checks") == 102
        and validation.get("no_leak_checks") == 102,
        "only_gate_passing_sirc_variant_enters_table": validation.get(
            "expanded_method"
        )
        == EXTENDED_METHOD
        and validation.get("incidental_method_excluded_from_26method_table")
        == "sirc_msp_l1",
        "posthoc_25method_metrics_are_inherited": inherited_metrics_identical,
        "extended_summary_binds_25method_summary": extended_summary.get(
            "existing_25method_summary_sha256"
        )
        == posthoc_summary_sha256,
        "sirc_protocol_chain_is_bound": all(
            isinstance(extended_summary.get(name), str)
            and len(extended_summary[name]) == 64
            for name in (
                "full_protocol_manifest_sha256",
                "pilot_expansion_gate_manifest_sha256",
                "pilot_analysis_sha256",
            )
        ),
        "frozen_external_comparator_remains_opendetect": comparator.get(
            "selected_comparator"
        )
        == "opendetect"
        and comparator.get("comparator_changed") is False,
    }


def _doc_pilot_checks(
    protocol: dict[str, Any],
    gate: dict[str, Any],
    analysis: dict[str, Any],
) -> dict[str, bool]:
    validation = analysis.get("validation", {})
    expansion = analysis.get("expansion_checks", {})
    rows = {row.get("method"): row for row in analysis.get("overall", [])}
    doc_row = rows.get("doc_fixed", {})
    opendetect_row = rows.get("opendetect", {})
    selection_checks = ("top_two_rank", "metric_breadth", "overall_gain", "suite_robustness")
    return {
        "protocol_schema_and_sha_are_valid": protocol.get("schema_version")
        == "strict_v4_mlp_doc_fixed_protocol_v1"
        and protocol.get("manifest_sha256") == canonical_hash(protocol),
        "protocol_is_zero_ood_fixed_14_scenario_pilot": protocol.get("mode") == "pilot"
        and protocol.get("expected_runs") == 14
        and protocol.get("fit_data") == "known_training_embeddings_and_labels_only"
        and protocol.get("ood_parameter_sweep") is False
        and protocol.get("alpha") == 3.0
        and protocol.get("minimum_class_threshold") == 0.5,
        "gate_schema_and_sha_are_valid": gate.get("schema_version")
        == "strict_v4_mlp_doc_fixed_expansion_gate_v1"
        and gate.get("manifest_sha256") == canonical_hash(gate),
        "gate_was_frozen_at_zero_and_binds_protocol": gate.get(
            "pilot_metrics_observed_at_freeze"
        )
        == 0
        and gate.get("pilot_protocol_manifest_sha256")
        == protocol.get("manifest_sha256"),
        "analysis_schema_and_chain_are_valid": analysis.get("schema_version")
        == "strict_v4_mlp_doc_fixed_pilot_analysis_v1"
        and analysis.get("pilot_protocol_manifest_sha256")
        == protocol.get("manifest_sha256")
        and analysis.get("expansion_gate_manifest_sha256")
        == gate.get("manifest_sha256"),
        "doc_validation_passes": validation.get("passes") is True,
        "doc_14_scenarios_zero_failures_and_no_leak": validation.get(
            "scenario_count"
        )
        == 14
        and validation.get("failure_count") == 0
        and validation.get("split_fingerprint_checks") == 14
        and validation.get("no_leak_checks") == 14
        and validation.get("optimization_checks") == 14
        and validation.get("threshold_range_checks") == 14,
        "doc_structural_expansion_checks_pass": all(
            expansion.get(name) is True
            for name in (
                "pilot_runs_complete",
                "split_integrity",
                "known_f1_tolerance",
                "optimization_integrity",
                "nondegenerate_score",
            )
        ),
        "doc_negative_expansion_decision_is_preserved": analysis.get(
            "decision", {}
        ).get("expand_doc_fixed_to_full102")
        is False
        and all(expansion.get(name) is False for name in selection_checks),
        "doc_does_not_replace_opendetect": set(rows)
        == {"doc_fixed", "mlp_msp", "mlp_energy", "opendetect"}
        and float(doc_row.get("mean_unknown_metric_rank", 0.0))
        > float(opendetect_row.get("mean_unknown_metric_rank", 99.0)),
    }


def _mandatory_screen_checks(
    extended_summary: dict[str, Any],
    mandatory_summary: dict[str, Any],
    extended_summary_sha256: str,
) -> dict[str, bool]:
    extended_rows = {row["method"]: row for row in extended_summary.get("overall", [])}
    mandatory_rows = {row["method"]: row for row in mandatory_summary.get("overall", [])}
    inherited_metrics_identical = bool(extended_rows) and all(
        method in mandatory_rows
        and all(
            abs(float(row[metric]) - float(mandatory_rows[method][metric])) <= 1e-12
            for metric in REPORT_METRICS
        )
        for method, row in extended_rows.items()
    )
    validation = mandatory_summary.get("validation", {})
    comparator = mandatory_summary.get("comparator_decision", {})
    return {
        "schema_is_28method_screen": mandatory_summary.get("schema_version")
        == "strict_v4_mandatory_scores_28method_screen_v1",
        "status_is_complete": mandatory_summary.get("status") == "complete",
        "method_count_is_28": mandatory_summary.get("method_count") == 28
        and len(mandatory_rows) == 28,
        "added_methods_are_entropy_and_prototype": mandatory_summary.get("added_methods")
        == ["shannon_entropy", "prototype_distance"]
        and {"shannon_entropy", "prototype_distance"}.issubset(mandatory_rows),
        "mandatory_validation_passes": validation.get("passes") is True,
        "mandatory_counts_are_102_scenarios_204_reports": validation.get("scenario_count") == 102
        and validation.get("report_count") == 204
        and validation.get("failure_count") == 0,
        "mandatory_integrity_checks_are_102": validation.get("split_fingerprint_pair_checks") == 102
        and validation.get("source_provenance_checks") == 102
        and validation.get("no_leak_checks") == 102
        and validation.get("nondegenerate_score_checks") == 102,
        "extended_26method_metrics_are_inherited": inherited_metrics_identical,
        "mandatory_summary_binds_26method_summary": mandatory_summary.get(
            "existing_26method_summary_sha256"
        )
        == extended_summary_sha256,
        "mandatory_full_protocol_is_bound": isinstance(
            mandatory_summary.get("protocol_manifest_sha256"), str
        )
        and len(mandatory_summary["protocol_manifest_sha256"]) == 64,
        "frozen_external_comparator_remains_opendetect": comparator.get(
            "selected_comparator"
        )
        == "opendetect"
        and comparator.get("previous_comparator") == "opendetect"
        and comparator.get("comparator_changed") is False,
    }


def _mahalanobis_pp_screen_checks(
    mandatory_summary: dict[str, Any],
    mahalanobis_summary: dict[str, Any],
    mandatory_summary_sha256: str,
) -> dict[str, bool]:
    mandatory_rows = {row["method"]: row for row in mandatory_summary.get("overall", [])}
    extended_rows = {
        row["method"]: row for row in mahalanobis_summary.get("overall", [])
    }
    inherited_metrics_identical = bool(mandatory_rows) and all(
        method in extended_rows
        and all(
            abs(float(row[metric]) - float(extended_rows[method][metric])) <= 1e-12
            for metric in REPORT_METRICS
        )
        for method, row in mandatory_rows.items()
    )
    validation = mahalanobis_summary.get("validation", {})
    comparator = mahalanobis_summary.get("comparator_decision", {})
    return {
        "schema_is_29method_screen": mahalanobis_summary.get("schema_version")
        == "strict_v4_mahalanobis_pp_29method_screen_v1",
        "status_is_complete": mahalanobis_summary.get("status") == "complete",
        "method_count_is_29": mahalanobis_summary.get("method_count") == 29
        and len(extended_rows) == 29,
        "added_method_is_mahalanobis_pp": mahalanobis_summary.get("added_methods")
        == ["mahalanobis_pp"]
        and "mahalanobis_pp" in extended_rows,
        "full102_validation_passes": validation.get("passes") is True,
        "full102_counts_are_complete": validation.get("scenario_count") == 102
        and validation.get("artifact_checks") == 612
        and validation.get("split_fingerprint_checks") == 102
        and validation.get("failure_count") == 0,
        "full102_has_no_test_label_fitting_or_selection": validation.get(
            "unknown_or_test_labels_used_for_fitting_or_selection"
        )
        is False,
        "mandatory_28method_metrics_are_inherited": inherited_metrics_identical,
        "summary_binds_mandatory_28method_file": mahalanobis_summary.get(
            "existing_28method_summary_sha256"
        )
        == mandatory_summary_sha256,
        "full102_protocol_is_bound": isinstance(
            mahalanobis_summary.get("protocol_manifest_sha256"), str
        )
        and len(mahalanobis_summary["protocol_manifest_sha256"]) == 64,
        "frozen_external_comparator_remains_opendetect": comparator.get(
            "selected_comparator"
        )
        == "opendetect"
        and comparator.get("existing_opendetect_protocol_remains_valid") is True,
    }


def _excel_screen_checks(
    mahalanobis_summary: dict[str, Any],
    excel_summary: dict[str, Any],
    mahalanobis_summary_sha256: str,
) -> dict[str, bool]:
    inherited_rows = {
        row["method"]: row for row in mahalanobis_summary.get("overall", [])
    }
    extended_rows = {row["method"]: row for row in excel_summary.get("overall", [])}
    inherited_metrics_identical = bool(inherited_rows) and all(
        method in extended_rows
        and all(
            abs(float(row[metric]) - float(extended_rows[method][metric])) <= 1e-12
            for metric in REPORT_METRICS
        )
        for method, row in inherited_rows.items()
    )
    validation = excel_summary.get("validation", {})
    comparator = excel_summary.get("comparator_decision", {})
    return {
        "schema_is_30method_screen": excel_summary.get("schema_version")
        == "strict_v4_excel_30method_screen_v1",
        "status_is_complete": excel_summary.get("status") == "complete",
        "method_count_is_30": excel_summary.get("method_count") == 30
        and len(extended_rows) == 30,
        "added_method_is_excel": excel_summary.get("added_methods") == ["excel"]
        and "excel" in extended_rows,
        "full102_validation_passes": validation.get("passes") is True,
        "full102_counts_are_complete": validation.get("scenario_count") == 102
        and validation.get("artifact_checks") == 612
        and validation.get("split_fingerprint_checks") == 102
        and validation.get("failure_count") == 0,
        "full102_has_no_test_label_fitting_or_selection": validation.get(
            "unknown_or_test_labels_used_for_fitting_or_selection"
        )
        is False,
        "mahalanobis_29method_metrics_are_inherited": inherited_metrics_identical,
        "summary_binds_mahalanobis_29method_file": excel_summary.get(
            "existing_29method_summary_sha256"
        )
        == mahalanobis_summary_sha256,
        "full102_protocol_is_bound": isinstance(
            excel_summary.get("protocol_manifest_sha256"), str
        )
        and len(excel_summary["protocol_manifest_sha256"]) == 64,
        "frozen_external_comparator_remains_opendetect": comparator.get(
            "selected_comparator"
        )
        == "opendetect"
        and comparator.get("existing_opendetect_protocol_remains_valid") is True,
    }


def _external_training_pilot_checks(
    protocol: dict[str, Any],
    gate: dict[str, Any],
    analysis: dict[str, Any],
) -> dict[str, bool]:
    validation = analysis.get("validation", {})
    decisions = analysis.get("candidate_decisions", {})
    decisions_are_complete_negative = set(decisions) == EXTERNAL_TRAINING_METHODS and all(
        set(decision.get("checks", {})) == EXTERNAL_TRAINING_CHECKS
        and all(isinstance(value, bool) for value in decision["checks"].values())
        and decision.get("expand_to_full102") is False
        for decision in decisions.values()
    )
    return {
        "protocol_schema_and_sha_are_valid": protocol.get("schema_version")
        == "strict_v4_external_training_pilot_protocol_v1"
        and protocol.get("manifest_sha256") == canonical_hash(protocol),
        "protocol_is_frozen_zero_result_14_scenario_42_run_screen": protocol.get(
            "status"
        )
        == "frozen_before_pilot_results"
        and protocol.get("pilot_metrics_observed_at_freeze") == 0
        and protocol.get("expected_scenarios") == 14
        and protocol.get("expected_runs") == 42
        and protocol.get("seed") == 7
        and set(protocol.get("methods", [])) == EXTERNAL_TRAINING_METHODS
        and protocol.get("unknown_or_test_labels_used_for_fitting_or_selection")
        is False
        and isinstance(protocol.get("coverage_manifest_sha256"), str)
        and len(protocol["coverage_manifest_sha256"]) == 64,
        "gate_schema_and_sha_are_valid": gate.get("schema_version")
        == "strict_v4_external_training_pilot_expansion_gate_v1"
        and gate.get("manifest_sha256") == canonical_hash(gate),
        "gate_was_frozen_at_zero_and_binds_protocol": gate.get(
            "pilot_metrics_observed_at_freeze"
        )
        == 0
        and gate.get("pilot_protocol_manifest_sha256")
        == protocol.get("manifest_sha256")
        and set(gate.get("candidates", [])) == EXTERNAL_TRAINING_METHODS,
        "analysis_schema_status_and_chain_are_valid": analysis.get("schema_version")
        == "strict_v4_external_training_pilot_analysis_v1"
        and analysis.get("status") == "complete"
        and analysis.get("pilot_protocol_manifest_sha256")
        == protocol.get("manifest_sha256")
        and analysis.get("expansion_gate_manifest_sha256")
        == gate.get("manifest_sha256"),
        "validation_passes_14_scenarios_42_runs_zero_failures": validation.get(
            "passes"
        )
        is True
        and validation.get("scenario_count") == 14
        and validation.get("method_run_count") == 42
        and validation.get("failure_count") == 0
        and validation.get("split_fingerprint_checks") == 14
        and validation.get("no_leak_checks") == 14,
        "no_candidate_requires_full102_expansion": analysis.get(
            "expand_to_full102"
        )
        == []
        and decisions_are_complete_negative,
    }


def _training_full102_expansion_checks(
    pilot_protocol: dict[str, Any],
    pilot_analysis: dict[str, Any],
    expansion_protocol: Optional[dict[str, Any]],
    expansion_analysis: Optional[dict[str, Any]],
    expected_group: str,
    expanded: set[str],
) -> dict[str, bool]:
    if not expanded:
        return {
            "full102_expansion_is_not_required_or_is_complete": True,
            "full102_expansion_chain_is_valid": expansion_protocol is None
            and expansion_analysis is None,
        }
    if expansion_protocol is None or expansion_analysis is None:
        return {
            "full102_expansion_is_not_required_or_is_complete": False,
            "full102_expansion_chain_is_valid": False,
        }
    validation = expansion_analysis.get("validation", {})
    expected_runs = 102 * len(expanded)
    chain_valid = (
        expansion_protocol.get("schema_version")
        == "strict_v4_training_full102_expansion_protocol_v1"
        and expansion_protocol.get("manifest_sha256")
        == canonical_hash(expansion_protocol)
        and expansion_protocol.get("status") == "frozen_before_full102_results"
        and expansion_protocol.get("group") == expected_group
        and expansion_protocol.get("pilot_protocol_manifest_sha256")
        == pilot_protocol.get("manifest_sha256")
        and expansion_protocol.get("pilot_analysis_sha256")
        == canonical_hash(pilot_analysis)
        and set(expansion_protocol.get("methods", [])) == expanded
        and expansion_protocol.get("expected_scenarios") == 102
        and expansion_protocol.get("expected_runs") == expected_runs
        and expansion_protocol.get("full102_metrics_observed_at_freeze") == 0
        and expansion_analysis.get("schema_version")
        == "strict_v4_training_full102_expansion_analysis_v1"
        and expansion_analysis.get("status") == "complete"
        and expansion_analysis.get("group") == expected_group
        and expansion_analysis.get("protocol_manifest_sha256")
        == expansion_protocol.get("manifest_sha256")
        and set(expansion_analysis.get("methods", [])) == expanded
    )
    complete = (
        validation.get("passes") is True
        and validation.get("scenario_count") == 102
        and validation.get("method_run_count") == expected_runs
        and validation.get("expected_method_run_count") == expected_runs
        and validation.get("split_fingerprint_checks") == 102
        and validation.get("no_leak_checks") == 102
        and validation.get("failure_count") == 0
    )
    return {
        "full102_expansion_is_not_required_or_is_complete": complete,
        "full102_expansion_chain_is_valid": chain_valid,
    }


def _complementary_training_pilot_checks(
    protocol: dict[str, Any],
    gate: dict[str, Any],
    analysis: dict[str, Any],
    expansion_protocol: Optional[dict[str, Any]] = None,
    expansion_analysis: Optional[dict[str, Any]] = None,
) -> dict[str, bool]:
    validation = analysis.get("validation", {})
    decisions = analysis.get("candidate_decisions", {})
    expanded = set(analysis.get("expand_to_full102", []))
    decisions_are_complete = (
        set(decisions) == COMPLEMENTARY_TRAINING_METHODS
        and all(
            set(decision.get("checks", {})) == EXTERNAL_TRAINING_CHECKS
            and all(isinstance(value, bool) for value in decision["checks"].values())
            and decision.get("expand_to_full102") is (method in expanded)
            for method, decision in decisions.items()
        )
    )
    expansion_checks = _training_full102_expansion_checks(
        protocol,
        analysis,
        expansion_protocol,
        expansion_analysis,
        "complementary",
        expanded,
    )
    return {
        "protocol_schema_and_sha_are_valid": protocol.get("schema_version")
        == "strict_v4_complementary_training_pilot_protocol_v1"
        and protocol.get("manifest_sha256") == canonical_hash(protocol),
        "protocol_is_frozen_zero_result_14_scenario_56_run_screen": protocol.get(
            "status"
        )
        == "frozen_before_pilot_results"
        and protocol.get("pilot_metrics_observed_at_freeze") == 0
        and protocol.get("expected_scenarios") == 14
        and protocol.get("expected_runs") == 56
        and protocol.get("seed") == 7
        and set(protocol.get("methods", [])) == COMPLEMENTARY_TRAINING_METHODS
        and protocol.get("unknown_or_test_labels_used_for_fitting_or_selection")
        is False
        and isinstance(protocol.get("coverage_manifest_sha256"), str)
        and len(protocol["coverage_manifest_sha256"]) == 64,
        "gate_schema_and_sha_are_valid": gate.get("schema_version")
        == "strict_v4_complementary_training_pilot_expansion_gate_v1"
        and gate.get("manifest_sha256") == canonical_hash(gate),
        "gate_was_frozen_at_zero_and_binds_protocol": gate.get(
            "pilot_metrics_observed_at_freeze"
        )
        == 0
        and gate.get("pilot_protocol_manifest_sha256")
        == protocol.get("manifest_sha256")
        and set(gate.get("candidates", [])) == COMPLEMENTARY_TRAINING_METHODS,
        "analysis_schema_status_and_chain_are_valid": analysis.get("schema_version")
        == "strict_v4_complementary_training_pilot_analysis_v1"
        and analysis.get("status") == "complete"
        and analysis.get("pilot_protocol_manifest_sha256")
        == protocol.get("manifest_sha256")
        and analysis.get("expansion_gate_manifest_sha256")
        == gate.get("manifest_sha256"),
        "validation_passes_14_scenarios_56_runs_zero_failures": validation.get(
            "passes"
        )
        is True
        and validation.get("scenario_count") == 14
        and validation.get("method_run_count") == 56
        and validation.get("failure_count") == 0
        and validation.get("split_fingerprint_checks") == 14
        and validation.get("no_leak_checks") == 14,
        "candidate_decisions_are_complete_and_consistent": decisions_are_complete,
        **expansion_checks,
    }


def _aegis_training_pilot_checks(
    protocol: dict[str, Any],
    gate: dict[str, Any],
    analysis: dict[str, Any],
    expansion_protocol: Optional[dict[str, Any]] = None,
    expansion_analysis: Optional[dict[str, Any]] = None,
) -> dict[str, bool]:
    validation = analysis.get("validation", {})
    decisions = analysis.get("candidate_decisions", {})
    expanded = set(analysis.get("expand_to_full102", []))
    decisions_are_complete = set(decisions) == AEGIS_TRAINING_METHODS and all(
        set(decision.get("checks", {})) == EXTERNAL_TRAINING_CHECKS
        and all(isinstance(value, bool) for value in decision["checks"].values())
        and decision.get("expand_to_full102") is (method in expanded)
        for method, decision in decisions.items()
    )
    expansion_checks = _training_full102_expansion_checks(
        protocol,
        analysis,
        expansion_protocol,
        expansion_analysis,
        "aegis",
        expanded,
    )
    return {
        "protocol_schema_and_sha_are_valid": protocol.get("schema_version")
        == "strict_v4_aegis_training_pilot_protocol_v1"
        and protocol.get("manifest_sha256") == canonical_hash(protocol),
        "protocol_is_frozen_zero_result_14_scenario_14_run_screen": protocol.get(
            "status"
        )
        == "frozen_before_pilot_results"
        and protocol.get("pilot_metrics_observed_at_freeze") == 0
        and protocol.get("expected_scenarios") == 14
        and protocol.get("expected_runs") == 14
        and protocol.get("seed") == 7
        and set(protocol.get("methods", [])) == AEGIS_TRAINING_METHODS
        and protocol.get("unknown_or_test_labels_used_for_fitting_or_selection")
        is False
        and protocol.get("smoke_evidence", {}).get("status") == "pass"
        and isinstance(protocol.get("coverage_manifest_sha256"), str)
        and len(protocol["coverage_manifest_sha256"]) == 64,
        "gate_schema_and_sha_are_valid": gate.get("schema_version")
        == "strict_v4_aegis_training_pilot_expansion_gate_v1"
        and gate.get("manifest_sha256") == canonical_hash(gate),
        "gate_was_frozen_at_zero_and_binds_protocol": gate.get(
            "pilot_metrics_observed_at_freeze"
        )
        == 0
        and gate.get("pilot_protocol_manifest_sha256")
        == protocol.get("manifest_sha256")
        and set(gate.get("candidates", [])) == AEGIS_TRAINING_METHODS,
        "analysis_schema_status_and_chain_are_valid": analysis.get("schema_version")
        == "strict_v4_aegis_training_pilot_analysis_v1"
        and analysis.get("status") == "complete"
        and analysis.get("pilot_protocol_manifest_sha256")
        == protocol.get("manifest_sha256")
        and analysis.get("expansion_gate_manifest_sha256")
        == gate.get("manifest_sha256"),
        "validation_passes_14_scenarios_14_runs_zero_failures": validation.get(
            "passes"
        )
        is True
        and validation.get("scenario_count") == 14
        and validation.get("method_run_count") == 14
        and validation.get("failure_count") == 0
        and validation.get("split_fingerprint_checks") == 14
        and validation.get("no_leak_checks") == 14,
        "candidate_decisions_are_complete_and_consistent": decisions_are_complete,
        **expansion_checks,
    }


def _fusion_operator_checks(
    fusion_protocol: dict[str, Any],
    fusion_analysis: dict[str, Any],
    attention_protocol: dict[str, Any],
    attention_analysis: dict[str, Any],
) -> dict[str, bool]:
    expected_methods = {
        "f2_probability_average",
        "f3_entropy_conditioned_attention",
        "f4_edl_evidence_sum",
        "f5_reliability_gate",
        "f6_standard_ds_fusion",
        "f9_caeos_final_probability",
    }
    metrics = {
        "known_macro_f1",
        "unknown_auroc",
        "unknown_aupr",
        "unknown_fpr95",
        "oscr",
        "known_ece",
    }
    fusion_aggregate = fusion_analysis.get("aggregate", {})
    attention_aggregate = attention_analysis.get("aggregate", {})
    cross_analysis_consistent = all(
        abs(
            float(fusion_aggregate.get(fusion_method, {}).get(metric, {}).get("mean", math.nan))
            - float(attention_aggregate.get(attention_method, {}).get(metric, {}).get("mean", math.nan))
        )
        <= 1e-12
        for fusion_method, attention_method in (
            ("f3_entropy_conditioned_attention", "entropy_conditioned_learnable_attention"),
            ("f5_reliability_gate", "caeos_reliability_fusion"),
        )
        for metric in metrics
    )
    return {
        "fusion_protocol_v2_schema_and_sha_are_valid": fusion_protocol.get(
            "schema_version"
        )
        == "strict_v4_fusion_operator_protocol_v2"
        and fusion_protocol.get("manifest_sha256") == canonical_hash(fusion_protocol),
        "fusion_analysis_is_complete_and_bound": fusion_analysis.get("schema_version")
        == "strict_v4_fusion_operator_analysis_v2"
        and fusion_analysis.get("status") == "complete"
        and fusion_analysis.get("protocol_manifest_sha256")
        == fusion_protocol.get("manifest_sha256"),
        "fusion_matrix_has_102_scenarios_and_306_source_checks": fusion_analysis.get(
            "scenario_count"
        )
        == 102
        and fusion_analysis.get("source_integrity_checks") == 306,
        "all_six_fusion_methods_are_present": set(fusion_protocol.get("methods", []))
        == expected_methods
        and set(fusion_aggregate) == expected_methods,
        "attention_source_is_complete_and_bound": attention_protocol.get(
            "schema_version"
        )
        == "strict_v4_attention_fusion_protocol_v1"
        and attention_protocol.get("manifest_sha256") == canonical_hash(attention_protocol)
        and attention_analysis.get("schema_version")
        == "strict_v4_attention_fusion_analysis_v1"
        and attention_analysis.get("status") == "complete"
        and attention_analysis.get("protocol_manifest_sha256")
        == attention_protocol.get("manifest_sha256")
        and attention_analysis.get("scenario_count") == 102
        and attention_analysis.get("source_integrity_checks") == 306,
        "f3_and_f5_match_the_independent_attention_analysis": cross_analysis_consistent,
        "test_truth_is_isolated_and_pollution_claim_is_disabled": fusion_analysis.get(
            "test_truth_isolated_from_evidence_package"
        )
        is True
        and fusion_analysis.get("pollution_claim_allowed") is False
        and attention_analysis.get("test_truth_isolated_from_evidence_package") is True,
    }


def audit(
    summary: dict[str, Any],
    posthoc_summary: dict[str, Any],
    extended_summary: dict[str, Any],
    mandatory_summary: dict[str, Any],
    doc_protocol: dict[str, Any],
    doc_gate: dict[str, Any],
    doc_analysis: dict[str, Any],
    training_pilot_protocol: dict[str, Any],
    training_pilot_gate: dict[str, Any],
    training_pilot_analysis: dict[str, Any],
    complementary_pilot_protocol: dict[str, Any],
    complementary_pilot_gate: dict[str, Any],
    complementary_pilot_analysis: dict[str, Any],
    aegis_pilot_protocol: dict[str, Any],
    aegis_pilot_gate: dict[str, Any],
    aegis_pilot_analysis: dict[str, Any],
    optimal_decision: dict[str, Any],
    router_confirmation: dict[str, Any],
    external_confirmation: dict[str, Any],
    doh_summary: dict[str, Any],
    tournament_protocol: dict[str, Any],
    full_summary_sha256: str,
    posthoc_summary_sha256: str,
    extended_summary_sha256: str,
    fusion_protocol: dict[str, Any],
    fusion_analysis: dict[str, Any],
    attention_protocol: dict[str, Any],
    attention_analysis: dict[str, Any],
    mahalanobis_summary: dict[str, Any],
    mandatory_summary_sha256: str,
    excel_summary: dict[str, Any],
    mahalanobis_summary_sha256: str,
    complementary_expansion_protocol: Optional[dict[str, Any]] = None,
    complementary_expansion_analysis: Optional[dict[str, Any]] = None,
    aegis_expansion_protocol: Optional[dict[str, Any]] = None,
    aegis_expansion_analysis: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    if summary.get("schema_version") != "strict_v4_full103_coverage_summary_v1":
        raise ValueError("unexpected full summary schema")
    validation = summary.get("validation", {})
    screen_checks = {
        "summary_validation_passes": validation.get("passes") is True,
        "scenario_count_is_102": validation.get("scenario_count") == 102,
        "dataset_count_is_7": validation.get("dataset_count") == 7,
        "method_count_at_least_22": validation.get("method_count", 0) >= 22,
        "independent_baseline_run_checks_is_204": validation.get(
            "independent_baseline_run_checks"
        )
        == 204,
        "split_fingerprints_identical": validation.get(
            "split_fingerprints_identical"
        )
        is True,
    }
    if not all(screen_checks.values()):
        raise ValueError("full 102-scenario screen is incomplete")
    posthoc_checks = _posthoc_screen_checks(
        summary, posthoc_summary, full_summary_sha256
    )
    if not all(posthoc_checks.values()):
        raise ValueError("complete 25-method posthoc screen is incomplete")
    extended_checks = _extended_screen_checks(
        posthoc_summary, extended_summary, posthoc_summary_sha256
    )
    if not all(extended_checks.values()):
        raise ValueError("complete 26-method extended screen is incomplete")
    mandatory_checks = _mandatory_screen_checks(
        extended_summary, mandatory_summary, extended_summary_sha256
    )
    if not all(mandatory_checks.values()):
        raise ValueError("complete 28-method mandatory baseline screen is incomplete")
    mahalanobis_checks = _mahalanobis_pp_screen_checks(
        mandatory_summary, mahalanobis_summary, mandatory_summary_sha256
    )
    if not all(mahalanobis_checks.values()):
        raise ValueError("complete 29-method Mahalanobis++ baseline screen is incomplete")
    excel_checks = _excel_screen_checks(
        mahalanobis_summary, excel_summary, mahalanobis_summary_sha256
    )
    if not all(excel_checks.values()):
        raise ValueError("complete 30-method ExCeL baseline screen is incomplete")
    doc_checks = _doc_pilot_checks(doc_protocol, doc_gate, doc_analysis)
    if not all(doc_checks.values()):
        raise ValueError("required DOC-Fixed baseline pilot is incomplete")
    training_pilot_checks = _external_training_pilot_checks(
        training_pilot_protocol, training_pilot_gate, training_pilot_analysis
    )
    if not all(training_pilot_checks.values()):
        raise ValueError(
            "required external training baseline pilot is incomplete or requires full102 expansion"
        )
    complementary_pilot_checks = _complementary_training_pilot_checks(
        complementary_pilot_protocol,
        complementary_pilot_gate,
        complementary_pilot_analysis,
        complementary_expansion_protocol,
        complementary_expansion_analysis,
    )
    if not all(complementary_pilot_checks.values()):
        raise ValueError(
            "required complementary training baseline pilot is incomplete or requires full102 expansion"
        )
    aegis_pilot_checks = _aegis_training_pilot_checks(
        aegis_pilot_protocol,
        aegis_pilot_gate,
        aegis_pilot_analysis,
        aegis_expansion_protocol,
        aegis_expansion_analysis,
    )
    if not all(aegis_pilot_checks.values()):
        raise ValueError(
            "required AEGIS training baseline pilot is incomplete or requires full102 expansion"
        )
    fusion_operator_checks = _fusion_operator_checks(
        fusion_protocol,
        fusion_analysis,
        attention_protocol,
        attention_analysis,
    )
    if not all(fusion_operator_checks.values()):
        raise ValueError("required fusion operator baseline matrix is incomplete")
    if (
        optimal_decision.get("schema_version")
        != "strict_v4_optimal_self_algorithm_decision_v1"
    ):
        raise ValueError("unexpected optimal algorithm decision schema")
    if optimal_decision.get("manifest_sha256") != canonical_hash(optimal_decision):
        raise ValueError("optimal algorithm decision SHA mismatch")
    if (
        tournament_protocol.get("schema_version")
        != "strict_v4_self_algorithm_tournament_protocol_v1"
    ):
        raise ValueError("unexpected self-algorithm tournament protocol schema")
    if tournament_protocol.get("manifest_sha256") != canonical_hash(
        tournament_protocol
    ):
        raise ValueError("self-algorithm tournament protocol SHA mismatch")
    if (
        optimal_decision.get("tournament_protocol_manifest_sha256")
        != tournament_protocol["manifest_sha256"]
    ):
        raise ValueError("optimal decision tournament binding mismatch")
    selected = optimal_decision["selected_algorithm"]
    if selected not in {
        "caeos_domain_safe_router",
        "caeos_pairwise",
        "caeos_tail_aware_pairwise",
    }:
        raise ValueError("unsupported selected algorithm")
    if (
        router_confirmation.get("schema_version")
        != "strict_v4_domain_safe_router_confirmation_v1"
    ):
        raise ValueError("unexpected router confirmation schema")
    router_pass = router_confirmation.get("decision", {}).get("passes") is True
    expected_incumbent = (
        "caeos_domain_safe_router" if router_pass else "caeos_pairwise"
    )
    incumbent_consistent = (
        optimal_decision.get("incumbent_algorithm") == expected_incumbent
    )
    tail_wins = selected == "caeos_tail_aware_pairwise"
    tail_flags = (
        optimal_decision.get("tail_challenger_confirmation_passes") is True
        and optimal_decision.get("tail_vs_incumbent_replacement_gate_passes") is True
    )
    tournament_selection_consistent = (
        incumbent_consistent
        and ((tail_wins and tail_flags) or (not tail_wins and selected == expected_incumbent and not tail_flags))
    )
    if not tournament_selection_consistent:
        raise ValueError("optimal algorithm contradicts router or tournament confirmation")
    if (
        external_confirmation.get("schema_version")
        != "strict_v4_external_comparator_confirmation_v1"
    ):
        raise ValueError("unexpected external confirmation schema")
    if external_confirmation.get("selected_algorithm") != selected:
        raise ValueError("external confirmation algorithm mismatch")
    if doh_summary.get("schema_version") != "strict_v4_doh_extension_screen_v1":
        raise ValueError("unexpected DoH summary schema")
    doh_validation = doh_summary.get("validation", {})
    doh_checks = {
        "validation_passes": doh_validation.get("passes") is True,
        "scenario_count_is_3": doh_validation.get("scenario_count") == 3,
        "selection_is_descriptive_only": doh_summary.get("selection_policy")
        == "descriptive_only_no_method_selected_on_doh_test_results",
        "full_sota_claim_is_disabled_on_doh_screen": doh_summary.get(
            "full_sota_claim_allowed"
        )
        is False,
    }
    development = (
        {
            "passes": True,
            "status": "not_applicable_tail_selected_by_frozen_tournament",
            "metric_checks": {},
            "strongest_external_by_metric": {},
        }
        if tail_wins
        else _development_external_dominance(excel_summary, selected)
    )
    expected_external_seeds = (
        tournament_protocol["external_confirmation_branch"][
            "tail_challenger_wins"
        ]["fresh_seeds"]
        if tail_wins
        else tournament_protocol["external_confirmation_branch"]["incumbent_wins"][
            "seeds"
        ]
    )
    observed_external_seeds = external_confirmation.get("candidate_validation", {}).get(
        "seeds"
    )
    external_seed_branch_consistent = (
        sorted(optimal_decision.get("external_confirmation_seeds", []))
        == sorted(expected_external_seeds)
        and sorted(observed_external_seeds or []) == sorted(expected_external_seeds)
    )
    external_pass = external_confirmation.get("decision", {}).get("passes") is True
    seven_dataset_checks = {
        "complete_22_method_core_development_screen": all(screen_checks.values()),
        "complete_25_method_posthoc_development_screen": all(
            posthoc_checks.values()
        ),
        "complete_26_method_extended_development_screen": all(
            extended_checks.values()
        ),
        "complete_28_method_mandatory_development_screen": all(
            mandatory_checks.values()
        ),
        "complete_29_method_mahalanobis_pp_development_screen": all(
            mahalanobis_checks.values()
        ),
        "complete_30_method_excel_development_screen": all(excel_checks.values()),
        "required_doc_fixed_baseline_pilot_is_complete": all(doc_checks.values()),
        "required_external_training_baseline_pilot_is_complete": all(
            training_pilot_checks.values()
        ),
        "required_complementary_training_baseline_pilot_is_complete": all(
            complementary_pilot_checks.values()
        ),
        "required_aegis_training_baseline_pilot_is_complete": all(
            aegis_pilot_checks.values()
        ),
        "required_fusion_operator_baseline_matrix_is_complete": all(
            fusion_operator_checks.values()
        ),
        "incumbent_selection_consistent": incumbent_consistent,
        "optimal_tournament_selection_consistent": tournament_selection_consistent,
        "development_or_tournament_preselection_passes": development["passes"],
        "external_seed_branch_is_disjoint_and_consistent": external_seed_branch_consistent,
        "new_seed_external_confirmation_passes": external_pass,
    }
    seven_dataset_allowed = all(seven_dataset_checks.values())
    result = {
        "schema_version": "strict_v4_comprehensive_sota_audit_v11",
        "selected_algorithm": selected,
        "screen_checks": screen_checks,
        "posthoc_25method_checks": posthoc_checks,
        "extended_26method_checks": extended_checks,
        "mandatory_28method_checks": mandatory_checks,
        "mahalanobis_pp_29method_checks": mahalanobis_checks,
        "excel_30method_checks": excel_checks,
        "doc_fixed_pilot_checks": doc_checks,
        "external_training_pilot_checks": training_pilot_checks,
        "complementary_training_pilot_checks": complementary_pilot_checks,
        "aegis_training_pilot_checks": aegis_pilot_checks,
        "fusion_operator_checks": fusion_operator_checks,
        "router_confirmation_passes": router_pass,
        "tail_challenger_selected": tail_wins,
        "tournament_selection_consistent": tournament_selection_consistent,
        "development_external_dominance": development,
        "external_seed_branch_consistent": external_seed_branch_consistent,
        "external_confirmation_passes": external_pass,
        "seven_dataset_sota_checks": seven_dataset_checks,
        "strict_v4_confirmed_external_sota_allowed": seven_dataset_allowed,
        "doh_extension_checks": doh_checks,
        "doh_extension_is_descriptive_only": True,
        "eight_dataset_confirmed_sota_allowed": False,
        "claim_tier": (
            "confirmed_external_sota_7_datasets_102_scenarios"
            if seven_dataset_allowed
            else (
                "self_algorithm_confirmed_external_sota_unconfirmed"
                if tournament_selection_consistent
                else "development_only"
            )
        ),
        "claim_scope_note": (
            "DoHBrw2020 is an eighth-dataset descriptive screen and is not included "
            "in the confirmatory seven-dataset SOTA claim"
        ),
    }
    return result


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 comprehensive SOTA audit",
        "",
        f"Selected algorithm: `{result['selected_algorithm']}`.",
        f"Claim tier: `{result['claim_tier']}`.",
        "",
        "## Seven-dataset gate",
        "",
    ]
    for name, passed in result["seven_dataset_sota_checks"].items():
        lines.append(f"- `{name}`: {'PASS' if passed else 'FAIL'}")
    lines.extend(
        [
            "",
            "## Complete baseline screen",
            "",
        ]
    )
    for name, passed in result["posthoc_25method_checks"].items():
        lines.append(f"- `{name}`: {'PASS' if passed else 'FAIL'}")
    lines.extend(["", "## Extended 26-method screen", ""])
    for name, passed in result["extended_26method_checks"].items():
        lines.append(f"- `{name}`: {'PASS' if passed else 'FAIL'}")
    lines.extend(["", "## Mandatory 28-method screen", ""])
    for name, passed in result["mandatory_28method_checks"].items():
        lines.append(f"- `{name}`: {'PASS' if passed else 'FAIL'}")
    lines.extend(["", "## Mahalanobis++ 29-method screen", ""])
    for name, passed in result["mahalanobis_pp_29method_checks"].items():
        lines.append(f"- `{name}`: {'PASS' if passed else 'FAIL'}")
    lines.extend(["", "## ExCeL 30-method screen", ""])
    for name, passed in result["excel_30method_checks"].items():
        lines.append(f"- `{name}`: {'PASS' if passed else 'FAIL'}")
    lines.extend(["", "## Required DOC-Fixed pilot", ""])
    for name, passed in result["doc_fixed_pilot_checks"].items():
        lines.append(f"- `{name}`: {'PASS' if passed else 'FAIL'}")
    lines.extend(["", "## Required external training baseline pilot", ""])
    for name, passed in result["external_training_pilot_checks"].items():
        lines.append(f"- `{name}`: {'PASS' if passed else 'FAIL'}")
    lines.extend(["", "## Required complementary training baseline pilot", ""])
    for name, passed in result["complementary_training_pilot_checks"].items():
        lines.append(f"- `{name}`: {'PASS' if passed else 'FAIL'}")
    lines.extend(["", "## Required AEGIS training baseline pilot", ""])
    for name, passed in result["aegis_training_pilot_checks"].items():
        lines.append(f"- `{name}`: {'PASS' if passed else 'FAIL'}")
    lines.extend(["", "## Required fusion operator baseline matrix", ""])
    for name, passed in result["fusion_operator_checks"].items():
        lines.append(f"- `{name}`: {'PASS' if passed else 'FAIL'}")
    lines.extend(
        [
            "",
            "## DoH extension",
            "",
            result["claim_scope_note"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-summary", type=Path, required=True)
    parser.add_argument("--posthoc-summary", type=Path, required=True)
    parser.add_argument("--extended-summary", type=Path, required=True)
    parser.add_argument("--mandatory-summary", type=Path, required=True)
    parser.add_argument("--mahalanobis-pp-summary", type=Path, required=True)
    parser.add_argument("--excel-summary", type=Path, required=True)
    parser.add_argument("--doc-protocol", type=Path, required=True)
    parser.add_argument("--doc-gate", type=Path, required=True)
    parser.add_argument("--doc-analysis", type=Path, required=True)
    parser.add_argument("--training-pilot-protocol", type=Path, required=True)
    parser.add_argument("--training-pilot-gate", type=Path, required=True)
    parser.add_argument("--training-pilot-analysis", type=Path, required=True)
    parser.add_argument("--complementary-pilot-protocol", type=Path, required=True)
    parser.add_argument("--complementary-pilot-gate", type=Path, required=True)
    parser.add_argument("--complementary-pilot-analysis", type=Path, required=True)
    parser.add_argument("--aegis-pilot-protocol", type=Path, required=True)
    parser.add_argument("--aegis-pilot-gate", type=Path, required=True)
    parser.add_argument("--aegis-pilot-analysis", type=Path, required=True)
    parser.add_argument("--complementary-expansion-protocol", type=Path)
    parser.add_argument("--complementary-expansion-analysis", type=Path)
    parser.add_argument("--aegis-expansion-protocol", type=Path)
    parser.add_argument("--aegis-expansion-analysis", type=Path)
    parser.add_argument("--fusion-protocol", type=Path, required=True)
    parser.add_argument("--fusion-analysis", type=Path, required=True)
    parser.add_argument("--attention-protocol", type=Path, required=True)
    parser.add_argument("--attention-analysis", type=Path, required=True)
    parser.add_argument("--final-decision", type=Path, required=True)
    parser.add_argument("--router-confirmation", type=Path, required=True)
    parser.add_argument("--external-confirmation", type=Path, required=True)
    parser.add_argument("--doh-summary", type=Path, required=True)
    parser.add_argument("--tournament-protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    payloads = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in (
            args.full_summary,
            args.posthoc_summary,
            args.extended_summary,
            args.mandatory_summary,
            args.doc_protocol,
            args.doc_gate,
            args.doc_analysis,
            args.training_pilot_protocol,
            args.training_pilot_gate,
            args.training_pilot_analysis,
            args.complementary_pilot_protocol,
            args.complementary_pilot_gate,
            args.complementary_pilot_analysis,
            args.aegis_pilot_protocol,
            args.aegis_pilot_gate,
            args.aegis_pilot_analysis,
            args.final_decision,
            args.router_confirmation,
            args.external_confirmation,
            args.doh_summary,
            args.tournament_protocol,
        )
    ]
    optional_paths = (
        args.complementary_expansion_protocol,
        args.complementary_expansion_analysis,
        args.aegis_expansion_protocol,
        args.aegis_expansion_analysis,
    )
    if (optional_paths[0] is None) != (optional_paths[1] is None):
        raise ValueError("complementary expansion protocol and analysis must be provided together")
    if (optional_paths[2] is None) != (optional_paths[3] is None):
        raise ValueError("AEGIS expansion protocol and analysis must be provided together")
    optional_payloads = [
        json.loads(path.read_text(encoding="utf-8")) if path is not None else None
        for path in optional_paths
    ]
    fusion_payloads = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in (
            args.fusion_protocol,
            args.fusion_analysis,
            args.attention_protocol,
            args.attention_analysis,
        )
    ]
    mahalanobis_payload = json.loads(
        args.mahalanobis_pp_summary.read_text(encoding="utf-8")
    )
    excel_payload = json.loads(args.excel_summary.read_text(encoding="utf-8"))
    result = audit(
        *payloads,
        file_hash(args.full_summary),
        file_hash(args.posthoc_summary),
        file_hash(args.extended_summary),
        *fusion_payloads,
        mahalanobis_payload,
        file_hash(args.mandatory_summary),
        excel_payload,
        file_hash(args.mahalanobis_pp_summary),
        *optional_payloads,
    )
    result["input_file_sha256"] = {
        "full_summary": file_hash(args.full_summary),
        "posthoc_summary": file_hash(args.posthoc_summary),
        "extended_summary": file_hash(args.extended_summary),
        "mandatory_summary": file_hash(args.mandatory_summary),
        "mahalanobis_pp_summary": file_hash(args.mahalanobis_pp_summary),
        "excel_summary": file_hash(args.excel_summary),
        "doc_protocol": file_hash(args.doc_protocol),
        "doc_gate": file_hash(args.doc_gate),
        "doc_analysis": file_hash(args.doc_analysis),
        "training_pilot_protocol": file_hash(args.training_pilot_protocol),
        "training_pilot_gate": file_hash(args.training_pilot_gate),
        "training_pilot_analysis": file_hash(args.training_pilot_analysis),
        "complementary_pilot_protocol": file_hash(args.complementary_pilot_protocol),
        "complementary_pilot_gate": file_hash(args.complementary_pilot_gate),
        "complementary_pilot_analysis": file_hash(args.complementary_pilot_analysis),
        "aegis_pilot_protocol": file_hash(args.aegis_pilot_protocol),
        "aegis_pilot_gate": file_hash(args.aegis_pilot_gate),
        "aegis_pilot_analysis": file_hash(args.aegis_pilot_analysis),
        "fusion_protocol": file_hash(args.fusion_protocol),
        "fusion_analysis": file_hash(args.fusion_analysis),
        "attention_protocol": file_hash(args.attention_protocol),
        "attention_analysis": file_hash(args.attention_analysis),
        "optimal_decision": file_hash(args.final_decision),
        "router_confirmation": file_hash(args.router_confirmation),
        "external_confirmation": file_hash(args.external_confirmation),
        "doh_summary": file_hash(args.doh_summary),
        "tournament_protocol": file_hash(args.tournament_protocol),
    }
    for name, path in zip(
        (
            "complementary_expansion_protocol",
            "complementary_expansion_analysis",
            "aegis_expansion_protocol",
            "aegis_expansion_analysis",
        ),
        optional_paths,
    ):
        if path is not None:
            result["input_file_sha256"][name] = file_hash(path)
    result["audit_implementation_sha256"] = file_hash(Path(__file__))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "audit.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "audit.md").write_text(render(result), encoding="utf-8")
    print(render(result), end="")


if __name__ == "__main__":
    main()
