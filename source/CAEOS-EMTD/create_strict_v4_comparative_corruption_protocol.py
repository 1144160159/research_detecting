from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


PRIMARY_METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)


def validate_manifest(payload: dict[str, Any], schema: str, label: str) -> None:
    if payload.get("schema_version") != schema or payload.get("manifest_sha256") != canonical_hash(payload):
        raise ValueError(f"{label} manifest validation failed")


def candidate_selection_is_label_free(metrics: dict[str, Any]) -> bool:
    details = metrics.get("risk_selection_details", {})
    return (
        details.get("unknown_or_test_labels_used_for_selection") is False
        and details.get("pseudo_unknown_learned_blend", {}).get(
            "unknown_or_test_labels_used"
        )
        is False
    )


def _source_record(
    candidate_root: Path,
    comparator_root: Path,
    suite: str,
    scenario: str,
    seed: int,
) -> dict[str, Any]:
    candidate = candidate_root / suite / f"{scenario}_seed{seed}"
    comparator = comparator_root / suite / f"{scenario}_seed{seed}_opendetect"
    candidate_files = {name: candidate / name for name in ("metrics.json", "scores.npz", "provenance.json")}
    comparator_files = {
        name: comparator / name
        for name in ("metrics.json", "scores.npz", "provenance.json", "model.pt")
    }
    missing = [str(path) for path in (*candidate_files.values(), *comparator_files.values()) if not path.is_file()]
    if missing:
        raise FileNotFoundError("comparative corruption source artifacts are incomplete: " + ", ".join(missing))
    candidate_metrics = json.loads(candidate_files["metrics.json"].read_text(encoding="utf-8"))
    comparator_metrics = json.loads(comparator_files["metrics.json"].read_text(encoding="utf-8"))
    if (
        int(candidate_metrics.get("seed", -1)) != seed
        or int(comparator_metrics.get("seed", -1)) != seed
    ):
        raise ValueError(f"source seed mismatch: {suite}/{scenario}/{seed}")
    if candidate_metrics.get("selected_risk") not in {
        "pseudo_unknown_learned_blend",
        "cauchy_modality_support_union",
    }:
        raise ValueError(f"candidate source is not the frozen pairwise runtime branch: {candidate}")
    if comparator_metrics.get("model") != "opendetect" or "opendetect" not in comparator_metrics.get("reports", {}):
        raise ValueError(f"comparator source is not OpenDetect: {comparator}")
    candidate_fingerprint = candidate_metrics["split_metadata"]["split_fingerprint"]["combined"]
    comparator_fingerprint = comparator_metrics["split_metadata"]["split_fingerprint"]["combined"]
    if candidate_fingerprint != comparator_fingerprint:
        raise ValueError(f"source split fingerprint mismatch: {suite}/{scenario}/{seed}")
    if not candidate_selection_is_label_free(candidate_metrics):
        raise ValueError(f"candidate leakage declaration failed: {candidate}")
    if comparator_metrics.get("selection_evidence", {}).get(
        "unknown_or_test_labels_used_for_fitting_or_selection"
    ) is not False:
        raise ValueError(f"comparator leakage declaration failed: {comparator}")
    return {
        "suite": suite,
        "scenario": scenario,
        "seed": seed,
        "split_fingerprint": candidate_fingerprint,
        "candidate_root": str(candidate.resolve()),
        "comparator_root": str(comparator.resolve()),
        "candidate_file_sha256": {name: file_hash(path) for name, path in candidate_files.items()},
        "comparator_file_sha256": {name: file_hash(path) for name, path in comparator_files.items()},
    }


