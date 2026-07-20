from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from summarize_paired_confirmation import (
    INFERENCE_METRICS,
    LOWER_IS_BETTER,
    bootstrap_ci,
    effect_sizes,
    holm_adjust,
    paired_wilcoxon,
    stable_bootstrap_seed,
)


REPORT_METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)
DEFAULT_FINAL_METHOD = "cauchy_modality_support_union"
DEFAULT_ABLATIONS = (
    "baseline",
    "cauchy_evidence",
    "modality_support_union",
    "cauchy_modality_support",
    "support_union",
    "max_modality_knn",
)
REQUIRED_ARTIFACTS = (
    "metrics.json",
    "scores.npz",
    "evidence_package.npz",
    "provenance.json",
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Summarize strict-v2 Edge ablations with scenarios as independent "
            "inference units and one Holm family across all ablation hypotheses"
        )
    )
    parser.add_argument("--root", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--seeds", default="7,11,19,23,37")
    parser.add_argument("--expected-scenarios", type=int, default=14)
    parser.add_argument("--final-method", default=DEFAULT_FINAL_METHOD)
    parser.add_argument("--ablations", default=",".join(DEFAULT_ABLATIONS))
    parser.add_argument(
        "--expected-risk-policy", default="confirmed_cauchy_modality_union_v1_edge"
    )
    parser.add_argument("--bootstrap-repetitions", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260717)
    return parser.parse_args()


def discover_ablations(root: Path, final_method: str) -> tuple[str, ...]:
    paths = sorted(root.glob("*/*/metrics.json"))
    if not paths:
        raise ValueError(f"no metrics found under {root}")
    payload = json.loads(paths[0].read_text(encoding="utf-8"))
    reports = payload.get("reports")
    if not isinstance(reports, dict) or final_method not in reports:
        raise ValueError("cannot discover ablations from the first metrics report")
    ablations = tuple(sorted(set(reports) - {final_method}))
    if not ablations:
        raise ValueError("discovered zero ablations")
    return ablations


def task_key(path: Path, root: Path) -> tuple[str, str, int]:
    relative = path.relative_to(root)
    if len(relative.parts) != 3 or relative.name != "metrics.json":
        raise ValueError(f"unexpected metrics path: {path}")
    suite, run = relative.parts[:2]
    if "_seed" not in run:
        raise ValueError(f"run directory has no seed suffix: {path.parent}")
    scenario, seed_text = run.rsplit("_seed", 1)
    return suite, scenario, int(seed_text)


def _assert_report(
    report: object, method: str, key: tuple[str, str, int]
) -> dict[str, float]:
    if not isinstance(report, dict):
        raise ValueError(f"missing report {method!r} for {key}")
    missing = [metric for metric in REPORT_METRICS if metric not in report]
    if missing:
        raise ValueError(f"report {method!r} for {key} misses metrics {missing}")
    return {metric: float(report[metric]) for metric in REPORT_METRICS}


def load_runs(
    root: Path,
    seeds: set[int],
    expected_scenarios: int,
    final_method: str,
    ablations: tuple[str, ...],
    expected_risk_policy: str,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    if final_method in ablations:
        raise ValueError("final method must not also be listed as an ablation")
    if len(set(ablations)) != len(ablations):
        raise ValueError("ablation names must be unique")

    rows: list[dict[str, object]] = []
    grouped: dict[tuple[str, str], set[int]] = defaultdict(set)
    seen: set[tuple[str, str, int]] = set()
    for path in sorted(root.glob("*/*/metrics.json")):
        key = task_key(path, root)
        if key in seen:
            raise ValueError(f"duplicate task under {root}: {key}")
        seen.add(key)
        suite, scenario, seed = key
        if seed not in seeds:
            raise ValueError(f"unexpected seed {seed} for {key}")
        missing_artifacts = [
            name for name in REQUIRED_ARTIFACTS if not (path.parent / name).exists()
        ]
        if missing_artifacts:
            raise ValueError(f"missing artifacts for {key}: {missing_artifacts}")

        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("risk_policy") != expected_risk_policy:
            raise ValueError(
                f"risk policy mismatch for {key}: {payload.get('risk_policy')!r}"
            )
        if payload.get("selected_risk") != final_method:
            raise ValueError(
                f"selected risk mismatch for {key}: {payload.get('selected_risk')!r}"
            )
        details = payload.get("risk_selection_details", {})
        if details.get("unknown_or_test_labels_used_for_selection") is not False:
            raise ValueError(f"selection leakage guard failed for {key}")
        fingerprint = (
            payload.get("split_metadata", {})
            .get("split_fingerprint", {})
            .get("combined")
        )
        if not fingerprint:
            raise ValueError(f"missing split fingerprint for {key}")

        reports = payload.get("reports")
        if not isinstance(reports, dict):
            raise ValueError(f"missing reports mapping for {key}")
        methods = (final_method,) + ablations
        selected = _assert_report(payload.get("selected_report"), final_method, key)
        selected_in_reports = _assert_report(reports.get(final_method), final_method, key)
        if any(
            not np.isclose(selected[metric], selected_in_reports[metric], atol=1e-12)
            for metric in REPORT_METRICS
        ):
            raise ValueError(f"selected report does not match final report for {key}")
        normalized_reports = {
            method: _assert_report(reports.get(method), method, key)
            for method in methods
        }
        rows.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed": seed,
                "split_fingerprint": str(fingerprint),
                "reports": normalized_reports,
            }
        )
        grouped[(suite, scenario)].add(seed)

    if not rows:
        raise ValueError(f"no metrics found under {root}")
    if len(grouped) != expected_scenarios:
        raise ValueError(
            f"scenario coverage mismatch: expected {expected_scenarios}, "
            f"found {len(grouped)}"
        )
    mismatched = {
        f"{suite}/{scenario}": sorted(observed)
        for (suite, scenario), observed in grouped.items()
        if observed != seeds
    }
    if mismatched:
        raise ValueError(
            f"seed coverage mismatch: expected {sorted(seeds)}, observed {mismatched}"
        )
    expected_runs = expected_scenarios * len(seeds)
    if len(rows) != expected_runs:
        raise ValueError(
            f"run coverage mismatch: expected {expected_runs}, found {len(rows)}"
        )
    return rows, {
        "passes": True,
        "run_count": len(rows),
        "scenario_count": len(grouped),
        "seeds": sorted(seeds),
        "required_artifacts_checked": list(REQUIRED_ARTIFACTS),
        "artifact_checks": len(rows) * len(REQUIRED_ARTIFACTS),
        "risk_policy": expected_risk_policy,
        "selected_risk": final_method,
        "selection_uses_unknown_or_test_labels": False,
        "split_fingerprint_checks": len(rows),
        "report_methods": [final_method, *ablations],
    }


