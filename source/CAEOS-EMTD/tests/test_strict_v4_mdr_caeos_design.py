from __future__ import annotations

import copy

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_caeos_design import (
    FAMILIES,
    FIXED_SEVERITY,
    create_design,
)


def fixture_payloads():
    registry = {
        f"suite_{index}": {
            "count": 2,
            "scenarios": [f"scenario_{index}_a", f"scenario_{index}_b"],
        }
        for index in range(7)
    }
    coverage = {
        "schema_version": "strict_v4_coverage_manifest_v2",
        "scenario_registry": registry,
    }
    coverage["manifest_sha256"] = canonical_hash(coverage)
    corruption = {
        "schema_version": "strict_v4_postselection_corruption_protocol_v1",
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "full102_confirmation": {
            "corruption_families": FAMILIES,
            "fixed_severity": FIXED_SEVERITY,
        },
        "confirmatory_graceful_degradation_gate": {
            "maximum_mean_degradation": {
                "known_macro_f1": 0.1,
                "unknown_auroc": 0.15,
                "unknown_aupr": 0.15,
                "unknown_fpr95": 0.2,
                "oscr": 0.15,
            }
        },
    }
    corruption["manifest_sha256"] = canonical_hash(corruption)
    suite_results = {}
    remaining_failures = 79
    for family in FAMILIES:
        suite_results[family] = {}
        for suite_index in range(7):
            metrics = {}
            for metric_index, metric in enumerate(
                (
                    "known_macro_f1",
                    "unknown_auroc",
                    "unknown_aupr",
                    "unknown_fpr95",
                    "oscr",
                )
            ):
                failed = remaining_failures > 0
                remaining_failures -= int(failed)
                metrics[metric] = {
                    "thresholded": True,
                    "passes": not failed,
                }
            metrics["ece"] = {"thresholded": False, "passes": None}
            suite_results[family][f"suite_{suite_index}"] = metrics
    audit = {
        "schema_version": "strict_v4_postselection_corruption_suite_gate_audit_v1",
        "validation": {"passes": True},
        "passes": False,
        "all_175_suite_threshold_checks_pass": False,
        "suite_results": suite_results,
        "manifest_sha256": "audit-manifest",
    }
    return coverage, corruption, audit


def test_design_freezes_fresh_seeds_and_zero_result_boundary() -> None:
    coverage, corruption, audit = fixture_payloads()
    design = create_design(
        coverage,
        corruption,
        audit,
        input_file_sha256={"a": "b"},
        implementation_sha256={"c": "d"},
        result_count_at_freeze=0,
    )
    assert design["pilot"]["scenario_count"] == 14
    assert design["pilot"]["expected_evaluations"] == 84
    assert design["reserved_confirmation"]["expected_evaluations"] == 1836
    assert design["execution_boundary"]["execution_admitted"] is False
    assert design["candidate_result_count_at_freeze"] == 0
    assert design["manifest_sha256"] == canonical_hash(design)


def test_design_rejects_results_or_positive_suite_audit() -> None:
    coverage, corruption, audit = fixture_payloads()
    with pytest.raises(ValueError, match="before candidate results"):
        create_design(
            coverage,
            corruption,
            audit,
            input_file_sha256={},
            implementation_sha256={},
            result_count_at_freeze=1,
        )
    positive = copy.deepcopy(audit)
    positive["passes"] = True
    with pytest.raises(ValueError, match="formal negative"):
        create_design(
            coverage,
            corruption,
            positive,
            input_file_sha256={},
            implementation_sha256={},
            result_count_at_freeze=0,
        )
