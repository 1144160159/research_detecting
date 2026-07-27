from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: Dict[str, Any], schema: str, label: str
) -> None:
    if value.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError(f"{label} canonical SHA mismatch")


def create_protocol(
    *,
    project_root: Path,
    postselection_design: Dict[str, Any],
    opendetect_efficiency_design: Dict[str, Any],
    input_file_sha256: Dict[str, str],
    implementation_sha256: Dict[str, str],
    observed_audits: int,
) -> Dict[str, Any]:
    require_canonical(
        postselection_design,
        "strict_v4_mdr_postselection_evidence_design_v1",
        "MDR postselection design",
    )
    require_canonical(
        opendetect_efficiency_design,
        "strict_v4_mdr_opendetect_efficiency_design_v1",
        "MDR-OpenDetect efficiency design",
    )
    if int(observed_audits) != 0:
        raise ValueError("integrated protocol must freeze before audit outputs")
    required_implementation = {
        "create_strict_v4_mdr_integrated_comprehensive_sota_protocol.py",
        "audit_strict_v4_mdr_integrated_comprehensive_sota.py",
        "scripts/wait_and_audit_strict_v4_mdr_integrated_comprehensive_sota.sh",
    }
    if not required_implementation.issubset(implementation_sha256):
        raise ValueError("integrated audit implementation hashes incomplete")
    policy = postselection_design["integrated_claim_policy"]
    if (
        policy[
            "accuracy_robustness_external_sota_with_deployability_requires"
        ]
        != [
            "mdr_full102_confirmation",
            "fresh_two_dataset_external_malicious_confirmation",
            "selected_system_deployability",
            "parrot_external_benign_safety",
        ]
        or policy["multidimensional_comprehensive_sota_additionally_requires"]
        != [
            "strict_efficiency_superiority_over_embedded_pairwise",
            "strict_efficiency_superiority_over_opendetect",
        ]
    ):
        raise ValueError("integrated claim policy drifted")
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_mdr_integrated_comprehensive_sota_protocol_v1"
        ),
        "status": "conditionally_frozen_before_integrated_audit_outputs",
        "activation_gate": postselection_design["activation_gate"],
        "postselection_design_manifest_sha256": postselection_design[
            "manifest_sha256"
        ],
        "opendetect_efficiency_design_manifest_sha256": (
            opendetect_efficiency_design["manifest_sha256"]
        ),
        "required_branches": {
            "mdr_confirmation": {
                "protocol_schema": (
                    "strict_v4_mdr_caeos_confirmation_protocol_v1"
                ),
                "summary_schema": (
                    "strict_v4_mdr_caeos_confirmation_summary_v1"
                ),
                "audit_schema": (
                    "strict_v4_mdr_caeos_confirmation_audit_v1"
                ),
                "required_gate": "decision.passes",
            },
            "external_malicious": {
                "datasets": ["LSNM2024", "CICDDoS2019"],
                "protocol_schema": (
                    "strict_v4_mdr_external_malicious_protocol_v1"
                ),
                "summary_schema": (
                    "strict_v4_mdr_external_malicious_summary_v1"
                ),
                "audit_schema": (
                    "strict_v4_mdr_external_malicious_audit_v1"
                ),
                "required_gate": "external_effect_gate_passes",
            },
            "selected_system": {
                "protocol_schema": (
                    "strict_v4_mdr_selected_system_protocol_v1"
                ),
                "summary_schema": (
                    "strict_v4_mdr_selected_system_summary_v1"
                ),
                "audit_schema": (
                    "strict_v4_mdr_selected_system_audit_v1"
                ),
                "required_gates": [
                    "deployability_gate_passes",
                    "strict_efficiency_superiority_gate_passes",
                ],
            },
            "opendetect_efficiency": {
                "protocol_schema": (
                    "strict_v4_mdr_opendetect_efficiency_protocol_v1"
                ),
                "summary_schema": (
                    "strict_v4_mdr_opendetect_efficiency_summary_v1"
                ),
                "audit_schema": (
                    "strict_v4_mdr_opendetect_efficiency_audit_v1"
                ),
                "required_gate": (
                    "strict_efficiency_superiority_gate_passes"
                ),
            },
            "external_benign_safety": {
                "dataset": "PARROT2025",
                "role": (
                    "cross_domain_benign_false_alert_safety_only"
                ),
                "protocol_schema": (
                    "strict_v4_mdr_parrot_safety_protocol_v1"
                ),
                "summary_schema": (
                    "strict_v4_mdr_parrot_safety_summary_v1"
                ),
                "audit_schema": (
                    "strict_v4_mdr_parrot_safety_audit_v1"
                ),
                "required_gate": (
                    "benign_domain_shift_safety_gate_passes"
                ),
                "malicious_accuracy_evidence": False,
            },
        },
        "claim_tiers": {
            "tier1_requires": policy[
                "accuracy_robustness_external_sota_with_deployability_requires"
            ],
            "tier2_additionally_requires": policy[
                "multidimensional_comprehensive_sota_additionally_requires"
            ],
            "all_gates_without_splicing": True,
            "scope": (
                "frozen_strict_v4_comparator_dataset_and_metric_universe"
            ),
        },
        "claim_boundary": {
            "parrot_cannot_substitute_for_malicious_external_evidence": True,
            "parrot_cannot_support_malicious_accuracy_or_sota": True,
            "no_dataset_metric_scenario_suite_or_component_splicing": True,
            "universal_state_of_the_art_claim_is_not_authorized": True,
            "failed_branch_gate_is_preserved_not_overridden": True,
        },
        "expected_integrated_audit_schema": (
            "strict_v4_mdr_integrated_comprehensive_sota_audit_v1"
        ),
        "integrated_audit_count_at_freeze": 0,
        "paths": {"project_root": str(project_root.resolve())},
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": dict(
            sorted(implementation_sha256.items())
        ),
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def implementation_hashes(
    project_root: Path, relatives: Iterable[str]
) -> Dict[str, str]:
    output = {}
    for relative in relatives:
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(f"missing integrated audit file: {relative}")
        output[relative] = file_hash(path)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--postselection-design", type=Path, required=True)
    parser.add_argument(
        "--opendetect-efficiency-design", type=Path, required=True
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "postselection_design": args.postselection_design,
        "opendetect_efficiency_design": (
            args.opendetect_efficiency_design
        ),
    }
    required = [
        "create_strict_v4_mdr_integrated_comprehensive_sota_protocol.py",
        "audit_strict_v4_mdr_integrated_comprehensive_sota.py",
        "scripts/wait_and_audit_strict_v4_mdr_integrated_comprehensive_sota.sh",
    ]
    observed = int(args.output.is_file())
    value = create_protocol(
        project_root=args.project_root,
        postselection_design=load(args.postselection_design),
        opendetect_efficiency_design=load(
            args.opendetect_efficiency_design
        ),
        input_file_sha256={
            name: file_hash(path) for name, path in paths.items()
        },
        implementation_sha256=implementation_hashes(
            args.project_root, required
        ),
        observed_audits=observed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
