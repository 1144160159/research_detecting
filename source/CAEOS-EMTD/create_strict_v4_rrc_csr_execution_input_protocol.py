from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def canonical(value: Dict[str, Any], schema: str) -> bool:
    return bool(
        value.get("schema_version") == schema
        and value.get("manifest_sha256") == canonical_hash(value)
    )


def create_input_protocol(
    *,
    project_root: Path,
    rrc_design: Dict[str, Any],
    rrc_core_protocol: Dict[str, Any],
    integrated_protocol: Dict[str, Any],
    krc_protocol: Dict[str, Any],
    downstream_decision: Dict[str, Any],
    input_file_sha256: Dict[str, str],
) -> Dict[str, Any]:
    if (
        not canonical(
            rrc_design, "strict_v4_rrc_csr_fallback_design_v1"
        )
        or not canonical(
            rrc_core_protocol, "strict_v4_rrc_csr_core_protocol_v1"
        )
        or not canonical(
            integrated_protocol,
            "strict_v4_krc_integrated_comprehensive_sota_protocol_v1",
        )
        or not canonical(
            krc_protocol, "strict_v4_krc_csr_confirmation_protocol_v1"
        )
        or not canonical(
            downstream_decision, "strict_v4_krc_downstream_decision_v1"
        )
        or rrc_core_protocol.get("design_manifest_sha256")
        != rrc_design["manifest_sha256"]
        or integrated_protocol.get("protocol_revision")
        != "integrity_effect_separated_negative_branch_v2"
        or downstream_decision.get("decision_revision")
        != "integrity_effect_separated_negative_branch_v2"
        or downstream_decision.get("integrated_protocol_manifest_sha256")
        != integrated_protocol["manifest_sha256"]
        or downstream_decision.get("krc_audit_integrity_passes") is not True
        or downstream_decision.get("krc_effect_gate_passes") is not False
        or downstream_decision.get("selected_algorithm") != "caeos_pairwise"
        or downstream_decision.get("downstream_execution_required") is not False
        or downstream_decision.get("rrc_fallback_execution_permitted") is not True
    ):
        raise ValueError(
            "canonical terminal-negative KRC decision and RRC design required"
        )

    registry = {
        f"{row['suite']}/{row['scenario']}": row
        for row in krc_protocol["source_registry"]
    }
    heldout = list(
        rrc_design["data_isolation"]["heldout_confirmation_identities"]
    )
    if (
        len(registry) != 102
        or len(heldout) != 83
        or len(set(heldout)) != 83
        or not set(heldout) <= set(registry)
    ):
        raise ValueError("exact 83-of-102 RRC held-out registry required")

    training_seeds = [
        int(seed) for seed in rrc_design["confirmation"]["training_seeds"]
    ]
    corruption_seeds = [
        int(seed) for seed in rrc_design["confirmation"]["corruption_seeds"]
    ]
    if (
        training_seeds != [701, 709, 719]
        or corruption_seeds != [727, 733, 739]
    ):
        raise ValueError("frozen RRC seed contract drifted")
    corruption_by_training = dict(zip(training_seeds, corruption_seeds))

    tasks = []
    source_registry = []
    for identity in sorted(heldout):
        source = registry[identity]
        source_registry.append(source)
        for training_seed in training_seeds:
            tasks.append(
                {
                    "suite": source["suite"],
                    "scenario": source["scenario"],
                    "training_seed": training_seed,
                    "corruption_seed": corruption_by_training[training_seed],
                    "source_seed": int(source["source_seed"]),
                    "source_split_fingerprint": source[
                        "source_split_fingerprint"
                    ],
                    "source_csv_sha256": source["csv_sha256"],
                    "source_config_sha256": source["config_sha256"],
                    "scenario_certificate_group": identity,
                }
            )
    if len(tasks) != 249 or len(
        {
            (task["suite"], task["scenario"], task["training_seed"])
            for task in tasks
        }
    ) != 249:
        raise ValueError("RRC task universe must be 83 scenarios x 3 seeds")

    creator_path = (
        project_root
        / "create_strict_v4_rrc_csr_execution_input_protocol.py"
    )
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_rrc_csr_execution_input_protocol_v1",
        "state": "task_universe_frozen_waiting_full_execution_chain",
        "algorithm": "rrc_csr_caeos_v1",
        "activation_gate_satisfied": True,
        "execution_admitted": False,
        "rrc_design_manifest_sha256": rrc_design["manifest_sha256"],
        "rrc_core_protocol_manifest_sha256": rrc_core_protocol[
            "manifest_sha256"
        ],
        "integrated_protocol_manifest_sha256": integrated_protocol[
            "manifest_sha256"
        ],
        "krc_protocol_manifest_sha256": krc_protocol["manifest_sha256"],
        "downstream_decision_manifest_sha256": downstream_decision[
            "manifest_sha256"
        ],
        "source_registry": source_registry,
        "source_registry_count": len(source_registry),
        "training_seeds": training_seeds,
        "corruption_seeds": corruption_seeds,
        "tasks": tasks,
        "task_counts": {
            "scenarios": 83,
            "training_seeds": 3,
            "base_csr_captures": 249,
            "scenario_certificates": 83,
            "rrc_runtime_captures": 249,
            "conditions_per_runtime": 6,
            "evaluations": 1494,
        },
        "execution_phases": [
            "base_csr_capture_249",
            "scenario_certificate_83",
            "rrc_runtime_materialization_and_roundtrip_249",
            "six_condition_evaluation_1494",
            "primary83_summary",
            "independent_audit",
        ],
        "remaining_implementation_gate": (
            rrc_core_protocol["remaining_required_components"]
        ),
        "implementation_sha256": {
            creator_path.relative_to(project_root).as_posix(): file_hash(
                creator_path
            )
        },
        "output_counts_at_freeze": {
            "execution_protocol": 0,
            "base_csr_captures": 0,
            "scenario_certificates": 0,
            "rrc_runtime_captures": 0,
            "evaluations": 0,
            "summary": 0,
            "audit": 0,
        },
        "claim_boundary": {
            "input_protocol_is_not_execution_protocol": True,
            "negative_krc_does_not_establish_rrc_effect": True,
            "rrc_uses_new_training_and_corruption_seeds": True,
            "rrc_requires_full_execution_chain_and_independent_audit": True,
            "rrc_success_would_not_alone_establish_sota": True,
        },
        "input_file_sha256": input_file_sha256,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--rrc-design", type=Path, required=True)
    parser.add_argument("--rrc-core-protocol", type=Path, required=True)
    parser.add_argument("--integrated-protocol", type=Path, required=True)
    parser.add_argument("--krc-protocol", type=Path, required=True)
    parser.add_argument("--downstream-decision", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "rrc_design": args.rrc_design,
        "rrc_core_protocol": args.rrc_core_protocol,
        "integrated_protocol": args.integrated_protocol,
        "krc_protocol": args.krc_protocol,
        "downstream_decision": args.downstream_decision,
    }
    value = create_input_protocol(
        project_root=args.project_root.resolve(),
        rrc_design=load_json(args.rrc_design),
        rrc_core_protocol=load_json(args.rrc_core_protocol),
        integrated_protocol=load_json(args.integrated_protocol),
        krc_protocol=load_json(args.krc_protocol),
        downstream_decision=load_json(args.downstream_decision),
        input_file_sha256={
            name: file_hash(path) for name, path in paths.items()
        },
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
