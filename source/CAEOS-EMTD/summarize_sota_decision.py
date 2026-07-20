from __future__ import annotations

import argparse
import json
from pathlib import Path


METRICS = (
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
    "known_macro_f1",
)
LOWER_IS_BETTER = {"unknown_fpr95"}


def read_object(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def scope_decision(scope: dict[str, object]) -> dict[str, object]:
    methods = scope.get("methods")
    if not isinstance(methods, dict) or not methods:
        raise ValueError("comparison scope contains no methods")
    metric_results = {}
    for metric in METRICS:
        rows = []
        gate_values = set()
        for method, payload in methods.items():
            if not isinstance(payload, dict):
                raise ValueError(f"invalid method payload: {method}")
            metrics = payload.get("metrics")
            if not isinstance(metrics, dict) or metric not in metrics:
                raise ValueError(f"missing metric {metric}: {method}")
            item = metrics[metric]
            if not isinstance(item, dict):
                raise ValueError(f"invalid metric {metric}: {method}")
            gate = float(item["gate_scenario_mean"])
            baseline = float(item["baseline_scenario_mean"])
            gate_values.add(gate)
            inference = item["paired_inference"]
            rows.append((str(method), baseline, inference))
        if len(gate_values) != 1:
            raise ValueError(f"inconsistent CAEOS mean for metric {metric}")
        gate = next(iter(gate_values))
        lower = metric in LOWER_IS_BETTER
        strongest = (min if lower else max)(rows, key=lambda row: row[1])
        better_count = sum(
            row[1] < gate - 1e-12 if lower else row[1] > gate + 1e-12
            for row in rows
        )
        tied_count = sum(abs(row[1] - gate) <= 1e-12 for row in rows)
        inference = strongest[2]
        ci = inference["bootstrap_95_ci"]
        wilcoxon = inference["wilcoxon"]
        delta = float(inference["mean_delta"])
        confirmed = (
            delta > 0.0
            and float(ci["lower"]) > 0.0
            and float(wilcoxon["holm_adjusted_p_value"]) < 0.05
        )
        metric_results[metric] = {
            "direction": "lower_is_better" if lower else "higher_is_better",
            "caeos_mean": gate,
            "caeos_rank_among_all_methods": better_count + 1,
            "total_methods_including_caeos": len(rows) + 1,
            "baseline_ties_with_caeos": tied_count,
            "strongest_baseline": strongest[0],
            "strongest_baseline_mean": strongest[1],
            "oriented_delta_vs_strongest": delta,
            "bootstrap_95_ci": ci,
            "holm_adjusted_p_value": wilcoxon["holm_adjusted_p_value"],
            "wins_ties_losses": [
                inference["wins"],
                inference["ties"],
                inference["losses"],
            ],
            "confirmed_better_than_strongest": confirmed,
        }
    primary = (
        "unknown_auroc",
        "unknown_aupr",
        "unknown_fpr95",
        "oscr",
    )
    return {
        "scope": scope.get("scope"),
        "scenario_inference_units": scope.get("scenario_inference_units"),
        "baseline_method_count": len(methods),
        "metrics": metric_results,
        "all_primary_metrics_mean_rank_one": all(
            metric_results[name]["caeos_rank_among_all_methods"] == 1
            for name in primary
        ),
        "all_metrics_mean_rank_one": all(
            item["caeos_rank_among_all_methods"] == 1
            for item in metric_results.values()
        ),
        "all_primary_strongest_comparisons_confirmed": all(
            metric_results[name]["confirmed_better_than_strongest"]
            for name in primary
        ),
        "all_metrics_strongest_comparisons_confirmed": all(
            item["confirmed_better_than_strongest"]
            for item in metric_results.values()
        ),
    }


def build_claim_gate(
    global_scope: dict[str, object], by_suite: dict[str, dict[str, object]]
) -> dict[str, object]:
    has_suites = bool(by_suite)
    gates = {
        "global_primary_mean_rank_one": bool(
            global_scope["all_primary_metrics_mean_rank_one"]
        ),
        "global_all_metrics_mean_rank_one": bool(
            global_scope["all_metrics_mean_rank_one"]
        ),
        "global_primary_confirmed": bool(
            global_scope["all_primary_strongest_comparisons_confirmed"]
        ),
        "global_all_metrics_confirmed": bool(
            global_scope["all_metrics_strongest_comparisons_confirmed"]
        ),
        "cross_suite_primary_mean_rank_one": has_suites
        and all(
            scope["all_primary_metrics_mean_rank_one"]
            for scope in by_suite.values()
        ),
        "cross_suite_all_metrics_mean_rank_one": has_suites
        and all(scope["all_metrics_mean_rank_one"] for scope in by_suite.values()),
        "cross_suite_primary_confirmed": has_suites
        and all(
            scope["all_primary_strongest_comparisons_confirmed"]
            for scope in by_suite.values()
        ),
        "cross_suite_all_metrics_confirmed": has_suites
        and all(
            scope["all_metrics_strongest_comparisons_confirmed"]
            for scope in by_suite.values()
        ),
    }
    gates["comprehensive_confirmed_sota"] = all(
        gates[name]
        for name in (
            "global_all_metrics_mean_rank_one",
            "global_all_metrics_confirmed",
            "cross_suite_all_metrics_mean_rank_one",
        )
    )
    if gates["comprehensive_confirmed_sota"]:
        highest = "comprehensive_confirmed_sota"
    elif (
        gates["global_primary_confirmed"]
        and gates["cross_suite_primary_mean_rank_one"]
    ):
        highest = "global_confirmed_cross_suite_primary_mean_sota"
    elif gates["global_primary_confirmed"]:
        highest = "global_confirmed_primary_sota"
    elif gates["cross_suite_primary_mean_rank_one"]:
        highest = "cross_suite_primary_mean_sota_only"
    elif gates["global_primary_mean_rank_one"]:
        highest = "global_primary_mean_sota_only"
    else:
        highest = "no_sota_claim"
    return {
        "suite_count": len(by_suite),
        "gates": gates,
        "highest_supported_claim": highest,
        "full_sota_claim_allowed": gates["comprehensive_confirmed_sota"],
        "fail_closed_note": (
            "A full SOTA claim requires rank one and confirmatory superiority on "
            "all five metrics in the global scenario-blocked family, plus rank one "
            "on all five metrics in every reported suite. Suite-wise significance "
            "is reported as stronger replication evidence but is not required because "
            "small suite-level scenario counts can make family-wise significance "
            "mathematically unattainable."
        ),
        "confirmatory_scope": "global_scenario_blocked_family",
        "cross_suite_scope": "all_five_metric_mean_rank_nonregression",
    }


def build_decision(report: dict[str, object]) -> dict[str, object]:
    global_scope = report.get("global")
    by_suite = report.get("by_suite")
    if not isinstance(global_scope, dict) or not isinstance(by_suite, dict):
        raise ValueError("comparison report lacks global or by_suite results")
    global_decision = scope_decision(global_scope)
    suite_decisions = {
        str(suite): scope_decision(scope)
        for suite, scope in sorted(by_suite.items())
        if isinstance(scope, dict)
    }
    return {
        "schema_version": "strict_v2_sota_decision_v1",
        "source_schema_version": report.get("schema_version"),
        "interpretation": {
            "mean_rank_one": "CAEOS has the best scenario-balanced mean",
            "confirmed_better_than_strongest": (
                "positive oriented mean, bootstrap CI lower bound > 0, and "
                "Holm-adjusted paired Wilcoxon p < 0.05"
            ),
        },
        "global": global_decision,
        "by_suite": suite_decisions,
        "claim_gate": build_claim_gate(global_decision, suite_decisions),
    }


def markdown(decision: dict[str, object]) -> str:
    claim_gate = decision["claim_gate"]
    lines = [
        "# Strict-v2 SOTA decision",
        "",
        "Mean rank and confirmatory significance are reported separately.",
        "",
        f"Highest supported claim: `{claim_gate['highest_supported_claim']}`",
        f"Full SOTA claim allowed: `{claim_gate['full_sota_claim_allowed']}`",
        "",
        "## Claim gates",
        "",
        "| Gate | Pass |",
        "|---|---:|",
    ]
    lines.extend(
        f"| {name} | {str(value).lower()} |"
        for name, value in claim_gate["gates"].items()
    )
    lines.extend(["", claim_gate["fail_closed_note"], ""])
    scopes = [("global", decision["global"]), *decision["by_suite"].items()]
    for name, scope in scopes:
        lines.extend(
            [
                f"## {name}",
                "",
                f"Scenarios: {scope['scenario_inference_units']}; baselines: {scope['baseline_method_count']}",
                "",
                "| Metric | CAEOS | Rank | Strongest baseline | Baseline | Delta | 95% CI | Holm p | Confirmed |",
                "|---|---:|---:|---|---:|---:|---:|---:|---:|",
            ]
        )
        for metric in METRICS:
            item = scope["metrics"][metric]
            ci = item["bootstrap_95_ci"]
            lines.append(
                f"| {metric} | {item['caeos_mean']:.6f} | "
                f"{item['caeos_rank_among_all_methods']}/{item['total_methods_including_caeos']} | "
                f"{item['strongest_baseline']} | {item['strongest_baseline_mean']:.6f} | "
                f"{item['oriented_delta_vs_strongest']:+.6f} | "
                f"[{ci['lower']:+.6f}, {ci['upper']:+.6f}] | "
                f"{item['holm_adjusted_p_value']:.6g} | "
                f"{str(item['confirmed_better_than_strongest']).lower()} |"
            )
        lines.extend(
            [
                "",
                f"All primary means rank first: `{scope['all_primary_metrics_mean_rank_one']}`",
                f"All metrics mean rank first: `{scope['all_metrics_mean_rank_one']}`",
                f"All primary strongest comparisons confirmed: `{scope['all_primary_strongest_comparisons_confirmed']}`",
                f"All metrics strongest comparisons confirmed: `{scope['all_metrics_strongest_comparisons_confirmed']}`",
                "",
            ]
        )
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize strict-v2 SOTA evidence")
    parser.add_argument("--comparison", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--markdown-output")
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    result = build_decision(read_object(Path(args.comparison)))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    markdown_output = (
        Path(args.markdown_output)
        if args.markdown_output
        else output.with_suffix(".md")
    )
    markdown_output.write_text(markdown(result), encoding="utf-8")
    print(json.dumps(result["global"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
