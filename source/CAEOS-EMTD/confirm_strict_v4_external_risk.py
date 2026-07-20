from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from select_strict_v4_external_risk_candidate import canonical_hash
from summarize_paired_confirmation import METRICS, aggregate


UNKNOWN_METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_task(task: str) -> tuple[str, int]:
    if "_seed" not in task:
        raise ValueError(f"task has no seed suffix: {task!r}")
    scenario, seed = task.rsplit("_seed", 1)
    return scenario, int(seed)


def load_manifest(path: Path, project_root: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "strict_v4_external_risk_candidate_v1":
        raise ValueError("unexpected external-risk manifest schema")
    if payload.get("status") != "frozen_unconfirmed":
        raise ValueError("external-risk candidate is not frozen")
    if payload.get("manifest_sha256") != canonical_hash(payload):
        raise ValueError("external-risk manifest canonical SHA mismatch")
    candidate = payload["candidate"]
    if (candidate.get("expert_model"), candidate.get("expert_risk"), candidate.get("fusion")) != (
        "mlp",
        "openmax",
        "rank_union",
    ):
        raise ValueError("external-risk candidate does not match frozen endpoint")
    for relative, expected in candidate["implementation_sha256"].items():
        if file_hash(project_root / relative) != expected:
            raise ValueError(f"implementation SHA mismatch: {relative}")
    return payload


def build_rows(raw: dict[str, Any], manifest: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    candidate = manifest["candidate"]
    confirmation = manifest["confirmation"]
    if raw.get("calibration") != (
        "each expert empirical CDF fitted on known validation only"
    ):
        raise ValueError("confirmation calibration declaration mismatch")
    if raw.get("selection_scope", {}).get("seeds") != confirmation["seeds"]:
        raise ValueError("confirmation seed allowlist mismatch")
    if raw.get("selection_scope", {}).get("expert_model") != candidate["expert_model"]:
        raise ValueError("confirmation expert model mismatch")
    if raw.get("overall", {}).get("expert_name") != candidate["expert_risk"]:
        raise ValueError("confirmation expert risk mismatch")
    expected = {
        (suite, scenario, seed)
        for suite, scenarios in confirmation["scenarios"].items()
        for scenario in scenarios
        for seed in confirmation["seeds"]
    }
    rows = []
    observed = set()
    fingerprints = set()
    fusion = candidate["fusion"]
    for run in raw["runs"]:
        scenario, seed = parse_task(run["task"])
        key = (run["suite"], scenario, seed)
        if key in observed:
            raise ValueError(f"duplicate confirmation run: {key}")
        observed.add(key)
        audit = run.get("audit", {})
        if not (
            audit.get("split_fingerprints_identical") is True
            and audit.get("caeos_unknown_or_test_labels_used_for_selection") is False
            and audit.get(
                "expert_unknown_or_test_labels_used_for_fitting_or_selection"
            )
            is False
            and audit.get("fusion_calibration_split") == "known_only_validation"
            and audit.get("test_labels_used_for_final_metrics_only") is True
        ):
            raise ValueError(f"confirmation leakage/split audit failed for {key}")
        fingerprints.add(audit["split_fingerprint"])
        candidate_report = run["reports"][fusion]
        reference_report = run["gate_report"]
        for metric in METRICS:
            if metric not in candidate_report or metric not in reference_report:
                raise ValueError(f"missing {metric} for {key}")
        rows.append(
            {
                "suite": run["suite"],
                "scenario": scenario,
                "seed": seed,
                "candidate_selected": f"{candidate['expert_risk']}/{fusion}",
                "reference_selected": run["gate_selected_risk"],
                "candidate_report": candidate_report,
                "reference_report": reference_report,
                "split_fingerprint": audit["split_fingerprint"],
            }
        )
    if observed != expected:
        raise ValueError(
            f"confirmation coverage mismatch: missing={sorted(expected-observed)}, "
            f"unexpected={sorted(observed-expected)}"
        )
    if len(rows) != confirmation["expected_run_count"]:
        raise ValueError("confirmation run count mismatch")
    return rows, {
        "passes": True,
        "run_count": len(rows),
        "scenario_count": confirmation["expected_scenario_count"],
        "seeds": confirmation["seeds"],
        "split_fingerprint_checks": len(rows),
        "unique_split_fingerprints": len(fingerprints),
        "base_selection_uses_unknown_or_test_labels": False,
        "expert_fitting_or_selection_uses_unknown_or_test_labels": False,
        "fusion_calibration_uses_unknown_or_test_labels": False,
        "test_labels_used_for_final_metrics_only": True,
    }


def decide(combined: dict[str, Any], suites: dict[str, dict[str, Any]]) -> dict[str, Any]:
    combined_positive = {
        metric: combined["metrics"][metric]["oriented_mean_improvement"] > 0.0
        for metric in UNKNOWN_METRICS
    }
    suite_nonnegative = {
        suite: {
            metric: report["metrics"][metric]["oriented_mean_improvement"] >= 0.0
            for metric in UNKNOWN_METRICS
        }
        for suite, report in suites.items()
    }
    known = combined["metrics"]["known_macro_f1"]
    result = {
        "frozen_gate": "strict_v4_external_risk_confirmation_v1",
        "all_combined_unknown_metrics_positive": all(combined_positive.values()),
        "combined_unknown_metrics_positive": combined_positive,
        "combined_auroc_bootstrap_lower_gt_zero": (
            combined["metrics"]["unknown_auroc"]["bootstrap_95_ci"]["lower"] > 0.0
        ),
        "all_suite_unknown_metrics_nonnegative": all(
            value for values in suite_nonnegative.values() for value in values.values()
        ),
        "suite_unknown_metric_nonnegative": suite_nonnegative,
        "known_macro_f1_unchanged": abs(known["raw_mean_delta"]) <= 1e-12,
    }
    result["passes"] = all(
        (
            result["all_combined_unknown_metrics_positive"],
            result["combined_auroc_bootstrap_lower_gt_zero"],
            result["all_suite_unknown_metrics_nonnegative"],
            result["known_macro_f1_unchanged"],
        )
    )
    return result


def render(report: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 external-risk confirmation",
        "",
        f"State: **{'confirmed' if report['decision']['passes'] else 'rejected'}**; "
        f"runs: {report['validation']['run_count']}; scenario blocks: "
        f"{report['validation']['scenario_count']}.",
        "",
        "| Metric | Base CAEOS | Fused CAEOS | Oriented gain | 95% CI | W/T/L | Holm p |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for metric in METRICS:
        item = report["combined"]["metrics"][metric]
        ci = item["bootstrap_95_ci"]
        adjusted = item["wilcoxon"].get("holm_adjusted_p_value")
        lines.append(
            f"| {metric} | {item['reference_scenario_mean']:.6f} | "
            f"{item['candidate_scenario_mean']:.6f} | "
            f"{item['oriented_mean_improvement']:+.6f} | "
            f"[{ci['lower']:+.6f}, {ci['upper']:+.6f}] | "
            f"{item['wins']}/{item['ties']}/{item['losses']} | "
            f"{'NA' if adjusted is None else f'{adjusted:.6g}'} |"
        )
    lines.extend(
        [
            "",
            f"Frozen gate: **{'PASS' if report['decision']['passes'] else 'FAIL'}**.",
            "A failed gate rejects this frozen fusion without post-confirmation retuning.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-analysis", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-repetitions", type=int, default=10000)
    args = parser.parse_args()
    manifest = load_manifest(args.manifest, args.project_root.resolve())
    raw = json.loads(args.raw_analysis.read_text(encoding="utf-8"))
    rows, validation = build_rows(raw, manifest)
    combined = aggregate(rows, args.bootstrap_repetitions, 20260718)
    suites = {
        suite: aggregate(
            [row for row in rows if row["suite"] == suite],
            args.bootstrap_repetitions,
            20260718,
        )
        for suite in manifest["confirmation"]["scenarios"]
    }
    result = {
        "schema_version": "strict_v4_external_risk_confirmation_v1",
        "manifest_sha256": manifest["manifest_sha256"],
        "raw_analysis_sha256": file_hash(args.raw_analysis),
        "validation": validation,
        "combined": combined,
        "by_suite": suites,
        "rows": rows,
        "decision": decide(combined, suites),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "confirmation.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "confirmation.md").write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
