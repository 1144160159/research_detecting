#!/usr/bin/env python3
"""Compose the exact receipt required before Rust A09 local fallback can run."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import stat
import tempfile
from pathlib import Path


SHA_RE = re.compile(r"^[0-9a-f]{64}$")


def pairs(items):
    value = {}
    for key, item in items:
        if key in value:
            raise ValueError("duplicate JSON key: " + key)
        value[key] = item
    return value


def nonfinite(value):
    raise ValueError("non-finite JSON: " + value)


def stable(path: Path, maximum: int = 256 * 1024 * 1024) -> bytes:
    path = path.absolute()
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        if current.is_symlink():
            raise ValueError("symlink component rejected: " + str(path))
    descriptor = os.open(
        str(path), os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_BINARY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
            raise ValueError("bounded regular file required: " + str(path))
        chunks = []
        remaining = before.st_size
        while remaining:
            block = os.read(descriptor, min(1024 * 1024, remaining))
            if not block:
                raise ValueError("short read: " + str(path))
            chunks.append(block)
            remaining -= len(block)
        if os.read(descriptor, 1):
            raise ValueError("file grew during read: " + str(path))
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    identity = lambda item: (
        item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns, item.st_ctime_ns
    )
    if identity(before) != identity(after):
        raise ValueError("file changed during read: " + str(path))
    return b"".join(chunks)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_json(path: Path):
    raw = stable(path)
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=nonfinite)
    if not isinstance(value, dict):
        raise ValueError("JSON object required: " + str(path))
    return value, raw


def require_sha(label: str, actual: str, expected: str) -> None:
    if not SHA_RE.fullmatch(expected) or actual != expected:
        raise ValueError(label + " SHA-256 mismatch")


def create_json(path: Path, value) -> str:
    if path.exists() or path.is_symlink():
        raise ValueError("output must be new")
    raw = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    parent = path.parent.resolve(strict=True)
    descriptor, temporary_raw = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(parent))
    temporary = Path(temporary_raw)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists() or path.is_symlink():
            raise ValueError("output raced")
        os.link(str(temporary), str(path))
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
    os.chmod(str(path), 0o400 if os.name != "nt" else 0o600)
    return digest(raw)


def compose(
    *, artifact: Path, equivalence: Path, benchmark: Path, rust_source: Path,
    capture_binary: Path, evidence_manifest: Path, output: Path,
    expected_artifact_sha256: str, expected_equivalence_sha256: str,
    expected_benchmark_sha256: str, expected_rust_source_sha256: str,
    expected_capture_binary_sha256: str, expected_evidence_manifest_sha256: str,
) -> dict:
    artifact_raw = stable(artifact, 64 * 1024 * 1024)
    source_raw = stable(rust_source, 8 * 1024 * 1024)
    binary_raw = stable(capture_binary, 256 * 1024 * 1024)
    manifest_raw = stable(evidence_manifest, 16 * 1024 * 1024)
    equivalence_value, equivalence_raw = read_json(equivalence)
    benchmark_value, benchmark_raw = read_json(benchmark)
    for label, actual, expected in (
        ("artifact", digest(artifact_raw), expected_artifact_sha256),
        ("equivalence", digest(equivalence_raw), expected_equivalence_sha256),
        ("benchmark", digest(benchmark_raw), expected_benchmark_sha256),
        ("Rust source", digest(source_raw), expected_rust_source_sha256),
        ("capture binary", digest(binary_raw), expected_capture_binary_sha256),
        ("evidence manifest", digest(manifest_raw), expected_evidence_manifest_sha256),
    ):
        require_sha(label, actual, expected)
    equivalence_fields = {
        "schema_version", "scope", "candidate_id", "portable_artifact_sha256",
        "source_model_sha256", "numpy_engine_sha256", "campaign_contract_sha256",
        "holdout_input_sha256", "sample_count", "probability_bit_exact_count",
        "decision_exact_count", "rust_fallback_source_sha256", "capture_binary_sha256",
        "evidence_manifest_sha256", "accepted", "errors",
    }
    if set(equivalence_value) != equivalence_fields \
      or equivalence_value.get("schema_version") != 1 \
      or equivalence_value.get("scope") != "hft_mgbs_a09_local_fallback_equivalence_evidence_v1" \
      or equivalence_value.get("candidate_id") != "A09" \
      or equivalence_value.get("accepted") is not True \
      or equivalence_value.get("errors") != []:
        raise ValueError("cross-language equivalence evidence is invalid")
    sample_count = equivalence_value.get("sample_count")
    if type(sample_count) is not int or sample_count <= 0 \
      or equivalence_value.get("probability_bit_exact_count") != sample_count \
      or equivalence_value.get("decision_exact_count") != sample_count:
        raise ValueError("cross-language equivalence is not bit and decision exact")
    if equivalence_value.get("portable_artifact_sha256") != expected_artifact_sha256 \
      or equivalence_value.get("rust_fallback_source_sha256") != expected_rust_source_sha256 \
      or equivalence_value.get("capture_binary_sha256") != expected_capture_binary_sha256 \
      or equivalence_value.get("evidence_manifest_sha256") != expected_evidence_manifest_sha256:
        raise ValueError("cross-language equivalence identity drifted")
    benchmark_fields = {
        "schema_version", "scope", "candidate_id", "portable_artifact_sha256",
        "capture_binary_sha256", "rust_fallback_source_sha256", "evidence_manifest_sha256",
        "runs", "restoration_verified", "accepted", "errors",
    }
    if set(benchmark_value) != benchmark_fields \
      or benchmark_value.get("schema_version") != 1 \
      or benchmark_value.get("scope") != "hft_mgbs_a09_local_fallback_physical_benchmark_v1" \
      or benchmark_value.get("candidate_id") != "A09" \
      or benchmark_value.get("restoration_verified") is not True \
      or benchmark_value.get("accepted") is not True or benchmark_value.get("errors") != []:
        raise ValueError("physical fallback benchmark evidence is invalid")
    if benchmark_value.get("portable_artifact_sha256") != expected_artifact_sha256 \
      or benchmark_value.get("capture_binary_sha256") != expected_capture_binary_sha256 \
      or benchmark_value.get("rust_fallback_source_sha256") != expected_rust_source_sha256 \
      or benchmark_value.get("evidence_manifest_sha256") != expected_evidence_manifest_sha256:
        raise ValueError("physical fallback benchmark identity drifted")
    runs = benchmark_value.get("runs")
    if not isinstance(runs, list) or len(runs) < 3:
        raise ValueError("at least three physical fallback benchmark runs are required")
    run_ids = set()
    flows = []
    p99 = []
    for run in runs:
        if not isinstance(run, dict) or set(run) != {
            "run_id", "flows_per_second", "p50_us", "p99_us", "max_us",
            "node_visits_per_second", "cpu_cores", "rss_bytes",
        }:
            raise ValueError("physical fallback benchmark run is not exact")
        run_id = run.get("run_id")
        numeric = [run.get(name) for name in (
            "flows_per_second", "p50_us", "p99_us", "max_us", "node_visits_per_second", "cpu_cores"
        )]
        if not isinstance(run_id, str) or not run_id or run_id in run_ids \
          or any(type(value) not in (int, float) or not math.isfinite(value) or value < 0 for value in numeric) \
          or type(run.get("rss_bytes")) is not int or run["rss_bytes"] <= 0:
            raise ValueError("physical fallback benchmark run value is invalid")
        run_ids.add(run_id)
        flows.append(float(run["flows_per_second"]))
        p99.append(float(run["p99_us"]))
    if min(flows) <= 0.0 or max(p99) > 10_000.0:
        raise ValueError("physical fallback benchmark misses throughput or P99 gate")
    for name in (
        "source_model_sha256", "numpy_engine_sha256", "campaign_contract_sha256", "holdout_input_sha256"
    ):
        if not SHA_RE.fullmatch(str(equivalence_value.get(name, ""))):
            raise ValueError("equivalence identity is invalid: " + name)
    receipt = {
        "schema_version": 1,
        "scope": "hft_mgbs_local_a09_fallback_quality_receipt_v1",
        "candidate_id": "A09",
        "portable_artifact_sha256": expected_artifact_sha256,
        "source_model_sha256": equivalence_value["source_model_sha256"],
        "numpy_engine_sha256": equivalence_value["numpy_engine_sha256"],
        "campaign_contract_sha256": equivalence_value["campaign_contract_sha256"],
        "holdout_input_sha256": equivalence_value["holdout_input_sha256"],
        "equivalence_evidence_sha256": expected_equivalence_sha256,
        "physical_benchmark_evidence_sha256": expected_benchmark_sha256,
        "rust_fallback_source_sha256": expected_rust_source_sha256,
        "capture_binary_sha256": expected_capture_binary_sha256,
        "evidence_manifest_sha256": expected_evidence_manifest_sha256,
        "cross_language_sample_count": sample_count,
        "probability_bit_exact_count": sample_count,
        "decision_exact_count": sample_count,
        "physical_benchmark_runs": len(runs),
        "physical_flows_per_second_min": min(flows),
        "physical_p99_us_max": max(p99),
        "accepted": True,
        "production_release_accepted": False,
        "final_pareto_ingestion_allowed": False,
        "errors": [],
    }
    create_json(output, receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("artifact", "equivalence", "benchmark", "rust-source", "capture-binary", "evidence-manifest", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    for name in (
        "artifact", "equivalence", "benchmark", "rust-source", "capture-binary", "evidence-manifest"
    ):
        parser.add_argument("--expected-" + name + "-sha256", required=True)
    args = parser.parse_args()
    try:
        receipt = compose(
            artifact=args.artifact, equivalence=args.equivalence, benchmark=args.benchmark,
            rust_source=args.rust_source, capture_binary=args.capture_binary,
            evidence_manifest=args.evidence_manifest, output=args.output,
            expected_artifact_sha256=args.expected_artifact_sha256,
            expected_equivalence_sha256=args.expected_equivalence_sha256,
            expected_benchmark_sha256=args.expected_benchmark_sha256,
            expected_rust_source_sha256=args.expected_rust_source_sha256,
            expected_capture_binary_sha256=args.expected_capture_binary_sha256,
            expected_evidence_manifest_sha256=args.expected_evidence_manifest_sha256,
        )
    except (OSError, UnicodeError, ValueError) as error:
        print("local fallback quality receipt rejected: {}".format(error))
        return 74
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
