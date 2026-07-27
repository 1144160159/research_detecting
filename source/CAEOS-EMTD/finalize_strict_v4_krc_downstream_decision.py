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


def decide(
    *,
    integrated_protocol: Dict[str, Any],
    confirmation_protocol: Dict[str, Any],
    confirmation_summary: Dict[str, Any],
    confirmation_audit: Dict[str, Any],
    input_file_sha256: Dict[str, str],
) -> Dict[str, Any]:
    expected = integrated_protocol["required_branches"]["krc_confirmation"]
    canonical_inputs = (
        integrated_protocol.get("schema_version")
        == "strict_v4_krc_integrated_comprehensive_sota_protocol_v1"
        and integrated_protocol.get("manifest_sha256")
        == canonical_hash(integrated_protocol)
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
        and confirmation_audit.get("passes") is True
    )
    if not canonical_inputs:
        raise ValueError("canonical finalized KRC confirmation evidence required")
    positive = bool(
        confirmation_summary.get("passes") is True
        and confirmation_summary.get("selection") == "krc_csr_caeos_v1"
        and confirmation_summary.get(
            "authorize_external_safety_efficiency_confirmation"
        )
        is True
        and confirmation_audit.get("decision_matches_summary") is True
    )
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_downstream_decision_v1",
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
        "krc_confirmation_passes": positive,
        "selected_algorithm": (
            "krc_csr_caeos_v1" if positive else "caeos_pairwise"
        ),
        "downstream_execution_required": positive,
        "decision": (
            "activate_all_frozen_krc_downstream_branches"
            if positive
            else "terminal_not_required_retain_caeos_pairwise"
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
            else []
        ),
        "claim_boundary": {
            "negative_krc_does_not_erase_exploration_evidence": True,
            "negative_krc_forbids_downstream_candidate_result_generation": True,
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
