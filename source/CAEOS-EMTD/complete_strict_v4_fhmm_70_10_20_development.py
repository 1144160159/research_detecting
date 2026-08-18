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


def complete(
    protocol_path: Path,
    run_root: Path,
    result_root: Path,
) -> dict[str, Any]:
    protocol_path = protocol_path.resolve()
    run_root = run_root.resolve()
    result_root = result_root.resolve()
    protocol = load_canonical(protocol_path, "70/10/20 protocol")
    project_root = Path(protocol["paths"]["project_root"]).resolve()
    if any(
        file_hash(project_root / name) != expected
        for name, expected in protocol["implementation_sha256"].items()
    ):
        raise ValueError("70/10/20 implementation hash drifted")
    development_path = result_root / "development.json"
    development = load_canonical(
        development_path,
        "70/10/20 development result",
    )
    expected_training = protocol["training"]
    members = {}
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
            gpu = load_canonical(gpu_path, f"{identity} GPU")
            audit = load_canonical(audit_path, f"{identity} resource")
            history = metrics["training"]["history"]
            epoch_match = (
                0 < len(history) <= expected_training["epochs_requested"]
                and all(
                    int(item["epoch"]) == index
                    for index, item in enumerate(history)
                )
            )
            training_match = all(
                metrics["training"][name] == value
                for name, value in expected_training.items()
            )
            integrity = (
                metrics["state"] == "complete"
                and metrics["schema_version"]
                == "strict_v4_fhmm_stable_70_10_20_cuda_task_v1"
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
                and metrics["source"]["split_wrapper_sha256"]
                == protocol["implementation_sha256"][
                    "train_strict_v4_fhmm_stable_70_10_20_task_cuda.py"
                ]
                and training_match
                and epoch_match
                and finite_history(metrics)
                and bool(metrics["gpu_execution"]["passes"])
                and bool(gpu["passes"])
            )
            resource = bool(audit["gates"]["all_pass"])
            all_integrity = all_integrity and integrity
            all_resources = all_resources and resource
            members[identity] = {
                "integrity_pass": integrity,
                "resource_pass": resource,
                "finite_history": finite_history(metrics),
                "epoch_count_match": epoch_match,
                "resource_observed": audit["observed"],
                "metrics_sha256": file_hash(metrics_path),
                "gpu_execution_sha256": file_hash(gpu_path),
                "resource_audit_sha256": file_hash(audit_path),
            }
    effect = (
        development["state"]
        == "development_candidate_qualifies_for_disjoint_families"
    )
    expand = all_integrity and all_resources and effect
    result: dict[str, Any] = {
        "schema_version": "strict_v4_fhmm_70_10_20_development_completion_v1",
        "state": (
            "development_expansion_gate_passed"
            if expand
            else "development_expansion_gate_not_met"
        ),
        "expand_to_disjoint_unknown_families": expand,
        "all_integrity_passed": all_integrity,
        "all_resources_passed": all_resources,
        "development_effect_gate_passed": effect,
        "selected": development["selected"],
        "members": members,
        "development": {
            "path": str(development_path),
            "file_sha256": file_hash(development_path),
            "manifest_sha256": development["manifest_sha256"],
        },
        "protocol": {
            "path": str(protocol_path),
            "file_sha256": file_hash(protocol_path),
            "manifest_sha256": protocol["manifest_sha256"],
        },
        "claim_boundary": {
            "development_only": True,
            "botnet_not_future_confirmation": True,
            "disjoint_family_expansion_requires_all_gates": True,
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
