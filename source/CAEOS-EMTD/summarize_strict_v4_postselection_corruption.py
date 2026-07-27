from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_postselection_corruption import build_tasks, file_hash, task_key


METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
    "ece",
)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON object required: {path}")
    return payload


def risk_ece(scores_path: Path, selected_risk: str, bins: int = 10) -> float:
    with np.load(scores_path, allow_pickle=False) as archive:
        risk_name = f"test_{selected_risk}"
        if risk_name not in archive or "test_unknown" not in archive:
            raise ValueError(f"risk ECE inputs are missing: {scores_path}")
        risk = np.clip(np.asarray(archive[risk_name], dtype=np.float64), 0.0, 1.0)
        unknown = np.asarray(archive["test_unknown"], dtype=np.float64)
    if risk.ndim != 1 or unknown.shape != risk.shape or risk.size == 0:
        raise ValueError(f"risk ECE inputs are invalid: {scores_path}")
    edges = np.linspace(0.0, 1.0, bins + 1)
    assignments = np.minimum(np.searchsorted(edges, risk, side="right") - 1, bins - 1)
    assignments = np.maximum(assignments, 0)
    total = float(risk.size)
    result = 0.0
    for index in range(bins):
        mask = assignments == index
        if np.any(mask):
            result += float(mask.sum() / total) * abs(
                float(risk[mask].mean()) - float(unknown[mask].mean())
            )
    return result


def extract_metrics(metrics_path: Path) -> dict[str, float]:
    payload = load_json(metrics_path)
    report = payload.get("selected_report")
    selected_risk = payload.get("selected_risk")
    if not isinstance(report, dict) or not isinstance(selected_risk, str):
        raise ValueError(f"selected risk report is missing: {metrics_path}")
    result = {metric: float(report[metric]) for metric in METRICS if metric != "ece"}
    result["ece"] = risk_ece(metrics_path.with_name("scores.npz"), selected_risk)
    if not all(np.isfinite(value) for value in result.values()):
        raise ValueError(f"nonfinite metric under {metrics_path}")
    return result


def degradation(clean: dict[str, float], corrupted: dict[str, float], metric: str) -> float:
    return (
        corrupted[metric] - clean[metric]
        if metric in ("unknown_fpr95", "ece")
        else clean[metric] - corrupted[metric]
    )


def mean_ci(values: Iterable[float], seed: int, repetitions: int) -> dict[str, Any]:
    array = np.asarray(list(values), dtype=np.float64)
    if array.ndim != 1 or array.size == 0 or not np.all(np.isfinite(array)):
        raise ValueError("bootstrap values must be finite and nonempty")
    rng = np.random.default_rng(seed)
    samples = np.mean(
        array[rng.integers(0, array.size, size=(repetitions, array.size))], axis=1
    )
    return {
        "n_scenarios": int(array.size),
        "mean_degradation": float(array.mean()),
        "bootstrap_95ci": [
            float(np.quantile(samples, 0.025)),
            float(np.quantile(samples, 0.975)),
        ],
    }


