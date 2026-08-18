from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)


def finite_history(report: dict[str, Any]) -> bool:
    history = report["training"]["history"]
    return bool(history) and all(
        item["meta_outer_loss"] is not None
        and all(
            math.isfinite(float(item[name]))
            for name in (
                "training_loss",
                "validation_loss",
                "meta_outer_loss",
            )
        )
        for item in history
    )


def implementations_match(protocol: dict[str, Any]) -> bool:
    project_root = Path(protocol["paths"]["project_root"]).resolve()
    return all(
        file_hash(project_root / name) == expected
        for name, expected in protocol["implementation_sha256"].items()
    )


def complete(
    protocol_path: Path,
    run_root: Path,
    result_root: Path,
) -> dict[str, Any]:
    protocol_path = protocol_path.resolve()
    run_root = run_root.resolve()
    result_root = result_root.resolve()
    protocol = load_canonical(protocol_path, "FHMM-S confirmation protocol")
    if not implementations_match(protocol):
        raise ValueError("confirmation implementation hash drifted")
    evaluation_path = result_root / "evaluation.json"
    evaluation = load_canonical(
        evaluation_path,
        "FHMM-S confirmation evaluation",
    )
    if evaluation["protocol"]["file_sha256"] != file_hash(protocol_path):
        raise ValueError("evaluation protocol binding drifted")
    expected_training = protocol["training"]
    member_results = {}
    all_integrity = True
    all_resources = True
    for task in protocol["tasks"]:
        split_seed = int(task["split_seed"])
        for model_seed in task["model_seeds"]:
            model_seed = int(model_seed)
            identity = f"split{split_seed}_model{model_seed}"
            task_dir = run_root / identity
            metrics_path = task_dir / "metrics.json"
            gpu_path = task_dir / "gpu_execution.json"
            audit_path = result_root / f"resource_audit_{identity}.json"
            metrics = load_canonical(metrics_path, f"{identity} metrics")
            gpu = load_canonical(gpu_path, f"{identity} GPU evidence")
            audit = load_canonical(audit_path, f"{identity} resource audit")
            training_match = all(
                metrics["training"][name] == value
                for name, value in expected_training.items()
            )
            history = metrics["training"]["history"]
            epoch_count_match = (
                0 < len(history) <= expected_training["epochs_requested"]
                and all(
                    int(item["epoch"]) == index
                    for index, item in enumerate(history)
                )
            )
            integrity = (
                metrics["state"] == "complete"
                and metrics["schema_version"]
                == "strict_v4_fhmm_stable_cuda_task_v2"
                and metrics["task"]
                == {
                    "unknown_family": "Botnet",
                    "split_seed": split_seed,
                    "model_seed": model_seed,
                }
                and metrics["source"]["sequence_dataset_sha256"]
                == protocol["dataset"]["sha256"]
                and metrics["source"]["stable_training_core_sha256"]
                == protocol["implementation_sha256"][
                    "train_strict_v4_fhmm_stable_task_cuda.py"
                ]
                and training_match
                and epoch_count_match
                and finite_history(metrics)
                and bool(metrics["gpu_execution"]["passes"])
                and bool(gpu["passes"])
            )
            resource = bool(audit["gates"]["all_pass"])
            all_integrity = all_integrity and integrity
            all_resources = all_resources and resource
            member_results[identity] = {
                "integrity_pass": integrity,
                "resource_pass": resource,
                "history_all_losses_finite": finite_history(metrics),
                "epoch_count_match": epoch_count_match,
                "amp_scale_reduction_count": metrics["training"][
                    "amp_scale_reduction_count"
                ],
                "resource_observed": audit["observed"],
                "metrics_sha256": file_hash(metrics_path),
                "gpu_execution_sha256": file_hash(gpu_path),
                "resource_audit_sha256": file_hash(audit_path),
            }
    primary_effect = bool(
        evaluation["all_repeat_gates"][
            "primary_known_unknown_confirmation"
        ]
    )
    full_typed_effect = bool(
        evaluation["all_repeat_gates"]["full_typed_known_unknown_95_5"]
    )
    expand = all_integrity and all_resources and primary_effect
    result: dict[str, Any] = {
        "schema_version": "strict_v4_fhmm_stable_confirmation_completion_v1",
        "state": (
            "confirmation_expansion_gate_passed"
            if expand
            else "confirmation_expansion_gate_not_met"
        ),
        "expand_to_seven_unknown_families": expand,
        "all_integrity_passed": all_integrity,
        "all_resources_passed": all_resources,
        "primary_effect_gate_passed": primary_effect,
        "full_typed_95_5_gate_passed": full_typed_effect,
        "macro_mean": evaluation["macro_mean"],
        "per_repeat": evaluation["per_repeat"],
        "members": member_results,
        "evaluation": {
            "path": str(evaluation_path),
            "file_sha256": file_hash(evaluation_path),
            "manifest_sha256": evaluation["manifest_sha256"],
        },
        "protocol": {
            "path": str(protocol_path),
            "file_sha256": file_hash(protocol_path),
            "manifest_sha256": protocol["manifest_sha256"],
        },
        "claim_boundary": {
            "fresh_two_split_confirmation": True,
            "not_formal_five_seed_seven_scenario_evidence": True,
            "seven_scenario_expansion_requires_primary_gate": True,
            "full_typed_95_5_claim_requires_separate_gate": True,
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
