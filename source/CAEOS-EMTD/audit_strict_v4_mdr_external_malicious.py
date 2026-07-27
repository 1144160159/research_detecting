from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_mdr_external_malicious import (
    load,
    verify_protocol,
)
from summarize_strict_v4_mdr_external_malicious import summarize


def audit(
    *,
    protocol: Dict[str, Any],
    recorded: Dict[str, Any],
    recomputed: Dict[str, Any],
    protocol_file_sha256: str,
    summary_file_sha256: str,
    auditor_sha256: str,
) -> Dict[str, Any]:
    if (
        recorded.get("schema_version")
        != "strict_v4_mdr_external_malicious_summary_v1"
        or recorded.get("manifest_sha256") != canonical_hash(recorded)
    ):
        raise ValueError("canonical MDR external summary required")
    checks = {
        "recorded_summary_exactly_recomputed": recorded == recomputed,
        "protocol_binding": (
            recorded.get("protocol_manifest_sha256")
            == protocol["manifest_sha256"]
        ),
        "selected_algorithm_is_mdr": (
            recorded.get("selected_algorithm") == "mdr_caeos_v1"
        ),
        "primary_comparator_is_opendetect": (
            recorded.get("primary_comparator") == "opendetect"
        ),
        "formal_run_coverage": (
            int(recorded.get("formal_run_count", -1))
            == int(protocol["expected_formal_runs"])
        ),
        "failure_count_zero": recorded.get("failure_count") == 0,
        "validation_boolean_present": type(
            recorded.get("validation", {}).get("passes")
        )
        is bool,
        "external_effect_gate_boolean_present": type(
            recorded.get(
                "fresh_two_dataset_external_malicious_"
                "confirmation_passes"
            )
        )
        is bool,
    }
    passes = all(checks.values())
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_mdr_external_malicious_audit_v1"
        ),
        "status": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "summary_manifest_sha256": recorded["manifest_sha256"],
        "checks": checks,
        "validation_passes": passes,
        "external_effect_gate_passes": recorded[
            "fresh_two_dataset_external_malicious_confirmation_passes"
        ],
        "passes": passes,
        "claim_boundary": {
            "audit_pass_does_not_imply_external_effect_gate_pass": True,
            "external_effect_claim_requires_both_booleans_true": True,
            "failed_effect_gate_is_preserved_not_overridden": True,
        },
        "input_file_sha256": {
            "protocol": protocol_file_sha256,
            "summary": summary_file_sha256,
        },
        "implementation_sha256": {
            "audit_strict_v4_mdr_external_malicious.py": auditor_sha256
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = load(args.protocol)
    verify_protocol(protocol, args.project_root)
    recorded = load(args.summary)
    recomputed = summarize(protocol, args.run_root)
    value = audit(
        protocol=protocol,
        recorded=recorded,
        recomputed=recomputed,
        protocol_file_sha256=file_hash(args.protocol),
        summary_file_sha256=file_hash(args.summary),
        auditor_sha256=file_hash(Path(__file__).resolve()),
    )
    if value["passes"] is not True:
        raise ValueError("MDR external independent audit failed")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output.parent / "audit_complete").touch()
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
