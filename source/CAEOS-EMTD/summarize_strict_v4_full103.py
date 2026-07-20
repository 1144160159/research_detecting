from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from analyze_caeos_closr_fusion import empirical_percentile
from caeos.hybrid_open_set import evaluate_hybrid_open_set
from select_strict_v4_external_risk_candidate import canonical_hash
from summarize_paired_confirmation import aggregate
from summarize_strict_v4_pilot import (
    LOWER_IS_BETTER,
    METRICS,
    aggregate_table,
    oriented_delta,
    report_metrics,
)


FINAL_METHOD = "caeos_domain_safe_router"
RANK_UNION_METHOD = "caeos_openmax_rank_union"
PAIRWISE_METHOD = "caeos_pairwise"
REFERENCE_METHOD = "caeos_reference"
OPENMAX_RISK_METHOD = "caeos_openmax_risk"
UNKNOWN_METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
PAIRED_EXTRA_METRICS = ("known_acceptance_rate", "unknown_rejection_rate")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_task(task: str) -> tuple[str, int]:
    if "_seed" not in task:
        raise ValueError(f"task has no seed suffix: {task!r}")
    scenario, seed_text = task.rsplit("_seed", 1)
    return scenario, int(seed_text)


def full_report_metrics(report: object, label: str) -> dict[str, float]:
    values = report_metrics(report, label)
    if not isinstance(report, dict):
        raise ValueError(f"missing report for {label}")
    missing = [metric for metric in PAIRED_EXTRA_METRICS if metric not in report]
    if missing:
        raise ValueError(f"report for {label} misses paired metrics {missing}")
    for metric in PAIRED_EXTRA_METRICS:
        value = float(report[metric])
        if not np.isfinite(value):
            raise ValueError(f"non-finite paired metric {metric} for {label}")
        values[metric] = value
    return values


def expected_tasks(manifest: dict[str, Any]) -> set[tuple[str, str]]:
    return {
        (suite, scenario)
        for suite, values in manifest["scenario_registry"].items()
        for scenario in values["scenarios"]
    }


def base_report(gate_dir: Path, acceptance: float = 0.95) -> dict[str, float]:
    name = "cauchy_modality_support_union"
    with np.load(gate_dir / "scores.npz") as scores:
        validation_key = f"validation_{name}"
        test_key = f"test_{name}"
        if validation_key not in scores or test_key not in scores:
            raise ValueError(f"base risk is absent under {gate_dir}")
        validation = empirical_percentile(scores[validation_key], scores[validation_key])
        test = empirical_percentile(scores[validation_key], scores[test_key])
        threshold = float(np.quantile(validation, acceptance))
        report = evaluate_hybrid_open_set(
            scores["test_labels"],
            scores["test_unknown"].astype(bool),
            scores["test_prediction"],
            test,
            threshold,
        )
    return full_report_metrics(report, f"{gate_dir}/reference")


def validate_router_manifest(
    router: dict[str, Any], manifest: dict[str, Any], raw_fusion: Path
) -> None:
    if router.get("schema_version") != "strict_v4_domain_safe_router_candidate_v1":
        raise ValueError("unexpected strict-v4 router manifest schema")
    if router.get("manifest_sha256") != canonical_hash(router):
        raise ValueError("strict-v4 router manifest SHA mismatch")
    if router.get("coverage_manifest_sha256") != manifest["manifest_sha256"]:
        raise ValueError("router manifest does not bind the coverage manifest")
    if router.get("raw_fusion_sha256") != file_hash(raw_fusion):
        raise ValueError("router manifest does not bind the raw fusion artifact")
    if set(router.get("routing", {})) != set(manifest["scenario_registry"]):
        raise ValueError("router suite coverage differs from the coverage manifest")
    audit = router.get("inference_audit", {})
    if not (
        audit.get("runtime_selection_inputs") == ["suite_id"]
        and audit.get("unknown_or_test_labels_used_at_inference") is False
        and audit.get("unknown_or_test_labels_used_for_thresholds") is False
        and audit.get("new_seed_confirmation_must_not_change_routing") is True
    ):
        raise ValueError("router inference audit is not frozen and leakage-safe")