def render(summary: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 post-selection corruption confirmation",
        "",
        f"Validation: **{'PASS' if summary['validation']['passes'] else 'FAIL'}**; "
        f"graceful-degradation gate: **{'PASS' if summary['confirmatory_gate']['passes'] else 'FAIL'}**.",
        "Risk ECE is the 10-bin calibration error between frozen unknown-risk scores and the test unknown indicator; it is evaluation-only.",
        "",
        "| Family | Known F1 drop | AUROC drop | AUPR drop | FPR95 increase | OSCR drop | Risk ECE increase | Gate |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for family, record in summary["full102_confirmation"].items():
        metrics = record["metrics"]
        lines.append(
            f"| {family} | {metrics['known_macro_f1']['mean_degradation']:+.6f} | "
            f"{metrics['unknown_auroc']['mean_degradation']:+.6f} | "
            f"{metrics['unknown_aupr']['mean_degradation']:+.6f} | "
            f"{metrics['unknown_fpr95']['mean_degradation']:+.6f} | "
            f"{metrics['oscr']['mean_degradation']:+.6f} | "
            f"{metrics['ece']['mean_degradation']:+.6f} | "
            f"{'PASS' if record['passes'] else 'FAIL'} |"
        )
    lines.extend(
        [
            "",
            "Sentinel severity/modality results are descriptive only and are not pooled with the 102-scenario confirmation.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol, coverage = load_json(args.protocol), load_json(args.coverage)
    tasks = build_tasks(protocol, coverage)
    if len(tasks) != 783:
        raise ValueError("expected 783 frozen corruption tasks")
    repetitions = int(protocol["statistical_analysis"]["bootstrap_repetitions"])
    base_seed = int(protocol["statistical_analysis"]["bootstrap_seed"])
    full: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: {metric: [] for metric in METRICS}
    )
    suite_values: dict[str, dict[str, dict[str, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: {metric: [] for metric in METRICS})
    )
    sentinel: dict[str, dict[str, dict[str, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: {metric: [] for metric in METRICS})
    )
    for task in tasks:
        wrapper_path = args.run_root / task_key(task) / "corruption_metrics.json"
        wrapper = load_json(wrapper_path)
        if (
            wrapper.get("schema_version") != "strict_v4_postselection_corruption_run_v1"
            or wrapper.get("record_sha256") != canonical_hash(wrapper)
            or wrapper.get("validation_passes") is not True
            or wrapper.get("unknown_or_test_labels_used_for_generation_fitting_or_selection")
            is not False
            or wrapper.get("task") != task.__dict__
        ):
            raise ValueError(f"corruption wrapper validation failed: {wrapper_path}")
        metrics_path = Path(wrapper["metrics_path"])
        clean_path = Path(protocol["clean_anchor"]["root"]) / task.suite / f"{task.scenario}_seed7" / "metrics.json"
        if not clean_path.is_absolute():
            clean_path = args.run_root.parent.parent / clean_path
        if file_hash(metrics_path) != wrapper["metrics_sha256"] or file_hash(clean_path) != wrapper["clean_metrics_sha256"]:
            raise ValueError(f"metric file SHA mismatch: {wrapper_path}")
        corrupted, clean = extract_metrics(metrics_path), extract_metrics(clean_path)
        observed = {metric: degradation(clean, corrupted, metric) for metric in METRICS}
        if task.tier == "full102":
            for metric, value in observed.items():
                full[task.corruption][metric].append(value)
                suite_values[task.corruption][task.suite][metric].append(value)
        else:
            key = f"severity={task.severity:.12g};modality={task.modality}"
            for metric, value in observed.items():
                sentinel[task.corruption][key][metric].append(value)
    thresholds = protocol["confirmatory_graceful_degradation_gate"][
        "maximum_mean_degradation"
    ]
    confirmation: dict[str, Any] = {}
    family_passes = []
    for family_index, family in enumerate(protocol["full102_confirmation"]["corruption_families"]):
        metric_summaries = {
            metric: mean_ci(full[family][metric], base_seed + family_index * 100 + index, repetitions)
            for index, metric in enumerate(METRICS)
        }
        metric_gates = {
            metric: metric_summaries[metric]["n_scenarios"] == 102
            and metric_summaries[metric]["mean_degradation"] <= float(limit)
            for metric, limit in thresholds.items()
        }
        passes = all(metric_gates.values())
        family_passes.append(passes)
        confirmation[family] = {
            "severity": protocol["full102_confirmation"]["fixed_severity"][family],
            "metrics": metric_summaries,
            "by_suite_mean_degradation": {
                suite: {
                    metric: float(np.mean(values))
                    for metric, values in metrics.items()
                }
                for suite, metrics in suite_values[family].items()
            },
            "threshold_gates": metric_gates,
            "passes": passes,
        }
    sentinel_summary = {
        family: {
            condition: {
                metric: {
                    "n_sentinels": len(values),
                    "mean_degradation": float(np.mean(values)),
                }
                for metric, values in metrics.items()
            }
            for condition, metrics in conditions.items()
        }
        for family, conditions in sentinel.items()
    }
    summary = {
        "schema_version": "strict_v4_postselection_corruption_summary_v1",
        "status": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "analysis_implementation_sha256": file_hash(Path(__file__)),
        "validation": {
            "expected_runs": 783,
            "observed_runs": len(tasks),
            "sentinel_runs": sum(task.tier == "sentinel" for task in tasks),
            "full102_runs": sum(task.tier == "full102" for task in tasks),
            "all_wrapper_hashes_and_split_gates_pass": True,
            "passes": True,
        },
        "risk_ece_definition": {
            "bins": 10,
            "target": "test_unknown_indicator",
            "score": "frozen_selected_unknown_risk",
            "used_for_fitting_or_selection": False,
        },
        "sentinel_descriptive": sentinel_summary,
        "full102_confirmation": confirmation,
        "confirmatory_gate": {
            "all_families_all_frozen_metrics_pass": all(family_passes),
            "passes": all(family_passes),
        },
        "claim_policy": {
            "sentinel_not_pooled_with_confirmation": True,
            "negative_result_reported_if_gate_fails": True,
            "no_robustness_superlative_without_gate": True,
        },
    }
    summary["manifest_sha256"] = canonical_hash(summary)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "summary.md").write_text(render(summary), encoding="utf-8")
    (args.output_dir / "summary_complete").touch()
    print(render(summary), end="")


if __name__ == "__main__":
    main()
