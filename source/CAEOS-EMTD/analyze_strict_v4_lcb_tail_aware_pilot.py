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
    if protocol.get("schema_version") != "strict_v4_lcb_tail_aware_pilot_protocol_v1":
        raise ValueError("unexpected LCB tail-aware pilot protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("LCB tail-aware pilot protocol SHA mismatch")
    if len(rows) != int(protocol["pilot"]["expected_run_count"]):
        raise ValueError("LCB tail-aware pilot run count is incomplete")

    candidate_cfg = protocol["candidate"]
    candidate_name = candidate_cfg["risk_endpoint"]
    reference_name = candidate_cfg["reference_endpoint"]
    seen = set()
    blocks = []
    selected_count = 0
    fingerprints = []
    for row in rows:
        identity = (str(row["suite"]), str(row["scenario"]), int(row["seed"]))
        if identity in seen:
            raise ValueError("duplicate LCB pilot run")
        seen.add(identity)
        payload = row["metrics"]
        arguments = payload.get("arguments", {})
        if arguments.get("risk_selection") != candidate_cfg["risk_selection"]:
            raise ValueError("LCB pilot risk selection mismatch")
        if arguments.get("risk_policy_name") != candidate_cfg["risk_policy_name"]:
            raise ValueError("LCB pilot risk policy mismatch")
        frozen_arguments = {
            "pseudo_unknown_max_alpha": "maximum_alpha",
            "pseudo_unknown_min_fold_gain": "minimum_fold_gain",
            "boundary_hard_pseudo_fraction": "hard_pseudo_fraction",
            "boundary_interpolation": "boundary_interpolation",
            "boundary_max_per_task": "boundary_max_per_task",
            "tail_aware_confidence_z": "confidence_z",
            "tail_aware_min_metric_lcb_gain": "minimum_metric_lcb_gain",
            "tail_aware_min_aupr_lcb_gain": "minimum_aupr_lcb_gain",
            "tail_aware_min_aupr_fold_gain": "minimum_aupr_fold_gain",
        }
        for argument_name, protocol_name in frozen_arguments.items():
            if argument_name not in arguments:
                raise ValueError(f"LCB frozen argument is absent: {argument_name}")
            if float(arguments[argument_name]) != float(candidate_cfg[protocol_name]):
                raise ValueError(f"LCB frozen argument mismatch: {argument_name}")
        details = payload.get("risk_selection_details", {})
        if details.get("unknown_or_test_labels_used_for_selection") is not False:
            raise ValueError("LCB pilot runtime leakage guard failed")
        learned = details.get("pseudo_unknown_learned_blend", {})
        if learned.get("schema_version") != "tail_aware_lcb_pairwise_ranking_head_v1":
            raise ValueError("LCB ranking audit is absent")
        if learned.get("unknown_or_test_labels_used") is not False:
            raise ValueError("LCB ranking leakage guard failed")
        if learned.get("training_objective") != candidate_cfg["training_objective"]:
            raise ValueError("LCB ranking objective mismatch")
        frozen_values = {
            "confidence_z": "confidence_z",
            "minimum_metric_lcb_gain": "minimum_metric_lcb_gain",
            "minimum_aupr_lcb_gain": "minimum_aupr_lcb_gain",
            "minimum_aupr_fold_gain": "minimum_aupr_fold_gain",
        }
        for learned_name, protocol_name in frozen_values.items():
            if float(learned[learned_name]) != float(candidate_cfg[protocol_name]):
                raise ValueError(f"LCB frozen parameter mismatch: {learned_name}")
        gate_checks = learned.get("gate_checks", {})
        required_gate_checks = {
            "all_metric_means_above_minimum",
            "all_metric_lcbs_above_minimum",
            "aupr_lcb_above_minimum",
            "aupr_worst_fold_above_minimum",
        }
        if set(gate_checks) != required_gate_checks:
            raise ValueError("LCB known-only gate checks are incomplete")
        learned_passes = bool(learned.get("passes"))
        if learned_passes != all(bool(gate_checks[name]) for name in required_gate_checks):
            raise ValueError("LCB learned pass flag disagrees with known-only gates")
        selected_alpha = float(learned.get("selected_alpha", -1.0))
        development_alpha = float(learned.get("development_selected_alpha", -1.0))
        if not 0.0 < development_alpha <= float(candidate_cfg["maximum_alpha"]):
            raise ValueError("LCB development alpha is outside the frozen range")
        if selected_alpha != (development_alpha if learned_passes else 0.0):
            raise ValueError("LCB selected alpha disagrees with known-only gates")
        robust_gate = details.get("pseudo_unknown_robust_fold_gate", {})
        if float(robust_gate.get("required_minimum_fold_gain", float("nan"))) != float(
            candidate_cfg["minimum_fold_gain"]
        ):
            raise ValueError("LCB robust fold threshold mismatch")
        if robust_gate.get("mean_gain_gate_passes") is not learned_passes:
            raise ValueError("LCB robust gate disagrees with learned gate")
        expected_robust_pass = bool(
            learned_passes and robust_gate.get("fold_stability_gate_passes") is True
        )
        if robust_gate.get("passes") is not expected_robust_pass:
            raise ValueError("LCB robust pass flag is inconsistent")
        if details.get("pseudo_unknown_gate_passes") is not expected_robust_pass:
            raise ValueError("LCB runtime gate flag is inconsistent")
        reports = payload.get("reports", {})
        if candidate_name not in reports or reference_name not in reports:
            raise ValueError("LCB pilot reports are incomplete")
        expected_endpoint = candidate_name if expected_robust_pass else reference_name
        if payload.get("selected_risk") != expected_endpoint:
            raise ValueError("LCB selected endpoint disagrees with frozen runtime gates")
        candidate = reports[candidate_name]
        reference = reports[reference_name]
        gains = {
            metric: oriented_gain(candidate[metric], reference[metric], metric)
            for metric in METRICS
        }
        blocks.append(
            {
                "suite": identity[0],
                "scenario": identity[1],
                "seed": identity[2],
                "oriented_gains": gains,
                "known_macro_f1_gain": float(
                    candidate["known_macro_f1"] - reference["known_macro_f1"]
                ),
                "selected_risk": payload.get("selected_risk"),
                "known_only_gate_checks": learned.get("gate_checks", {}),
            }
        )
        selected_count += payload.get("selected_risk") == candidate_name
        fingerprint = payload.get("split_metadata", {}).get("split_fingerprint")
        if not fingerprint:
            raise ValueError("LCB pilot split fingerprint is absent")
        fingerprints.append(str(fingerprint))

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
        value for suite_values in by_suite.values() for value in suite_values.values()
    )
    safe_suite_count = sum(
        all(value >= 0.0 for value in suite_values.values())
        for suite_values in by_suite.values()
    )
    gate = protocol["pilot"]["gate"]
    checks = {
        "all_four_overall_oriented_means_strictly_positive": all(
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
        "minimum_candidate_endpoint_selected_count": selected_count
        >= int(gate["minimum_candidate_endpoint_selected_count"]),
    }
    passes = all(checks.values())
    return {
        "schema_version": "strict_v4_lcb_tail_aware_pilot_analysis_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "validation": {
            "passes": True,
            "run_count": len(blocks),
            "suite_count": len(suites),
            "unique_split_fingerprint_count": len(set(fingerprints)),
            "unknown_or_test_labels_used_for_runtime_selection": False,
            "pilot_test_labels_used_for_development_decision": True,
        },
        "overall_oriented_gains": overall,
        "by_suite_oriented_gains": by_suite,
        "minimum_suite_metric_gain": float(minimum_suite_gain),
        "fully_nonregressing_suite_count": int(safe_suite_count),
        "candidate_endpoint_selected_count": int(selected_count),
        "checks": checks,
        "passes": passes,
        "decision": (
            "freeze_for_new_seed_confirmation"
            if passes
            else "retain_caeos_pairwise_incumbent"
        ),
        "blocks": blocks,
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 LCB tail-aware pilot",
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
    seed = int(protocol["pilot"]["development_seed"])
    rows = []
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
