from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from typing import Any

import numpy as np

from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_paired_confirmation import (
    bootstrap_ci,
    effect_sizes,
    holm_adjust,
    paired_wilcoxon,
    stable_bootstrap_seed,
)


METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")


def oriented_gain(candidate: float, reference: float, metric: str) -> float:
    return reference - candidate if metric == "unknown_fpr95" else candidate - reference


def analyze(protocol: dict[str, Any], run_root: Path) -> dict[str, Any]:
    if protocol.get("schema_version") != "strict_v4_conflict_topology_copula_confirmation_protocol_v1":
        raise ValueError("unexpected CTC confirmation protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("CTC confirmation protocol SHA mismatch")
    rows = []
    for suite, registry in protocol["scenario_registry"].items():
        for scenario in registry["scenarios"]:
            for seed in protocol["seeds"]:
                path = run_root / suite / f"{scenario}_seed{seed}" / "metrics.json"
                if not path.is_file():
                    raise FileNotFoundError(f"missing CTC confirmation result: {path}")
                payload = json.loads(path.read_text(encoding="utf-8"))
                if payload.get("protocol_manifest_sha256") != protocol["manifest_sha256"]:
                    raise ValueError("CTC confirmation result binding mismatch")
                if payload.get("seed") != seed:
                    raise ValueError("CTC confirmation result seed mismatch")
                diagnostics = payload["diagnostics"]
                reference = payload["reports"]["reference"]
                candidate = payload["reports"]["candidate"]
                rows.append(
                    {
                        "suite": suite,
                        "scenario": scenario,
                        "seed": seed,
                        "oriented_gains": {
                            name: oriented_gain(candidate[name], reference[name], name)
                            for name in METRICS
                        },
                        "prediction_array_equal": diagnostics["prediction_array_equal"] is True,
                        "known_macro_f1_absolute_difference": float(
                            diagnostics["known_macro_f1_absolute_difference"]
                        ),
                    }
                )
    if len(rows) != protocol["expected_ctc_runs"]:
        raise ValueError("CTC confirmation result count is incomplete")

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["suite"], row["scenario"])].append(row)
    if len(grouped) != protocol["scenario_count"]:
        raise ValueError("CTC confirmation scenario coverage is incomplete")
    scenario_blocks = []
    for (suite, scenario), items in sorted(grouped.items()):
        if {item["seed"] for item in items} != set(protocol["seeds"]):
            raise ValueError("CTC confirmation seed coverage is incomplete")
        scenario_blocks.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed_count": len(items),
                "oriented_gains": {
                    metric: float(
                        np.mean([item["oriented_gains"][metric] for item in items])
                    )
                    for metric in METRICS
                },
            }
        )

    inference = protocol["confirmation_inference"]
    metric_reports = {}
    raw_p = {}
    for metric in METRICS:
        values = [block["oriented_gains"][metric] for block in scenario_blocks]
        wilcoxon = paired_wilcoxon(values)
        raw_p[metric] = float(wilcoxon["raw_p_value"])
        metric_reports[metric] = {
            "oriented_mean_improvement": float(np.mean(values)),
            "wins": int(np.sum(np.asarray(values) > 1e-12)),
            "ties": int(np.sum(np.abs(values) <= 1e-12)),
            "losses": int(np.sum(np.asarray(values) < -1e-12)),
            "bootstrap_95_ci": bootstrap_ci(
                values,
                int(inference["bootstrap_repetitions"]),
                stable_bootstrap_seed(int(inference["bootstrap_seed"]), metric),
            ),
            "effect_sizes": effect_sizes(values),
            "wilcoxon": wilcoxon,
        }
    adjusted = holm_adjust(raw_p)
    for metric, value in adjusted.items():
        metric_reports[metric]["wilcoxon"]["holm_adjusted_p_value"] = value

    suite_reports = {}
    for suite in sorted(protocol["scenario_registry"]):
        selected = [block for block in scenario_blocks if block["suite"] == suite]
        suite_reports[suite] = {
            metric: float(np.mean([block["oriented_gains"][metric] for block in selected]))
            for metric in METRICS
        }
    tolerance = float(
        inference["gate"]["known_macro_f1_absolute_tolerance"]
    )
    checks = {
        "all_four_oriented_means_strictly_positive": all(
            metric_reports[name]["oriented_mean_improvement"] > 0.0
            for name in METRICS
        ),
        "auroc_and_aupr_bootstrap_lower_strictly_positive": all(
            metric_reports[name]["bootstrap_95_ci"]["lower"] > 0.0
            for name in ("unknown_auroc", "unknown_aupr")
        ),
        "all_four_holm_adjusted_p_below_0_05": all(
            metric_reports[name]["wilcoxon"]["holm_adjusted_p_value"] < 0.05
            for name in METRICS
        ),
        "all_suite_metric_oriented_means_nonnegative": all(
            value >= -1e-12 for suite in suite_reports.values() for value in suite.values()
        ),
        "prediction_array_equal_for_all_306_runs": all(
            row["prediction_array_equal"] for row in rows
        ),
        "known_macro_f1_absolute_tolerance": max(
            row["known_macro_f1_absolute_difference"] for row in rows
        )
        <= tolerance,
    }
    passes = all(checks.values())
    return {
        "schema_version": "strict_v4_conflict_topology_copula_confirmation_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "paired_run_count": len(rows),
        "scenario_count": len(scenario_blocks),
        "seed_count": len(protocol["seeds"]),
        "inference_unit": "scenario_after_within_scenario_seed_average",
        "metrics": metric_reports,
        "by_suite_oriented_gains": suite_reports,
        "scenario_blocks": scenario_blocks,
        "checks": checks,
        "passes": passes,
        "decision": (
            "ctc_accuracy_confirmed_pending_efficiency_and_external_dataset_gates"
            if passes
            else "retain_caeos_pairwise_and_reject_ctc_replacement"
        ),
    }


def render(report: dict[str, Any]) -> str:
    lines = [
        "# CTC reserved-seed confirmation",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Passes: `{report['passes']}`",
        f"- Paired runs: `{report['paired_run_count']}`",
        f"- Scenario inference units: `{report['scenario_count']}`",
        "",
        "| Metric | Oriented mean | 95% CI | W/T/L | Holm p |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in METRICS:
        item = report["metrics"][name]
        ci = item["bootstrap_95_ci"]
        lines.append(
            f"| {name} | {item['oriented_mean_improvement']:+.6f} | "
            f"[{ci['lower']:+.6f}, {ci['upper']:+.6f}] | "
            f"{item['wins']}/{item['ties']}/{item['losses']} | "
            f"{item['wilcoxon']['holm_adjusted_p_value']:.3g} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    report = analyze(protocol, args.run_root)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "confirmation.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "confirmation.md").write_text(render(report), encoding="utf-8")
    (args.output_dir / "confirmation_complete").touch()


if __name__ == "__main__":
    main()
