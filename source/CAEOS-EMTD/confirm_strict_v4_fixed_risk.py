from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from screen_strict_v4_risk_candidates import canonical_hash
from summarize_paired_confirmation import METRICS, aggregate


UNKNOWN_METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
REQUIRED_ARTIFACTS = (
    "metrics.json",
    "scores.npz",
    "evidence_package.npz",
    "provenance.json",
)
EXPECTED_POLICY = "strict_v4_confirmation_current_policy_v1"


def load_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "strict_v4_fixed_risk_candidate_manifest_v1":
        raise ValueError("unexpected strict-v4 candidate manifest schema")
    if payload.get("status") != "frozen_unconfirmed":
        raise ValueError("strict-v4 candidate manifest is not frozen")
    if payload.get("manifest_sha256") != canonical_hash(payload):
        raise ValueError("strict-v4 candidate manifest internal SHA mismatch")
    if payload.get("runtime_policy", {}).get("uses_unknown_or_test_labels") is not False:
        raise ValueError("runtime label boundary is invalid")
    if payload.get("development", {}).get(
        "candidate_screening_uses_test_unknown_labels"
    ) is not True:
        raise ValueError("development label-use disclosure is missing")
    confirmation = payload.get("confirmation", {})
    if not confirmation.get("scenario_disjoint") or not confirmation.get(
        "seed_disjoint"
    ):
        raise ValueError("confirmation boundary is not disjoint")
    return payload


def metric_report(value: object, label: str) -> dict[str, float]:
    if not isinstance(value, dict):
        raise ValueError(f"missing report for {label}")
    missing = [metric for metric in METRICS if metric not in value]
    if missing:
        raise ValueError(f"report for {label} misses {missing}")
    return {metric: float(value[metric]) for metric in METRICS}


