from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch


def verify(reference_path: Path, candidate_path: Path) -> dict[str, object]:
    reference = torch.load(reference_path, map_location="cpu")
    candidate = torch.load(candidate_path, map_location="cpu")
    reference_state = reference["model_state"]
    candidate_state = candidate["model_state"]
    missing = sorted(set(reference_state) - set(candidate_state))
    changed = sorted(
        name
        for name, value in reference_state.items()
        if name in candidate_state and not torch.equal(value, candidate_state[name])
    )
    adapter_names = sorted(set(candidate_state) - set(reference_state))
    invalid_adapter_names = [
        name for name in adapter_names if not name.startswith("evidence_adapters.")
    ]
    nonfinite_adapter_names = [
        name
        for name in adapter_names
        if not torch.isfinite(candidate_state[name]).all().item()
    ]
    candidate_arguments = candidate.get("arguments", {})
    checks = {
        "reference_tensors_all_present": not missing,
        "reference_tensors_bitwise_equal": not changed,
        "candidate_only_tensors_are_adapters": bool(adapter_names)
        and not invalid_adapter_names,
        "adapter_tensors_are_finite": not nonfinite_adapter_names,
        "candidate_profile_is_geometry_preserving": candidate_arguments.get(
            "encoder_profile"
        )
        == "mal_tls_geometry_preserving_adapter",
        "base_freeze_flag_is_true": candidate_arguments.get(
            "freeze_base_for_adapter"
        )
        is True,
        "consistency_weight_is_positive": float(
            candidate_arguments.get("consistency_weight", 0.0)
        )
        > 0.0,
    }
    return {
        "schema_version": "mal_tls_geometry_preserving_checkpoint_audit_v1",
        "passes": all(checks.values()),
        "checks": checks,
        "reference_tensor_count": len(reference_state),
        "adapter_tensor_count": len(adapter_names),
        "missing_reference_tensors": missing,
        "changed_reference_tensors": changed,
        "invalid_adapter_tensor_names": invalid_adapter_names,
        "nonfinite_adapter_tensor_names": nonfinite_adapter_names,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.reference, args.candidate)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if not result["passes"]:
        raise RuntimeError(f"geometry-preserving checkpoint audit failed: {result}")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
