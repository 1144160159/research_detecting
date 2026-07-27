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


def _load_run(
    root: Path, profile: str, expected_kinds: list[str]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    metrics = json.loads((root / "metrics.json").read_text(encoding="utf-8"))
    metadata = json.loads((root / "data_metadata.json").read_text(encoding="utf-8"))
    temperature = json.loads(
        (root / "evidence_temperature.json").read_text(encoding="utf-8")
    )
    if metrics.get("encoder_profile") != profile:
        raise ValueError(f"encoder profile mismatch: {root}")
    if metadata.get("encoder_kinds") != expected_kinds:
        raise ValueError(f"encoder kinds mismatch: {root}")
    if metrics.get("evidence_temperature_calibration") is not True:
        raise ValueError(f"temperature calibration missing: {root}")
    if temperature.get("enabled") is not True:
        raise ValueError(f"temperature evidence missing: {root}")
    if temperature.get("fit_split") != "known_only_validation":
        raise ValueError(f"temperature fit split mismatch: {root}")
    if temperature.get("unknown_or_test_labels_used") is not False:
        raise ValueError(f"temperature leakage marker failed: {root}")
    if abs(float(metrics["evidence_temperature"]) - float(temperature["temperature"])) > 1e-12:
        raise ValueError(f"temperature value mismatch: {root}")
    return metrics, metadata, temperature


def analyze(protocol: dict[str, Any], run_root: Path) -> dict[str, Any]:
    if protocol.get("schema_version") != "mal_tls_conservative_residual_pilot_protocol_v1":
        raise ValueError("unexpected residual pilot schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("residual pilot protocol SHA mismatch")
    seed = int(protocol["training"]["development_seed"])
    methods = protocol["paired_methods"]
    blocks = []
    for scenario in protocol["dataset"]["scenarios"]:
        loaded = {}
        for role in ("reference", "candidate"):
            method = methods[role]
            profile = method["encoder_profile"]
            root = run_root / profile / f"{scenario}_seed{seed}"
            loaded[role] = _load_run(root, profile, method["encoder_kinds"])
        reference, reference_meta, reference_temperature = loaded["reference"]
        candidate, candidate_meta, candidate_temperature = loaded["candidate"]
        reference_fp = reference_meta["split_metadata"]["split_fingerprint"]["combined"]
        candidate_fp = candidate_meta["split_metadata"]["split_fingerprint"]["combined"]
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
                "reference_temperature": float(reference_temperature["temperature"]),
                "candidate_temperature": float(candidate_temperature["temperature"]),
            }
        )
    if len(blocks) * 2 != int(protocol["training"]["expected_development_runs"]):
        raise ValueError("residual pilot run count is incomplete")
    means = {
        metric: float(np.mean([block["oriented_gains"][metric] for block in blocks]))
        for metric in METRICS
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
    }
    passes = all(checks.values())
    return {
        "schema_version": "mal_tls_conservative_residual_pilot_analysis_v1",
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
            else "retain_caeos_pairwise_and_reject_residual_candidate"
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
