from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from create_strict_v4_external_confirmation_protocol import canonical_hash


METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")


def oriented_gain(candidate: float, reference: float, metric: str) -> float:
    return reference - candidate if metric == "unknown_fpr95" else candidate - reference


def analyze(protocol: dict[str, Any], run_root: Path) -> dict[str, Any]:
    if protocol.get("schema_version") != "mal_tls_heterogeneous_pilot_protocol_v1":
        raise ValueError("unexpected heterogeneous pilot schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("heterogeneous pilot protocol SHA mismatch")
    seed = int(protocol["training"]["development_seed"])
    methods = protocol["paired_methods"]
    blocks = []
    for scenario in protocol["dataset"]["scenarios"]:
        loaded = {}
        for role in ("reference", "candidate"):
            profile = methods[role]["encoder_profile"]
            root = run_root / profile / f"{scenario}_seed{seed}"
            metrics = json.loads((root / "metrics.json").read_text(encoding="utf-8"))
            metadata = json.loads(
                (root / "data_metadata.json").read_text(encoding="utf-8")
            )
            if metrics.get("encoder_profile") != profile:
                raise ValueError(f"encoder profile mismatch: {root}")
            if metadata.get("encoder_kinds") != methods[role]["encoder_kinds"]:
                raise ValueError(f"encoder kinds mismatch: {root}")
            loaded[role] = (metrics, metadata)
        reference, reference_meta = loaded["reference"]
        candidate, candidate_meta = loaded["candidate"]
        reference_fp = reference_meta.get("split_metadata", {}).get(
            "split_fingerprint", {}
        ).get("combined")
        candidate_fp = candidate_meta.get("split_metadata", {}).get(
            "split_fingerprint", {}
        ).get("combined")
        if not reference_fp or reference_fp != candidate_fp:
            raise ValueError(f"paired split fingerprint mismatch: {scenario}")
        gains = {
            metric: oriented_gain(candidate[metric], reference[metric], metric)
            for metric in METRICS
        }
        blocks.append(
            {
                "scenario": scenario,
                "seed": seed,
                "split_fingerprint": reference_fp,
                "oriented_gains": gains,
                "known_macro_f1_gain": float(
                    candidate["known_macro_f1"] - reference["known_macro_f1"]
                ),
                "ece_gain": float(reference["ece"] - candidate["ece"]),
            }
        )
    expected = int(protocol["training"]["expected_development_runs"])
    if len(blocks) * 2 != expected:
        raise ValueError("heterogeneous pilot run count is incomplete")
    means = {
        metric: float(np.mean([block["oriented_gains"][metric] for block in blocks]))
        for metric in METRICS
    }
    minimum = min(
        gain for block in blocks for gain in block["oriented_gains"].values()
    )
    nonregressing = sum(
        all(gain >= 0.0 for gain in block["oriented_gains"].values())
        for block in blocks
    )
    gate = protocol["development_gate"]
    checks = {
        "all_four_mean_oriented_gains_positive": all(v > 0.0 for v in means.values()),
        "minimum_scenario_metric_gain": minimum
        >= float(gate["minimum_scenario_metric_gain"]),
        "minimum_all_metric_nonregressing_scenarios": nonregressing
        >= int(gate["minimum_all_metric_nonregressing_scenarios"]),
        "minimum_mean_known_macro_f1_gain": float(
            np.mean([block["known_macro_f1_gain"] for block in blocks])
        )
        >= float(gate["minimum_mean_known_macro_f1_gain"]),
        "minimum_mean_ece_gain": float(
            np.mean([block["ece_gain"] for block in blocks])
        )
        >= float(gate["minimum_mean_ece_gain"]),
    }
    passes = all(checks.values())
    return {
        "schema_version": "mal_tls_heterogeneous_pilot_analysis_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "paired_scenario_count": len(blocks),
        "mean_oriented_gains": means,
        "minimum_scenario_metric_gain": float(minimum),
        "all_metric_nonregressing_scenario_count": int(nonregressing),
        "checks": checks,
        "passes": passes,
        "decision": (
            "freeze_for_reserved_seed_confirmation"
            if passes
            else "retain_multi_view_claim_and_revise_encoder_candidate"
        ),
        "blocks": blocks,
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Mal_TLS heterogeneous encoder pilot",
        "",
        f"Decision: `{result['decision']}`.",
        "",
        "| Metric | Mean oriented gain |",
        "|---|---:|",
    ]
    for metric, value in result["mean_oriented_gains"].items():
        lines.append(f"| {metric} | {value:+.6f} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    result = analyze(protocol, args.run_root)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "analysis.md").write_text(render(result), encoding="utf-8")
    print(render(result), end="")


if __name__ == "__main__":
    main()
