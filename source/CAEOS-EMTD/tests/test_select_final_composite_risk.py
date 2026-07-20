from select_final_composite_risk import CURRENT_SUITE_RISK, build_selection


def edge_selection() -> dict[str, object]:
    return {
        "schema_version": "final_internal_risk_selection_v1",
        "status": "confirmed_frozen",
        "selected_internal_risk": "cauchy_modality_support_union",
        "validated_task_count": 56,
        "scenario_count": 14,
    }


def manifest() -> dict[str, object]:
    return {
        "manifest_sha256": "manifest-hash",
        "confirmation_seeds": [83, 89, 97, 101],
        "selected_suite_risks": {
            "nf_cse": "disagreement_augmented",
            "ustc_tfc2016": "cauchy_conflict",
        },
    }


def inference(delta: float, lower: float) -> dict[str, object]:
    return {
        "metrics": {
            metric: {
                "oriented_mean_improvement": delta,
                "bootstrap_95_ci": {"lower": lower, "upper": 0.1},
            }
            for metric in (
                "known_macro_f1",
                "unknown_auroc",
                "unknown_aupr",
                "unknown_fpr95",
                "oscr",
            )
        }
    }


def confirmation(passes: bool) -> dict[str, object]:
    combined = inference(0.02, 0.01 if passes else 0.0)
    suites = {"nf_cse": inference(0.01, 0.01), "ustc_tfc2016": inference(0.01, 0.01)}
    return {
        "schema_version": "cross_suite_fixed_report_confirmation_v1",
        "candidate_status_before_confirmation": "frozen_unconfirmed",
        "selection_manifest_sha256": "manifest-hash",
        "selected_suite_risks": manifest()["selected_suite_risks"],
        "validation": {
            "paired_tasks": 96,
            "expected_seeds": [83, 89, 97, 101],
            "expected_scenarios": 24,
            "scenario_count": 24,
            "candidate_reports_extracted_from_same_model_run": True,
            "candidate_thresholds_fitted_on_known_validation": True,
            "candidate_runtime_selection_uses_unknown_or_test_labels": False,
            "reference_selection_uses_unknown_or_test_labels": False,
            "required_artifacts_validated_by_load_root": True,
        },
        "scenario_blocked_inference": combined,
        "suite_inference": suites,
        "frozen_confirmation_decision": {
            "frozen_gate": "cross_suite_fixed_risk_v1",
            "combined_auroc_bootstrap_lower_gt_zero": passes,
            "combined_safety_nonregression_tolerance": 0.01,
            "combined_safety_metrics": {
                "known_macro_f1": True,
                "unknown_aupr": True,
                "unknown_fpr95": True,
                "oscr": True,
            },
            "all_combined_safety_metrics_pass": True,
            "suite_unknown_metric_positive": {
                "nf_cse": {
                    "unknown_auroc": True,
                    "unknown_aupr": True,
                    "unknown_fpr95": True,
                    "oscr": True,
                },
                "ustc_tfc2016": {
                    "unknown_auroc": True,
                    "unknown_aupr": True,
                    "unknown_fpr95": True,
                    "oscr": True,
                },
            },
            "all_suite_unknown_metrics_positive": True,
            "passes": passes,
        },
        "confirmation_status": "confirmed" if passes else "not_confirmed",
    }


def test_confirmed_cross_suite_candidates_enter_final_policy() -> None:
    result = build_selection(
        edge_selection(), confirmation(True), manifest(), "edge", "confirmation", "manifest"
    )
    assert result["suite_risks"] == {
        "edge_iiot": "cauchy_modality_support_union",
        "nf_cse": "disagreement_augmented",
        "ustc_tfc2016": "cauchy_conflict",
    }
    assert result["cross_suite_candidate_confirmed"] is True


def test_failed_cross_suite_candidates_fall_back_to_current_policy() -> None:
    result = build_selection(
        edge_selection(), confirmation(False), manifest(), "edge", "confirmation", "manifest"
    )
    assert result["suite_risks"]["nf_cse"] == CURRENT_SUITE_RISK
    assert result["suite_risks"]["ustc_tfc2016"] == CURRENT_SUITE_RISK
    assert result["runtime_selection_uses_unknown_or_test_labels"] is False
