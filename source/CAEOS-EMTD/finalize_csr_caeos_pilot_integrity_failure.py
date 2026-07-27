from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


Identity = Tuple[str, str, str]
REQUIRED_TRUE = (
    "prediction_exactly_pairwise_all_rows",
    "probability_exactly_pairwise_all_rows",
    "risk_monotone_not_below_pairwise",
    "inactive_risk_exactly_pairwise",
)


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def expected_identities(design: Dict[str, Any]) -> set[Identity]:
    return {
        (str(suite), str(scenario), str(condition))
        for suite, scenarios in design["development"]["scenarios"].items()
        for scenario in scenarios
        for condition in design["development"]["conditions"]
    }


def scan_routing_integrity(
    design: Dict[str, Any],
    evaluations: Iterable[Tuple[Path, Dict[str, Any]]],
) -> Tuple[list[Dict[str, Any]], Dict[str, str], set[Identity]]:
    expected = expected_identities(design)
    if len(expected) != 84:
        raise ValueError("CSR pilot integrity finalizer requires 84 identities")
    observed: set[Identity] = set()
    invalid = []
    hashes = {}
    for path, value in evaluations:
        identity = (
            str(value.get("suite")),
            str(value.get("scenario")),
            str(value.get("condition")),
        )
        if (
            value.get("schema_version")
            != "strict_v4_csr_caeos_pilot_evaluation_v1"
            or value.get("state") != "complete"
            or value.get("algorithm") != "csr_caeos_v1"
            or value.get("manifest_sha256") != canonical_hash(value)
            or value.get("design_manifest_sha256")
            != design["manifest_sha256"]
            or identity not in expected
            or identity in observed
        ):
            raise ValueError(f"invalid CSR evaluation identity or manifest: {path}")
        observed.add(identity)
        hashes["/".join(identity)] = file_hash(path)
        routing = value.get("routing", {})
        failed_fields = [
            field for field in REQUIRED_TRUE if routing.get(field) is not True
        ]
        if routing.get("unknown_or_test_labels_used") is not False:
            failed_fields.append("unknown_or_test_labels_used")
        if failed_fields:
            invalid.append(
                {
                    "suite": identity[0],
                    "scenario": identity[1],
                    "condition": identity[2],
                    "failed_fields": sorted(failed_fields),
                    "evaluation_manifest_sha256": value["manifest_sha256"],
                    "evaluation_file_sha256": hashes["/".join(identity)],
                }
            )
    if observed != expected:
        raise ValueError(
            "CSR evaluation universe mismatch: "
            f"missing={len(expected - observed)} extra={len(observed - expected)}"
        )
    return (
        sorted(
            invalid,
            key=lambda row: (
                row["suite"],
                row["scenario"],
                row["condition"],
            ),
        ),
        dict(sorted(hashes.items())),
        observed,
    )


def finalize(
    protocol: Dict[str, Any],
    design: Dict[str, Any],
    admission: Dict[str, Any],
    evaluations: Iterable[Tuple[Path, Dict[str, Any]]],
    *,
    finalizer_file_sha256: str,
) -> Dict[str, Any]:
    if (
        protocol.get("schema_version")
        != "strict_v4_csr_caeos_pilot_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("canonical CSR pilot protocol required")
    if (
        design.get("schema_version") != "strict_v4_csr_caeos_design_v4"
        or design.get("manifest_sha256") != canonical_hash(design)
        or protocol.get("design_manifest_sha256")
        != design["manifest_sha256"]
    ):
        raise ValueError("canonical protocol-bound CSR v4 design required")
    if (
        admission.get("schema_version")
        != "strict_v4_csr_caeos_clean_admission_v1"
        or admission.get("manifest_sha256") != canonical_hash(admission)
        or admission.get("design_manifest_sha256")
        != design["manifest_sha256"]
        or admission.get("passes") is not True
        or admission.get("test_effect_metrics_read") is not False
    ):
        raise ValueError("passing effect-blind CSR clean admission required")

    invalid, hashes, observed = scan_routing_integrity(design, evaluations)
    if not invalid:
        raise ValueError("integrity failure branch requires invalid routing rows")
    failed_fields = sorted(
        {
            field
            for row in invalid
            for field in row["failed_fields"]
        }
    )
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_csr_caeos_pilot_integrity_rejection_v1",
        "state": "complete_integrity_rejection_before_effect_summary",
        "algorithm": "csr_caeos_v1",
        "reason": "frozen_risk_only_routing_contract_failed",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "design_manifest_sha256": design["manifest_sha256"],
        "clean_admission_manifest_sha256": admission["manifest_sha256"],
        "finalizer_file_sha256": finalizer_file_sha256,
        "evaluation_count": len(observed),
        "valid_routing_count": len(observed) - len(invalid),
        "invalid_routing_count": len(invalid),
        "failed_fields": failed_fields,
        "invalid_rows": invalid,
        "evaluation_file_sha256": hashes,
        "checks": {
            "all_84_evaluations_canonical_and_complete": len(observed) == 84,
            "prediction_exactly_pairwise_all_rows": (
                "prediction_exactly_pairwise_all_rows" not in failed_fields
            ),
            "probability_exactly_pairwise_all_rows": (
                "probability_exactly_pairwise_all_rows" not in failed_fields
            ),
            "risk_monotone_not_below_pairwise": (
                "risk_monotone_not_below_pairwise" not in failed_fields
            ),
            "inactive_risk_exactly_pairwise": (
                "inactive_risk_exactly_pairwise" not in failed_fields
            ),
            "zero_unknown_or_test_labels_used_for_routing": (
                "unknown_or_test_labels_used" not in failed_fields
            ),
        },
        "effect_metric_fields_accessed_for_integrity_decision": [],
        "test_labels_accessed_for_integrity_decision": False,
        "effect_summary_generated": False,
        "scientific_effect_decision": None,
        "expand_to_full102": False,
        "selected_algorithm": "caeos_pairwise",
        "claim_boundary": {
            "integrity_rejection_is_not_an_effect_failure": True,
            "integrity_rejection_cannot_establish_csr_quality": True,
            "pilot_success_does_not_establish_sota": True,
            "effect_values_must_remain_unread_for_any_technical_repair": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--admission", type=Path, required=True)
    parser.add_argument("--evaluation-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for name in ("summary.json", "audit.json", "pilot_complete"):
        if (args.result_root / name).exists():
            raise ValueError(
                "integrity rejection must precede effect summary and completion"
            )
    paths = sorted(args.evaluation_root.rglob("evaluation.json"))
    value = finalize(
        load(args.protocol),
        load(args.design),
        load(args.admission),
        [(path, load(path)) for path in paths],
        finalizer_file_sha256=file_hash(Path(__file__).resolve()),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