def routed_report(
    run: dict[str, Any], suite: str, router: dict[str, Any], label: str
) -> dict[str, float]:
    method = router["routing"][suite]["method"]
    if method == PAIRWISE_METHOD:
        report = run["gate_report"]
    else:
        reports = run.get("reports", {})
        if method not in reports:
            raise ValueError(f"router method {method!r} is absent for {label}")
        report = reports[method]
    return full_report_metrics(report, f"{label}/{FINAL_METHOD}")


def load_blocks(
    manifest: dict[str, Any],
    raw: dict[str, Any],
    router: dict[str, Any],
    gate_root: Path,
    mlp_root: Path,
    baseline_root: Path | None = None,
) -> tuple[dict[str, dict[str, dict[str, float]]], dict[str, Any]]:
    expected = expected_tasks(manifest)
    expected_count = manifest["scenario_inference_units"]
    if len(expected) != expected_count:
        raise ValueError(
            f"expected {expected_count} manifest tasks, found {len(expected)}"
        )
    if raw.get("overall", {}).get("number_of_runs") != expected_count:
        raise ValueError(f"raw fusion does not contain {expected_count} runs")
    observed: set[tuple[str, str]] = set()
    blocks: dict[str, dict[str, dict[str, float]]] = {}
    selected_paths: dict[str, int] = {}
    artifact_checks = 0
    split_checks = 0
    baseline_run_checks = 0
    for run in raw["runs"]:
        scenario, seed = parse_task(run["task"])
        task = (run["suite"], scenario)
        if seed != 7 or task in observed:
            raise ValueError(f"invalid or duplicate coverage task: {task}/seed{seed}")
        observed.add(task)
        suite, scenario = task
        gate_dir = gate_root / suite / f"{scenario}_seed7"
        mlp_dir = mlp_root / suite / f"{scenario}_seed7_mlp"
        for directory, names in (
            (gate_dir, ("metrics.json", "scores.npz", "evidence_package.npz", "provenance.json")),
            (mlp_dir, ("metrics.json", "scores.npz", "provenance.json")),
        ):
            missing = [name for name in names if not (directory / name).is_file()]
            if missing:
                raise ValueError(f"missing artifacts under {directory}: {missing}")
            artifact_checks += len(names)
        gate_metrics = json.loads((gate_dir / "metrics.json").read_text(encoding="utf-8"))
        mlp_metrics = json.loads((mlp_dir / "metrics.json").read_text(encoding="utf-8"))
        if gate_metrics.get("risk_policy") != "strict_v4_full103_pairwise_coverage_v1":
            raise ValueError(f"pairwise coverage policy mismatch for {task}")
        details = gate_metrics.get("risk_selection_details", {})
        if details.get("unknown_or_test_labels_used_for_selection") is not False:
            raise ValueError(f"pairwise leakage guard failed for {task}")
        selection = mlp_metrics.get("selection_evidence", {})
        if selection.get("unknown_or_test_labels_used_for_fitting_or_selection") is not False:
            raise ValueError(f"MLP leakage guard failed for {task}")
        gate_fingerprint = gate_metrics["split_metadata"]["split_fingerprint"]["combined"]
        mlp_fingerprint = mlp_metrics["split_metadata"]["split_fingerprint"]["combined"]
        raw_fingerprint = run.get("audit", {}).get("split_fingerprint")
        if gate_fingerprint != mlp_fingerprint or gate_fingerprint != raw_fingerprint:
            raise ValueError(f"split fingerprint mismatch for {task}")
        split_checks += 1
        selected = run["gate_selected_risk"]
        selected_paths[selected] = selected_paths.get(selected, 0) + 1
        key = f"{suite}/{scenario}"
        methods = {
            REFERENCE_METHOD: base_report(gate_dir),
            PAIRWISE_METHOD: full_report_metrics(run["gate_report"], f"{key}/pairwise"),
            OPENMAX_RISK_METHOD: full_report_metrics(
                run["expert_report"], f"{key}/caeos_openmax_risk"
            ),
            RANK_UNION_METHOD: full_report_metrics(
                run["reports"]["rank_union"], f"{key}/final"
            ),
            FINAL_METHOD: routed_report(run, suite, router, key),
        }
        reports = mlp_metrics.get("reports", {})
        if not reports:
            raise ValueError(f"MLP reports are missing for {task}")
        for risk, report in reports.items():
            methods[f"mlp_{risk}"] = full_report_metrics(
                report, f"{key}/mlp_{risk}"
            )
        if baseline_root is not None:
            for model in ("opendetect", "classical_ood"):
                directory = baseline_root / suite / f"{scenario}_seed7_{model}"
                missing = [
                    name
                    for name in ("metrics.json", "scores.npz", "provenance.json")
                    if not (directory / name).is_file()
                ]
                if missing:
                    raise ValueError(
                        f"missing independent baseline artifacts under {directory}: {missing}"
                    )
                artifact_checks += 3
                baseline_metrics = json.loads(
                    (directory / "metrics.json").read_text(encoding="utf-8")
                )
                fingerprint = baseline_metrics["split_metadata"]["split_fingerprint"][
                    "combined"
                ]
                if fingerprint != gate_fingerprint:
                    raise ValueError(f"baseline split fingerprint mismatch for {task}/{model}")
                evidence = baseline_metrics.get("selection_evidence", {})
                if model == "opendetect":
                    if evidence.get(
                        "unknown_or_test_labels_used_for_fitting_or_selection"
                    ) is not False:
                        raise ValueError(f"OpenDetect leakage guard failed for {task}")
                else:
                    if not (
                        evidence.get("unknown_or_test_labels_used_for_training") is False
                        and evidence.get("unknown_or_test_labels_used_for_thresholds")
                        is False
                    ):
                        raise ValueError(f"classical OOD leakage guard failed for {task}")
                baseline_reports = baseline_metrics.get("reports", {})
                expected_reports = (
                    {"opendetect"}
                    if model == "opendetect"
                    else {
                        "isolation_forest",
                        "one_class_svm",
                        "local_outlier_factor",
                        "pca_reconstruction",
                    }
                )
                if set(baseline_reports) != expected_reports:
                    raise ValueError(f"baseline report set mismatch for {task}/{model}")
                for method, report in baseline_reports.items():
                    methods[method] = full_report_metrics(
                        report, f"{key}/{method}"
                    )
                baseline_run_checks += 1
        blocks[key] = methods
    if observed != expected:
        raise ValueError(
            f"coverage mismatch: missing={sorted(expected-observed)}, "
            f"unexpected={sorted(observed-expected)}"
        )
    method_set = set(next(iter(blocks.values())))
    if any(set(methods) != method_set for methods in blocks.values()):
        raise ValueError("method coverage differs across full-matrix scenarios")
    return blocks, {
        "passes": True,
        "scenario_count": len(blocks),
        "dataset_count": len(manifest["scenario_registry"]),
        "method_count": len(method_set),
        "artifact_checks": artifact_checks,
        "split_fingerprint_pair_checks": split_checks,
        "split_fingerprints_identical": True,
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
        "pairwise_selected_paths": selected_paths,
        "independent_baseline_run_checks": baseline_run_checks,
        "router_manifest_sha256": router["manifest_sha256"],
        "router_routes": {
            suite: details["method"] for suite, details in router["routing"].items()
        },
    }


