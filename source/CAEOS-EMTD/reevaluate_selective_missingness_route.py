from __future__ import annotations

import argparse
import json
from pathlib import Path

from evaluate_dual_path_robustness import evaluate_pair
from summarize_missingness_routed_expansion import validate_manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Replay a modality-selective missingness routing policy"
    )
    parser.add_argument("--detector-root", type=Path, required=True)
    parser.add_argument("--classifier-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    manifest = validate_manifest(args.manifest)
    routing_modalities = tuple(int(value) for value in manifest["selected_routing_modalities"])
    evaluation_role = str(
        manifest.get(
            "evaluation_role",
            "post_rejection_selective_route_replay_not_confirmation",
        )
    )
    args.output_root.mkdir(parents=True, exist_ok=True)
    completed = 0
    for scenario in manifest["scenarios"]:
        for seed in manifest["seeds"]:
            for modality in manifest["modalities"]:
                run_id = f"{scenario}_seed{seed}_m{modality}"
                result = evaluate_pair(
                    args.detector_root / run_id,
                    args.classifier_root / run_id,
                    prediction_routing="missingness",
                    routing_modalities=routing_modalities,
                )
                result["evaluation_role"] = evaluation_role
                (args.output_root / f"{run_id}.json").write_text(
                    json.dumps(result, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                completed += 1
    outputs = list(args.output_root.glob("*.json"))
    if completed != manifest["expected_pair_count"] or len(outputs) != completed:
        raise ValueError("selective replay output count mismatch")
    print(json.dumps({"state": "complete", "pairs": completed}, sort_keys=True))


if __name__ == "__main__":
    main()
