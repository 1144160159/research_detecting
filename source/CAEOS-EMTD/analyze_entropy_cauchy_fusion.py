from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from analyze_caeos_closr_fusion import (
    FUSION_METHODS,
    REPORT_METRICS,
    empirical_percentile,
    fixed_fusions,
)
from caeos.hybrid_open_set import cauchy_combined_risk, evaluate_hybrid_open_set
from screen_edge_risk_candidates import screen


CAUCHY_ALL_COMPONENTS = (
    "uncertainty",
    "distance",
    "conflict",
    "tree_disagreement",
)
REQUIRED_ARTIFACTS = ("metrics.json", "scores.npz", "evidence_package.npz")
ALL_REPORT_METRICS = REPORT_METRICS + (
    "known_acceptance_rate",
    "unknown_rejection_rate",
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search fixed validation-calibrated entropy/Cauchy fusion risks"
    )
    parser.add_argument("--root", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--seeds", default="7,11,19,23,37")
    parser.add_argument("--confirmation-seeds", default="67,71,73,79")
    parser.add_argument("--expected-scenarios", type=int, default=14)
    parser.add_argument("--known-acceptance", type=float, default=0.95)
    parser.add_argument("--nonregression-tolerance", type=float, default=0.01)
    return parser.parse_args()


def normalized_entropy_risk(
    validation_raw: np.ndarray, values: np.ndarray
) -> np.ndarray:
    validation = np.asarray(validation_raw, dtype=np.float64)
    query = np.asarray(values, dtype=np.float64)
    low, high = np.quantile(validation, [0.05, 0.95])
    if high - low < 1e-8:
        high = low + 1e-8
    return np.clip((query - low) / (high - low), 0.0, 2.0)


def reports_match(
    reconstructed: dict[str, float], recorded: dict[str, object], tolerance: float = 1e-9
) -> bool:
    return all(
        metric in recorded
        and np.isclose(
            float(reconstructed[metric]), float(recorded[metric]), atol=tolerance, rtol=0.0
        )
        for metric in ALL_REPORT_METRICS
    )


def task_report(directory: Path, acceptance: float) -> dict[str, object]:
    metrics = json.loads((directory / "metrics.json").read_text(encoding="utf-8"))
    with np.load(directory / "scores.npz") as scores, np.load(
        directory / "evidence_package.npz"
    ) as evidence:
        unknown = scores["test_unknown"].astype(bool)
        labels = scores["test_labels"]
        prediction = scores["test_prediction"]
        validation_entropy_raw = evidence["validation_component_uncertainty"]
        test_entropy_raw = evidence["test_component_uncertainty"]
        entropy_validation = normalized_entropy_risk(
            validation_entropy_raw, validation_entropy_raw
        )
        entropy_test = normalized_entropy_risk(
            validation_entropy_raw, test_entropy_raw
        )
        validation_tail = {
            name: evidence[f"validation_tail_{name}"]
            for name in CAUCHY_ALL_COMPONENTS
        }
        test_tail = {
            name: evidence[f"test_tail_{name}"] for name in CAUCHY_ALL_COMPONENTS
        }
        cauchy_validation = cauchy_combined_risk(
            validation_tail, CAUCHY_ALL_COMPONENTS
        )
        cauchy_test = cauchy_combined_risk(test_tail, CAUCHY_ALL_COMPONENTS)

        thresholds = metrics.get("validation_thresholds", {})
        entropy_replay = evaluate_hybrid_open_set(
            labels,
            unknown,
            prediction,
            entropy_test,
            float(thresholds["entropy"]),
        )
        cauchy_replay = evaluate_hybrid_open_set(
            labels,
            unknown,
            prediction,
            cauchy_test,
            float(thresholds["cauchy_all"]),
        )
        if not reports_match(entropy_replay, metrics["reports"]["entropy"]):
            raise ValueError(f"entropy replay mismatch under {directory}")
        if not reports_match(cauchy_replay, metrics["reports"]["cauchy_all"]):
            raise ValueError(f"cauchy_all replay mismatch under {directory}")

        entropy_validation_rank = empirical_percentile(
            entropy_validation, entropy_validation
        )
        entropy_test_rank = empirical_percentile(entropy_validation, entropy_test)
        cauchy_validation_rank = empirical_percentile(
            cauchy_validation, cauchy_validation
        )
        cauchy_test_rank = empirical_percentile(cauchy_validation, cauchy_test)
        validation_fusions = fixed_fusions(
            entropy_validation_rank, cauchy_validation_rank
        )
        test_fusions = fixed_fusions(entropy_test_rank, cauchy_test_rank)
        reports = {
            "entropy": {
                metric: float(metrics["reports"]["entropy"][metric])
                for metric in ALL_REPORT_METRICS
            },
            "cauchy_all": {
                metric: float(metrics["reports"]["cauchy_all"][metric])
                for metric in ALL_REPORT_METRICS
            },
        }
        for method in FUSION_METHODS:
            threshold = float(np.quantile(validation_fusions[method], acceptance))
            report = evaluate_hybrid_open_set(
                labels, unknown, prediction, test_fusions[method], threshold
            )
            reports[method] = {
                metric: float(report[metric]) for metric in ALL_REPORT_METRICS
            }
        return {
            "seed": int(metrics["seed"]),
            "reports": reports,
            "endpoint_replay_checks": 2,
            "validation_diagnostics": {
                "rank_correlation": float(
                    np.corrcoef(entropy_validation_rank, cauchy_validation_rank)[0, 1]
                ),
                "mean_absolute_rank_difference": float(
                    np.mean(
                        np.abs(entropy_validation_rank - cauchy_validation_rank)
                    )
                ),
            },
        }


def build_blocks(runs: list[dict[str, object]]) -> dict[str, dict[str, dict[str, float]]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for run in runs:
        grouped[str(run["scenario"])].append(run)
    methods = sorted(runs[0]["reports"])
    return {
        scenario: {
            method: {
                metric: float(
                    np.mean([run["reports"][method][metric] for run in items])
                )
                for metric in REPORT_METRICS
            }
            for method in methods
        }
        for scenario, items in sorted(grouped.items())
    }


def build_manifest(
    screening: dict[str, object],
    development_seeds: set[int],
    confirmation_seeds: set[int],
    source_sha256: str,
) -> dict[str, object]:
    selected = str(screening["selected_candidate"])
    core = {
        "schema_version": "entropy_cauchy_fusion_manifest_v1",
        "status": "frozen_unconfirmed" if selected != "entropy" else "no_fusion_selected",
        "selected_candidate": selected,
        "candidate_family": ["entropy", "cauchy_all", *FUSION_METHODS],
        "endpoint_calibration": "known_validation_empirical_cdf_only",
        "fusion_definitions": {
            "rank_mean": "0.5 * (entropy_rank + cauchy_all_rank)",
            "rank_union": "1 - (1 - entropy_rank) * (1 - cauchy_all_rank)",
            "rank_max": "max(entropy_rank, cauchy_all_rank)",
            "rank_min": "min(entropy_rank, cauchy_all_rank)",
            "rank_cauchy": "equal_weight_cauchy_p_value_combination",
            "rank_bonferroni": "two_test_bonferroni_union",
        },
        "selection_rule": screening["selection_rule"],
        "development_seeds": sorted(development_seeds),
        "confirmation_seeds": sorted(confirmation_seeds),
        "source_artifacts_combined_sha256": source_sha256,
        "analysis_implementation_sha256": hashlib.sha256(
            Path(__file__).read_bytes()
        ).hexdigest(),
        "development_candidate_screening_uses_test_unknown_labels": True,
        "runtime_fusion_uses_unknown_or_test_labels": False,
    }
    digest = hashlib.sha256(
        json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {**core, "manifest_sha256": digest}


def markdown(report: dict[str, object]) -> str:
    screening = report["screening"]
    manifest = report["candidate_manifest"]
    lines = [
        "# Entropy-Cauchy fusion development screen",
        "",
        f"Validated runs: {report['validation']['run_count']}; endpoint replay "
        f"checks: {report['validation']['endpoint_replay_checks']}.",
        f"Selected candidate: `{screening['selected_candidate']}`; status: "
        f"`{manifest['status']}`; manifest SHA-256: `{manifest['manifest_sha256']}`.",
        "",
        "| Rank | Method | Gate | AUROC | AUPR | FPR95 | OSCR | Mean rank |",
        "|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for index, row in enumerate(screening["method_table"], start=1):
        lines.append(
            f"| {index} | {row['method']} | "
            f"{'PASS' if row['passes_safety_gate'] else 'FAIL'} | "
            f"{row['unknown_auroc']:.6f} | {row['unknown_aupr']:.6f} | "
            f"{row['unknown_fpr95']:.6f} | {row['oscr']:.6f} | "
            f"{row['mean_unknown_metric_rank']:.2f} |"
        )
    lines.extend(
        [
            "",
            f"LOSO selected paths: `{screening['loso']['selected_paths']}`.",
            "This is development-only evidence; any frozen fusion requires the "
            "reserved confirmation seeds.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_arguments()
    root = Path(args.root)
    seeds = {int(value) for value in args.seeds.split(",") if value.strip()}
    confirmation_seeds = {
        int(value) for value in args.confirmation_seeds.split(",") if value.strip()
    }
    if not seeds or not confirmation_seeds or seeds & confirmation_seeds:
        raise ValueError("development and disjoint confirmation seeds are required")
    runs = []
    source_hashes = []
    scenario_seeds: dict[str, set[int]] = defaultdict(set)
    for path in sorted(root.glob("*/*/metrics.json")):
        directory = path.parent
        missing = [name for name in REQUIRED_ARTIFACTS if not (directory / name).exists()]
        if missing:
            raise ValueError(f"missing artifacts under {directory}: {missing}")
        run = task_report(directory, args.known_acceptance)
        if run["seed"] not in seeds:
            raise ValueError(f"unexpected seed {run['seed']} under {directory}")
        scenario = f"{directory.parent.name}/{directory.name.rsplit('_seed', 1)[0]}"
        run["scenario"] = scenario
        runs.append(run)
        scenario_seeds[scenario].add(int(run["seed"]))
        for name in REQUIRED_ARTIFACTS:
            artifact = directory / name
            source_hashes.append(
                {
                    "path": artifact.relative_to(root).as_posix(),
                    "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                }
            )
    if len(scenario_seeds) != args.expected_scenarios:
        raise ValueError(
            f"scenario coverage mismatch: expected {args.expected_scenarios}, "
            f"found {len(scenario_seeds)}"
        )
    mismatched = {
        scenario: sorted(observed)
        for scenario, observed in scenario_seeds.items()
        if observed != seeds
    }
    if mismatched:
        raise ValueError(f"seed coverage mismatch: {mismatched}")
    source_sha = hashlib.sha256(
        json.dumps(source_hashes, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    blocks = build_blocks(runs)
    screening = screen(blocks, "entropy", args.nonregression_tolerance)
    manifest = build_manifest(screening, seeds, confirmation_seeds, source_sha)
    report = {
        "schema_version": "entropy_cauchy_fusion_screen_v1",
        "root": args.root,
        "validation": {
            "passes": True,
            "run_count": len(runs),
            "scenario_count": len(scenario_seeds),
            "seeds": sorted(seeds),
            "artifact_checks": len(source_hashes),
            "endpoint_replay_checks": sum(
                int(run["endpoint_replay_checks"]) for run in runs
            ),
            "source_artifacts_combined_sha256": source_sha,
        },
        "screening": screening,
        "candidate_manifest": manifest,
        "runs": runs,
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
    print(json.dumps({"validation": report["validation"], "manifest": manifest}, indent=2))


if __name__ == "__main__":
    main()
