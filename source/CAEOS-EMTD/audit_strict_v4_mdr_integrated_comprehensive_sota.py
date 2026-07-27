from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def canonical(value: Dict[str, Any], schema: str) -> bool:
    return (
        value.get("schema_version") == schema
        and value.get("manifest_sha256") == canonical_hash(value)
    )


def branch_integrity(
    branch: Dict[str, Any],
    protocol: Dict[str, Any],
    summary: Dict[str, Any],
    audit: Dict[str, Any],
) -> Dict[str, bool]:
    return {
        "protocol_is_canonical": canonical(
            protocol, branch["protocol_schema"]
        ),
        "summary_is_canonical": canonical(
            summary, branch["summary_schema"]
        ),
        "audit_is_canonical": canonical(audit, branch["audit_schema"]),
        "summary_binds_protocol": (
            summary.get("protocol_manifest_sha256")
            == protocol.get("manifest_sha256")
        ),
        "audit_binds_protocol": (
            audit.get("protocol_manifest_sha256")
            == protocol.get("manifest_sha256")
        ),
        "audit_binds_summary": (
            audit.get("summary_manifest_sha256")
            == summary.get("manifest_sha256")
        ),
        "branch_audit_passes": audit.get("passes") is True,
    }


def audit_integrated(
    *,
    project_root: Path,
    integrated_protocol: Dict[str, Any],
    postselection_design: Dict[str, Any],
    opendetect_efficiency_design: Dict[str, Any],
    selection: Dict[str, Any],
    confirmation_protocol: Dict[str, Any],
    confirmation_summary: Dict[str, Any],
    confirmation_audit: Dict[str, Any],
    external_protocol: Dict[str, Any],
    external_summary: Dict[str, Any],
    external_audit: Dict[str, Any],
    system_protocol: Dict[str, Any],
    system_summary: Dict[str, Any],
    system_audit: Dict[str, Any],
    opendetect_protocol: Dict[str, Any],
    opendetect_summary: Dict[str, Any],
    opendetect_audit: Dict[str, Any],
    parrot_protocol: Dict[str, Any],
    parrot_summary: Dict[str, Any],
    parrot_audit: Dict[str, Any],
    input_file_sha256: Dict[str, str],
) -> Dict[str, Any]:
    protocol_ok = canonical(
        integrated_protocol,
        "strict_v4_mdr_integrated_comprehensive_sota_protocol_v1",
    )
    postselection_ok = canonical(
        postselection_design,
        "strict_v4_mdr_postselection_evidence_design_v1",
    )
    opendetect_design_ok = canonical(
        opendetect_efficiency_design,
        "strict_v4_mdr_opendetect_efficiency_design_v1",
    )
    designs_bound = (
        postselection_ok
        and opendetect_design_ok
        and integrated_protocol.get(
            "postselection_design_manifest_sha256"
        )
        == postselection_design.get("manifest_sha256")
        and integrated_protocol.get(
            "opendetect_efficiency_design_manifest_sha256"
        )
        == opendetect_efficiency_design.get("manifest_sha256")
    )
    implementation_ok = all(
        (project_root / relative).is_file()
        and file_hash(project_root / relative) == expected
        for relative, expected in integrated_protocol.get(
            "implementation_sha256", {}
        ).items()
    )
    selection_ok = canonical(
        selection, "strict_v4_final_self_algorithm_selection_v2"
    )
    selected_mdr = (
        selection_ok
        and selection.get("selected_algorithm") == "mdr_caeos_v1"
        and selection.get("mdr_confirmation_passes") is True
        and selection.get("protocol_manifest_sha256")
        == confirmation_protocol.get("manifest_sha256")
        and selection.get("summary_manifest_sha256")
        == confirmation_summary.get("manifest_sha256")
    )
    branches = integrated_protocol["required_branches"]
    branch_values = {
        "mdr_confirmation": (
            confirmation_protocol,
            confirmation_summary,
            confirmation_audit,
        ),
        "external_malicious": (
            external_protocol,
            external_summary,
            external_audit,
        ),
        "selected_system": (
            system_protocol,
            system_summary,
            system_audit,
        ),
        "opendetect_efficiency": (
            opendetect_protocol,
            opendetect_summary,
            opendetect_audit,
        ),
        "external_benign_safety": (
            parrot_protocol,
            parrot_summary,
            parrot_audit,
        ),
    }
    branch_checks = {
        name: branch_integrity(
            branches[name],
            branch_values[name][0],
            branch_values[name][1],
            branch_values[name][2],
        )
        for name in branch_values
    }
    branch_integrity_passes = {
        name: all(checks.values())
        for name, checks in branch_checks.items()
    }
    confirmation_gate = (
        branch_integrity_passes["mdr_confirmation"]
        and confirmation_summary.get("decision", {}).get("passes") is True
        and confirmation_summary.get("decision", {}).get(
            "selected_algorithm"
        )
        == "mdr_caeos_v1"
        and confirmation_audit.get(
            "effect_decision_inherited_without_override", {}
        ).get("passes")
        is True
    )
    external_gate = (
        branch_integrity_passes["external_malicious"]
        and external_summary.get(
            "fresh_two_dataset_external_malicious_confirmation_passes"
        )
        is True
        and external_audit.get("external_effect_gate_passes") is True
    )
    deployability_gate = (
        branch_integrity_passes["selected_system"]
        and system_summary.get("deployability_decision", {}).get("passes")
        is True
        and system_audit.get("deployability_gate_passes") is True
    )
    pairwise_efficiency_gate = (
        branch_integrity_passes["selected_system"]
        and system_summary.get("strict_efficiency_decision", {}).get(
            "passes"
        )
        is True
        and system_audit.get(
            "strict_efficiency_superiority_gate_passes"
        )
        is True
    )
    opendetect_efficiency_gate = (
        branch_integrity_passes["opendetect_efficiency"]
        and opendetect_summary.get(
            "strict_efficiency_decision", {}
        ).get("passes")
        is True
        and opendetect_audit.get(
            "strict_efficiency_superiority_gate_passes"
        )
        is True
    )
    parrot_safety_gate = (
        branch_integrity_passes["external_benign_safety"]
        and parrot_summary.get("safety_gate_passes") is True
        and parrot_audit.get(
            "benign_domain_shift_safety_gate_passes"
        )
        is True
        and parrot_audit.get("claim_boundary", {}).get(
            "malicious_detection_accuracy_claim_supported_by_this_audit"
        )
        is False
    )
    integrity_checks = {
        "integrated_protocol_is_canonical": protocol_ok,
        "frozen_designs_are_canonical_and_bound": designs_bound,
        "implementation_hashes_match": implementation_ok,
        "selection_is_canonical_and_selects_mdr": selected_mdr,
        "all_branch_integrity_audits_pass": all(
            branch_integrity_passes.values()
        ),
        "input_file_hash_registry_complete": (
            len(input_file_sha256) == 19
            and all(input_file_sha256.values())
        ),
        "parrot_role_boundary_preserved": (
            branches["external_benign_safety"].get(
                "malicious_accuracy_evidence"
            )
            is False
        ),
        "no_splicing_policy_preserved": (
            integrated_protocol.get("claim_boundary", {}).get(
                "no_dataset_metric_scenario_suite_or_component_splicing"
            )
            is True
        ),
    }
    integrity_passes = all(integrity_checks.values())
    tier1 = bool(
        integrity_passes
        and confirmation_gate
        and external_gate
        and deployability_gate
        and parrot_safety_gate
    )
    tier2 = bool(
        tier1 and pairwise_efficiency_gate and opendetect_efficiency_gate
    )
    if tier2:
        claim_tier = (
            "multidimensional_comprehensive_sota_within_frozen_scope"
        )
    elif tier1:
        claim_tier = (
            "accuracy_robustness_external_sota_with_deployability_"
            "within_frozen_scope"
        )
    else:
        claim_tier = "integrated_sota_not_supported"
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_mdr_integrated_comprehensive_sota_audit_v1"
        ),
        "status": "complete",
        "selected_algorithm": selection.get("selected_algorithm"),
        "integrated_protocol_manifest_sha256": integrated_protocol.get(
            "manifest_sha256"
        ),
        "postselection_design_manifest_sha256": postselection_design.get(
            "manifest_sha256"
        ),
        "opendetect_efficiency_design_manifest_sha256": (
            opendetect_efficiency_design.get("manifest_sha256")
        ),
        "integrity_checks": integrity_checks,
        "branch_integrity_checks": branch_checks,
        "branch_integrity_passes": branch_integrity_passes,
        "passes": integrity_passes,
        "evidence_gates": {
            "mdr_full102_confirmation": confirmation_gate,
            "fresh_two_dataset_external_malicious_confirmation": (
                external_gate
            ),
            "selected_system_deployability": deployability_gate,
            "parrot_external_benign_safety": parrot_safety_gate,
            "strict_efficiency_superiority_over_embedded_pairwise": (
                pairwise_efficiency_gate
            ),
            "strict_efficiency_superiority_over_opendetect": (
                opendetect_efficiency_gate
            ),
        },
        "accuracy_robustness_external_sota_with_deployability_supported": (
            tier1
        ),
        "multidimensional_comprehensive_sota_supported": tier2,
        "comprehensive_sota_confirmed": tier2,
        "claim_tier": claim_tier,
        "claim_scope": (
            "frozen_strict_v4_comparator_dataset_and_metric_universe"
        ),
        "paper_writing_evidence_ready": integrity_passes,
        "claim_boundary": {
            **integrated_protocol["claim_boundary"],
            "parrot_used_only_for_benign_false_alert_safety": True,
            "parrot_malicious_accuracy_claim_supported": False,
            "tier1_does_not_imply_strict_efficiency_superiority": True,
            "universal_sota_claim_supported": False,
        },
        "input_file_sha256": input_file_sha256,
        "input_manifest_sha256": {
            "selection": selection.get("manifest_sha256"),
            "confirmation_protocol": confirmation_protocol.get(
                "manifest_sha256"
            ),
            "confirmation_summary": confirmation_summary.get(
                "manifest_sha256"
            ),
            "confirmation_audit": confirmation_audit.get(
                "manifest_sha256"
            ),
            "external_protocol": external_protocol.get("manifest_sha256"),
            "external_summary": external_summary.get("manifest_sha256"),
            "external_audit": external_audit.get("manifest_sha256"),
            "system_protocol": system_protocol.get("manifest_sha256"),
            "system_summary": system_summary.get("manifest_sha256"),
            "system_audit": system_audit.get("manifest_sha256"),
            "opendetect_protocol": opendetect_protocol.get(
                "manifest_sha256"
            ),
            "opendetect_summary": opendetect_summary.get(
                "manifest_sha256"
            ),
            "opendetect_audit": opendetect_audit.get("manifest_sha256"),
            "parrot_protocol": parrot_protocol.get("manifest_sha256"),
            "parrot_summary": parrot_summary.get("manifest_sha256"),
            "parrot_audit": parrot_audit.get("manifest_sha256"),
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--integrated-protocol", type=Path, required=True)
    parser.add_argument("--postselection-design", type=Path, required=True)
    parser.add_argument(
        "--opendetect-efficiency-design", type=Path, required=True
    )
    parser.add_argument("--selection", type=Path, required=True)
    for name in (
        "confirmation",
        "external",
        "system",
        "opendetect",
        "parrot",
    ):
        parser.add_argument(f"--{name}-protocol", type=Path, required=True)
        parser.add_argument(f"--{name}-summary", type=Path, required=True)
        parser.add_argument(f"--{name}-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "integrated_protocol": args.integrated_protocol,
        "postselection_design": args.postselection_design,
        "opendetect_efficiency_design": (
            args.opendetect_efficiency_design
        ),
        "selection": args.selection,
        "confirmation_protocol": args.confirmation_protocol,
        "confirmation_summary": args.confirmation_summary,
        "confirmation_audit": args.confirmation_audit,
        "external_protocol": args.external_protocol,
        "external_summary": args.external_summary,
        "external_audit": args.external_audit,
        "system_protocol": args.system_protocol,
        "system_summary": args.system_summary,
        "system_audit": args.system_audit,
        "opendetect_protocol": args.opendetect_protocol,
        "opendetect_summary": args.opendetect_summary,
        "opendetect_audit": args.opendetect_audit,
        "parrot_protocol": args.parrot_protocol,
        "parrot_summary": args.parrot_summary,
        "parrot_audit": args.parrot_audit,
    }
    documents = {name: load(path) for name, path in paths.items()}
    value = audit_integrated(
        project_root=args.project_root,
        integrated_protocol=documents["integrated_protocol"],
        postselection_design=documents["postselection_design"],
        opendetect_efficiency_design=documents[
            "opendetect_efficiency_design"
        ],
        selection=documents["selection"],
        confirmation_protocol=documents["confirmation_protocol"],
        confirmation_summary=documents["confirmation_summary"],
        confirmation_audit=documents["confirmation_audit"],
        external_protocol=documents["external_protocol"],
        external_summary=documents["external_summary"],
        external_audit=documents["external_audit"],
        system_protocol=documents["system_protocol"],
        system_summary=documents["system_summary"],
        system_audit=documents["system_audit"],
        opendetect_protocol=documents["opendetect_protocol"],
        opendetect_summary=documents["opendetect_summary"],
        opendetect_audit=documents["opendetect_audit"],
        parrot_protocol=documents["parrot_protocol"],
        parrot_summary=documents["parrot_summary"],
        parrot_audit=documents["parrot_audit"],
        input_file_sha256={
            name: file_hash(path) for name, path in paths.items()
        },
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["claim_tier"])


if __name__ == "__main__":
    main()
