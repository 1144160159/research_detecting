from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from audit_rrc_csr_confirmation import audit
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_rrc_csr_capture_pipeline import (
    load_json,
    run as run_capture_pipeline,
    validate_implementation,
    validate_protocol,
)
from summarize_rrc_csr_confirmation import summarize


def validate_summary(
    path: Path, protocol: Dict[str, Any], pipeline: Dict[str, Any]
) -> bool:
    if not path.exists():
        return False
    value = load_json(path)
    if (
        value.get("schema_version")
        != "strict_v4_rrc_csr_confirmation_summary_v1"
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or value.get("pipeline_inventory_manifest_sha256")
        != pipeline["manifest_sha256"]
    ):
        raise ValueError(f"invalid existing RRC summary: {path}")
    return True


def validate_audit(
    path: Path,
    protocol: Dict[str, Any],
    pipeline: Dict[str, Any],
    summary: Dict[str, Any],
) -> bool:
    if not path.exists():
        return False
    value = load_json(path)
    if (
        value.get("schema_version")
        != "strict_v4_rrc_csr_confirmation_audit_v1"
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or value.get("pipeline_inventory_manifest_sha256")
        != pipeline["manifest_sha256"]
        or value.get("summary_manifest_sha256")
        != summary["manifest_sha256"]
    ):
        raise ValueError(f"invalid existing RRC audit: {path}")
    return True


def run(
    protocol: Dict[str, Any],
    protocol_path: Path,
    project_root: Path,
    run_root: Path,
    result_root: Path,
    workers: int,
) -> Dict[str, Any]:
    validate_protocol(protocol)
    validate_implementation(protocol, project_root)
    pipeline = run_capture_pipeline(
        protocol,
        protocol_path,
        project_root,
        run_root,
        result_root,
        workers,
    )
    pipeline_path = result_root / "capture_pipeline_inventory.json"
    pipeline_disk = load_json(pipeline_path)
    if (
        pipeline.get("manifest_sha256") != canonical_hash(pipeline)
        or pipeline_disk != pipeline
    ):
        raise RuntimeError("RRC capture pipeline finalization failed")

    certificate_paths = sorted(
        (run_root / "scenario_certificates").rglob("certificate.json")
    )
    capture_paths = sorted(
        (run_root / "rrc_runtime_captures").rglob("capture_manifest.json")
    )
    evaluation_paths = sorted(
        (run_root / "evaluations").rglob("evaluation.json")
    )
    summary_path = result_root / "summary.json"
    if not validate_summary(summary_path, protocol, pipeline):
        summary_value = summarize(
            protocol,
            certificate_paths,
            capture_paths,
            evaluation_paths,
            pipeline,
        )
        summary_value["input_file_sha256"] = {
            "protocol": file_hash(protocol_path),
            "pipeline_inventory": file_hash(pipeline_path),
        }
        summary_value["manifest_sha256"] = canonical_hash(summary_value)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(
            json.dumps(summary_value, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    summary_value = load_json(summary_path)
    validate_summary(summary_path, protocol, pipeline)

    audit_path = result_root / "audit.json"
    if not validate_audit(
        audit_path, protocol, pipeline, summary_value
    ):
        audit_value = audit(
            protocol,
            summary_value,
            pipeline,
            certificate_paths,
            capture_paths,
            evaluation_paths,
        )
        audit_value["input_file_sha256"] = {
            "protocol": file_hash(protocol_path),
            "summary": file_hash(summary_path),
            "pipeline_inventory": file_hash(pipeline_path),
        }
        audit_value["manifest_sha256"] = canonical_hash(audit_value)
        audit_path.write_text(
            json.dumps(audit_value, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    audit_value = load_json(audit_path)
    validate_audit(
        audit_path, protocol, pipeline, summary_value
    )
    if audit_value["integrity_passes"] is not True:
        raise RuntimeError("RRC independent integrity audit failed")

    completion: Dict[str, Any] = {
        "schema_version": "strict_v4_rrc_csr_execution_complete_v1",
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "pipeline_inventory_manifest_sha256": pipeline["manifest_sha256"],
        "summary_manifest_sha256": summary_value["manifest_sha256"],
        "audit_manifest_sha256": audit_value["manifest_sha256"],
        "integrity_passes": True,
        "effect_gate_passes": bool(audit_value["effect_gate_passes"]),
        "selection": audit_value["selection"],
        "full_sota_established": False,
        "external_and_system_gates_still_required_if_rrc_selected": True,
    }
    completion["manifest_sha256"] = canonical_hash(completion)
    completion_path = result_root / "execution_complete.json"
    if completion_path.exists():
        existing = load_json(completion_path)
        if existing != completion:
            raise ValueError("existing RRC completion marker drifted")
    else:
        completion_path.write_text(
            json.dumps(completion, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return completion


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--workers", type=int)
    args = parser.parse_args()
    protocol_path = args.protocol.resolve()
    protocol = load_json(protocol_path)
    workers = (
        int(args.workers)
        if args.workers is not None
        else int(protocol["resource_contract"]["outer_workers"])
    )
    value = run(
        protocol,
        protocol_path,
        args.project_root.resolve(),
        args.run_root.resolve(),
        args.result_root.resolve(),
        workers,
    )
    print(json.dumps(value, sort_keys=True))


if __name__ == "__main__":
    main()
