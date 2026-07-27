from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_protocol(
    *,
    pilot_protocol: dict[str, Any],
    pilot_analysis: dict[str, Any],
    coverage: dict[str, Any],
    pairwise_manifest: dict[str, Any],
    input_file_sha256: dict[str, str],
    implementation_sha256: dict[str, str],
    observed_metrics: int,
) -> dict[str, Any]:
    if observed_metrics != 0:
        raise ValueError("CTC confirmation protocol must freeze before results")
    if pilot_protocol.get("schema_version") != "strict_v4_conflict_topology_copula_protocol_v1":
        raise ValueError("unexpected CTC pilot protocol schema")
    if pilot_protocol.get("manifest_sha256") != canonical_hash(pilot_protocol):
        raise ValueError("CTC pilot protocol SHA mismatch")
    if pilot_analysis.get("schema_version") != "strict_v4_conflict_topology_copula_analysis_v1":
        raise ValueError("unexpected CTC pilot analysis schema")
    if pilot_analysis.get("protocol_manifest_sha256") != pilot_protocol["manifest_sha256"]:
        raise ValueError("CTC pilot analysis binding mismatch")
    if not pilot_analysis.get("passes") or pilot_analysis.get("decision") != "freeze_for_reserved_seed_confirmation":
        raise ValueError("CTC pilot did not authorize reserved-seed confirmation")
    if coverage.get("schema_version") != "strict_v4_coverage_manifest_v2":
        raise ValueError("unexpected strict-v4 coverage schema")
    if coverage.get("manifest_sha256") != canonical_hash(coverage):
        raise ValueError("strict-v4 coverage manifest SHA mismatch")
    registry = coverage.get("scenario_registry", {})
    scenario_count = sum(int(block["count"]) for block in registry.values())
    if len(registry) != 7 or scenario_count != 102:
        raise ValueError("CTC confirmation requires the complete 7-suite/102-scenario registry")
    for block in registry.values():
        if int(block["count"]) != len(block["scenarios"]):
            raise ValueError("coverage scenario count is inconsistent")
    if pairwise_manifest.get("schema_version") != "strict_v4_boundary_pairwise_candidate_v1":
        raise ValueError("unexpected Pairwise candidate schema")
    if pairwise_manifest.get("manifest_sha256") != canonical_hash(pairwise_manifest):
        raise ValueError("Pairwise candidate manifest SHA mismatch")
    candidate = pairwise_manifest["candidate"]
    if candidate.get("runtime_uses_unknown_or_test_labels") is not False:
        raise ValueError("Pairwise runtime leakage boundary is invalid")

    seeds = [233, 239, 241]
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_conflict_topology_copula_confirmation_protocol_v1",
        "status": "frozen_after_positive_pilot_before_confirmation",
        "selected_candidate": "caeos_conflict_topology_copula",
        "pilot_protocol_manifest_sha256": pilot_protocol["manifest_sha256"],
        "pilot_decision": pilot_analysis["decision"],
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "pairwise_candidate_manifest_sha256": pairwise_manifest["manifest_sha256"],
        "seeds": seeds,
        "scenario_registry": registry,
        "scenario_count": scenario_count,
        "expected_pairwise_runs": scenario_count * len(seeds),
        "expected_ctc_runs": scenario_count * len(seeds),
        "pairwise_generation": {
            "risk_selection": candidate["risk_selection"],
            "maximum_alpha": candidate["maximum_alpha"],
            "minimum_fold_gain": candidate["minimum_fold_gain"],
            "hard_pseudo_fraction": candidate["hard_pseudo_fraction"],
            "boundary_interpolation": candidate["interpolation"],
            "boundary_max_per_task": candidate["max_per_task"],
            "training_objective": candidate["training_objective"],
            "risk_policy_name": "strict_v4_ctc_confirmation_pairwise_v1",
            "unknown_or_test_labels_used_for_runtime_selection": False,
        },
        "ctc_parameters": {
            "alpha": 0.25,
            "calibration_fraction": 0.4,
            "split_seed": 229,
            "known_rejection_quantile": 0.95,
            "prediction_policy": "frozen_pairwise_prediction_unchanged",
        },
        "confirmation_inference": {
            "independent_unit": "scenario",
            "seed_repeats_averaged_within_scenario": True,
            "bootstrap_repetitions": 10000,
            "bootstrap_seed": 20260721,
            "holm_family": ["unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr"],
            "gate": {
                "all_four_oriented_means_strictly_positive": True,
                "auroc_and_aupr_bootstrap_lower_strictly_positive": True,
                "all_four_holm_adjusted_p_below_0_05": True,
                "all_suite_metric_oriented_means_nonnegative": True,
                "prediction_array_equal_for_all_306_runs": True,
                "known_macro_f1_absolute_tolerance": 1e-12,
            },
        },
        "claim_boundary": {
            "positive_confirmation_still_requires_efficiency_and_external_dataset_gates": True,
            "negative_confirmation_retains_caeos_pairwise": True,
            "unknown_or_test_labels_used_for_fit_threshold_or_weight_selection": False,
        },
        "metrics_observed_at_freeze": observed_metrics,
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": implementation_sha256,
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-protocol", type=Path, required=True)
    parser.add_argument("--pilot-analysis", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--pairwise-manifest", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sources = {
        "pilot_protocol": args.pilot_protocol,
        "pilot_analysis": args.pilot_analysis,
        "coverage": args.coverage,
        "pairwise_manifest": args.pairwise_manifest,
    }
    names = (
        "caeos/conflict_topology_copula.py",
        "evaluate_conflict_topology_copula.py",
        "train_hybrid_open_set.py",
        "run_nested_gate_matrix.py",
        "prepare_stratified_cache.py",
        "prepare_cic_iot2023_strict.py",
        "prepare_group_supported_cache.py",
        "run_strict_v4_conflict_topology_copula_confirmation_matrix.py",
        "summarize_strict_v4_conflict_topology_copula_confirmation.py",
        "summarize_paired_confirmation.py",
        "scripts/run_strict_v4_conflict_topology_copula_confirmation.sh",
    )
    protocol = create_protocol(
        pilot_protocol=json.loads(args.pilot_protocol.read_text(encoding="utf-8")),
        pilot_analysis=json.loads(args.pilot_analysis.read_text(encoding="utf-8")),
        coverage=json.loads(args.coverage.read_text(encoding="utf-8")),
        pairwise_manifest=json.loads(args.pairwise_manifest.read_text(encoding="utf-8")),
        input_file_sha256={name: file_hash(path) for name, path in sources.items()},
        implementation_sha256={
            name: file_hash(args.project_root / name) for name in names
        },
        observed_metrics=(
            len(list(args.run_root.rglob("metrics.json"))) if args.run_root.exists() else 0
        ),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
