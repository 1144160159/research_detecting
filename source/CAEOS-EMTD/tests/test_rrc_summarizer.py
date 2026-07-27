from __future__ import annotations

from pathlib import Path

import summarize_rrc_csr_confirmation as summary
import audit_rrc_csr_confirmation as auditor
from create_strict_v4_external_confirmation_protocol import canonical_hash


def canonical(value):
    value["manifest_sha256"] = canonical_hash(value)
    return value


def fixtures(enabled_count: int):
    conditions = list(summary.CONDITIONS)
    scenarios = [
        (f"suite{index % 7}", f"scenario{index}") for index in range(83)
    ]
    tasks = [
        {
            "suite": suite,
            "scenario": scenario,
            "training_seed": training_seed,
            "corruption_seed": corruption_seed,
        }
        for suite, scenario in scenarios
        for training_seed, corruption_seed in zip(
            [701, 709, 719], [727, 733, 739]
        )
    ]
    protocol = canonical(
        {
            "schema_version": "strict_v4_rrc_csr_execution_protocol_v1",
            "execution_admitted": True,
            "algorithm": "rrc_csr_caeos_v1",
            "conditions": conditions,
            "training_seeds": [701, 709, 719],
            "corruption_seeds": [727, 733, 739],
            "tasks": tasks,
            "effect_gate": {
                "primary_enabled_scenario_count_minimum": 18,
                "primary_enabled_suite_count_minimum": 4,
                "suite_nonnegative_count_minimum_each_metric": 5,
                "each_family_metric_regression_maximum": 0.02,
            },
            "aggregation_protocol": {
                "bootstrap_replicates": 100,
                "bootstrap_seed": 20260727,
            },
        }
    )
    values = {}
    certificate_paths = []
    capture_paths = []
    evaluation_paths = []
    certificates = {}
    for index, (suite, scenario) in enumerate(scenarios):
        path = Path(f"certificate_{index}.json")
        certificate = canonical(
            {
                "schema_version": (
                    "strict_v4_rrc_csr_scenario_certificate_v1"
                ),
                "suite": suite,
                "scenario": scenario,
                "routing_enabled": index < enabled_count,
            }
        )
        values[path] = certificate
        certificate_paths.append(path)
        certificates[(suite, scenario)] = certificate
    pairwise = {metric: 0.5 for metric in summary.DIRECTED_METRICS}
    candidate = dict(pairwise)
    for metric in summary.DIRECTED_METRICS:
        candidate[metric] = 0.49 if metric == "unknown_fpr95" else 0.51
    for task_index, task in enumerate(tasks):
        capture_path = Path(f"capture_{task_index}.json")
        values[capture_path] = {
            "task": {
                "suite": task["suite"],
                "scenario": task["scenario"],
            },
            "training_seed": task["training_seed"],
            "corruption_seed": task["corruption_seed"],
            "scenario_certificate_manifest_sha256": certificates[
                (task["suite"], task["scenario"])
            ]["manifest_sha256"],
            "routing_enabled": certificates[
                (task["suite"], task["scenario"])
            ]["routing_enabled"],
        }
        capture_paths.append(capture_path)
        for condition in conditions:
            evaluation_path = Path(
                f"evaluation_{task_index}_{condition}.json"
            )
            values[evaluation_path] = {
                "suite": task["suite"],
                "scenario": task["scenario"],
                "training_seed": task["training_seed"],
                "corruption_seed": task["corruption_seed"],
                "condition": condition,
                "certificate_routing_enabled": certificates[
                    (task["suite"], task["scenario"])
                ]["routing_enabled"],
                "candidate_report": candidate,
                "pairwise_report": pairwise,
                "routing": {
                    "prediction_exactly_pairwise_all_rows": True,
                    "probability_exactly_pairwise_all_rows": True,
                    "risk_monotone_not_below_pairwise": True,
                    "inactive_risk_exactly_pairwise": True,
                    "disabled_risk_exactly_pairwise_all_rows": True,
                    "unknown_or_test_labels_used": False,
                },
                "test_labels_used_for_final_evaluation_only": True,
            }
            evaluation_paths.append(evaluation_path)
    pipeline = canonical(
        {
            "schema_version": (
                "strict_v4_rrc_csr_capture_pipeline_inventory_v1"
            ),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "counts": {
                "base_csr_captures": 249,
                "scenario_certificates": 83,
                "rrc_runtime_captures": 249,
                "evaluations": 1494,
            },
            "inventories": {
                "scenario_certificates": [
                    {"path": str(path), "file_sha256": "h"}
                    for path in certificate_paths
                ],
                "rrc_runtime_captures": [
                    {"path": str(path), "file_sha256": "h"}
                    for path in capture_paths
                ],
                "evaluations": [
                    {"path": str(path), "file_sha256": "h"}
                    for path in evaluation_paths
                ],
            },
        }
    )
    return (
        protocol,
        pipeline,
        values,
        certificate_paths,
        capture_paths,
        evaluation_paths,
    )


