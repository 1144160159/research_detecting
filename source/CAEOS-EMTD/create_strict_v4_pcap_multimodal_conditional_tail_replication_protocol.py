from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from strict_v4_cic_iot2023_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)


FIXED_METHOD = "CCTF-DualPathMax"
RESERVED_CONFIRMATION_SEEDS = {331, 337, 347}


def build_protocol(
    *,
    source_diagnostic_path: Path,
    target_training_protocol_path: Path,
) -> dict[str, Any]:
    source_path = source_diagnostic_path.resolve()
    target_path = target_training_protocol_path.resolve()
    source = load_canonical(source_path, "source development diagnostic")
    target = load_canonical(target_path, "target training protocol")
    if (
        source.get("state") != "complete_development_diagnostic"
        or source["selected_development_candidate"]["selected_candidate"]
        != FIXED_METHOD
        or not source["claim_boundary"][
            "unknown_test_used_for_candidate_selection"
        ]
    ):
        raise ValueError("source diagnostic does not freeze the expected method")
    if (
        target.get("state") != "frozen_before_development_effects"
        or target["algorithm"]["model_source"] != "fresh_training"
        or target["claim_boundary"][
            "frozen_model_calibrator_and_split_reused"
        ]
    ):
        raise ValueError("target protocol is not a fresh frozen training run")
    target_seed = int(target["protocol"]["development_seed"])
    source_seed = 283
    if (
        target_seed == source_seed
        or target_seed in RESERVED_CONFIRMATION_SEEDS
    ):
        raise ValueError("target seed is not a fresh development seed")
    result_root = Path(target["paths"]["result_root"])
    if any(
        (result_root / name).exists()
        for name in ("completion.json", "evaluation.json")
    ):
        raise ValueError("target effects exist before method freeze")

    evaluator_path = (
        Path(__file__).resolve().parent
        / "evaluate_strict_v4_pcap_multimodal_conditional_tail_fusion.py"
    )
    protocol: dict[str, Any] = {
        "schema_version": (
            "strict_v4_pcap_multimodal_conditional_tail_"
            "replication_protocol_v1"
        ),
        "state": "frozen_before_replication_effects",
        "selected_method": FIXED_METHOD,
        "method_definition": source["methods"][FIXED_METHOD],
        "component_order": source["component_order"],
        "source_seed": source_seed,
        "target_seed": target_seed,
        "source_development_diagnostic": {
            "path": str(source_path),
            "file_sha256": file_hash(source_path),
            "manifest_sha256": source["manifest_sha256"],
        },
        "target_training_protocol": {
            "path": str(target_path),
            "file_sha256": file_hash(target_path),
            "manifest_sha256": target["manifest_sha256"],
        },
        "implementation_sha256": {
            evaluator_path.name: file_hash(evaluator_path),
            Path(__file__).name: file_hash(Path(__file__).resolve()),
        },
        "claim_boundary": {
            "method_selected_on_source_development_unknown": True,
            "method_frozen_before_target_training_effects": True,
            "method_reselection_on_target_unknown_permitted": False,
            "target_unknown_used_to_fit_scores_or_thresholds": False,
            "reserved_confirmation_seed_used": False,
            "development_replication_only": True,
            "confirmation_claim_not_permitted": True,
            "sota_claim_not_permitted": True,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-diagnostic", type=Path, required=True)
    parser.add_argument(
        "--target-training-protocol",
        type=Path,
        required=True,
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise ValueError(f"refusing to overwrite frozen protocol: {output}")
    protocol = build_protocol(
        source_diagnostic_path=args.source_diagnostic,
        target_training_protocol_path=args.target_training_protocol,
    )
    atomic_json(output, protocol)
    print(
        {
            "output": str(output),
            "manifest_sha256": protocol["manifest_sha256"],
            "selected_method": protocol["selected_method"],
            "target_seed": protocol["target_seed"],
        }
    )


if __name__ == "__main__":
    main()
