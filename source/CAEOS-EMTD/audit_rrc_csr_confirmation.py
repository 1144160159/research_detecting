from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_rrc_csr_capture_pipeline import (
    CONDITIONS,
    load_json,
    validate_certificate,
    validate_evaluation,
    validate_protocol,
    validate_rrc_capture,
)


METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")
FAMILIES = CONDITIONS[1:]
Scenario = Tuple[str, str]


def delta(value: Dict[str, Any], metric: str) -> float:
    candidate = float(value["candidate_report"][metric])
    pairwise = float(value["pairwise_report"][metric])
    return pairwise - candidate if metric == "unknown_fpr95" else candidate - pairwise


def equal_suite_mean(values: Dict[Scenario, float]) -> Tuple[float, Dict[str, float]]:
    grouped: Dict[str, List[float]] = defaultdict(list)
    for (suite, _), value in values.items():
        grouped[suite].append(float(value))
    suite_means = {
        suite: float(np.mean(rows)) for suite, rows in sorted(grouped.items())
    }
    if len(suite_means) != 7:
        raise ValueError("independent RRC audit requires seven suites")
    return float(np.mean(list(suite_means.values()))), suite_means


def audit(
    protocol: Dict[str, Any],
    summary: Dict[str, Any],
    pipeline: Dict[str, Any],
    certificate_paths: List[Path],
    capture_paths: List[Path],
    evaluation_paths: List[Path],
) -> Dict[str, Any]:
    validate_protocol(protocol)
    if (
        summary.get("schema_version")
        != "strict_v4_rrc_csr_confirmation_summary_v1"
        or summary.get("manifest_sha256") != canonical_hash(summary)
        or summary.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or pipeline.get("schema_version")
        != "strict_v4_rrc_csr_capture_pipeline_inventory_v1"
        or pipeline.get("manifest_sha256") != canonical_hash(pipeline)
        or summary.get("pipeline_inventory_manifest_sha256")
        != pipeline["manifest_sha256"]
    ):
        raise ValueError("canonical bound RRC summary and inventory required")

    tasks = protocol["tasks"]
    task_map = {
        (
            task["suite"],
            task["scenario"],
            int(task["training_seed"]),
            int(task["corruption_seed"]),
        ): task
        for task in tasks
    }
    scenarios = sorted({identity[:2] for identity in task_map})
    certificates = {}
    for path in certificate_paths:
        item = load_json(path)
        identity = (item.get("suite"), item.get("scenario"))
        if identity not in scenarios or not validate_certificate(
            path, protocol, identity[0], identity[1]
        ):
            raise ValueError(f"invalid certificate in RRC audit: {path}")
        if identity in certificates:
            raise ValueError("duplicate RRC certificate")
        certificates[identity] = item

    captures = {}
    for path in capture_paths:
        item = load_json(path)
        task_value = item.get("task", {})
        identity = (
            task_value.get("suite"),
            task_value.get("scenario"),
            int(item.get("training_seed", -1)),
            int(item.get("corruption_seed", -1)),
        )
        task = task_map.get(identity)
        if (
            task is None
            or not validate_rrc_capture(path, protocol, task)
            or item.get("scenario_certificate_manifest_sha256")
            != certificates[identity[:2]]["manifest_sha256"]
        ):
            raise ValueError(f"invalid capture in RRC audit: {path}")
        if identity in captures:
            raise ValueError("duplicate RRC capture")
        captures[identity] = item

    evaluations = {}
    effect_rows = []
    routing_invariants = []
    for path in evaluation_paths:
        item = load_json(path)
        identity = (
            item.get("suite"),
            item.get("scenario"),
            int(item.get("training_seed", -1)),
            item.get("condition"),
        )
        task = task_map.get(
            (*identity[:3], int(item.get("corruption_seed", -1)))
        )
        if task is None or not validate_evaluation(
            path, protocol, task, identity[3]
        ):
            raise ValueError(f"invalid evaluation in RRC audit: {path}")
        if identity in evaluations:
            raise ValueError("duplicate RRC evaluation")
        evaluations[identity] = item
        routing = item["routing"]
        routing_invariants.append(
            bool(
                routing["prediction_exactly_pairwise_all_rows"]
                and routing["probability_exactly_pairwise_all_rows"]
                and routing["risk_monotone_not_below_pairwise"]
                and routing["inactive_risk_exactly_pairwise"]
                and routing["disabled_risk_exactly_pairwise_all_rows"]
                and routing["unknown_or_test_labels_used"] is False
                and item["test_labels_used_for_final_evaluation_only"]
                is True
            )
        )
        if identity[3] != "clean":
            for metric in METRICS:
                effect_rows.append(
                    (
                        identity[0],
                        identity[1],
                        identity[3],
                        metric,
                        delta(item, metric),
                    )
                )

    expected_evaluations = {
        (suite, scenario, training_seed, condition)
        for suite, scenario, training_seed, _ in task_map
        for condition in CONDITIONS
    }
    inventory_records = pipeline.get("inventories", {})
    inventory_paths = {
        "scenario_certificates": certificate_paths,
        "rrc_runtime_captures": capture_paths,
        "evaluations": evaluation_paths,
    }
    inventory_hashes_match = True
    for name, paths in inventory_paths.items():
        expected = {
            row["path"]: row["file_sha256"]
            for row in inventory_records.get(name, [])
        }
        actual = {
            path.as_posix().split("/", 1)[-1]: file_hash(path)
            for path in paths
        }
        # Absolute roots differ between the inventory writer and auditor CLI.
        inventory_hashes_match &= sorted(expected.values()) == sorted(
            actual.values()
        )

    metric_result = {}
    for metric in METRICS:
        scenario_values = {
            scenario: float(
                np.mean(
                    [
                        value
                        for suite, name, _, row_metric, value in effect_rows
                        if row_metric == metric
                        and (suite, name) == scenario
                    ]
                )
            )
            for scenario in scenarios
        }
        overall, suite_means = equal_suite_mean(scenario_values)
        metric_result[metric] = {
            "overall": overall,
            "suite_nonnegative_count": sum(
                value >= -1e-12 for value in suite_means.values()
            ),
        }

    family_result = {}
    for family in FAMILIES:
        family_result[family] = {}
        for metric in METRICS:
            scenario_values = {
                scenario: float(
                    np.mean(
                        [
                            value
                            for suite, name, row_family, row_metric, value
                            in effect_rows
                            if row_family == family
                            and row_metric == metric
                            and (suite, name) == scenario
                        ]
                    )
                )
                for scenario in scenarios
            }
            family_result[family][metric] = equal_suite_mean(
                scenario_values
            )[0]
        family_result[family]["composite"] = float(
            np.mean([family_result[family][metric] for metric in METRICS])
        )

    enabled = [
        identity
        for identity, item in certificates.items()
        if item["routing_enabled"] is True
    ]
    gate = protocol["effect_gate"]
    effect_checks = {
        "enabled_scenario_count_minimum": len(enabled)
        >= int(gate["primary_enabled_scenario_count_minimum"]),
        "enabled_suite_count_minimum": len({suite for suite, _ in enabled})
        >= int(gate["primary_enabled_suite_count_minimum"]),
        "overall_directed_means_strictly_positive": all(
            metric_result[metric]["overall"] > 0.0 for metric in METRICS
        ),
        "suite_nonnegative_count_minimum_each_metric": all(
            metric_result[metric]["suite_nonnegative_count"]
            >= int(gate["suite_nonnegative_count_minimum_each_metric"])
            for metric in METRICS
        ),
        "each_family_metric_regression_maximum": all(
            family_result[family][metric]
            >= -float(gate["each_family_metric_regression_maximum"])
            for family in FAMILIES
            for metric in METRICS
        ),
        "modality_missing_composite_improves": family_result[
            "modality_missing"
        ]["composite"]
        > 0.0,
        "gaussian_drift_composite_improves": family_result[
            "gaussian_drift"
        ]["composite"]
        > 0.0,
    }
    effect_passes = all(effect_checks.values())
    summary_matches = bool(
        summary["effect_gate_checks"] == effect_checks
        and bool(summary["passes"]) == effect_passes
        and summary["selection"]
        == ("rrc_csr_caeos_v1" if effect_passes else "caeos_pairwise")
        and all(
            abs(
                float(
                    summary["metric_summary"][metric][
                        "overall_equal_suite_mean"
                    ]
                )
                - metric_result[metric]["overall"]
            )
            <= 1e-12
            for metric in METRICS
        )
    )
    integrity_checks = {
        "exact_task_count": len(task_map) == 249,
        "exact_scenario_count": len(scenarios) == 83,
        "exact_certificate_inventory": len(certificates) == 83,
        "exact_runtime_capture_inventory": len(captures) == 249,
        "exact_evaluation_inventory": set(evaluations)
        == expected_evaluations,
        "pipeline_inventory_hashes_match": inventory_hashes_match,
        "all_routing_and_leakage_invariants_pass": all(routing_invariants),
        "summary_matches_independent_recomputation": summary_matches,
    }
    integrity_passes = all(integrity_checks.values())
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_rrc_csr_confirmation_audit_v1",
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "summary_manifest_sha256": summary["manifest_sha256"],
        "pipeline_inventory_manifest_sha256": pipeline["manifest_sha256"],
        "integrity_checks": integrity_checks,
        "integrity_passes": integrity_passes,
        "effect_gate_checks": effect_checks,
        "effect_gate_passes": effect_passes,
        "passes": bool(integrity_passes and effect_passes),
        "selection": (
            "rrc_csr_caeos_v1" if effect_passes else "caeos_pairwise"
        ),
        "claim_boundary": {
            "integrity_and_effect_are_reported_separately": True,
            "scientific_negative_is_not_structural_failure": True,
            "rrc_positive_is_not_full_external_sota": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--pipeline-inventory", type=Path, required=True)
    parser.add_argument("--certificate-root", type=Path, required=True)
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--evaluation-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = audit(
        load_json(args.protocol.resolve()),
        load_json(args.summary.resolve()),
        load_json(args.pipeline_inventory.resolve()),
        sorted(args.certificate_root.resolve().rglob("certificate.json")),
        sorted(args.capture_root.resolve().rglob("capture_manifest.json")),
        sorted(args.evaluation_root.resolve().rglob("evaluation.json")),
    )
    value["input_file_sha256"] = {
        "protocol": file_hash(args.protocol.resolve()),
        "summary": file_hash(args.summary.resolve()),
        "pipeline_inventory": file_hash(
            args.pipeline_inventory.resolve()
        ),
    }
    value["manifest_sha256"] = canonical_hash(value)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
