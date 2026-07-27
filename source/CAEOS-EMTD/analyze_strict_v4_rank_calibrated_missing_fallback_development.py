from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from analyze_strict_v4_missing_aware_fallback_development import (
    CANDIDATE_RISK,
    METRICS,
    degradation,
    report_metrics,
    summarize,
)
from audit_strict_v4_postselection_corruption_suite_gate import (
    load,
    wrapper_record_hash,
)
from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from run_strict_v4_postselection_corruption import build_tasks, task_key


RC_MAF = "rank_calibrated_missing_aware_fallback_v1"


def development_report(
    labels: np.ndarray,
    unknown: np.ndarray,
    output: dict[str, np.ndarray],
    threshold: float,
) -> dict[str, float]:
    from caeos.hybrid_open_set import evaluate_hybrid_open_set

    result = evaluate_hybrid_open_set(
        labels,
        unknown,
        np.asarray(output["prediction"]),
        np.asarray(output["risk"]),
        float(threshold),
    )
    return {metric: float(result[metric]) for metric in METRICS}


def empirical_quantile_map(
    values: np.ndarray,
    source_reference: np.ndarray,
    target_reference: np.ndarray,
) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    source = np.sort(np.asarray(source_reference, dtype=np.float64))
    target = np.sort(np.asarray(target_reference, dtype=np.float64))
    if (
        values.ndim != 1
        or source.ndim != 1
        or target.ndim != 1
        or source.size < 2
        or target.size < 2
        or not np.all(np.isfinite(values))
        or not np.all(np.isfinite(source))
        or not np.all(np.isfinite(target))
    ):
        raise ValueError("quantile-map inputs must be finite vectors")
    percentiles = (
        np.searchsorted(source, values, side="right") - 0.5
    ) / source.size
    percentiles = np.clip(percentiles, 0.0, 1.0)
    target_grid = (np.arange(target.size) + 0.5) / target.size
    return np.interp(
        percentiles,
        target_grid,
        target,
        left=target[0],
        right=target[-1],
    )


def candidate_output(
    archive: Any, selected_risk: str
) -> tuple[dict[str, np.ndarray], int, bool]:
    required = (
        f"validation_{selected_risk}",
        f"test_{selected_risk}",
        f"validation_{CANDIDATE_RISK}",
        f"test_{CANDIDATE_RISK}",
        "test_any_missing",
        "test_missing_aware_prediction",
        "test_prediction",
    )
    missing = [name for name in required if name not in archive]
    if missing:
        raise ValueError(f"RC-MAF score inputs are missing: {missing}")
    mask = np.asarray(archive["test_any_missing"], dtype=bool)
    incumbent_risk = np.asarray(
        archive[f"test_{selected_risk}"], dtype=np.float64
    )
    incumbent_prediction = np.asarray(
        archive["test_prediction"], dtype=np.int64
    )
    missing_risk = np.asarray(
        archive[f"test_{CANDIDATE_RISK}"], dtype=np.float64
    )
    missing_prediction = np.asarray(
        archive["test_missing_aware_prediction"], dtype=np.int64
    )
    if not (
        mask.ndim == 1
        and incumbent_risk.shape == mask.shape
        and incumbent_prediction.shape == mask.shape
        and missing_risk.shape == mask.shape
        and missing_prediction.shape == mask.shape
    ):
        raise ValueError("RC-MAF test arrays are not aligned")
    mapped = empirical_quantile_map(
        missing_risk,
        np.asarray(
            archive[f"validation_{CANDIDATE_RISK}"],
            dtype=np.float64,
        ),
        np.asarray(
            archive[f"validation_{selected_risk}"],
            dtype=np.float64,
        ),
    )
    risk = np.where(mask, mapped, incumbent_risk)
    prediction = np.where(
        mask, missing_prediction, incumbent_prediction
    )
    exact = bool(
        np.array_equal(risk[~mask], incumbent_risk[~mask])
        and np.array_equal(
            prediction[~mask], incumbent_prediction[~mask]
        )
    )
    return {"risk": risk, "prediction": prediction}, int(mask.sum()), exact


