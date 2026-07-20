from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_paired_confirmation import METRICS, aggregate


UNKNOWN_METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
REQUIRED_ARTIFACTS = ("metrics.json", "scores.npz", "evidence_package.npz", "provenance.json")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_manifest(payload: dict[str, Any], schema: str, label: str) -> None:
    if payload.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if payload.get("manifest_sha256") != canonical_hash(payload):
        raise ValueError(f"{label} manifest SHA mismatch")


def command_value(command: list[str], flag: str) -> str:
    if command.count(flag) != 1:
        raise ValueError(f"provenance command must contain {flag} exactly once")
    index = command.index(flag)
    if index + 1 >= len(command):
        raise ValueError(f"provenance command has no value for {flag}")
    return command[index + 1]


def build_rows(
    protocol: dict[str, Any], run_root: Path
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    candidate = protocol["candidate"]
    confirmation = protocol["confirmation"]
    seeds = {int(seed) for seed in confirmation["seeds"]}
    expected = {
        (suite, scenario, seed)
        for suite, scenarios in confirmation["scenario_registry"].items()
        for scenario in scenarios
        for seed in seeds
    }
    rows: list[dict[str, Any]] = []
    selected_count = 0
    learned_count = 0
    split_checks = 0
    observed: set[tuple[str, str, int]] = set()
    for suite, scenario, seed in sorted(expected):
        directory = run_root / suite / f"{scenario}_seed{seed}"
        missing = [name for name in REQUIRED_ARTIFACTS if not (directory / name).is_file()]
        if missing:
            raise ValueError(f"missing tail-aware artifacts for {(suite, scenario, seed)}: {missing}")
        payload = json.loads((directory / "metrics.json").read_text(encoding="utf-8"))
        provenance = json.loads((directory / "provenance.json").read_text(encoding="utf-8"))
        command = [str(value) for value in provenance.get("command", [])]
        if provenance.get("task") != {
            "suite": suite,
            "scenario": scenario,
            "unknown_classes": provenance.get("task", {}).get("unknown_classes"),
            "seed": seed,
        }:
            raise ValueError(f"provenance task identity mismatch for {(suite, scenario, seed)}")
        if command_value(command, "--risk-selection") != candidate["risk_selection"]:
            raise ValueError("tail-aware confirmation risk selection mismatch")
        if command_value(command, "--risk-policy-name") != confirmation["risk_policy"]:
            raise ValueError("tail-aware confirmation risk policy mismatch")
        if float(command_value(command, "--pseudo-unknown-min-fold-gain")) != float(
            candidate["runtime_minimum_fold_gain"]
        ):
            raise ValueError("tail-aware runtime fold floor mismatch")
        if int(command_value(command, "--seed")) != seed:
            raise ValueError("tail-aware confirmation command seed mismatch")
        details = payload.get("risk_selection_details", {})
        learned = details.get("pseudo_unknown_learned_blend", {})
        if details.get("unknown_or_test_labels_used_for_selection") is not False:
            raise ValueError("tail-aware confirmation runtime leakage guard failed")
        if not (
            learned.get("schema_version") == "tail_aware_pairwise_ranking_head_v1"
            and learned.get("unknown_or_test_labels_used") is False
        ):
            raise ValueError("tail-aware confirmation learned-head audit failed")
        reports = payload.get("reports", {})
        candidate_report = reports.get(candidate["risk_endpoint"])
        reference_report = reports.get(candidate["reference_endpoint"])
        if not isinstance(candidate_report, dict) or not isinstance(reference_report, dict):
            raise ValueError("tail-aware confirmation reports are incomplete")
        for metric in METRICS:
            if metric not in candidate_report or metric not in reference_report:
                raise ValueError(f"tail-aware report misses {metric}")
        learned_passes = learned.get("passes") is True
        expected_selected = (
            candidate["risk_endpoint"] if learned_passes else candidate["reference_endpoint"]
        )
        if payload.get("selected_risk") != expected_selected:
            raise ValueError("tail-aware runtime endpoint contradicts the frozen mean gate")
        if details.get("pseudo_unknown_gate_passes") is not learned_passes:
            raise ValueError("tail-aware runtime fold-floor gate is inconsistent")
        if not learned_passes and any(
            abs(float(candidate_report[m]) - float(reference_report[m])) > 1e-12
            for m in METRICS
        ):
            raise ValueError("failed tail-aware mean gate did not fall back exactly")
        fingerprint = payload.get("split_metadata", {}).get("split_fingerprint", {})
        if not fingerprint.get("combined"):
            raise ValueError("tail-aware confirmation split fingerprint is absent")
        split_checks += 1
        learned_count += learned_passes
        selected_count += payload.get("selected_risk") == candidate["risk_endpoint"]
        observed.add((suite, scenario, seed))
        rows.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed": seed,
                "candidate_selected": payload.get("selected_risk"),
                "reference_selected": candidate["reference_endpoint"],
                "candidate_report": candidate_report,
                "reference_report": reference_report,
                "split_fingerprint": fingerprint["combined"],
            }
        )
    discovered = {
        (path.relative_to(run_root).parts[0], path.parent.name.rsplit("_seed", 1)[0], int(path.parent.name.rsplit("_seed", 1)[1]))
        for path in run_root.glob("*/*/metrics.json")
    }
    if observed != expected or discovered != expected:
        raise ValueError("tail-aware confirmation task set is not exact")
    return rows, {
        "passes": True,
        "paired_runs": len(rows),
        "scenario_count": int(confirmation["expected_scenario_count"]),
        "seeds": sorted(seeds),
        "task_set_complete_and_exact": True,
        "artifact_checks": len(rows) * len(REQUIRED_ARTIFACTS),
        "split_fingerprint_checks": split_checks,
        "runtime_candidate_selected_count": selected_count,
        "known_only_learned_head_pass_count": learned_count,
        "unknown_or_test_labels_used_for_runtime_selection": False,
    }


