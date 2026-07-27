from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import joblib


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit_contract(
    deployment_artifact: Path,
    source_config: Path,
    parrot_protocol: Path,
) -> dict[str, Any]:
    deployment_artifact = deployment_artifact.resolve()
    source_config = source_config.resolve()
    parrot_protocol = parrot_protocol.resolve()
    deployment = joblib.load(deployment_artifact)
    bundle = (
        deployment.pairwise
        if hasattr(deployment, "pairwise")
        else deployment
    )
    deployment_evidence = (
        deployment.evidence()
        if hasattr(deployment, "evidence")
        else {}
    )
    config = json.loads(source_config.read_text(encoding="utf-8"))
    protocol = json.loads(parrot_protocol.read_text(encoding="utf-8"))

    modality_names = tuple(str(name) for name in config["modalities"])
    config_columns = tuple(
        str(column)
        for name in modality_names
        for column in config["modalities"][name]
    )
    protocol_columns = tuple(str(column) for column in protocol["feature_columns"])
    bundle_columns = tuple(str(column) for column in bundle.feature_columns)
    if tuple(bundle.modality_names) != modality_names:
        raise ValueError("deployment modality order differs from source config")
    if bundle_columns != config_columns:
        raise ValueError("deployment feature order differs from source config")
    if bundle_columns != protocol_columns:
        raise ValueError("deployment feature order differs from PARROT protocol")
    if len(protocol_columns) != int(protocol["feature_count"]):
        raise ValueError("PARROT protocol feature count is internally inconsistent")
    if file_hash(source_config) != bundle.source_config_sha256:
        raise ValueError("deployment source config SHA-256 mismatch")
    if protocol["schema_version"] != (
        "parrot2025_full_no_decryption_feature_protocol_v1"
    ):
        raise ValueError("unsupported PARROT feature protocol")
    if protocol["status"] != "frozen_before_full_feature_extraction":
        raise ValueError("PARROT feature protocol is not in the frozen state")

    required_input_contract = {
        "capture_group_is_indivisible": True,
        "deep_packet_inspection": False,
        "payload_decryption": False,
        "ssl_key_members_read": 0,
    }
    for key, expected in required_input_contract.items():
        if protocol["input_contract"].get(key) != expected:
            raise ValueError(f"PARROT input contract {key} is not {expected!r}")
    for key in (
        "training_use",
        "validation_use",
        "calibration_use",
        "threshold_selection_use",
        "feature_selection_use",
        "model_metrics_generated",
    ):
        if protocol["safety_policy"].get(key) is not False:
            raise ValueError(f"PARROT safety policy {key} is not false")

    return {
        "schema_version": "pairwise_parrot_feature_contract_audit_v1",
        "deployment_artifact_sha256": file_hash(deployment_artifact),
        "deployment_algorithm": deployment_evidence.get(
            "algorithm", "caeos_pairwise"
        ),
        "source_config_sha256": file_hash(source_config),
        "parrot_protocol_sha256": file_hash(parrot_protocol),
        "parrot_manifest_sha256": protocol["manifest_sha256"],
        "feature_schema_sha256": bundle.feature_schema_sha256,
        "feature_count": len(bundle_columns),
        "modality_names": list(modality_names),
        "ordered_feature_contract_equal": True,
        "source_config_binding_passes": True,
        "parrot_no_decryption_policy_passes": True,
        "parrot_no_fit_selection_or_metrics_policy_passes": True,
        "formal_model_metrics_admitted": 0,
        "formal_external_execution_admitted": False,
        "passes": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deployment-artifact", type=Path, required=True)
    parser.add_argument("--source-config", type=Path, required=True)
    parser.add_argument("--parrot-protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit_contract(
        args.deployment_artifact,
        args.source_config,
        args.parrot_protocol,
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
