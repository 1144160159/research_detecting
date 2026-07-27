from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


IMPLEMENTATION = (
    "create_strict_v4_krc_integrated_comprehensive_sota_protocol.py",
    "audit_strict_v4_krc_integrated_comprehensive_sota.py",
    "finalize_strict_v4_krc_downstream_decision.py",
)


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def verify_implementation(
    project_root: Path, relatives: Iterable[str] = IMPLEMENTATION
) -> Dict[str, str]:
    output = {}
    for relative in relatives:
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(
                f"missing KRC integrated implementation: {relative}"
            )
        output[relative] = file_hash(path)
    return dict(sorted(output.items()))


def create(
    *,
    project_root: Path,
    downstream_design: Dict[str, Any],
    downstream_design_file_sha256: str,
    observed_audits: int,
    implementation_sha256: Dict[str, str],
) -> Dict[str, Any]:
    if (
        downstream_design.get("schema_version")
        != "strict_v4_krc_downstream_sota_design_v1"
        or downstream_design.get("manifest_sha256")
        != canonical_hash(downstream_design)
    ):
        raise ValueError("canonical KRC downstream design required")
    if int(observed_audits) != 0:
        raise ValueError("integrated protocol must freeze before audit outputs")
    if not set(IMPLEMENTATION).issubset(implementation_sha256):
        raise ValueError("integrated implementation hashes are incomplete")
    policy = downstream_design["integrated_claim_tiers"]
    if (
        policy[
            "tier1_accuracy_robustness_external_and_deployability_requires"
        ]
        != [
            "krc_primary88_confirmation",
            "fresh_two_dataset_external_malicious_confirmation",
            "selected_system_deployability",
            "parrot_external_benign_safety",
        ]
        or policy[
            "tier2_multidimensional_comprehensive_sota_additionally_requires"
        ]
        != [
            "strict_efficiency_superiority_over_embedded_pairwise",
            "strict_efficiency_superiority_over_opendetect",
        ]
    ):
        raise ValueError("KRC integrated claim policy drifted")
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_krc_integrated_comprehensive_sota_protocol_v1"
        ),
        "status": "conditionally_frozen_before_krc_and_branch_outputs",
        "selected_algorithm_if_activated": "krc_csr_caeos_v1",
        "negative_incumbent": "caeos_pairwise",
        "downstream_design_manifest_sha256": downstream_design[
            "manifest_sha256"
        ],
        "activation_gate": downstream_design["activation_gate"],
        "required_branches": {
            "krc_confirmation": {
                "protocol_schema": (
                    "strict_v4_krc_csr_confirmation_protocol_v1"
                ),
                "summary_schema": (
                    "strict_v4_krc_csr_confirmation_summary_v1"
                ),
                "audit_schema": "strict_v4_krc_csr_confirmation_audit_v1",
            },
            "external_malicious": {
                "protocol_schema": (
                    "strict_v4_krc_external_malicious_execution_protocol_v1"
                ),
                "summary_schema": (
                    "strict_v4_krc_external_malicious_summary_v1"
                ),
                "audit_schema": (
                    "strict_v4_krc_external_malicious_audit_v1"
                ),
            },
            "selected_system": {
                "protocol_schema": (
                    "strict_v4_krc_selected_system_protocol_v1"
                ),
                "summary_schema": (
                    "strict_v4_krc_selected_system_summary_v1"
                ),
                "audit_schema": "strict_v4_krc_selected_system_audit_v1",
            },
            "opendetect_efficiency": {
                "protocol_schema": (
                    "strict_v4_krc_opendetect_efficiency_protocol_v1"
                ),
                "summary_schema": (
                    "strict_v4_krc_opendetect_efficiency_summary_v1"
                ),
                "audit_schema": (
                    "strict_v4_krc_opendetect_efficiency_audit_v1"
                ),
            },
            "external_benign_safety": {
                "protocol_schema": (
                    "strict_v4_krc_parrot_safety_protocol_v1"
                ),
                "summary_schema": (
                    "strict_v4_krc_parrot_safety_summary_v1"
                ),
                "audit_schema": "strict_v4_krc_parrot_safety_audit_v1",
                "malicious_accuracy_evidence": False,
            },
        },
        "claim_tiers": {
            "tier1_requires": policy[
                "tier1_accuracy_robustness_external_and_deployability_requires"
            ],
            "tier2_additionally_requires": policy[
                "tier2_multidimensional_comprehensive_sota_additionally_requires"
            ],
            "all_gates_without_splicing": True,
            "scope": (
                "frozen_strict_v4_comparator_dataset_and_metric_universe"
            ),
        },
        "negative_branch": {
            "when_krc_confirmation_fails": (
                "write_terminal_not_required_and_retain_caeos_pairwise"
            ),
            "downstream_model_execution_required": False,
            "does_not_erase_krc_exploration_evidence": True,
        },
        "claim_boundary": {
            "parrot_cannot_substitute_for_malicious_external_evidence": True,
            "no_dataset_metric_scenario_suite_or_component_splicing": True,
            "failed_branch_gate_is_preserved_not_overridden": True,
            "universal_state_of_the_art_claim_is_not_authorized": True,
        },
        "integrated_audit_count_at_freeze": 0,
        "paths": {"project_root": str(project_root.resolve())},
        "input_file_sha256": {
            "downstream_design": downstream_design_file_sha256
        },
        "implementation_sha256": implementation_sha256,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--downstream-design", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = create(
        project_root=args.project_root.resolve(),
        downstream_design=load(args.downstream_design),
        downstream_design_file_sha256=file_hash(args.downstream_design),
        observed_audits=int(args.output.is_file()),
        implementation_sha256=verify_implementation(
            args.project_root.resolve()
        ),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
