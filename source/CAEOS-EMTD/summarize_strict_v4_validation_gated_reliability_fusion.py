from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from create_strict_v4_external_confirmation_protocol import canonical_hash


METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")


def gain(candidate: float, reference: float, metric: str) -> float:
    return reference - candidate if metric == "unknown_fpr95" else candidate - reference


def analyze(protocol: dict[str, Any], run_root: Path) -> dict[str, Any]:
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("validation-gated protocol SHA mismatch")
    blocks = []
    for record in protocol["pilot"]["inputs"]:
        path = run_root / record["suite"] / f'{record["scenario"]}_seed307' / "metrics.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        if (
            payload.get("schema_version") != "strict_v4_validation_gated_reliability_fusion_metrics_v1"
            or payload.get("protocol_manifest_sha256") != protocol["manifest_sha256"]
        ):
            raise ValueError(f"candidate result binding mismatch: {path}")
        reference, candidate = payload["reports"]["reference"], payload["reports"]["candidate"]
        oriented = {metric: gain(candidate[metric], reference[metric], metric) for metric in METRICS}
        diagnostics = payload["diagnostics"]
        blocks.append({
            "suite": record["suite"], "scenario": record["scenario"],
            "enabled": diagnostics["enabled"] is True,
            "exact_fallback": diagnostics["exact_fallback"] is True,
            "known_macro_f1_gain": float(diagnostics["known_macro_f1_gain"]),
            "prediction_change_rate": float(diagnostics["prediction_change_rate"]),
            "temperature_reconstruction_error": max(
                float(diagnostics["validation_temperature_reconstruction_max_abs_error"]),
                float(diagnostics["test_temperature_reconstruction_max_abs_error"]),
            ),
            "oriented_gains": oriented,
            "four_metric_mean_gain": float(np.mean(list(oriented.values()))),
            "unknown_or_test_labels_used": diagnostics[
                "unknown_or_test_labels_used_for_reliability_gate_threshold_or_prediction"
            ] is True,
        })
    if len(blocks) != 14:
        raise ValueError("validation-gated result count is incomplete")
    by_suite = {}
    for suite in sorted({block["suite"] for block in blocks}):
        selected = [block for block in blocks if block["suite"] == suite]
        by_suite[suite] = {
            metric: float(np.mean([block["oriented_gains"][metric] for block in selected]))
            for metric in METRICS
        }
    overall = {
        metric: float(np.mean([values[metric] for values in by_suite.values()]))
        for metric in METRICS
    }
    suite_minimum = min(value for values in by_suite.values() for value in values.values())
    nonregressing = sum(all(value >= -1e-12 for value in values.values()) for values in by_suite.values())
    positive = sum(block["four_metric_mean_gain"] > 0.0 for block in blocks)
    enabled = sum(block["enabled"] for block in blocks)
    known = [block["known_macro_f1_gain"] for block in blocks]
    gate = protocol["pilot"]["gate"]
    checks = {
        "minimum_enabled_scenarios": enabled >= gate["minimum_enabled_scenarios"],
        "all_four_equal_suite_oriented_means_strictly_positive": all(value > 0.0 for value in overall.values()),
        "minimum_suite_metric_gain": suite_minimum >= gate["minimum_suite_metric_gain"],
        "minimum_fully_nonregressing_suite_count": nonregressing >= gate["minimum_fully_nonregressing_suite_count"],
        "minimum_positive_scenario_four_metric_mean_count": positive >= gate["minimum_positive_scenario_four_metric_mean_count"],
        "minimum_mean_known_macro_f1_gain": float(np.mean(known)) >= gate["minimum_mean_known_macro_f1_gain"],
        "minimum_scenario_known_macro_f1_gain": min(known) >= gate["minimum_scenario_known_macro_f1_gain"],
        "maximum_temperature_reconstruction_error": max(block["temperature_reconstruction_error"] for block in blocks) <= gate["maximum_temperature_reconstruction_error"],
        "exact_fallback_for_every_disabled_scenario": all(block["enabled"] or block["exact_fallback"] for block in blocks),
        "no_unknown_or_test_labels_for_gate": not any(block["unknown_or_test_labels_used"] for block in blocks),
    }
    passes = all(checks.values())
    return {
        "schema_version": "strict_v4_validation_gated_reliability_fusion_analysis_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "scenario_count": len(blocks), "suite_count": len(by_suite),
        "enabled_scenario_count": enabled,
        "blocks": blocks,
        "overall_equal_suite_oriented_gains": overall,
        "by_suite_oriented_gains": by_suite,
        "minimum_suite_metric_gain": suite_minimum,
        "fully_nonregressing_suite_count": nonregressing,
        "positive_scenario_four_metric_mean_count": positive,
        "mean_known_macro_f1_gain": float(np.mean(known)),
        "minimum_known_macro_f1_gain": min(known),
        "checks": checks, "passes": passes,
        "decision": (
            "freeze_seed311_313_full102_confirmation"
            if passes else "retain_caeos_pairwise_and_reject_validation_gated_reliability_fusion"
        ),
    }


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
    (args.output_dir / "pilot_complete").touch()
    print(json.dumps({"passes": result["passes"], "decision": result["decision"]}))


if __name__ == "__main__":
    main()
