from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_neural_empirical_tail_hybrid_qualification_protocol import (
    file_hash,
    load_canonical,
)
from run_strict_v4_neural_empirical_tail_hybrid_qualification import (
    canonical_hash,
)


ALERT_CANDIDATES = (
    {
        "name": "xgboost_only_040",
        "primary_alert_budget": 0.04,
        "autoencoder_rescue_budget": 0.0,
    },
    {
        "name": "xgboost_035_autoencoder_005",
        "primary_alert_budget": 0.035,
        "autoencoder_rescue_budget": 0.005,
    },
    {
        "name": "xgboost_030_autoencoder_010",
        "primary_alert_budget": 0.03,
        "autoencoder_rescue_budget": 0.01,
    },
    {
        "name": "xgboost_025_autoencoder_015",
        "primary_alert_budget": 0.025,
        "autoencoder_rescue_budget": 0.015,
    },
    {
        "name": "xgboost_020_autoencoder_020",
        "primary_alert_budget": 0.02,
        "autoencoder_rescue_budget": 0.02,
    },
    {
        "name": "autoencoder_only_040",
        "primary_alert_budget": 0.0,
        "autoencoder_rescue_budget": 0.04,
    },
    {
        "name": "xgboost_only_044",
        "primary_alert_budget": 0.044,
        "autoencoder_rescue_budget": 0.0,
    },
    {
        "name": "xgboost_039_autoencoder_005",
        "primary_alert_budget": 0.039,
        "autoencoder_rescue_budget": 0.005,
    },
    {
        "name": "xgboost_034_autoencoder_010",
        "primary_alert_budget": 0.034,
        "autoencoder_rescue_budget": 0.01,
    },
    {
        "name": "xgboost_029_autoencoder_015",
        "primary_alert_budget": 0.029,
        "autoencoder_rescue_budget": 0.015,
    },
    {
        "name": "xgboost_024_autoencoder_020",
        "primary_alert_budget": 0.024,
        "autoencoder_rescue_budget": 0.02,
    },
)


