from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from materialize_csr_caeos_exact_replay import load
from run_strict_v4_csr_caeos_pilot import validate_capture


IMPLEMENTATION = {
    "wrapper": "caeos/csr_exact_replay_runtime.py",
    "materializer": "materialize_csr_caeos_exact_replay.py",
    "evaluator": "evaluate_csr_caeos_exact_replay_runtime.py",
    "runner": "run_strict_v4_csr_caeos_exact_replay_pilot.py",
    "summarizer": "summarize_csr_caeos_pilot.py",
    "auditor": "audit_csr_caeos_exact_replay_pilot.py",
    "creator": "create_strict_v4_csr_caeos_exact_replay_protocol.py",
}


def output_counts(run_root: Path, result_root: Path) -> Dict[str, int]:
    return {
        "repair_capture": len(
            list(run_root.rglob("repair_capture_manifest.json"))
        )
        if run_root.exists()
        else 0,
        "evaluation": len(list(run_root.rglob("evaluation.json")))
        if run_root.exists()
        else 0,
        "summary": int((result_root / "summary.json").exists()),
        "audit": int((result_root / "audit.json").exists()),
        "completion": int((result_root / "pilot_complete").exists()),
    }


def create(
    project_root: Path,
    design: Dict[str, Any],
    source_protocol: Dict[str, Any],
    admission: Dict[str, Any],
    rejection: Dict[str, Any],
    rejection_audit: Dict[str, Any],
    source_capture_root: Path,
    run_root: Path,
    result_root: Path,
) -> Dict[str, Any]:
    if (
        design.get("schema_version") != "strict_v4_csr_caeos_design_v4"
        or design.get("manifest_sha256") != canonical_hash(design)
        or source_protocol.get("schema_version")
        != "strict_v4_csr_caeos_pilot_protocol_v1"
        or source_protocol.get("manifest_sha256")
        != canonical_hash(source_protocol)
        or source_protocol.get("design_manifest_sha256")
        != design["manifest_sha256"]
    ):
        raise ValueError("canonical source CSR protocol and design required")
    if (
        admission.get("manifest_sha256") != canonical_hash(admission)
        or admission.get("passes") is not True
        or admission.get("test_effect_metrics_read") is not False
    ):
        raise ValueError("passing effect-blind source admission required")
    if (
        rejection.get("schema_version")
        != "strict_v4_csr_caeos_pilot_integrity_rejection_v1"
        or rejection.get("manifest_sha256") != canonical_hash(rejection)
        or rejection.get("failed_fields")
        != ["probability_exactly_pairwise_all_rows"]
        or rejection.get("invalid_routing_count") != 16
        or rejection.get("effect_metric_fields_accessed_for_integrity_decision")
        != []
        or rejection.get("test_labels_accessed_for_integrity_decision")
        is not False
        or rejection.get("effect_summary_generated") is not False
    ):
        raise ValueError("effect-blind probability-only rejection required")
    if (
        rejection_audit.get("schema_version")
        != "strict_v4_csr_caeos_pilot_integrity_audit_v1"
        or rejection_audit.get("manifest_sha256")
        != canonical_hash(rejection_audit)
        or rejection_audit.get("passes") is not True
        or rejection_audit.get("integrity_rejection_manifest_sha256")
        != rejection["manifest_sha256"]
    ):
        raise ValueError("passing source integrity rejection audit required")
    counts = output_counts(run_root, result_root)
    if any(counts.values()):
        raise ValueError("exact-replay protocol must freeze before outputs")
    source_hashes = {}
    for suite, scenarios in sorted(
        design["development"]["scenarios"].items()
    ):
        for scenario in scenarios:
            path = source_capture_root / suite / scenario / "capture_manifest.json"
            validate_capture(path, suite, scenario, 0.5)
            source_hashes[f"{suite}/{scenario}"] = file_hash(path)
    if len(source_hashes) != 14:
        raise ValueError("exactly 14 source captures required")
    implementation_sha256 = {
        name: file_hash(project_root / relative)
        for name, relative in IMPLEMENTATION.items()
    }
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_csr_caeos_exact_replay_protocol_v2",
        "status": "frozen_before_repair_outputs",
        "algorithm": "csr_caeos_v1",
        "runtime_revision": "exact_clean_probability_replay_v2",
        "design_manifest_sha256": design["manifest_sha256"],
        "source_protocol_manifest_sha256": source_protocol[
            "manifest_sha256"
        ],
        "clean_admission_manifest_sha256": admission["manifest_sha256"],
        "source_integrity_rejection_manifest_sha256": rejection[
            "manifest_sha256"
        ],
        "source_integrity_audit_manifest_sha256": rejection_audit[
            "manifest_sha256"
        ],
        "source_capture_manifest_file_sha256": dict(
            sorted(source_hashes.items())
        ),
        "implementation": IMPLEMENTATION,
        "implementation_sha256": implementation_sha256,
        "repair_scope": {
            "root_cause": (
                "repeated clean model forward produced machine-precision "
                "probability differences"
            ),
            "probability_output": (
                "copy clean_probability from the same clean forward"
            ),
            "prediction_output": (
                "argmax clean_probability from the same clean forward"
            ),
            "risk_output": "unchanged",
            "active_mask": "unchanged",
            "threshold": "unchanged",
            "training": "not_repeated",
            "data_split": "unchanged",
            "conditions": "unchanged",
            "effect_metric_fields_read_for_repair_decision": [],
            "test_labels_read_for_repair_decision": False,
        },
        "expected_output_count": {
            "repair_capture": 14,
            "evaluation": 84,
            "summary": 1,
            "audit": 1,
            "completion": 1,
        },
        "output_counts_at_freeze": counts,
        "claim_boundary": {
            "repair_is_effect_blind": True,
            "repair_does_not_override_source_integrity_rejection": True,
            "repaired_run_requires_fresh_summary_and_audit": True,
            "pilot_success_does_not_establish_sota": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--source-protocol", type=Path, required=True)
    parser.add_argument("--admission", type=Path, required=True)
    parser.add_argument("--rejection", type=Path, required=True)
    parser.add_argument("--rejection-audit", type=Path, required=True)
    parser.add_argument("--source-capture-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = create(
        args.project_root.resolve(),
        load(args.design),
        load(args.source_protocol),
        load(args.admission),
        load(args.rejection),
        load(args.rejection_audit),
        args.source_capture_root.resolve(),
        args.run_root.resolve(),
        args.result_root.resolve(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
