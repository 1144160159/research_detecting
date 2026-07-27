from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import numpy as np

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_caeos_design import FAMILIES
from select_mdr_caeos_weight import load


METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)
LOWER_IS_BETTER = {"unknown_fpr95"}


def degradation(clean: float, corrupted: float, metric: str) -> float:
    if metric in LOWER_IS_BETTER:
        return float(corrupted - clean)
    return float(clean - corrupted)


def mean_records(
    records: Iterable[Tuple[Dict[str, float], Dict[str, float]]]
) -> Dict[str, float]:
    values = list(records)
    if not values:
        raise ValueError("empty MDR aggregation unit")
    return {
        metric: float(
            np.mean(
                [
                    degradation(clean[metric], corrupted[metric], metric)
                    for clean, corrupted in values
                ]
            )
        )
        for metric in METRICS
    }


def summarize(
    design: Dict[str, Any],
    selection: Dict[str, Any],
    evaluation_paths: List[Path],
) -> Dict[str, Any]:
    if (
        design.get("schema_version") != "strict_v4_mdr_caeos_design_v2"
        or design.get("manifest_sha256") != canonical_hash(design)
    ):
        raise ValueError("canonical MDR v2 design required")
    if (
        selection.get("schema_version")
        != "strict_v4_mdr_caeos_weight_selection_v1"
        or selection.get("manifest_sha256") != canonical_hash(selection)
        or selection.get("design_manifest_sha256")
        != design["manifest_sha256"]
    ):
        raise ValueError("invalid MDR weight selection")
    expected = {
        (suite, scenario, condition)
        for suite, scenarios in design["pilot"]["scenarios"].items()
        for scenario in scenarios
        for condition in design["pilot"]["conditions"]
    }
    evaluations: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    file_sha = {}
    for path in evaluation_paths:
        value = load(path)
        if (
            value.get("schema_version")
            != "strict_v4_mdr_caeos_pilot_evaluation_v1"
            or value.get("manifest_sha256") != canonical_hash(value)
            or value.get("design_manifest_sha256")
            != design["manifest_sha256"]
            or float(value.get("capture", {}).get("weight", -1.0))
            != float(selection["selected_weight"])
            or value.get("routing", {}).get(
                "unknown_or_test_labels_used"
            )
            is not False
        ):
            raise ValueError(f"invalid MDR evaluation: {path}")
        identity = (
            value["suite"],
            value["scenario"],
            value["condition"],
        )
        if identity in evaluations:
            raise ValueError(f"duplicate MDR evaluation: {identity}")
        evaluations[identity] = value
        file_sha["/".join(identity)] = file_hash(path)
    if set(evaluations) != expected:
        raise ValueError(
            f"MDR evaluation universe mismatch: "
            f"missing={len(expected-set(evaluations))} "
            f"extra={len(set(evaluations)-expected)}"
        )

    clean_f1_deltas = []
    by_method_suite_family = defaultdict(list)
    for suite, scenarios in design["pilot"]["scenarios"].items():
        for scenario in scenarios:
            clean = evaluations[(suite, scenario, "clean")]
            clean_f1_deltas.append(
                float(clean["candidate_report"]["known_macro_f1"])
                - float(clean["pairwise_report"]["known_macro_f1"])
            )
            for family in FAMILIES:
                corrupted = evaluations[(suite, scenario, family)]
                by_method_suite_family[
                    ("candidate", suite, family)
                ].append(
                    (
                        clean["candidate_report"],
                        corrupted["candidate_report"],
                    )
                )
                by_method_suite_family[
                    ("pairwise", suite, family)
                ].append(
                    (
                        clean["pairwise_report"],
                        corrupted["pairwise_report"],
                    )
                )

    thresholds = {
        name: float(value)
        for name, value in design["thresholds"].items()
    }
    suite_results: Dict[str, Dict[str, Dict[str, Any]]] = {}
    failure_counts = {
        "candidate": {family: 0 for family in FAMILIES},
        "pairwise": {family: 0 for family in FAMILIES},
    }
    method_values = {"candidate": {}, "pairwise": {}}
    for method in ("candidate", "pairwise"):
        method_values[method] = {}
        for family in FAMILIES:
            method_values[method][family] = {}
            for suite in sorted(design["pilot"]["scenarios"]):
                means = mean_records(
                    by_method_suite_family[(method, suite, family)]
                )
                records = {}
                for metric, value in means.items():
                    passed = value <= thresholds[metric] + 1e-12
                    failure_counts[method][family] += int(not passed)
                    records[metric] = {
                        "mean_degradation": value,
                        "maximum_mean_degradation": thresholds[metric],
                        "passes": passed,
                        "n_scenarios": len(
                            design["pilot"]["scenarios"][suite]
                        ),
                    }
                method_values[method][family][suite] = records
    suite_results = method_values["candidate"]

    family_means = {"candidate": {}, "pairwise": {}}
    for method in ("candidate", "pairwise"):
        for family in FAMILIES:
            pairs = []
            for suite in sorted(design["pilot"]["scenarios"]):
                pairs.extend(
                    by_method_suite_family[(method, suite, family)]
                )
            family_means[method][family] = mean_records(pairs)

    clean_delta = np.asarray(clean_f1_deltas, dtype=np.float64)
    clean_mean_degradation = float(-clean_delta.mean())
    clean_worst_degradation = float(-clean_delta.min())
    gate = design["pilot"]["expansion_gate"]
    no_family_extra_regression = all(
        family_means["candidate"][family][metric]
        <= family_means["pairwise"][family][metric]
        + float(gate["no_family_metric_worse_than_pairwise_by_more_than"])
        + 1e-12
        for family in FAMILIES
        for metric in METRICS
    )
    checks = {
        "all_14_scenarios_complete": len(clean_f1_deltas) == 14,
        "all_84_evaluations_complete": len(evaluations) == 84,
        "weight_selected_on_known_validation_only": (
            selection.get("unknown_or_test_labels_used") is False
        ),
        "clean_known_macro_f1_mean": (
            clean_mean_degradation
            <= float(
                gate[
                    "clean_known_macro_f1_mean_degradation_maximum"
                ]
            )
            + 1e-12
        ),
        "clean_known_macro_f1_worst": (
            clean_worst_degradation
            <= float(
                gate[
                    "clean_known_macro_f1_worst_degradation_maximum"
                ]
            )
            + 1e-12
        ),
        "failed_suite_checks": (
            sum(failure_counts["candidate"].values())
            <= int(gate["failed_suite_checks_maximum"])
        ),
        "modality_missing_failures_reduced": (
            failure_counts["candidate"]["modality_missing"]
            < failure_counts["pairwise"]["modality_missing"]
        ),
        "gaussian_drift_failures_reduced": (
            failure_counts["candidate"]["gaussian_drift"]
            < failure_counts["pairwise"]["gaussian_drift"]
        ),
        "no_family_metric_extra_regression": no_family_extra_regression,
    }
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_caeos_pilot_summary_v1",
        "state": "complete",
        "algorithm": "mdr_caeos_v1",
        "design_manifest_sha256": design["manifest_sha256"],
        "weight_selection_manifest_sha256": selection["manifest_sha256"],
        "selected_weight": float(selection["selected_weight"]),
        "validation": {
            "scenario_count": len(clean_f1_deltas),
            "evaluation_count": len(evaluations),
            "suite_threshold_check_count": 175,
            "evaluation_file_sha256": file_sha,
            "passes": True,
        },
        "clean_pairwise_comparison": {
            "known_macro_f1_mean_degradation": clean_mean_degradation,
            "known_macro_f1_worst_degradation": clean_worst_degradation,
        },
        "family_mean_degradation": family_means,
        "suite_results": suite_results,
        "suite_failure_counts": failure_counts,
        "expansion_checks": checks,
        "decision": {
            "expand_to_full102_confirmation": all(checks.values())
        },
        "claim_boundary": {
            "pilot_is_development_only": True,
            "pilot_success_does_not_establish_sota": True,
            "full_confirmation_not_started_by_summarizer": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--evaluation-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = summarize(
        load(args.design),
        load(args.selection),
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
