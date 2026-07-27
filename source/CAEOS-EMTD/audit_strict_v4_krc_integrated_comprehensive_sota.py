from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


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
    specification: Dict[str, Any],
    protocol: Dict[str, Any],
    summary: Dict[str, Any],
    audit: Dict[str, Any],
) -> Dict[str, bool]:
    return {
        "protocol_is_canonical": canonical(
            protocol, specification["protocol_schema"]
        ),
        "summary_is_canonical": canonical(
            summary, specification["summary_schema"]
        ),
        "audit_is_canonical": canonical(
            audit, specification["audit_schema"]
        ),
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
        "branch_audit_integrity_passes": audit.get("passes") is True,
    }


def audit_integrated(
    *,
    project_root: Path,
    integrated_protocol: Dict[str, Any],
    downstream_design: Dict[str, Any],
    downstream_decision: Dict[str, Any],
    branch_values: Dict[
        str, tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]
    ],
    input_file_sha256: Dict[str, str],
) -> Dict[str, Any]:
    protocol_ok = canonical(
        integrated_protocol,
        "strict_v4_krc_integrated_comprehensive_sota_protocol_v1",
    )
    design_ok = canonical(
        downstream_design, "strict_v4_krc_downstream_sota_design_v1"
    )
    decision_ok = canonical(
        downstream_decision, "strict_v4_krc_downstream_decision_v1"
    )
    implementation_ok = all(
        (project_root / relative).is_file()
        and file_hash(project_root / relative) == expected
        for relative, expected in integrated_protocol.get(
            "implementation_sha256", {}
        ).items()
    )
    specifications = integrated_protocol["required_branches"]
    branch_checks = {
        name: branch_integrity(
            specifications[name], protocol, summary, audit
        )
        for name, (protocol, summary, audit) in branch_values.items()
    }
    branch_integrity_passes = {
        name: all(checks.values())
        for name, checks in branch_checks.items()
    }
    confirmation_summary = branch_values["krc_confirmation"][1]
    confirmation_audit = branch_values["krc_confirmation"][2]
    external_summary = branch_values["external_malicious"][1]
    external_audit = branch_values["external_malicious"][2]
    system_summary = branch_values["selected_system"][1]
    system_audit = branch_values["selected_system"][2]
    opendetect_summary = branch_values["opendetect_efficiency"][1]
    opendetect_audit = branch_values["opendetect_efficiency"][2]
    parrot_summary = branch_values["external_benign_safety"][1]
    parrot_audit = branch_values["external_benign_safety"][2]

    confirmation_gate = bool(
        branch_integrity_passes["krc_confirmation"]
        and confirmation_summary.get("passes") is True
        and confirmation_summary.get("selection") == "krc_csr_caeos_v1"
        and confirmation_summary.get(
            "authorize_external_safety_efficiency_confirmation"
        )
        is True
        and confirmation_audit.get("decision_matches_summary") is True
    )
    external_gate = bool(
        branch_integrity_passes["external_malicious"]
        and external_summary.get(
            "fresh_two_dataset_external_malicious_confirmation_passes"
        )
        is True
        and external_audit.get("external_effect_gate_passes") is True
    )
    deployability_gate = bool(
        branch_integrity_passes["selected_system"]
        and system_summary.get("deployability_decision", {}).get("passes")
        is True
        and system_audit.get("deployability_gate_passes") is True
    )
    pairwise_efficiency_gate = bool(
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
    opendetect_efficiency_gate = bool(
        branch_integrity_passes["opendetect_efficiency"]
        and opendetect_summary.get("strict_efficiency_decision", {}).get(
            "passes"
        )
        is True
        and opendetect_audit.get(
            "strict_efficiency_superiority_gate_passes"
        )
        is True
    )
    parrot_gate = bool(
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
        "downstream_design_is_canonical_and_bound": (
            design_ok
            and integrated_protocol.get(
                "downstream_design_manifest_sha256"
            )
            == downstream_design.get("manifest_sha256")
        ),
        "positive_downstream_decision_is_canonical_and_bound": (
            decision_ok
            and downstream_decision.get("krc_confirmation_passes") is True
            and downstream_decision.get("downstream_execution_required")
            is True
            and downstream_decision.get(
                "integrated_protocol_manifest_sha256"
            )
            == integrated_protocol.get("manifest_sha256")
        ),
        "implementation_hashes_match": implementation_ok,
        "all_branch_integrity_audits_pass": all(
            branch_integrity_passes.values()
        ),
        "input_file_hash_registry_complete": (
            len(input_file_sha256) == 18
            and all(input_file_sha256.values())
        ),
        "parrot_role_boundary_preserved": (
            specifications["external_benign_safety"].get(
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
        and parrot_gate
    )
    tier2 = bool(
        tier1 and pairwise_efficiency_gate and opendetect_efficiency_gate
    )
    claim_tier = (
        "multidimensional_comprehensive_sota_within_frozen_scope"
        if tier2
        else (
            "accuracy_robustness_external_sota_with_deployability_within_frozen_scope"
            if tier1
            else "integrated_sota_not_supported"
        )
    )
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_krc_integrated_comprehensive_sota_audit_v1"
        ),
        "state": "complete",
        "selected_algorithm": downstream_decision.get("selected_algorithm"),
        "integrated_protocol_manifest_sha256": integrated_protocol.get(
            "manifest_sha256"
        ),
        "downstream_design_manifest_sha256": downstream_design.get(
            "manifest_sha256"
        ),
        "downstream_decision_manifest_sha256": downstream_decision.get(
            "manifest_sha256"
        ),
        "integrity_checks": integrity_checks,
        "branch_integrity_checks": branch_checks,
        "branch_integrity_passes": branch_integrity_passes,
        "passes": integrity_passes,
        "evidence_gates": {
            "krc_primary88_confirmation": confirmation_gate,
            "fresh_two_dataset_external_malicious_confirmation": (
                external_gate
            ),
            "selected_system_deployability": deployability_gate,
            "parrot_external_benign_safety": parrot_gate,
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
            "integrated_protocol": integrated_protocol.get("manifest_sha256"),
            "downstream_design": downstream_design.get("manifest_sha256"),
            "downstream_decision": downstream_decision.get("manifest_sha256"),
            **{
                f"{name}_{kind}": value.get("manifest_sha256")
                for name, values in branch_values.items()
                for kind, value in zip(
                    ("protocol", "summary", "audit"), values
                )
            },
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--integrated-protocol", type=Path, required=True)
    parser.add_argument("--downstream-design", type=Path, required=True)
    parser.add_argument("--downstream-decision", type=Path, required=True)
    for branch in (
        "confirmation",
        "external",
        "system",
        "opendetect",
        "parrot",
    ):
        parser.add_argument(f"--{branch}-protocol", type=Path, required=True)
        parser.add_argument(f"--{branch}-summary", type=Path, required=True)
        parser.add_argument(f"--{branch}-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "integrated_protocol": args.integrated_protocol,
        "downstream_design": args.downstream_design,
        "downstream_decision": args.downstream_decision,
    }
    branches = {}
    mapping = {
        "krc_confirmation": "confirmation",
        "external_malicious": "external",
        "selected_system": "system",
        "opendetect_efficiency": "opendetect",
        "external_benign_safety": "parrot",
    }
    for logical, cli in mapping.items():
        values = []
        for kind in ("protocol", "summary", "audit"):
            path = getattr(args, f"{cli}_{kind}")
            paths[f"{logical}_{kind}"] = path
            values.append(load(path))
        branches[logical] = tuple(values)
    value = audit_integrated(
        project_root=args.project_root.resolve(),
        integrated_protocol=load(args.integrated_protocol),
        downstream_design=load(args.downstream_design),
        downstream_decision=load(args.downstream_decision),
        branch_values=branches,
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
