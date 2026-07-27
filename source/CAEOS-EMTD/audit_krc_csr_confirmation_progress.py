from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_krc_csr_confirmation import (
    load_json,
    validate_capture,
    validate_capture_execution,
    validate_evaluation,
    validate_protocol,
)


def numeric_report_max_abs_difference(
    left: Dict[str, Any], right: Dict[str, Any]
) -> float:
    if set(left) != set(right):
        raise ValueError("candidate and Pairwise report keys differ")
    differences = []
    for key in sorted(left):
        left_value = left[key]
        right_value = right[key]
        if not isinstance(left_value, (int, float)) or not isinstance(
            right_value, (int, float)
        ):
            raise ValueError(f"non-numeric report metric: {key}")
        differences.append(abs(float(left_value) - float(right_value)))
    return max(differences, default=0.0)


def relative_inventory(
    paths: Iterable[Path], root: Path
) -> list[Dict[str, str]]:
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "file_sha256": file_hash(path),
            "manifest_sha256": load_json(path)["manifest_sha256"],
        }
        for path in sorted(paths)
    ]


def audit(
    protocol_path: Path, run_root: Path, output_path: Path
) -> Dict[str, Any]:
    protocol = load_json(protocol_path)
    validate_protocol(protocol)
    confirmation = protocol["confirmation"]
    conditions = list(confirmation["conditions"])
    weight = float(confirmation["fixed_augmentation_weight"])
    tasks = {
        (
            task["suite"],
            task["scenario"],
            int(task["training_seed"]),
        ): task
        for task in confirmation["tasks"]
    }

    capture_root = run_root / "captures"
    evaluation_root = run_root / "evaluations"
    capture_paths = sorted(capture_root.rglob("capture_manifest.json"))
    execution_paths = sorted(capture_root.rglob("capture_execution.json"))
    evaluation_paths = sorted(evaluation_root.rglob("evaluation.json"))
    if not capture_paths:
        raise ValueError("no KRC captures are available")
    if len(capture_paths) != len(execution_paths):
        raise ValueError("capture and execution timing counts differ")

    records = []
    expected_evaluations = set()
    for capture_path in capture_paths:
        capture = load_json(capture_path)
        suite = capture["task"]["suite"]
        scenario = capture["task"]["scenario"]
        training_seed = int(capture["training_seed"])
        identity = (suite, scenario, training_seed)
        if identity not in tasks:
            raise ValueError(f"capture is not frozen in protocol: {identity}")
        task = tasks[identity]
        validate_capture(
            capture_path,
            suite=suite,
            scenario=scenario,
            training_seed=training_seed,
            weight=weight,
        )
        execution_path = capture_path.with_name("capture_execution.json")
        validate_capture_execution(execution_path, capture_path, task)

        routing_enabled = bool(
            capture["known_only_certificate"]["routing_enabled"]
        )
        safety = capture["safety_profile"]
        roundtrip = capture["roundtrip"]
        if (
            roundtrip.get("passes") is not True
            or roundtrip.get("prediction_array_equal") is not True
            or float(
                roundtrip.get("probability_max_absolute_difference", -1.0)
            )
            > 1e-12
            or float(roundtrip.get("risk_max_absolute_difference", -1.0))
            > 1e-12
            or capture.get(
                "unknown_or_test_labels_used_for_training_selection_or_calibration"
            )
            is not False
            or capture.get("test_labels_read_for_certificate_or_roundtrip")
            is not False
        ):
            raise ValueError(f"capture invariant failed: {identity}")
        if not routing_enabled and (
            int(safety.get("active_count", -1)) != 0
            or safety.get("prediction_array_equal_pairwise") is not True
            or float(
                safety.get("probability_max_absolute_difference", -1.0)
            )
            != 0.0
            or float(
                safety.get("inactive_risk_max_absolute_difference", -1.0)
            )
            != 0.0
            or float(safety.get("clean_delta", float("nan"))) != 0.0
        ):
            raise ValueError(f"disabled routing is not exact: {identity}")

        max_report_difference = 0.0
        for condition in conditions:
            evaluation_path = (
                evaluation_root
                / suite
                / scenario
                / f"seed{training_seed}"
                / condition
                / "evaluation.json"
            )
            expected_evaluations.add(evaluation_path.resolve())
            validate_evaluation(
                evaluation_path, protocol, task, condition
            )
            evaluation = load_json(evaluation_path)
            routing = evaluation["routing"]
            corruption = evaluation["corruption"]
            if (
                evaluation.get("state") != "complete"
                or evaluation.get(
                    "test_labels_used_for_final_evaluation_only"
                )
                is not True
                or routing.get("unknown_or_test_labels_used") is not False
                or routing.get("prediction_exactly_pairwise_all_rows")
                is not True
                or routing.get("probability_exactly_pairwise_all_rows")
                is not True
                or routing.get("risk_monotone_not_below_pairwise") is not True
                or corruption.get("selection_uses_effect_metrics") is not False
            ):
                raise ValueError(
                    f"evaluation invariant failed: {identity}/{condition}"
                )
            difference = numeric_report_max_abs_difference(
                evaluation["candidate_report"],
                evaluation["pairwise_report"],
            )
            max_report_difference = max(
                max_report_difference, difference
            )
            if not routing_enabled and (
                routing.get("disabled_risk_exactly_pairwise_all_rows")
                is not True
                or difference != 0.0
            ):
                raise ValueError(
                    f"disabled evaluation is not exact: "
                    f"{identity}/{condition}"
                )

        records.append(
            {
                "suite": suite,
                "scenario": scenario,
                "training_seed": training_seed,
                "primary_heldout_scenario": bool(
                    task["primary_heldout_scenario"]
                ),
                "routing_enabled": routing_enabled,
                "calibration_known_macro_f1": float(
                    capture["known_only_certificate"][
                        "calibration_known_macro_f1"
                    ]
                ),
                "calibration_error_detection_auroc": float(
                    capture["known_only_certificate"][
                        "calibration_error_detection_auroc"
                    ]
                ),
                "calibration_count": int(
                    capture["known_only_certificate"]["partition"][
                        "calibration_count"
                    ]
                ),
                "next_exchangeable_false_activation_bound": float(
                    capture["runtime_evidence"]["routing_calibration"][
                        "next_exchangeable_false_activation_bound"
                    ]
                ),
                "safety_active_count": int(safety["active_count"]),
                "safety_clean_delta": float(safety["clean_delta"]),
                "maximum_candidate_pairwise_report_absolute_difference": (
                    max_report_difference
                ),
                "capture_wall_seconds": float(
                    load_json(execution_path)[
                        "total_capture_wall_seconds"
                    ]
                ),
                "capture_manifest_file_sha256": file_hash(capture_path),
                "capture_manifest_sha256": capture["manifest_sha256"],
                "capture_execution_file_sha256": file_hash(execution_path),
            }
        )

    actual_evaluations = {path.resolve() for path in evaluation_paths}
    if actual_evaluations != expected_evaluations:
        missing = sorted(
            path.as_posix()
            for path in expected_evaluations - actual_evaluations
        )
        unexpected = sorted(
            path.as_posix()
            for path in actual_evaluations - expected_evaluations
        )
        raise ValueError(
            f"evaluation inventory mismatch: "
            f"missing={missing}, unexpected={unexpected}"
        )

    enabled_count = sum(
        int(record["routing_enabled"]) for record in records
    )
    evaluation_inventory = relative_inventory(
        evaluation_paths, evaluation_root
    )
    evidence: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_csr_confirmation_progress_audit_v1",
        "state": "valid_partial_progress",
        "passes": True,
        "protocol": {
            "path": protocol_path.resolve().as_posix(),
            "file_sha256": file_hash(protocol_path),
            "manifest_sha256": protocol["manifest_sha256"],
        },
        "frozen_totals": {
            "captures": int(confirmation["capture_count"]),
            "evaluations": int(confirmation["evaluation_count"]),
        },
        "observed_totals": {
            "captures": len(capture_paths),
            "capture_executions": len(execution_paths),
            "evaluations": len(evaluation_paths),
            "conditions_per_capture": len(conditions),
            "primary_captures": sum(
                int(record["primary_heldout_scenario"])
                for record in records
            ),
            "routing_enabled_captures": enabled_count,
            "routing_disabled_captures": len(records) - enabled_count,
        },
        "conditions": conditions,
        "records": records,
        "capture_inventory": relative_inventory(
            capture_paths, capture_root
        ),
        "capture_execution_inventory": [
            {
                "path": path.relative_to(capture_root).as_posix(),
                "file_sha256": file_hash(path),
                "manifest_sha256": load_json(path)["manifest_sha256"],
            }
            for path in execution_paths
        ],
        "evaluation_inventory": evaluation_inventory,
        "evaluation_inventory_manifest_sha256": canonical_hash(
            {"evaluations": evaluation_inventory}
        ),
        "invariants": {
            "all_captures_validate_against_frozen_protocol": True,
            "all_capture_executions_validate": True,
            "all_observed_captures_have_every_frozen_condition": True,
            "no_orphan_or_unexpected_evaluations": True,
            "all_evaluations_validate_against_frozen_protocol": True,
            "prediction_and_probability_exactly_pairwise": True,
            "risk_monotone_not_below_pairwise": True,
            "disabled_routing_is_exact_pairwise": True,
            "unknown_or_test_labels_not_used_for_selection": True,
        },
        "output_path": output_path.resolve().as_posix(),
    }
    evidence["manifest_sha256"] = canonical_hash(evidence)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evidence = audit(
        args.protocol.resolve(),
        args.run_root.resolve(),
        args.output.resolve(),
    )
    print(
        json.dumps(
            {
                "passes": evidence["passes"],
                "observed_totals": evidence["observed_totals"],
                "evaluation_inventory_manifest_sha256": evidence[
                    "evaluation_inventory_manifest_sha256"
                ],
                "manifest_sha256": evidence["manifest_sha256"],
                "file_sha256": file_hash(args.output.resolve()),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
