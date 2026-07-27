from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from audit_strict_v4_medaf_tabular_pilot import audit
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_medaf_tabular_pilot_protocol import (
    SCHEMA as PROTOCOL_SCHEMA,
    create_protocol,
)
from run_strict_v4_medaf_tabular_pilot import (
    SCHEMA as RUN_SCHEMA,
    replace_option,
    score_diagnostics,
)
from summarize_strict_v4_medaf_tabular_pilot import summarize


SUITES = {
    f"suite_{index}": [f"scenario_{index}_a", f"scenario_{index}_b"]
    for index in range(7)
}
METHODS = [
    "medaf_tabular_adapter",
    "mlp_energy",
    "opendetect",
]


def canonical(value: dict) -> dict:
    value["manifest_sha256"] = canonical_hash(value)
    return value


def design() -> dict:
    return canonical(
        {
            "schema_version": "strict_v4_medaf_tabular_design_v1",
            "candidate_result_count_at_freeze": 0,
            "manifest_note": "synthetic unit test",
            "pilot": {
                "training_seed": 383,
                "scenario_count": 14,
                "expected_reports": 42,
                "methods": METHODS,
                "scenario_selection": {"scenarios": SUITES},
                "expansion_gate": {
                    "complete_reports_required": 42,
                    "failed_runs_maximum": 0,
                    "split_fingerprint_match_required": True,
                    "unknown_or_test_selection_count_maximum": 0,
                    "risk_and_gate_non_degenerate_required": True,
                    "unknown_metrics_improved_vs_mlp_energy_minimum": 2,
                    "mean_oriented_unknown_gain_vs_mlp_energy_minimum": 0.0,
                    "mean_unknown_metric_rank_maximum": 2.0,
                    "known_macro_f1_mean_degradation_vs_opendetect_maximum": 0.03,
                    "nonnegative_suite_gain_vs_mlp_energy_minimum": 4,
                    "worst_suite_gain_vs_mlp_energy_minimum": -0.05,
                },
            },
            "mechanism": {
                "training_epochs": 150,
                "learning_rate_milestone": 130,
                "learning_rate": 0.1,
                "momentum": 0.9,
                "weight_decay": 1e-5,
                "gate_temperature": 100.0,
                "logit_temperature": 100.0,
            },
            "leakage_policy": {"known_acceptance_quantile": 0.95},
        }
    )


def protocol(value: dict) -> dict:
    return canonical(
        {
            "schema_version": PROTOCOL_SCHEMA,
            "execution_admitted": True,
            "design_manifest_sha256": value["manifest_sha256"],
            "implementation": {},
            "implementation_sha256": {},
        }
    )


def reports(method: str) -> dict:
    if method == "medaf_tabular_adapter":
        return {
            "medaf_tabular_adapter": {
                "known_macro_f1": 0.79,
                "unknown_auroc": 0.75,
                "unknown_aupr": 0.65,
                "unknown_fpr95": 0.35,
                "oscr": 0.55,
                "ece": 0.05,
            }
        }
    if method == "mlp_energy":
        return {
            "energy": {
                "known_macro_f1": 0.78,
                "unknown_auroc": 0.70,
                "unknown_aupr": 0.60,
                "unknown_fpr95": 0.40,
                "oscr": 0.50,
            }
        }
    return {
        "opendetect": {
            "known_macro_f1": 0.81,
            "unknown_auroc": 0.72,
            "unknown_aupr": 0.62,
            "unknown_fpr95": 0.38,
            "oscr": 0.52,
        }
    }


