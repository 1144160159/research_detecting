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


def analyze(protocol: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    if protocol.get("schema_version") != "strict_v4_tail_aware_pilot_protocol_v1":
        raise ValueError("unexpected tail-aware pilot protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("tail-aware pilot protocol SHA mismatch")
    expected = int(protocol["pilot"]["expected_run_count"])
    if len(rows) != expected:
        raise ValueError("tail-aware pilot run count is incomplete")
    candidate_name = protocol["candidate"]["risk_endpoint"]
    reference_name = protocol["candidate"]["reference_endpoint"]
    seen = set()
    blocks = []
    selected_count = 0
    split_fingerprints = []
    for row in rows:
        identity = (str(row["suite"]), str(row["scenario"]), int(row["seed"]))
        if identity in seen:
            raise ValueError("duplicate tail-aware pilot run")
        seen.add(identity)
        payload = row["metrics"]
        if payload.get("arguments", {}).get("risk_selection") != protocol["candidate"]["risk_selection"]:
            raise ValueError("tail-aware pilot risk selection mismatch")
        details = payload.get("risk_selection_details", {})
        if details.get("unknown_or_test_labels_used_for_selection") is not False:
            raise ValueError("tail-aware pilot runtime leakage guard failed")
        learned = details.get("pseudo_unknown_learned_blend", {})
        if learned.get("schema_version") != "tail_aware_pairwise_ranking_head_v1":
            raise ValueError("tail-aware ranking head audit is absent")
        if learned.get("unknown_or_test_labels_used") is not False:
            raise ValueError("tail-aware ranking head leakage guard failed")
        reports = payload.get("reports", {})
        if candidate_name not in reports or reference_name not in reports:
            raise ValueError("tail-aware pilot reports are incomplete")
        candidate = reports[candidate_name]
        reference = reports[reference_name]
        gains = {
            metric: oriented_gain(candidate[metric], reference[metric], metric)
            for metric in METRICS
        }
        known_gain = float(candidate["known_macro_f1"] - reference["known_macro_f1"])
        blocks.append(
            {
                "suite": identity[0],
                "scenario": identity[1],
                "seed": identity[2],
                "oriented_gains": gains,
                "known_macro_f1_gain": known_gain,
                "selected_risk": payload.get("selected_risk"),
            }
        )
        selected_count += payload.get("selected_risk") == candidate_name
        fingerprint = payload.get("split_metadata", {}).get("split_fingerprint")
        if not fingerprint:
            raise ValueError("tail-aware pilot split fingerprint is absent")
        split_fingerprints.append(str(fingerprint))

    overall = {
        metric: float(np.mean([block["oriented_gains"][metric] for block in blocks]))
        for metric in METRICS
    }
    suites = sorted({block["suite"] for block in blocks})
    by_suite = {
        suite: {
            metric: float(
                np.mean(
                    [
                        block["oriented_gains"][metric]
                        for block in blocks
                        if block["suite"] == suite
                    ]
                )
            )
            for metric in METRICS
        }
        for suite in suites
    }
    minimum_suite_gain = min(
        value for values in by_suite.values() for value in values.values()
    )
    safe_suite_count = sum(
        all(value >= 0.0 for value in values.values())
        for values in by_suite.values()
    )
    gate = protocol["pilot"]["gate"]
    checks = {
        "all_four_overall_oriented_means_positive": all(
            value > 0.0 for value in overall.values()
        ),
        "minimum_suite_metric_gain": minimum_suite_gain
        >= float(gate["minimum_suite_metric_gain"]),
        "minimum_fully_nonregressing_suite_count": safe_suite_count
        >= int(gate["minimum_fully_nonregressing_suite_count"]),
        "known_macro_f1_nonregression": min(
            block["known_macro_f1_gain"] for block in blocks
        )
        >= -1e-12,
        "candidate_endpoint_must_be_exercised": selected_count > 0,
    }
    return {
        "schema_version": "strict_v4_tail_aware_pilot_analysis_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "validation": {
            "passes": True,
            "run_count": len(blocks),
            "suite_count": len(suites),
            "unique_split_fingerprint_count": len(set(split_fingerprints)),
            "unknown_or_test_labels_used_for_runtime_selection": False,
            "pilot_test_labels_used_for_development_decision": True,
        },
        "overall_oriented_gains": overall,
        "by_suite_oriented_gains": by_suite,
        "minimum_suite_metric_gain": float(minimum_suite_gain),
        "fully_nonregressing_suite_count": int(safe_suite_count),
        "candidate_endpoint_selected_count": int(selected_count),
        "checks": checks,
        "passes": all(checks.values()),
        "decision": (
            "freeze_for_new_seed_confirmation"
            if all(checks.values())
            else "reject_tail_aware_candidate"
        ),
        "blocks": blocks,
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 tail-aware ranking pilot",
        "",
        f"Decision: `{result['decision']}`.",
        f"Candidate endpoint selected in {result['candidate_endpoint_selected_count']} runs.",
        "",
        "| Metric | Oriented gain |",
        "|---|---:|",
    ]
    for metric, value in result["overall_oriented_gains"].items():
        lines.append(f"| {metric} | {value:+.6f} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    rows = []
    seed = int(protocol["pilot"]["development_seed"])
    for suite, scenarios in protocol["pilot"]["scenarios"].items():
        for scenario in scenarios:
            path = args.run_root / suite / f"{scenario}_seed{seed}" / "metrics.json"
            rows.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "seed": seed,
                    "metrics": json.loads(path.read_text(encoding="utf-8")),
                }
            )
    result = analyze(protocol, rows)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "analysis.md").write_text(render(result), encoding="utf-8")
    print(render(result), end="")


if __name__ == "__main__":
    main()
