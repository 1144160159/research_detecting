from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from screen_edge_risk_candidates import METRICS, UNKNOWN_METRICS, screen


CORRELATION_THRESHOLDS = (0.70, 0.75, 0.80, 0.85, 0.90, 0.925)
RANK_DIFFERENCE_THRESHOLDS = (0.09, 0.11, 0.13, 0.15, 0.17, 0.19)
PARENTS = ("entropy", "rank_union")


def build_rules() -> list[dict[str, object]]:
    rules: list[dict[str, object]] = [
        {"name": "always_rank_union", "kind": "always_rank_union"},
        {"name": "always_entropy", "kind": "always_entropy"},
    ]
    for threshold in CORRELATION_THRESHOLDS:
        token = str(threshold)
        for operator in ("ge", "le"):
            rules.append(
                {
                    "name": f"entropy_if_corr_{operator}_{token}",
                    "kind": "correlation",
                    "operator": operator,
                    "threshold": threshold,
                }
            )
    for threshold in RANK_DIFFERENCE_THRESHOLDS:
        token = str(threshold)
        for operator in ("ge", "le"):
            rules.append(
                {
                    "name": f"entropy_if_mad_{operator}_{token}",
                    "kind": "rank_difference",
                    "operator": operator,
                    "threshold": threshold,
                }
            )
    for correlation in CORRELATION_THRESHOLDS:
        for difference in RANK_DIFFERENCE_THRESHOLDS:
            for operator in ("ge", "le"):
                rules.append(
                    {
                        "name": (
                            f"entropy_if_corr_{operator}_{correlation}_and_"
                            f"mad_ge_{difference}"
                        ),
                        "kind": "joint",
                        "correlation_operator": operator,
                        "correlation_threshold": correlation,
                        "rank_difference_threshold": difference,
                    }
                )
    names = [str(rule["name"]) for rule in rules]
    if len(names) != len(set(names)):
        raise AssertionError("adaptive fusion rule names must be unique")
    return rules


def _compare(value: float, operator: object, threshold: object) -> bool:
    return value >= float(threshold) if operator == "ge" else value <= float(threshold)


def selected_parent(rule: dict[str, object], diagnostics: dict[str, object]) -> str:
    correlation = float(diagnostics["rank_correlation"])
    difference = float(diagnostics["mean_absolute_rank_difference"])
    if not math.isfinite(correlation) or not math.isfinite(difference):
        raise ValueError("validation diagnostics must be finite")
    kind = rule["kind"]
    if kind == "always_rank_union":
        choose_entropy = False
    elif kind == "always_entropy":
        choose_entropy = True
    elif kind == "correlation":
        choose_entropy = _compare(correlation, rule["operator"], rule["threshold"])
    elif kind == "rank_difference":
        choose_entropy = _compare(difference, rule["operator"], rule["threshold"])
    elif kind == "joint":
        choose_entropy = _compare(
            correlation,
            rule["correlation_operator"],
            rule["correlation_threshold"],
        ) and difference >= float(rule["rank_difference_threshold"])
    else:
        raise ValueError(f"unsupported adaptive rule kind: {kind!r}")
    return "entropy" if choose_entropy else "rank_union"


