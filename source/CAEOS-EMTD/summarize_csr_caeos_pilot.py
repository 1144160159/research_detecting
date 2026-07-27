from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from scipy.stats import beta

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_caeos_design import FAMILIES


DIRECTED_METRICS = (
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def clopper_pearson_upper(
    successes: int, trials: int, confidence: float = 0.95
) -> float:
    if not 0 <= successes <= trials or trials <= 0:
        raise ValueError("valid positive binomial counts required")
    if successes == trials:
        return 1.0
    return float(beta.ppf(confidence, successes + 1, trials - successes))


def clean_admission(
    design: Dict[str, Any],
    capture_paths: List[Path],
) -> Dict[str, Any]:
    if (
        design.get("schema_version")
        not in {
            "strict_v4_csr_caeos_design_v3",
            "strict_v4_csr_caeos_design_v4",
        }
        or design.get("manifest_sha256") != canonical_hash(design)
    ):
        raise ValueError("canonical CSR v3 or v4 design required")
    expected = {
        (suite, scenario)
        for suite, scenarios in design["development"]["scenarios"].items()
        for scenario in scenarios
    }
    rows = []
    observed = set()
    for path in capture_paths:
        capture = load_json(path)
        if (
            capture.get("schema_version")
            != "strict_v4_csr_caeos_runtime_capture_v1"
            or capture.get("state") != "complete"
            or capture.get("algorithm") != "csr_caeos_v1"
            or capture.get("roundtrip", {}).get("passes") is not True
            or capture.get("test_effect_metrics_computed") is not False
        ):
            raise ValueError(f"invalid CSR capture: {path}")
        identity = (
            str(capture["task"]["suite"]),
            str(capture["task"]["scenario"]),
        )
        if identity in observed:
            raise ValueError("duplicate CSR capture identity")
        observed.add(identity)
        profile = capture.get("safety_profile", {})
        if (
            profile.get("schema_version")
            != "strict_v4_csr_known_validation_safety_profile_v1"
            or profile.get("test_arrays_read") != []
            or profile.get(
                "unknown_or_test_labels_used_for_calibration"
            )
            is not False
        ):
            raise ValueError("invalid CSR clean safety profile")
        safety_count = int(profile["partition"]["safety_count"])
        missing = int(profile["missing_active_count"])
        nonmissing_trials = safety_count - missing
        nonmissing_active = int(profile["active_count"]) - missing
        upper = clopper_pearson_upper(
            nonmissing_active, nonmissing_trials
        )
        row = {
            "suite": identity[0],
            "scenario": identity[1],
            "safety_count": safety_count,
            "nonmissing_count": nonmissing_trials,
            "nonmissing_active_count": nonmissing_active,
            "nonmissing_active_rate": float(
                nonmissing_active / nonmissing_trials
            ),
            "nonmissing_active_rate_one_sided_95pct_upper": upper,
            "prediction_array_equal_pairwise": bool(
                profile["prediction_array_equal_pairwise"]
            ),
            "probability_max_absolute_difference": float(
                profile["probability_max_absolute_difference"]
            ),
            "inactive_risk_max_absolute_difference": float(
                profile["inactive_risk_max_absolute_difference"]
            ),
            "clean_delta": float(profile["clean_delta"]),
            "capture_manifest_file_sha256": file_hash(path),
        }
        rows.append(row)
    if observed != expected or len(rows) != 14:
        raise ValueError(
            f"CSR capture universe mismatch: missing={len(expected-observed)} "
            f"extra={len(observed-expected)}"
        )
    gate = design["development"]["clean_gate"]
    checks = {
        "all_14_captures_complete": True,
        "prediction_array_equal_pairwise": all(
            row["prediction_array_equal_pairwise"] for row in rows
        ),
        "probability_max_absolute_difference": max(
            row["probability_max_absolute_difference"] for row in rows
        )
        <= float(gate["probability_max_absolute_difference"]) + 1e-12,
        "inactive_risk_max_absolute_difference": max(
            row["inactive_risk_max_absolute_difference"] for row in rows
        )
        <= float(
            gate["inactive_nonmissing_risk_max_absolute_difference"]
        )
        + 1e-12,
        "known_macro_f1_exact_pairwise": all(
            abs(row["clean_delta"]) <= 1e-12 for row in rows
        ),
        "safety_nonmissing_activation_upper": max(
            row[
                "nonmissing_active_rate_one_sided_95pct_upper"
            ]
            for row in rows
        )
        <= float(
            gate[
                "safety_nonmissing_activation_rate_one_sided_95pct_upper_maximum"
            ]
        )
        + 1e-12,
        "zero_unknown_or_test_labels_used_for_calibration_or_selection": True,
    }
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_csr_caeos_clean_admission_v1",
        "state": "complete_known_validation_only",
        "design_manifest_sha256": design["manifest_sha256"],
        "capture_count": len(rows),
        "rows": sorted(
            rows, key=lambda row: (row["suite"], row["scenario"])
        ),
        "checks": checks,
        "passes": all(checks.values()),
        "test_effect_metrics_read": False,
        "unknown_or_test_labels_used": False,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def directed_delta(
    candidate: Dict[str, Any],
    pairwise: Dict[str, Any],
    metric: str,
) -> float:
    if metric == "unknown_fpr95":
        return float(pairwise[metric]) - float(candidate[metric])
    return float(candidate[metric]) - float(pairwise[metric])


def summarize(
    design: Dict[str, Any],
    admission: Dict[str, Any],
    evaluation_paths: List[Path],
) -> Dict[str, Any]:
    if (
        admission.get("schema_version")
        != "strict_v4_csr_caeos_clean_admission_v1"
        or admission.get("manifest_sha256") != canonical_hash(admission)
        or admission.get("design_manifest_sha256")
        != design["manifest_sha256"]
        or admission.get("passes") is not True
    ):
        raise ValueError("passing canonical CSR clean admission required")
    expected = {
        (suite, scenario, condition)
        for suite, scenarios in design["development"]["scenarios"].items()
        for scenario in scenarios
        for condition in design["development"]["conditions"]
    }
    evaluations: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    hashes = {}
    for path in evaluation_paths:
        value = load_json(path)
        if (
            value.get("schema_version")
            != "strict_v4_csr_caeos_pilot_evaluation_v1"
            or value.get("manifest_sha256") != canonical_hash(value)
            or value.get("design_manifest_sha256")
            != design["manifest_sha256"]
            or value.get("state") != "complete"
        ):
            raise ValueError(f"invalid CSR evaluation: {path}")
        identity = (
            str(value["suite"]),
            str(value["scenario"]),
            str(value["condition"]),
        )
        if identity in evaluations:
            raise ValueError("duplicate CSR evaluation identity")
        route = value.get("routing", {})
        if not (
            route.get("prediction_exactly_pairwise_all_rows") is True
            and route.get("probability_exactly_pairwise_all_rows") is True
            and route.get("risk_monotone_not_below_pairwise") is True
            and route.get("inactive_risk_exactly_pairwise") is True
            and route.get("unknown_or_test_labels_used") is False
        ):
            raise ValueError("CSR risk-only routing contract failed")
        evaluations[identity] = value
        hashes["/".join(identity)] = file_hash(path)
    if set(evaluations) != expected or len(evaluations) != 84:
        raise ValueError(
            f"CSR evaluation universe mismatch: "
            f"missing={len(expected-set(evaluations))} "
            f"extra={len(set(evaluations)-expected)}"
        )

    clean_exact = []
    deltas = []
    for identity, value in sorted(evaluations.items()):
        suite, scenario, condition = identity
        candidate = value["candidate_report"]
        pairwise = value["pairwise_report"]
        clean_exact.append(
            abs(
                float(candidate["known_macro_f1"])
                - float(pairwise["known_macro_f1"])
            )
            <= 1e-12
        )
        if condition == "clean":
            continue
        for metric in DIRECTED_METRICS:
            deltas.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "family": condition,
                    "metric": metric,
                    "directed_delta": directed_delta(
                        candidate, pairwise, metric
                    ),
                }
            )

    overall = {}
    suite_means = {}
    family_means = {}
    for metric in DIRECTED_METRICS:
        values = [
            row["directed_delta"]
            for row in deltas
            if row["metric"] == metric
        ]
        overall[metric] = float(np.mean(values))
        suite_means[metric] = {}
        for suite in sorted(design["development"]["scenarios"]):
            selected = [
                row["directed_delta"]
                for row in deltas
                if row["metric"] == metric and row["suite"] == suite
            ]
            suite_means[metric][suite] = float(np.mean(selected))
        family_means[metric] = {}
        for family in FAMILIES:
            selected = [
                row["directed_delta"]
                for row in deltas
                if row["metric"] == metric and row["family"] == family
            ]
            family_means[metric][family] = float(np.mean(selected))
    suite_nonnegative_count = {
        metric: sum(
            value >= -1e-12
            for value in suite_means[metric].values()
        )
        for metric in DIRECTED_METRICS
    }
    family_composite = {
        family: float(
            np.mean(
                [
                    family_means[metric][family]
                    for metric in DIRECTED_METRICS
                ]
            )
        )
        for family in FAMILIES
    }
    gate = design["development"]["robustness_gate"]
    checks = {
        "all_84_evaluations_complete": True,
        "known_macro_f1_exact_pairwise_all_conditions": all(clean_exact),
        "overall_directed_means_strictly_positive": all(
            overall[metric] > 0.0 for metric in DIRECTED_METRICS
        ),
        "at_least_5_of_7_suites_nonnegative_each_metric": all(
            suite_nonnegative_count[metric]
            >= int(gate["suite_nonnegative_count_minimum"])
            for metric in DIRECTED_METRICS
        ),
        "no_family_metric_regression_over_limit": all(
            family_means[metric][family]
            >= -float(gate["each_family_metric_regression_maximum"])
            - 1e-12
            for metric in DIRECTED_METRICS
            for family in FAMILIES
        ),
        "modality_missing_composite_improves": (
            family_composite["modality_missing"] > 0.0
        ),
        "gaussian_drift_composite_improves": (
            family_composite["gaussian_drift"] > 0.0
        ),
        "clean_admission_passes": True,
        "zero_unknown_or_test_labels_used_for_routing_or_selection": True,
    }
    value = {
        "schema_version": "strict_v4_csr_caeos_pilot_summary_v1",
        "state": "complete",
        "algorithm": "csr_caeos_v1",
        "design_manifest_sha256": design["manifest_sha256"],
        "clean_admission_manifest_sha256": admission["manifest_sha256"],
        "evaluation_count": len(evaluations),
        "evaluation_file_sha256": hashes,
        "overall_directed_mean": overall,
        "suite_directed_mean": suite_means,
        "suite_nonnegative_count": suite_nonnegative_count,
        "family_directed_mean": family_means,
        "family_composite_directed_mean": family_composite,
        "checks": checks,
        "passes": all(checks.values()),
        "expand_to_full102": all(checks.values()),
        "claim_boundary": {
            "pilot_success_establishes_sota": False,
            "full102_external_safety_efficiency_still_required": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    clean_parser = subparsers.add_parser("clean-admission")
    clean_parser.add_argument("--design", type=Path, required=True)
    clean_parser.add_argument("--capture-root", type=Path, required=True)
    clean_parser.add_argument("--output", type=Path, required=True)
    summary_parser = subparsers.add_parser("summary")
    summary_parser.add_argument("--design", type=Path, required=True)
    summary_parser.add_argument("--admission", type=Path, required=True)
    summary_parser.add_argument("--evaluation-root", type=Path, required=True)
    summary_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "clean-admission":
        value = clean_admission(
            load_json(args.design),
            sorted(args.capture_root.rglob("capture_manifest.json")),
        )
    else:
        value = summarize(
            load_json(args.design),
            load_json(args.admission),
            sorted(args.evaluation_root.rglob("evaluation.json")),
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
