from create_strict_v4_external_confirmation_protocol import canonical_hash
from audit_strict_v4_krc_integrated_comprehensive_sota import (
    audit_integrated,
)
from finalize_strict_v4_krc_downstream_decision import decide


def canonical(value):
    value["manifest_sha256"] = canonical_hash(value)
    return value


def confirmation(positive=True):
    protocol = canonical(
        {"schema_version": "strict_v4_krc_csr_confirmation_protocol_v1"}
    )
    summary = canonical(
        {
            "schema_version": (
                "strict_v4_krc_csr_confirmation_summary_v1"
            ),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "passes": positive,
            "selection": (
                "krc_csr_caeos_v1" if positive else "caeos_pairwise"
            ),
            "authorize_external_safety_efficiency_confirmation": positive,
        }
    )
    audit = canonical(
        {
            "schema_version": (
                "strict_v4_krc_csr_confirmation_audit_v1"
            ),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "summary_manifest_sha256": summary["manifest_sha256"],
            "passes": True,
            "decision_matches_summary": positive,
        }
    )
    return protocol, summary, audit


def integrated_protocol():
    schemas = {
        "krc_confirmation": (
            "strict_v4_krc_csr_confirmation_protocol_v1",
            "strict_v4_krc_csr_confirmation_summary_v1",
            "strict_v4_krc_csr_confirmation_audit_v1",
        ),
        "external_malicious": (
            "strict_v4_krc_external_malicious_execution_protocol_v1",
            "strict_v4_krc_external_malicious_summary_v1",
            "strict_v4_krc_external_malicious_audit_v1",
        ),
        "selected_system": (
            "strict_v4_krc_selected_system_protocol_v1",
            "strict_v4_krc_selected_system_summary_v1",
            "strict_v4_krc_selected_system_audit_v1",
        ),
        "opendetect_efficiency": (
            "strict_v4_krc_opendetect_efficiency_protocol_v1",
            "strict_v4_krc_opendetect_efficiency_summary_v1",
            "strict_v4_krc_opendetect_efficiency_audit_v1",
        ),
        "external_benign_safety": (
            "strict_v4_krc_parrot_safety_protocol_v1",
            "strict_v4_krc_parrot_safety_summary_v1",
            "strict_v4_krc_parrot_safety_audit_v1",
        ),
    }
    return canonical(
        {
            "schema_version": (
                "strict_v4_krc_integrated_comprehensive_sota_protocol_v1"
            ),
            "downstream_design_manifest_sha256": None,
            "required_branches": {
                name: {
                    "protocol_schema": values[0],
                    "summary_schema": values[1],
                    "audit_schema": values[2],
                    **(
                        {"malicious_accuracy_evidence": False}
                        if name == "external_benign_safety"
                        else {}
                    ),
                }
                for name, values in schemas.items()
            },
            "claim_boundary": {
                "no_dataset_metric_scenario_suite_or_component_splicing": True
            },
            "implementation_sha256": {},
        }
    )


def branch(schema, summary_fields=None, audit_fields=None):
    protocol = canonical({"schema_version": schema[0]})
    summary = canonical(
        {
            "schema_version": schema[1],
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            **(summary_fields or {}),
        }
    )
    audit = canonical(
        {
            "schema_version": schema[2],
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "summary_manifest_sha256": summary["manifest_sha256"],
            "passes": True,
            **(audit_fields or {}),
        }
    )
    return protocol, summary, audit


