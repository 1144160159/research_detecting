from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from create_strict_v4_external_confirmation_protocol import canonical_hash


COMPONENT_METRICS = (
    "conflict_auroc",
    "raw_conflict_auroc",
    "distance_auroc",
    "normal_distance_auroc",
    "uncertainty_auroc",
    "inverse_belief_auroc",
    "energy_auroc",
)


def diagnose(protocol: dict[str, Any], run_root: Path) -> dict[str, Any]:
    if protocol.get("schema_version") != "mal_tls_conservative_residual_pilot_protocol_v1":
        raise ValueError("unexpected residual pilot schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("residual pilot protocol SHA mismatch")
    seed = int(protocol["training"]["development_seed"])
    reference_profile = protocol["paired_methods"]["reference"]["encoder_profile"]
    candidate_profile = protocol["paired_methods"]["candidate"]["encoder_profile"]
    blocks = []
    for scenario in protocol["dataset"]["scenarios"]:
        reference = json.loads(
            (
                run_root
                / reference_profile
                / f"{scenario}_seed{seed}"
                / "metrics.json"
            ).read_text(encoding="utf-8")
        )
        candidate = json.loads(
            (
                run_root
                / candidate_profile
                / f"{scenario}_seed{seed}"
                / "metrics.json"
            ).read_text(encoding="utf-8")
        )
        gains = {
            name: float(candidate[name] - reference[name]) for name in COMPONENT_METRICS
        }
        blocks.append({"scenario": scenario, "component_auroc_gains": gains})
    means = {
        name: float(np.mean([block["component_auroc_gains"][name] for block in blocks]))
        for name in COMPONENT_METRICS
    }
    negative_counts = {
        name: int(sum(block["component_auroc_gains"][name] < 0.0 for block in blocks))
        for name in COMPONENT_METRICS
    }
    ranked = sorted(means, key=lambda name: (means[name], name))
    return {
        "schema_version": "mal_tls_conservative_residual_component_diagnostic_v1",
        "formal_selection_evidence": False,
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "paired_scenario_count": len(blocks),
        "mean_component_auroc_gains": means,
        "negative_scenario_counts": negative_counts,
        "most_degraded_components": ranked,
        "decision_use": (
            "hypothesis_generation_only; a new candidate requires a result-free "
            "protocol and a disjoint development seed"
        ),
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
        "blocks": blocks,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    result = diagnose(protocol, args.run_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
