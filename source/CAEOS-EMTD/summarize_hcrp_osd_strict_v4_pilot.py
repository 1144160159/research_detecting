from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from summarize_strict_v4_pilot import (
    EXPECTED_SCENARIOS,
    METRICS,
    aggregate_table,
    load_json,
    report_metrics,
    split_fingerprint,
)


METHOD = "hcrp_osd_adapter"
MODEL = "hcrp_osd"
REQUIRED_ARTIFACTS = ("metrics.json", "scores.npz", "provenance.json")


def expected_tasks() -> set[tuple[str, str]]:
    return {
        (suite, scenario)
        for suite, scenarios in EXPECTED_SCENARIOS.items()
        for scenario in scenarios
    }


def parse_task(path: Path, seed: int) -> tuple[str, str]:
    marker = f"_seed{seed}_{MODEL}"
    if not path.parent.name.endswith(marker):
        raise ValueError(f"unexpected HCRP-OSD directory: {path.parent}")
    return path.parent.parent.name, path.parent.name[: -len(marker)]


def load_hcrp_blocks(
    hcrp_root: Path,
    caeos_root: Path,
    seed: int,
) -> tuple[dict[str, dict[str, dict[str, float]]], dict[str, Any]]:
    tasks = expected_tasks()
    found: set[tuple[str, str]] = set()
    blocks: dict[str, dict[str, dict[str, float]]] = {}
    artifact_checks = 0
    fingerprint_checks = 0
    for path in sorted(hcrp_root.glob("*/*/metrics.json")):
        task = parse_task(path, seed)
        if task not in tasks:
            continue
        if task in found:
            raise ValueError(f"duplicate HCRP-OSD task: {task}")
        found.add(task)
        missing = [name for name in REQUIRED_ARTIFACTS if not (path.parent / name).is_file()]
        if missing:
            raise ValueError(f"missing HCRP-OSD artifacts for {task}: {missing}")
        artifact_checks += len(REQUIRED_ARTIFACTS)
        metrics = load_json(path)
        if metrics.get("model") != MODEL or metrics.get("method") != METHOD:
            raise ValueError(f"HCRP-OSD identity mismatch for {task}")
        if int(metrics.get("seed", -1)) != seed:
            raise ValueError(f"HCRP-OSD seed mismatch for {task}")
        report = report_metrics(metrics.get("reports", {}).get(METHOD), f"{task}/{METHOD}")

        suite, scenario = task
        caeos_path = caeos_root / suite / f"{scenario}_seed{seed}" / "metrics.json"
        caeos = load_json(caeos_path)
        if split_fingerprint(metrics, f"{task}/{METHOD}") != split_fingerprint(
            caeos, f"{task}/caeos"
        ):
            raise ValueError(f"split fingerprint mismatch for {task}")
        fingerprint_checks += 1
        blocks[f"{suite}/{scenario}"] = {METHOD: report}
    if found != tasks:
        raise ValueError(
            f"HCRP-OSD coverage mismatch: missing={sorted(tasks - found)}, "
            f"extra={sorted(found - tasks)}"
        )
    return blocks, {
        "passes": True,
        "tasks": len(found),
        "artifact_checks": artifact_checks,
        "split_fingerprint_checks": fingerprint_checks,
        "paper_structure_adapter": True,
        "author_code_reproduction": False,
    }


def extend_table(
    existing: list[dict[str, Any]],
    hcrp_report: dict[str, float],
) -> list[dict[str, Any]]:
    blocks = {
        "aggregate": {
            **{
                str(row["method"]): {
                    metric: float(row[metric]) for metric in METRICS
                }
                for row in existing
            },
            METHOD: hcrp_report,
        }
    }
    return aggregate_table(blocks)


def mean_report(blocks: dict[str, dict[str, dict[str, float]]]) -> dict[str, float]:
    return {
        metric: float(
            np.mean([methods[METHOD][metric] for methods in blocks.values()])
        )
        for metric in METRICS
    }