def paired_analysis(
    blocks: dict[str, dict[str, dict[str, float]]], candidate: str, reference: str
) -> dict[str, Any]:
    rows = []
    for key, methods in sorted(blocks.items()):
        suite, scenario = key.split("/", 1)
        rows.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed": 7,
                "candidate_selected": candidate,
                "reference_selected": reference,
                "candidate_report": methods[candidate],
                "reference_report": methods[reference],
            }
        )
    return aggregate(rows, 10000, 20260718)


def decision(
    overall: list[dict[str, Any]],
    by_suite: dict[str, list[dict[str, Any]]],
    pairwise_gain: dict[str, Any],
    independent_baselines_included: bool,
) -> dict[str, Any]:
    final = next(row for row in overall if row["method"] == FINAL_METHOD)
    competitors = [row for row in overall if row["method"] != FINAL_METHOD]
    strongest = {}
    for metric in METRICS:
        best = (
            min(competitors, key=lambda row: row[metric])
            if metric in LOWER_IS_BETTER
            else max(competitors, key=lambda row: row[metric])
        )
        strongest[metric] = {
            "method": best["method"],
            "value": best[metric],
            "final_value": final[metric],
            "oriented_delta": oriented_delta(final[metric], best[metric], metric),
        }
    suite_nonnegative = {
        suite: {
            metric: (
                next(row for row in table if row["method"] == FINAL_METHOD)[metric]
                - next(row for row in table if row["method"] == PAIRWISE_METHOD)[metric]
            )
            * (-1.0 if metric in LOWER_IS_BETTER else 1.0)
            >= 0.0
            for metric in UNKNOWN_METRICS
        }
        for suite, table in by_suite.items()
    }
    pairwise_positive = {
        metric: pairwise_gain["metrics"][metric]["oriented_mean_improvement"] > 0.0
        for metric in UNKNOWN_METRICS
    }
    blockers = [
        "coverage matrix uses one development seed",
        "frozen router requires confirmation on entirely new seeds",
        "confirmatory multi-seed scenario-block inference remains pending",
    ]
    if not independent_baselines_included:
        blockers.insert(1, "independent strong baselines are not yet in this matrix")
    return {
        "coverage_gate_passes": True,
        "final_mean_unknown_metric_rank": final["mean_unknown_metric_rank"],
        "final_is_mean_rank_one": final["mean_unknown_metric_rank"] == 1.0,
        "all_unknown_metrics_improve_vs_pairwise": all(pairwise_positive.values()),
        "unknown_metrics_improve_vs_pairwise": pairwise_positive,
        "all_suites_nonnegative_vs_pairwise": all(
            value for values in suite_nonnegative.values() for value in values.values()
        ),
        "suite_nonnegative_vs_pairwise": suite_nonnegative,
        "strongest_competitors": strongest,
        "full_sota_claim_allowed": False,
        "full_sota_blockers": blockers,
    }