def suite_gains(rows: list[dict[str, Any]], repetitions: int, seed: int) -> dict[str, dict[str, float]]:
    output: dict[str, dict[str, float]] = {}
    for suite in sorted({row["suite"] for row in rows}):
        report = aggregate([row for row in rows if row["suite"] == suite], repetitions, seed)
        output[suite] = {
            metric: float(report["metrics"][metric]["oriented_mean_improvement"])
            for metric in UNKNOWN_METRICS
        }
    return output


def confirmation_decision(
    inference: dict[str, Any], by_suite: dict[str, dict[str, float]], selected_count: int
) -> dict[str, Any]:
    metrics = inference["metrics"]
    mean_checks = {
        metric: metrics[metric]["oriented_mean_improvement"] > 0.0
        for metric in UNKNOWN_METRICS
    }
    bootstrap_checks = {
        metric: metrics[metric]["bootstrap_95_ci"]["lower"] > 0.0
        for metric in UNKNOWN_METRICS
    }
    holm_checks = {
        metric: (
            metrics[metric]["wilcoxon"]["holm_adjusted_p_value"] is not None
            and metrics[metric]["wilcoxon"]["holm_adjusted_p_value"] < 0.05
        )
        for metric in UNKNOWN_METRICS
    }
    suite_checks = {
        suite: {metric: value >= -1e-12 for metric, value in values.items()}
        for suite, values in by_suite.items()
    }
    known_unchanged = abs(metrics["known_macro_f1"]["raw_mean_delta"]) <= 1e-12
    checks = {
        "all_four_unknown_metric_means_strictly_positive": all(mean_checks.values()),
        "all_four_bootstrap_lowers_strictly_positive": all(bootstrap_checks.values()),
        "all_four_holm_p_values_below_0_05": all(holm_checks.values()),
        "all_suite_unknown_metric_means_nonnegative": all(
            value for values in suite_checks.values() for value in values.values()
        ),
        "known_macro_f1_unchanged": known_unchanged,
        "runtime_candidate_endpoint_exercised": selected_count > 0,
    }
    return {
        "passes": all(checks.values()),
        "checks": checks,
        "unknown_metric_mean_checks": mean_checks,
        "unknown_metric_bootstrap_checks": bootstrap_checks,
        "unknown_metric_holm_checks": holm_checks,
        "suite_nonregression_checks": suite_checks,
    }


def render(result: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 tail-aware ranking confirmation",
        "",
        f"Decision: `{'confirmed' if result['decision']['passes'] else 'not_confirmed'}`.",
        f"Paired runs: {result['validation']['paired_runs']}; scenarios: "
        f"{result['validation']['scenario_count']}; seeds: {result['validation']['seeds']}.",
        "",
        "| Metric | Reference | Tail-aware | Gain | 95% CI | Holm p |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for metric in METRICS:
        item = result["scenario_blocked_inference"]["metrics"][metric]
        ci = item["bootstrap_95_ci"]
        p = item["wilcoxon"]["holm_adjusted_p_value"]
        lines.append(
            f"| {metric} | {item['reference_scenario_mean']:.6f} | "
            f"{item['candidate_scenario_mean']:.6f} | "
            f"{item['oriented_mean_improvement']:+.6f} | "
            f"[{ci['lower']:+.6f}, {ci['upper']:+.6f}] | "
            f"{'NA' if p is None else f'{p:.3g}'} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--pilot-protocol", type=Path, required=True)
    parser.add_argument("--pilot-analysis", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    pilot_protocol = json.loads(args.pilot_protocol.read_text(encoding="utf-8"))
    pilot_analysis = json.loads(args.pilot_analysis.read_text(encoding="utf-8"))
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    validate_manifest(coverage, "strict_v4_coverage_manifest_v2", "coverage")
    validate_manifest(pilot_protocol, "strict_v4_tail_aware_pilot_protocol_v1", "pilot protocol")
    validate_manifest(protocol, "strict_v4_tail_aware_confirmation_protocol_v1", "confirmation protocol")
    bindings = protocol["bindings"]
    if not (
        bindings["coverage_manifest_sha256"] == coverage["manifest_sha256"]
        and bindings["coverage_file_sha256"] == file_hash(args.coverage)
        and bindings["pilot_protocol_manifest_sha256"] == pilot_protocol["manifest_sha256"]
        and bindings["pilot_protocol_file_sha256"] == file_hash(args.pilot_protocol)
        and bindings["pilot_analysis_file_sha256"] == file_hash(args.pilot_analysis)
        and pilot_analysis.get("passes") is True
    ):
        raise ValueError("tail-aware confirmation binding audit failed")
    rows, validation = build_rows(protocol, args.run_root)
    confirmation = protocol["confirmation"]
    inference = aggregate(
        rows,
        int(confirmation["bootstrap_repetitions"]),
        int(confirmation["bootstrap_seed"]),
    )
    by_suite = suite_gains(
        rows,
        int(confirmation["bootstrap_repetitions"]),
        int(confirmation["bootstrap_seed"]),
    )
    result = {
        "schema_version": "strict_v4_tail_aware_confirmation_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "pilot_analysis_sha256": file_hash(args.pilot_analysis),
        "analysis_implementation_sha256": file_hash(Path(__file__)),
        "validation": validation,
        "scenario_blocked_inference": inference,
        "suite_oriented_mean_gains": by_suite,
        "decision": confirmation_decision(
            inference, by_suite, validation["runtime_candidate_selected_count"]
        ),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "confirmation.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "confirmation.md").write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