def aggregate(
    rows: list[dict[str, object]],
    final_method: str,
    ablations: tuple[str, ...],
    bootstrap_repetitions: int,
    bootstrap_seed: int,
) -> dict[str, object]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[f"{row['suite']}/{row['scenario']}"] .append(row)

    comparisons: dict[str, object] = {}
    raw_p_values: dict[str, float] = {}
    for ablation in ablations:
        metric_reports: dict[str, object] = {}
        for metric in REPORT_METRICS:
            direction = -1.0 if metric in LOWER_IS_BETTER else 1.0
            final_means: list[float] = []
            ablation_means: list[float] = []
            raw_deltas: list[float] = []
            oriented_deltas: list[float] = []
            scenario_blocks: list[dict[str, object]] = []
            for scenario, items in sorted(grouped.items()):
                final_mean = float(
                    np.mean([row["reports"][final_method][metric] for row in items])
                )
                ablation_mean = float(
                    np.mean([row["reports"][ablation][metric] for row in items])
                )
                raw_delta = final_mean - ablation_mean
                oriented_delta = direction * raw_delta
                final_means.append(final_mean)
                ablation_means.append(ablation_mean)
                raw_deltas.append(raw_delta)
                oriented_deltas.append(oriented_delta)
                scenario_blocks.append(
                    {
                        "scenario": scenario,
                        "seed_count": len(items),
                        "ablation_mean": ablation_mean,
                        "final_mean": final_mean,
                        "raw_delta": raw_delta,
                        "oriented_improvement": oriented_delta,
                    }
                )
            oriented = np.asarray(oriented_deltas, dtype=np.float64)
            test = paired_wilcoxon(oriented_deltas)
            hypothesis = f"{ablation}|{metric}"
            if metric in INFERENCE_METRICS:
                raw_p_values[hypothesis] = float(test["raw_p_value"])
            metric_reports[metric] = {
                "direction": (
                    "lower_is_better" if direction < 0 else "higher_is_better"
                ),
                "ablation_scenario_mean": float(np.mean(ablation_means)),
                "final_scenario_mean": float(np.mean(final_means)),
                "raw_mean_delta": float(np.mean(raw_deltas)),
                "oriented_mean_improvement": float(np.mean(oriented)),
                "wins": int((oriented > 1e-12).sum()),
                "ties": int((np.abs(oriented) <= 1e-12).sum()),
                "losses": int((oriented < -1e-12).sum()),
                "bootstrap_95_ci": bootstrap_ci(
                    oriented_deltas,
                    bootstrap_repetitions,
                    stable_bootstrap_seed(bootstrap_seed, hypothesis),
                ),
                "effect_sizes": effect_sizes(oriented_deltas),
                "wilcoxon": test,
                "scenario_blocks": scenario_blocks,
            }
        comparisons[ablation] = {"metrics": metric_reports}

    adjusted = holm_adjust(raw_p_values)
    for hypothesis, adjusted_p in adjusted.items():
        ablation, metric = hypothesis.split("|", 1)
        comparisons[ablation]["metrics"][metric]["wilcoxon"][
            "holm_adjusted_p_value"
        ] = adjusted_p

    for ablation in ablations:
        significant: list[str] = []
        directional: list[str] = []
        for metric in INFERENCE_METRICS:
            item = comparisons[ablation]["metrics"][metric]
            if item["oriented_mean_improvement"] > 0.0:
                directional.append(metric)
            if (
                item["bootstrap_95_ci"]["lower"] > 0.0
                and item["wilcoxon"]["holm_adjusted_p_value"] < 0.05
            ):
                significant.append(metric)
        comparisons[ablation]["decision"] = {
            "final_directionally_better_metrics": directional,
            "final_significantly_better_metrics": significant,
            "final_better_on_all_unknown_metrics": len(directional)
            == len(INFERENCE_METRICS),
        }

    return {
        "inference_unit": "scenario",
        "scenario_count": len(grouped),
        "seed_repeats_are_averaged_within_scenario": True,
        "final_method": final_method,
        "ablations": list(ablations),
        "holm_family": {
            "metrics": list(INFERENCE_METRICS),
            "comparisons": list(ablations),
            "hypothesis_count": len(raw_p_values),
        },
        "comparisons": comparisons,
    }


