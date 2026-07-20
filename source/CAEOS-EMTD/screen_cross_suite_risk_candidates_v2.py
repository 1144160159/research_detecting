from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from screen_cross_suite_risk_candidates import (
    DEFAULT_SUITES,
    REFERENCE,
    canonical_manifest_hash,
    load_development_blocks,
)
from screen_edge_risk_candidates import (
    METRICS,
    aggregate_methods,
    candidate_is_eligible,
)


UNKNOWN_METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")


def parse_seed_root(value: str) -> tuple[int, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("seed root must use SEED=PATH")
    seed_text, path = value.split("=", 1)
    try:
        seed = int(seed_text)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"invalid seed: {seed_text!r}") from error
    if not path:
        raise argparse.ArgumentTypeError("seed root path is empty")
    return seed, Path(path)


def mean_blocks(
    seed_blocks: dict[int, dict[str, dict[str, dict[str, float]]]],
    seeds: set[int],
) -> dict[str, dict[str, dict[str, float]]]:
    if not seeds:
        raise ValueError("cannot aggregate an empty seed set")
    first = seed_blocks[min(seeds)]
    scenarios = set(first)
    method_sets: list[set[str]] = []
    for seed in seeds:
        blocks = seed_blocks[seed]
        if set(blocks) != scenarios:
            raise ValueError(f"scenario set mismatch for seed {seed}")
        seed_methods = set(next(iter(blocks.values())))
        if any(set(blocks[scenario]) != seed_methods for scenario in scenarios):
            raise ValueError(f"method set mismatch for seed {seed}")
        method_sets.append(seed_methods)
    methods = set.intersection(*method_sets)
    if REFERENCE not in methods or len(methods) < 2:
        raise ValueError("common method intersection is incomplete")
    return {
        scenario: {
            method: {
                metric: sum(
                    seed_blocks[seed][scenario][method][metric] for seed in seeds
                )
                / len(seeds)
                for metric in METRICS
            }
            for method in sorted(methods)
        }
        for scenario in sorted(scenarios)
    }


def oriented_delta(
    candidate: dict[str, float], reference: dict[str, float], metric: str
) -> float:
    raw = candidate[metric] - reference[metric]
    return -raw if metric == "unknown_fpr95" else raw


def robust_screen(
    seed_blocks: dict[int, dict[str, dict[str, dict[str, float]]]],
    tolerance: float,
) -> dict[str, object]:
    seeds = set(seed_blocks)
    combined_blocks = mean_blocks(seed_blocks, seeds)
    overall = aggregate_methods(combined_blocks)
    if REFERENCE not in overall:
        raise ValueError("reference method is absent")
    reference = overall[REFERENCE]
    rows: list[dict[str, object]] = []
    for method in sorted(overall):
        if method == REFERENCE:
            continue
        values = overall[method]
        overall_eligible = candidate_is_eligible(values, reference, tolerance)
        fold_deltas: dict[int, dict[str, float]] = {}
        fold_safety: dict[int, bool] = {}
        for held_out in sorted(seeds):
            fold_blocks = mean_blocks(seed_blocks, seeds - {held_out})
            fold_means = aggregate_methods(fold_blocks)
            fold_candidate = fold_means[method]
            fold_reference = fold_means[REFERENCE]
            fold_deltas[held_out] = {
                metric: oriented_delta(fold_candidate, fold_reference, metric)
                for metric in METRICS
            }
            fold_safety[held_out] = candidate_is_eligible(
                fold_candidate, fold_reference, tolerance
            )
        auroc_folds = [item["unknown_auroc"] for item in fold_deltas.values()]
        robust_eligible = bool(
            overall_eligible
            and all(fold_safety.values())
            and min(auroc_folds) > 0.0
        )
        rows.append(
            {
                "method": method,
                "overall_metrics": values,
                "overall_oriented_deltas": {
                    metric: oriented_delta(values, reference, metric)
                    for metric in METRICS
                },
                "leave_one_seed_out_oriented_deltas": fold_deltas,
                "leave_one_seed_out_safety": fold_safety,
                "minimum_loso_auroc_improvement": min(auroc_folds),
                "maximum_loso_auroc_improvement": max(auroc_folds),
                "overall_eligible": overall_eligible,
                "robust_eligible": robust_eligible,
            }
        )
    eligible = [row for row in rows if row["robust_eligible"]]
    if eligible:
        selected_row = min(
            eligible,
            key=lambda row: (
                -float(row["minimum_loso_auroc_improvement"]),
                -float(row["overall_oriented_deltas"]["unknown_auroc"]),
                -float(row["overall_oriented_deltas"]["unknown_aupr"]),
                -float(row["overall_oriented_deltas"]["unknown_fpr95"]),
                -float(row["overall_oriented_deltas"]["oscr"]),
                str(row["method"]),
            ),
        )
        selected = str(selected_row["method"])
        status = "robust_candidate_selected"
    else:
        selected = REFERENCE
        status = "no_candidate_passes_robust_seed_gate"
    return {
        "status": status,
        "selected_candidate": selected,
        "development_seeds": sorted(seeds),
        "scenario_count": len(combined_blocks),
        "method_count": len(overall),
        "robust_eligible_methods": sorted(str(row["method"]) for row in eligible),
        "selection_rule": {
            "primary": "maximize_minimum_leave_one_seed_out_unknown_auroc_improvement",
            "all_leave_one_seed_out_auroc_improvements_must_be_positive": True,
            "overall_and_each_leave_one_seed_out_safety_required": True,
            "known_macro_f1_nonregression": 0.0,
            "unknown_aupr_nonregression_tolerance": tolerance,
            "unknown_fpr95_raw_regression_tolerance": tolerance,
            "oscr_nonregression_tolerance": tolerance,
        },
        "method_table": rows,
    }


