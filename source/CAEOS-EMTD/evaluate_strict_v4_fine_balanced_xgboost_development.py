from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from evaluate_strict_v4_packet_sequence_fusion_development import (
    add_benign_reference_distance_tail,
    compact,
    configurations,
    evaluate_configuration,
    selection_key,
    verify_task,
)
from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)


ATTACK_PROBABILITY_VARIANTS = ("family", "binary", "maximum", "noisy_or")


def prepared_for_variant(
    source: dict[str, dict[str, Any]],
    variant: str,
) -> dict[str, dict[str, Any]]:
    prepared = {}
    for scenario, task in source.items():
        arrays = dict(task["arrays"])
        for split in ("validation", "test"):
            key = f"{split}_{variant}_attack_probability"
            if key not in arrays:
                raise ValueError(f"task scores miss attack variant: {key}")
            arrays[f"{split}_attack_probability"] = np.asarray(
                arrays[key], dtype=np.float64
            )
        prepared[scenario] = {
            "metrics": task["metrics"],
            "arrays": arrays,
        }
    return prepared


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    completion = load_canonical(
        args.completion.resolve(), "fine-balanced CUDA completion"
    )
    if (
        completion.get("state") != "complete"
        or completion.get("failure_count") != 0
        or not completion.get("gpu_execution", {}).get("all_tasks_passed")
    ):
        raise ValueError("fine-balanced CUDA completion did not pass")
    source = {}
    task_sources = {}
    for _, task in sorted(completion["task_artifacts"].items()):
        task_dir = Path(task["output_dir"])
        metrics, arrays = verify_task(task_dir)
        add_benign_reference_distance_tail(metrics, arrays)
        scenario = str(metrics["task"]["unknown_family"])
        if scenario in source:
            raise ValueError(f"duplicate unknown-family task: {scenario}")
        source[scenario] = {"metrics": metrics, "arrays": arrays}
        task_sources[scenario] = {
            "task_dir": str(task_dir),
            "metrics_sha256": file_hash(task_dir / "metrics.json"),
            "scores_sha256": file_hash(task_dir / "scores.npz"),
            "gpu_execution_sha256": file_hash(task_dir / "gpu_execution.json"),
        }
    candidates = []
    for variant in ATTACK_PROBABILITY_VARIANTS:
        prepared = prepared_for_variant(source, variant)
        for configuration in configurations():
            enriched = dict(configuration)
            enriched["attack_probability_variant"] = variant
            candidates.append(evaluate_configuration(prepared, enriched))
    selected = max(candidates, key=selection_key)
    result: dict[str, Any] = {
        "schema_version": (
            "strict_v4_fine_balanced_xgboost_development_evaluation_v1"
        ),
        "state": (
            "development_full_gate_passed"
            if selected["gates"]["full_known_unknown_95_5_gate"]
            else "development_gate_not_met"
        ),
        "selection_seed": int(completion["seed"]),
        "candidate_count": len(candidates),
        "attack_probability_variants": list(ATTACK_PROBABILITY_VARIANTS),
        "selected": selected,
        "candidate_summaries": [compact(candidate) for candidate in candidates],
        "task_sources": task_sources,
        "completion": {
            "path": str(args.completion.resolve()),
            "file_sha256": file_hash(args.completion.resolve()),
            "manifest_sha256": completion["manifest_sha256"],
        },
        "claim_boundary": {
            "development_only": True,
            "true_unknown_used_for_configuration_selection": True,
            "fresh_confirmation_required_for_effect_claim": True,
            "fresh_confirmation_seeds_read_or_launched": False,
            "gpu_execution_proven_for_each_training_task": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    atomic_json(args.output.resolve(), result)
    return result


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--completion", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    result = evaluate(parse_arguments())
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
