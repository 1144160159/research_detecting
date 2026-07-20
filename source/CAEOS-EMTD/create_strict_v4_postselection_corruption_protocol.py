from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


CORRUPTION_GRID = {
    "modality_missing": [1.0],
    "field_missing": [0.1, 0.3, 0.5],
    "row_missing": [0.1, 0.3, 0.5],
    "feature_shuffle": [0.1, 0.3, 0.5],
    "gaussian_drift": [0.25, 0.5, 1.0],
}
CONFIRMATORY_SEVERITY = {
    "modality_missing": 1.0,
    "field_missing": 0.3,
    "row_missing": 0.3,
    "feature_shuffle": 0.3,
    "gaussian_drift": 0.5,
}


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require_sha(value: object, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{name} SHA is missing")
    return value


def _sentinel(coverage_sha: str, suite: str, scenarios: list[str]) -> str:
    digest = hashlib.sha256(f"{coverage_sha}:{suite}".encode("utf-8")).hexdigest()
    return scenarios[int(digest[:16], 16) % len(scenarios)]


def create_protocol(
    coverage: dict[str, Any],
    decision: dict[str, Any],
    *,
    coverage_file_sha256: str,
    decision_file_sha256: str,
    pairwise_candidate_manifest_sha256: str,
    clean_pairwise_root_manifest_sha256: str,
    trainer_implementation_sha256: str,
    runner_implementation_sha256: str,
    corruption_metrics_observed_at_freeze: int,
) -> dict[str, Any]:
    if coverage.get("schema_version") != "strict_v4_coverage_manifest_v2":
        raise ValueError("unexpected coverage schema")
    if coverage.get("manifest_sha256") != canonical_hash(coverage):
        raise ValueError("coverage manifest SHA mismatch")
    if coverage.get("datasets") != 7 or coverage.get("scenario_inference_units") != 102:
        raise ValueError("post-selection corruption requires seven datasets and 102 scenarios")
    if decision.get("schema_version") != "strict_v4_optimal_self_algorithm_decision_v1":
        raise ValueError("unexpected optimal self-algorithm decision schema")
    if decision.get("manifest_sha256") != canonical_hash(decision):
        raise ValueError("optimal self-algorithm decision SHA mismatch")
    if decision.get("status") != "frozen_optimal_self_algorithm":
        raise ValueError("optimal self-algorithm decision is not frozen")
    if decision.get("selected_algorithm") != "caeos_pairwise":
        raise ValueError("post-selection corruption is bound to caeos_pairwise")
    if int(corruption_metrics_observed_at_freeze) != 0:
        raise ValueError("corruption protocol must be frozen before any corruption metrics")

    coverage_sha = _require_sha(coverage.get("manifest_sha256"), "coverage manifest")
    registry = coverage.get("scenario_registry")
    if not isinstance(registry, dict) or len(registry) != 7:
        raise ValueError("scenario registry is incomplete")
    sentinels = {}
    for suite in sorted(registry):
        item = registry[suite]
        scenarios = item.get("scenarios") if isinstance(item, dict) else None
        if not isinstance(scenarios, list) or len(scenarios) != item.get("count"):
            raise ValueError(f"invalid scenario registry for {suite}")
        sentinels[suite] = _sentinel(coverage_sha, suite, scenarios)

    sentinel_runs = len(sentinels) * 3 * sum(len(v) for v in CORRUPTION_GRID.values())
    confirmatory_runs = 102 * len(CONFIRMATORY_SEVERITY)
    protocol = {
        "schema_version": "strict_v4_postselection_corruption_protocol_v1",
        "status": "frozen_post_selection_before_corruption_results",
        "corruption_metrics_observed_at_freeze": 0,
        "selected_algorithm": "caeos_pairwise",
        "optimal_self_algorithm_manifest_sha256": decision["manifest_sha256"],
        "coverage_manifest_sha256": coverage_sha,
        "input_file_sha256": {
            "coverage_manifest": _require_sha(coverage_file_sha256, "coverage file"),
            "optimal_self_algorithm_decision": _require_sha(
                decision_file_sha256, "decision file"
            ),
            "pairwise_candidate_manifest": _require_sha(
                pairwise_candidate_manifest_sha256, "pairwise candidate manifest"
            ),
            "clean_pairwise_root_manifest": _require_sha(
                clean_pairwise_root_manifest_sha256, "clean pairwise manifest"
            ),
        },
        "implementation_sha256": {
            "train_hybrid_open_set": _require_sha(
                trainer_implementation_sha256, "trainer implementation"
            ),
            "matrix_runner": _require_sha(
                runner_implementation_sha256, "runner implementation"
            ),
        },
        "execution_gate": {
            "requires_external_comparator_confirmation_complete": True,
            "must_not_overlap_accuracy_confirmation_or_efficiency_benchmark": True,
            "outer_scenario_workers": 1,
            "training_seed": 7,
            "corruption_seed": 211,
        },
        "clean_anchor": {
            "root": "runs/strict_v4_full103_pairwise_caeos_seed7",
            "expected_scenarios": 102,
            "reuse_metrics_only_no_refit_or_selection": True,
            "required_artifacts_per_scenario": [
                "metrics.json",
                "scores.npz",
                "evidence_package.npz",
                "provenance.json",
            ],
        },
        "corruption_definitions": {
            "test_only": True,
            "families": CORRUPTION_GRID,
            "modality_count": 3,
            "unknown_or_test_labels_used_for_generation_or_selection": False,
        },
        "sentinel_severity_screen": {
            "selection_rule": "one coverage-SHA-indexed scenario per dataset",
            "sentinel_scenarios": sentinels,
            "all_three_modalities": True,
            "expected_runs": sentinel_runs,
            "role": "descriptive severity and modality heterogeneity only",
        },
        "full102_confirmation": {
            "expected_scenarios": 102,
            "corruption_families": list(CONFIRMATORY_SEVERITY),
            "fixed_severity": CONFIRMATORY_SEVERITY,
            "modality_selection_rule": (
                "sha256(coverage_manifest_sha256:suite:scenario:corruption) modulo 3"
            ),
            "expected_runs": confirmatory_runs,
            "selection_is_independent_of_corruption_metrics": True,
        },
        "total_expected_corruption_runs": sentinel_runs + confirmatory_runs,
        "reported_metrics": [
            "known_macro_f1",
            "unknown_auroc",
            "unknown_aupr",
            "unknown_fpr95",
            "oscr",
            "ece",
        ],
        "statistical_analysis": {
            "unit": "scenario",
            "paired_against_clean_anchor": True,
            "bootstrap_repetitions": 20000,
            "bootstrap_seed": 20260720,
            "report_suite_means_and_95ci": True,
            "do_not_pool_corruption_conditions_as_independent_datasets": True,
        },
        "confirmatory_graceful_degradation_gate": {
            "maximum_mean_degradation": {
                "known_macro_f1": 0.10,
                "unknown_auroc": 0.15,
                "unknown_aupr": 0.15,
                "unknown_fpr95": 0.20,
                "oscr": 0.15,
            },
            "all_families_must_pass_all_metrics": True,
            "failure_must_be_reported_as_a_negative_result": True,
        },
        "claim_policy": {
            "algorithm_hyperparameters_and_routing_are_frozen": True,
            "no_post_corruption_algorithm_or_condition_selection": True,
            "sentinel_results_cannot_replace_full102_confirmation": True,
            "no_robustness_superlative_without_complete_gate": True,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def render(protocol: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 post-selection corruption protocol",
        "",
        f"Protocol SHA: `{protocol['manifest_sha256']}`.",
        f"Selected algorithm: `{protocol['selected_algorithm']}`.",
        f"Expected corruption runs: `{protocol['total_expected_corruption_runs']}`.",
        "",
        "## Sentinel scenarios",
        "",
    ]
    for suite, scenario in protocol["sentinel_severity_screen"][
        "sentinel_scenarios"
    ].items():
        lines.append(f"- `{suite}`: `{scenario}`")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--decision", type=Path, required=True)
    parser.add_argument("--pairwise-candidate-manifest", type=Path, required=True)
    parser.add_argument("--clean-pairwise-manifest", type=Path, required=True)
    parser.add_argument("--trainer", type=Path, required=True)
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    observed = len(list(args.output_dir.glob("**/corruption_metrics.json")))
    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    decision = json.loads(args.decision.read_text(encoding="utf-8"))
    protocol = create_protocol(
        coverage,
        decision,
        coverage_file_sha256=file_hash(args.coverage),
        decision_file_sha256=file_hash(args.decision),
        pairwise_candidate_manifest_sha256=file_hash(
            args.pairwise_candidate_manifest
        ),
        clean_pairwise_root_manifest_sha256=file_hash(args.clean_pairwise_manifest),
        trainer_implementation_sha256=file_hash(args.trainer),
        runner_implementation_sha256=file_hash(args.runner),
        corruption_metrics_observed_at_freeze=observed,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "protocol_manifest.json").write_text(
        json.dumps(protocol, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "protocol.md").write_text(render(protocol), encoding="utf-8")
    print(render(protocol), end="")


if __name__ == "__main__":
    main()
