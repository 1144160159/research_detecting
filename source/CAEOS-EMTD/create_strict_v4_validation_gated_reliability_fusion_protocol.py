from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


SELECTION_SALT = "strict-v4-validation-gated-reliability-fusion-seed307-v1"
TRAINING_SEED = 307


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def selected_scenarios(coverage: dict[str, Any], excluded: set[tuple[str, str]]) -> dict[str, list[str]]:
    selected = {}
    for suite, entry in sorted(coverage["scenario_registry"].items()):
        ranked = []
        for scenario in entry["scenarios"]:
            if (suite, scenario) in excluded:
                continue
            digest = hashlib.sha256(
                f"{SELECTION_SALT}|{suite}|{scenario}".encode("utf-8")
            ).hexdigest()
            ranked.append((digest, scenario))
        if len(ranked) < 2:
            raise ValueError(f"fewer than two fresh scenarios for {suite}")
        selected[suite] = [scenario for _, scenario in sorted(ranked)[:2]]
    if len(selected) != 7 or sum(map(len, selected.values())) != 14:
        raise ValueError("validation-gated pilot requires two scenarios per seven suites")
    return selected


def command_value(command: list[str], flag: str) -> str:
    index = command.index(flag)
    return command[index + 1]


def input_manifest(
    project_root: Path,
    coverage: dict[str, Any],
    selected: dict[str, list[str]],
) -> list[dict[str, Any]]:
    records = []
    source_root = project_root / "runs/strict_v4_full103_pairwise_caeos_seed7"
    for suite, scenarios in selected.items():
        for scenario in scenarios:
            provenance_path = source_root / suite / f"{scenario}_seed7" / "provenance.json"
            provenance = load(provenance_path)
            command = provenance["command"]
            csv_path = Path(command_value(command, "--csv"))
            config_path = project_root / command_value(command, "--config")
            if not csv_path.is_file() or not config_path.is_file():
                raise FileNotFoundError(f"source input missing for {suite}/{scenario}")
            if file_hash(csv_path) != coverage["cache_artifacts"][suite]["sha256"]:
                raise ValueError(f"coverage cache SHA mismatch for {suite}")
            records.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "source_seed": 7,
                    "training_seed": TRAINING_SEED,
                    "source_provenance": str(provenance_path.relative_to(project_root)).replace("\\", "/"),
                    "source_provenance_sha256": file_hash(provenance_path),
                    "unknown_classes": command_value(command, "--unknown-classes"),
                    "csv": str(csv_path),
                    "csv_sha256": file_hash(csv_path),
                    "config": str(config_path.relative_to(project_root)).replace("\\", "/"),
                    "config_sha256": file_hash(config_path),
                    "source_parameter_fingerprint": provenance["parameter_fingerprint"],
                }
            )
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--fixed-protocol", type=Path, required=True)
    parser.add_argument("--fixed-analysis", type=Path, required=True)
    parser.add_argument("--reference-run-root", type=Path, required=True)
    parser.add_argument("--candidate-run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    coverage = load(args.coverage)
    fixed_protocol = load(args.fixed_protocol)
    fixed_analysis = load(args.fixed_analysis)
    if coverage.get("manifest_sha256") != canonical_hash(coverage):
        raise ValueError("coverage manifest SHA mismatch")
    if fixed_protocol.get("manifest_sha256") != canonical_hash(fixed_protocol):
        raise ValueError("fixed reliability protocol SHA mismatch")
    if (
        fixed_analysis.get("protocol_manifest_sha256") != fixed_protocol["manifest_sha256"]
        or fixed_analysis.get("passes") is not False
        or fixed_analysis.get("decision")
        != "retain_caeos_pairwise_and_reject_class_conditional_reliability_fusion"
    ):
        raise ValueError("fixed reliability-fusion negative analysis is invalid")
    reference_metrics = len(list(args.reference_run_root.rglob("metrics.json"))) if args.reference_run_root.exists() else 0
    candidate_metrics = len(list(args.candidate_run_root.rglob("metrics.json"))) if args.candidate_run_root.exists() else 0
    if reference_metrics != 0 or candidate_metrics != 0:
        raise ValueError("validation-gated protocol must freeze before paired metrics")
    excluded = {
        (record["suite"], record["scenario"])
        for record in fixed_protocol["pilot"]["inputs"]
    }
    selected = selected_scenarios(coverage, excluded)
    names = (
        "train_hybrid_open_set.py",
        "caeos/class_conditional_reliability_fusion.py",
        "caeos/validation_gated_reliability_fusion.py",
        "evaluate_validation_gated_reliability_fusion.py",
        "create_strict_v4_validation_gated_reliability_fusion_protocol.py",
        "run_strict_v4_validation_gated_reliability_fusion_matrix.py",
        "summarize_strict_v4_validation_gated_reliability_fusion.py",
        "scripts/run_strict_v4_validation_gated_reliability_fusion_pilot.sh",
        "scripts/wait_and_run_strict_v4_validation_gated_reliability_fusion_pilot.sh",
    )
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_validation_gated_reliability_fusion_protocol_v1",
        "status": "frozen_after_fixed_reliability_negative_before_seed307_paired_metrics",
        "paper_incumbent": "caeos_pairwise",
        "candidate": {
            "name": "caeos_validation_gated_class_conditional_reliability_fusion",
            "base_formula": "same_empirical_bayes_class_conditional_reliability_and_0.25_risk_blend_as_fixed_candidate",
            "scenario_gate": (
                "enable only if known-validation Macro-F1 gain>=-0.002, correct-risk increase<=0.01, "
                "error-detection AUROC gain>=0, error/correct separation gain>=0, and at least one proxy gain>=0.005"
            ),
            "fallback": "exact_paired_pairwise_probability_risk_and_threshold_inputs",
            "changes_training_objective": False,
            "changes_evidence_reliability_and_fusion": True,
        },
        "paired_reference": {
            "training_seed": TRAINING_SEED,
            "sample_cache_seed": 7,
            "trainer": "current_active_train_hybrid_open_set.py",
            "command_policy": (
                "copy each frozen seed7 provenance command and replace only seed, output-dir, "
                "and risk-policy-name; candidate and reference share the resulting evidence package"
            ),
            "historical_pairwise_metrics_reused": False,
            "trainer_drift_isolated_by_within_run_pairing": True,
        },
        "known_only_parameters": {
            "empirical_bayes_shrinkage": 20.0,
            "minimum_reliability": 0.05,
            "risk_blend": 0.25,
            "known_rejection_quantile": 0.95,
            "minimum_f1_gain": -0.002,
            "maximum_correct_risk_increase": 0.01,
            "minimum_auc_gain": 0.0,
            "minimum_separation_gain": 0.0,
            "minimum_strict_proxy_gain": 0.005,
            "unknown_or_test_labels_used_for_reliability_gate_threshold_or_prediction": False,
        },
        "motivation": {
            "fixed_protocol_manifest_sha256": fixed_protocol["manifest_sha256"],
            "fixed_protocol_file_sha256": file_hash(args.fixed_protocol),
            "fixed_analysis_file_sha256": file_hash(args.fixed_analysis),
            "fixed_overall_oriented_gains": fixed_analysis["overall_equal_suite_oriented_gains"],
            "fixed_fully_nonregressing_suite_count": fixed_analysis["fully_nonregressing_suite_count"],
            "interpretation": "retain positive reliability signal while making activation an independently testable known-only decision",
        },
        "pilot": {
            "scenario_count": 14,
            "suite_count": 7,
            "scenarios_per_suite": 2,
            "selection_salt": SELECTION_SALT,
            "selection_uses_metric_values": False,
            "scenario_overlap_with_fixed_seed7_pilot": 0,
            "inputs": input_manifest(project_root, coverage, selected),
            "aggregation": "mean_within_suite_then_equal_mean_across_seven_suites",
            "gate": {
                "minimum_enabled_scenarios": 4,
                "all_four_equal_suite_oriented_means_strictly_positive": True,
                "minimum_suite_metric_gain": -0.005,
                "minimum_fully_nonregressing_suite_count": 6,
                "minimum_positive_scenario_four_metric_mean_count": 9,
                "minimum_mean_known_macro_f1_gain": -0.002,
                "minimum_scenario_known_macro_f1_gain": -0.01,
                "maximum_temperature_reconstruction_error": 1e-10,
                "exact_fallback_for_every_disabled_scenario": True,
            },
        },
        "reserved_confirmation": {
            "seeds": [311, 313],
            "scenario_scope": "all_102_scenarios_across_seven_suites",
            "freeze_only_after_positive_seed307_pilot": True,
        },
        "claim_boundary": {
            "seed307_pilot_success_does_not_establish_sota": True,
            "same_seed7_sample_cache_limits_data_resampling_claim": True,
            "replacement_requires_reserved_seed_external_dataset_efficiency_and_corruption_gates": True,
        },
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "coverage_file_sha256": file_hash(args.coverage),
        "paired_metrics_observed_at_freeze": {"reference": 0, "candidate": 0},
        "implementation_sha256": {name: file_hash(project_root / name) for name in names},
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
