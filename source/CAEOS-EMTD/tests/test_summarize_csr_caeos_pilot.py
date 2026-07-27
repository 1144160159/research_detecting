from __future__ import annotations

import json
from pathlib import Path

import pytest

from audit_csr_caeos_pilot import audit
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_caeos_design import FAMILIES
from summarize_csr_caeos_pilot import (
    clean_admission,
    clopper_pearson_upper,
    summarize,
)


def test_clopper_upper_is_finite_and_conservative() -> None:
    assert 0.0 < clopper_pearson_upper(0, 1000) < 0.01
    assert clopper_pearson_upper(1, 1000) > 0.001
    assert clopper_pearson_upper(1000, 1000) == 1.0


def test_clopper_upper_rejects_invalid_counts() -> None:
    with pytest.raises(ValueError):
        clopper_pearson_upper(2, 1)


def make_design() -> dict:
    scenarios = {
        f"suite_{index}": ["scenario_a", "scenario_b"]
        for index in range(7)
    }
    value = {
        "schema_version": "strict_v4_csr_caeos_design_v3",
        "development": {
            "scenarios": scenarios,
            "conditions": ["clean", *FAMILIES],
            "clean_gate": {
                "probability_max_absolute_difference": 0.0,
                "inactive_nonmissing_risk_max_absolute_difference": 1e-12,
                "safety_nonmissing_activation_rate_one_sided_95pct_upper_maximum": 0.01,
            },
            "robustness_gate": {
                "suite_nonnegative_count_minimum": 5,
                "each_family_metric_regression_maximum": 0.02,
            },
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def test_clean_admission_and_positive_summary(tmp_path: Path) -> None:
    design = make_design()
    capture_paths = []
    for suite, scenarios in design["development"]["scenarios"].items():
        for scenario in scenarios:
            path = tmp_path / "captures" / suite / scenario / "capture_manifest.json"
            path.parent.mkdir(parents=True)
            value = {
                "schema_version": "strict_v4_csr_caeos_runtime_capture_v1",
                "state": "complete",
                "algorithm": "csr_caeos_v1",
                "task": {"suite": suite, "scenario": scenario},
                "roundtrip": {"passes": True},
                "test_effect_metrics_computed": False,
                "safety_profile": {
                    "schema_version": "strict_v4_csr_known_validation_safety_profile_v1",
                    "partition": {"safety_count": 1000},
                    "test_arrays_read": [],
                    "unknown_or_test_labels_used_for_calibration": False,
                    "missing_active_count": 0,
                    "active_count": 0,
                    "prediction_array_equal_pairwise": True,
                    "probability_max_absolute_difference": 0.0,
                    "inactive_risk_max_absolute_difference": 0.0,
                    "clean_delta": 0.0,
                },
            }
            path.write_text(json.dumps(value), encoding="utf-8")
            capture_paths.append(path)
    admission = clean_admission(design, capture_paths)
    assert admission["passes"] is True

    evaluation_paths = []
    for suite, scenarios in design["development"]["scenarios"].items():
        for scenario in scenarios:
            for condition in design["development"]["conditions"]:
                pairwise = {
                    "known_macro_f1": 0.8,
                    "unknown_auroc": 0.7,
                    "unknown_aupr": 0.6,
                    "unknown_fpr95": 0.4,
                    "oscr": 0.5,
                }
                candidate = dict(pairwise)
                if condition != "clean":
                    candidate.update(
                        {
                            "unknown_auroc": 0.71,
                            "unknown_aupr": 0.61,
                            "unknown_fpr95": 0.39,
                            "oscr": 0.51,
                        }
                    )
                value = {
                    "schema_version": "strict_v4_csr_caeos_pilot_evaluation_v1",
                    "state": "complete",
                    "design_manifest_sha256": design["manifest_sha256"],
                    "suite": suite,
                    "scenario": scenario,
                    "condition": condition,
                    "routing": {
                        "prediction_exactly_pairwise_all_rows": True,
                        "probability_exactly_pairwise_all_rows": True,
                        "risk_monotone_not_below_pairwise": True,
                        "inactive_risk_exactly_pairwise": True,
                        "unknown_or_test_labels_used": False,
                    },
                    "candidate_report": candidate,
                    "pairwise_report": pairwise,
                }
                value["manifest_sha256"] = canonical_hash(value)
                path = (
                    tmp_path
                    / "evaluations"
                    / suite
                    / scenario
                    / condition
                    / "evaluation.json"
                )
                path.parent.mkdir(parents=True)
                path.write_text(json.dumps(value), encoding="utf-8")
                evaluation_paths.append(path)
    summary = summarize(design, admission, evaluation_paths)
    assert summary["passes"] is True
    assert summary["expand_to_full102"] is True
    audited = audit(
        design,
        admission,
        summary,
        capture_paths,
        evaluation_paths,
        implementation_file_sha256={"test": "a" * 64},
    )
    assert audited["passes"] is True
    assert audited["scientific_effect_gate_passes"] is True