def fixtures():
    integrated = integrated_protocol()
    design = canonical(
        {"schema_version": "strict_v4_krc_downstream_sota_design_v1"}
    )
    integrated["downstream_design_manifest_sha256"] = design[
        "manifest_sha256"
    ]
    integrated["manifest_sha256"] = canonical_hash(integrated)
    confirm = confirmation()
    decision = canonical(
        {
            "schema_version": "strict_v4_krc_downstream_decision_v1",
            "integrated_protocol_manifest_sha256": integrated[
                "manifest_sha256"
            ],
            "krc_confirmation_passes": True,
            "downstream_execution_required": True,
            "selected_algorithm": "krc_csr_caeos_v1",
        }
    )
    specs = integrated["required_branches"]
    branches = {
        "krc_confirmation": confirm,
        "external_malicious": branch(
            (
                specs["external_malicious"]["protocol_schema"],
                specs["external_malicious"]["summary_schema"],
                specs["external_malicious"]["audit_schema"],
            ),
            {
                "fresh_two_dataset_external_malicious_confirmation_passes": True
            },
            {"external_effect_gate_passes": True},
        ),
        "selected_system": branch(
            (
                specs["selected_system"]["protocol_schema"],
                specs["selected_system"]["summary_schema"],
                specs["selected_system"]["audit_schema"],
            ),
            {
                "deployability_decision": {"passes": True},
                "strict_efficiency_decision": {"passes": True},
            },
            {
                "deployability_gate_passes": True,
                "strict_efficiency_superiority_gate_passes": True,
            },
        ),
        "opendetect_efficiency": branch(
            (
                specs["opendetect_efficiency"]["protocol_schema"],
                specs["opendetect_efficiency"]["summary_schema"],
                specs["opendetect_efficiency"]["audit_schema"],
            ),
            {"strict_efficiency_decision": {"passes": True}},
            {"strict_efficiency_superiority_gate_passes": True},
        ),
        "external_benign_safety": branch(
            (
                specs["external_benign_safety"]["protocol_schema"],
                specs["external_benign_safety"]["summary_schema"],
                specs["external_benign_safety"]["audit_schema"],
            ),
            {"safety_gate_passes": True},
            {
                "benign_domain_shift_safety_gate_passes": True,
                "claim_boundary": {
                    "malicious_detection_accuracy_claim_supported_by_this_audit": False
                },
            },
        ),
    }
    return integrated, design, decision, branches


def test_negative_confirmation_writes_terminal_pairwise_decision():
    integrated = integrated_protocol()
    protocol, summary, audit = confirmation(positive=False)
    value = decide(
        integrated_protocol=integrated,
        confirmation_protocol=protocol,
        confirmation_summary=summary,
        confirmation_audit=audit,
        input_file_sha256={"input": "a" * 64},
    )
    assert value["selected_algorithm"] == "caeos_pairwise"
    assert value["downstream_execution_required"] is False
    assert value["required_next_outputs"] == []


def test_positive_confirmation_activates_all_downstream_branches():
    integrated = integrated_protocol()
    protocol, summary, audit = confirmation(positive=True)
    value = decide(
        integrated_protocol=integrated,
        confirmation_protocol=protocol,
        confirmation_summary=summary,
        confirmation_audit=audit,
        input_file_sha256={"input": "a" * 64},
    )
    assert value["selected_algorithm"] == "krc_csr_caeos_v1"
    assert value["downstream_execution_required"] is True
    assert len(value["required_next_outputs"]) == 5


def test_integrated_audit_supports_tier2_only_when_all_gates_pass(tmp_path):
    integrated, design, decision, branches = fixtures()
    result = audit_integrated(
        project_root=tmp_path,
        integrated_protocol=integrated,
        downstream_design=design,
        downstream_decision=decision,
        branch_values=branches,
        input_file_sha256={str(index): "a" * 64 for index in range(18)},
    )
    assert result["passes"] is True
    assert result["comprehensive_sota_confirmed"] is True


def test_efficiency_failure_preserves_tier1(tmp_path):
    integrated, design, decision, branches = fixtures()
    protocol, summary, audit = branches["opendetect_efficiency"]
    summary["strict_efficiency_decision"]["passes"] = False
    summary["manifest_sha256"] = canonical_hash(summary)
    audit["summary_manifest_sha256"] = summary["manifest_sha256"]
    audit["strict_efficiency_superiority_gate_passes"] = False
    audit["manifest_sha256"] = canonical_hash(audit)
    result = audit_integrated(
        project_root=tmp_path,
        integrated_protocol=integrated,
        downstream_design=design,
        downstream_decision=decision,
        branch_values=branches,
        input_file_sha256={str(index): "a" * 64 for index in range(18)},
    )
    assert (
        result[
            "accuracy_robustness_external_sota_with_deployability_supported"
        ]
        is True
    )
    assert result["comprehensive_sota_confirmed"] is False