def build_summary(
    existing_summary: dict[str, Any],
    hcrp_blocks: dict[str, dict[str, dict[str, float]]],
    validation: dict[str, Any],
) -> dict[str, Any]:
    hcrp_overall = mean_report(hcrp_blocks)
    overall = extend_table(existing_summary["overall"], hcrp_overall)
    by_suite: dict[str, list[dict[str, Any]]] = {}
    for suite in sorted(EXPECTED_SCENARIOS):
        suite_blocks = {
            key: value for key, value in hcrp_blocks.items() if key.startswith(f"{suite}/")
        }
        by_suite[suite] = extend_table(
            existing_summary["by_suite"][suite], mean_report(suite_blocks)
        )
    caeos = next(row for row in overall if row["method"] == "caeos")
    hcrp = next(row for row in overall if row["method"] == METHOD)
    oriented = {
        metric: (
            caeos[metric] - hcrp[metric]
            if metric == "unknown_fpr95"
            else hcrp[metric] - caeos[metric]
        )
        for metric in METRICS
    }
    unknown_wins = sum(oriented[metric] > 0 for metric in METRICS[1:])
    return {
        "schema_version": "strict_v4_hcrp_osd_pilot_v1",
        "status": "complete",
        "scenario_count": len(hcrp_blocks),
        "validation": validation,
        "protocol_classification": {
            "method": METHOD,
            "paper_structure_adapter": True,
            "author_code_reproduction": False,
            "claim_limit": "same-split pilot baseline only",
        },
        "hcrp_osd": hcrp,
        "caeos": caeos,
        "hcrp_oriented_delta_vs_caeos": oriented,
        "overall": overall,
        "by_suite": by_suite,
        "budget_decision": {
            "state": (
                "expand_hcrp_multiseed" if unknown_wins >= 2 else "hold_hcrp_at_pilot"
            ),
            "unknown_metric_wins_vs_caeos": unknown_wins,
            "reason": (
                "HCRP-OSD beats CAEOS on at least two aggregate unknown metrics."
                if unknown_wins >= 2
                else "HCRP-OSD does not beat CAEOS on enough aggregate unknown metrics."
            ),
        },
    }


def render_markdown(summary: dict[str, Any]) -> str:
    hcrp = summary["hcrp_osd"]
    caeos = summary["caeos"]
    delta = summary["hcrp_oriented_delta_vs_caeos"]
    lines = [
        "# HCRP-OSD strict-v4 pilot",
        "",
        "- Evidence level: same-split six-scenario pilot.",
        "- Implementation: paper-structure adapter; not an author-code reproduction.",
        f"- Decision: `{summary['budget_decision']['state']}`.",
        "",
        "| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean unknown rank |",
        "|---|---:|---:|---:|---:|---:|---:|",
        f"| HCRP-OSD adapter | {hcrp['known_macro_f1']:.6f} | {hcrp['unknown_auroc']:.6f} | {hcrp['unknown_aupr']:.6f} | {hcrp['unknown_fpr95']:.6f} | {hcrp['oscr']:.6f} | {hcrp['mean_unknown_metric_rank']:.3f} |",
        f"| CAEOS | {caeos['known_macro_f1']:.6f} | {caeos['unknown_auroc']:.6f} | {caeos['unknown_aupr']:.6f} | {caeos['unknown_fpr95']:.6f} | {caeos['oscr']:.6f} | {caeos['mean_unknown_metric_rank']:.3f} |",
        "",
        "## Oriented HCRP-OSD delta versus CAEOS",
        "",
    ]
    for metric in METRICS:
        lines.append(f"- `{metric}`: {delta[metric]:+.6f}")
    lines.extend(["", "## Sixteen-method ranking", ""])
    for index, row in enumerate(summary["overall"], start=1):
        lines.append(
            f"{index}. `{row['method']}`: mean unknown rank "
            f"{row['mean_unknown_metric_rank']:.3f}"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hcrp-root", type=Path, required=True)
    parser.add_argument("--caeos-root", type=Path, required=True)
    parser.add_argument("--existing-summary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    blocks, validation = load_hcrp_blocks(args.hcrp_root, args.caeos_root, args.seed)
    summary = build_summary(load_json(args.existing_summary), blocks, validation)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "summary.md").write_text(render_markdown(summary), encoding="utf-8")


if __name__ == "__main__":
    main()
