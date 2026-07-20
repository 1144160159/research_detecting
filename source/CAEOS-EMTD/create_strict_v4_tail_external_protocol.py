from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(payload: dict[str, Any], schema: str, label: str) -> None:
    if payload.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if payload.get("manifest_sha256") != canonical_hash(payload):
        raise ValueError(f"{label} manifest SHA mismatch")


def create_protocol(
    coverage: dict[str, Any],
    tail_protocol: dict[str, Any],
    tournament: dict[str, Any],
    external_protocol: dict[str, Any],
    *,
    input_file_sha256: dict[str, str],
    implementation_sha256: dict[str, str],
) -> dict[str, Any]:
    validate(coverage, "strict_v4_coverage_manifest_v2", "coverage")
    validate(tail_protocol, "strict_v4_tail_aware_confirmation_protocol_v1", "tail protocol")
    validate(tournament, "strict_v4_self_algorithm_tournament_protocol_v1", "tournament")
    validate(external_protocol, "strict_v4_external_confirmation_protocol_v1", "external protocol")
    branch = tournament["external_confirmation_branch"]["tail_challenger_wins"]
    seeds = [int(seed) for seed in branch["fresh_seeds"]]
    scenario_count = int(tournament["coverage"]["scenario_count"])
    used = {
        7,
        *tournament["incumbent_branch"]["confirmation_seeds"],
        *tournament["challenger_branch"]["confirmation_seeds"],
    }
    if used.intersection(seeds) or seeds != [173, 179, 181]:
        raise ValueError("tail external seeds are not fresh")
    if external_protocol["selected_comparator"] != "opendetect":
        raise ValueError("tail external branch currently requires frozen OpenDetect")
    candidate = tail_protocol["candidate"]
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_tail_external_confirmation_protocol_v1",
        "status": "conditionally_frozen_before_any_tail_external_run",
        "activation_condition": (
            "strict_v4_optimal_self_algorithm_decision_v1 selects "
            "caeos_tail_aware_pairwise"
        ),
        "selected_algorithm": "caeos_tail_aware_pairwise",
        "selected_comparator": "opendetect",
        "seeds": seeds,
        "scenario_registry": tournament["coverage"]["scenario_registry"],
        "scenario_count": scenario_count,
        "expected_candidate_runs": scenario_count * len(seeds),
        "expected_comparator_runs": scenario_count * len(seeds),
        "candidate": {
            "risk_selection": candidate["risk_selection"],
            "risk_endpoint": candidate["risk_endpoint"],
            "reference_endpoint": candidate["reference_endpoint"],
            "maximum_alpha": candidate["maximum_alpha"],
            "runtime_minimum_fold_gain": candidate["runtime_minimum_fold_gain"],
            "hard_pseudo_fraction": candidate["hard_pseudo_fraction"],
            "boundary_interpolation": candidate["boundary_interpolation"],
            "boundary_max_per_task": candidate["boundary_max_per_task"],
            "risk_policy": "strict_v4_tail_external_confirmation_v1",
        },
        "inference": {
            "unit": "dataset-scenario after averaging three seed repeats",
            "bootstrap_repetitions": 20000,
            "bootstrap_seed": 20260721,
            "gate": {
                "all_four_unknown_metric_means_strictly_positive": True,
                "all_four_bootstrap_lowers_strictly_positive": True,
                "all_four_holm_wilcoxon_p_values_below_0_05": True,
                "all_suite_unknown_metric_means_nonnegative": True,
                "known_macro_f1_nonnegative": True,
            },
        },
        "bindings": {
            "coverage_manifest_sha256": coverage["manifest_sha256"],
            "tail_confirmation_protocol_sha256": tail_protocol["manifest_sha256"],
            "tournament_protocol_sha256": tournament["manifest_sha256"],
            "development_external_protocol_sha256": external_protocol["manifest_sha256"],
        },
        "leakage_boundary": {
            "candidate_and_comparator_fitting": "known_train_and_known_validation_only",
            "external_test_labels": "final_metrics_only",
            "external_seeds_disjoint_from_all_algorithm_selection": True,
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": implementation_sha256,
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--tail-protocol", type=Path, required=True)
    parser.add_argument("--tournament", type=Path, required=True)
    parser.add_argument("--external-protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "coverage": args.coverage,
        "tail_protocol": args.tail_protocol,
        "tournament": args.tournament,
        "external_protocol": args.external_protocol,
    }
    payloads = {
        name: json.loads(path.read_text(encoding="utf-8"))
        for name, path in paths.items()
    }
    sources = (
        "confirm_strict_v4_tail_external.py",
        "scripts/run_strict_v4_tail_external_confirmation.sh",
    )
    protocol = create_protocol(
        payloads["coverage"],
        payloads["tail_protocol"],
        payloads["tournament"],
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
