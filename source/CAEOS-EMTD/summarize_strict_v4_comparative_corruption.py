from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy.stats import wilcoxon

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash


METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
    "ece",
)


def mean_ci(values: Iterable[float], seed: int, repetitions: int) -> dict[str, Any]:
    array = np.asarray(list(values), dtype=np.float64)
    if array.shape != (102,) or not np.all(np.isfinite(array)):
        raise ValueError("comparative corruption inference requires 102 finite scenario values")
    rng = np.random.default_rng(seed)
    samples = np.mean(array[rng.integers(0, 102, size=(repetitions, 102))], axis=1)
    if np.all(np.abs(array) <= 1e-15):
        p_value = 1.0
    else:
        p_value = float(wilcoxon(array, alternative="greater", zero_method="wilcox").pvalue)
    return {
        "n_scenarios": 102,
        "mean_advantage": float(array.mean()),
        "bootstrap_95ci": [
            float(np.quantile(samples, 0.025)),
            float(np.quantile(samples, 0.975)),
        ],
        "wilcoxon_one_sided_p": p_value,
        "wins": int(np.sum(array > 1e-12)),
        "ties": int(np.sum(np.abs(array) <= 1e-12)),
        "losses": int(np.sum(array < -1e-12)),
    }


def holm_adjust(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values, key=lambda name: (p_values[name], name))
    adjusted: dict[str, float] = {}
    running = 0.0
    total = len(ordered)
    for index, name in enumerate(ordered):
        running = max(running, (total - index) * float(p_values[name]))
        adjusted[name] = min(1.0, running)
    return adjusted


