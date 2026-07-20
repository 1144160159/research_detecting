from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from analyze_strict_v4_validation_router import (
    REFERENCE,
    UNKNOWN_METRICS,
    canonical_hash,
    select_endpoint,
    validation_features,
)
from summarize_paired_confirmation import METRICS, aggregate


REQUIRED_ARTIFACTS = (
    "metrics.json",
    "scores.npz",
    "evidence_package.npz",
    "provenance.json",
)
EXPECTED_POLICY = "strict_v4_confirmation_current_policy_v1"


def load_manifest(path: Path, implementation: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "strict_v4_validation_router_candidate_v1":
        raise ValueError("unexpected router candidate manifest schema")
    if payload.get("status") != "frozen_unconfirmed":
        raise ValueError("router candidate is not frozen")
    if payload.get("manifest_sha256") != canonical_hash(payload):
        raise ValueError("router candidate manifest internal SHA mismatch")
    expected = payload.get("candidate", {}).get("implementation_sha256")
    actual = hashlib.sha256(implementation.read_bytes()).hexdigest()
    if expected != actual:
        raise ValueError("router implementation SHA mismatch")
    if payload.get("candidate", {}).get(
        "runtime_features_use_known_validation_only"
    ) is not True:
        raise ValueError("router runtime feature boundary is invalid")
    if payload.get("development", {}).get(
        "rule_selection_uses_test_unknown_labels"
    ) is not True:
        raise ValueError("router development label disclosure is missing")
    if payload.get("confirmation", {}).get("seed_disjoint") is not True:
        raise ValueError("router confirmation seeds are not disjoint")
    return payload


def metric_report(value: object, label: str) -> dict[str, float]:
    if not isinstance(value, dict):
        raise ValueError(f"missing report for {label}")
    missing = [metric for metric in METRICS if metric not in value]
    if missing:
        raise ValueError(f"report for {label} misses {missing}")
    return {metric: float(value[metric]) for metric in METRICS}


def build_rows(root: Path, manifest: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    confirmation = manifest["confirmation"]
    rule = manifest["candidate"]["selected_rule"]
    rows = []
    fingerprints = set()
    source_metrics = []
    for suite, scenarios in confirmation["scenarios"].items():
        for scenario in scenarios:
            for seed in confirmation["seeds"]:
                directory = root / suite / f"{scenario}_seed{seed}"
                missing = [
                    name for name in REQUIRED_ARTIFACTS if not (directory / name).is_file()
                ]
                if missing:
                    raise ValueError(f"missing artifacts under {directory}: {missing}")
                path = directory / "metrics.json"
                raw = path.read_bytes()
                payload = json.loads(raw.decode("utf-8"))
                if int(payload.get("seed", -1)) != int(seed):
                    raise ValueError(f"seed mismatch under {directory}")
                if payload.get("risk_policy") != EXPECTED_POLICY:
                    raise ValueError(f"risk policy mismatch under {directory}")
                if payload.get("selected_risk") != REFERENCE:
                    raise ValueError(f"reference risk mismatch under {directory}")
                if payload.get("risk_selection_details", {}).get(
                    "unknown_or_test_labels_used_for_selection"
                ) is not False:
                    raise ValueError(f"runtime leakage guard failed under {directory}")
                features = validation_features(directory)
                selected = select_endpoint(rule, {"features": features})
                reports = payload.get("reports", {})
                candidate = metric_report(
                    reports.get(selected), f"{suite}/{scenario}/{seed}/candidate"
                )
                reference = metric_report(
                    reports.get(REFERENCE), f"{suite}/{scenario}/{seed}/reference"
                )
                selected_report = metric_report(
                    payload.get("selected_report"), f"{suite}/{scenario}/{seed}/selected"
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
                source_metrics.append(
                    {
                        "path": path.relative_to(root).as_posix(),
                        "sha256": hashlib.sha256(raw).hexdigest(),
                    }
                )
                rows.append(
                    {
                        "suite": suite,
                        "scenario": scenario,
                        "seed": int(seed),
                        "candidate_selected": selected,
                        "reference_selected": REFERENCE,
                        "candidate_report": candidate,
                        "reference_report": reference,
                        "validation_router_feature": rule["feature"],
                        "validation_router_value": features[rule["feature"]],
                        "validation_router_threshold": rule["threshold"],
                        "split_fingerprint": str(fingerprint),
                    }
                )
    expected = int(confirmation["expected_run_count"])
    if len(rows) != expected:
        raise ValueError(f"router confirmation run count mismatch: {len(rows)} != {expected}")
    source_hash = hashlib.sha256(
        json.dumps(source_metrics, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return rows, {
        "passes": True,
        "run_count": len(rows),
        "scenario_count": sum(len(values) for values in confirmation["scenarios"].values()),
        "seeds": confirmation["seeds"],
        "artifact_checks": len(rows) * len(REQUIRED_ARTIFACTS),
        "split_fingerprint_checks": len(fingerprints),
        "source_metrics_combined_sha256": source_hash,
        "runtime_features_use_known_validation_only": True,
        "runtime_uses_unknown_or_test_labels": False,
        "scenario_boundary": confirmation["scenario_boundary"],
    }


def decision(
    combined: dict[str, Any], suites: dict[str, dict[str, Any]], paths: Counter[str], tolerance: float
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
    endpoints_exercised = paths[REFERENCE] > 0 and paths["cauchy_all"] > 0
    result = {
        "frozen_gate": "strict_v4_known_validation_router_confirmation_v1",
        "combined_auroc_mean_positive": metrics["unknown_auroc"][
            "oriented_mean_improvement"
        ]
        > 0.0,
        "combined_auroc_bootstrap_lower_gt_zero": metrics["unknown_auroc"][
            "bootstrap_95_ci"
        ]["lower"]
        > 0.0,
        "combined_safety_metrics": safety,
        "all_combined_safety_metrics_pass": all(safety.values()),
        "suite_unknown_metric_positive": suite_positive,
        "all_suite_unknown_metrics_positive": all(
            value for values in suite_positive.values() for value in values.values()
        ),
        "both_endpoints_exercised": endpoints_exercised,
        "endpoint_counts": dict(paths),
        "safety_nonregression_tolerance": tolerance,
    }
    result["passes"] = all(
        [
            result["combined_auroc_mean_positive"],
            result["combined_auroc_bootstrap_lower_gt_zero"],
            result["all_combined_safety_metrics_pass"],
            result["all_suite_unknown_metrics_positive"],
            result["both_endpoints_exercised"],
        ]
    )
    return result


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 known-validation router confirmation",
        "",
        f"State: **{'confirmed' if report['decision']['passes'] else 'rejected'}**; "
        f"runs: {report['validation']['run_count']}; scenario blocks: "
        f"{report['validation']['scenario_count']}.",
        "Seed repeats are averaged within scenarios before inference.",
        f"Endpoint counts: `{report['decision']['endpoint_counts']}`.",
        "",
        "| Metric | Reference | Router | Oriented gain | 95% CI | W/T/L | Holm p |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for metric in METRICS:
        values = report["combined"]["metrics"][metric]
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
    lines.extend(["", f"Frozen gate: **{'PASS' if report['decision']['passes'] else 'FAIL'}**.", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Confirm the frozen strict-v4 validation router")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--router-implementation", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-repetitions", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260717)
    parser.add_argument("--nonregression-tolerance", type=float, default=0.01)
    args = parser.parse_args()
    manifest = load_manifest(args.manifest, args.router_implementation)
    rows, validation = build_rows(args.root, manifest)
    combined = aggregate(rows, args.bootstrap_repetitions, args.bootstrap_seed)
    suites = {
        suite: aggregate(
            [row for row in rows if row["suite"] == suite],
            args.bootstrap_repetitions,
            args.bootstrap_seed,
        )
        for suite in sorted(manifest["confirmation"]["scenarios"])
    }
    paths = Counter(row["candidate_selected"] for row in rows)
    result = {
        "schema_version": "strict_v4_validation_router_confirmation_v1",
        "manifest_sha256": manifest["manifest_sha256"],
        "validation": validation,
        "combined": combined,
        "by_suite": suites,
        "rows": rows,
        "decision": decision(combined, suites, paths, args.nonregression_tolerance),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "confirmation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "confirmation.md").write_text(render_markdown(result), encoding="utf-8")
    print(json.dumps({"decision": result["decision"]}, indent=2))


if __name__ == "__main__":
    main()
