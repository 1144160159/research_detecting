from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_paired_confirmation import bootstrap_ci, stable_bootstrap_seed


REPORT_METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)
LOWER_IS_BETTER = {"unknown_fpr95"}
REFERENCE_METHOD = "cauchy_modality_support_union"
ABLATION_METHODS = (
    "baseline",
    "cauchy_evidence",
    "modality_support_union",
    "cauchy_modality_support",
    "support_union",
    "max_modality_knn",
)
METHOD_DEFINITIONS = {
    "baseline": "equal-weight normalized uncertainty and global distance",
    "cauchy_evidence": "Cauchy combination of conflict and tree disagreement tails",
    "modality_support_union": (
        "Bonferroni union of global distance and every modality-specific KNN tail"
    ),
    "cauchy_modality_support": (
        "Cauchy combination of global distance and every modality-specific KNN tail"
    ),
    "support_union": "Bonferroni union of global distance and global KNN tail",
    "max_modality_knn": "maximum tail risk across modality-specific KNN components",
    REFERENCE_METHOD: (
        "Bonferroni union of the Cauchy evidence branch and modality support union"
    ),
    "selected_pairwise_endpoint": (
        "the frozen Pairwise report selected without unknown or test labels in each scenario"
    ),
}
REQUIRED_ARTIFACTS = ("metrics.json", "scores.npz", "provenance.json")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _report(value: object, name: str, run_key: str) -> dict[str, float]:
    if not isinstance(value, dict):
        raise ValueError("missing report %r for %s" % (name, run_key))
    missing = [metric for metric in REPORT_METRICS if metric not in value]
    if missing:
        raise ValueError("report %r for %s misses %r" % (name, run_key, missing))
    result = {metric: float(value[metric]) for metric in REPORT_METRICS}
    if not np.isfinite(list(result.values())).all():
        raise ValueError("report %r for %s contains non-finite values" % (name, run_key))
    return result


def discover_runs(root: Path) -> list[tuple[str, str, Path]]:
    paths = sorted(root.glob("*/*_seed7/metrics.json"))
    runs = []
    for path in paths:
        suite = path.parent.parent.name
        run_name = path.parent.name
        scenario = run_name[: -len("_seed7")]
        if not suite or not scenario:
            raise ValueError("unexpected strict-v4 run path: %s" % path)
        runs.append((suite, scenario, path))
    keys = [(suite, scenario) for suite, scenario, _ in runs]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate suite/scenario keys under %s" % root)
    return runs


