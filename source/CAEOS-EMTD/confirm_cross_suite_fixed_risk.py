from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

from summarize_paired_confirmation import aggregate, build_rows, markdown


UNKNOWN_METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
SAFETY_METRICS = ("known_macro_f1", "unknown_aupr", "unknown_fpr95", "oscr")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Confirm frozen suite-specific risks on held-out seeds"
    )
    parser.add_argument("--reference-root", required=True)
    parser.add_argument("--candidate-root", required=True)
    parser.add_argument("--selection-manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--candidate-risk-policy", required=True)
    parser.add_argument("--reference-risk-policy", required=True)
    parser.add_argument("--expected-scenarios", type=int, default=24)
    parser.add_argument("--bootstrap-repetitions", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260717)
    parser.add_argument("--nonregression-tolerance", type=float, default=0.01)
    return parser.parse_args()


def canonical_hash(payload: dict[str, object]) -> str:
    core = {key: value for key, value in payload.items() if key != "manifest_sha256"}
    return hashlib.sha256(
        json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def load_manifest(path: Path) -> dict[str, object]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("status") != "frozen_unconfirmed":
        raise ValueError("selection manifest is not frozen_unconfirmed")
    if manifest.get("manifest_sha256") != canonical_hash(manifest):
        raise ValueError("selection manifest hash mismatch")
    if manifest.get("development_candidate_screening_uses_test_unknown_labels") is not True:
        raise ValueError("development screening disclosure is missing")
    if manifest.get("runtime_policy_uses_unknown_or_test_labels") is not False:
        raise ValueError("runtime label boundary is invalid")
    selected = manifest.get("selected_suite_risks")
    if not isinstance(selected, dict) or not selected:
        raise ValueError("selection manifest has no suite risks")
    seeds = manifest.get("confirmation_seeds")
    if not isinstance(seeds, list) or not seeds:
        raise ValueError("selection manifest has no confirmation seeds")
    if int(manifest.get("development_seed", -1)) in {int(seed) for seed in seeds}:
        raise ValueError("development seed overlaps confirmation seeds")
    return manifest


def subset_rows(rows: list[dict[str, object]], suite: str) -> list[dict[str, object]]:
    selected = [row for row in rows if row["suite"] == suite]
    if not selected:
        raise ValueError(f"no confirmation rows for suite {suite}")
    return selected


def confirmation_decision(
    combined: dict[str, object],
    suites: dict[str, dict[str, object]],
    tolerance: float,
) -> dict[str, object]:
    combined_metrics = combined["metrics"]
    safety = {
        metric: combined_metrics[metric]["oriented_mean_improvement"] >= -tolerance
        for metric in SAFETY_METRICS
    }
    suite_positive = {
        suite: {
            metric: report["metrics"][metric]["oriented_mean_improvement"] > 0.0
            for metric in UNKNOWN_METRICS
        }
        for suite, report in suites.items()
    }
    primary_ci = combined_metrics["unknown_auroc"]["bootstrap_95_ci"]
    decision = {
        "frozen_gate": "cross_suite_fixed_risk_v1",
        "combined_auroc_bootstrap_lower_gt_zero": primary_ci["lower"] > 0.0,
        "combined_safety_nonregression_tolerance": tolerance,
        "combined_safety_metrics": safety,
        "all_combined_safety_metrics_pass": all(safety.values()),
        "suite_unknown_metric_positive": suite_positive,
        "all_suite_unknown_metrics_positive": all(
            value for metrics in suite_positive.values() for value in metrics.values()
        ),
    }
    decision["passes"] = bool(
        decision["combined_auroc_bootstrap_lower_gt_zero"]
        and decision["all_combined_safety_metrics_pass"]
        and decision["all_suite_unknown_metrics_positive"]
    )
    return decision


def main() -> None:
    args = parse_arguments()
    manifest = load_manifest(Path(args.selection_manifest))
    seeds = {int(seed) for seed in manifest["confirmation_seeds"]}
    rows, validation = build_rows(
        Path(args.reference_root),
        Path(args.candidate_root),
        seeds,
        args.expected_scenarios,
        args.candidate_risk_policy,
        args.reference_risk_policy,
    )
    selected_suite_risks = {
        str(suite): str(risk)
        for suite, risk in manifest["selected_suite_risks"].items()
    }
    observed_suites = {str(row["suite"]) for row in rows}
    if observed_suites != set(selected_suite_risks):
        raise ValueError("confirmation suites do not match the frozen manifest")
    for row in rows:
        suite = str(row["suite"])
        expected = selected_suite_risks[suite]
        if row["candidate_selected"] != expected:
            raise ValueError(
                f"candidate selected risk mismatch for {suite}/{row['scenario']}"
            )

    combined = aggregate(rows, args.bootstrap_repetitions, args.bootstrap_seed)
    suite_reports = {
        suite: aggregate(
            subset_rows(rows, suite),
            args.bootstrap_repetitions,
            args.bootstrap_seed,
        )
        for suite in sorted(selected_suite_risks)
    }
    decision = confirmation_decision(
        combined, suite_reports, args.nonregression_tolerance
    )
    report = {
        "schema_version": "cross_suite_fixed_risk_confirmation_v1",
        "selection_manifest": args.selection_manifest,
        "selection_manifest_sha256": manifest["manifest_sha256"],
        "candidate_status_before_confirmation": manifest["status"],
        "selected_suite_risks": selected_suite_risks,
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
