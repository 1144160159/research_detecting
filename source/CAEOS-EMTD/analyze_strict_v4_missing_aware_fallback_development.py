from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from audit_strict_v4_postselection_corruption_suite_gate import (
    load,
    wrapper_record_hash,
)
from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from run_strict_v4_postselection_corruption import build_tasks, task_key


CANDIDATE_RISK = "missing_aware_cauchy_modality_support_union"
METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)


def report_metrics(report: dict[str, Any]) -> dict[str, float]:
    values = {metric: float(report[metric]) for metric in METRICS}
    if not all(np.isfinite(value) for value in values.values()):
        raise ValueError("report metrics must be finite")
    return values


def degradation(
    clean: dict[str, float],
    corrupted: dict[str, float],
    metric: str,
) -> float:
    if metric == "unknown_fpr95":
        return corrupted[metric] - clean[metric]
    return clean[metric] - corrupted[metric]


def summarize(
    *,
    protocol: dict[str, Any],
    suite_counts: dict[str, int],
    candidate: dict[str, dict[str, dict[str, list[float]]]],
    incumbent: dict[str, dict[str, dict[str, list[float]]]],
    clean_differences: dict[str, list[float]],
    observed_runs: int,
) -> dict[str, Any]:
    thresholds = protocol["maximum_mean_degradation"]
    families = protocol["corruption_families"]
    candidate_results: dict[str, Any] = {}
    incumbent_failures = Counter()
    candidate_failures = Counter()
    family_improvements: dict[str, dict[str, float]] = {}
    for family in families:
        suite_results: dict[str, Any] = {}
        family_candidate = {metric: [] for metric in METRICS}
        family_incumbent = {metric: [] for metric in METRICS}
        for suite, expected in suite_counts.items():
            metric_results: dict[str, Any] = {}
            for metric in METRICS:
                candidate_values = np.asarray(
                    candidate[family][suite][metric], dtype=np.float64
                )
                incumbent_values = np.asarray(
                    incumbent[family][suite][metric], dtype=np.float64
                )
                if (
                    candidate_values.size != expected
                    or incumbent_values.size != expected
                    or not np.all(np.isfinite(candidate_values))
                    or not np.all(np.isfinite(incumbent_values))
                ):
                    raise ValueError(
                        f"invalid development values: "
                        f"{family}/{suite}/{metric}"
                    )
                candidate_mean = float(candidate_values.mean())
                incumbent_mean = float(incumbent_values.mean())
                limit = float(thresholds[metric])
                candidate_passes = candidate_mean <= limit
                incumbent_passes = incumbent_mean <= limit
                if not candidate_passes:
                    candidate_failures.update(
                        (family, suite, metric, "total")
                    )
                if not incumbent_passes:
                    incumbent_failures.update(
                        (family, suite, metric, "total")
                    )
                metric_results[metric] = {
                    "n_scenarios": expected,
                    "candidate_mean_degradation": candidate_mean,
                    "incumbent_mean_degradation": incumbent_mean,
                    "candidate_advantage": (
                        incumbent_mean - candidate_mean
                    ),
                    "maximum_mean_degradation": limit,
                    "candidate_passes": candidate_passes,
                    "incumbent_passes": incumbent_passes,
                }
                family_candidate[metric].extend(candidate_values.tolist())
                family_incumbent[metric].extend(incumbent_values.tolist())
            suite_results[suite] = metric_results
        aggregate = {}
        improvements = {}
        for metric in METRICS:
            candidate_mean = float(np.mean(family_candidate[metric]))
            incumbent_mean = float(np.mean(family_incumbent[metric]))
            aggregate[metric] = {
                "candidate_mean_degradation": candidate_mean,
                "incumbent_mean_degradation": incumbent_mean,
                "candidate_advantage": incumbent_mean - candidate_mean,
                "maximum_mean_degradation": float(thresholds[metric]),
                "candidate_passes": (
                    candidate_mean <= float(thresholds[metric])
                ),
            }
            improvements[metric] = incumbent_mean - candidate_mean
        family_improvements[family] = improvements
        candidate_results[family] = {
            "aggregate": aggregate,
            "suite_results": suite_results,
            "aggregate_passes": all(
                item["candidate_passes"] for item in aggregate.values()
            ),
        }

    clean_max = max(
        abs(value)
        for values in clean_differences.values()
        for value in values
    )
    incumbent_failed = int(incumbent_failures["total"])
    candidate_failed = int(candidate_failures["total"])
    modality_passes = candidate_results["modality_missing"][
        "aggregate_passes"
    ]
    gates = {
        "all_510_development_runs_valid": observed_runs == 510,
        "clean_input_exact_fallback_all_five_metrics": clean_max <= 1e-12,
        "modality_missing_aggregate_gate_passes": modality_passes,
        "suite_threshold_failures_reduced": (
            candidate_failed < incumbent_failed
        ),
        "modality_missing_all_metric_advantages_positive": all(
            value > 0.0
            for value in family_improvements["modality_missing"].values()
        ),
    }
    admitted = all(gates.values())
    return {
        "candidate_risk": CANDIDATE_RISK,
        "development_results": candidate_results,
        "clean_input_max_absolute_metric_difference": clean_max,
        "incumbent_suite_threshold_failures": incumbent_failed,
        "candidate_suite_threshold_failures": candidate_failed,
        "suite_threshold_failures_reduced_by": (
            incumbent_failed - candidate_failed
        ),
        "development_gates": gates,
        "decision": (
            "admit_missing_aware_fallback_to_new_seed_component_confirmation"
            if admitted
            else "retain_as_development_hypothesis_only"
        ),
        "passes_development_admission": admitted,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--base-protocol", type=Path, required=True)
    parser.add_argument("--suite-protocol", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--authority-summary", type=Path, required=True)
    parser.add_argument("--suite-audit", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project = args.project_root.resolve()
    base, protocol, coverage = (
        load(args.base_protocol),
        load(args.suite_protocol),
        load(args.coverage),
    )
    authority, suite_audit = (
        load(args.authority_summary),
        load(args.suite_audit),
    )
    for value, schema, label in (
        (
            base,
            "strict_v4_postselection_corruption_protocol_v1",
            "base protocol",
        ),
        (
            protocol,
            "strict_v4_postselection_corruption_suite_gate_protocol_v1",
            "suite protocol",
        ),
        (
            coverage,
            "strict_v4_coverage_manifest_v2",
            "coverage",
        ),
        (
            authority,
            "strict_v4_postselection_corruption_summary_v1",
            "authority summary",
        ),
        (
            suite_audit,
            "strict_v4_postselection_corruption_suite_gate_audit_v1",
            "suite audit",
        ),
    ):
        if (
            value.get("schema_version") != schema
            or value.get("manifest_sha256") != canonical_hash(value)
        ):
            raise ValueError(f"invalid {label}")
    if (
        authority.get("confirmatory_gate", {}).get("passes") is not False
        or suite_audit.get("passes") is not False
    ):
        raise ValueError(
            "missing-aware development is only authorized after negative gates"
        )

    tasks = build_tasks(base, coverage)
    candidate: dict[str, dict[str, dict[str, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: {metric: [] for metric in METRICS})
    )
    incumbent: dict[str, dict[str, dict[str, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: {metric: [] for metric in METRICS})
    )
    clean_differences = {metric: [] for metric in METRICS}
    observed = 0
    for task in tasks:
        if task.tier != "full102":
            continue
        wrapper_path = args.run_root / task_key(task) / "corruption_metrics.json"
        wrapper = load(wrapper_path)
        if (
            wrapper.get("record_sha256") != wrapper_record_hash(wrapper)
            or wrapper.get("validation_passes") is not True
            or wrapper.get(
                "unknown_or_test_labels_used_for_generation_fitting_or_selection"
            )
            is not False
            or wrapper.get("task") != task.__dict__
        ):
            raise ValueError(f"invalid wrapper: {wrapper_path}")
        metrics_path = Path(wrapper["metrics_path"])
        clean_path = (
            project
            / base["clean_anchor"]["root"]
            / task.suite
            / f"{task.scenario}_seed7"
            / "metrics.json"
        )
        if (
            file_hash(metrics_path) != wrapper["metrics_sha256"]
            or file_hash(clean_path) != wrapper["clean_metrics_sha256"]
        ):
            raise ValueError(f"metric SHA mismatch: {wrapper_path}")
        corrupted_metrics, clean_metrics = (
            load(metrics_path),
            load(clean_path),
        )
        corrupted_diagnostics = corrupted_metrics.get(
            "missing_aware_diagnostics", {}
        )
        if (
            corrupted_diagnostics.get("uses_unknown_or_test_labels")
            is not False
            or CANDIDATE_RISK
            not in corrupted_metrics.get("validation_thresholds", {})
            or CANDIDATE_RISK not in corrupted_metrics.get("reports", {})
            or CANDIDATE_RISK not in clean_metrics.get("reports", {})
        ):
            raise ValueError(
                f"missing-aware candidate contract failed: {metrics_path}"
            )
        corrupted_candidate = report_metrics(
            corrupted_metrics["reports"][CANDIDATE_RISK]
        )
        corrupted_incumbent = report_metrics(
            corrupted_metrics["selected_report"]
        )
        clean_candidate = report_metrics(
            clean_metrics["reports"][CANDIDATE_RISK]
        )
        clean_incumbent = report_metrics(clean_metrics["selected_report"])
        for metric in METRICS:
            candidate[task.corruption][task.suite][metric].append(
                degradation(
                    clean_candidate, corrupted_candidate, metric
                )
            )
            incumbent[task.corruption][task.suite][metric].append(
                degradation(
                    clean_incumbent, corrupted_incumbent, metric
                )
            )
            clean_differences[metric].append(
                clean_candidate[metric] - clean_incumbent[metric]
            )
        observed += 1

    result = summarize(
        protocol=protocol,
        suite_counts=protocol["suite_scenario_counts"],
        candidate=candidate,
        incumbent=incumbent,
        clean_differences=clean_differences,
        observed_runs=observed,
    )
    result.update(
        {
            "schema_version": (
                "strict_v4_missing_aware_fallback_development_analysis_v1"
            ),
            "status": "complete_posthoc_development_only",
            "development_source": (
                "completed_seed7_postselection_corruption_confirmation"
            ),
            "posthoc_development_only": True,
            "test_labels_used_for_development_scoring_only": True,
            "unknown_or_test_labels_used_by_candidate_routing": False,
            "new_seed_confirmation_required": True,
            "base_protocol_manifest_sha256": base["manifest_sha256"],
            "suite_protocol_manifest_sha256": protocol["manifest_sha256"],
            "authority_summary_manifest_sha256": authority[
                "manifest_sha256"
            ],
            "suite_audit_manifest_sha256": suite_audit[
                "manifest_sha256"
            ],
            "validation": {
                "expected_runs": 510,
                "observed_runs": observed,
                "all_wrappers_and_file_hashes_valid": True,
                "passes": observed == 510,
            },
            "claim_boundary": {
                "cannot_relabel_seed7_as_confirmation": True,
                "cannot_change_existing_negative_robustness_result": True,
                "candidate_is_not_the_final_selected_algorithm": True,
                "fresh_training_and_corruption_seeds_required": True,
            },
        }
    )
    result["analysis_implementation_sha256"] = file_hash(
        Path(__file__).resolve()
    )
    result["input_file_sha256"] = {
        "base_protocol": file_hash(args.base_protocol),
        "suite_protocol": file_hash(args.suite_protocol),
        "coverage": file_hash(args.coverage),
        "authority_summary": file_hash(args.authority_summary),
        "suite_audit": file_hash(args.suite_audit),
    }
    result["manifest_sha256"] = canonical_hash(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["decision"])


if __name__ == "__main__":
    main()