def render(summary: dict[str, Any]) -> str:
    lines = [
        "# Strict-v4 comparative post-selection corruption",
        "",
        f"Comparative robustness gate: **{'PASS' if summary['comparative_robustness_gate']['passes'] else 'FAIL'}**.",
        "Positive values mean CAEOS Pairwise degrades less than OpenDetect.",
        "",
        "| Family | Known F1 | AUROC | AUPR | FPR95 | OSCR | ECE | Gate |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for family, record in summary["by_family"].items():
        values = record["metrics"]
        lines.append(
            f"| {family} | {values['known_macro_f1']['mean_advantage']:+.6f} | "
            f"{values['unknown_auroc']['mean_advantage']:+.6f} | "
            f"{values['unknown_aupr']['mean_advantage']:+.6f} | "
            f"{values['unknown_fpr95']['mean_advantage']:+.6f} | "
            f"{values['oscr']['mean_advantage']:+.6f} | "
            f"{values['ece']['mean_advantage']:+.6f} | "
            f"{'PASS' if record['passes'] else 'FAIL'} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    if protocol.get("schema_version") != "strict_v4_comparative_corruption_protocol_v2" or protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("comparative corruption protocol validation failed")
    if protocol["implementation_sha256"]["summarizer"] != file_hash(Path(__file__)):
        raise ValueError("comparative corruption summarizer implementation SHA mismatch")
    if not (args.run_root / "execution_complete").is_file():
        raise ValueError("comparative corruption execution is incomplete")
    values: dict[str, dict[str, dict[str, dict[int, float]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(dict))
    )
    observed_conditions = 0
    for source in protocol["source_registry"]:
        suite, scenario, seed = source["suite"], source["scenario"], int(source["seed"])
        path = args.run_root / "blocks" / suite / scenario / f"seed{seed}" / "paired_corruption.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        if (
            payload.get("schema_version") != "strict_v4_comparative_corruption_block_v1"
            or payload.get("manifest_sha256") != canonical_hash(payload)
            or payload.get("protocol_manifest_sha256") != protocol["manifest_sha256"]
            or payload.get("suite") != suite
            or payload.get("scenario") != scenario
            or int(payload.get("seed", -1)) != seed
            or payload.get("candidate_comparator_input_arrays_equal") is not True
            or payload.get("degradation_uses_same_device_runtime_clean_anchors") is not True
            or payload.get("unknown_or_test_labels_used_for_fitting_selection_or_corruption_generation") is not False
        ):
            raise ValueError(f"comparative corruption block validation failed: {path}")
        conditions = payload.get("conditions", [])
        if len(conditions) != 5 or {item["family"] for item in conditions} != set(protocol["corruption_conditions"]["families"]):
            raise ValueError(f"comparative corruption condition coverage failed: {path}")
        for condition in conditions:
            family = condition["family"]
            advantage = condition["candidate_robustness_advantage"]
            for metric in METRICS:
                value = float(advantage[metric])
                if not np.isfinite(value) or seed in values[family][metric][f"{suite}/{scenario}"]:
                    raise ValueError("comparative corruption advantage is invalid or duplicated")
                values[family][metric][f"{suite}/{scenario}"][seed] = value
            observed_conditions += 1
    if observed_conditions != 1530:
        raise ValueError("comparative corruption condition evaluation count mismatch")
    repetitions = int(protocol["statistical_analysis"]["bootstrap_repetitions"])
    base_seed = int(protocol["statistical_analysis"]["bootstrap_seed"])
    by_family: dict[str, Any] = {}
    family_passes = []
    for family_index, family in enumerate(protocol["corruption_conditions"]["families"]):
        metric_summaries: dict[str, Any] = {}
        scenario_values_by_metric: dict[str, dict[str, float]] = {}
        for metric_index, metric in enumerate(METRICS):
            scenario_values = {}
            for scenario_key, seeds in values[family][metric].items():
                if sorted(seeds) != protocol["seeds"]:
                    raise ValueError(f"comparative corruption seed coverage failed: {family}/{metric}/{scenario_key}")
                scenario_values[scenario_key] = float(np.mean(list(seeds.values())))
            if len(scenario_values) != 102:
                raise ValueError(f"comparative corruption scenario coverage failed: {family}/{metric}")
            scenario_values_by_metric[metric] = scenario_values
            metric_summaries[metric] = mean_ci(
                [scenario_values[key] for key in sorted(scenario_values)],
                base_seed + family_index * 100 + metric_index,
                repetitions,
            )
        adjusted = holm_adjust(
            {metric: metric_summaries[metric]["wilcoxon_one_sided_p"] for metric in METRICS}
        )
        for metric in METRICS:
            metric_summaries[metric]["holm_adjusted_p"] = adjusted[metric]
        suite_means: dict[str, dict[str, float]] = {}
        for suite in sorted({key.split("/", 1)[0] for key in scenario_values_by_metric[METRICS[0]]}):
            suite_means[suite] = {
                metric: float(
                    np.mean(
                        [
                            value
                            for key, value in scenario_values_by_metric[metric].items()
                            if key.startswith(f"{suite}/")
                        ]
                    )
                )
                for metric in METRICS
            }
        checks = {
            "all_six_means_strictly_positive": all(metric_summaries[metric]["mean_advantage"] > 0.0 for metric in METRICS),
            "all_six_bootstrap_lower_bounds_strictly_positive": all(metric_summaries[metric]["bootstrap_95ci"][0] > 0.0 for metric in METRICS),
            "all_six_holm_adjusted_p_below_0_05": all(metric_summaries[metric]["holm_adjusted_p"] < 0.05 for metric in METRICS),
            "all_suite_metric_means_nonnegative": all(value >= -1e-12 for metrics in suite_means.values() for value in metrics.values()),
        }
        passes = all(checks.values())
        family_passes.append(passes)
        by_family[family] = {
            "metrics": metric_summaries,
            "suite_mean_advantages": suite_means,
            "checks": checks,
            "passes": passes,
        }
    summary = {
        "schema_version": "strict_v4_comparative_corruption_summary_v1",
        "status": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "analysis_implementation_sha256": protocol["implementation_sha256"]["summarizer"],
        "validation": {
            "runtime_capture_pairs": 306,
            "paired_condition_evaluations": observed_conditions,
            "scenario_units": 102,
            "seeds_averaged_inside_scenario": protocol["seeds"],
            "passes": True,
        },
        "by_family": by_family,
        "comparative_robustness_gate": {
            "all_five_families_pass": all(family_passes),
            "passes": all(family_passes),
        },
        "claim_policy": {
            "positive_advantage_means_candidate_degrades_less": True,
            "failure_is_reported_as_negative_result": True,
            "no_comparative_robustness_sota_without_gate": True,
        },
    }
    summary["manifest_sha256"] = canonical_hash(summary)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output_dir / "summary.md").write_text(render(summary), encoding="utf-8")
    (args.output_dir / "summary_complete").touch()
    print(render(summary), end="")


if __name__ == "__main__":
    main()
