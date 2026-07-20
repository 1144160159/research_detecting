from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from analyze_strict_v4_local_rank_development import CANDIDATE
from analyze_strict_v4_pseudo_unknown_development import (
    REFERENCE,
    REQUIRED_ARTIFACTS,
    UNKNOWN_METRICS,
    canonical_hash,
    metric_report,
)
from summarize_paired_confirmation import METRICS, aggregate


EXPECTED_POLICY = "strict_v4_local_rank_confirmation_v1"


def load_manifest(path: Path, project_root: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "strict_v4_local_rank_candidate_v1":
        raise ValueError("unexpected local-rank manifest schema")
    if payload.get("status") != "frozen_unconfirmed":
        raise ValueError("local-rank candidate is not frozen")
    if payload.get("manifest_sha256") != canonical_hash(payload):
        raise ValueError("local-rank manifest SHA mismatch")
    for relative, expected in payload["candidate"]["implementation_sha256"].items():
        actual = hashlib.sha256((project_root / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"implementation SHA mismatch: {relative}")
    if payload["candidate"].get("runtime_uses_unknown_or_test_labels") is not False:
        raise ValueError("local-rank runtime leakage boundary is invalid")
    if payload["confirmation"].get("seed_disjoint") is not True:
        raise ValueError("confirmation seeds are not disjoint")
    return payload


def validate_runtime(
    payload: dict[str, Any], manifest: dict[str, Any], label: str
) -> dict[str, Any]:
    candidate = manifest["candidate"]
    arguments = payload.get("arguments", {})
    if arguments.get("risk_selection") != candidate["risk_selection"]:
        raise ValueError(f"risk selection mismatch for {label}")
    details = payload.get("risk_selection_details", {})
    if details.get("unknown_or_test_labels_used_for_selection") is not False:
        raise ValueError(f"runtime leakage guard failed for {label}")
    learned = details.get("pseudo_unknown_learned_blend", {})
    if learned.get("unknown_or_test_labels_used") is not False:
        raise ValueError(f"learned-risk leakage guard failed for {label}")
    robust = details.get("pseudo_unknown_robust_fold_gate", {})
    local = details.get("pseudo_unknown_local_rank", {})
    checks = (
        (
            float(robust.get("required_minimum_fold_gain", float("nan"))),
            float(candidate["minimum_fold_gain"]),
            "minimum fold gain",
        ),
        (
            float(details.get("pseudo_unknown_max_alpha", float("nan"))),
            float(candidate["maximum_alpha"]),
            "maximum alpha",
        ),
        (float(local.get("bins", float("nan"))), float(candidate["local_rank_bins"]), "bins"),
        (float(local.get("beta", float("nan"))), float(candidate["local_rank_beta"]), "beta"),
    )
    for observed, expected, name in checks:
        if abs(observed - expected) > 1e-12:
            raise ValueError(f"{name} mismatch for {label}")
    if local.get("global_reference_bin_order_preserved") is not True:
        raise ValueError(f"global bin order guard failed for {label}")
    gate = bool(robust.get("passes"))
    if bool(details.get("pseudo_unknown_gate_passes")) != gate:
        raise ValueError(f"gate record mismatch for {label}")
    expected_endpoint = CANDIDATE if gate else REFERENCE
    if payload.get("selected_risk") != expected_endpoint:
        raise ValueError(f"endpoint mismatch for {label}")
    return {
        "gate_passes": gate,
        "minimum_fold_metric_gain": float(robust["minimum_fold_metric_gain"]),
    }


def build_rows(
    root: Path, manifest: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    confirmation = manifest["confirmation"]
    rows = []
    fingerprints = set()
    source = []
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
                protocol = validate_runtime(payload, manifest, f"{suite}/{scenario}/{seed}")
                selected = str(payload["selected_risk"])
                candidate_report = metric_report(
                    payload["reports"][selected], "candidate policy"
                )
                reference_report = metric_report(
                    payload["reports"][REFERENCE], "reference"
                )
                if metric_report(payload["selected_report"], "selected report") != candidate_report:
                    raise ValueError(f"selected report mismatch under {directory}")
                fingerprint = (
                    payload.get("split_metadata", {})
                    .get("split_fingerprint", {})
                    .get("combined")
                )
                if not fingerprint:
                    raise ValueError(f"missing split fingerprint under {directory}")
                fingerprints.add(str(fingerprint))
                source.append(
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
                        "candidate_report": candidate_report,
                        "reference_report": reference_report,
                        "split_fingerprint": str(fingerprint),
                        **protocol,
                    }
                )
    if len(rows) != int(confirmation["expected_run_count"]):
        raise ValueError("local-rank confirmation run count mismatch")
    return rows, {
        "passes": True,
        "run_count": len(rows),
        "scenario_count": int(confirmation["expected_scenario_count"]),
        "seeds": confirmation["seeds"],
        "artifact_checks": len(rows) * len(REQUIRED_ARTIFACTS),
        "split_fingerprint_checks": len(fingerprints),
        "runtime_uses_unknown_or_test_labels": False,
        "scenario_boundary": confirmation["scenario_boundary"],
        "source_metrics_combined_sha256": hashlib.sha256(
            json.dumps(source, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }


def make_decision(
    combined: dict[str, Any], suites: dict[str, dict[str, Any]], endpoints: Counter[str]
) -> dict[str, Any]:
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
    result = {
        "frozen_gate": "strict_v4_local_rank_confirmation_v1",
        "combined_unknown_metrics_positive": combined_positive,
        "all_combined_unknown_metrics_positive": all(combined_positive.values()),
        "combined_auroc_bootstrap_lower_gt_zero": (
            combined["metrics"]["unknown_auroc"]["bootstrap_95_ci"]["lower"] > 0.0
        ),
        "suite_unknown_metric_nonnegative": suite_nonnegative,
        "all_suite_unknown_metrics_nonnegative": all(
            value for values in suite_nonnegative.values() for value in values.values()
        ),
        "local_rank_endpoint_exercised": endpoints[CANDIDATE] > 0,
        "reference_fallback_exercised": endpoints[REFERENCE] > 0,
        "endpoint_counts": dict(endpoints),
    }
    result["passes"] = all(
        (
            result["all_combined_unknown_metrics_positive"],
            result["combined_auroc_bootstrap_lower_gt_zero"],
            result["all_suite_unknown_metrics_nonnegative"],
            result["local_rank_endpoint_exercised"],
            result["reference_fallback_exercised"],
        )
    )
    return result


def render(report: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 local-rank confirmation",
        "",
        f"State: **{'confirmed' if report['decision']['passes'] else 'rejected'}**; "
        f"runs: {report['validation']['run_count']}; scenario blocks: "
        f"{report['validation']['scenario_count']}.",
        f"Endpoint counts: `{report['decision']['endpoint_counts']}`.",
        "",
        "| Metric | Reference | Candidate | Oriented gain | 95% CI | W/T/L | Holm p |",
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
    lines.extend(
        [
            "",
            f"Frozen gate: **{'PASS' if report['decision']['passes'] else 'FAIL'}**.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-repetitions", type=int, default=10000)
    args = parser.parse_args()
    manifest = load_manifest(args.manifest, args.project_root.resolve())
    rows, validation = build_rows(args.root, manifest)
    combined = aggregate(rows, args.bootstrap_repetitions, 20260718)
    suites = {
        suite: aggregate(
            [row for row in rows if row["suite"] == suite],
            args.bootstrap_repetitions,
            20260718,
        )
        for suite in manifest["confirmation"]["scenarios"]
    }
    endpoints = Counter(row["candidate_selected"] for row in rows)
    result = {
        "schema_version": "strict_v4_local_rank_confirmation_v1",
        "manifest_sha256": manifest["manifest_sha256"],
        "validation": validation,
        "combined": combined,
        "by_suite": suites,
        "rows": rows,
        "decision": make_decision(combined, suites, endpoints),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "confirmation.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "confirmation.md").write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
