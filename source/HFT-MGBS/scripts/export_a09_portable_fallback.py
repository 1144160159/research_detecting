#!/usr/bin/env python3
"""Export frozen A09 ExtraTrees parameters for the unwired Rust fallback.

This command never trains or mutates a model.  It is intentionally fail-closed:
all three source roots are supplied by the release operator, re-hashed before
and after export, and embedded in a deterministic little-endian artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import math
import os
import statistics
import struct
import tempfile
from pathlib import Path

import joblib
import numpy as np

from hft_mgbs.a09_numpy_inference import A09NumpyExactPredictor

MAGIC = b"HFTA09P1"
SCHEMA_VERSION = 1
RAW_FEATURE_COUNT = 38
MEMBER_COUNT = 3
TREES_PER_MEMBER = 200
EXPECTED_FEATURE_NAMES = (
    "byte_direction_imbalance", "deep_tier_available",
    "directional_iat_std_s_max_log1p", "directional_iat_std_s_min_log1p",
    "directional_mean_iat_s_max_log1p", "directional_mean_iat_s_min_log1p",
    "flow_ack_flag_count_log1p", "flow_bytes_log1p", "flow_cwr_flag_count_log1p",
    "flow_duration_s_log1p", "flow_ece_flag_count_log1p", "flow_fin_flag_count_log1p",
    "flow_iat_std_s_log1p", "flow_length_std_log1p", "flow_max_length_log1p",
    "flow_mean_iat_s_log1p", "flow_mean_length_log1p", "flow_min_length_log1p",
    "flow_packets_log1p", "flow_payload_bytes_log1p", "flow_psh_flag_count_log1p",
    "flow_rst_flag_count_log1p", "flow_syn_flag_count_log1p", "flow_tcp_flags_or",
    "flow_urg_flag_count_log1p", "packet_direction_imbalance", "payload_byte_ratio",
    "payload_direction_imbalance", "payload_entropy", "payload_printable_ratio",
    "payload_zero_ratio", "protocol", "protocol_tcp", "protocol_udp",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_absolute_regular(path: Path, label: str) -> tuple[int, int, int, int, int]:
    if not path.is_absolute():
        raise ValueError("{} path must be absolute".format(label))
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        if current.is_symlink():
            raise ValueError("{} path must not contain a symlink".format(label))
    if not path.is_file():
        raise ValueError("{} path must be a regular file".format(label))
    stat = path.stat()
    if stat.st_nlink != 1:
        raise ValueError("{} path must have exactly one hard link".format(label))
    return (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)


def _validate_create_only_output(output: Path) -> None:
    if not output.is_absolute():
        raise ValueError("output path must be absolute")
    if output.name in ("", ".", ".."):
        raise ValueError("output path must name a file")
    parent = output.parent
    current = Path(parent.anchor)
    for part in parent.parts[1:]:
        current = current / part
        if current.is_symlink():
            raise ValueError("output parent must not contain a symlink")
    if not parent.is_dir() or parent.resolve(strict=True) != parent:
        raise ValueError("output parent must be an existing canonical directory")
    if output.exists() or output.is_symlink():
        raise FileExistsError("output already exists")


def _create_only_bytes(output: Path, payload: bytes) -> None:
    _validate_create_only_output(output)
    temporary_fd, temporary_name = tempfile.mkstemp(
        prefix=output.name + ".", suffix=".tmp", dir=output.parent
    )
    try:
        with os.fdopen(temporary_fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary_name, output)
        os.unlink(temporary_name)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def require_sha(label: str, actual: str, expected: str) -> None:
    if len(expected) != 64 or any(char not in "0123456789abcdef" for char in expected):
        raise ValueError("{} expected SHA-256 is not lowercase hex".format(label))
    if not hashlib.sha256(actual.encode()).digest() == hashlib.sha256(expected.encode()).digest():
        raise ValueError("{} SHA-256 mismatch".format(label))


def _validate_bundle(bundle) -> tuple[tuple[object, ...], tuple[int, ...], tuple[float, ...]]:
    if bundle.get("schema_version") != 1 or bundle.get("candidate_id") != "A09":
        raise ValueError("bundle is not the frozen A09 schema")
    if bundle.get("classifier") != "extra_trees":
        raise ValueError("A09 classifier is not extra_trees")
    if bundle.get("feature_profile") != "invariant_no_ports_v1":
        raise ValueError("A09 feature profile is not invariant_no_ports_v1")
    feature_names = tuple(bundle["vectorizer"].feature_names_)
    if feature_names != EXPECTED_FEATURE_NAMES:
        raise ValueError("A09 vectorizer feature order differs from the portable contract")
    models = tuple(bundle.get("models") or ())
    positive_indices = tuple(int(value) for value in bundle.get("positive_indices") or ())
    thresholds = tuple(float(value) for value in bundle.get("thresholds") or ())
    if len(models) != MEMBER_COUNT or len(positive_indices) != MEMBER_COUNT or len(thresholds) != MEMBER_COUNT:
        raise ValueError("A09 must contain exactly three members, indices, and thresholds")
    if any(not math.isfinite(value) or not 0.0 <= value <= 1.0 for value in thresholds):
        raise ValueError("A09 contains an invalid member threshold")
    metadata = bundle.get("metadata") or {}
    if metadata.get("seeds") != [7, 11, 19] or metadata.get("estimators_per_seed") != TREES_PER_MEMBER:
        raise ValueError("A09 seed/tree release contract mismatch")
    return models, positive_indices, thresholds


def build_artifact(
    bundle,
    source_model_sha256: str,
    numpy_engine_sha256: str,
    campaign_contract_sha256: str,
) -> bytes:
    models, positive_indices, thresholds = _validate_bundle(bundle)
    predictor = A09NumpyExactPredictor(models, positive_indices)
    if predictor.feature_count != len(EXPECTED_FEATURE_NAMES):
        raise ValueError("compiled A09 feature count mismatch")
    output = bytearray(MAGIC)
    output.extend(struct.pack("<IIII", SCHEMA_VERSION, len(EXPECTED_FEATURE_NAMES), RAW_FEATURE_COUNT, MEMBER_COUNT))
    for value in (source_model_sha256, numpy_engine_sha256, campaign_contract_sha256):
        if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
            raise ValueError("embedded source SHA-256 is not lowercase hex")
        output.extend(bytes.fromhex(value))
    output.extend(struct.pack("<dI", statistics.median(thresholds), len(EXPECTED_FEATURE_NAMES)))
    for name in EXPECTED_FEATURE_NAMES:
        encoded = name.encode("utf-8")
        output.extend(struct.pack("<H", len(encoded)))
        output.extend(encoded)
    for model, positive_index, threshold, forest in zip(
        models, positive_indices, thresholds, predictor._forests
    ):
        if int(model.classes_[positive_index]) != 1:
            raise ValueError("A09 positive index is not bound to class 1")
        if forest.tree_count != TREES_PER_MEMBER:
            raise ValueError("A09 member tree count differs from release contract")
        output.extend(struct.pack("<dII", threshold, 1, forest.tree_count))
        for tree_index, estimator in enumerate(model.estimators_):
            count = int(estimator.tree_.node_count)
            output.extend(struct.pack("<I", count))
            for node_index in range(count):
                output.extend(
                    struct.pack(
                        "<iiidd",
                        int(forest.children_left[tree_index, node_index]),
                        int(forest.children_right[tree_index, node_index]),
                        int(forest.feature[tree_index, node_index]),
                        float(forest.threshold[tree_index, node_index]),
                        float(forest.positive_probability[tree_index, node_index]),
                    )
                )
    return bytes(output)


def export(
    model: Path,
    engine: Path,
    campaign_contract: Path,
    output: Path,
    expected_model_sha256: str,
    expected_engine_sha256: str,
    expected_campaign_sha256: str,
) -> str:
    source_identity = tuple(
        _require_absolute_regular(path, label)
        for path, label in (
            (model, "model"),
            (engine, "NumPy engine"),
            (campaign_contract, "campaign contract"),
        )
    )
    _validate_create_only_output(output)
    initial = (sha256(model), sha256(engine), sha256(campaign_contract))
    for label, actual, expected in zip(
        ("model", "NumPy engine", "campaign contract"),
        initial,
        (expected_model_sha256, expected_engine_sha256, expected_campaign_sha256),
    ):
        require_sha(label, actual, expected)
    bundle = joblib.load(model)
    artifact = build_artifact(bundle, *initial)
    final = (sha256(model), sha256(engine), sha256(campaign_contract))
    if final != initial:
        raise ValueError("A09 export source changed while it was being read")
    final_identity = tuple(
        _require_absolute_regular(path, label)
        for path, label in (
            (model, "model"),
            (engine, "NumPy engine"),
            (campaign_contract, "campaign contract"),
        )
    )
    if final_identity != source_identity:
        raise ValueError("A09 export source identity changed while it was being read")
    _create_only_bytes(output, artifact)
    return hashlib.sha256(artifact).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--numpy-engine", type=Path, required=True)
    parser.add_argument("--campaign-contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-model-sha256", required=True)
    parser.add_argument("--expected-engine-sha256", required=True)
    parser.add_argument("--expected-campaign-sha256", required=True)
    args = parser.parse_args()
    digest = export(
        args.model, args.numpy_engine, args.campaign_contract, args.output,
        args.expected_model_sha256, args.expected_engine_sha256,
        args.expected_campaign_sha256,
    )
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