def render(report: dict[str, Any]) -> str:
    lines = [
        f"# Strict-v4 full {report['validation']['scenario_count']}-scenario coverage screen",
        "",
        f"Validation: **PASS**; datasets: {report['validation']['dataset_count']}; "
        f"scenarios: {report['validation']['scenario_count']}; methods: "
        f"{report['validation']['method_count']}.",
        "This is a seed7 coverage screen, not confirmatory multi-seed inference.",
        "",
        "| Rank | Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, row in enumerate(report["overall"], 1):
        lines.append(
            f"| {rank} | {row['method']} | {row['known_macro_f1']:.6f} | "
            f"{row['unknown_auroc']:.6f} | {row['unknown_aupr']:.6f} | "
            f"{row['unknown_fpr95']:.6f} | {row['oscr']:.6f} | "
            f"{row['mean_unknown_metric_rank']:.3f} |"
        )
    lines.extend(["", "## Frozen domain-safe router versus pairwise CAEOS", ""])
    comparison = report["comparisons"]["final_vs_pairwise"]
    lines.extend(
        [
            "| Metric | Pairwise | Domain-safe router | Oriented gain | 95% CI | W/T/L |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for metric in METRICS:
        item = comparison["metrics"][metric]
        ci = item["bootstrap_95_ci"]
        lines.append(
            f"| {metric} | {item['reference_scenario_mean']:.6f} | "
            f"{item['candidate_scenario_mean']:.6f} | "
            f"{item['oriented_mean_improvement']:+.6f} | "
            f"[{ci['lower']:+.6f}, {ci['upper']:+.6f}] | "
            f"{item['wins']}/{item['ties']}/{item['losses']} |"
        )
    decision_value = report["decision"]
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"Final mean-rank-one: **{decision_value['final_is_mean_rank_one']}**.",
            f"All four means improve versus pairwise CAEOS: "
            f"**{decision_value['all_unknown_metrics_improve_vs_pairwise']}**.",
            f"Every suite is non-regressing versus pairwise CAEOS: "
            f"**{decision_value['all_suites_nonnegative_vs_pairwise']}**.",
            "Full SOTA claim: **NOT YET ALLOWED**; this router was selected on seed7 "
            "and requires frozen new-seed confirmation.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--raw-fusion", type=Path, required=True)
    parser.add_argument("--router-manifest", type=Path, required=True)
    parser.add_argument("--gate-root", type=Path, required=True)
    parser.add_argument("--mlp-root", type=Path, required=True)
    parser.add_argument("--baseline-root", type=Path)
    parser.add_argument("--baseline-manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "strict_v4_coverage_manifest_v2":
        raise ValueError("unexpected strict-v4 coverage manifest schema")
    if manifest.get("manifest_sha256") != canonical_hash(manifest):
        raise ValueError("full103 coverage manifest SHA mismatch")
    raw = json.loads(args.raw_fusion.read_text(encoding="utf-8"))
    router = json.loads(args.router_manifest.read_text(encoding="utf-8"))
    validate_router_manifest(router, manifest, args.raw_fusion)
    baseline_manifest_sha256 = None
    if (args.baseline_root is None) != (args.baseline_manifest is None):
        raise ValueError("--baseline-root and --baseline-manifest must be provided together")
    if args.baseline_manifest is not None:
        baseline_manifest = json.loads(
            args.baseline_manifest.read_text(encoding="utf-8")
        )
        if baseline_manifest.get("schema_version") != (
            "strict_v4_baseline_manifest_v2"
        ):
            raise ValueError("unexpected strict-v4 baseline manifest schema")
        if baseline_manifest.get("manifest_sha256") != canonical_hash(
            baseline_manifest
        ):
            raise ValueError("full103 baseline manifest SHA mismatch")
        if baseline_manifest.get("coverage_manifest_sha256") != manifest[
            "manifest_sha256"
        ]:
            raise ValueError("baseline manifest does not bind the coverage manifest")
        baseline_manifest_sha256 = baseline_manifest["manifest_sha256"]
    blocks, validation = load_blocks(
        manifest, raw, router, args.gate_root, args.mlp_root, args.baseline_root
    )
    overall = aggregate_table(blocks)
    by_suite = {
        suite: aggregate_table(
            {key: value for key, value in blocks.items() if key.startswith(f"{suite}/")}
        )
        for suite in manifest["scenario_registry"]
    }
    comparisons = {
        "final_vs_reference": paired_analysis(blocks, FINAL_METHOD, REFERENCE_METHOD),
        "final_vs_pairwise": paired_analysis(blocks, FINAL_METHOD, PAIRWISE_METHOD),
        "final_vs_caeos_openmax_risk": paired_analysis(
            blocks, FINAL_METHOD, OPENMAX_RISK_METHOD
        ),
        "final_vs_mlp_openmax": paired_analysis(blocks, FINAL_METHOD, "mlp_openmax"),
    }
    result = {
        "schema_version": "strict_v4_full103_coverage_summary_v1",
        "coverage_manifest_sha256": manifest["manifest_sha256"],
        "baseline_manifest_sha256": baseline_manifest_sha256,
        "router_manifest_sha256": router["manifest_sha256"],
        "raw_fusion_sha256": file_hash(args.raw_fusion),
        "analysis_implementation_sha256": file_hash(Path(__file__)),
        "validation": validation,
        "overall": overall,
        "by_suite": by_suite,
        "comparisons": comparisons,
        "decision": decision(
            overall,
            by_suite,
            comparisons["final_vs_pairwise"],
            independent_baselines_included=args.baseline_root is not None,
        ),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "summary.md").write_text(render(result), encoding="utf-8")
    print(render(result))


if __name__ == "__main__":
    main()
