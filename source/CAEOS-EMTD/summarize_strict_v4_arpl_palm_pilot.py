from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import summarize_strict_v4_pilot as base
from summarize_hcrp_osd_strict_v4_pilot import load_hcrp_blocks


MODEL_METHODS = {"arpl": "arpl", "palm": "palm_ssd_plus"}


def parse_task(directory: Path, seed: int) -> tuple[str, str, str]:
    for model in MODEL_METHODS:
        marker = f"_seed{seed}_{model}"
        if directory.name.endswith(marker):
            return directory.parent.name, directory.name[: -len(marker)], model
    raise ValueError(f"unexpected ARPL/PALM directory: {directory}")


def load_extension_blocks(
    root: Path, caeos_root: Path, seed: int
) -> tuple[dict[str, dict[str, dict[str, float]]], dict[str, Any]]:
    expected = {
        (suite, scenario, model)
        for suite, scenarios in base.EXPECTED_SCENARIOS.items()
        for scenario in scenarios
        for model in MODEL_METHODS
    }
    found = set()
    blocks: dict[str, dict[str, dict[str, float]]] = {}
    artifact_checks = 0
    fingerprint_checks = 0
    for path in sorted(root.glob("*/*/metrics.json")):
        suite, scenario, model = parse_task(path.parent, seed)
        task = (suite, scenario, model)
        if task not in expected or task in found:
            raise ValueError(f"invalid or duplicate ARPL/PALM task: {task}")
        found.add(task)
        artifact_checks += base.check_artifacts(path.parent, base.NEURAL_ARTIFACTS)
        metrics = base.load_json(path)
        method = MODEL_METHODS[model]
        if (
            int(metrics.get("seed", -1)) != seed
            or metrics.get("model") != model
            or metrics.get("method") != method
        ):
            raise ValueError(f"ARPL/PALM identity mismatch for {task}")
        key = f"{suite}/{scenario}"
        caeos_path = caeos_root / suite / f"{scenario}_seed{seed}" / "metrics.json"
        caeos = base.load_json(caeos_path)
        if base.split_fingerprint(metrics, f"{key}/{method}") != base.split_fingerprint(
            caeos, f"{key}/caeos"
        ):
            raise ValueError(f"split fingerprint mismatch for {task}")
        fingerprint_checks += 1
        blocks.setdefault(key, {})[method] = base.report_metrics(
            metrics.get("reports", {}).get(method), f"{key}/{method}"
        )
    if found != expected:
        raise ValueError(
            f"ARPL/PALM coverage mismatch: missing={sorted(expected - found)}, "
            f"extra={sorted(found - expected)}"
        )
    return blocks, {
        "passes": True,
        "tasks": len(found),
        "artifact_checks": artifact_checks,
        "split_fingerprint_checks": fingerprint_checks,
        "methods": sorted(MODEL_METHODS.values()),
    }


def oriented_delta(candidate: dict[str, Any], reference: dict[str, Any]) -> dict[str, float]:
    return {
        metric: float(
            reference[metric] - candidate[metric]
            if metric == "unknown_fpr95"
            else candidate[metric] - reference[metric]
        )
        for metric in base.METRICS
    }


def task_diagnostics(
    blocks: dict[str, dict[str, dict[str, float]]], caeos_root: Path, seed: int
) -> list[dict[str, Any]]:
    rows = []
    for key, methods in blocks.items():
        suite, scenario = key.split("/", 1)
        caeos = methods["caeos"]
        baselines = {name: report for name, report in methods.items() if name != "caeos"}
        metric_gaps = {}
        strongest = {}
        for metric in base.METRICS[1:]:
            if metric == "unknown_fpr95":
                method = min(baselines, key=lambda name: baselines[name][metric])
                gap = baselines[method][metric] - caeos[metric]
            else:
                method = max(baselines, key=lambda name: baselines[name][metric])
                gap = caeos[metric] - baselines[method][metric]
            strongest[metric] = method
            metric_gaps[metric] = float(gap)
        payload = base.load_json(
            caeos_root / suite / f"{scenario}_seed{seed}" / "metrics.json"
        )
        learned = payload.get("risk_selection_details", {}).get(
            "pseudo_unknown_learned_blend", {}
        )
        rows.append(
            {
                "task": key,
                "selected_risk": payload.get("selected_risk"),
                "minimum_fold_metric_gain": learned.get("selected_summary", {}).get(
                    "minimum_fold_metric_gain"
                ),
                "oriented_gap_vs_strongest_baseline": metric_gaps,
                "strongest_baseline": strongest,
            }
        )
    return sorted(
        rows,
        key=lambda row: row["oriented_gap_vs_strongest_baseline"]["unknown_auroc"],
    )


