from __future__ import annotations

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_rrc_csr_execution_input_protocol import (
    create_input_protocol,
)


def canonical(value):
    value["manifest_sha256"] = canonical_hash(value)
    return value


def fixtures(tmp_path):
    identities = [
        f"suite{index // 20}/scenario{index:03d}" for index in range(102)
    ]
    heldout = identities[19:]
    design = canonical(
        {
            "schema_version": "strict_v4_rrc_csr_fallback_design_v1",
            "data_isolation": {
                "heldout_confirmation_identities": heldout,
            },
            "confirmation": {
                "training_seeds": [701, 709, 719],
                "corruption_seeds": [727, 733, 739],
            },
        }
    )
    core = canonical(
        {
            "schema_version": "strict_v4_rrc_csr_core_protocol_v1",
            "design_manifest_sha256": design["manifest_sha256"],
            "remaining_required_components": ["runner"],
        }
    )
    integrated = canonical(
        {
            "schema_version": (
                "strict_v4_krc_integrated_comprehensive_sota_protocol_v1"
            ),
            "protocol_revision": (
                "integrity_effect_separated_negative_branch_v2"
            ),
        }
    )
    krc = canonical(
        {
            "schema_version": "strict_v4_krc_csr_confirmation_protocol_v1",
            "source_registry": [
                {
                    "suite": identity.split("/", 1)[0],
                    "scenario": identity.split("/", 1)[1],
                    "source_seed": 137,
                    "source_split_fingerprint": f"split-{index}",
                    "csv_sha256": f"{index:064x}",
                    "config_sha256": f"{index + 102:064x}",
                }
                for index, identity in enumerate(identities)
            ],
        }
    )
    decision = canonical(
        {
            "schema_version": "strict_v4_krc_downstream_decision_v1",
            "decision_revision": (
                "integrity_effect_separated_negative_branch_v2"
            ),
            "integrated_protocol_manifest_sha256": integrated[
                "manifest_sha256"
            ],
            "krc_audit_integrity_passes": True,
            "krc_effect_gate_passes": False,
            "selected_algorithm": "caeos_pairwise",
            "downstream_execution_required": False,
            "rrc_fallback_execution_permitted": True,
        }
    )
    return design, core, integrated, krc, decision


def test_negative_decision_freezes_exact_83_by_3_task_universe(
    tmp_path,
) -> None:
    design, core, integrated, krc, decision = fixtures(tmp_path)
    value = create_input_protocol(
        project_root=__import__("pathlib").Path(__file__).resolve().parents[1],
        rrc_design=design,
        rrc_core_protocol=core,
        integrated_protocol=integrated,
        krc_protocol=krc,
        downstream_decision=decision,
        input_file_sha256={"input": "a" * 64},
    )
    assert value["activation_gate_satisfied"] is True
    assert value["execution_admitted"] is False
    assert value["source_registry_count"] == 83
    assert value["task_counts"]["base_csr_captures"] == 249
    assert value["task_counts"]["evaluations"] == 1494
    assert len(value["tasks"]) == 249
    assert {
        task["training_seed"] for task in value["tasks"]
    } == {701, 709, 719}


def test_positive_krc_decision_cannot_freeze_rrc_input(tmp_path) -> None:
    design, core, integrated, krc, decision = fixtures(tmp_path)
    decision["krc_effect_gate_passes"] = True
    decision["selected_algorithm"] = "krc_csr_caeos_v1"
    decision["downstream_execution_required"] = True
    decision["rrc_fallback_execution_permitted"] = False
    decision["manifest_sha256"] = canonical_hash(decision)
    with pytest.raises(ValueError):
        create_input_protocol(
            project_root=__import__("pathlib").Path(__file__).resolve().parents[1],
            rrc_design=design,
            rrc_core_protocol=core,
            integrated_protocol=integrated,
            krc_protocol=krc,
            downstream_decision=decision,
            input_file_sha256={"input": "a" * 64},
        )
