from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch


GATE_PREFIX = "counterfactual_conflict_gate."


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
    gate_names = sorted(set(candidate_state) - set(reference_state))
    invalid_gate_names = [name for name in gate_names if not name.startswith(GATE_PREFIX)]
    nonfinite_gate_names = [
        name
        for name in gate_names
        if not torch.isfinite(candidate_state[name]).all().item()
    ]
    arguments = candidate.get("arguments", {})
    checks = {
        "reference_tensors_all_present": not missing,
        "reference_tensors_bitwise_equal": not changed,
        "candidate_only_tensors_are_conflict_gate": bool(gate_names)
        and not invalid_gate_names,
        "gate_tensors_are_finite": not nonfinite_gate_names,
        "candidate_profile_is_counterfactual_conflict_gate": arguments.get(
            "encoder_profile"
        )
        == "mal_tls_counterfactual_conflict_gate",
        "base_freeze_flag_is_true": arguments.get("freeze_base_for_adapter") is True,
        "consistency_weight_is_one": float(arguments.get("consistency_weight", 0.0))
        == 1.0,
        "counterfactual_weight_is_one": float(
            arguments.get("counterfactual_weight", 0.0)
        )
        == 1.0,
        "counterfactual_margin_is_frozen": float(
            arguments.get("counterfactual_margin", 0.0)
        )
        == 0.05,
        "f1_tie_selection_rule_is_frozen": arguments.get(
            "prefer_last_epoch_on_known_f1_tie"
        )
        is True,
    }
    return {
        "schema_version": "mal_tls_counterfactual_conflict_gate_checkpoint_audit_v1",
        "passes": all(checks.values()),
        "checks": checks,
        "reference_tensor_count": len(reference_state),
        "gate_tensor_count": len(gate_names),
        "missing_reference_tensors": missing,
        "changed_reference_tensors": changed,
        "invalid_gate_tensor_names": invalid_gate_names,
        "nonfinite_gate_tensor_names": nonfinite_gate_names,
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
        raise RuntimeError(f"counterfactual conflict-gate checkpoint audit failed: {result}")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
