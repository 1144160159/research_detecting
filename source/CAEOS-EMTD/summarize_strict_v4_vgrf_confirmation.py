from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from create_strict_v4_external_confirmation_protocol import canonical_hash
from caeos.vgrf_confirmation_validation import (
    validate_candidate_result,
    validate_reference_result,
)


METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")


def gain(candidate: float, reference: float, metric: str) -> float:
    return reference - candidate if metric == "unknown_fpr95" else candidate - reference


def analyze(
    protocol: dict[str, Any],
    run_root: Path,
    reference_root: Path,
    project_root: Path,
) -> dict[str, Any]:
    if protocol.get("schema_version") != (
        "strict_v4_vgrf_confirmation_protocol_v1"
    ):
        raise ValueError("unexpected VGRF confirmation protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("VGRF confirmation protocol SHA mismatch")
    if protocol.get("status") != (
        "frozen_after_positive_seed307_pilot_before_seed311_313_full102_metrics"
    ):
        raise ValueError("VGRF confirmation protocol is not frozen")
    inputs = protocol["confirmation"]["inputs"]
    identities = {
        (
            record["suite"],
            record["scenario"],
            record["training_seed"],
        )
        for record in inputs
    }
    if len(inputs) != 204 or len(identities) != 204:
        raise ValueError("VGRF confirmation input universe is not 204 unique rows")
    if {record["training_seed"] for record in inputs} != {311, 313}:
        raise ValueError("VGRF confirmation seed universe mismatch")
    if len({record["suite"] for record in inputs}) != 7:
        raise ValueError("VGRF confirmation suite universe mismatch")
    rows: list[dict[str, Any]] = []
    for record in inputs:
        suffix = f'{record["scenario"]}_seed{record["training_seed"]}'
        path = run_root / record["suite"] / suffix / "metrics.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        reference_path = reference_root / record["suite"] / suffix
        validate_reference_result(
            reference_path, record, protocol, project_root
        )
        validate_candidate_result(
            payload, record, protocol, reference_path
        )
        reference, candidate = payload["reports"]["reference"], payload["reports"]["candidate"]
        gains = {metric: gain(float(candidate[metric]), float(reference[metric]), metric) for metric in METRICS}
        if not np.isfinite(
            np.asarray(list(gains.values()), dtype=np.float64)
        ).all():
            raise ValueError(f"non-finite oriented gain: {path}")
        diagnostics = payload["diagnostics"]
        rows.append({
            "suite": record["suite"], "scenario": record["scenario"], "seed": record["training_seed"],
            "oriented_gains": gains, "composite_gain": float(np.mean(list(gains.values()))),
            "known_macro_f1_gain": float(candidate["known_macro_f1"] - reference["known_macro_f1"]),
            "enabled": diagnostics["enabled"], "exact_fallback": diagnostics["exact_fallback"],
            "temperature_error": max(diagnostics["validation_temperature_reconstruction_max_abs_error"], diagnostics["test_temperature_reconstruction_max_abs_error"]),
            "no_unknown_or_test_labels_for_gate": diagnostics[
                "unknown_or_test_labels_used_for_reliability_gate_threshold_or_prediction"
            ] is False,
            "test_labels_used_for_final_metrics_only": diagnostics[
                "test_labels_used_for_final_metrics_only"
            ] is True,
        })
    by_suite = {}
    for suite in sorted({row["suite"] for row in rows}):
        selected = [row for row in rows if row["suite"] == suite]
        by_suite[suite] = {metric: float(np.mean([row["oriented_gains"][metric] for row in selected])) for metric in METRICS}
        by_suite[suite]["composite_gain"] = float(np.mean([row["composite_gain"] for row in selected]))
    overall = {metric: float(np.mean([value[metric] for value in by_suite.values()])) for metric in METRICS}
    rng = np.random.default_rng(protocol["confirmation"]["bootstrap"]["seed"])
    suites = sorted(by_suite)
    boot = []
    for _ in range(protocol["confirmation"]["bootstrap"]["replicates"]):
        sampled_suites = rng.choice(suites, size=len(suites), replace=True)
        suite_values = []
        for suite in sampled_suites:
            candidates = [row["composite_gain"] for row in rows if row["suite"] == suite]
            suite_values.append(float(np.mean(rng.choice(candidates, size=len(candidates), replace=True))))
        boot.append(float(np.mean(suite_values)))
    ci = [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))]
    gate = protocol["confirmation"]["gate"]
    enabled = sum(row["enabled"] for row in rows)
    nonregressing = sum(all(by_suite[s][m] >= 0.0 for m in METRICS) for s in suites)
    minimum_suite_metric = min(by_suite[s][m] for s in suites for m in METRICS)
    positive = sum(row["composite_gain"] > 0.0 for row in rows)
    known = [row["known_macro_f1_gain"] for row in rows]
    checks = {
        "all_four_equal_suite_oriented_means_strictly_positive": all(overall[m] > 0.0 for m in METRICS),
        "primary_bootstrap_lower_bound_strictly_positive": ci[0] > 0.0,
        "minimum_fully_nonregressing_suite_count": nonregressing >= gate["minimum_fully_nonregressing_suite_count"],
        "minimum_suite_metric_gain": minimum_suite_metric >= gate["minimum_suite_metric_gain"],
        "minimum_enabled_scenarios": enabled >= gate["minimum_enabled_scenarios"],
        "minimum_positive_scenario_composite_count": positive >= gate["minimum_positive_scenario_composite_count"],
        "minimum_mean_known_macro_f1_gain": float(np.mean(known)) >= gate["minimum_mean_known_macro_f1_gain"],
        "minimum_scenario_known_macro_f1_gain": min(known) >= gate["minimum_scenario_known_macro_f1_gain"],
        "maximum_temperature_reconstruction_error": max(row["temperature_error"] for row in rows) <= gate["maximum_temperature_reconstruction_error"],
        "exact_fallback_for_every_disabled_scenario": all(row["enabled"] or row["exact_fallback"] for row in rows),
        "no_unknown_or_test_labels_for_gate": all(
            row["no_unknown_or_test_labels_for_gate"] for row in rows
        ),
        "test_labels_used_for_final_metrics_only": all(
            row["test_labels_used_for_final_metrics_only"] for row in rows
        ),
    }
    passes = all(checks.values())
    result = {
        "schema_version": "strict_v4_vgrf_confirmation_summary_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"], "paired_result_count": len(rows),
        "rows": rows, "by_suite_oriented_gains": by_suite, "overall_equal_suite_oriented_gains": overall,
        "primary_composite_bootstrap_95_ci": ci, "enabled_scenario_count": enabled,
        "fully_nonregressing_suite_count": nonregressing, "minimum_suite_metric_gain": minimum_suite_metric,
        "positive_scenario_composite_count": positive, "mean_known_macro_f1_gain": float(np.mean(known)),
        "minimum_scenario_known_macro_f1_gain": min(known), "checks": checks, "passes": passes,
        "selected_algorithm": "caeos_validation_gated_class_conditional_reliability_fusion" if passes else "caeos_pairwise",
        "decision": "select_vgrf_as_best_self_algorithm" if passes else "retain_caeos_pairwise_as_best_self_algorithm",
        "claim_boundary": protocol["claim_boundary"],
        "candidate_result_validation": {
            "schema_identity_parameters_input_sha_and_finite_metrics": True,
            "all_204_unique_results_validated": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def write_outputs(result: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    passes = result["passes"]
    selection = {
        "schema_version": "strict_v4_final_self_algorithm_selection_v1",
        "status": "complete_after_positive_pilot_and_full102_confirmation",
        "selected_algorithm": result["selected_algorithm"],
        "vgrf_confirmation_passes": passes,
        "confirmation_summary_manifest_sha256": result["manifest_sha256"],
        "confirmation_summary_file_sha256": __import__("hashlib").sha256(
            summary_path.read_bytes()
        ).hexdigest(),
        "selection_rule": (
            "select VGRF only if every frozen full102 confirmation check "
            "passes; otherwise retain Pairwise"
        ),
    }
    selection["manifest_sha256"] = canonical_hash(selection)
    (output_dir / "final_selection.json").write_text(
        json.dumps(selection, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "branch_complete").touch()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--reference-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    result = analyze(
        protocol, args.run_root, args.reference_root, args.project_root
    )
    write_outputs(result, args.output_dir)
    print(
        json.dumps(
            {
                "passes": result["passes"],
                "selected_algorithm": result["selected_algorithm"],
            }
        )
    )


if __name__ == "__main__":
    main()
