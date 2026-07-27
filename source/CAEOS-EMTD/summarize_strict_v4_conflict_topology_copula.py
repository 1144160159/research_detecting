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
    if protocol.get("schema_version") != "strict_v4_conflict_topology_copula_protocol_v1":
        raise ValueError("unexpected conflict-topology copula protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("conflict-topology copula protocol SHA mismatch")
    blocks = []
    for record in protocol["pilot"]["inputs"]:
        path = run_root / record["suite"] / f'{record["scenario"]}_seed7' / "metrics.json"
        if not path.is_file():
            raise FileNotFoundError(f"missing conflict-topology result: {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("protocol_manifest_sha256") != protocol["manifest_sha256"]:
            raise ValueError("conflict-topology result binding mismatch")
        reference = payload["reports"]["reference"]
        candidate = payload["reports"]["candidate"]
        gains = {
            name: oriented_gain(candidate[name], reference[name], name)
            for name in METRICS
        }
        diagnostics = payload["diagnostics"]
        blocks.append(
            {
                "suite": record["suite"],
                "scenario": record["scenario"],
                "oriented_gains": gains,
                "four_metric_mean_gain": float(np.mean(list(gains.values()))),
                "prediction_array_equal": diagnostics["prediction_array_equal"] is True,
                "known_macro_f1_absolute_difference": float(
                    diagnostics["known_macro_f1_absolute_difference"]
                ),
            }
        )
    if len(blocks) != 14:
        raise ValueError("conflict-topology pilot result count is incomplete")

    overall = {
        metric: float(np.mean([block["oriented_gains"][metric] for block in blocks]))
        for metric in METRICS
    }
    by_suite = {}
    for suite in sorted({block["suite"] for block in blocks}):
        selected = [block for block in blocks if block["suite"] == suite]
        by_suite[suite] = {
            metric: float(
                np.mean([block["oriented_gains"][metric] for block in selected])
            )
            for metric in METRICS
        }
    suite_minimum = min(
        value for suite in by_suite.values() for value in suite.values()
    )
    fully_nonregressing_suites = sum(
        all(value >= -1e-12 for value in suite.values()) for suite in by_suite.values()
    )
    positive_scenarios = sum(block["four_metric_mean_gain"] > 0.0 for block in blocks)
    gate = protocol["pilot"]["gate"]
    checks = {
        "all_four_overall_oriented_means_strictly_positive": all(
            value > 0.0 for value in overall.values()
        ),
        "minimum_suite_metric_gain": suite_minimum
        >= float(gate["minimum_suite_metric_gain"]),
        "minimum_fully_nonregressing_suite_count": fully_nonregressing_suites
        >= int(gate["minimum_fully_nonregressing_suite_count"]),
        "minimum_positive_scenario_four_metric_mean_count": positive_scenarios
        >= int(gate["minimum_positive_scenario_four_metric_mean_count"]),
        "prediction_array_equal_in_all_scenarios": all(
            block["prediction_array_equal"] for block in blocks
        ),
        "known_macro_f1_absolute_tolerance": max(
            block["known_macro_f1_absolute_difference"] for block in blocks
        )
        <= float(gate["known_macro_f1_absolute_tolerance"]),
    }
    passes = all(checks.values())
    return {
        "schema_version": "strict_v4_conflict_topology_copula_analysis_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "scenario_count": len(blocks),
        "suite_count": len(by_suite),
        "blocks": blocks,
        "overall_oriented_gains": overall,
        "by_suite_oriented_gains": by_suite,
        "minimum_suite_metric_gain": suite_minimum,
        "fully_nonregressing_suite_count": fully_nonregressing_suites,
        "positive_scenario_four_metric_mean_count": positive_scenarios,
        "checks": checks,
        "passes": passes,
        "decision": (
            "freeze_for_reserved_seed_confirmation"
            if passes
            else "retain_caeos_pairwise_and_reject_conflict_topology_copula"
        ),
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Conflict-Topology Copula Pilot",
        "",
        f"- Decision: `{result['decision']}`",
        f"- Passes: `{result['passes']}`",
        f"- Scenarios/suites: `{result['scenario_count']}/{result['suite_count']}`",
        f"- Minimum suite-metric gain: `{result['minimum_suite_metric_gain']:.6f}`",
        "",
        "## Overall oriented gains",
        "",
    ]
    lines.extend(
        f"- {name}: `{value:.6f}`"
        for name, value in result["overall_oriented_gains"].items()
    )
    lines.extend(["", "## Gate checks", ""])
    lines.extend(f"- {name}: `{value}`" for name, value in result["checks"].items())
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
    (args.output_dir / "pilot_complete").touch()


if __name__ == "__main__":
    main()
