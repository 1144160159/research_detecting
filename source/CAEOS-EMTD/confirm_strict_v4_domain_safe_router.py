from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from select_strict_v4_external_risk_candidate import canonical_hash
from summarize_paired_confirmation import METRICS, aggregate
from summarize_strict_v4_full103 import PAIRWISE_METHOD, UNKNOWN_METRICS, parse_task


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_manifest(payload: dict[str, Any], schema: str, label: str) -> None:
    if payload.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if payload.get("manifest_sha256") != canonical_hash(payload):
        raise ValueError(f"{label} manifest SHA mismatch")


def build_rows(
    raw: dict[str, Any],
    coverage: dict[str, Any],
    router: dict[str, Any],
    protocol: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    seeds = set(protocol["confirmation_seeds"])
    expected_scenarios = {
        (suite, scenario)
        for suite, details in coverage["scenario_registry"].items()
        for scenario in details["scenarios"]
    }
    expected_runs = len(expected_scenarios) * len(seeds)
    if raw.get("overall", {}).get("number_of_runs") != expected_runs:
        raise ValueError("raw fusion run count differs from confirmation protocol")
    if set(raw.get("selection_scope", {}).get("seeds", [])) != seeds:
        raise ValueError("raw fusion seed scope differs from confirmation protocol")
    observed: set[tuple[str, str, int]] = set()
    scenario_seeds: dict[tuple[str, str], set[int]] = defaultdict(set)
    rows: list[dict[str, Any]] = []
    routes: Counter[str] = Counter()
    for run in raw["runs"]:
        scenario, seed = parse_task(run["task"])
        suite = run["suite"]
        key = (suite, scenario, seed)
        if seed not in seeds or key in observed:
            raise ValueError(f"unexpected or duplicate confirmation task: {key}")
        if (suite, scenario) not in expected_scenarios:
            raise ValueError(f"scenario is absent from coverage manifest: {key}")
        audit = run.get("audit", {})
        if audit.get("split_fingerprints_identical") is not True:
            raise ValueError(f"split fingerprint mismatch for {key}")
        if not (
            audit.get("caeos_unknown_or_test_labels_used_for_selection") is False
            and audit.get(
                "expert_unknown_or_test_labels_used_for_fitting_or_selection"
            )
            is False
            and audit.get("fusion_calibration_split") == "known_only_validation"
            and audit.get("test_labels_used_for_final_metrics_only") is True
        ):
            raise ValueError(f"fusion leakage audit failed for {key}")
        observed.add(key)
        scenario_seeds[(suite, scenario)].add(seed)
        method = router["routing"][suite]["method"]
        candidate = (
            run["gate_report"]
            if method == PAIRWISE_METHOD
            else run["reports"][method]
        )
        for name, report in (("candidate", candidate), ("reference", run["gate_report"])):
            missing = [metric for metric in METRICS if metric not in report]
            if missing:
                raise ValueError(f"{name} report misses {missing} for {key}")
        rows.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed": seed,
                "candidate_selected": method,
                "reference_selected": PAIRWISE_METHOD,
                "candidate_report": candidate,
                "reference_report": run["gate_report"],
            }
        )
        routes[method] += 1
    missing = [
        f"{suite}/{scenario}"
        for suite, scenario in sorted(expected_scenarios)
        if scenario_seeds[(suite, scenario)] != seeds
    ]
    if missing:
        raise ValueError(f"incomplete confirmation seed coverage: {missing}")
    return rows, {
        "passes": True,
        "paired_runs": len(rows),
        "scenario_count": len(expected_scenarios),
        "seeds": sorted(seeds),
        "task_set_complete": len(observed) == expected_runs,
        "route_run_counts": dict(sorted(routes.items())),
        "unknown_or_test_labels_used_for_confirmation_selection": False,
        "caeos_and_expert_training_selection_leakage_checks": len(rows),
        "known_only_fusion_calibration_checks": len(rows),
    }


def suite_nonregression(
    rows: list[dict[str, Any]], seeds: list[int]
) -> dict[str, dict[str, float]]:
    suites = sorted({row["suite"] for row in rows})
    output: dict[str, dict[str, float]] = {}
    for suite in suites:
        report = aggregate(
            [row for row in rows if row["suite"] == suite], 10000, 20260719
        )
        output[suite] = {
            metric: float(report["metrics"][metric]["oriented_mean_improvement"])
            for metric in UNKNOWN_METRICS
        }
    return output


