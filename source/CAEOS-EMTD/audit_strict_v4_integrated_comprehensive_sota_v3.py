from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: dict[str, Any], schema: str, label: str
) -> None:
    if value.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError(f"{label} canonical SHA mismatch")


def create_audit(
    *,
    design: dict[str, Any],
    v2_audit: dict[str, Any],
    suite_audit: dict[str, Any],
) -> dict[str, Any]:
    require_canonical(
        design,
        "strict_v4_integrated_comprehensive_sota_design_v3",
        "integrated v3 design",
    )
    require_canonical(
        v2_audit,
        "strict_v4_integrated_comprehensive_sota_audit_v2",
        "integrated v2 audit",
    )
    require_canonical(
        suite_audit,
        "strict_v4_postselection_corruption_suite_gate_audit_v1",
        "corruption suite-gate audit",
    )
    gates = {
        "integrated_v2_multidimensional_comprehensive_sota": (
            v2_audit.get("status") == "complete"
            and v2_audit.get(
                "multidimensional_comprehensive_sota_allowed"
            )
            is True
        ),
        "postselection_anchor_aggregate_corruption_gate": (
            suite_audit.get("aggregate_family_gate_passes") is True
        ),
        "postselection_anchor_all_175_suite_threshold_checks": (
            suite_audit.get("all_175_suite_threshold_checks_pass") is True
            and suite_audit.get("validation", {}).get(
                "suite_threshold_checks"
            )
            == 175
        ),
        "postselection_anchor_suite_gate_validation": (
            suite_audit.get("status") == "complete"
            and suite_audit.get("validation", {}).get("passes") is True
            and suite_audit.get("passes") is True
        ),
    }
    passes = all(gates.values())
    value: dict[str, Any] = {
        "schema_version": (
            "strict_v4_integrated_comprehensive_sota_audit_v3"
        ),
        "status": "complete",
        "selected_algorithm": v2_audit.get("selected_algorithm"),
        "integrated_v2_audit_manifest_sha256": v2_audit[
            "manifest_sha256"
        ],
        "corruption_suite_gate_audit_manifest_sha256": suite_audit[
            "manifest_sha256"
        ],
        "gates": gates,
        "comprehensive_sota_confirmed": passes,
        "claim_tier": (
            "multidimensional_comprehensive_sota_with_suite_"
            "stratified_anchor_robustness"
            if passes
            else "comprehensive_sota_not_established"
        ),
        "claim_boundary": {
            "integrated_v2_is_superseded_for_final_claims": True,
            "pairwise_anchor_suite_gate_does_not_substitute_for_selected_system_evidence": True,
            "ece_is_descriptive_without_a_frozen_threshold": True,
            "all_required_gates_pass_without_dimension_substitution": passes,
        },
        "required_follow_up": [
            name for name, passed in gates.items() if not passed
        ],
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--v2-design", type=Path, required=True)
    parser.add_argument("--suite-gate-protocol", type=Path, required=True)
    parser.add_argument("--v2-audit", type=Path, required=True)
    parser.add_argument("--suite-gate-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    design = load(args.design)
    if (
        file_hash(args.v2_design)
        != design["input_file_sha256"]["v2_design"]
        or file_hash(args.suite_gate_protocol)
        != design["input_file_sha256"][
            "corruption_suite_gate_protocol"
        ]
        or file_hash(Path(__file__).resolve())
        != design["implementation_sha256"]["integrated_v3_auditor"]
    ):
        raise ValueError("integrated v3 frozen file SHA mismatch")
    v2_audit, suite_audit = (
        load(args.v2_audit),
        load(args.suite_gate_audit),
    )
    if (
        v2_audit.get("input_file_sha256", {}).get("design")
        != design["input_file_sha256"]["v2_design"]
        or suite_audit.get("input_file_sha256", {}).get("suite_protocol")
        != design["input_file_sha256"][
            "corruption_suite_gate_protocol"
        ]
    ):
        raise ValueError("predecessor audit protocol binding mismatch")
    value = create_audit(
        design=design,
        v2_audit=v2_audit,
        suite_audit=suite_audit,
    )
    value["input_file_sha256"] = {
        "design": file_hash(args.design),
        "v2_design": file_hash(args.v2_design),
        "suite_gate_protocol": file_hash(args.suite_gate_protocol),
        "v2_audit": file_hash(args.v2_audit),
        "suite_gate_audit": file_hash(args.suite_gate_audit),
    }
    value["audit_implementation_sha256"] = file_hash(
        Path(__file__).resolve()
    )
    value["manifest_sha256"] = canonical_hash(value)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output.parent / "audit_complete").touch()
    print(value["claim_tier"])


if __name__ == "__main__":
    main()
