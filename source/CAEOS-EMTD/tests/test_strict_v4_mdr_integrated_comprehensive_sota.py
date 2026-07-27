from pathlib import Path

import pytest

from audit_strict_v4_mdr_integrated_comprehensive_sota import (
    audit_integrated,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_integrated_comprehensive_sota_protocol import (
    create_protocol,
)


IMPLEMENTATION = {
    "create_strict_v4_mdr_integrated_comprehensive_sota_protocol.py": "a",
    "audit_strict_v4_mdr_integrated_comprehensive_sota.py": "b",
    "scripts/wait_and_audit_strict_v4_mdr_integrated_comprehensive_sota.sh": "c",
}


def canonical(schema, **values):
    value = {"schema_version": schema, **values}
    value["manifest_sha256"] = canonical_hash(value)
    return value


def designs():
    post = canonical(
        "strict_v4_mdr_postselection_evidence_design_v1",
        activation_gate={"selected_algorithm_must_equal": "mdr_caeos_v1"},
        integrated_claim_policy={
            "accuracy_robustness_external_sota_with_deployability_requires": [
                "mdr_full102_confirmation",
                "fresh_two_dataset_external_malicious_confirmation",
                "selected_system_deployability",
                "parrot_external_benign_safety",
            ],
            "multidimensional_comprehensive_sota_additionally_requires": [
                "strict_efficiency_superiority_over_embedded_pairwise",
                "strict_efficiency_superiority_over_opendetect",
            ],
        },
    )
    efficiency = canonical(
        "strict_v4_mdr_opendetect_efficiency_design_v1"
    )
    return post, efficiency


def protocol(tmp_path: Path):
    post, efficiency = designs()
    return create_protocol(
        project_root=tmp_path,
        postselection_design=post,
        opendetect_efficiency_design=efficiency,
        input_file_sha256={"post": "p", "efficiency": "e"},
        implementation_sha256=IMPLEMENTATION,
        observed_audits=0,
    )


def linked_branch(protocol_schema, summary_schema, audit_schema, **summary):
    protocol = canonical(protocol_schema)
    summary_value = canonical(
        summary_schema,
        protocol_manifest_sha256=protocol["manifest_sha256"],
        **summary,
    )
    audit = canonical(
        audit_schema,
        protocol_manifest_sha256=protocol["manifest_sha256"],
        summary_manifest_sha256=summary_value["manifest_sha256"],
        passes=True,
    )
    return protocol, summary_value, audit


def fixture(tmp_path: Path, opendetect_gate=True):
    post, efficiency_design = designs()
    integrated = protocol(tmp_path)
    integrated = dict(integrated)
    integrated["implementation_sha256"] = {}
    integrated["manifest_sha256"] = canonical_hash(integrated)
    confirmation = linked_branch(
        "strict_v4_mdr_caeos_confirmation_protocol_v1",
        "strict_v4_mdr_caeos_confirmation_summary_v1",
        "strict_v4_mdr_caeos_confirmation_audit_v1",
        decision={"passes": True, "selected_algorithm": "mdr_caeos_v1"},
    )
    confirmation[2]["effect_decision_inherited_without_override"] = {
        "passes": True,
        "selected_algorithm": "mdr_caeos_v1",
    }
    confirmation[2]["manifest_sha256"] = canonical_hash(confirmation[2])
    external = linked_branch(
        "strict_v4_mdr_external_malicious_protocol_v1",
        "strict_v4_mdr_external_malicious_summary_v1",
        "strict_v4_mdr_external_malicious_audit_v1",
        fresh_two_dataset_external_malicious_confirmation_passes=True,
    )
    external[2]["external_effect_gate_passes"] = True
    external[2]["manifest_sha256"] = canonical_hash(external[2])
    system = linked_branch(
        "strict_v4_mdr_selected_system_protocol_v1",
        "strict_v4_mdr_selected_system_summary_v1",
        "strict_v4_mdr_selected_system_audit_v1",
        deployability_decision={"passes": True},
        strict_efficiency_decision={"passes": True},
    )
    system[2]["deployability_gate_passes"] = True
    system[2]["strict_efficiency_superiority_gate_passes"] = True
    system[2]["manifest_sha256"] = canonical_hash(system[2])
    opendetect = linked_branch(
        "strict_v4_mdr_opendetect_efficiency_protocol_v1",
        "strict_v4_mdr_opendetect_efficiency_summary_v1",
        "strict_v4_mdr_opendetect_efficiency_audit_v1",
        strict_efficiency_decision={"passes": opendetect_gate},
    )
    opendetect[2]["strict_efficiency_superiority_gate_passes"] = (
        opendetect_gate
    )
    opendetect[2]["manifest_sha256"] = canonical_hash(opendetect[2])
    parrot = linked_branch(
        "strict_v4_mdr_parrot_safety_protocol_v1",
        "strict_v4_mdr_parrot_safety_summary_v1",
        "strict_v4_mdr_parrot_safety_audit_v1",
        safety_gate_passes=True,
    )
    parrot[2]["benign_domain_shift_safety_gate_passes"] = True
    parrot[2]["claim_boundary"] = {
        "malicious_detection_accuracy_claim_supported_by_this_audit": False
    }
    parrot[2]["manifest_sha256"] = canonical_hash(parrot[2])
    selection = canonical(
        "strict_v4_final_self_algorithm_selection_v2",
        selected_algorithm="mdr_caeos_v1",
        mdr_confirmation_passes=True,
        protocol_manifest_sha256=confirmation[0]["manifest_sha256"],
        summary_manifest_sha256=confirmation[1]["manifest_sha256"],
    )
    return {
        "project_root": tmp_path,
        "integrated_protocol": integrated,
        "postselection_design": post,
        "opendetect_efficiency_design": efficiency_design,
        "selection": selection,
        "confirmation_protocol": confirmation[0],
        "confirmation_summary": confirmation[1],
        "confirmation_audit": confirmation[2],
        "external_protocol": external[0],
        "external_summary": external[1],
        "external_audit": external[2],
        "system_protocol": system[0],
        "system_summary": system[1],
        "system_audit": system[2],
        "opendetect_protocol": opendetect[0],
        "opendetect_summary": opendetect[1],
        "opendetect_audit": opendetect[2],
        "parrot_protocol": parrot[0],
        "parrot_summary": parrot[1],
        "parrot_audit": parrot[2],
        "input_file_sha256": {f"input_{index}": "hash" for index in range(19)},
    }


def test_protocol_freezes_two_claim_tiers_before_output(tmp_path):
    value = protocol(tmp_path)
    assert value["integrated_audit_count_at_freeze"] == 0
    assert value["claim_tiers"]["tier2_additionally_requires"] == [
        "strict_efficiency_superiority_over_embedded_pairwise",
        "strict_efficiency_superiority_over_opendetect",
    ]
    assert value["manifest_sha256"] == canonical_hash(value)


def test_protocol_rejects_post_result_freeze(tmp_path):
    post, efficiency = designs()
    with pytest.raises(ValueError, match="before audit outputs"):
        create_protocol(
            project_root=tmp_path,
            postselection_design=post,
            opendetect_efficiency_design=efficiency,
            input_file_sha256={},
            implementation_sha256=IMPLEMENTATION,
            observed_audits=1,
        )


def test_integrated_audit_supports_tier2_only_when_every_gate_passes(tmp_path):
    value = audit_integrated(**fixture(tmp_path, opendetect_gate=True))
    assert value["passes"] is True
    assert (
        value[
            "accuracy_robustness_external_sota_with_deployability_supported"
        ]
        is True
    )
    assert value["multidimensional_comprehensive_sota_supported"] is True
    assert value["claim_boundary"]["universal_sota_claim_supported"] is False


def test_failed_efficiency_gate_preserves_tier1_without_tier2(tmp_path):
    value = audit_integrated(**fixture(tmp_path, opendetect_gate=False))
    assert value["passes"] is True
    assert (
        value[
            "accuracy_robustness_external_sota_with_deployability_supported"
        ]
        is True
    )
    assert value["multidimensional_comprehensive_sota_supported"] is False
    assert "accuracy_robustness" in value["claim_tier"]


def test_watcher_refuses_post_result_protocol_freeze():
    path = (
        Path(__file__).parents[1]
        / "scripts"
        / "wait_and_audit_strict_v4_mdr_integrated_comprehensive_sota.sh"
    )
    text = path.read_text(encoding="utf-8")
    assert "refusing post-result freeze" in text
    assert "parrot-protocol" in text
    assert "opendetect-audit" in text
