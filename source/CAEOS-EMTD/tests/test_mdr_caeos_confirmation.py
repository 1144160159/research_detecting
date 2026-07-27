from __future__ import annotations

import json
from pathlib import Path

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_caeos_confirmation_protocol import create_protocol
from run_strict_v4_mdr_caeos_confirmation import (
    validate_evaluation,
    validate_protocol,
)
from summarize_mdr_caeos_confirmation import final_selection, summarize


def canonical(value):
    value["manifest_sha256"] = canonical_hash(value)
    return value


def fixtures():
    scenarios = {}
    for suite_index in range(7):
        count = 15 if suite_index < 4 else 14
        scenarios[f"suite_{suite_index}"] = [
            f"scenario_{suite_index}_{index}" for index in range(count)
        ]
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
    pilot_protocol = canonical(
        {
            "schema_version": (
                "strict_v4_mdr_caeos_pilot_execution_protocol_v1"
            ),
            "design_manifest_sha256": design["manifest_sha256"],
        }
    )
    selection = canonical(
        {
            "schema_version": (
                "strict_v4_mdr_caeos_weight_selection_v1"
            ),
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
            "schema_version": "strict_v4_mdr_caeos_pilot_audit_v1",
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
    return (
        design,
        pilot_protocol,
        selection,
        summary,
        audit,
        comparative,
        sources,
    )


def make_protocol():
    (
        design,
        pilot_protocol,
        selection,
        summary,
        audit,
        comparative,
        sources,
    ) = fixtures()
    protocol = create_protocol(
        design,
        pilot_protocol,
        selection,
        summary,
        audit,
        comparative,
        input_file_sha256={"design": "design-file"},
        source_records=sources,
        implementation={"runner": "runner.py"},
        implementation_sha256={"runner": "runner-sha"},
        observed_counts={"captures": 0, "evaluations": 0},
    )
    return protocol


def report(f1, auroc, aupr, fpr95, oscr):
    return {
        "known_macro_f1": f1,
        "unknown_auroc": auroc,
        "unknown_aupr": aupr,
        "unknown_fpr95": fpr95,
        "oscr": oscr,
    }


def test_confirmation_protocol_requires_positive_pilot_and_zero_results():
    protocol = make_protocol()
    assert protocol["confirmation"]["task_count"] == 306
    assert protocol["confirmation"]["evaluation_count"] == 1836
    assert protocol["selected_augmentation_weight"] == 0.25
    assert protocol["manifest_sha256"] == canonical_hash(protocol)
    validate_protocol(protocol)

    values = list(fixtures())
    negative = dict(values[3])
    negative["decision"] = {"expand_to_full102_confirmation": False}
    negative["manifest_sha256"] = canonical_hash(negative)
    with pytest.raises(ValueError, match="positive canonical"):
        create_protocol(
            values[0],
            values[1],
            values[2],
            negative,
            values[4],
            values[5],
            input_file_sha256={},
            source_records=values[6],
            implementation={},
            implementation_sha256={},
            observed_counts={},
        )


def test_confirmation_summary_recomputes_full_universe(tmp_path: Path):
    protocol = make_protocol()
    protocol["statistics"]["bootstrap_replicates"] = 200
    protocol["manifest_sha256"] = canonical_hash(protocol)
    paths = []
    for task in protocol["confirmation"]["tasks"]:
        for condition in protocol["confirmation"]["conditions"]:
            if condition == "clean":
                pairwise = report(0.8, 0.8, 0.8, 0.1, 0.75)
                candidate = report(0.8, 0.8, 0.8, 0.1, 0.75)
            else:
                pairwise = report(0.6, 0.6, 0.6, 0.35, 0.55)
                candidate = report(0.78, 0.78, 0.78, 0.12, 0.73)
            value = canonical(
                {
                    "schema_version": (
                        "strict_v4_mdr_caeos_confirmation_evaluation_v1"
                    ),
                    "protocol_manifest_sha256": protocol[
                        "manifest_sha256"
                    ],
                    "suite": task["suite"],
                    "scenario": task["scenario"],
                    "training_seed": task["training_seed"],
                    "corruption_seed": task["corruption_seed"],
                    "condition": condition,
                    "capture": {"weight": 0.25},
                    "routing": {
                        "active_rate": 0.5,
                        "inactive_prediction_exactly_pairwise": True,
                        "inactive_risk_exactly_pairwise": True,
                        "inactive_probability_exactly_pairwise": True,
                        "unknown_or_test_labels_used": False,
                    },
                    "pairwise_report": pairwise,
                    "candidate_report": candidate,
                    "test_labels_used_for_final_evaluation_only": True,
                }
            )
            path = (
                tmp_path
                / task["suite"]
                / task["scenario"]
                / f"seed{task['training_seed']}"
                / condition
                / "evaluation.json"
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value), encoding="utf-8")
            paths.append(path)
    summary = summarize(protocol, paths)
    assert summary["validation"]["evaluation_count"] == 1836
    assert summary["validation"]["suite_threshold_check_count"] == 175
    assert sum(
        summary["suite_failure_counts"]["candidate"].values()
    ) == 0
    assert summary["primary_composite_advantage"]["lower_95"] > 0
    assert summary["decision"]["passes"] is True
    selection = final_selection(protocol, summary)
    assert selection["selected_algorithm"] == "mdr_caeos_v1"
    assert selection["comprehensive_sota_confirmed"] is False


def test_existing_evaluation_validation_rejects_identity_drift(
    tmp_path: Path,
):
    protocol = make_protocol()
    task = protocol["confirmation"]["tasks"][0]
    value = canonical(
        {
            "schema_version": (
                "strict_v4_mdr_caeos_confirmation_evaluation_v1"
            ),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "suite": task["suite"],
            "scenario": task["scenario"],
            "training_seed": task["training_seed"],
            "corruption_seed": task["corruption_seed"],
            "condition": "clean",
        }
    )
    path = tmp_path / "evaluation.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    assert validate_evaluation(path, protocol, task, "clean")
    value["condition"] = "field_missing"
    value["manifest_sha256"] = canonical_hash(value)
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="invalid existing"):
        validate_evaluation(path, protocol, task, "clean")


def test_confirmation_idle_gate_ignores_wait_only_watchers():
    path = (
        Path(__file__).parents[1]
        / "scripts"
        / "wait_and_run_strict_v4_mdr_caeos_confirmation.sh"
    )
    text = path.read_text(encoding="utf-8")
    assert "grep -v -E 'wait_and_|pgrep -af'" in text
