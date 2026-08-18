from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)


OPERATIONAL_METRICS = (
    "alert_accuracy",
    "alert_precision",
    "alert_recall",
    "alert_f1",
    "benign_fpr",
    "known_attack_type_accuracy",
    "unknown_attack_alert_recall",
    "unknown_attack_recall",
    "unknown_label_precision",
)
RESEARCH_METRICS = {
    "known_macro_f1": ("closed_set_known", "known_macro_f1"),
    "known_balanced_accuracy": (
        "closed_set_known",
        "known_balanced_accuracy",
    ),
    "unknown_auroc": ("unknown_detection", "unknown_auroc"),
    "unknown_aupr_out": ("unknown_detection", "unknown_aupr_out"),
    "fpr_known_at_95_unknown_tpr": (
        "unknown_detection",
        "fpr_known_at_95_unknown_tpr",
    ),
    "oscr_exact_v2": ("joint_open_set", "oscr_exact_v2"),
}


def _mean(records: list[dict[str, float]]) -> dict[str, float]:
    if not records:
        raise ValueError("metric records are required")
    return {
        name: float(np.mean([record[name] for record in records]))
        for name in records[0]
    }


def _research_vector(report: dict[str, Any]) -> dict[str, float]:
    return {
        name: float(report[group][metric])
        for name, (group, metric) in RESEARCH_METRICS.items()
    }


def complete(
    protocol_path: Path,
    run_root: Path,
    result_root: Path,
) -> dict[str, Any]:
    protocol_path = protocol_path.resolve()
    run_root = run_root.resolve()
    result_root = result_root.resolve()
    protocol = load_canonical(protocol_path, "same-split ensemble protocol")
    if protocol["state"] != "frozen_before_any_member_training":
        raise ValueError("protocol is not a frozen pre-registration")
    all_integrity = True
    all_resources = True
    all_effects = True
    split_reports = {}
    operational_records = []
    research_records = []
    for task in protocol["tasks"]:
        split_seed = int(task["split_seed"])
        expected_model_seeds = [int(value) for value in task["model_seeds"]]
        evaluation_path = result_root / f"evaluation_split{split_seed}.json"
        evaluation = load_canonical(
            evaluation_path,
            f"split{split_seed} ensemble evaluation",
        )
        fixed_match = (
            evaluation["fixed_configuration"]["member_count"] == 3
            and evaluation["fixed_configuration"]["alert_budget"]
            == protocol["evaluation"]["alert_budget"]
            and evaluation["fixed_configuration"]["open_budget"]
            == protocol["evaluation"]["open_budget"]
            and evaluation["fixed_configuration"]["configuration_selection"]
            == "none_fixed_before_test"
        )
        identity_match = (
            evaluation["task"]["unknown_family"] == task["unknown_family"]
            and int(evaluation["task"]["split_seed"]) == split_seed
            and [int(value) for value in evaluation["task"]["model_seeds"]]
            == expected_model_seeds
        )
        member_reports = {}
        split_integrity = fixed_match and identity_match
        split_resources = True
        for model_seed in expected_model_seeds:
            identity = f"split{split_seed}_model{model_seed}"
            task_dir = run_root / identity
            metrics_path = task_dir / "metrics.json"
            gpu_path = task_dir / "gpu_execution.json"
            audit_path = result_root / f"resource_audit_{identity}.json"
            metrics = load_canonical(metrics_path, f"{identity} metrics")
            gpu = load_canonical(gpu_path, f"{identity} GPU evidence")
            audit = load_canonical(audit_path, f"{identity} resource audit")
            history = metrics["training"]["history"]
            finite_meta = bool(history) and all(
                item["meta_outer_loss"] is not None
                and math.isfinite(float(item["meta_outer_loss"]))
                for item in history
            )
            integrity = (
                metrics["state"] == "complete"
                and metrics["schema_version"]
                == "strict_v4_fhmm_same_split_member_cuda_task_v1"
                and metrics["task"]
                == {
                    "unknown_family": task["unknown_family"],
                    "split_seed": split_seed,
                    "model_seed": model_seed,
                }
                and metrics["source"]["sequence_dataset_sha256"]
                == protocol["dataset"]["sha256"]
                and metrics["source"]["base_training_kernel_sha256"]
                == protocol["implementation_sha256"][
                    "train_strict_v4_dual_metric_contrastive_task_cuda.py"
                ]
                and metrics["source"]["member_wrapper_sha256"]
                == protocol["implementation_sha256"][
                    "train_strict_v4_fhmm_same_split_member_cuda.py"
                ]
                and finite_meta
                and bool(metrics["gpu_execution"]["passes"])
                and bool(gpu["passes"])
            )
            resource_pass = bool(audit["gates"]["all_pass"])
            split_integrity = split_integrity and integrity
            split_resources = split_resources and resource_pass
            member_reports[str(model_seed)] = {
                "integrity_pass": integrity,
                "resource_pass": resource_pass,
                "finite_meta_outer_loss_each_epoch": finite_meta,
                "resource_observed": audit["observed"],
                "metrics_sha256": file_hash(metrics_path),
                "gpu_execution_sha256": file_hash(gpu_path),
                "resource_audit_sha256": file_hash(audit_path),
            }
        effect_pass = bool(
            evaluation["expansion_gate"]["expand_to_seven_scenarios"]
        )
        operational = {
            name: float(evaluation["operational_metrics"][name])
            for name in OPERATIONAL_METRICS
        }
        research = _research_vector(
            evaluation["research_metric_contract"]
        )
        operational_records.append(operational)
        research_records.append(research)
        all_integrity = all_integrity and split_integrity
        all_resources = all_resources and split_resources
        all_effects = all_effects and effect_pass
        split_reports[str(split_seed)] = {
            "integrity_pass": split_integrity,
            "resource_pass": split_resources,
            "effect_expansion_gate_pass": effect_pass,
            "operational_metrics": operational,
            "research_main_metrics": research,
            "expansion_gate": evaluation["expansion_gate"],
            "members": member_reports,
            "evaluation_sha256": file_hash(evaluation_path),
            "evaluation_manifest_sha256": evaluation["manifest_sha256"],
        }
    expand = all_integrity and all_resources and all_effects
    result: dict[str, Any] = {
        "schema_version": (
            "strict_v4_fhmm_same_split_ensemble_botnet_completion_v1"
        ),
        "state": (
            "pilot_expansion_gate_passed"
            if expand
            else "pilot_expansion_gate_not_met"
        ),
        "expand_to_seven_scenarios": expand,
        "all_integrity_passed": all_integrity,
        "all_resources_passed": all_resources,
        "all_effect_gates_passed": all_effects,
        "split_repeat_count": len(split_reports),
        "macro_mean": {
            "operational": _mean(operational_records),
            "research_main": _mean(research_records),
        },
        "split_repeats": split_reports,
        "protocol": {
            "path": str(protocol_path),
            "file_sha256": file_hash(protocol_path),
            "manifest_sha256": protocol["manifest_sha256"],
        },
        "claim_boundary": {
            "development_pilot_only": True,
            "two_split_repeats_are_not_formal_five_seed_confirmation": True,
            "true_unknown_used_for_configuration_or_threshold_selection": False,
            "fresh_confirmation_effect_claim_authorized": False,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    result = complete(args.protocol, args.run_root, args.result_root)
    atomic_json(args.output.resolve(), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()