def build_blocks(
    runs: list[dict[str, object]], rules: list[dict[str, object]]
) -> dict[str, dict[str, dict[str, float]]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for run in runs:
        scenario = str(run.get("scenario", ""))
        diagnostics = run.get("validation_diagnostics")
        reports = run.get("reports")
        if not scenario or not isinstance(diagnostics, dict) or not isinstance(reports, dict):
            raise ValueError("screening run lacks scenario, diagnostics, or reports")
        if any(parent not in reports for parent in PARENTS):
            raise ValueError(f"screening run {scenario!r} lacks fusion parent reports")
        grouped[scenario].append(run)
    return {
        scenario: {
            str(rule["name"]): {
                metric: float(
                    np.mean(
                        [
                            run["reports"][
                                selected_parent(rule, run["validation_diagnostics"])
                            ][metric]
                            for run in items
                        ]
                    )
                )
                for metric in METRICS
            }
            for rule in rules
        }
        for scenario, items in sorted(grouped.items())
    }


def loso_mean_deltas(screening: dict[str, object]) -> dict[str, float]:
    folds = screening["loso"]["folds"]
    return {
        metric: float(
            np.mean(
                [fold["oriented_deltas_vs_final"][metric] for fold in folds]
            )
        )
        for metric in UNKNOWN_METRICS
    }


def build_report(
    source: dict[str, object], source_sha256: str, expected_runs: int, expected_scenarios: int
) -> dict[str, object]:
    if source.get("schema_version") != "entropy_cauchy_fusion_screen_v1":
        raise ValueError("unexpected entropy-Cauchy screening schema")
    runs = source.get("runs")
    if not isinstance(runs, list) or len(runs) != expected_runs:
        raise ValueError(f"expected {expected_runs} development runs")
    rules = build_rules()
    blocks = build_blocks(runs, rules)
    if len(blocks) != expected_scenarios:
        raise ValueError(f"expected {expected_scenarios} development scenarios")
    adaptive_screen = screen(blocks, "always_entropy", 0.01)
    deltas = loso_mean_deltas(adaptive_screen)
    selected = str(adaptive_screen["selected_candidate"])
    loso_nonregression = all(value >= -1e-12 for value in deltas.values())
    freeze = selected not in {"always_entropy", "always_rank_union"} and loso_nonregression
    return {
        "schema_version": "validation_adaptive_fusion_gate_v1",
        "status": "freeze_candidate" if freeze else "rejected_development_candidate",
        "selected_development_rule": selected,
        "freeze_candidate": freeze,
        "decision_reason": (
            "selected_rule_passed_all_loso_nonregression_gates"
            if freeze
            else "loso_nonregression_failed_or_no_adaptive_rule_selected"
        ),
        "validation": {
            "run_count": len(runs),
            "scenario_count": len(blocks),
            "candidate_rule_count": len(rules),
            "runtime_rule_inputs": [
                "known_validation_entropy_cauchy_rank_correlation",
                "known_validation_mean_absolute_rank_difference",
            ],
            "runtime_uses_unknown_or_test_labels": False,
            "development_screening_uses_test_unknown_labels": True,
            "source_sha256": source_sha256,
        },
        "loso_oriented_mean_deltas_vs_entropy": deltas,
        "screening": adaptive_screen,
        "rules": rules,
    }


def markdown(report: dict[str, object]) -> str:
    selected = report["selected_development_rule"]
    table = {
        row["method"]: row for row in report["screening"]["method_table"]
    }
    row = table[selected]
    deltas = report["loso_oriented_mean_deltas_vs_entropy"]
    lines = [
        "# Validation-adaptive entropy/Cauchy fusion gate",
        "",
        f"Development-selected rule: `{selected}`.",
        f"Decision: `{report['status']}`; freeze candidate: `{report['freeze_candidate']}`.",
        "",
        "| Evidence | AUROC | AUPR | FPR95 | OSCR |",
        "|---|---:|---:|---:|---:|",
        (
            f"| Development mean | {row['unknown_auroc']:.6f} | "
            f"{row['unknown_aupr']:.6f} | {row['unknown_fpr95']:.6f} | "
            f"{row['oscr']:.6f} |"
        ),
        (
            f"| LOSO oriented delta vs entropy | {deltas['unknown_auroc']:+.6f} | "
            f"{deltas['unknown_aupr']:+.6f} | {deltas['unknown_fpr95']:+.6f} | "
            f"{deltas['oscr']:+.6f} |"
        ),
        "",
        "The adaptive rule is rejected unless every LOSO oriented metric is non-negative.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Screen validation-only adaptive entropy/Cauchy fusion gates"
    )
    parser.add_argument("--screening", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--expected-runs", type=int, default=70)
    parser.add_argument("--expected-scenarios", type=int, default=14)
    args = parser.parse_args()
    source_path = Path(args.screening)
    source_bytes = source_path.read_bytes()
    source = json.loads(source_bytes.decode("utf-8"))
    report = build_report(
        source,
        hashlib.sha256(source_bytes).hexdigest(),
        args.expected_runs,
        args.expected_scenarios,
    )
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "analysis.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "analysis.md").write_text(markdown(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "selected_development_rule": report["selected_development_rule"],
                "loso_oriented_mean_deltas_vs_entropy": report[
                    "loso_oriented_mean_deltas_vs_entropy"
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
