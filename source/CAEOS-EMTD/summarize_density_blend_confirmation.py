from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

from analyze_density_blend import load_trigger, task_seed
from caeos.hybrid_open_set import evaluate_hybrid_open_set


METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize density-reliability blend against its stable parent"
    )
    parser.add_argument("--root", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--seeds",
        required=True,
        help="Comma-separated confirmation seeds, disjoint from development",
    )
    parser.add_argument(
        "--selection-manifest",
        required=True,
        help="Development analysis JSON containing a frozen selection_manifest",
    )
    return parser.parse_args()


def paired(values: list[float]) -> dict[str, object]:
    array = np.asarray(values, dtype=np.float64)
    nonzero = array[np.abs(array) > 1e-12]
    return {
        "mean_delta": float(array.mean()),
        "wins": int((array > 1e-12).sum()),
        "ties": int((np.abs(array) <= 1e-12).sum()),
        "losses": int((array < -1e-12).sum()),
        "wilcoxon_p_value": (
            float(wilcoxon(nonzero).pvalue) if len(nonzero) else 1.0
        ),
    }


def holm_adjust(p_values: dict[str, float]) -> dict[str, float]:
    """Return Holm family-wise adjusted p-values without extra dependencies."""
    ordered = sorted(p_values, key=p_values.get)
    adjusted: dict[str, float] = {}
    running_max = 0.0
    hypotheses = len(ordered)
    for rank, name in enumerate(ordered):
        candidate = min(1.0, (hypotheses - rank) * p_values[name])
        running_max = max(running_max, candidate)
        adjusted[name] = running_max
    return adjusted


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_selection_manifest(
    manifest: dict[str, object], runs: list[dict[str, object]]
) -> dict[str, object]:
    if manifest.get("purpose") != "development_only_hyperparameter_selection":
        raise ValueError("selection manifest is not a frozen development selection")
    if manifest.get("eligible_for_confirmation_or_final_metrics") is not False:
        raise ValueError("selection manifest must mark development metrics as ineligible")
    selected_weight = float(manifest["selected_weight"])
    development_tasks = {str(value) for value in manifest["development_tasks"]}
    confirmation_tasks = {str(run["task_id"]) for run in runs}
    overlap = sorted(development_tasks & confirmation_tasks)
    if overlap:
        raise ValueError(f"development/confirmation task overlap: {overlap}")
    observed_weights = {
        float(run["blend_weight"])
        for run in runs
        if run["triggered"] and run.get("blend_weight") is not None
    }
    if observed_weights and observed_weights != {selected_weight}:
        raise ValueError(
            f"confirmation blend weights {sorted(observed_weights)} do not match "
            f"frozen development weight {selected_weight}"
        )
    development_hashes = {
        value
        for artifacts in manifest.get("development_artifacts", {}).values()
        for value in artifacts.values()
    }
    confirmation_hashes = {
        value
        for run in runs
        for value in run.get("artifact_sha256", {}).values()
    }
    hash_overlap = sorted(development_hashes & confirmation_hashes)
    if hash_overlap:
        raise ValueError(f"development/confirmation artifact overlap: {hash_overlap}")
    return {
        "selected_weight": selected_weight,
        "development_task_count": len(development_tasks),
        "confirmation_task_count": len(confirmation_tasks),
        "task_overlap": [],
        "artifact_hash_overlap": [],
        "validated_disjoint": True,
    }


def metric_summary(runs: list[dict[str, object]], metric: str) -> dict[str, object]:
    direction = -1.0 if metric == "unknown_fpr95" else 1.0
    parent = [float(run["parent_report"][metric]) for run in runs]
    selected = [float(run["selected_report"][metric]) for run in runs]
    oriented_delta = [
        direction * (selected_value - parent_value)
        for selected_value, parent_value in zip(selected, parent)
    ]
    return {
        "parent_mean": float(np.mean(parent)),
        "selected_mean": float(np.mean(selected)),
        "oriented": paired(oriented_delta),
    }


