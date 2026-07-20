from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_manifest(payload: dict[str, Any], schema: str, label: str) -> None:
    if payload.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if payload.get("manifest_sha256") != canonical_hash(payload):
        raise ValueError(f"{label} manifest SHA mismatch")


def create_protocol(
    coverage: dict[str, Any],
    pilot_protocol: dict[str, Any],
    pilot_analysis: dict[str, Any],
    *,
    coverage_sha256: str,
    pilot_protocol_sha256: str,
    pilot_analysis_sha256: str,
    implementation_sha256: dict[str, str],
) -> dict[str, Any]:
    validate_manifest(coverage, "strict_v4_coverage_manifest_v2", "coverage")
    validate_manifest(
        pilot_protocol, "strict_v4_tail_aware_pilot_protocol_v1", "pilot protocol"
    )
    if pilot_analysis.get("schema_version") != "strict_v4_tail_aware_pilot_analysis_v1":
        raise ValueError("unexpected pilot analysis schema")
    if not (
        pilot_analysis.get("passes") is True
        and pilot_analysis.get("decision") == "freeze_for_new_seed_confirmation"
        and pilot_analysis.get("protocol_manifest_sha256")
        == pilot_protocol["manifest_sha256"]
    ):
        raise ValueError("tail-aware pilot did not pass its frozen gate")

    reserved = pilot_protocol["reserved_confirmation"]
    seeds = [int(seed) for seed in reserved["seeds"]]
    registry = {
        suite: list(details["scenarios"])
        for suite, details in sorted(coverage["scenario_registry"].items())
    }
    scenario_count = sum(len(values) for values in registry.values())
    if coverage.get("datasets") != 7 or scenario_count != 102:
        raise ValueError("tail-aware confirmation requires 7 datasets and 102 scenarios")
    if seeds != [157, 163, 167] or int(reserved["expected_run_count"]) != 306:
        raise ValueError("unexpected reserved tail-aware confirmation scope")

    pilot_candidate = pilot_protocol["candidate"]
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_tail_aware_confirmation_protocol_v1",
        "status": "frozen_after_passed_pilot_before_confirmation",
        "candidate": {
            "risk_selection": pilot_candidate["risk_selection"],
            "risk_endpoint": pilot_candidate["risk_endpoint"],
            "reference_endpoint": pilot_candidate["reference_endpoint"],
            "maximum_alpha": float(pilot_candidate["maximum_alpha"]),
            "pilot_minimum_fold_gain": float(pilot_candidate["minimum_fold_gain"]),
            "runtime_minimum_fold_gain": -1.0,
            "hard_pseudo_fraction": float(pilot_candidate["hard_pseudo_fraction"]),
            "boundary_interpolation": float(pilot_candidate["boundary_interpolation"]),
            "boundary_max_per_task": int(pilot_candidate["boundary_max_per_task"]),
            "tail_gammas": list(pilot_candidate["tail_gammas"]),
            "monotone_powers": list(pilot_candidate["monotone_powers"]),
            "runtime_selection_rule": (
                "select the pilot-evaluated tail-aware endpoint when its known-only "
                "cross-fitted four-metric mean gate passes; otherwise use the frozen "
                "Cauchy modality-support reference"
            ),
            "selection_change_after_pilot": (
                "the pilot predefined and scored the risk endpoint directly; setting "
                "the fold floor to -1 only makes that evaluated endpoint deployable and "
                "does not change its fitted scores"
            ),
        },
        "confirmation": {
            "seeds": seeds,
            "scenario_registry": registry,
            "expected_scenario_count": scenario_count,
            "expected_run_count": scenario_count * len(seeds),
            "risk_policy": "strict_v4_tail_aware_pairwise_confirmation_v1",
            "inference_unit": "dataset-scenario after averaging three seed repeats",
            "bootstrap_repetitions": 20000,
            "bootstrap_seed": 20260719,
            "gates": {
                "all_four_unknown_metric_means_strictly_positive": True,
                "all_four_scenario_block_bootstrap_lowers_strictly_positive": True,
                "all_four_holm_wilcoxon_p_values_below_0_05": True,
                "all_suite_unknown_metric_means_nonnegative": True,
                "known_macro_f1_unchanged": True,
                "runtime_candidate_endpoint_exercised": True,
            },
        },
        "leakage_boundary": {
            "runtime_training_and_selection": "known_train_and_known_validation_only",
            "pilot_seed7_labels": "development_and_freeze_decision_only",
            "confirmation_labels": "final_metrics_only",
            "confirmation_seeds_disjoint_from_tail_aware_development": True,
        },
        "bindings": {
            "coverage_manifest_sha256": coverage["manifest_sha256"],
            "coverage_file_sha256": coverage_sha256,
            "pilot_protocol_manifest_sha256": pilot_protocol["manifest_sha256"],
            "pilot_protocol_file_sha256": pilot_protocol_sha256,
            "pilot_analysis_file_sha256": pilot_analysis_sha256,
        },
        "implementation_sha256": implementation_sha256,
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--pilot-protocol", type=Path, required=True)
    parser.add_argument("--pilot-analysis", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    pilot_protocol = json.loads(args.pilot_protocol.read_text(encoding="utf-8"))
    pilot_analysis = json.loads(args.pilot_analysis.read_text(encoding="utf-8"))
    sources = (
        "caeos/tail_aware_ranking.py",
        "train_hybrid_open_set.py",
        "run_nested_gate_matrix.py",
        "confirm_strict_v4_tail_aware.py",
    )
    protocol = create_protocol(
        coverage,
        pilot_protocol,
        pilot_analysis,
        coverage_sha256=file_hash(args.coverage),
        pilot_protocol_sha256=file_hash(args.pilot_protocol),
        pilot_analysis_sha256=file_hash(args.pilot_analysis),
        implementation_sha256={
            name: file_hash(args.project_root / name) for name in sources
        },
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(protocol, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
