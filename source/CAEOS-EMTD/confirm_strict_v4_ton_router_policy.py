from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from analyze_strict_v4_validation_router import REFERENCE, UNKNOWN_METRICS, canonical_hash, select_endpoint, validation_features
from confirm_strict_v4_validation_router import EXPECTED_POLICY, REQUIRED_ARTIFACTS, metric_report
from summarize_paired_confirmation import METRICS, aggregate


def load_manifest(path: Path, router_implementation: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "strict_v4_ton_router_partial_policy_candidate_v1":
        raise ValueError("unexpected ToN partial-policy manifest")
    if payload.get("status") != "frozen_unconfirmed" or payload.get("manifest_sha256") != canonical_hash(payload):
        raise ValueError("ToN partial-policy manifest is not valid and frozen")
    actual = hashlib.sha256(router_implementation.read_bytes()).hexdigest()
    if payload.get("candidate", {}).get("router_implementation_sha256") != actual:
        raise ValueError("ToN router implementation SHA mismatch")
    if payload.get("development", {}).get("partial_policy_selection_uses_opened_confirmation_labels") is not True:
        raise ValueError("partial-policy development disclosure is missing")
    if payload.get("confirmation", {}).get("seed_disjoint") is not True:
        raise ValueError("ToN confirmation seeds are not disjoint")
    return payload


def build_rows(root: Path, manifest: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    confirmation = manifest["confirmation"]
    rule = manifest["candidate"]["suite_policy"]["cic_ton_iot"]["rule"]
    rows = []
    fingerprints = set()
    for scenario in confirmation["scenarios"]["cic_ton_iot"]:
        for seed in confirmation["seeds"]:
            directory = root / "cic_ton_iot" / f"{scenario}_seed{seed}"
            missing = [name for name in REQUIRED_ARTIFACTS if not (directory / name).is_file()]
            if missing:
                raise ValueError(f"missing artifacts under {directory}: {missing}")
            payload = json.loads((directory / "metrics.json").read_text(encoding="utf-8"))
            if int(payload.get("seed", -1)) != int(seed):
                raise ValueError(f"seed mismatch under {directory}")
            if payload.get("risk_policy") != EXPECTED_POLICY or payload.get("selected_risk") != REFERENCE:
                raise ValueError(f"reference policy mismatch under {directory}")
            if payload.get("risk_selection_details", {}).get("unknown_or_test_labels_used_for_selection") is not False:
                raise ValueError(f"runtime leakage guard failed under {directory}")
            features = validation_features(directory)
            endpoint = select_endpoint(rule, {"features": features})
            reports = payload.get("reports", {})
            candidate = metric_report(reports.get(endpoint), f"{scenario}/{seed}/candidate")
            reference = metric_report(reports.get(REFERENCE), f"{scenario}/{seed}/reference")
            fingerprint = payload.get("split_metadata", {}).get("split_fingerprint", {}).get("combined")
            if not fingerprint:
                raise ValueError(f"missing split fingerprint under {directory}")
            fingerprints.add(str(fingerprint))
            rows.append({
                "suite": "cic_ton_iot",
                "scenario": scenario,
                "seed": int(seed),
                "candidate_selected": endpoint,
                "reference_selected": REFERENCE,
                "candidate_report": candidate,
                "reference_report": reference,
                "validation_router_feature": rule["feature"],
                "validation_router_value": features[rule["feature"]],
                "validation_router_threshold": rule["threshold"],
                "split_fingerprint": str(fingerprint),
            })
    expected = int(confirmation["expected_run_count"])
    if len(rows) != expected:
        raise ValueError(f"ToN confirmation run count mismatch: {len(rows)} != {expected}")
    return rows, {
        "passes": True,
        "run_count": len(rows),
        "scenario_count": len(confirmation["scenarios"]["cic_ton_iot"]),
        "seeds": confirmation["seeds"],
        "artifact_checks": len(rows) * len(REQUIRED_ARTIFACTS),
        "split_fingerprint_checks": len(fingerprints),
        "runtime_features_use_known_validation_only": True,
        "runtime_uses_unknown_or_test_labels": False,
    }


def make_decision(combined: dict[str, Any], paths: Counter[str], tolerance: float) -> dict[str, Any]:
    metrics = combined["metrics"]
    positive = {
        metric: metrics[metric]["oriented_mean_improvement"] > 0.0
        for metric in UNKNOWN_METRICS
    }
    safety = {
        metric: metrics[metric]["oriented_mean_improvement"] >= -tolerance
        for metric in ("unknown_aupr", "unknown_fpr95", "oscr")
    }
    result = {
        "frozen_gate": "strict_v4_ton_router_partial_policy_confirmation_v1",
        "all_four_unknown_metric_means_positive": all(positive.values()),
        "unknown_metric_positive": positive,
        "unknown_auroc_bootstrap_lower_gt_zero": metrics["unknown_auroc"]["bootstrap_95_ci"]["lower"] > 0.0,
        "safety_metrics": safety,
        "all_safety_metrics_pass": all(safety.values()),
        "both_endpoints_exercised": paths[REFERENCE] > 0 and paths["cauchy_all"] > 0,
        "endpoint_counts": dict(paths),
        "cic_iot2023_exact_fallback": REFERENCE,
    }
    result["passes"] = all([
        result["all_four_unknown_metric_means_positive"],
        result["unknown_auroc_bootstrap_lower_gt_zero"],
        result["all_safety_metrics_pass"],
        result["both_endpoints_exercised"],
    ])
    return result


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 ToN router partial-policy confirmation",
        "",
        f"State: **{'confirmed' if report['decision']['passes'] else 'rejected'}**; "
        f"runs: {report['validation']['run_count']}; scenarios: {report['validation']['scenario_count']}.",
        f"Endpoint counts: `{report['decision']['endpoint_counts']}`. CICIoT2023 remains exact current-risk fallback.",
        "",
        "| Metric | Reference | Router | Oriented gain | 95% CI | W/T/L | Holm p |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for metric in METRICS:
        value = report["combined"]["metrics"][metric]
        ci = value["bootstrap_95_ci"]
        p = value["wilcoxon"].get("holm_adjusted_p_value")
        lines.append(
            f"| {metric} | {value['reference_scenario_mean']:.6f} | "
            f"{value['candidate_scenario_mean']:.6f} | {value['oriented_mean_improvement']:+.6f} | "
            f"[{ci['lower']:+.6f}, {ci['upper']:+.6f}] | "
            f"{value['wins']}/{value['ties']}/{value['losses']} | "
            f"{'NA' if p is None else f'{p:.6g}'} |"
        )
    lines.extend(["", f"Frozen gate: **{'PASS' if report['decision']['passes'] else 'FAIL'}**.", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Confirm frozen ToN router partial policy")
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
    paths = Counter(row["candidate_selected"] for row in rows)
    result = {
        "schema_version": "strict_v4_ton_router_partial_policy_confirmation_v1",
        "manifest_sha256": manifest["manifest_sha256"],
        "validation": validation,
        "combined": combined,
        "rows": rows,
        "decision": make_decision(combined, paths, args.nonregression_tolerance),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "confirmation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output_dir / "confirmation.md").write_text(markdown(result), encoding="utf-8")
    print(json.dumps({"decision": result["decision"]}, indent=2))


if __name__ == "__main__":
    main()
