from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import rankdata


METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)
UNKNOWN_METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
LOWER_IS_BETTER = {"unknown_fpr95"}
REQUIRED_ARTIFACTS = (
    "metrics.json",
    "scores.npz",
    "evidence_package.npz",
    "provenance.json",
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Screen every fixed Edge risk and freeze a confirmation candidate"
    )
    parser.add_argument("--root", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--seeds", default="7,11,19,23,37")
    parser.add_argument("--confirmation-seeds", default="67,71,73,79")
    parser.add_argument("--expected-scenarios", type=int, default=14)
    parser.add_argument(
        "--final-method", default="cauchy_modality_support_union"
    )
    parser.add_argument(
        "--expected-risk-policy", default="confirmed_cauchy_modality_union_v1_edge"
    )
    parser.add_argument("--nonregression-tolerance", type=float, default=0.01)
    return parser.parse_args()


def task_key(path: Path, root: Path) -> tuple[str, str, int]:
    relative = path.relative_to(root)
    if len(relative.parts) != 3 or relative.name != "metrics.json":
        raise ValueError(f"unexpected metrics path: {path}")
    suite, run = relative.parts[:2]
    if "_seed" not in run:
        raise ValueError(f"run directory has no seed suffix: {path.parent}")
    scenario, seed_text = run.rsplit("_seed", 1)
    return suite, scenario, int(seed_text)


def normalized_report(report: object, method: str, key: tuple[str, str, int]) -> dict[str, float]:
    if not isinstance(report, dict):
        raise ValueError(f"missing report {method!r} for {key}")
    missing = [metric for metric in METRICS if metric not in report]
    if missing:
        raise ValueError(f"report {method!r} for {key} misses metrics {missing}")
    return {metric: float(report[metric]) for metric in METRICS}


def load_matrix(
    root: Path,
    seeds: set[int],
    expected_scenarios: int,
    final_method: str,
    expected_risk_policy: str,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows: list[dict[str, object]] = []
    grouped: dict[tuple[str, str], set[int]] = defaultdict(set)
    method_set: set[str] | None = None
    source_hashes: list[dict[str, str]] = []
    for path in sorted(root.glob("*/*/metrics.json")):
        key = task_key(path, root)
        suite, scenario, seed = key
        if seed not in seeds:
            raise ValueError(f"unexpected seed {seed} for {key}")
        missing_artifacts = [
            name for name in REQUIRED_ARTIFACTS if not (path.parent / name).exists()
        ]
        if missing_artifacts:
            raise ValueError(f"missing artifacts for {key}: {missing_artifacts}")
        raw = path.read_bytes()
        payload = json.loads(raw.decode("utf-8"))
        if payload.get("risk_policy") != expected_risk_policy:
            raise ValueError(f"risk policy mismatch for {key}")
        if payload.get("selected_risk") != final_method:
            raise ValueError(f"selected risk mismatch for {key}")
        details = payload.get("risk_selection_details", {})
        if details.get("unknown_or_test_labels_used_for_selection") is not False:
            raise ValueError(f"runtime selection leakage guard failed for {key}")
        fingerprint = (
            payload.get("split_metadata", {})
            .get("split_fingerprint", {})
            .get("combined")
        )
        if not fingerprint:
            raise ValueError(f"missing split fingerprint for {key}")
        reports = payload.get("reports")
        if not isinstance(reports, dict) or not reports:
            raise ValueError(f"missing reports mapping for {key}")
        observed_methods = set(reports)
        if method_set is None:
            method_set = observed_methods
        elif observed_methods != method_set:
            raise ValueError(
                f"report method set mismatch for {key}: "
                f"missing={sorted(method_set - observed_methods)}, "
                f"extra={sorted(observed_methods - method_set)}"
            )
        if final_method not in observed_methods:
            raise ValueError(f"final method missing for {key}")
        normalized = {
            method: normalized_report(report, method, key)
            for method, report in reports.items()
        }
        selected = normalized_report(payload.get("selected_report"), final_method, key)
        if any(
            not np.isclose(selected[metric], normalized[final_method][metric], atol=1e-12)
            for metric in METRICS
        ):
            raise ValueError(f"selected report mismatch for {key}")
        rows.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed": seed,
                "split_fingerprint": str(fingerprint),
                "reports": normalized,
            }
        )
        grouped[(suite, scenario)].add(seed)
        source_hashes.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )

    if not rows or method_set is None:
        raise ValueError(f"no metrics found under {root}")
    if len(grouped) != expected_scenarios:
        raise ValueError(
            f"scenario coverage mismatch: expected {expected_scenarios}, "
            f"found {len(grouped)}"
        )
    mismatched = {
        f"{suite}/{scenario}": sorted(values)
        for (suite, scenario), values in grouped.items()
        if values != seeds
    }
    if mismatched:
        raise ValueError(
            f"seed coverage mismatch: expected {sorted(seeds)}, observed {mismatched}"
        )
    combined_source_hash = hashlib.sha256(
        json.dumps(source_hashes, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return rows, {
        "passes": True,
        "run_count": len(rows),
        "scenario_count": len(grouped),
        "seeds": sorted(seeds),
        "method_count": len(method_set),
        "methods": sorted(method_set),
        "artifact_checks": len(rows) * len(REQUIRED_ARTIFACTS),
        "split_fingerprint_checks": len(rows),
        "runtime_selection_uses_unknown_or_test_labels": False,
        "source_metrics_combined_sha256": combined_source_hash,
        "source_metrics": source_hashes,
    }


def scenario_means(rows: list[dict[str, object]]) -> dict[str, dict[str, dict[str, float]]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[f"{row['suite']}/{row['scenario']}"] .append(row)
    methods = sorted(rows[0]["reports"])
    return {
        scenario: {
            method: {
                metric: float(
                    np.mean([row["reports"][method][metric] for row in items])
                )
                for metric in METRICS
            }
            for method in methods
        }
        for scenario, items in sorted(grouped.items())
    }


def aggregate_methods(
    blocks: dict[str, dict[str, dict[str, float]]],
    included_scenarios: set[str] | None = None,
) -> dict[str, dict[str, float]]:
    scenarios = sorted(included_scenarios or set(blocks))
    methods = sorted(next(iter(blocks.values())))
    return {
        method: {
            metric: float(np.mean([blocks[s][method][metric] for s in scenarios]))
            for metric in METRICS
        }
        for method in methods
    }


def candidate_is_eligible(
    candidate: dict[str, float],
    reference: dict[str, float],
    tolerance: float,
) -> bool:
    return bool(
        candidate["known_macro_f1"] >= reference["known_macro_f1"] - 1e-12
        and candidate["unknown_aupr"] >= reference["unknown_aupr"] - tolerance
        and candidate["unknown_fpr95"] <= reference["unknown_fpr95"] + tolerance
        and candidate["oscr"] >= reference["oscr"] - tolerance
    )


def choose_candidate(
    means: dict[str, dict[str, float]], final_method: str, tolerance: float
) -> tuple[str, list[str]]:
    reference = means[final_method]
    eligible = sorted(
        method
        for method, values in means.items()
        if candidate_is_eligible(values, reference, tolerance)
    )
    if not eligible:
        raise ValueError("no candidate passes the multi-metric safety gate")
    selected = min(
        eligible,
        key=lambda method: (
            -means[method]["unknown_auroc"],
            -means[method]["unknown_aupr"],
            means[method]["unknown_fpr95"],
            -means[method]["oscr"],
            method,
        ),
    )
    return selected, eligible


def pareto_frontier(means: dict[str, dict[str, float]]) -> list[str]:
    def oriented(values: dict[str, float]) -> np.ndarray:
        return np.asarray(
            [
                -values[metric] if metric in LOWER_IS_BETTER else values[metric]
                for metric in UNKNOWN_METRICS
            ],
            dtype=np.float64,
        )

    vectors = {method: oriented(values) for method, values in means.items()}
    frontier = []
    for method, vector in vectors.items():
        dominated = any(
            other != method
            and np.all(other_vector >= vector - 1e-12)
            and np.any(other_vector > vector + 1e-12)
            for other, other_vector in vectors.items()
        )
        if not dominated:
            frontier.append(method)
    return sorted(frontier)


def screen(
    blocks: dict[str, dict[str, dict[str, float]]],
    final_method: str,
    tolerance: float,
) -> dict[str, object]:
    means = aggregate_methods(blocks)
    selected, eligible = choose_candidate(means, final_method, tolerance)
    methods = sorted(means)
    ranks: dict[str, dict[str, float]] = {method: {} for method in methods}
    for metric in UNKNOWN_METRICS:
        values = np.asarray([means[m][metric] for m in methods], dtype=np.float64)
        rank_values = rankdata(values if metric in LOWER_IS_BETTER else -values)
        for method, rank_value in zip(methods, rank_values):
            ranks[method][metric] = float(rank_value)
    table = []
    reference = means[final_method]
    for method in methods:
        row = {
            "method": method,
            **means[method],
            "mean_unknown_metric_rank": float(
                np.mean([ranks[method][metric] for metric in UNKNOWN_METRICS])
            ),
            "metric_ranks": ranks[method],
            "passes_safety_gate": method in eligible,
            "versus_final": {
                metric: (
                    (reference[metric] - means[method][metric])
                    if metric in LOWER_IS_BETTER
                    else (means[method][metric] - reference[metric])
                )
                for metric in METRICS
            },
        }
        table.append(row)
    table.sort(
        key=lambda row: (
            row["mean_unknown_metric_rank"],
            -row["unknown_auroc"],
            row["method"],
        )
    )

    loso_rows = []
    selected_paths: Counter[str] = Counter()
    all_scenarios = set(blocks)
    for held_out in sorted(blocks):
        train_means = aggregate_methods(blocks, all_scenarios - {held_out})
        path, train_eligible = choose_candidate(train_means, final_method, tolerance)
        selected_paths[path] += 1
        held_out_candidate = blocks[held_out][path]
        held_out_reference = blocks[held_out][final_method]
        loso_rows.append(
            {
                "held_out_scenario": held_out,
                "selected_method": path,
                "eligible_method_count": len(train_eligible),
                "oriented_deltas_vs_final": {
                    metric: (
                        held_out_reference[metric] - held_out_candidate[metric]
                        if metric in LOWER_IS_BETTER
                        else held_out_candidate[metric] - held_out_reference[metric]
                    )
                    for metric in UNKNOWN_METRICS
                },
            }
        )
    return {
        "status": "development_only_requires_independent_confirmation",
        "selection_rule": {
            "primary": "maximize_scenario_mean_unknown_auroc",
            "known_macro_f1_nonregression": 0.0,
            "unknown_aupr_nonregression_tolerance": tolerance,
            "unknown_fpr95_raw_regression_tolerance": tolerance,
            "oscr_nonregression_tolerance": tolerance,
            "tie_break": [
                "higher_unknown_aupr",
                "lower_unknown_fpr95",
                "higher_oscr",
                "lexical_method_name",
            ],
        },
        "selected_candidate": selected,
        "eligible_methods": eligible,
        "pareto_frontier": pareto_frontier(means),
        "method_table": table,
        "loso": {
            "selected_paths": dict(sorted(selected_paths.items())),
            "folds": loso_rows,
        },
    }


def build_manifest(
    validation: dict[str, object],
    screening: dict[str, object],
    confirmation_seeds: set[int],
) -> dict[str, object]:
    core = {
        "schema_version": "edge_fixed_risk_candidate_manifest_v1",
        "status": "frozen_unconfirmed",
        "selected_candidate": screening["selected_candidate"],
        "selection_rule": screening["selection_rule"],
        "development_seeds": validation["seeds"],
        "confirmation_seeds": sorted(confirmation_seeds),
        "development_scenario_count": validation["scenario_count"],
        "development_method_count": validation["method_count"],
        "source_metrics_combined_sha256": validation[
            "source_metrics_combined_sha256"
        ],
        "candidate_runtime_selection_uses_unknown_or_test_labels": False,
        "development_candidate_screening_uses_test_unknown_labels": True,
        "confirmation_labels_must_remain_unseen_until_manifest_is_frozen": True,
    }
    digest = hashlib.sha256(
        json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {**core, "manifest_sha256": digest}


def markdown(report: dict[str, object]) -> str:
    validation = report["validation"]
    screening = report["screening"]
    manifest = report["candidate_manifest"]
    lines = [
        "# Edge fixed-risk candidate screening",
        "",
        f"Development runs: {validation['run_count']}; scenarios: "
        f"{validation['scenario_count']}; fixed risks: {validation['method_count']}.",
        f"Selected candidate: `{screening['selected_candidate']}`.",
        f"Status: `{manifest['status']}`; manifest SHA-256: "
        f"`{manifest['manifest_sha256']}`.",
        "Development test unknown labels are used only for candidate screening; "
        "the reserved confirmation seeds must remain unseen.",
        "",
        "| Rank | Method | Gate | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean metric rank |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for index, row in enumerate(screening["method_table"][:15], start=1):
        lines.append(
            f"| {index} | {row['method']} | "
            f"{'PASS' if row['passes_safety_gate'] else 'FAIL'} | "
            f"{row['known_macro_f1']:.6f} | {row['unknown_auroc']:.6f} | "
            f"{row['unknown_aupr']:.6f} | {row['unknown_fpr95']:.6f} | "
            f"{row['oscr']:.6f} | {row['mean_unknown_metric_rank']:.2f} |"
        )
    lines.extend(
        [
            "",
            "## Stability",
            "",
            f"Leave-one-scenario-out selected paths: `{screening['loso']['selected_paths']}`.",
            f"Pareto frontier: `{screening['pareto_frontier']}`.",
            "",
            "This screen is exploratory development evidence, not an independent "
            "confirmation result.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_arguments()
    seeds = {int(value) for value in args.seeds.split(",") if value.strip()}
    confirmation_seeds = {
        int(value) for value in args.confirmation_seeds.split(",") if value.strip()
    }
    if not seeds or not confirmation_seeds:
        raise ValueError("development and confirmation seeds are required")
    if seeds & confirmation_seeds:
        raise ValueError("development and confirmation seeds must be disjoint")
    rows, validation = load_matrix(
        Path(args.root),
        seeds,
        args.expected_scenarios,
        args.final_method,
        args.expected_risk_policy,
    )
    blocks = scenario_means(rows)
    screening = screen(blocks, args.final_method, args.nonregression_tolerance)
    manifest = build_manifest(validation, screening, confirmation_seeds)
    report = {
        "schema_version": "edge_fixed_risk_screen_v1",
        "root": args.root,
        "validation": validation,
        "screening": screening,
        "candidate_manifest": manifest,
    }
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "screening.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "candidate_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "screening.md").write_text(markdown(report), encoding="utf-8")
    print(json.dumps({"validation": validation, "manifest": manifest}, indent=2))


if __name__ == "__main__":
    main()