def build_rows(
    root: Path, manifest: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    confirmation = manifest["confirmation"]
    selected = {
        str(suite): str(risk)
        for suite, risk in manifest["selected_suite_risks"].items()
    }
    reference_risk = str(manifest["reference_risk"])
    rows: list[dict[str, Any]] = []
    source_paths: set[Path] = set()
    fingerprints: set[str] = set()
    for suite, scenarios in confirmation["scenarios"].items():
        candidate_risk = selected[str(suite)]
        for scenario in scenarios:
            for seed in confirmation["seeds"]:
                directory = root / str(suite) / f"{scenario}_seed{seed}"
                missing = [
                    name for name in REQUIRED_ARTIFACTS if not (directory / name).is_file()
                ]
                if missing:
                    raise ValueError(f"missing artifacts under {directory}: {missing}")
                path = directory / "metrics.json"
                source_paths.add(path)
                payload = json.loads(path.read_text(encoding="utf-8"))
                if int(payload.get("seed", -1)) != int(seed):
                    raise ValueError(f"seed mismatch under {directory}")
                if payload.get("risk_policy") != EXPECTED_POLICY:
                    raise ValueError(f"risk policy mismatch under {directory}")
                if payload.get("selected_risk") != reference_risk:
                    raise ValueError(f"reference risk mismatch under {directory}")
                details = payload.get("risk_selection_details", {})
                if details.get("unknown_or_test_labels_used_for_selection") is not False:
                    raise ValueError(f"runtime leakage guard failed under {directory}")
                reports = payload.get("reports", {})
                candidate = metric_report(
                    reports.get(candidate_risk), f"{suite}/{scenario}/{seed}/candidate"
                )
                reference = metric_report(
                    reports.get(reference_risk), f"{suite}/{scenario}/{seed}/reference"
                )
                selected_report = metric_report(
                    payload.get("selected_report"),
                    f"{suite}/{scenario}/{seed}/selected",
                )
                if selected_report != reference:
                    raise ValueError(f"selected report mismatch under {directory}")
                fingerprint = (
                    payload.get("split_metadata", {})
                    .get("split_fingerprint", {})
                    .get("combined")
                )
                if not fingerprint:
                    raise ValueError(f"missing split fingerprint under {directory}")
                fingerprints.add(str(fingerprint))
                rows.append(
                    {
                        "suite": str(suite),
                        "scenario": str(scenario),
                        "seed": int(seed),
                        "candidate_selected": candidate_risk,
                        "reference_selected": reference_risk,
                        "candidate_report": candidate,
                        "reference_report": reference,
                        "split_fingerprint": str(fingerprint),
                    }
                )
    expected = int(confirmation["expected_run_count"])
    if len(rows) != expected or len(source_paths) != expected:
        raise ValueError(f"confirmation run count mismatch: {len(rows)} != {expected}")
    return rows, {
        "passes": True,
        "run_count": len(rows),
        "scenario_count": sum(
            len(values) for values in confirmation["scenarios"].values()
        ),
        "seeds": confirmation["seeds"],
        "artifact_checks": len(rows) * len(REQUIRED_ARTIFACTS),
        "split_fingerprint_checks": len(fingerprints),
        "runtime_selection_uses_unknown_or_test_labels": False,
    }


def subset(rows: list[dict[str, Any]], suite: str) -> list[dict[str, Any]]:
    return [row for row in rows if row["suite"] == suite]


def decision(
    combined: dict[str, Any],
    suites: dict[str, dict[str, Any]],
    tolerance: float,
) -> dict[str, Any]:
    metrics = combined["metrics"]
    safety = {
        metric: metrics[metric]["oriented_mean_improvement"] >= -tolerance
        for metric in ("unknown_aupr", "unknown_fpr95", "oscr")
    }
    suite_positive = {
        suite: {
            metric: report["metrics"][metric]["oriented_mean_improvement"] > 0.0
            for metric in UNKNOWN_METRICS
        }
        for suite, report in suites.items()
    }
    result = {
        "frozen_gate": "strict_v4_fixed_risk_confirmation_v1",
        "combined_auroc_mean_positive": metrics["unknown_auroc"][
            "oriented_mean_improvement"
        ]
        > 0.0,
        "combined_auroc_bootstrap_lower_gt_zero": metrics["unknown_auroc"][
            "bootstrap_95_ci"
        ]["lower"]
        > 0.0,
        "safety_nonregression_tolerance": tolerance,
        "combined_safety_metrics": safety,
        "all_combined_safety_metrics_pass": all(safety.values()),
        "suite_unknown_metric_positive": suite_positive,
        "all_suite_unknown_metrics_positive": all(
            value for values in suite_positive.values() for value in values.values()
        ),
    }
    result["passes"] = all(
        [
            result["combined_auroc_mean_positive"],
            result["combined_auroc_bootstrap_lower_gt_zero"],
            result["all_combined_safety_metrics_pass"],
            result["all_suite_unknown_metrics_positive"],
        ]
    )
    return result


def render_markdown(report: dict[str, Any]) -> str:
    combined = report["combined"]
    lines = [
        "# Strict-v4 fixed-risk frozen confirmation",
        "",
        f"State: **{'confirmed' if report['decision']['passes'] else 'rejected'}**; "
        f"runs: {report['validation']['run_count']}; "
        f"scenario blocks: {report['validation']['scenario_count']}.",
        "Seed repeats are averaged within scenarios before inference.",
        "",
        "| Metric | Reference | Candidate | Oriented gain | 95% CI | W/T/L | Holm p |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for metric in METRICS:
        values = combined["metrics"][metric]
        ci = values["bootstrap_95_ci"]
        p = values["wilcoxon"].get("holm_adjusted_p_value")
        lines.append(
            f"| {metric} | {values['reference_scenario_mean']:.6f} | "
            f"{values['candidate_scenario_mean']:.6f} | "
            f"{values['oriented_mean_improvement']:+.6f} | "
            f"[{ci['lower']:+.6f}, {ci['upper']:+.6f}] | "
            f"{values['wins']}/{values['ties']}/{values['losses']} | "
            f"{'NA' if p is None else f'{p:.6g}'} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"Frozen gate: **{'PASS' if report['decision']['passes'] else 'FAIL'}**.",
            f"Candidate paths: `{combined['candidate_selected_paths']}`.",
            f"Reference paths: `{combined['reference_selected_paths']}`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Confirm frozen strict-v4 suite-specific risks"
    )
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-repetitions", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260717)
    parser.add_argument("--nonregression-tolerance", type=float, default=0.01)
    args = parser.parse_args()
    manifest = load_manifest(args.manifest)
    rows, validation = build_rows(args.root, manifest)
    combined = aggregate(rows, args.bootstrap_repetitions, args.bootstrap_seed)
    suites = {
        suite: aggregate(
            subset(rows, suite), args.bootstrap_repetitions, args.bootstrap_seed
        )
        for suite in sorted(manifest["selected_suite_risks"])
    }
    result = {
        "schema_version": "strict_v4_fixed_risk_confirmation_v1",
        "manifest_sha256": manifest["manifest_sha256"],
        "validation": validation,
        "combined": combined,
        "by_suite": suites,
        "decision": decision(combined, suites, args.nonregression_tolerance),
        "candidate_paths": dict(
            Counter(row["candidate_selected"] for row in rows)
        ),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "confirmation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "confirmation.md").write_text(
        render_markdown(result), encoding="utf-8"
    )
    print(json.dumps({"decision": result["decision"]}, indent=2))


if __name__ == "__main__":
    main()
