from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from analyze_strict_v4_pseudo_unknown_development import (
    CANDIDATE,
    REFERENCE,
    REQUIRED_ARTIFACTS,
    UNKNOWN_METRICS,
    canonical_hash,
    metric_report,
    validate_pseudo_unknown_protocol,
)
from summarize_paired_confirmation import METRICS, aggregate


EXPECTED_POLICY = "strict_v4_pseudo_unknown_confirmation_v1"


def load_manifest(path: Path, project_root: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "strict_v4_pseudo_unknown_candidate_v1":
        raise ValueError("unexpected pseudo-unknown candidate manifest schema")
    if payload.get("status") != "frozen_unconfirmed":
        raise ValueError("pseudo-unknown candidate is not frozen")
    if payload.get("manifest_sha256") != canonical_hash(payload):
        raise ValueError("pseudo-unknown candidate manifest SHA mismatch")
    for relative, expected in payload["candidate"]["implementation_sha256"].items():
        actual = hashlib.sha256((project_root / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"implementation SHA mismatch: {relative}")
    if payload["candidate"].get("runtime_uses_unknown_or_test_labels") is not False:
        raise ValueError("candidate runtime leakage boundary is invalid")
    confirmation = payload.get("confirmation", {})
    if confirmation.get("seed_disjoint") is not True:
        raise ValueError("confirmation seeds are not disjoint")
    if confirmation.get("scenario_disjoint_from_candidate_development") is not True:
        raise ValueError("confirmation scenarios are not disjoint")
    return payload


def build_rows(root: Path, manifest: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    confirmation = manifest["confirmation"]
    rows = []
    fingerprints = set()
    source_metrics = []
    internal_passes = 0
    for suite, scenarios in confirmation["scenarios"].items():
        for scenario in scenarios:
            for seed in confirmation["seeds"]:
                directory = root / suite / f"{scenario}_seed{seed}"
                missing = [name for name in REQUIRED_ARTIFACTS if not (directory / name).is_file()]
                if missing:
                    raise ValueError(f"missing artifacts under {directory}: {missing}")
                path = directory / "metrics.json"
                raw = path.read_bytes()
                payload = json.loads(raw.decode("utf-8"))
                if int(payload.get("seed", -1)) != int(seed):
                    raise ValueError(f"seed mismatch under {directory}")
                if payload.get("risk_policy") != EXPECTED_POLICY:
                    raise ValueError(f"risk policy mismatch under {directory}")
                protocol = validate_pseudo_unknown_protocol(
                    payload,
                    f"{suite}/{scenario}/{seed}",
                    float(manifest["candidate"]["maximum_alpha"]),
                )
                internal_passes += int(protocol["gate_passes"])
                selected = str(payload["selected_risk"])
                reports = payload.get("reports", {})
                candidate = metric_report(reports.get(selected), "candidate policy")
                reference = metric_report(reports.get(REFERENCE), "reference")
                if metric_report(payload.get("selected_report"), "selected report") != candidate:
                    raise ValueError(f"selected report mismatch under {directory}")
                fingerprint = payload.get("split_metadata", {}).get("split_fingerprint", {}).get("combined")
                if not fingerprint:
                    raise ValueError(f"missing split fingerprint under {directory}")
                fingerprints.add(str(fingerprint))
                source_metrics.append(
                    {"path": path.relative_to(root).as_posix(), "sha256": hashlib.sha256(raw).hexdigest()}
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
                        "split_fingerprint": str(fingerprint),
                        "internal_gate_passes": protocol["gate_passes"],
                        "selected_alpha": protocol["selected_alpha"],
                    }
                )
    if len(rows) != int(confirmation["expected_run_count"]):
        raise ValueError("pseudo-unknown confirmation run count mismatch")
    return rows, {
        "passes": True,
        "run_count": len(rows),
        "scenario_count": int(confirmation["expected_scenario_count"]),
        "seeds": confirmation["seeds"],
        "artifact_checks": len(rows) * len(REQUIRED_ARTIFACTS),
        "split_fingerprint_checks": len(fingerprints),
        "internal_gate_pass_count": internal_passes,
        "source_metrics_combined_sha256": hashlib.sha256(
            json.dumps(source_metrics, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "runtime_uses_unknown_or_test_labels": False,
        "scenario_boundary": confirmation["scenario_boundary"],
    }


def decision(
    combined: dict[str, Any],
    suites: dict[str, dict[str, Any]],
    endpoints: Counter[str],
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
        "frozen_gate": "strict_v4_pseudo_unknown_confirmation_v1",
        "combined_auroc_mean_positive": metrics["unknown_auroc"]["oriented_mean_improvement"] > 0.0,
        "combined_auroc_bootstrap_lower_gt_zero": metrics["unknown_auroc"]["bootstrap_95_ci"]["lower"] > 0.0,
        "combined_safety_metrics": safety,
        "all_combined_safety_metrics_pass": all(safety.values()),
        "suite_unknown_metric_positive": suite_positive,
        "all_suite_unknown_metrics_positive": all(
            value for values in suite_positive.values() for value in values.values()
        ),
        "learned_endpoint_exercised": endpoints[CANDIDATE] > 0,
        "endpoint_counts": dict(endpoints),
        "safety_nonregression_tolerance": float(tolerance),
    }
    result["passes"] = all(
        (
            result["combined_auroc_mean_positive"],
            result["combined_auroc_bootstrap_lower_gt_zero"],
            result["all_combined_safety_metrics_pass"],
            result["all_suite_unknown_metrics_positive"],
            result["learned_endpoint_exercised"],
        )
    )
    return result


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 pseudo-unknown risk confirmation",
        "",
        f"State: **{'confirmed' if report['decision']['passes'] else 'rejected'}**; "
        f"runs: {report['validation']['run_count']}; scenario blocks: "
        f"{report['validation']['scenario_count']}.",
        "Seed repeats are averaged within scenarios before inference.",
        f"Endpoint counts: `{report['decision']['endpoint_counts']}`.",
        "",
        "| Metric | Reference | Candidate policy | Oriented gain | 95% CI | W/T/L | Holm p |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for metric in METRICS:
        values = report["combined"]["metrics"][metric]
        ci = values["bootstrap_95_ci"]
        p_value = values["wilcoxon"].get("holm_adjusted_p_value")
        lines.append(
            f"| {metric} | {values['reference_scenario_mean']:.6f} | "
            f"{values['candidate_scenario_mean']:.6f} | "
            f"{values['oriented_mean_improvement']:+.6f} | "
            f"[{ci['lower']:+.6f}, {ci['upper']:+.6f}] | "
            f"{values['wins']}/{values['ties']}/{values['losses']} | "
            f"{'NA' if p_value is None else f'{p_value:.6g}'} |"
        )
    lines.extend(["", f"Frozen gate: **{'PASS' if report['decision']['passes'] else 'FAIL'}**.", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Confirm strict-v4 pseudo-unknown risk")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-repetitions", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260718)
    parser.add_argument("--nonregression-tolerance", type=float, default=0.01)
    args = parser.parse_args()
    manifest = load_manifest(args.manifest, args.project_root.resolve())
    rows, validation = build_rows(args.root, manifest)
    combined = aggregate(rows, args.bootstrap_repetitions, args.bootstrap_seed)
    suites = {
        suite: aggregate(
            [row for row in rows if row["suite"] == suite],
            args.bootstrap_repetitions,
            args.bootstrap_seed,
        )
        for suite in manifest["confirmation"]["scenarios"]
    }
    endpoints = Counter(row["candidate_selected"] for row in rows)
    result = {
        "schema_version": "strict_v4_pseudo_unknown_confirmation_v1",
        "manifest_sha256": manifest["manifest_sha256"],
        "validation": validation,
        "combined": combined,
        "by_suite": suites,
        "rows": rows,
        "decision": decision(combined, suites, endpoints, args.nonregression_tolerance),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "confirmation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "confirmation.md").write_text(render_markdown(result), encoding="utf-8")
    print(json.dumps({"decision": result["decision"]}, indent=2))


if __name__ == "__main__":
    main()