def markdown(report: dict[str, object]) -> str:
    summary = report["scenario_blocked_inference"]
    validation = report["validation"]
    lines = [
        "# Strict-v2 Edge component ablation",
        "",
        f"Validated runs: {validation['run_count']}; inference units: "
        f"{summary['scenario_count']} scenarios; seeds: {validation['seeds']}.",
        "Seed repeats are averaged within each scenario before inference.",
        f"Holm family: {summary['holm_family']['hypothesis_count']} hypotheses "
        "across all ablations and unknown-detection metrics.",
        "",
        "| Ablation | Metric | Ablation | Final | Oriented improvement | 95% CI | W/T/L | Holm p |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for ablation in summary["ablations"]:
        comparison = summary["comparisons"][ablation]
        for metric in REPORT_METRICS:
            item = comparison["metrics"][metric]
            ci = item["bootstrap_95_ci"]
            adjusted = item["wilcoxon"]["holm_adjusted_p_value"]
            adjusted_text = "NA" if adjusted is None else f"{adjusted:.6f}"
            lines.append(
                f"| {ablation} | {metric} | "
                f"{item['ablation_scenario_mean']:.6f} | "
                f"{item['final_scenario_mean']:.6f} | "
                f"{item['oriented_mean_improvement']:+.6f} | "
                f"[{ci['lower']:+.6f}, {ci['upper']:+.6f}] | "
                f"{item['wins']}/{item['ties']}/{item['losses']} | "
                f"{adjusted_text} |"
            )
    lines.extend(["", "## Component decisions", ""])
    for ablation in summary["ablations"]:
        decision = summary["comparisons"][ablation]["decision"]
        significant = decision["final_significantly_better_metrics"]
        significant_text = ", ".join(significant) if significant else "none"
        lines.append(
            f"- `{ablation}`: final directionally better on "
            f"{len(decision['final_directionally_better_metrics'])}/"
            f"{len(INFERENCE_METRICS)} unknown metrics; Holm-confirmed: "
            f"{significant_text}."
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_arguments()
    seeds = {int(value) for value in args.seeds.split(",") if value.strip()}
    ablations = (
        discover_ablations(Path(args.root), args.final_method)
        if args.ablations.strip().lower() == "all"
        else tuple(value for value in args.ablations.split(",") if value.strip())
    )
    if not seeds:
        raise ValueError("at least one seed is required")
    if not ablations:
        raise ValueError("at least one ablation is required")
    rows, validation = load_runs(
        Path(args.root),
        seeds,
        args.expected_scenarios,
        args.final_method,
        ablations,
        args.expected_risk_policy,
    )
    report = {
        "schema_version": "strict_v2_edge_ablation_v1",
        "root": args.root,
        "validation": validation,
        "scenario_blocked_inference": aggregate(
            rows,
            args.final_method,
            ablations,
            args.bootstrap_repetitions,
            args.bootstrap_seed,
        ),
    }
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "ablation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "ablation.md").write_text(markdown(report), encoding="utf-8")
    print(json.dumps(report["scenario_blocked_inference"], indent=2))


if __name__ == "__main__":
    main()
