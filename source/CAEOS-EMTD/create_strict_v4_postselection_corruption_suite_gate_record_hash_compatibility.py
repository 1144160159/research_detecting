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


def create_compatibility(
    protocol: dict[str, Any],
    *,
    authority_summary_manifest_sha256: str,
    authority_summary_file_sha256: str,
    corrected_auditor_sha256: str,
    suite_audit_count_at_amendment: int,
) -> dict[str, Any]:
    if (
        protocol.get("schema_version")
        != "strict_v4_postselection_corruption_suite_gate_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("invalid suite-gate protocol")
    if int(suite_audit_count_at_amendment) != 0:
        raise ValueError("compatibility must precede suite audit output")
    old_sha = protocol.get("implementation_sha256", {}).get(
        "suite_auditor"
    )
    if not isinstance(old_sha, str) or len(old_sha) != 64:
        raise ValueError("original suite auditor SHA is missing")
    for name, value in (
        ("authority summary manifest", authority_summary_manifest_sha256),
        ("authority summary file", authority_summary_file_sha256),
        ("corrected auditor", corrected_auditor_sha256),
    ):
        if not isinstance(value, str) or len(value) != 64:
            raise ValueError(f"{name} SHA is missing")
    result: dict[str, Any] = {
        "schema_version": (
            "strict_v4_postselection_corruption_suite_gate_"
            "record_hash_compatibility_v1"
        ),
        "status": (
            "post_authority_summary_schema_compatibility_before_suite_audit"
        ),
        "authority_summary_existed_at_amendment": True,
        "effect_thresholds_or_suite_means_used_for_change": False,
        "suite_audit_count_at_amendment": 0,
        "suite_gate_protocol_manifest_sha256": protocol[
            "manifest_sha256"
        ],
        "authority_summary_manifest_sha256": (
            authority_summary_manifest_sha256
        ),
        "authority_summary_file_sha256": authority_summary_file_sha256,
        "superseded_auditor_sha256": old_sha,
        "corrected_auditor_sha256": corrected_auditor_sha256,
        "allowed_change": {
            "record_hash_body_excludes_record_sha256_self_field": True,
            "matches_runner_record_creation_order": True,
            "task_identity_validation_unchanged": True,
            "wrapper_schema_validation_unchanged": True,
            "metrics_and_clean_file_sha_validation_unchanged": True,
            "unknown_or_test_label_gate_unchanged": True,
            "metric_extraction_and_degradation_orientation_unchanged": True,
            "all_175_thresholds_and_gate_logic_unchanged": True,
        },
        "claim_boundary": {
            "not_a_results_before_summary_protocol": True,
            "cannot_change_thresholds_or_select_suites_or_conditions": True,
            "negative_results_remain_admissible_and_mandatory": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite-protocol", type=Path, required=True)
    parser.add_argument("--authority-summary", type=Path, required=True)
    parser.add_argument("--corrected-auditor", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summary = load(args.authority_summary)
    if (
        summary.get("schema_version")
        != "strict_v4_postselection_corruption_summary_v1"
        or summary.get("manifest_sha256") != canonical_hash(summary)
    ):
        raise ValueError("invalid authority corruption summary")
    value = create_compatibility(
        load(args.suite_protocol),
        authority_summary_manifest_sha256=summary["manifest_sha256"],
        authority_summary_file_sha256=file_hash(args.authority_summary),
        corrected_auditor_sha256=file_hash(args.corrected_auditor),
        suite_audit_count_at_amendment=int(
            (args.output.parent / "audit.json").exists()
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
