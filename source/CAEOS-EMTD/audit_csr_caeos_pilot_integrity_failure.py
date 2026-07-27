from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from finalize_csr_caeos_pilot_integrity_failure import finalize, load


def audit(
    protocol: Dict[str, Any],
    design: Dict[str, Any],
    admission: Dict[str, Any],
    rejection: Dict[str, Any],
    evaluations: list[tuple[Path, Dict[str, Any]]],
    *,
    finalizer_file_sha256: str,
    auditor_file_sha256: str,
) -> Dict[str, Any]:
    expected = finalize(
        protocol,
        design,
        admission,
        evaluations,
        finalizer_file_sha256=finalizer_file_sha256,
    )
    checks = {
        "rejection_canonical": (
            rejection.get("manifest_sha256") == canonical_hash(rejection)
        ),
        "rejection_exactly_recomputed_without_effect_fields": (
            rejection == expected
        ),
        "evaluation_count_84": expected["evaluation_count"] == 84,
        "invalid_routing_rows_present": (
            expected["invalid_routing_count"] > 0
        ),
        "effect_metric_fields_accessed_for_integrity_decision_empty": (
            expected["effect_metric_fields_accessed_for_integrity_decision"]
            == []
        ),
        "test_labels_accessed_for_integrity_decision_false": (
            expected["test_labels_accessed_for_integrity_decision"] is False
        ),
        "effect_summary_generated_false": (
            expected["effect_summary_generated"] is False
        ),
        "full102_expansion_blocked": (
            expected["expand_to_full102"] is False
        ),
    }
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_csr_caeos_pilot_integrity_audit_v1",
        "state": "complete_integrity_rejection_audit",
        "audit_mode": "routing_metadata_only_no_effect_fields",
        "algorithm": "csr_caeos_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "design_manifest_sha256": design["manifest_sha256"],
        "clean_admission_manifest_sha256": admission["manifest_sha256"],
        "integrity_rejection_manifest_sha256": rejection["manifest_sha256"],
        "finalizer_file_sha256": finalizer_file_sha256,
        "auditor_file_sha256": auditor_file_sha256,
        "checks": checks,
        "passes": all(checks.values()),
        "claim_boundary": {
            "audit_passes_means_negative_branch_integrity_only": True,
            "no_csr_effect_claim_allowed": True,
            "no_sota_claim_allowed": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--admission", type=Path, required=True)
    parser.add_argument("--rejection", type=Path, required=True)
    parser.add_argument("--evaluation-root", type=Path, required=True)
    parser.add_argument("--finalizer", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for name in ("summary.json", "audit.json", "pilot_complete"):
        if (args.result_root / name).exists():
            raise ValueError(
                "integrity audit requires absent effect summary and completion"
            )
    paths = sorted(args.evaluation_root.rglob("evaluation.json"))
    value = audit(
        load(args.protocol),
        load(args.design),
        load(args.admission),
        load(args.rejection),
        [(path, load(path)) for path in paths],
        finalizer_file_sha256=file_hash(args.finalizer),
        auditor_file_sha256=file_hash(Path(__file__).resolve()),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
