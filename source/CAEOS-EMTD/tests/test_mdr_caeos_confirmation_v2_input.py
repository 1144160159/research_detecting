from __future__ import annotations

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_caeos_confirmation_protocol_v2 import (
    create_protocol,
)
from run_strict_v4_mdr_caeos_confirmation import validate_protocol


def canonical(value):
    value["manifest_sha256"] = canonical_hash(value)
    return value


def inputs():
    scenarios = {
        f"suite_{index}": [
            f"scenario_{index}_{offset}"
            for offset in range(15 if index < 4 else 14)
        ]
        for index in range(7)
    }
    design = canonical(
        {
            "schema_version": "strict_v4_mdr_caeos_design_v2",
            "algorithm": "mdr_caeos_v1",
            "input_manifest_sha256": {"coverage": "coverage-sha"},
            "mechanism": {
                "training_sample_fraction": 0.25,
                "family_severities": {
                    "modality_missing": 1.0,
                    "field_missing": 0.3,
                    "row_missing": 0.3,
                    "feature_shuffle": 0.3,
                    "gaussian_drift": 0.5,
                },
                "health_gate": {"quantile": 0.99},
            },
            "pilot": {
                "expansion_gate": {
                    "clean_known_macro_f1_mean_degradation_maximum": 0.01,
                    "clean_known_macro_f1_worst_degradation_maximum": 0.03,
                }
            },
            "reserved_confirmation": {
                "training_seeds": [347, 349, 353],
                "corruption_seeds": [359, 367, 373],
                "conditions": [
                    "clean",
                    "modality_missing",
                    "field_missing",
                    "row_missing",
                    "feature_shuffle",
                    "gaussian_drift",
                ],
            },
            "thresholds": {
                "known_macro_f1": 0.1,
                "unknown_auroc": 0.15,
                "unknown_aupr": 0.15,
                "unknown_fpr95": 0.2,
                "oscr": 0.15,
            },
        }
    )
    pilot = canonical(
        {
            "schema_version": (
                "strict_v4_mdr_caeos_pilot_execution_protocol_v2"
            ),
            "design_manifest_sha256": design["manifest_sha256"],
        }
    )
    selection = canonical(
        {
            "schema_version": "strict_v4_mdr_caeos_weight_selection_v1",
            "design_manifest_sha256": design["manifest_sha256"],
            "selected_weight": 0.25,
            "unknown_or_test_labels_used": False,
        }
    )
    summary = canonical(
        {
            "schema_version": "strict_v4_mdr_caeos_pilot_summary_v1",
            "design_manifest_sha256": design["manifest_sha256"],
            "weight_selection_manifest_sha256": selection[
                "manifest_sha256"
            ],
            "decision": {"expand_to_full102_confirmation": True},
        }
    )
    audit = canonical(
        {
            "schema_version": "strict_v4_mdr_caeos_pilot_audit_v2",
            "passes": True,
            "summary_manifest_sha256": summary["manifest_sha256"],
            "selection_manifest_sha256": selection["manifest_sha256"],
        }
    )
    comparative = canonical(
        {
            "schema_version": (
                "strict_v4_comparative_corruption_protocol_v2"
            ),
            "coverage_manifest_sha256": "coverage-sha",
        }
    )
    sources = [
        {"suite": suite, "scenario": scenario}
        for suite, values in scenarios.items()
        for scenario in values
    ]
    return design, pilot, selection, summary, audit, comparative, sources


def test_confirmation_accepts_positive_pilot_v2_without_changing_scope():
    values = inputs()
    protocol = create_protocol(
        *values[:6],
        input_file_sha256={"design": "design-file"},
        source_records=values[6],
        implementation={"runner": "runner.py"},
        implementation_sha256={"runner": "runner-sha"},
        observed_counts={"captures": 0, "evaluations": 0},
    )
    validate_protocol(protocol)
    assert protocol["confirmation"]["task_count"] == 306
    assert protocol["confirmation"]["evaluation_count"] == 1836
    assert protocol["selected_augmentation_weight"] == 0.25


def test_confirmation_rejects_pilot_v1_on_v2_input_path():
    values = list(inputs())
    values[1]["schema_version"] = (
        "strict_v4_mdr_caeos_pilot_execution_protocol_v1"
    )
    values[1]["manifest_sha256"] = canonical_hash(values[1])
    with pytest.raises(ValueError, match="pilot v2"):
        create_protocol(
            *values[:6],
            input_file_sha256={"design": "design-file"},
            source_records=values[6],
            implementation={"runner": "runner.py"},
            implementation_sha256={"runner": "runner-sha"},
            observed_counts={"captures": 0, "evaluations": 0},
        )
