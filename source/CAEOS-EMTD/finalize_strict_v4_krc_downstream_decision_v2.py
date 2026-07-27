from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


STRUCTURAL_CHECKS = (
    "protocol_task_count_306",
    "protocol_primary_task_count_264",
    "capture_universe_exact",
    "evaluation_universe_exact",
    "capture_contracts_pass",
    "evaluation_contracts_pass",
    "capture_file_hash_registry_exact",
    "evaluation_file_hash_registry_exact",
    "primary_numerical_recomputation_matches",
    "enabled_primary_identity_registry_exact",
    "reported_checks_match_independent_gate",
    "reported_passes_is_conjunction",
    "selection_obeys_frozen_rule",
)

EFFECT_CHECKS = (
    "clean_safety_nonmissing_activation_upper",
    "known_macro_f1_exact_pairwise_all_conditions",
    "enabled_primary_scenario_count_minimum",
    "enabled_primary_suite_count_minimum",
    "overall_directed_means_strictly_positive",
    "at_least_5_of_7_suites_nonnegative_each_metric",
    "no_family_metric_regression_over_limit",
    "modality_missing_composite_improves",
    "gaussian_drift_composite_improves",
    "bootstrap_primary_composite_lower_bound_strictly_positive",
)


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def decide(
    *,
    integrated_protocol: Dict[str, Any],
    confirmation_protocol: Dict[str, Any],
    confirmation_summary: Dict[str, Any],
    confirmation_audit: Dict[str, Any],
    input_file_sha256: Dict[str, str],
) -> Dict[str, Any]:
    expected = integrated_protocol["required_branches"]["krc_confirmation"]
    audit_checks = confirmation_audit.get("checks", {})
    expected_checks = set(STRUCTURAL_CHECKS) | set(EFFECT_CHECKS)
    canonical_inputs = bool(
        integrated_protocol.get("schema_version")
        == "strict_v4_krc_integrated_comprehensive_sota_protocol_v1"
        and integrated_protocol.get("manifest_sha256")
        == canonical_hash(integrated_protocol)
        and integrated_protocol.get("protocol_revision")
        == "integrity_effect_separated_negative_branch_v2"
        and confirmation_protocol.get("schema_version")
        == expected["protocol_schema"]
        and confirmation_protocol.get("manifest_sha256")
        == canonical_hash(confirmation_protocol)
        and confirmation_summary.get("schema_version")
        == expected["summary_schema"]
        and confirmation_summary.get("manifest_sha256")
        == canonical_hash(confirmation_summary)
        and confirmation_audit.get("schema_version")
        == expected["audit_schema"]
        and confirmation_audit.get("manifest_sha256")
        == canonical_hash(confirmation_audit)
        and confirmation_summary.get("protocol_manifest_sha256")
        == confirmation_protocol.get("manifest_sha256")
        and confirmation_audit.get("protocol_manifest_sha256")
        == confirmation_protocol.get("manifest_sha256")
        and confirmation_audit.get("summary_manifest_sha256")
        == confirmation_summary.get("manifest_sha256")
        and set(audit_checks) == expected_checks
    )
    if not canonical_inputs:
        raise ValueError("canonical finalized KRC confirmation evidence required")

    integrity_passes = all(
        audit_checks[name] is True for name in STRUCTURAL_CHECKS
    )
    effect_gate_passes = all(
        audit_checks[name] is True for name in EFFECT_CHECKS
    )
    summary_effect_consistent = bool(
        confirmation_summary.get("passes") is effect_gate_passes
        and confirmation_summary.get(
            "authorize_external_safety_efficiency_confirmation"
        )
        is effect_gate_passes
        and confirmation_summary.get("selection")
        == (
            "krc_csr_caeos_v1"
            if effect_gate_passes
            else "caeos_pairwise"
        )
        and confirmation_audit.get("passes")
        is (integrity_passes and effect_gate_passes)
        and confirmation_audit.get("decision_matches_summary")
        is (integrity_passes and effect_gate_passes)
    )
    if not integrity_passes or not summary_effect_consistent:
        raise ValueError(
            "KRC evidence integrity or effect/decision consistency failed"
        )

    positive = effect_gate_passes
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_downstream_decision_v1",
        "decision_revision": "integrity_effect_separated_negative_branch_v2",
        "state": "complete",
        "integrated_protocol_manifest_sha256": integrated_protocol[
            "manifest_sha256"
        ],
        "confirmation_protocol_manifest_sha256": confirmation_protocol[
            "manifest_sha256"
        ],
        "confirmation_summary_manifest_sha256": confirmation_summary[
            "manifest_sha256"
        ],
        "confirmation_audit_manifest_sha256": confirmation_audit[
            "manifest_sha256"
        ],
        "krc_audit_integrity_passes": integrity_passes,
        "krc_effect_gate_passes": effect_gate_passes,
        "krc_confirmation_passes": positive,
        "selected_algorithm": (
            "krc_csr_caeos_v1" if positive else "caeos_pairwise"
        ),
        "downstream_execution_required": positive,
        "rrc_fallback_execution_permitted": not positive,
        "decision": (
            "activate_all_frozen_krc_downstream_branches"
            if positive
            else "terminal_negative_krc_retain_pairwise_and_permit_rrc"
        ),
        "required_next_outputs": (
            [
                "external_malicious",
                "selected_system",
                "opendetect_efficiency",
                "parrot_external_benign_safety",
                "integrated_audit",
            ]
            if positive
            else ["rrc_conditional_execution_protocol"]
        ),
        "claim_boundary": {
            "negative_krc_does_not_erase_exploration_evidence": True,
            "negative_krc_forbids_krc_downstream_candidate_results": True,
            "negative_krc_may_activate_only_preregistered_rrc": True,
            "rrc_requires_its_own_new_seeds_execution_and_audit": True,
            "positive_krc_alone_does_not_establish_sota": True,
        },
        "input_file_sha256": input_file_sha256,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--integrated-protocol", type=Path, required=True)
    parser.add_argument("--confirmation-protocol", type=Path, required=True)
    parser.add_argument("--confirmation-summary", type=Path, required=True)
    parser.add_argument("--confirmation-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "integrated_protocol": args.integrated_protocol,
        "confirmation_protocol": args.confirmation_protocol,
        "confirmation_summary": args.confirmation_summary,
        "confirmation_audit": args.confirmation_audit,
    }
    value = decide(
        integrated_protocol=load(args.integrated_protocol),
        confirmation_protocol=load(args.confirmation_protocol),
        confirmation_summary=load(args.confirmation_summary),
        confirmation_audit=load(args.confirmation_audit),
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
