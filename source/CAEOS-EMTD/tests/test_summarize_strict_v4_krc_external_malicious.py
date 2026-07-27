import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_strict_v4_krc_external_malicious import (
    METRICS,
    candidate_report,
    comparator_checks,
)


def report(value):
    return {
        "unknown_auroc": value,
        "unknown_aupr": value,
        "unknown_fpr95": 1.0 - value,
        "oscr": value,
        "known_macro_f1": value,
    }


def metrics():
    value = {
        "schema_version": "strict_v4_krc_external_runtime_metrics_v1",
        "state": "complete",
        "algorithm": "krc_csr_caeos_v1",
        "diagnostics": {
            "unknown_or_test_labels_used_for_fit_selection_calibration_"
            "threshold_or_routing": False,
            "test_labels_used_for_final_metrics_only": True,
            "external_parameters_reselected": False,
        },
        "routing": {
            "prediction_exactly_pairwise_all_rows": True,
            "probability_exactly_pairwise_all_rows": True,
            "risk_monotone_not_below_pairwise": True,
            "inactive_risk_exactly_pairwise": True,
            "disabled_risk_exactly_pairwise_all_rows": True,
        },
        "reports": {
            "candidate": report(0.8),
            "embedded_pairwise": report(0.6),
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def aggregation(gain=0.1, lower=0.01, p_value=0.01):
    return {
        "metrics": {
            metric: {
                "oriented_mean_gain": gain,
                "label_block_bootstrap_95ci": [lower, 0.2],
                "wilcoxon_holm_p": p_value,
            }
            for metric in METRICS
        },
        "datasets": {
            dataset: {
                **{metric: gain for metric in METRICS},
                "known_macro_f1": 0.0,
            }
            for dataset in ("LSNM2024", "CICDDoS2019")
        },
        "known_macro_f1_mean_gain": 0.0,
    }


def gates():
    return {
        "known_macro_f1_mean_gain_minimum": -0.01,
        "known_macro_f1_each_dataset_gain_minimum": -0.02,
    }


def test_candidate_and_embedded_pairwise_reports_are_validated():
    value = metrics()
    assert candidate_report(value, "candidate")["unknown_auroc"] == 0.8
    assert (
        candidate_report(value, "embedded_pairwise")["unknown_auroc"]
        == 0.6
    )


def test_candidate_report_rejects_prediction_change():
    value = metrics()
    value["routing"]["prediction_exactly_pairwise_all_rows"] = False
    value["manifest_sha256"] = canonical_hash(value)
    with pytest.raises(ValueError, match="routing gate"):
        candidate_report(value, "candidate")


def test_comparator_gate_requires_all_four_effect_families():
    assert all(comparator_checks(aggregation(), gates()).values())
    failed = aggregation()
    failed["metrics"]["unknown_aupr"]["label_block_bootstrap_95ci"][0] = 0.0
    checks = comparator_checks(failed, gates())
    assert (
        checks[
            "all_four_label_block_bootstrap_95ci_lower_strictly_positive"
        ]
        is False
    )