def create_protocol(
    coverage: dict[str, Any],
    decision: dict[str, Any],
    external: dict[str, Any],
    candidate_corruption_protocol: dict[str, Any],
    candidate_corruption_summary: dict[str, Any],
    *,
    input_file_sha256: dict[str, str],
    implementation_sha256: dict[str, str],
    candidate_root: Path,
    comparator_root: Path,
    observed_paired_results: int,
) -> dict[str, Any]:
    validate_manifest(coverage, "strict_v4_coverage_manifest_v2", "coverage")
    validate_manifest(decision, "strict_v4_optimal_self_algorithm_decision_v1", "decision")
    validate_manifest(candidate_corruption_protocol, "strict_v4_postselection_corruption_protocol_v1", "candidate corruption protocol")
    if decision.get("selected_algorithm") != "caeos_pairwise":
        raise ValueError("comparative corruption is bound to caeos_pairwise")
    if external.get("schema_version") != "strict_v4_external_comparator_confirmation_v1":
        raise ValueError("unexpected external confirmation schema")
    if external.get("selected_algorithm") != "caeos_pairwise" or external.get("selected_comparator") != "opendetect":
        raise ValueError("external confirmation method binding mismatch")
    validation = external.get("comparator_validation", {})
    if validation.get("passes") is not True or validation.get("paired_runs") != 306:
        raise ValueError("external OpenDetect confirmation is incomplete")
    if candidate_corruption_summary.get("schema_version") != "strict_v4_postselection_corruption_summary_v1":
        raise ValueError("candidate corruption summary is incomplete")
    if candidate_corruption_summary.get("manifest_sha256") != canonical_hash(candidate_corruption_summary):
        raise ValueError("candidate corruption summary SHA mismatch")
    if candidate_corruption_summary.get("validation", {}).get("passes") is not True:
        raise ValueError("candidate corruption validation failed")
    if int(observed_paired_results) != 0:
        raise ValueError("comparative corruption protocol must freeze before paired results")
    registry = coverage.get("scenario_registry", {})
    if len(registry) != 7 or sum(item["count"] for item in registry.values()) != 102:
        raise ValueError("comparative corruption requires the frozen 102-scenario registry")
    seeds = sorted(int(seed) for seed in external.get("candidate_validation", {}).get("seeds", []))
    if seeds != [137, 139, 149]:
        raise ValueError("comparative corruption requires the three frozen external seeds")
    sources = []
    for suite in sorted(registry):
        for scenario in registry[suite]["scenarios"]:
            for seed in seeds:
                sources.append(_source_record(candidate_root, comparator_root, suite, scenario, seed))
    if len(sources) != 306:
        raise ValueError("comparative corruption source registry is incomplete")
    conditions = candidate_corruption_protocol["full102_confirmation"]
    protocol = {
        "schema_version": "strict_v4_comparative_corruption_protocol_v1",
        "status": "frozen_after_method_selection_before_paired_corruption_results",
        "selected_algorithm": "caeos_pairwise",
        "selected_comparator": "opendetect",
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "optimal_self_algorithm_manifest_sha256": decision["manifest_sha256"],
        "external_confirmation_file_sha256": input_file_sha256["external_confirmation"],
        "candidate_corruption_protocol_manifest_sha256": candidate_corruption_protocol["manifest_sha256"],
        "candidate_corruption_summary_manifest_sha256": candidate_corruption_summary["manifest_sha256"],
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": implementation_sha256,
        "seeds": seeds,
        "source_registry": sources,
        "source_registry_count": 306,
        "paired_results_observed_at_freeze": 0,
        "corruption_conditions": {
            "families": conditions["corruption_families"],
            "fixed_severity": conditions["fixed_severity"],
            "corruption_seed": candidate_corruption_protocol["execution_gate"]["corruption_seed"],
            "modality_selection_rule": conditions["modality_selection_rule"],
            "same_condition_for_all_three_seeds_within_scenario": True,
            "test_only": True,
        },
        "expected_runtime_capture_pairs": 306,
        "expected_paired_condition_evaluations": 1530,
        "statistical_analysis": {
            "unit": "dataset_scenario_pair",
            "average_three_seeds_inside_scenario": True,
            "bootstrap_repetitions": 20000,
            "bootstrap_seed": 20260720,
            "holm_family": "six degradation-advantage metrics within each corruption family",
            "metrics": [*PRIMARY_METRICS, "ece"],
            "positive_advantage_means_candidate_degrades_less_than_opendetect": True,
        },
        "comparative_robustness_gate": {
            "all_five_families_required": True,
            "all_six_metric_mean_advantages_strictly_positive": True,
            "all_six_metric_bootstrap_lower_bounds_strictly_positive": True,
            "all_six_metric_holm_adjusted_p_below_0_05": True,
            "all_suite_metric_mean_advantages_nonnegative": True,
            "failure_is_a_reportable_negative_result": True,
        },
        "leakage_policy": {
            "algorithm_models_thresholds_conditions_and_modalities_frozen": True,
            "unknown_or_test_labels_used_for_fitting_selection_or_corruption_generation": False,
            "test_labels_used_for_final_metrics_only": True,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--decision", type=Path, required=True)
    parser.add_argument("--external-confirmation", type=Path, required=True)
    parser.add_argument("--candidate-corruption-protocol", type=Path, required=True)
    parser.add_argument("--candidate-corruption-summary", type=Path, required=True)
    parser.add_argument("--candidate-root", type=Path, required=True)
    parser.add_argument("--comparator-root", type=Path, required=True)
    parser.add_argument("--candidate-trainer", type=Path, required=True)
    parser.add_argument("--candidate-runtime", type=Path, required=True)
    parser.add_argument("--candidate-capture", type=Path, required=True)
    parser.add_argument("--comparator-runtime", type=Path, required=True)
    parser.add_argument("--comparator-capture", type=Path, required=True)
    parser.add_argument("--evaluator", type=Path, required=True)
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--summarizer", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    input_paths = {
        "coverage": args.coverage,
        "decision": args.decision,
        "external_confirmation": args.external_confirmation,
        "candidate_corruption_protocol": args.candidate_corruption_protocol,
        "candidate_corruption_summary": args.candidate_corruption_summary,
    }
    implementation_paths = {
        "candidate_trainer": args.candidate_trainer,
        "candidate_runtime": args.candidate_runtime,
        "candidate_capture": args.candidate_capture,
        "comparator_runtime": args.comparator_runtime,
        "comparator_capture": args.comparator_capture,
        "evaluator": args.evaluator,
        "runner": args.runner,
        "summarizer": args.summarizer,
        "protocol_creator": Path(__file__),
    }
    observed = len(list(args.run_root.glob("**/paired_corruption.json"))) if args.run_root.exists() else 0
    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in input_paths.values()]
    protocol = create_protocol(
        *payloads,
        input_file_sha256={name: file_hash(path) for name, path in input_paths.items()},
        implementation_sha256={name: file_hash(path) for name, path in implementation_paths.items()},
        candidate_root=args.candidate_root.resolve(),
        comparator_root=args.comparator_root.resolve(),
        observed_paired_results=observed,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "protocol_manifest.json").write_text(
        json.dumps(protocol, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "protocol_complete").touch()
    print(json.dumps({"manifest_sha256": protocol["manifest_sha256"], "sources": 306, "conditions": 1530}, sort_keys=True))


if __name__ == "__main__":
    main()
