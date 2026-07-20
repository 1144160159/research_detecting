from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from confirm_cross_suite_fixed_risk import (
    confirmation_decision,
    load_manifest,
    subset_rows,
)
from summarize_paired_confirmation import (
    METRICS,
    aggregate,
    load_root,
    markdown,
    split_fingerprint,
    validate_coverage,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Confirm frozen suite risks from reports in the same model runs"
    )
    parser.add_argument("--root", required=True)
    parser.add_argument("--selection-manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--reference-risk-policy", required=True)
    parser.add_argument("--expected-scenarios", type=int, default=24)
    parser.add_argument("--bootstrap-repetitions", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260717)
    parser.add_argument("--nonregression-tolerance", type=float, default=0.01)
    return parser.parse_args()


def normalized_report(
    payload: object, label: str, key: tuple[str, str, int]
) -> dict[str, float]:
    if not isinstance(payload, dict):
        raise ValueError(f"missing {label} report for {key}")
    missing = [metric for metric in METRICS if metric not in payload]
    if missing:
        raise ValueError(f"{label} report for {key} misses {missing}")
    report = {metric: float(payload[metric]) for metric in METRICS}
    if not all(np.isfinite(value) for value in report.values()):
        raise ValueError(f"non-finite {label} report for {key}")
    return report


def build_same_run_rows(
    root: Path,
    manifest: dict[str, object],
    expected_scenarios: int,
    reference_risk_policy: str,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    runs = load_root(root)
    seeds = {int(seed) for seed in manifest["confirmation_seeds"]}
    validate_coverage(runs, seeds, expected_scenarios, "reference")
    selected = {
        str(suite): str(risk)
        for suite, risk in manifest["selected_suite_risks"].items()
    }
    observed_suites = {suite for suite, _, _ in runs}
    if observed_suites != set(selected):
        raise ValueError("reference suites do not match the frozen manifest")
    grouped: dict[tuple[str, str], set[int]] = defaultdict(set)
    rows: list[dict[str, object]] = []
    for key, run in sorted(runs.items()):
        suite, scenario, seed = key
        payload = run["payload"]
        if payload.get("risk_policy") != reference_risk_policy:
            raise ValueError(f"reference risk policy mismatch for {key}")
        details = payload.get("risk_selection_details", {})
        if details.get("unknown_or_test_labels_used_for_selection") is not False:
            raise ValueError(f"reference selection leakage guard failed for {key}")
        candidate_name = selected[suite]
        reports = payload.get("reports")
        if not isinstance(reports, dict) or candidate_name not in reports:
            raise ValueError(f"candidate report {candidate_name!r} is absent for {key}")
        thresholds = payload.get("validation_thresholds")
        if not isinstance(thresholds, dict) or candidate_name not in thresholds:
            raise ValueError(
                f"known-validation threshold for {candidate_name!r} is absent for {key}"
            )
        threshold = float(thresholds[candidate_name])
        if not np.isfinite(threshold):
            raise ValueError(f"non-finite candidate threshold for {key}")
        reference_name = str(payload.get("selected_risk", ""))
        reference_report = normalized_report(
            payload.get("selected_report"), "reference", key
        )
        candidate_report = normalized_report(
            reports[candidate_name], candidate_name, key
        )
        fingerprint = split_fingerprint(payload)
        rows.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed": seed,
                "candidate_selected": candidate_name,
                "reference_selected": reference_name,
                "candidate_report": candidate_report,
                "reference_report": reference_report,
                "candidate_known_validation_threshold": threshold,
                "split_fingerprint": fingerprint["combined"],
            }
        )
        grouped[(suite, scenario)].add(seed)
    return rows, {
        "paired_tasks": len(rows),
        "expected_seeds": sorted(seeds),
        "expected_scenarios": expected_scenarios,
        "scenario_count": len(grouped),
        "candidate_reports_extracted_from_same_model_run": True,
        "candidate_thresholds_fitted_on_known_validation": True,
        "candidate_runtime_selection_uses_unknown_or_test_labels": False,
        "reference_selection_uses_unknown_or_test_labels": False,
        "required_artifacts_validated_by_load_root": True,
    }


def main() -> None:
    args = parse_arguments()
    manifest = load_manifest(Path(args.selection_manifest))
    rows, validation = build_same_run_rows(
        Path(args.root),
        manifest,
        args.expected_scenarios,
        args.reference_risk_policy,
    )
    combined = aggregate(rows, args.bootstrap_repetitions, args.bootstrap_seed)
    suite_reports = {
        suite: aggregate(
            subset_rows(rows, suite),
            args.bootstrap_repetitions,
            args.bootstrap_seed,
        )
        for suite in sorted(manifest["selected_suite_risks"])
    }
    decision = confirmation_decision(
        combined, suite_reports, args.nonregression_tolerance
    )
    report = {
        "schema_version": "cross_suite_fixed_report_confirmation_v1",
        "selection_manifest": args.selection_manifest,
        "selection_manifest_sha256": manifest["manifest_sha256"],
        "candidate_status_before_confirmation": manifest["status"],
        "selected_suite_risks": manifest["selected_suite_risks"],
        "validation": validation,
        "scenario_blocked_inference": combined,
        "suite_inference": suite_reports,
        "frozen_confirmation_decision": decision,
        "confirmation_status": "confirmed" if decision["passes"] else "not_confirmed",
        "runs": rows,
    }
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "confirmation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    body = markdown(report)
    body += (
        "\n## Frozen cross-suite gate\n\n"
        f"Status: **{report['confirmation_status']}**.\n\n"
        f"```json\n{json.dumps(decision, ensure_ascii=False, indent=2)}\n```\n"
    )
    (output / "confirmation.md").write_text(body, encoding="utf-8")
    print(json.dumps({"status": report["confirmation_status"], "decision": decision}, indent=2))


if __name__ == "__main__":
    main()