def summarize(runs: list[dict[str, object]]) -> dict[str, object]:
    summary = {"runs": len(runs), "triggers": sum(run["triggered"] for run in runs)}
    for metric in METRICS:
        summary[metric] = metric_summary(runs, metric)
    return summary


def summarize_scenario_blocks(runs: list[dict[str, object]]) -> dict[str, object]:
    """Use scenarios, not correlated seed repeats, as inference units."""
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for run in runs:
        grouped[str(run["scenario"])].append(run)
    summary: dict[str, object] = {
        "inference_unit": "scenario",
        "scenarios": len(grouped),
        "seed_repeats_are_averaged_within_scenario": True,
        "primary_metric": "unknown_auroc",
    }
    raw_p_values: dict[str, float] = {}
    for metric in METRICS:
        direction = -1.0 if metric == "unknown_fpr95" else 1.0
        parent_means = []
        selected_means = []
        scenario_deltas = []
        for items in grouped.values():
            parent = float(np.mean([run["parent_report"][metric] for run in items]))
            selected = float(np.mean([run["selected_report"][metric] for run in items]))
            parent_means.append(parent)
            selected_means.append(selected)
            scenario_deltas.append(direction * (selected - parent))
        inference = paired(scenario_deltas)
        raw_p_values[metric] = float(inference["wilcoxon_p_value"])
        summary[metric] = {
            "parent_scenario_mean": float(np.mean(parent_means)),
            "selected_scenario_mean": float(np.mean(selected_means)),
            "oriented": inference,
        }
    adjusted = holm_adjust(raw_p_values)
    for metric in METRICS:
        summary[metric]["oriented"]["holm_adjusted_p_value"] = adjusted[metric]
    return summary