def validate_previous_confirmation(path: Path, development_seeds: set[int]) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "cross_suite_fixed_report_confirmation_v1":
        raise ValueError("unexpected previous confirmation schema")
    decision = payload.get("frozen_confirmation_decision")
    if not isinstance(decision, dict) or decision.get("passes") is not False:
        raise ValueError("previous confirmation did not fail as required for v2 development")
    validation = payload.get("validation")
    if not isinstance(validation, dict):
        raise ValueError("previous confirmation validation is missing")
    previous_seeds = {int(seed) for seed in validation.get("expected_seeds", [])}
    if not previous_seeds < development_seeds:
        raise ValueError("previous confirmation seeds are not included in v2 development")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest(
    screenings: dict[str, dict[str, object]],
    development_seeds: set[int],
    confirmation_seeds: set[int],
    source_hash: str,
    previous_confirmation_sha: str,
) -> dict[str, object]:
    if not confirmation_seeds or development_seeds & confirmation_seeds:
        raise ValueError("development and confirmation seeds must be nonempty and disjoint")
    selected = {
        suite: result["selected_candidate"] for suite, result in sorted(screenings.items())
    }
    manifest: dict[str, object] = {
        "schema_version": "cross_suite_fixed_risk_candidate_manifest_v2",
        "status": "frozen_unconfirmed",
        "frozen_before_confirmation": True,
        "selected_suite_risks": selected,
        "reference_policy": REFERENCE,
        "selection_rules": {
            suite: result["selection_rule"] for suite, result in sorted(screenings.items())
        },
        "development_seeds": sorted(development_seeds),
        "development_seed": min(development_seeds),
        "development_scenario_count": sum(DEFAULT_SUITES.values()),
        "confirmation_seeds": sorted(confirmation_seeds),
        "development_source_metrics_combined_sha256": source_hash,
        "previous_failed_confirmation_sha256": previous_confirmation_sha,
        "development_candidate_screening_uses_test_unknown_labels": True,
        "runtime_policy_uses_unknown_or_test_labels": False,
        "runtime_policy": (
            "fixed risk selected by known suite identity; no per-task validation, "
            "unknown label or test label routing"
        ),
        "confirmation_gate": {
            "unit": "scenario mean across new confirmation seeds",
            "combined_suites": ["nf_cse", "ustc_tfc2016"],
            "unknown_auroc_mean_improvement_required": True,
            "unknown_auroc_scenario_bootstrap_ci_lower_gt_zero": True,
            "unknown_aupr_nonregression_tolerance": 0.01,
            "unknown_fpr95_oriented_nonregression_tolerance": 0.01,
            "oscr_nonregression_tolerance": 0.01,
            "each_suite_all_four_oriented_means_positive": True,
            "fallback": "retain current confirmed suite policy",
        },
    }
    manifest["manifest_sha256"] = canonical_manifest_hash(manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Freeze robust cross-suite candidates from multiple development seeds"
    )
    parser.add_argument("--seed-root", action="append", required=True)
    parser.add_argument("--previous-confirmation", required=True)
    parser.add_argument("--confirmation-seeds", default="103,107,109,113")
    parser.add_argument("--nonregression-tolerance", type=float, default=0.01)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    seed_roots = dict(parse_seed_root(value) for value in args.seed_root)
    if len(seed_roots) != len(args.seed_root):
        raise ValueError("duplicate development seed root")
    confirmation_seeds = {
        int(value) for value in args.confirmation_seeds.split(",") if value.strip()
    }
    all_seed_blocks: dict[str, dict[int, dict[str, dict[str, dict[str, float]]]]] = {
        suite: {} for suite in DEFAULT_SUITES
    }
    validations = []
    source_hashes = []
    for seed, root in sorted(seed_roots.items()):
        blocks, validation = load_development_blocks(root, DEFAULT_SUITES, seed)
        validations.append(validation)
        source_hashes.append(
            {"seed": seed, "sha256": validation["source_metrics_combined_sha256"]}
        )
        for suite in DEFAULT_SUITES:
            all_seed_blocks[suite][seed] = blocks[suite]
    development_seeds = set(seed_roots)
    previous_sha = validate_previous_confirmation(
        Path(args.previous_confirmation), development_seeds
    )
    screenings = {
        suite: robust_screen(all_seed_blocks[suite], args.nonregression_tolerance)
        for suite in DEFAULT_SUITES
    }
    combined_source_hash = hashlib.sha256(
        json.dumps(source_hashes, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    manifest = build_manifest(
        screenings,
        development_seeds,
        confirmation_seeds,
        combined_source_hash,
        previous_sha,
    )
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "screening.json").write_text(
        json.dumps(
            {"validations": validations, "screenings": screenings},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (output / "candidate_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "selected_suite_risks": manifest["selected_suite_risks"],
                "manifest_sha256": manifest["manifest_sha256"],
                "robust_eligible_methods": {
                    suite: report["robust_eligible_methods"]
                    for suite, report in screenings.items()
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
