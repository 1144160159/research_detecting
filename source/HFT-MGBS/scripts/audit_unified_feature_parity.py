#!/usr/bin/env python3
"""Re-hash and compare the CAEOS offline and HFT online feature contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from hft_mgbs.unified_feature_reservoir import (
    AUDIT_ONLY_COLUMNS,
    CAEOS_FEATURE_VIEWS_SHA256,
    CAEOS_SCHEMA_SHA256,
    CONTEXT_COLUMNS,
    DERIVED_FEATURE_COLUMNS,
    ENCRYPTED_STRUCTURE_COLUMNS,
    MODEL_CANDIDATE_PERSISTENT_COLUMNS,
    ONLINE_EXTRACTABLE_COLUMNS,
    PAYLOAD_MODALITY_COLUMNS,
    SAFE_SCALAR_COLUMNS,
    SEQUENCE_COLUMNS,
    TARGET_COLUMNS,
    UNIFIED_PCAP_COLUMN_COUNT,
    validate_reservoir_policy,
)


def strict_json(path: Path) -> Mapping[str, Any]:
    if not path.is_absolute() or path.is_symlink() or not path.is_file():
        raise ValueError("JSON reference must be an absolute regular non-symlink file")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key: {}".format(key))
            result[key] = value
        return result

    def constant(value):
        raise ValueError("non-finite JSON value: {}".format(value))

    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=pairs,
        parse_constant=constant,
    )
    if not isinstance(value, Mapping):
        raise ValueError("JSON root must be an object")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit(schema_path: Path, views_path: Path, policy_path: Path) -> Mapping[str, Any]:
    schema = strict_json(schema_path)
    views = strict_json(views_path)
    policy = strict_json(policy_path)
    errors = []
    try:
        validate_reservoir_policy(policy)
    except ValueError as error:
        errors.append("policy:" + str(error))
    schema_sha = sha256_file(schema_path)
    views_sha = sha256_file(views_path)
    if schema_sha != CAEOS_SCHEMA_SHA256:
        errors.append("caeos_schema_sha256")
    if views_sha != CAEOS_FEATURE_VIEWS_SHA256:
        errors.append("caeos_feature_views_sha256")
    columns = schema.get("columns")
    column_names = (
        [column.get("name") for column in columns]
        if isinstance(columns, list)
        and all(isinstance(column, Mapping) for column in columns)
        else []
    )
    if (
        len(column_names) != UNIFIED_PCAP_COLUMN_COUNT
        or len(set(column_names)) != UNIFIED_PCAP_COLUMN_COUNT
    ):
        errors.append("caeos_schema_column_count")
    if tuple(views.get("audit_only_columns", ())) != AUDIT_ONLY_COLUMNS:
        errors.append("audit_only_columns")
    if tuple(views.get("target_columns", ())) != TARGET_COLUMNS:
        errors.append("target_columns")
    packet_behavior = views.get("modalities", {}).get("packet_behavior", {})
    if tuple(packet_behavior.get("safe_scalar_columns", ())) != SAFE_SCALAR_COLUMNS:
        errors.append("safe_scalar_columns")
    if tuple(packet_behavior.get("sequence_columns", ())) != SEQUENCE_COLUMNS:
        errors.append("sequence_columns")
    if tuple(packet_behavior.get("encrypted_protocol_structure_columns", ())) != ENCRYPTED_STRUCTURE_COLUMNS:
        errors.append("encrypted_protocol_structure_columns")
    if tuple(packet_behavior.get("derived_from_existing_columns", ())) != DERIVED_FEATURE_COLUMNS:
        errors.append("derived_feature_columns")
    payload = views.get("modalities", {}).get("payload_semantics", {})
    payload_columns = tuple(
        dict.fromkeys(
            tuple(payload.get("primary_columns", ()))
            + tuple(payload.get("raw_byte_baseline_columns", ()))
        )
    )
    if set(payload_columns) != set(PAYLOAD_MODALITY_COLUMNS):
        errors.append("payload_modality_columns")
    expected_model_candidates = set(SAFE_SCALAR_COLUMNS).union(
        SEQUENCE_COLUMNS,
        ENCRYPTED_STRUCTURE_COLUMNS,
        payload_columns,
    )
    if expected_model_candidates != set(MODEL_CANDIDATE_PERSISTENT_COLUMNS):
        errors.append("model_candidate_persistent_columns")
    expected_online = set(column_names).difference(AUDIT_ONLY_COLUMNS, TARGET_COLUMNS)
    if expected_online != set(ONLINE_EXTRACTABLE_COLUMNS):
        errors.append("online_extractable_columns")
    forbidden = set(views.get("default_forbidden_model_features", ()))
    forbidden_overlap = sorted(forbidden.intersection(SAFE_SCALAR_COLUMNS))
    if forbidden_overlap:
        errors.append("forbidden_safe_scalar_overlap")
    ablations = views.get("selection_gate", {}).get("required_ablations")
    if not isinstance(ablations, list) or len(ablations) != 9:
        errors.append("required_ablation_count")
    result = {
        "schema_version": 1,
        "scope": "hft_mgbs_unified_feature_parity_audit_v1",
        "inputs": {
            "caeos_schema": {"path": str(schema_path), "sha256": schema_sha},
            "caeos_feature_views": {"path": str(views_path), "sha256": views_sha},
            "reservoir_policy": {"path": str(policy_path), "sha256": sha256_file(policy_path)},
        },
        "counts": {
            "caeos_columns": len(column_names),
            "audit_only_columns": len(AUDIT_ONLY_COLUMNS),
            "target_columns": len(TARGET_COLUMNS),
            "online_extractable_columns": len(ONLINE_EXTRACTABLE_COLUMNS),
            "model_candidate_persistent_columns": len(
                MODEL_CANDIDATE_PERSISTENT_COLUMNS
            ),
            "safe_scalars": len(SAFE_SCALAR_COLUMNS),
            "packet_sequences": len(SEQUENCE_COLUMNS),
            "encrypted_structure": len(ENCRYPTED_STRUCTURE_COLUMNS),
            "context_features": len(CONTEXT_COLUMNS),
            "derived_features": len(DERIVED_FEATURE_COLUMNS),
            "required_ablations": len(ablations) if isinstance(ablations, list) else 0,
        },
        "forbidden_safe_scalar_overlap": forbidden_overlap,
        "semantic_contract_verified": not errors,
        "rust_hotpath_parity_qualified": False,
        "hardware_experiment_required": True,
        "final_pareto_ingestion_allowed": False,
        "errors": errors,
    }
    encoded = json.dumps(
        result, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")
    result["audit_sha256"] = hashlib.sha256(encoded).hexdigest()
    return result


def write_create_only(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(str(path), flags, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
            handle.write("\n")
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--caeos-schema", type=Path, required=True)
    parser.add_argument("--caeos-feature-views", type=Path, required=True)
    parser.add_argument("--reservoir-policy", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-verified", action="store_true")
    args = parser.parse_args()
    result = audit(
        args.caeos_schema,
        args.caeos_feature_views,
        args.reservoir_policy,
    )
    write_create_only(args.output.resolve(), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 2 if args.require_verified and not result["semantic_contract_verified"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