def confirmation_decision(
    inference: dict[str, Any], by_suite: dict[str, dict[str, float]]
) -> dict[str, Any]:
    metrics = inference["metrics"]
    means_positive = {
        metric: metrics[metric]["oriented_mean_improvement"] > 0.0
        for metric in UNKNOWN_METRICS
    }
    holm = {
        metric: metrics[metric]["wilcoxon"]["holm_adjusted_p_value"] < 0.05
        for metric in UNKNOWN_METRICS
    }
    suite_safe = {
        suite: {metric: value >= -1e-12 for metric, value in values.items()}
        for suite, values in by_suite.items()
    }
    known = metrics["known_macro_f1"]
    checks = {
        "all_unknown_metric_means_strictly_positive": all(means_positive.values()),
        "auroc_bootstrap_lower_strictly_positive": metrics["unknown_auroc"][
            "bootstrap_95_ci"
        ]["lower"]
        > 0.0,
        "aupr_bootstrap_lower_strictly_positive": metrics["unknown_aupr"][
            "bootstrap_95_ci"
        ]["lower"]
        > 0.0,
        "all_unknown_metric_holm_p_below_0_05": all(holm.values()),
        "all_suite_unknown_metric_means_nonnegative": all(
            value for values in suite_safe.values() for value in values.values()
        ),
        "known_macro_f1_unchanged": abs(known["raw_mean_delta"]) <= 1e-12,
    }
    return {
        "passes": all(checks.values()),
        "checks": checks,
        "unknown_metric_mean_checks": means_positive,
        "unknown_metric_holm_checks": holm,
        "suite_nonregression_checks": suite_safe,
    }


def render(report: dict[str, Any]) -> str:
    inference = report["scenario_blocked_inference"]
    lines = [
        "# Strict-v4 frozen domain-safe router confirmation",
        "",
        f"Validation: **PASS**; paired runs: {report['validation']['paired_runs']}; "
        f"scenarios: {report['validation']['scenario_count']}; seeds: "
        f"{report['validation']['seeds']}.",
        "Seed repeats are averaged inside each dataset-scenario before inference.",
        "",
        "| Metric | Pairwise | Router | Gain | 95% CI | W/T/L | Holm p |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for metric in METRICS:
        item = inference["metrics"][metric]
        ci = item["bootstrap_95_ci"]
        p_value = item["wilcoxon"]["holm_adjusted_p_value"]
        p_text = "NA" if p_value is None else f"{p_value:.3g}"
        lines.append(
            f"| {metric} | {item['reference_scenario_mean']:.6f} | "
            f"{item['candidate_scenario_mean']:.6f} | "
            f"{item['oriented_mean_improvement']:+.6f} | "
            f"[{ci['lower']:+.6f}, {ci['upper']:+.6f}] | "
            f"{item['wins']}/{item['ties']}/{item['losses']} | {p_text} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"Frozen confirmation gate: **{'PASS' if report['decision']['passes'] else 'FAIL'}**.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage-manifest", type=Path, required=True)
    parser.add_argument("--router-manifest", type=Path, required=True)
    parser.add_argument("--protocol-manifest", type=Path, required=True)
    parser.add_argument("--raw-fusion", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    coverage = json.loads(args.coverage_manifest.read_text(encoding="utf-8"))
    router = json.loads(args.router_manifest.read_text(encoding="utf-8"))
    protocol = json.loads(args.protocol_manifest.read_text(encoding="utf-8"))
    validate_manifest(coverage, "strict_v4_coverage_manifest_v2", "coverage")
    validate_manifest(
        router, "strict_v4_domain_safe_router_candidate_v1", "router"
    )
    validate_manifest(
        protocol,
        "strict_v4_domain_safe_router_confirmation_protocol_v1",
        "confirmation protocol",
    )
    if protocol["coverage_manifest_sha256"] != coverage["manifest_sha256"]:
        raise ValueError("protocol coverage binding mismatch")
    if protocol["router_manifest_sha256"] != router["manifest_sha256"]:
        raise ValueError("protocol router binding mismatch")
    raw = json.loads(args.raw_fusion.read_text(encoding="utf-8"))
    rows, validation = build_rows(raw, coverage, router, protocol)
    inference = aggregate(rows, 20000, 20260719)
    by_suite = suite_nonregression(rows, protocol["confirmation_seeds"])
    result = {
        "schema_version": "strict_v4_domain_safe_router_confirmation_v1",
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "router_manifest_sha256": router["manifest_sha256"],
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "raw_fusion_sha256": file_hash(args.raw_fusion),
        "analysis_implementation_sha256": file_hash(Path(__file__)),
        "validation": validation,
        "scenario_blocked_inference": inference,
        "suite_oriented_mean_gains": by_suite,
        "decision": confirmation_decision(inference, by_suite),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "confirmation.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "confirmation.md").write_text(
        render(result), encoding="utf-8"
    )
    print(render(result))


if __name__ == "__main__":
    main()