def main() -> None:
    args = parse_arguments()
    root = Path(args.root)
    selection_path = Path(args.selection_manifest)
    selection_payload = json.loads(selection_path.read_text(encoding="utf-8"))
    selection_manifest = selection_payload.get("selection_manifest", selection_payload)
    selected_weight = float(selection_manifest["selected_weight"])
    supported_suites = {str(value) for value in selection_manifest["supported_suites"]}
    if not supported_suites:
        raise ValueError("selection manifest has no supported suites")
    known_acceptance = float(selection_payload.get("known_acceptance", 0.95))
    confirmation_seeds = {
        int(value) for value in args.seeds.split(",") if value.strip()
    }
    if not confirmation_seeds:
        raise ValueError("at least one confirmation seed is required")
    runs = []
    for path in sorted(root.rglob("metrics.json")):
        if task_seed(path) not in confirmation_seeds:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        details = payload.get("risk_selection_details", {})
        parent = details.get("parent_selected_risk")
        if not parent or parent not in payload.get("reports", {}):
            continue
        relative = path.relative_to(root)
        suite = relative.parts[0]
        scenario_name = path.parent.name.rsplit("_seed", 1)[0]
        scenario = f"{suite}/{scenario_name}"
        seed = int(path.parent.name.rsplit("_seed", 1)[1])
        original_selected = payload["selected_risk"]
        if (
            original_selected == "density_reliability_blend"
            and suite in supported_suites
        ):
            trigger = load_trigger(path)
            if trigger is None:
                raise ValueError(f"cannot recover density trigger from {path}")
            validation_risk = (
                (1.0 - selected_weight) * trigger["validation_parent"]
                + selected_weight * trigger["validation_candidate"]
            )
            test_risk = (
                (1.0 - selected_weight) * trigger["test_parent"]
                + selected_weight * trigger["test_candidate"]
            )
            threshold = float(np.quantile(validation_risk, known_acceptance))
            selected_report = evaluate_hybrid_open_set(
                trigger["test_labels"],
                trigger["test_unknown"],
                trigger["test_prediction"],
                test_risk,
                threshold,
            )
            selected = "density_reliability_blend"
            triggered = True
            blend_weight = selected_weight
        elif original_selected in {parent, "density_reliability_blend"}:
            selected = parent
            selected_report = payload["reports"][parent]
            triggered = False
            blend_weight = None
        else:
            raise ValueError(
                f"unexpected density-gate selection in {path}: "
                f"selected={original_selected!r}, parent={parent!r}"
            )
        scores_path = path.parent / "scores.npz"
        evidence_path = path.parent / "evidence_package.npz"
        runs.append(
            {
                "path": str(relative),
                "task_id": path.parent.relative_to(root).as_posix(),
                "scenario": scenario,
                "seed": seed,
                "parent": parent,
                "selected": selected,
                "triggered": triggered,
                "endpoint": details.get("density_support_endpoint"),
                "blend_weight": blend_weight,
                "artifact_sha256": {
                    "metrics.json": sha256(path),
                    **(
                        {"scores.npz": sha256(scores_path)}
                        if scores_path.exists()
                        else {}
                    ),
                    **(
                        {"evidence_package.npz": sha256(evidence_path)}
                        if evidence_path.exists()
                        else {}
                    ),
                },
                "parent_report": payload["reports"][parent],
                "selected_report": selected_report,
            }
        )
    if not runs:
        raise ValueError(f"no confirmation runs found under {root}")
    grouped = defaultdict(list)
    for run in runs:
        grouped[run["scenario"]].append(run)
    selection_validation = validate_selection_manifest(selection_manifest, runs)
    report = {
        "root": str(root),
        "selection_manifest": str(selection_path),
        "supported_suites": sorted(supported_suites),
        "confirmation_seeds": sorted(confirmation_seeds),
        "known_acceptance": known_acceptance,
        "selection_validation": selection_validation,
        "run_level_descriptive": summarize(runs),
        "scenario_blocked_inference": summarize_scenario_blocks(runs),
        "by_scenario": {
            scenario: summarize(items) for scenario, items in sorted(grouped.items())
        },
        "runs": runs,
    }
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    overall = report["run_level_descriptive"]
    blocked = report["scenario_blocked_inference"]
    lines = [
        "# Density reliability blend confirmation",
        "",
        f"Runs: {overall['runs']}; triggers: {overall['triggers']}",
        "",
        "Run-level rows below are descriptive because seeds within a scenario are correlated.",
        "",
        "| Metric | Parent | Blend | Oriented delta | W/T/L |",
        "|---|---:|---:|---:|---:|",
    ]
    for metric in METRICS:
        item = overall[metric]
        oriented = item["oriented"]
        lines.append(
            f"| {metric} | {item['parent_mean']:.6f} | "
            f"{item['selected_mean']:.6f} | {oriented['mean_delta']:+.6f} | "
            f"{oriented['wins']}/{oriented['ties']}/{oriented['losses']} |"
        )
    lines.extend(
        [
            "",
            "## Scenario-blocked inference",
            "",
            f"Inference units: {blocked['scenarios']} scenarios; seed repeats are averaged within each scenario.",
            "Unknown AUROC is the pre-specified primary metric. Holm p-values control the four-metric family.",
            "",
            "| Metric | Parent | Blend | Oriented delta | W/T/L | Wilcoxon p | Holm p |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for metric in METRICS:
        item = blocked[metric]
        oriented = item["oriented"]
        lines.append(
            f"| {metric} | {item['parent_scenario_mean']:.6f} | "
            f"{item['selected_scenario_mean']:.6f} | {oriented['mean_delta']:+.6f} | "
            f"{oriented['wins']}/{oriented['ties']}/{oriented['losses']} | "
            f"{oriented['wilcoxon_p_value']:.3g} | "
            f"{oriented['holm_adjusted_p_value']:.3g} |"
        )
    (output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(blocked, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
