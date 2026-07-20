from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from select_strict_v4_external_risk_candidate import canonical_hash


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_seeds(text: str) -> list[int]:
    seeds = [int(value.strip()) for value in text.split(",") if value.strip()]
    if len(seeds) < 3 or len(seeds) != len(set(seeds)):
        raise ValueError("confirmation requires at least three unique seeds")
    if 7 in seeds:
        raise ValueError("seed7 is the router development seed")
    return sorted(seeds)


def build_manifest(
    coverage: dict[str, Any],
    router: dict[str, Any],
    seeds: list[int],
    implementation_sha256: str,
) -> dict[str, Any]:
    if coverage.get("manifest_sha256") != canonical_hash(coverage):
        raise ValueError("coverage manifest SHA mismatch")
    if router.get("manifest_sha256") != canonical_hash(router):
        raise ValueError("router manifest SHA mismatch")
    if router.get("coverage_manifest_sha256") != coverage["manifest_sha256"]:
        raise ValueError("router is not bound to the coverage manifest")
    if router.get("status") != (
        "frozen_after_seed7_development_before_new_seed_confirmation"
    ):
        raise ValueError("router is not frozen for new-seed confirmation")
    scenario_count = int(coverage["scenario_inference_units"])
    payload: dict[str, Any] = {
        "schema_version": "strict_v4_domain_safe_router_confirmation_protocol_v1",
        "status": "frozen_before_any_confirmation_run",
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "router_manifest_sha256": router["manifest_sha256"],
        "development_seed": 7,
        "confirmation_seeds": seeds,
        "scenario_count": scenario_count,
        "expected_caeos_runs": scenario_count * len(seeds),
        "expected_mlp_runs": scenario_count * len(seeds),
        "inference_unit": "dataset_scenario",
        "seed_repeats": "averaged_within_dataset_scenario",
        "routing": {
            suite: details["method"]
            for suite, details in sorted(router["routing"].items())
        },
        "cache_policy": {
            "edge_iiot": {"sampler": "stratified", "max_per_class": 1000},
            "nf_cse": {"sampler": "stratified", "max_per_class": 1000},
            "ustc_tfc2016": {"sampler": "stratified", "max_per_class": 3000},
            "nf_unsw": {"sampler": "stratified", "max_per_class": 5000},
            "cicids2017": {"sampler": "stratified", "max_per_class": 5000},
            "cic_ton_iot": {"sampler": "stratified", "max_per_class": 1000},
            "cic_iot2023": {
                "sampler": "stratified_then_group_supported",
                "max_per_class": 1000,
                "minimum_capture_groups": 3,
            },
        },
        "selection_lock": {
            "routing_may_change_after_confirmation_starts": False,
            "test_labels_may_be_used_for_refitting_or_selection": False,
            "runtime_selection_inputs": ["suite_id"],
        },
        "confirmation_gate": {
            "all_unknown_metric_means_strictly_positive_vs_pairwise": True,
            "auroc_bootstrap_lower_strictly_positive": True,
            "aupr_bootstrap_lower_strictly_positive": True,
            "all_unknown_metric_holm_p_below_0_05": True,
            "all_suite_unknown_metric_means_nonnegative": True,
            "known_macro_f1_unchanged": True,
        },
        "implementation_sha256": implementation_sha256,
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage-manifest", type=Path, required=True)
    parser.add_argument("--router-manifest", type=Path, required=True)
    parser.add_argument("--seeds", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    coverage = json.loads(args.coverage_manifest.read_text(encoding="utf-8"))
    router = json.loads(args.router_manifest.read_text(encoding="utf-8"))
    payload = build_manifest(
        coverage, router, parse_seeds(args.seeds), file_hash(Path(__file__))
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