def build_protocol(
    runs: list[tuple[str, str, Path]], coverage: dict[str, Any], script_path: Path
) -> dict[str, Any]:
    source_hashes = {}
    for suite, scenario, metrics_path in runs:
        run_key = "%s/%s" % (suite, scenario)
        missing = [
            name for name in REQUIRED_ARTIFACTS if not (metrics_path.parent / name).is_file()
        ]
        if missing:
            raise ValueError("missing artifacts for %s: %r" % (run_key, missing))
        source_hashes[run_key] = {
            name: sha256_file(metrics_path.parent / name) for name in REQUIRED_ARTIFACTS
        }
    protocol = {
        "schema_version": "strict_v4_seed7_component_ablation_protocol_v1",
        "status": "frozen_before_ablation_metric_values_are_computed",
        "scope": "development_seed7_descriptive_only",
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "scenario_count": len(runs),
        "seed": 7,
        "reference_method": REFERENCE_METHOD,
        "ablation_methods": list(ABLATION_METHODS),
        "separate_algorithm_endpoint": "selected_pairwise_endpoint",
        "method_definitions": METHOD_DEFINITIONS,
        "metrics": list(REPORT_METRICS),
        "inference_unit": "dataset_by_leave_one_attack_scenario",
        "bootstrap_unit": "scenario",
        "confirmatory_hypothesis_tests": False,
        "test_labels_used_for_reporting_only": True,
        "result_cannot_select_or_modify_the_final_algorithm": True,
        "required_artifacts": list(REQUIRED_ARTIFACTS),
        "source_artifact_sha256": source_hashes,
        "implementation_sha256": sha256_file(script_path),
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def write_frozen_protocol(path: Path, protocol: dict[str, Any]) -> None:
    if path.is_file():
        existing = json.loads(path.read_text(encoding="utf-8"))
        if existing != protocol:
            raise ValueError("existing component-ablation protocol differs from frozen inputs")
        return
    path.write_text(
        json.dumps(protocol, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_rows(runs: list[tuple[str, str, Path]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    rows = []
    selected_counts: Counter[str] = Counter()
    for suite, scenario, path in runs:
        run_key = "%s/%s" % (suite, scenario)
        payload = json.loads(path.read_text(encoding="utf-8"))
        details = payload.get("risk_selection_details", {})
        if details.get("unknown_or_test_labels_used_for_selection") is not False:
            raise ValueError("selection leakage guard failed for %s" % run_key)
        fingerprint = payload.get("split_metadata", {}).get("split_fingerprint", {}).get(
            "combined"
        )
        if not fingerprint:
            raise ValueError("missing combined split fingerprint for %s" % run_key)
        reports = payload.get("reports")
        if not isinstance(reports, dict):
            raise ValueError("missing reports mapping for %s" % run_key)
        normalized = {
            method: _report(reports.get(method), method, run_key)
            for method in (REFERENCE_METHOD,) + ABLATION_METHODS
        }
        selected_name = payload.get("selected_risk")
        if not isinstance(selected_name, str):
            raise ValueError("missing selected_risk for %s" % run_key)
        selected_report = _report(payload.get("selected_report"), selected_name, run_key)
        report_copy = _report(reports.get(selected_name), selected_name, run_key)
        for metric in REPORT_METRICS:
            if not np.isclose(selected_report[metric], report_copy[metric], atol=1e-12):
                raise ValueError("selected report mismatch for %s" % run_key)
        selected_counts[selected_name] += 1
        normalized["selected_pairwise_endpoint"] = selected_report
        rows.append(
            {
                "suite": suite,
                "scenario": scenario,
                "split_fingerprint": str(fingerprint),
                "selected_risk": selected_name,
                "reports": normalized,
            }
        )
    return rows, dict(sorted(selected_counts.items()))


def _mean(values: Iterable[float]) -> float:
    values = list(values)
    return float(sum(values) / len(values))


def compare_method(
    rows: list[dict[str, Any]], method: str, repetitions: int, base_seed: int
) -> dict[str, Any]:
    metric_results = {}
    for metric in REPORT_METRICS:
        direction = -1.0 if metric in LOWER_IS_BETTER else 1.0
        reference = [row["reports"][REFERENCE_METHOD][metric] for row in rows]
        challenger = [row["reports"][method][metric] for row in rows]
        raw = np.asarray(reference, dtype=np.float64) - np.asarray(
            challenger, dtype=np.float64
        )
        oriented = direction * raw
        counts = Counter(
            "win" if value > 1e-12 else "loss" if value < -1e-12 else "tie"
            for value in oriented
        )
        suite_results = {}
        suites = sorted(set(row["suite"] for row in rows))
        for suite in suites:
            indices = [index for index, row in enumerate(rows) if row["suite"] == suite]
            values = oriented[indices]
            suite_results[suite] = {
                "scenario_count": len(indices),
                "oriented_mean_improvement": float(values.mean()),
                "nonnegative": bool(values.mean() >= -1e-12),
            }
        seed = stable_bootstrap_seed(base_seed, "%s|%s" % (method, metric))
        metric_results[metric] = {
            "reference_mean": _mean(reference),
            "comparison_mean": _mean(challenger),
            "raw_reference_minus_comparison": float(raw.mean()),
            "oriented_mean_improvement": float(oriented.mean()),
            "scenario_wins_ties_losses": {
                "wins": counts["win"],
                "ties": counts["tie"],
                "losses": counts["loss"],
            },
            "oriented_improvement_bootstrap_ci": bootstrap_ci(
                oriented, repetitions, seed
            ),
            "per_suite": suite_results,
        }
    unknown_metrics = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
    return {
        "method": method,
        "definition": METHOD_DEFINITIONS[method],
        "metrics": metric_results,
        "four_unknown_metric_oriented_mean": _mean(
            metric_results[metric]["oriented_mean_improvement"]
            for metric in unknown_metrics
        ),
        "nonnegative_suite_metric_cells": sum(
            int(metric_results[metric]["per_suite"][suite]["nonnegative"])
            for metric in unknown_metrics
            for suite in metric_results[metric]["per_suite"]
        ),
        "suite_metric_cell_count": len(unknown_metrics)
        * len(metric_results[unknown_metrics[0]]["per_suite"]),
    }


def aggregate(
    rows: list[dict[str, Any]], repetitions: int, base_seed: int
) -> dict[str, Any]:
    methods = list(ABLATION_METHODS) + ["selected_pairwise_endpoint"]
    comparisons = {
        method: compare_method(rows, method, repetitions, base_seed)
        for method in methods
    }
    reference_means = {
        metric: _mean(row["reports"][REFERENCE_METHOD][metric] for row in rows)
        for metric in REPORT_METRICS
    }
    return {"reference_means": reference_means, "comparisons": comparisons}


def render(report: dict[str, Any]) -> str:
    aggregate_values = report["aggregate"]
    lines = [
        "# Strict-v4 seed7 component ablation",
        "",
        "Development-only descriptive evidence. It cannot select or modify the final algorithm.",
        "",
        "Reference: `cauchy_modality_support_union`.",
        "",
        "| Comparison | Known F1 gain | AUROC gain | AUPR gain | FPR95 reduction | OSCR gain | Four-metric mean |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for method in list(ABLATION_METHODS) + ["selected_pairwise_endpoint"]:
        value = aggregate_values["comparisons"][method]
        metrics = value["metrics"]
        lines.append(
            "| %s | %+.6f | %+.6f | %+.6f | %+.6f | %+.6f | %+.6f |"
            % (
                method,
                metrics["known_macro_f1"]["oriented_mean_improvement"],
                metrics["unknown_auroc"]["oriented_mean_improvement"],
                metrics["unknown_aupr"]["oriented_mean_improvement"],
                metrics["unknown_fpr95"]["oriented_mean_improvement"],
                metrics["oscr"]["oriented_mean_improvement"],
                value["four_unknown_metric_oriented_mean"],
            )
        )
    lines.extend(
        [
            "",
            "Positive values favor the fixed reference. The selected Pairwise endpoint is shown separately and is not a component ablation.",
            "",
            "Selected risks: `%s`." % json.dumps(report["selected_risk_counts"], sort_keys=True),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-scenarios", type=int, default=102)
    parser.add_argument("--bootstrap-repetitions", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260719)
    args = parser.parse_args()

    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    if coverage.get("schema_version") != "strict_v4_coverage_manifest_v2":
        raise ValueError("component ablation requires strict-v4 coverage manifest v2")
    if coverage.get("scenario_inference_units") != args.expected_scenarios:
        raise ValueError("coverage manifest scenario count mismatch")
    runs = discover_runs(args.root)
    if len(runs) != args.expected_scenarios:
        raise ValueError(
            "expected %d strict-v4 reports, found %d" % (args.expected_scenarios, len(runs))
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    protocol = build_protocol(runs, coverage, Path(__file__).resolve())
    write_frozen_protocol(args.output_dir / "protocol_manifest.json", protocol)

    rows, selected_counts = load_rows(runs)
    report = {
        "schema_version": "strict_v4_seed7_component_ablation_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "scenario_count": len(rows),
        "selected_risk_counts": selected_counts,
        "aggregate": aggregate(
            rows, args.bootstrap_repetitions, args.bootstrap_seed
        ),
        "claim_boundary": (
            "descriptive_seed7_only_not_final_algorithm_selection_or_confirmed_sota"
        ),
    }
    (args.output_dir / "ablation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    rendered = render(report)
    (args.output_dir / "ablation.md").write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
