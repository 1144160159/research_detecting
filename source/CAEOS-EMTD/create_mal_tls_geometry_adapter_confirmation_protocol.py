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
    pilot: dict[str, Any],
    analysis: dict[str, Any],
    *,
    pilot_protocol_file_sha256: str,
    pilot_analysis_file_sha256: str,
    implementation_sha256: dict[str, str],
    observed_metrics: int,
) -> dict[str, Any]:
    if pilot.get("schema_version") != "mal_tls_geometry_preserving_adapter_protocol_v1":
        raise ValueError("unexpected geometry pilot protocol schema")
    if pilot.get("manifest_sha256") != canonical_hash(pilot):
        raise ValueError("geometry pilot protocol SHA mismatch")
    if analysis.get("schema_version") != "mal_tls_geometry_preserving_adapter_analysis_v1":
        raise ValueError("unexpected geometry pilot analysis schema")
    if analysis.get("protocol_manifest_sha256") != pilot["manifest_sha256"]:
        raise ValueError("geometry pilot analysis is not bound to the protocol")
    if analysis.get("passes") is not True or analysis.get("decision") != (
        "freeze_for_reserved_seed_confirmation"
    ):
        raise ValueError("geometry pilot did not authorize confirmation")
    if observed_metrics != 0:
        raise ValueError("geometry confirmation must freeze before results")
    seeds = pilot["reserved_confirmation"]["seeds"]
    if seeds != [197, 199, 211]:
        raise ValueError("unexpected geometry confirmation seeds")
    protocol: dict[str, Any] = {
        "schema_version": "mal_tls_geometry_adapter_confirmation_protocol_v1",
        "status": "frozen_after_positive_pilot_before_reserved_seed_results",
        "pilot_protocol_manifest_sha256": pilot["manifest_sha256"],
        "pilot_protocol_file_sha256": pilot_protocol_file_sha256,
        "pilot_analysis_file_sha256": pilot_analysis_file_sha256,
        "selected_candidate": "mal_tls_geometry_preserving_adapter",
        "reference": pilot["paired_methods"]["reference"],
        "candidate": pilot["paired_methods"]["candidate"],
        "dataset": pilot["dataset"],
        "training": {
            **{
                key: value
                for key, value in pilot["training"].items()
                if key not in {"development_seed", "expected_development_runs"}
            },
            "confirmation_seeds": seeds,
            "expected_confirmation_runs": 36,
        },
        "hard_invariants": pilot["hard_invariants"],
        "confirmatory_analysis": {
            "paired_unit": "scenario_seed",
            "paired_units": 18,
            "bootstrap_repetitions": 20000,
            "bootstrap_seed": 20260721,
            "all_four_mean_oriented_gains_positive": True,
            "all_four_bootstrap_95ci_lower_bounds_positive": True,
            "minimum_scenario_mean_metric_gain": -0.02,
            "minimum_all_metric_nonregressing_scenarios": 4,
            "every_seed_all_four_mean_oriented_gains_positive": True,
            "minimum_mean_known_macro_f1_gain": -0.01,
            "minimum_mean_ece_gain": 0.0,
            "all_geometry_invariants_pass": True,
        },
        "claim_boundary": {
            "confirmation_is_mal_tls_component_evidence_only": True,
            "does_not_by_itself_replace_global_incumbent": "caeos_pairwise",
            "failure_is_reported_without_retuning": True,
        },
        "confirmation_metrics_observed_at_freeze": observed_metrics,
        "implementation_sha256": implementation_sha256,
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-protocol", type=Path, required=True)
    parser.add_argument("--pilot-analysis", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    pilot = json.loads(args.pilot_protocol.read_text(encoding="utf-8"))
    analysis = json.loads(args.pilot_analysis.read_text(encoding="utf-8"))
    names = (
        "caeos/model.py",
        "caeos/training.py",
        "train.py",
        "verify_geometry_preserving_adapter_checkpoints.py",
        "create_mal_tls_geometry_adapter_confirmation_protocol.py",
        "analyze_mal_tls_geometry_adapter_confirmation.py",
        "scripts/run_mal_tls_geometry_adapter_confirmation.sh",
    )
    for name in ("caeos/model.py", "caeos/training.py", "train.py"):
        if file_hash(args.project_root / name) != pilot["implementation_sha256"][name]:
            raise ValueError(f"pilot-bound implementation drift: {name}")
    protocol = create_protocol(
        pilot,
        analysis,
        pilot_protocol_file_sha256=file_hash(args.pilot_protocol),
        pilot_analysis_file_sha256=file_hash(args.pilot_analysis),
        implementation_sha256={name: file_hash(args.project_root / name) for name in names},
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
