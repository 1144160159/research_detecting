from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from audit_csr_caeos_pilot import audit as audit_source
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from materialize_csr_caeos_exact_replay import load, validate_protocol


def audit(
    protocol: Dict[str, Any],
    design: Dict[str, Any],
    admission: Dict[str, Any],
    summary: Dict[str, Any],
    source_capture_paths: List[Path],
    repair_capture_paths: List[Path],
    evaluation_paths: List[Path],
    *,
    implementation_file_sha256: Dict[str, str],
) -> Dict[str, Any]:
    validate_protocol(protocol)
    implementation_bound = (
        implementation_file_sha256 == protocol["implementation_sha256"]
    )
    expected = {
        (suite, scenario)
        for suite, scenarios in design["development"]["scenarios"].items()
        for scenario in scenarios
    }
    observed = set()
    repair_hashes = {}
    for path in repair_capture_paths:
        value = load(path)
        identity = (str(value.get("suite")), str(value.get("scenario")))
        key = "/".join(identity)
        if (
            value.get("schema_version")
            != "strict_v4_csr_caeos_exact_replay_capture_v2"
            or value.get("manifest_sha256") != canonical_hash(value)
            or value.get("state") != "complete"
            or value.get("repair_protocol_manifest_sha256")
            != protocol["manifest_sha256"]
            or value.get("source_capture_manifest_file_sha256")
            != protocol["source_capture_manifest_file_sha256"].get(key)
            or value.get("effect_metric_fields_read") != []
            or value.get("test_labels_read_for_repair") is not False
            or identity in observed
            or identity not in expected
        ):
            raise ValueError(f"invalid exact-replay capture: {path}")
        observed.add(identity)
        repair_hashes[key] = file_hash(path)
    routing_exact = True
    repair_bound = True
    for path in evaluation_paths:
        value = load(path)
        routing = value.get("routing", {})
        routing_exact = routing_exact and all(
            (
                routing.get("prediction_exactly_pairwise_all_rows") is True,
                routing.get("probability_exactly_pairwise_all_rows") is True,
                routing.get("risk_monotone_not_below_pairwise") is True,
                routing.get("inactive_risk_exactly_pairwise") is True,
                routing.get("unknown_or_test_labels_used") is False,
            )
        )
        repair_bound = repair_bound and (
            value.get("runtime_revision")
            == "exact_clean_probability_replay_v2"
            and value.get("repair_protocol_manifest_sha256")
            == protocol["manifest_sha256"]
        )
    source = audit_source(
        design,
        admission,
        summary,
        source_capture_paths,
        evaluation_paths,
        implementation_file_sha256=implementation_file_sha256,
    )
    checks = {
        "repair_protocol_canonical": (
            protocol["manifest_sha256"] == canonical_hash(protocol)
        ),
        "implementation_hashes_exactly_bound": implementation_bound,
        "repair_capture_count_14": (
            observed == expected and len(repair_capture_paths) == 14
        ),
        "evaluation_count_84": len(evaluation_paths) == 84,
        "all_evaluations_bound_to_repair_protocol": repair_bound,
        "all_routing_contract_fields_pass": routing_exact,
        "source_admission_and_effect_summary_recomputed": (
            source["passes"] is True
        ),
    }
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_csr_caeos_exact_replay_audit_v2",
        "state": "complete",
        "algorithm": "csr_caeos_v1",
        "runtime_revision": "exact_clean_probability_replay_v2",
        "repair_protocol_manifest_sha256": protocol["manifest_sha256"],
        "design_manifest_sha256": design["manifest_sha256"],
        "clean_admission_manifest_sha256": admission["manifest_sha256"],
        "source_integrity_rejection_manifest_sha256": protocol[
            "source_integrity_rejection_manifest_sha256"
        ],
        "source_integrity_audit_manifest_sha256": protocol[
            "source_integrity_audit_manifest_sha256"
        ],
        "summary_manifest_sha256": summary["manifest_sha256"],
        "repair_capture_manifest_file_sha256": dict(
            sorted(repair_hashes.items())
        ),
        "implementation_file_sha256": implementation_file_sha256,
        "source_audit_recomputation": source,
        "checks": checks,
        "passes": all(checks.values()),
        "scientific_effect_gate_passes": bool(summary["passes"]),
        "expand_to_full102": bool(summary["expand_to_full102"]),
        "claim_boundary": {
            "audit_pass_does_not_imply_positive_effect": True,
            "pilot_success_does_not_establish_sota": True,
            "source_v1_integrity_rejection_remains_historical_record": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--admission", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--source-capture-root", type=Path, required=True)
    parser.add_argument("--repair-capture-root", type=Path, required=True)
    parser.add_argument("--evaluation-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = load(args.protocol)
    implementation_hashes = {
        name: file_hash(args.project_root / relative)
        for name, relative in protocol["implementation"].items()
    }
    value = audit(
        protocol,
        load(args.design),
        load(args.admission),
        load(args.summary),
        sorted(args.source_capture_root.rglob("capture_manifest.json")),
        sorted(args.repair_capture_root.rglob("repair_capture_manifest.json")),
        sorted(args.evaluation_root.rglob("evaluation.json")),
        implementation_file_sha256=implementation_hashes,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
