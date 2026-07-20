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
    router_protocol: dict[str, Any],
    tail_protocol: dict[str, Any],
    pairwise_manifest: dict[str, Any],
    external_protocol: dict[str, Any],
    *,
    input_file_sha256: dict[str, str],
    implementation_sha256: dict[str, str],
) -> dict[str, Any]:
    validate_manifest(coverage, "strict_v4_coverage_manifest_v2", "coverage")
    validate_manifest(
        router_protocol,
        "strict_v4_domain_safe_router_confirmation_protocol_v1",
        "router protocol",
    )
    validate_manifest(
        tail_protocol,
        "strict_v4_tail_aware_confirmation_protocol_v1",
        "tail-aware protocol",
    )
    validate_manifest(
        external_protocol,
        "strict_v4_external_confirmation_protocol_v1",
        "external protocol",
    )
    if pairwise_manifest.get("schema_version") != "strict_v4_boundary_pairwise_candidate_v1":
        raise ValueError("unexpected pairwise candidate schema")
    if pairwise_manifest.get("manifest_sha256") != canonical_hash(pairwise_manifest):
        raise ValueError("pairwise candidate manifest SHA mismatch")
    registry = {
        suite: list(details["scenarios"])
        for suite, details in sorted(coverage["scenario_registry"].items())
    }
    scenario_count = sum(len(values) for values in registry.values())
    tail_seeds = [int(seed) for seed in tail_protocol["confirmation"]["seeds"]]
    router_seeds = [int(seed) for seed in router_protocol["confirmation_seeds"]]
    fresh_external_seeds = [173, 179, 181]
    used = {7, *router_seeds, *tail_seeds}
    if scenario_count != 102 or len(registry) != 7:
        raise ValueError("self-algorithm tournament requires 7 datasets and 102 scenarios")
    if used.intersection(fresh_external_seeds):
        raise ValueError("fresh external seeds overlap development or internal confirmation")
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_self_algorithm_tournament_protocol_v1",
        "status": "frozen_before_tail_confirmation_or_tournament_outcomes",
        "coverage": {
            "scenario_registry": registry,
            "scenario_count": scenario_count,
            "coverage_manifest_sha256": coverage["manifest_sha256"],
        },
        "incumbent_branch": {
            "selection_source": "strict_v4_final_algorithm_decision_v1",
            "eligible_algorithms": ["caeos_domain_safe_router", "caeos_pairwise"],
            "confirmation_seeds": router_seeds,
        },
        "challenger_branch": {
            "algorithm": "caeos_tail_aware_pairwise",
            "tail_confirmation_protocol_sha256": tail_protocol["manifest_sha256"],
            "confirmation_seeds": tail_seeds,
            "advance_only_if_tail_confirmation_passes": True,
        },
        "head_to_head": {
            "seeds": tail_seeds,
            "expected_pairwise_runs": scenario_count * len(tail_seeds),
            "pairwise_risk_selection": "nested_boundary_pairwise_pseudo_unknown_blend",
            "pairwise_risk_policy": "strict_v4_tail_aware_incumbent_pairwise_v1",
            "pairwise_manifest_sha256": pairwise_manifest["manifest_sha256"],
            "candidate_report_source": "tail_confirmation_selected_report",
            "incumbent_report_source": (
                "pairwise selected report or the frozen suite-routed fixed report from "
                "the same pairwise run"
            ),
            "inference_unit": "dataset-scenario after averaging three seed repeats",
            "bootstrap_repetitions": 20000,
            "bootstrap_seed": 20260720,
            "replacement_gate": {
                "all_four_unknown_metric_means_strictly_positive": True,
                "all_four_bootstrap_lowers_strictly_positive": True,
                "all_four_holm_wilcoxon_p_values_below_0_05": True,
                "all_suite_unknown_metric_means_nonnegative": True,
                "known_macro_f1_nonnegative": True,
            },
        },
        "external_confirmation_branch": {
            "strongest_non_caeos_comparator": external_protocol["selected_comparator"],
            "incumbent_wins": {
                "reuse_protocol_sha256": external_protocol["manifest_sha256"],
                "seeds": router_seeds,
            },
            "tail_challenger_wins": {
                "fresh_seeds": fresh_external_seeds,
                "expected_candidate_runs": scenario_count * len(fresh_external_seeds),
                "expected_comparator_runs": scenario_count * len(fresh_external_seeds),
                "must_freeze_dedicated_protocol_before_first_run": True,
            },
        },
        "selection_rule": (
            "retain the confirmed incumbent unless the tail-aware challenger first "
            "passes its independent confirmation and then passes every frozen paired "
            "head-to-head replacement gate on seeds 157/163/167"
        ),
        "leakage_boundary": {
            "development_seed": 7,
            "router_internal_confirmation_seeds": router_seeds,
            "tail_internal_and_head_to_head_seeds": tail_seeds,
            "tail_external_confirmation_seeds": fresh_external_seeds,
            "all_seed_sets_disjoint": True,
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": implementation_sha256,
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--router-protocol", type=Path, required=True)
    parser.add_argument("--tail-protocol", type=Path, required=True)
    parser.add_argument("--pairwise-manifest", type=Path, required=True)
    parser.add_argument("--external-protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "coverage": args.coverage,
        "router_protocol": args.router_protocol,
        "tail_protocol": args.tail_protocol,
        "pairwise_manifest": args.pairwise_manifest,
        "external_protocol": args.external_protocol,
    }
    payloads = {
        name: json.loads(path.read_text(encoding="utf-8"))
        for name, path in paths.items()
    }
    sources = (
        "confirm_strict_v4_tail_vs_incumbent.py",
        "select_strict_v4_optimal_self_algorithm.py",
        "scripts/run_strict_v4_self_algorithm_tournament.sh",
    )
    protocol = create_protocol(
        payloads["coverage"],
        payloads["router_protocol"],
        payloads["tail_protocol"],
        payloads["pairwise_manifest"],
        payloads["external_protocol"],
        input_file_sha256={name: file_hash(path) for name, path in paths.items()},
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
