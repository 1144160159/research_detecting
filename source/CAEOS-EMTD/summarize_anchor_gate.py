from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon


SECONDARY_METRICS = {
    "unknown_aupr": 1.0,
    "oscr": 1.0,
    "unknown_fpr95": -1.0,
    "unknown_f1": 1.0,
    "known_acceptance_rate": 1.0,
    "unknown_rejection_rate": 1.0,
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize nested anchor/conflict gate")
    parser.add_argument("input_roots", nargs="+")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    return parser.parse_args()


def rank(aggregates, name: str):
    value = aggregates[name]
    return (
        value["robust_objective"],
        value["minimum_auroc"],
        value["mean_auroc"],
    )


def paired_p_value(left: np.ndarray, right: np.ndarray) -> float:
    difference = np.asarray(left) - np.asarray(right)
    nonzero = difference[np.abs(difference) > 1e-12]
    if nonzero.size == 0:
        return 1.0
    return float(wilcoxon(nonzero, alternative="two-sided").pvalue)


def oracle_candidate_names(metrics: dict[str, object]) -> tuple[str, ...]:
    names = ["anchor_support", "cauchy_evidence"]
    risk_selection = metrics.get("risk_selection", "")
    if risk_selection == "nested_hierarchical_joint_gate":
        names.append("cauchy_all")
    elif risk_selection == "nested_hierarchical_fallback_gate":
        names.append("cauchy_baseline")
    reports = metrics["reports"]
    return tuple(name for name in names if name in reports)


def aggregate(
    rows: list[dict[str, object]],
    prefix: str,
    baseline_prefix: str = "old",
) -> dict[str, object]:
    new = np.asarray([row[f"{prefix}_auroc"] for row in rows], dtype=np.float64)
    old = np.asarray(
        [row[f"{baseline_prefix}_auroc"] for row in rows], dtype=np.float64
    )
    oracle = np.asarray([row["oracle_auroc"] for row in rows], dtype=np.float64)
    delta = new - old
    result = {
        "number_of_runs": len(rows),
        "new_mean_auroc": float(new.mean()),
        "new_std_auroc": float(new.std()),
        "new_minimum_auroc": float(new.min()),
        "old_mean_auroc": float(old.mean()),
        "old_std_auroc": float(old.std()),
        "old_minimum_auroc": float(old.min()),
        "mean_delta": float(delta.mean()),
        "wins": int((delta > 1e-12).sum()),
        "ties": int((np.abs(delta) <= 1e-12).sum()),
        "losses": int((delta < -1e-12).sum()),
        "wilcoxon_p": paired_p_value(new, old),
        "selection_accuracy": float(
            np.mean([row[f"{prefix}_selection_correct"] for row in rows])
        ),
        "mean_oracle_regret": float((oracle - new).mean()),
        "maximum_oracle_regret": float((oracle - new).max()),
        "selected_paths": dict(
            Counter(row[f"{prefix}_selected"] for row in rows)
        ),
    }
    secondary = {}
    for metric, direction in SECONDARY_METRICS.items():
        candidate_key = f"{prefix}_{metric}"
        baseline_key = f"{baseline_prefix}_{metric}"
        if not all(candidate_key in row and baseline_key in row for row in rows):
            continue
        candidate = np.asarray(
            [row[candidate_key] for row in rows], dtype=np.float64
        )
        baseline = np.asarray(
            [row[baseline_key] for row in rows], dtype=np.float64
        )
        secondary[metric] = {
            "new_mean": float(candidate.mean()),
            "baseline_mean": float(baseline.mean()),
            "raw_delta": float((candidate - baseline).mean()),
            "oriented_improvement": float(
                direction * (candidate - baseline).mean()
            ),
        }
    result["secondary_metrics"] = secondary
    return result


def main() -> None:
    args = parse_arguments()
    rows = []
    seen = set()
    for input_root in args.input_roots:
        root = Path(input_root)
        for metrics_path in sorted(root.glob("*/*/metrics.json")):
            resolved = metrics_path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            with metrics_path.open("r", encoding="utf-8") as handle:
                metrics = json.load(handle)
            suite = metrics_path.parts[-3]
            run = metrics_path.parent.name
            aggregates = metrics["risk_selection_details"]["candidate_aggregates"]
            old_selected = max(
                ("support_union", "cauchy_evidence"),
                key=lambda name: rank(aggregates, name),
            )
            new_selected = metrics["selected_risk"]
            risk_selection = metrics.get("risk_selection", "")
            hierarchical_selected = (
                "anchor_support"
                if old_selected == "support_union"
                else "cauchy_evidence"
            )
            candidate_names = oracle_candidate_names(metrics)
            oracle_selected = max(
                candidate_names,
                key=lambda name: metrics["reports"][name]["unknown_auroc"],
            )
            selected_report = metrics["selected_report"]
            old_report = metrics["reports"][old_selected]
            hierarchical_report = metrics["reports"][hierarchical_selected]
            rows.append(
                {
                    "suite": suite,
                    "run": run,
                    "risk_selection": risk_selection,
                    "old_selected": old_selected,
                    "new_selected": new_selected,
                    "hierarchical_selected": hierarchical_selected,
                    "oracle_selected": oracle_selected,
                    "old_auroc": old_report["unknown_auroc"],
                    "new_auroc": selected_report["unknown_auroc"],
                    "hierarchical_auroc": hierarchical_report["unknown_auroc"],
                    "oracle_auroc": metrics["reports"][oracle_selected]["unknown_auroc"],
                    "new_selection_correct": new_selected == oracle_selected,
                    "hierarchical_selection_correct": hierarchical_selected
                    == oracle_selected,
                    "inner_anchor_support_gain": (
                        aggregates["anchor_support"]["robust_objective"]
                        - aggregates["support_union"]["robust_objective"]
                    ),
                    "anchor_auroc": metrics["reports"]["anchor_support"]["unknown_auroc"],
                    "support_auroc": metrics["reports"]["support_union"]["unknown_auroc"],
                    "conflict_auroc": metrics["reports"]["cauchy_evidence"]["unknown_auroc"],
                    **{
                        f"new_{metric}": selected_report[metric]
                        for metric in SECONDARY_METRICS
                    },
                    **{
                        f"old_{metric}": old_report[metric]
                        for metric in SECONDARY_METRICS
                    },
                    **{
                        f"hierarchical_{metric}": hierarchical_report[metric]
                        for metric in SECONDARY_METRICS
                    },
                }
            )
    if not rows:
        raise ValueError(f"no metrics found under {args.input_roots}")

    by_suite = defaultdict(list)
    for row in rows:
        by_suite[row["suite"]].append(row)
    result = {
        "input_roots": args.input_roots,
        "direct_gate": {
            "global": aggregate(rows, "new"),
            "by_suite": {
                suite: aggregate(values, "new")
                for suite, values in by_suite.items()
            },
        },
        "joint_gate_vs_hierarchical": {
            "global": aggregate(rows, "new", "hierarchical"),
            "by_suite": {
                suite: aggregate(values, "new", "hierarchical")
                for suite, values in by_suite.items()
            },
        },
        "hierarchical_gate": {
            "global": aggregate(rows, "hierarchical"),
            "by_suite": {
                suite: aggregate(values, "hierarchical")
                for suite, values in by_suite.items()
            },
        },
        "runs": rows,
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with output_json.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)

    joint_modes = {
        "nested_hierarchical_joint_gate",
        "nested_hierarchical_fallback_gate",
    }
    primary_name = (
        "joint_gate_vs_hierarchical"
        if rows and all(row["risk_selection"] in joint_modes for row in rows)
        else "hierarchical_gate"
    )
    baseline_label = "v1.4.3 hierarchical gate" if primary_name == "joint_gate_vs_hierarchical" else "original nested gate"
    primary = result[primary_name]
    lines = [
        "# Nested anchor/conflict gate summary",
        "",
        "| Suite | Runs | New AUROC | Baseline AUROC | Delta | W/T/L | Selection accuracy | Regret |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for suite, values in [
        *sorted(primary["by_suite"].items()),
        ("global", primary["global"]),
    ]:
        lines.append(
            "| %s | %d | %.6f | %.6f | %+.6f | %d/%d/%d | %.1f%% | %.6f |"
            % (
                suite,
                values["number_of_runs"],
                values["new_mean_auroc"],
                values["old_mean_auroc"],
                values["mean_delta"],
                values["wins"],
                values["ties"],
                values["losses"],
                100.0 * values["selection_accuracy"],
                values["mean_oracle_regret"],
            )
        )
    lines.extend(
        [
            "",
            "Global Wilcoxon p-value: `%.6g`."
            % primary["global"]["wilcoxon_p"],
            "",
            "Direct gate mean AUROC: `%.6f`; hierarchical gate mean AUROC: `%.6f`."
            % (
                result["direct_gate"]["global"]["new_mean_auroc"],
                result["hierarchical_gate"]["global"]["new_mean_auroc"],
            ),
            "Primary summary mode: `%s`." % primary_name,
            "Primary baseline: `%s`." % baseline_label,
            "",
            "The original nested gate is reconstructed from the same run by applying the original rule to `support_union` and `cauchy_evidence`; the v1.4.3 hierarchical gate additionally replaces the support branch with `anchor_support`.",
        ]
    )
    secondary = primary["global"]["secondary_metrics"]
    if secondary:
        lines.extend(
            [
                "",
                "| Metric | New | Baseline | Oriented improvement |",
                "|---|---:|---:|---:|",
            ]
        )
        for metric, values in secondary.items():
            lines.append(
                "| %s | %.6f | %.6f | %+.6f |"
                % (
                    metric,
                    values["new_mean"],
                    values["baseline_mean"],
                    values["oriented_improvement"],
                )
            )
    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(primary["global"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
