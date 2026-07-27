from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np
import pytest

from caeos.mdr_runtime import MDRRuntime
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_caeos_design_v2 import revise
from create_strict_v4_mdr_caeos_pilot_execution_protocol import (
    create_protocol,
)
from evaluate_mdr_caeos_runtime import selected_modality
from select_mdr_caeos_weight import select
from summarize_mdr_caeos_pilot import summarize
from train_mdr_caeos_open_set import ConfiguredStructuredRobustClassifier


def design_fixture():
    scenarios = {
        f"suite_{index}": [
            f"scenario_{index}_a",
            f"scenario_{index}_b",
        ]
        for index in range(7)
    }
    value = {
        "schema_version": "strict_v4_mdr_caeos_design_v2",
        "algorithm": "mdr_caeos_v1",
        "input_manifest_sha256": {"coverage": "coverage-sha"},
        "mechanism": {
            "training_augmentation_weight_grid": [0.125, 0.25, 0.5],
            "training_sample_fraction": 0.25,
            "health_gate": {"quantile": 0.99},
        },
        "pilot": {
            "training_seed": 331,
            "corruption_seed": 337,
            "scenarios": scenarios,
            "scenario_count": 14,
            "conditions": [
                "clean",
                "modality_missing",
                "field_missing",
                "row_missing",
                "feature_shuffle",
                "gaussian_drift",
            ],
            "expected_evaluations": 84,
            "expansion_gate": {
                "clean_known_macro_f1_mean_degradation_maximum": 0.01,
                "clean_known_macro_f1_worst_degradation_maximum": 0.03,
                "failed_suite_checks_maximum": 50,
                "no_family_metric_worse_than_pairwise_by_more_than": 0.02,
            },
        },
        "thresholds": {
            "known_macro_f1": 0.1,
            "unknown_auroc": 0.15,
            "unknown_aupr": 0.15,
            "unknown_fpr95": 0.2,
            "oscr": 0.15,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def capture_manifests(design):
    values = []
    hashes = []
    for suite, scenarios in design["pilot"]["scenarios"].items():
        for scenario in scenarios:
            for weight in (0.125, 0.25, 0.5):
                objective = 0.8 - abs(weight - 0.25)
                values.append(
                    {
                        "schema_version": (
                            "strict_v4_mdr_caeos_runtime_capture_v1"
                        ),
                        "state": "complete",
                        "task": {"suite": suite, "scenario": scenario},
                        "weight": weight,
                        "roundtrip": {"passes": True},
                        "known_validation_profile": {
                            "schema_version": (
                                "strict_v4_mdr_known_validation_profile_v1"
                            ),
                            "record_count": 15,
                            "unknown_or_test_labels_used": False,
                            "clean_delta": -0.001,
                            "corrupted_minimax_macro_f1": objective,
                        },
                    }
                )
                hashes.append(f"sha-{suite}-{scenario}-{weight}")
    return values, hashes


def test_design_v2_revision_is_zero_result_only_and_formula_preserving() -> None:
    v1 = design_fixture()
    v1["schema_version"] = "strict_v4_mdr_caeos_design_v1"
    v1["manifest_sha256"] = canonical_hash(v1)
    v2 = revise(
        v1,
        v1_file_sha256="v1-file-sha",
        implementation_sha256={"runtime": "runtime-sha"},
        result_count_at_revision=0,
    )
    assert v2["schema_version"] == "strict_v4_mdr_caeos_design_v2"
    assert v2["algorithm"] == v1["algorithm"]
    assert v2["mechanism"] == v1["mechanism"]
    assert v2["pilot"] == v1["pilot"]
    assert v2["thresholds"] == v1["thresholds"]
    assert v2["revision"]["algorithm_formula_changed"] is False
    assert v2["manifest_sha256"] == canonical_hash(v2)
    with pytest.raises(ValueError, match="zero candidate results"):
        revise(
            v1,
            v1_file_sha256="v1-file-sha",
            implementation_sha256={},
            result_count_at_revision=1,
        )


def test_runtime_corruption_is_deterministic_and_configured_class_pickles() -> None:
    runtime = MDRRuntime(
        clean_runtime=None,
        robust_runtime=None,
        health_calibration=None,
        missing_fraction_thresholds=np.asarray([0.1, 0.1]),
        training_feature_scales=[
            np.ones(3, dtype=np.float64),
            np.ones(2, dtype=np.float64),
        ],
        clean_threshold=0.5,
        augmentation_weight=0.25,
        training_seed=331,
        augmentation_seed=331,
    )
    views = [np.arange(30.0).reshape(10, 3), np.ones((10, 2))]
    first = runtime.corrupt(
        views,
        family="gaussian_drift",
        modality=0,
        severity=0.5,
        seed=337,
    )
    second = runtime.corrupt(
        views,
        family="gaussian_drift",
        modality=0,
        severity=0.5,
        seed=337,
    )
    np.testing.assert_array_equal(first[0], second[0])
    np.testing.assert_array_equal(first[1], views[1])
    assert "<locals>" not in ConfiguredStructuredRobustClassifier.__qualname__
    pickle.loads(pickle.dumps(ConfiguredStructuredRobustClassifier(estimators=2)))


def test_weight_selection_uses_all_42_captures() -> None:
    design = design_fixture()
    manifests, hashes = capture_manifests(design)
    result = select(design, manifests, hashes)
    assert result["capture_manifest_count"] == 42
    assert result["selected_weight"] == 0.25
    assert result["unknown_or_test_labels_used"] is False
    assert result["manifest_sha256"] == canonical_hash(result)


def test_execution_protocol_requires_zero_outputs_and_full_source_registry() -> None:
    design = design_fixture()
    comparative = {
        "schema_version": "strict_v4_comparative_corruption_protocol_v2"
    }
    comparative["manifest_sha256"] = canonical_hash(comparative)
    sources = [
        {"suite": suite, "scenario": scenario}
        for suite, scenarios in design["pilot"]["scenarios"].items()
        for scenario in scenarios
    ]
    value = create_protocol(
        design,
        comparative,
        design_path="results/design.json",
        design_file_sha256="design-file",
        comparative_file_sha256="comparative-file",
        source_records=sources,
        implementation={"runner": "runner.py"},
        implementation_sha256={"runner": "runner-sha"},
        observed_counts={"evaluations": 0},
    )
    assert value["execution_plan"]["weight_capture_count"] == 42
    assert value["execution_plan"]["fit_count"] == 84
    assert value["execution_plan"]["pilot_evaluation_count"] == 84
    assert value["manifest_sha256"] == canonical_hash(value)


def make_report(f1, auroc, aupr, fpr95, oscr):
    return {
        "known_macro_f1": f1,
        "unknown_auroc": auroc,
        "unknown_aupr": aupr,
        "unknown_fpr95": fpr95,
        "oscr": oscr,
    }


def test_summary_recomputes_84_evaluations_and_positive_gate(tmp_path: Path) -> None:
    design = design_fixture()
    manifests, hashes = capture_manifests(design)
    selection = select(design, manifests, hashes)
    paths = []
    for suite, scenarios in design["pilot"]["scenarios"].items():
        for scenario in scenarios:
            for condition in design["pilot"]["conditions"]:
                if condition == "clean":
                    pairwise = make_report(0.8, 0.8, 0.8, 0.1, 0.75)
                    candidate = make_report(0.8, 0.8, 0.8, 0.1, 0.75)
                else:
                    pairwise = make_report(0.58, 0.58, 0.58, 0.35, 0.53)
                    candidate = make_report(0.75, 0.75, 0.75, 0.15, 0.70)
                value = {
                    "schema_version": (
                        "strict_v4_mdr_caeos_pilot_evaluation_v1"
                    ),
                    "design_manifest_sha256": design["manifest_sha256"],
                    "suite": suite,
                    "scenario": scenario,
                    "condition": condition,
                    "capture": {"weight": selection["selected_weight"]},
                    "routing": {"unknown_or_test_labels_used": False},
                    "pairwise_report": pairwise,
                    "candidate_report": candidate,
                }
                value["manifest_sha256"] = canonical_hash(value)
                path = (
                    tmp_path
                    / suite
                    / scenario
                    / condition
                    / "evaluation.json"
                )
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(value), encoding="utf-8")
                paths.append(path)
    summary = summarize(design, selection, paths)
    assert summary["validation"]["evaluation_count"] == 84
    assert summary["validation"]["suite_threshold_check_count"] == 175
    assert sum(summary["suite_failure_counts"]["candidate"].values()) == 0
    assert summary["decision"]["expand_to_full102_confirmation"] is True
    assert summary["manifest_sha256"] == canonical_hash(summary)


def test_modality_selection_is_deterministic() -> None:
    first = selected_modality(
        "coverage", "suite", "scenario", "gaussian_drift", 3
    )
    second = selected_modality(
        "coverage", "suite", "scenario", "gaussian_drift", 3
    )
    assert first == second
    assert 0 <= first < 3
