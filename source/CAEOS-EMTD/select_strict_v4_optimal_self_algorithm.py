from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Optional

from create_strict_v4_external_confirmation_protocol import canonical_hash


TAIL = "caeos_tail_aware_pairwise"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select_optimal(
    protocol: dict[str, Any],
    incumbent: dict[str, Any],
    tail_confirmation: dict[str, Any],
    head_to_head: Optional[dict[str, Any]],
) -> dict[str, Any]:
    if protocol.get("schema_version") != "strict_v4_self_algorithm_tournament_protocol_v1":
        raise ValueError("unexpected tournament protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("tournament protocol SHA mismatch")
    if incumbent.get("schema_version") != "strict_v4_final_algorithm_decision_v1":
        raise ValueError("unexpected incumbent decision schema")
    if incumbent.get("manifest_sha256") != canonical_hash(incumbent):
        raise ValueError("incumbent decision SHA mismatch")
    if tail_confirmation.get("schema_version") != "strict_v4_tail_aware_confirmation_v1":
        raise ValueError("unexpected tail confirmation schema")
    if tail_confirmation.get("protocol_manifest_sha256") != protocol[
        "challenger_branch"
    ]["tail_confirmation_protocol_sha256"]:
        raise ValueError("tail confirmation protocol binding mismatch")
    incumbent_algorithm = incumbent["selected_algorithm"]
    tail_passes = tail_confirmation.get("decision", {}).get("passes") is True
    head_passes = False
    if tail_passes:
        if head_to_head is None:
            raise ValueError("passed tail challenger requires frozen head-to-head result")
        if head_to_head.get("schema_version") != "strict_v4_tail_vs_incumbent_confirmation_v1":
            raise ValueError("unexpected head-to-head schema")
        if head_to_head.get("protocol_manifest_sha256") != protocol["manifest_sha256"]:
            raise ValueError("head-to-head protocol binding mismatch")
        if head_to_head.get("validation", {}).get("incumbent_algorithm") != incumbent_algorithm:
            raise ValueError("head-to-head incumbent mismatch")
        head_passes = head_to_head.get("decision", {}).get("passes") is True
    selected = TAIL if tail_passes and head_passes else incumbent_algorithm
    result = {
        "schema_version": "strict_v4_optimal_self_algorithm_decision_v1",
        "selection_is_pre_registered": True,
        "tournament_protocol_manifest_sha256": protocol["manifest_sha256"],
        "incumbent_algorithm": incumbent_algorithm,
        "tail_challenger_confirmation_passes": tail_passes,
        "tail_vs_incumbent_replacement_gate_passes": head_passes,
        "selected_algorithm": selected,
        "selected_branch": "tail_challenger" if selected == TAIL else "incumbent",
        "status": "frozen_optimal_self_algorithm",
        "external_confirmation_seeds": (
            protocol["external_confirmation_branch"]["tail_challenger_wins"]["fresh_seeds"]
            if selected == TAIL
            else protocol["external_confirmation_branch"]["incumbent_wins"]["seeds"]
        ),
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def render(result: dict[str, Any]) -> str:
    return (
        "# Strict-v4 optimal self-algorithm decision\n\n"
        f"Selected: `{result['selected_algorithm']}`.\n\n"
        f"Tail confirmation: `{'PASS' if result['tail_challenger_confirmation_passes'] else 'FAIL'}`.\n"
        f"Tail replacement gate: `{'PASS' if result['tail_vs_incumbent_replacement_gate_passes'] else 'FAIL'}`.\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--incumbent-decision", type=Path, required=True)
    parser.add_argument("--tail-confirmation", type=Path, required=True)
    parser.add_argument("--head-to-head", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    incumbent = json.loads(args.incumbent_decision.read_text(encoding="utf-8"))
    tail = json.loads(args.tail_confirmation.read_text(encoding="utf-8"))
    head = json.loads(args.head_to_head.read_text(encoding="utf-8")) if args.head_to_head else None
    result = select_optimal(protocol, incumbent, tail, head)
    result["input_file_sha256"] = {
        "protocol": file_hash(args.protocol),
        "incumbent_decision": file_hash(args.incumbent_decision),
        "tail_confirmation": file_hash(args.tail_confirmation),
        "head_to_head": file_hash(args.head_to_head) if args.head_to_head else None,
    }
    result["selector_implementation_sha256"] = file_hash(Path(__file__))
    result["manifest_sha256"] = canonical_hash(result)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "decision.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "decision.md").write_text(render(result), encoding="utf-8")
    print(render(result), end="")


if __name__ == "__main__":
    main()