def render(report: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 ARPL/PALM baseline expansion",
        "",
        f"Validation: **PASS**; scenarios: {report['scenario_count']}; "
        f"methods: {report['method_count']}.",
        "This is a same-split single-seed pilot, not confirmatory inference.",
        "",
        "| Rank | Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, row in enumerate(report["overall"], start=1):
        lines.append(
            f"| {rank} | {row['method']} | {row['known_macro_f1']:.6f} | "
            f"{row['unknown_auroc']:.6f} | {row['unknown_aupr']:.6f} | "
            f"{row['unknown_fpr95']:.6f} | {row['oscr']:.6f} | "
            f"{row['mean_unknown_metric_rank']:.3f} |"
        )
    lines.extend(["", "## Added baseline decisions", ""])
    for method, decision in report["added_baseline_decisions"].items():
        lines.append(
            f"- `{method}`: `{decision['state']}`; unknown wins versus CAEOS "
            f"{decision['unknown_metric_wins_vs_caeos']}/4; deltas "
            f"`{decision['oriented_delta_vs_caeos']}`."
        )
    lines.extend(["", "## Task-level CAEOS gaps", ""])
    for row in report["task_diagnostics"]:
        gaps = row["oriented_gap_vs_strongest_baseline"]
        lines.append(
            f"- `{row['task']}` endpoint `{row['selected_risk']}`: "
            f"AUROC {gaps['unknown_auroc']:+.6f}, "
            f"AUPR {gaps['unknown_aupr']:+.6f}, "
            f"FPR95 {gaps['unknown_fpr95']:+.6f}, "
            f"OSCR {gaps['oscr']:+.6f}."
        )
    budget = report["budget_decision"]
    lines.extend(
        [
            "",
            "## CAEOS budget decision",
            "",
            f"State: **{budget['state']}**.",
            f"Gates: `{budget['gates']}`.",
            f"Worst task AUROC delta: `{budget['worst_task_auroc_oriented_delta']:+.6f}`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--caeos-root", type=Path, required=True)
    parser.add_argument("--neural-root", type=Path, required=True)
    parser.add_argument("--hcrp-root", type=Path, required=True)
    parser.add_argument("--extension-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    base.EXPECTED_POLICY = "strict_v4_pairwise_pilot_v1"
    base.EXPECTED_RISK = {
        "cauchy_modality_support_union",
        "pseudo_unknown_learned_blend",
    }
    blocks, base_validation = base.load_pilot(
        args.caeos_root, args.neural_root, args.seed
    )
    hcrp_blocks, hcrp_validation = load_hcrp_blocks(
        args.hcrp_root, args.caeos_root, args.seed
    )
    extension_blocks, extension_validation = load_extension_blocks(
        args.extension_root, args.caeos_root, args.seed
    )
    for key in blocks:
        blocks[key].update(hcrp_blocks[key])
        blocks[key].update(extension_blocks[key])
    method_count = len(next(iter(blocks.values())))
    if method_count != 18 or any(len(methods) != method_count for methods in blocks.values()):
        raise ValueError("strict-v4 expanded pilot must contain 18 methods per scenario")

    overall = base.aggregate_table(blocks)
    by_suite = {
        suite: base.aggregate_table(
            {key: methods for key, methods in blocks.items() if key.startswith(f"{suite}/")}
        )
        for suite in sorted(base.EXPECTED_SCENARIOS)
    }
    caeos = next(row for row in overall if row["method"] == "caeos")
    decisions = {}
    for method in MODEL_METHODS.values():
        row = next(item for item in overall if item["method"] == method)
        delta = oriented_delta(row, caeos)
        wins = sum(delta[metric] > 0.0 for metric in base.METRICS[1:])
        decisions[method] = {
            "state": "expand_multiseed" if wins >= 2 else "hold_at_pilot",
            "unknown_metric_wins_vs_caeos": wins,
            "oriented_delta_vs_caeos": delta,
        }
    report = {
        "schema_version": "strict_v4_arpl_palm_expanded_pilot_v1",
        "status": "complete",
        "scenario_count": len(blocks),
        "method_count": method_count,
        "validation": {
            "base": base_validation,
            "hcrp": hcrp_validation,
            "extension": extension_validation,
        },
        "protocol_classification": {
            "arpl": "same-split tabular adapter",
            "palm_ssd_plus": "same-split tabular-view adapter",
            "author_code_reproduction": False,
        },
        "overall": overall,
        "by_suite": by_suite,
        "added_baseline_decisions": decisions,
        "task_diagnostics": task_diagnostics(blocks, args.caeos_root, args.seed),
        "budget_decision": base.build_budget_decision(blocks, overall),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "summary.md").write_text(render(report), encoding="utf-8")
    print(render(report))


if __name__ == "__main__":
    main()
