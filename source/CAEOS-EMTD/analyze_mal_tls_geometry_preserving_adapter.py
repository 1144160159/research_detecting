from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from create_strict_v4_external_confirmation_protocol import canonical_hash


OPEN_METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")


def oriented_gain(candidate: float, reference: float, metric: str) -> float:
    return reference - candidate if metric == "unknown_fpr95" else candidate - reference


def analyze(protocol: dict[str, Any], run_root: Path) -> dict[str, Any]:
    if protocol.get("schema_version") != "mal_tls_geometry_preserving_adapter_protocol_v1":
        raise ValueError("unexpected geometry-preserving protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("geometry-preserving protocol SHA mismatch")
    seed = int(protocol["training"]["development_seed"])
    methods = protocol["paired_methods"]
    invariant_names = protocol["hard_invariants"]["invariant_metrics"]
    tolerance = float(
        protocol["hard_invariants"]["distance_and_conflict_metric_absolute_tolerance"]
    )
    blocks = []
    for scenario in protocol["dataset"]["scenarios"]:
        loaded = {}
        for role in ("reference", "candidate"):
            method = methods[role]
            root = run_root / method["encoder_profile"] / f"{scenario}_seed{seed}"
            metrics = json.loads((root / "metrics.json").read_text(encoding="utf-8"))
            metadata = json.loads((root / "data_metadata.json").read_text(encoding="utf-8"))
            if metrics.get("encoder_profile") != method["encoder_profile"]:
                raise ValueError(f"profile mismatch: {root}")
            if metrics.get("encoder_kinds") != method["encoder_kinds"]:
                raise ValueError(f"encoder mismatch: {root}")
            if metrics.get("evidence_adapter_kinds") != method["evidence_adapter_kinds"]:
                raise ValueError(f"adapter mismatch: {root}")
            if metrics.get("evidence_temperature_calibration") is not True:
                raise ValueError(f"temperature calibration missing: {root}")
            loaded[role] = (metrics, metadata, root)
        reference, reference_meta, _ = loaded["reference"]
        candidate, candidate_meta, candidate_root = loaded["candidate"]
        reference_fp = reference_meta["split_metadata"]["split_fingerprint"]["combined"]
        candidate_fp = candidate_meta["split_metadata"]["split_fingerprint"]["combined"]
        if not reference_fp or reference_fp != candidate_fp:
            raise ValueError(f"paired split mismatch: {scenario}")
        audit = json.loads(
            (candidate_root / "base_equivalence.json").read_text(encoding="utf-8")
        )
        invariant_differences = {
            name: float(abs(candidate[name] - reference[name])) for name in invariant_names
        }
        blocks.append(
            {
                "scenario": scenario,
                "oriented_gains": {
                    name: oriented_gain(candidate[name], reference[name], name)
                    for name in OPEN_METRICS
                },
                "known_macro_f1_gain": float(
                    candidate["known_macro_f1"] - reference["known_macro_f1"]
                ),
                "ece_gain": float(reference["ece"] - candidate["ece"]),
                "base_equivalence_passes": audit.get("passes") is True,
                "invariant_absolute_differences": invariant_differences,
                "geometry_invariants_pass": audit.get("passes") is True
                and max(invariant_differences.values()) <= tolerance,
            }
        )
    if len(blocks) * 2 != int(protocol["training"]["expected_development_runs"]):
        raise ValueError("geometry-preserving pilot run count is incomplete")
    means = {
        name: float(np.mean([block["oriented_gains"][name] for block in blocks]))
        for name in OPEN_METRICS
    }
    minimum = min(gain for block in blocks for gain in block["oriented_gains"].values())
    nonregressing = sum(
        all(gain >= 0.0 for gain in block["oriented_gains"].values()) for block in blocks
    )
    mean_known = float(np.mean([block["known_macro_f1_gain"] for block in blocks]))
    mean_ece = float(np.mean([block["ece_gain"] for block in blocks]))
    gate = protocol["development_gate"]
    checks = {
        "all_four_mean_oriented_gains_positive": all(value > 0.0 for value in means.values()),
        "minimum_scenario_metric_gain": minimum >= float(gate["minimum_scenario_metric_gain"]),
        "minimum_all_metric_nonregressing_scenarios": nonregressing
        >= int(gate["minimum_all_metric_nonregressing_scenarios"]),
        "minimum_mean_known_macro_f1_gain": mean_known
        >= float(gate["minimum_mean_known_macro_f1_gain"]),
        "minimum_mean_ece_gain": mean_ece >= float(gate["minimum_mean_ece_gain"]),
        "all_geometry_invariants_pass": all(
            block["geometry_invariants_pass"] for block in blocks
        ),
    }
    passes = all(checks.values())
    return {
        "schema_version": "mal_tls_geometry_preserving_adapter_analysis_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "paired_scenario_count": len(blocks),
        "mean_oriented_gains": means,
        "minimum_scenario_metric_gain": float(minimum),
        "all_metric_nonregressing_scenario_count": int(nonregressing),
        "mean_known_macro_f1_gain": mean_known,
        "mean_ece_gain": mean_ece,
        "checks": checks,
        "passes": passes,
        "decision": (
            "freeze_for_reserved_seed_confirmation"
            if passes
            else "retain_caeos_pairwise_and_reject_geometry_adapter"
        ),
        "blocks": blocks,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(json.loads(args.protocol.read_text(encoding="utf-8")), args.run_root)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
