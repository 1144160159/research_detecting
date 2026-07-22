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
    source: dict[str, Any],
    *,
    source_file_sha256: str,
    implementation_sha256: dict[str, str],
) -> dict[str, Any]:
    if source.get("schema_version") != "strict_v4_tail_aware_pilot_protocol_v1":
        raise ValueError("unexpected source hard-scenario protocol schema")
    if source.get("manifest_sha256") != canonical_hash(source):
        raise ValueError("source hard-scenario protocol SHA mismatch")
    scenarios = source.get("pilot", {}).get("scenarios", {})
    if len(scenarios) != 7 or sum(map(len, scenarios.values())) != 14:
        raise ValueError("LCB pilot requires the frozen 14 hard scenarios")

    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_lcb_tail_aware_pilot_protocol_v1",
        "status": "frozen_before_pilot",
        "paper_incumbent": "caeos_pairwise",
        "candidate": {
            "name": "caeos_lcb_tail_aware",
            "risk_selection": "nested_lcb_tail_aware_pairwise_pseudo_unknown_blend",
            "risk_endpoint": "pseudo_unknown_tail_aware_blend",
            "reference_endpoint": "cauchy_modality_support_union",
            "risk_policy_name": "strict_v4_lcb_tail_aware_pilot_seed191_v1",
            "maximum_alpha": 0.5,
            "minimum_fold_gain": -0.05,
            "hard_pseudo_fraction": 0.5,
            "boundary_interpolation": 0.5,
            "boundary_max_per_task": 512,
            "tail_gammas": [0.0, 1.0, 2.0, 4.0],
            "monotone_powers": [1, 2, 4],
            "training_objective": "tail_weighted_monotone_pairwise",
            "confidence_z": 1.645,
            "minimum_metric_lcb_gain": 0.0,
            "minimum_aupr_lcb_gain": 0.0,
            "minimum_aupr_fold_gain": -0.05,
            "selection_intent": (
                "activate the learned head only when known-only pseudo-unknown folds "
                "support all four metrics and the AUPR tail; otherwise retain the "
                "frozen reference"
            ),
        },
        "pilot": {
            "development_seed": 191,
            "scenarios": scenarios,
            "expected_run_count": 14,
            "selection_uses_seed191_test_labels": True,
            "purpose": "disjoint conservative candidate development screen",
            "gate": {
                "all_four_overall_oriented_means_strictly_positive": True,
                "minimum_suite_metric_gain": -0.01,
                "minimum_fully_nonregressing_suite_count": 6,
                "known_macro_f1_nonregression": True,
                "minimum_candidate_endpoint_selected_count": 1,
            },
        },
        "reserved_confirmation": {
            "seeds": [197, 199, 211],
            "scenario_scope": "all_102_strict_v4_scenarios",
            "expected_run_count": 306,
            "seed_disjoint_from_pairwise_tail_and_lcb_development": True,
            "must_freeze_candidate_before_first_confirmation_run": True,
            "replacement_gate": (
                "the incumbent is replaced only by a separately frozen confirmation "
                "that passes bootstrap, Holm, known-F1 and every-suite nonregression"
            ),
        },
        "leakage_boundary": {
            "runtime_training_and_selection": "known_train_and_known_validation_only",
            "pilot_test_labels": "development_metrics_and freeze decision only",
            "reserved_confirmation_labels": "final metrics only",
            "existing_seed7_and_tail_confirmation_labels": "diagnosis only, not tuning",
        },
        "source_hard_scenario_protocol_sha256": source_file_sha256,
        "source_hard_scenario_manifest_sha256": source["manifest_sha256"],
        "implementation_sha256": implementation_sha256,
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.source_protocol.read_bytes()
    source = json.loads(raw.decode("utf-8"))
    implementation_paths = (
        "caeos/tail_aware_ranking.py",
        "train_hybrid_open_set.py",
        "run_nested_gate_matrix.py",
        "analyze_strict_v4_lcb_tail_aware_pilot.py",
        "scripts/run_strict_v4_lcb_tail_aware_pilot.sh",
    )
    protocol = create_protocol(
        source,
        source_file_sha256=hashlib.sha256(raw).hexdigest(),
        implementation_sha256={
            name: file_hash(args.project_root / name) for name in implementation_paths
        },
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(protocol["pilot"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