def run_summary(monkeypatch, enabled_count: int):
    protocol, pipeline, values, certificates, captures, evaluations = (
        fixtures(enabled_count)
    )
    monkeypatch.setattr(summary, "load_json", lambda path: values[path])
    monkeypatch.setattr(
        summary, "validate_certificate", lambda *args, **kwargs: True
    )
    monkeypatch.setattr(
        summary, "validate_rrc_capture", lambda *args, **kwargs: True
    )
    monkeypatch.setattr(
        summary, "validate_evaluation", lambda *args, **kwargs: True
    )
    return summary.summarize(
        protocol, certificates, captures, evaluations, pipeline
    )


def test_suite_balanced_summary_passes_all_frozen_gates(monkeypatch):
    value = run_summary(monkeypatch, enabled_count=83)
    assert value["passes"] is True
    assert value["selection"] == "rrc_csr_caeos_v1"
    assert value["observed_counts"]["evaluations"] == 1494
    assert all(value["effect_gate_checks"].values())
    assert (
        value["metric_summary"]["unknown_auroc"][
            "overall_equal_suite_mean"
        ]
        > 0.0
    )


def test_summary_rejects_insufficient_certificate_coverage(monkeypatch):
    value = run_summary(monkeypatch, enabled_count=17)
    assert value["passes"] is False
    assert value["selection"] == "caeos_pairwise"
    assert (
        value["effect_gate_checks"]["enabled_scenario_count_minimum"]
        is False
    )


def run_audit(monkeypatch, enabled_count: int):
    protocol, pipeline, values, certificates, captures, evaluations = (
        fixtures(enabled_count)
    )
    monkeypatch.setattr(summary, "load_json", lambda path: values[path])
    monkeypatch.setattr(
        summary, "validate_certificate", lambda *args, **kwargs: True
    )
    monkeypatch.setattr(
        summary, "validate_rrc_capture", lambda *args, **kwargs: True
    )
    monkeypatch.setattr(
        summary, "validate_evaluation", lambda *args, **kwargs: True
    )
    summary_value = summary.summarize(
        protocol, certificates, captures, evaluations, pipeline
    )
    monkeypatch.setattr(auditor, "load_json", lambda path: values[path])
    monkeypatch.setattr(
        auditor, "validate_certificate", lambda *args, **kwargs: True
    )
    monkeypatch.setattr(
        auditor, "validate_rrc_capture", lambda *args, **kwargs: True
    )
    monkeypatch.setattr(
        auditor, "validate_evaluation", lambda *args, **kwargs: True
    )
    monkeypatch.setattr(auditor, "file_hash", lambda path: "h")
    return auditor.audit(
        protocol,
        summary_value,
        pipeline,
        certificates,
        captures,
        evaluations,
    )


def test_independent_audit_accepts_positive_summary(monkeypatch):
    value = run_audit(monkeypatch, enabled_count=83)
    assert value["integrity_passes"] is True
    assert value["effect_gate_passes"] is True
    assert value["passes"] is True


def test_independent_audit_preserves_valid_scientific_negative(monkeypatch):
    value = run_audit(monkeypatch, enabled_count=17)
    assert value["integrity_passes"] is True
    assert value["effect_gate_passes"] is False
    assert value["passes"] is False
    assert value["selection"] == "caeos_pairwise"