def build_protocol(
    *,
    project_root: Path,
    parent_protocol_path: Path,
    source_completion_path: Path,
    baseline_qualification_path: Path,
    output_root: Path,
    output: Path,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    parent_protocol_path = parent_protocol_path.resolve()
    source_completion_path = source_completion_path.resolve()
    baseline_qualification_path = baseline_qualification_path.resolve()
    output_root = output_root.resolve()
    output = output.resolve()
    parent = load_canonical(parent_protocol_path, "parent protocol")
    source_completion = load_canonical(
        source_completion_path, "source completion"
    )
    baseline = load_canonical(
        baseline_qualification_path, "baseline qualification"
    )
    expected = int(parent["expected_task_count"])
    if (
        source_completion.get("task_coverage", {}).get("complete") is not True
        or len(source_completion.get("xgboost_task_artifacts", {}))
        != expected
        or len(source_completion.get("neural_task_artifacts", {}))
        != expected
        or source_completion.get("all_tasks_confirmed_cuda", {}).get(
            "xgboost"
        )
        is not True
        or source_completion.get("all_tasks_confirmed_cuda", {}).get(
            "neural"
        )
        is not True
    ):
        raise ValueError("complete CUDA source anchors are required")
    if (
        source_completion.get("protocol", {}).get("manifest_sha256")
        != parent["manifest_sha256"]
    ):
        raise ValueError("source completion is not bound to parent protocol")
    if (
        baseline.get("binding", {}).get("protocol_manifest_sha256")
        != parent["manifest_sha256"]
        or baseline.get("binding", {}).get("completion_manifest_sha256")
        != source_completion["manifest_sha256"]
    ):
        raise ValueError("baseline qualification binding differs")
    if output_root.exists() and any(output_root.iterdir()):
        raise ValueError("autoencoder output root must be new or empty")

    tasks = {}
    for seed in parent["seeds"]:
        for scenario in parent["scenarios"]:
            identity = f"{scenario}_seed{seed}"
            artifact = source_completion["xgboost_task_artifacts"][identity]
            anchor_dir = Path(artifact["task_dir"])
            provenance_path = anchor_dir / "provenance.json"
            provenance = load_canonical(
                provenance_path, f"anchor provenance {identity}"
            )
            if (
                file_hash(anchor_dir / "metrics.json")
                != artifact["metrics_sha256"]
                or file_hash(anchor_dir / "scores.npz")
                != artifact["scores_sha256"]
                or file_hash(anchor_dir / "gpu_execution.json")
                != artifact["gpu_execution_sha256"]
                or provenance.get("task", {}).get("scenario") != scenario
                or int(provenance.get("task", {}).get("seed", -1)) != seed
            ):
                raise ValueError(f"anchor artifact mismatch: {identity}")
            cache_csv = Path(provenance["cache_csv"])
            config_path = Path(provenance["config"])
            tasks[identity] = {
                "identity": identity,
                "scenario": scenario,
                "seed": seed,
                "anchor_dir": str(anchor_dir),
                "anchor_sha256": {
                    "metrics": artifact["metrics_sha256"],
                    "scores": artifact["scores_sha256"],
                    "gpu_execution": artifact["gpu_execution_sha256"],
                    "provenance": file_hash(provenance_path),
                },
                "cache_csv": str(cache_csv),
                "cache_csv_sha256": file_hash(cache_csv),
                "config": str(config_path),
                "config_sha256": file_hash(config_path),
                "output_dir": str(output_root / identity),
            }
    implementation_names = (
        "train_strict_v4_benign_autoencoder_warning_task_cuda.py",
        "run_strict_v4_benign_autoencoder_warning_development.py",
        "evaluate_strict_v4_benign_autoencoder_warning_development.py",
    )
    protocol: dict[str, Any] = {
        "schema_version": (
            "strict_v4_benign_autoencoder_warning_development_protocol_v1"
        ),
        "state": "frozen_before_autoencoder_effect",
        "stage": "adaptive_development",
        "parent_protocol": {
            "path": str(parent_protocol_path),
            "file_sha256": file_hash(parent_protocol_path),
            "manifest_sha256": parent["manifest_sha256"],
        },
        "source_completion": {
            "path": str(source_completion_path),
            "file_sha256": file_hash(source_completion_path),
            "manifest_sha256": source_completion["manifest_sha256"],
        },
        "baseline_qualification": {
            "path": str(baseline_qualification_path),
            "file_sha256": file_hash(baseline_qualification_path),
            "manifest_sha256": baseline["manifest_sha256"],
        },
        "suite": parent["suite"],
        "seeds": parent["seeds"],
        "scenarios": parent["scenarios"],
        "expected_task_count": expected,
        "tasks": tasks,
        "output_root": str(output_root),
        "completion_path": str(output.parent / "completion.json"),
        "result_path": str(output.parent / "evaluation.json"),
        "training": {
            "parallel_tasks": 12,
            "required_gpu_uuid": parent["resource_contract"][
                "required_gpu_uuid"
            ],
            "validation_benign_fpr_budget": 0.04,
            "latent_dim": 16,
            "epochs": 100,
            "batch_size": 512,
            "learning_rate": 0.001,
            "weight_decay": 0.0001,
            "patience": 12,
            "minimum_delta": 1e-6,
            "gpu_sample_interval_seconds": 0.1,
        },
        "alert_evaluation": {
            "candidates": [dict(candidate) for candidate in ALERT_CANDIDATES],
            "maximum_nominal_union_budget": 0.044,
        },
        "open_set_evaluation": {
            "risk_name": "knn",
            "open_score": "global_attack_tail_noisy_or",
            "open_budget": 0.04,
        },
        "resource_contract": parent["resource_contract"],
        "implementation_sha256": {
            name: file_hash(project_root / name)
            for name in implementation_names
        },
        "claim_boundary": {
            "baseline_unknown_results_informed_autoencoder_candidate": True,
            "candidate_selection_reads_current_unknown_test_results": True,
            "current_seeds_are_adaptive_development_only": True,
            "thresholds_use_known_only_validation": True,
            "autoencoder_fit_uses_benign_training_only": True,
            "fresh_unseen_seeds_required_for_confirmation": True,
            "formal_training_runs_on_cuda": True,
            "eligible_for_paper_effect_claim": False,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--parent-protocol", type=Path, required=True)
    parser.add_argument("--source-completion", type=Path, required=True)
    parser.add_argument("--baseline-qualification", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = build_protocol(
        project_root=args.project_root,
        parent_protocol_path=args.parent_protocol,
        source_completion_path=args.source_completion,
        baseline_qualification_path=args.baseline_qualification,
        output_root=args.output_root,
        output=args.output,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "expected_task_count": protocol["expected_task_count"],
                "manifest_sha256": protocol["manifest_sha256"],
                "output": str(args.output.resolve()),
                "state": protocol["state"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
