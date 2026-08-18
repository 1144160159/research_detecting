from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evaluate_strict_v4_dual_metric_contrastive_development import (
    ATTACK_PROBABILITY_VARIANTS,
    prepared_for_variant,
)
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
)


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    task_dir = args.task_dir.resolve()
    metrics, arrays = verify_task(task_dir)
    add_benign_reference_distance_tail(metrics, arrays)
    scenario = str(metrics["task"]["unknown_family"])
    source = {scenario: {"metrics": metrics, "arrays": arrays}}
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
            "strict_v4_dual_metric_contrastive_pilot_evaluation_v1"
        ),
        "state": "pilot_complete",
        "scenario": scenario,
        "candidate_count": len(candidates),
        "selected": selected,
        "candidate_summaries": [compact(candidate) for candidate in candidates],
        "task_source": {
            "task_dir": str(task_dir),
            "metrics_sha256": file_hash(task_dir / "metrics.json"),
            "scores_sha256": file_hash(task_dir / "scores.npz"),
            "gpu_execution_sha256": file_hash(task_dir / "gpu_execution.json"),
        },
        "claim_boundary": {
            "development_pilot_only": True,
            "true_unknown_used_for_pilot_configuration_selection": True,
            "fresh_confirmation_effect_claim_authorized": False,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    atomic_json(args.output.resolve(), result)
    return result


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    result = evaluate(parse_arguments())
    print(
        json.dumps(
            {
                "manifest_sha256": result["manifest_sha256"],
                "selected": result["selected"],
                "state": result["state"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