def require(
    value: dict[str, Any], schema: str, label: str
) -> None:
    if (
        value.get("schema_version") != schema
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError(f"invalid {label}")


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
        require(value, schema, label)
    if (
        authority.get("confirmatory_gate", {}).get("passes") is not False
        or suite_audit.get("passes") is not False
    ):
        raise ValueError("development requires completed negative gates")

    candidate: dict[str, dict[str, dict[str, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: {metric: [] for metric in METRICS})
    )
    incumbent: dict[str, dict[str, dict[str, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: {metric: [] for metric in METRICS})
    )
    clean_differences = {metric: [] for metric in METRICS}
    activated_samples = Counter()
    no_missing_exact = True
    observed = 0
    for task in build_tasks(base, coverage):
        if task.tier != "full102":
            continue
        wrapper_path = (
            args.run_root / task_key(task) / "corruption_metrics.json"
        )
        wrapper = load(wrapper_path)
        if (
            wrapper.get("record_sha256") != wrapper_record_hash(wrapper)
            or wrapper.get("validation_passes") is not True
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
        selected = str(clean_metrics["selected_risk"])
        if corrupted_metrics.get("selected_risk") != selected:
            raise ValueError("test-only corruption changed selected risk")
        threshold = float(
            clean_metrics["validation_thresholds"][selected]
        )
        with (
            np.load(
                metrics_path.with_name("scores.npz"),
                allow_pickle=False,
            ) as corrupted_scores,
            np.load(
                clean_path.with_name("scores.npz"),
                allow_pickle=False,
            ) as clean_scores,
        ):
            corrupted_output, corrupted_count, corrupted_exact = (
                candidate_output(corrupted_scores, selected)
            )
            clean_output, clean_count, clean_exact = candidate_output(
                clean_scores, selected
            )
            no_missing_exact = (
                no_missing_exact and corrupted_exact and clean_exact
            )
            activated_samples[task.corruption] += corrupted_count
            activated_samples["clean"] += clean_count
            labels = np.asarray(
                corrupted_scores["test_labels"], dtype=np.int64
            )
            unknown = np.asarray(
                corrupted_scores["test_unknown"], dtype=bool
            )
            clean_labels = np.asarray(
                clean_scores["test_labels"], dtype=np.int64
            )
            clean_unknown = np.asarray(
                clean_scores["test_unknown"], dtype=bool
            )
            corrupted_candidate = development_report(
                labels, unknown, corrupted_output, threshold
            )
            clean_candidate = development_report(
                clean_labels, clean_unknown, clean_output, threshold
            )
        corrupted_incumbent = report_metrics(
            corrupted_metrics["selected_report"]
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
    clean_f1_losses = [
        -value for value in clean_differences["known_macro_f1"]
    ]
    component_gates = {
        "all_510_development_runs_valid": observed == 510,
        "all_no_missing_samples_exactly_preserve_incumbent": (
            no_missing_exact
        ),
        "clean_known_f1_mean_loss_at_most_0_005": (
            float(np.mean(clean_f1_losses)) <= 0.005
        ),
        "clean_known_f1_worst_loss_at_most_0_02": (
            max(clean_f1_losses) <= 0.02
        ),
        "modality_missing_aggregate_gate_passes": result[
            "development_results"
        ]["modality_missing"]["aggregate_passes"],
        "suite_threshold_failures_reduced": (
            result["candidate_suite_threshold_failures"]
            < result["incumbent_suite_threshold_failures"]
        ),
        "modality_missing_all_metric_advantages_positive": all(
            item["candidate_advantage"] > 0.0
            for item in result["development_results"][
                "modality_missing"
            ]["aggregate"].values()
        ),
    }
    admitted = all(component_gates.values())
    result.update(
        {
            "candidate_risk": RC_MAF,
            "schema_version": (
                "strict_v4_rank_calibrated_missing_fallback_"
                "development_analysis_v1"
            ),
            "status": "complete_posthoc_development_only",
            "posthoc_development_only": True,
            "calibration_source": (
                "known_validation_risk_distributions_only"
            ),
            "activation_source": "saved_label_free_test_missing_mask",
            "activated_sample_counts": dict(activated_samples),
            "no_missing_samples_exactly_preserve_incumbent": (
                no_missing_exact
            ),
            "clean_known_f1_mean_loss": float(
                np.mean(clean_f1_losses)
            ),
            "clean_known_f1_worst_loss": max(clean_f1_losses),
            "component_development_gates": component_gates,
            "passes_development_admission": admitted,
            "decision": (
                "admit_rc_maf_to_new_seed_component_confirmation"
                if admitted
                else "retain_rc_maf_as_development_hypothesis_only"
            ),
            "new_seed_confirmation_required": True,
            "validation": {
                "expected_runs": 510,
                "observed_runs": observed,
                "passes": observed == 510,
            },
            "input_manifest_sha256": {
                "base_protocol": base["manifest_sha256"],
                "suite_protocol": protocol["manifest_sha256"],
                "authority_summary": authority["manifest_sha256"],
                "suite_audit": suite_audit["manifest_sha256"],
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
    result["manifest_sha256"] = canonical_hash(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["decision"])


if __name__ == "__main__":
    main()