def write_run(
    root: Path,
    design_value: dict,
    protocol_value: dict,
    suite: str,
    scenario: str,
    method: str,
    *,
    split_suffix: str = "shared",
) -> None:
    directory = root / suite / scenario / method
    directory.mkdir(parents=True)
    split = {
        "seed": 383,
        "task": f"{suite}/{scenario}",
        "suffix": split_suffix,
    }
    metrics = {
        "reports": reports(method),
        "split_metadata": split,
        "selection_evidence": {
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
            "test_labels_used_for_final_metrics_only": True,
        },
    }
    metrics_path = directory / "metrics.json"
    metrics_path.write_text(json.dumps(metrics), encoding="utf-8")
    diagnostics = {}
    if method == "medaf_tabular_adapter":
        np.savez_compressed(
            directory / "scores.npz",
            validation_medaf_tabular=np.array([0.1, 0.2, 0.3]),
            test_medaf_tabular=np.array([0.15, 0.35, 0.55]),
            validation_gate_weights=np.array(
                [[0.2, 0.3, 0.5], [0.3, 0.3, 0.4], [0.4, 0.2, 0.4]]
            ),
            test_gate_weights=np.array(
                [[0.1, 0.4, 0.5], [0.5, 0.2, 0.3], [0.2, 0.5, 0.3]]
            ),
        )
        diagnostics = score_diagnostics(directory / "scores.npz")
    manifest = canonical(
        {
            "schema_version": RUN_SCHEMA,
            "state": "complete",
            "protocol_manifest_sha256": protocol_value[
                "manifest_sha256"
            ],
            "design_manifest_sha256": design_value["manifest_sha256"],
            "task": {
                "suite": suite,
                "scenario": scenario,
                "method": method,
            },
            "metrics_file_sha256": file_hash(metrics_path),
            "split_fingerprint": canonical_hash(split),
            "known_only_selection_verified": True,
            "score_diagnostics": diagnostics,
        }
    )
    (directory / "run_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )


def write_universe(root: Path, mismatch: bool = False) -> tuple[dict, dict]:
    design_value = design()
    protocol_value = protocol(design_value)
    for suite, scenarios in SUITES.items():
        for scenario in scenarios:
            for method in METHODS:
                suffix = (
                    "mismatch"
                    if mismatch
                    and suite == "suite_0"
                    and scenario == "scenario_0_a"
                    and method == "opendetect"
                    else "shared"
                )
                write_run(
                    root,
                    design_value,
                    protocol_value,
                    suite,
                    scenario,
                    method,
                    split_suffix=suffix,
                )
    return design_value, protocol_value


def test_protocol_freezes_zero_result_universe() -> None:
    design_value = design()
    comparative = canonical(
        {
            "schema_version": (
                "strict_v4_comparative_corruption_protocol_v2"
            ),
            "source_registry": [],
        }
    )
    sources = [
        {"suite": suite, "scenario": scenario}
        for suite, scenarios in SUITES.items()
        for scenario in scenarios
    ]
    value = create_protocol(
        design_value,
        comparative,
        design_path="results/design.json",
        design_file_sha256="a" * 64,
        comparative_file_sha256="b" * 64,
        source_records=sources,
        implementation={"runner": "runner.py"},
        implementation_sha256={"runner": "c" * 64},
        observed_counts={"metrics": 0, "summary": 0},
    )
    assert value["execution_admitted"] is True
    assert value["execution_plan"]["report_count"] == 42
    assert value["manifest_sha256"] == canonical_hash(value)


def test_runner_helpers_detect_non_degenerate_scores(tmp_path: Path) -> None:
    arguments = ["--seed", "137", "--output-dir", "old"]
    assert replace_option(arguments, "--seed", "383") == [
        "--seed",
        "383",
        "--output-dir",
        "old",
    ]
    write_run(
        tmp_path,
        design(),
        protocol(design()),
        "suite",
        "scenario",
        "medaf_tabular_adapter",
    )
    diagnostics = score_diagnostics(
        tmp_path
        / "suite"
        / "scenario"
        / "medaf_tabular_adapter"
        / "scores.npz"
    )
    assert diagnostics["risk_non_degenerate"] is True
    assert diagnostics["gate_non_degenerate"] is True


def test_summary_and_independent_audit_pass(tmp_path: Path) -> None:
    design_value, protocol_value = write_universe(tmp_path)
    summary = summarize(design_value, protocol_value, tmp_path)
    assert all(summary["expansion_checks"].values())
    assert summary["decision"]["expand_to_full102_confirmation"] is True
    result = audit(
        protocol_value,
        design_value,
        summary,
        tmp_path,
        tmp_path,
    )
    assert result["passes"] is True
    assert result["checks"]["summary_exactly_recomputed"] is True


def test_split_mismatch_blocks_expansion(tmp_path: Path) -> None:
    design_value, protocol_value = write_universe(
        tmp_path, mismatch=True
    )
    summary = summarize(design_value, protocol_value, tmp_path)
    assert (
        summary["expansion_checks"]["split_fingerprint_match"] is False
    )
    assert summary["decision"]["expand_to_full102_confirmation"] is False
