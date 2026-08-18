from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
import struct
import tempfile
import time
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Optional

import audit_caeos_flow_duplicates as duplicate_audit


POLICY_SCHEMA = "caeos_content_conflict_policy_v1"
DERIVED_AUDIT_SCHEMA = "caeos_remediated_duplicate_audit_v1"
KEY_RECORD = struct.Struct("!32s")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def canonical_json_hash(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sha256_file(path: Path, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_bytes), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def atomic_bytes(path: Path, values: Iterable[bytes]) -> tuple[int, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    count = 0
    digest = hashlib.sha256()
    try:
        with os.fdopen(descriptor, "wb") as handle:
            for value in values:
                if len(value) != KEY_RECORD.size:
                    raise ValueError("ambiguous content key must contain 32 bytes")
                handle.write(value)
                digest.update(value)
                count += 1
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise
    return count, digest.hexdigest()


def audit_partition_rows(scratch: Path) -> int:
    done_files = sorted(scratch.glob("partitions/class-*/shard-*/done.json"))
    if not done_files:
        raise ValueError(f"no completed duplicate-audit partitions in {scratch}")
    return sum(int(load_json(path)["rows"]) for path in done_files)


def validate_content_invariant_repair(
    proof_path: Optional[Path],
    audit: dict[str, Any],
    audit_path: Path,
    manifest: dict[str, Any],
) -> Optional[dict[str, Any]]:
    source_manifest = str(audit.get("dataset_manifest_sha256", ""))
    current_manifest = str(manifest.get("manifest_sha256", ""))
    if source_manifest == current_manifest:
        return None
    if proof_path is None:
        raise ValueError("duplicate audit is stale and no content-invariant repair proof was supplied")
    proof = load_json(proof_path)
    checks = {
        "dataset_id": proof.get("dataset_id") == manifest.get("dataset_id"),
        "new_manifest": proof.get("new_manifest_sha256") == current_manifest,
        "source_audit": proof.get("source_audit_sha256") == sha256_file(audit_path),
        "features_unchanged": proof.get("features_modified") is False,
        "labels_unchanged": proof.get("labels_modified") is False,
        "rows_unchanged": int(proof.get("rows_deleted", -1)) == 0,
        "identity_repaired": int(proof.get("post_repair_duplicate_key_count", -1)) == 0,
    }
    if not all(checks.values()):
        raise ValueError(f"invalid content-invariant repair proof: {checks}")
    return {
        "path": str(proof_path),
        "sha256": sha256_file(proof_path),
        "checks": checks,
    }


def content_bucket_paths(scratch: Path, bucket: int) -> list[Path]:
    pattern = f"partitions/class-*/shard-*/content-{bucket:04d}.bin"
    return sorted(scratch.glob(pattern))


def inspect_conflict_bucket(task: tuple[str, str, int]) -> dict[str, Any]:
    scratch_text, output_text, bucket = task
    scratch = Path(scratch_text)
    output = Path(output_text)
    output.mkdir(parents=True, exist_ok=True)
    # key -> [first label, occurrence count, first capture, cross-capture,
    #         optional label counter, optional label examples]
    seen: dict[bytes, list[Any]] = {}
    rows = 0
    for path in content_bucket_paths(scratch, bucket):
        size = path.stat().st_size
        if size % duplicate_audit.CONTENT_RECORD.size:
            raise ValueError(f"truncated content bucket: {path}")
        with path.open("rb") as handle:
            while True:
                value = handle.read(duplicate_audit.CONTENT_RECORD.size)
                if not value:
                    break
                key, label, capture, sample = duplicate_audit.CONTENT_RECORD.unpack(value)
                rows += 1
                state = seen.get(key)
                if state is None:
                    seen[key] = [label, 1, capture, False, None, {label: (capture, sample)}]
                    continue
                state[1] += 1
                if capture != state[2]:
                    state[3] = True
                label_counts = state[4]
                if label_counts is None and label != state[0]:
                    label_counts = Counter({state[0]: state[1] - 1, label: 1})
                    state[4] = label_counts
                    state[5][label] = (capture, sample)
                elif label_counts is not None:
                    label_counts[label] += 1
                    state[5].setdefault(label, (capture, sample))

    conflict_keys = sorted(key for key, state in seen.items() if state[4] is not None)
    key_path = output / f"ambiguous-{bucket:04d}.bin"
    key_count, key_sha256 = atomic_bytes(key_path, conflict_keys)
    evidence_path = output / f"evidence-{bucket:04d}.jsonl"
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{evidence_path.name}.", suffix=".tmp", dir=str(output)
    )
    conflicting_rows = 0
    evidence_digest = hashlib.sha256()
    try:
        with os.fdopen(descriptor, "wb") as handle:
            for key in conflict_keys:
                state = seen[key]
                label_counts: Counter[bytes] = state[4]
                conflicting_rows += int(state[1])
                examples = state[5]
                value = {
                    "content_sha256": key.hex(),
                    "occurrence_count": int(state[1]),
                    "cross_capture": bool(state[3]),
                    "label_counts": {
                        label.hex(): int(count)
                        for label, count in sorted(label_counts.items())
                    },
                    "label_examples": {
                        label.hex(): {
                            "capture_id": capture.hex(),
                            "sample_id": sample.hex(),
                        }
                        for label, (capture, sample) in sorted(examples.items())
                    },
                }
                encoded = (
                    json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                    + "\n"
                ).encode("utf-8")
                handle.write(encoded)
                evidence_digest.update(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, evidence_path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise
    result = {
        "bucket": bucket,
        "rows": rows,
        "unique_content_keys": len(seen),
        "conflicting_key_count": key_count,
        "conflicting_row_count": conflicting_rows,
        "key_path": str(key_path),
        "key_sha256": key_sha256,
        "evidence_path": str(evidence_path),
        "evidence_sha256": evidence_digest.hexdigest(),
    }
    atomic_json(output / f"done-{bucket:04d}.json", result)
    return result


def completed_bucket(output: Path, bucket: int) -> Optional[dict[str, Any]]:
    done_path = output / f"done-{bucket:04d}.json"
    if not done_path.is_file():
        return None
    result = load_json(done_path)
    key_path = Path(result.get("key_path", ""))
    evidence_path = Path(result.get("evidence_path", ""))
    if not key_path.is_file() or not evidence_path.is_file():
        return None
    if sha256_file(key_path) != result.get("key_sha256"):
        return None
    if sha256_file(evidence_path) != result.get("evidence_sha256"):
        return None
    return result


def inspect_conflicts(
    scratch: Path, work_output: Path, bucket_count: int, workers: int, resume: bool
) -> list[dict[str, Any]]:
    results: dict[int, dict[str, Any]] = {}
    tasks: list[tuple[str, str, int]] = []
    for bucket in range(bucket_count):
        existing = completed_bucket(work_output, bucket) if resume else None
        if existing is None:
            tasks.append((str(scratch), str(work_output), bucket))
        else:
            results[bucket] = existing
    if tasks:
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
            for result in executor.map(inspect_conflict_bucket, tasks):
                results[int(result["bucket"])] = result
    if len(results) != bucket_count:
        raise ValueError("not every content bucket was inspected")
    return [results[index] for index in range(bucket_count)]


def merge_bucket_outputs(
    results: list[dict[str, Any]], output_dir: Path
) -> dict[str, Any]:
    key_path = output_dir / "ambiguous_content_sha256.bin"
    evidence_path = output_dir / "ambiguous_content_evidence.jsonl"
    key_descriptor, key_temporary = tempfile.mkstemp(
        prefix=f".{key_path.name}.", suffix=".tmp", dir=str(output_dir)
    )
    evidence_descriptor, evidence_temporary = tempfile.mkstemp(
        prefix=f".{evidence_path.name}.", suffix=".tmp", dir=str(output_dir)
    )
    key_digest = hashlib.sha256()
    evidence_digest = hashlib.sha256()
    try:
        with os.fdopen(key_descriptor, "wb") as key_handle, os.fdopen(
            evidence_descriptor, "wb"
        ) as evidence_handle:
            for result in results:
                for source, target, digest in (
                    (Path(result["key_path"]), key_handle, key_digest),
                    (Path(result["evidence_path"]), evidence_handle, evidence_digest),
                ):
                    with source.open("rb") as handle:
                        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
                            target.write(block)
                            digest.update(block)
            key_handle.flush()
            evidence_handle.flush()
            os.fsync(key_handle.fileno())
            os.fsync(evidence_handle.fileno())
        os.replace(key_temporary, key_path)
        os.replace(evidence_temporary, evidence_path)
    except BaseException:
        for temporary in (key_temporary, evidence_temporary):
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
        raise
    return {
        "ambiguous_content_path": str(key_path),
        "ambiguous_content_sha256": key_digest.hexdigest(),
        "ambiguous_content_size_bytes": key_path.stat().st_size,
        "evidence_path": str(evidence_path),
        "evidence_sha256": evidence_digest.hexdigest(),
        "evidence_size_bytes": evidence_path.stat().st_size,
    }


def build_policy(
    manifest_path: Path,
    audit_path: Path,
    scratch: Path,
    output_dir: Path,
    workers: int,
    bucket_count: int,
    resume: bool,
    reuse_partitions: bool,
    repair_proof: Optional[Path],
    cleanup_owned_scratch: bool,
) -> dict[str, Any]:
    if workers < 1 or workers > 16:
        raise ValueError("workers must be between 1 and 16")
    manifest = load_json(manifest_path)
    audit = load_json(audit_path)
    dataset_id = str(manifest.get("dataset_id", ""))
    if not dataset_id or audit.get("dataset_id") != dataset_id:
        raise ValueError("dataset id differs between manifest and duplicate audit")
    if not manifest.get("complete"):
        raise ValueError("dataset manifest is incomplete")
    if int(audit.get("row_count", -1)) != int(manifest.get("row_count", -2)):
        raise ValueError("duplicate audit row count differs from dataset manifest")
    repair = validate_content_invariant_repair(
        repair_proof, audit, audit_path, manifest
    )
    raw_identity_duplicates = int(audit["identity"]["duplicate_key_count"])
    if raw_identity_duplicates and repair is None:
        raise ValueError("identity duplicates remain without a valid repair proof")
    expected_conflicts = int(audit["content"]["cross_label_key_count"])
    started = time.time()
    if reuse_partitions:
        partition_rows = audit_partition_rows(scratch)
    else:
        partition = duplicate_audit.partition_rows_parallel(
            manifest,
            scratch,
            bucket_count,
            class_parallelism=1,
            shards_per_class=workers,
        )
        partition_rows = int(partition["rows"])
    if partition_rows != int(manifest["row_count"]):
        raise ValueError("content partition row count differs from dataset manifest")

    work_output = scratch / "content-conflict-inspection"
    results = inspect_conflicts(
        scratch, work_output, bucket_count, workers, resume=resume
    )
    observed_rows = sum(int(item["rows"]) for item in results)
    observed_conflicts = sum(int(item["conflicting_key_count"]) for item in results)
    conflicting_rows = sum(int(item["conflicting_row_count"]) for item in results)
    if observed_rows != int(manifest["row_count"]):
        raise ValueError("inspected row count differs from dataset manifest")
    if observed_conflicts != expected_conflicts:
        raise ValueError(
            f"cross-label conflict count differs from audit: "
            f"{observed_conflicts} != {expected_conflicts}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    merged = merge_bucket_outputs(results, output_dir)
    if merged["ambiguous_content_size_bytes"] != observed_conflicts * KEY_RECORD.size:
        raise ValueError("ambiguous content index size does not match key count")
    identity_after = 0 if repair is not None else raw_identity_duplicates
    policy = {
        "schema_version": POLICY_SCHEMA,
        "dataset_id": dataset_id,
        "dataset_manifest_path": str(manifest_path),
        "dataset_manifest_sha256": manifest["manifest_sha256"],
        "source_duplicate_audit_path": str(audit_path),
        "source_duplicate_audit_sha256": sha256_file(audit_path),
        "fingerprint_contract": audit["fingerprint_contract"],
        "decision": "exclude_all_rows_whose_model_content_sha256_is_cross_label",
        "official_labels_modified": False,
        "source_rows_deleted": 0,
        "raw_row_count": int(manifest["row_count"]),
        "ambiguous_content_key_count": observed_conflicts,
        "ambiguous_row_count": conflicting_rows,
        "model_eligible_row_count": int(manifest["row_count"]) - conflicting_rows,
        "raw_identity_duplicate_key_count": raw_identity_duplicates,
        "post_identity_repair_duplicate_key_count": identity_after,
        "retained_cross_label_key_count": 0,
        "content_invariant_identity_repair": repair,
        "capture_equivalence_edges_retained_from_source_audit": True,
        "split_requirement": "capture_equivalence_grouped",
        "execution": {
            "workers": workers,
            "bucket_count": bucket_count,
            "dataset_parallelism": 1,
            "partitions_reused": reuse_partitions,
            "elapsed_seconds": time.time() - started,
        },
        **merged,
        "model_view_gate_pass": identity_after == 0,
    }
    policy["policy_sha256"] = canonical_json_hash(policy)
    atomic_json(output_dir / "policy.json", policy)
    derived = {
        "schema_version": DERIVED_AUDIT_SCHEMA,
        "dataset_id": dataset_id,
        "dataset_manifest_sha256": manifest["manifest_sha256"],
        "source_duplicate_audit_sha256": policy["source_duplicate_audit_sha256"],
        "content_conflict_policy_sha256": policy["policy_sha256"],
        "raw": {
            "identity_duplicate_key_count": raw_identity_duplicates,
            "content_cross_label_key_count": expected_conflicts,
        },
        "model_view": {
            "excluded_content_key_count": observed_conflicts,
            "excluded_row_count": conflicting_rows,
            "retained_row_count": policy["model_eligible_row_count"],
            "identity_duplicate_key_count": identity_after,
            "content_cross_label_key_count": 0,
        },
        "gate_pass": policy["model_view_gate_pass"],
    }
    derived["audit_sha256"] = canonical_json_hash(derived)
    atomic_json(output_dir / "remediated_duplicate_audit.json", derived)
    success = {
        "dataset_id": dataset_id,
        "policy_sha256": policy["policy_sha256"],
        "audit_sha256": derived["audit_sha256"],
        "gate_pass": derived["gate_pass"],
    }
    atomic_json(output_dir / "SUCCESS.json", success)
    if cleanup_owned_scratch and not reuse_partitions:
        shutil.rmtree(scratch)
    return policy


def load_ambiguous_content_keys(policy_path: Path) -> frozenset[bytes]:
    policy = load_json(policy_path)
    if policy.get("schema_version") != POLICY_SCHEMA:
        raise ValueError("unsupported content conflict policy")
    key_path = Path(policy["ambiguous_content_path"])
    if sha256_file(key_path) != policy["ambiguous_content_sha256"]:
        raise ValueError("ambiguous content index SHA-256 differs from policy")
    value = key_path.read_bytes()
    if len(value) % KEY_RECORD.size:
        raise ValueError("ambiguous content index is truncated")
    keys = frozenset(
        value[offset : offset + KEY_RECORD.size]
        for offset in range(0, len(value), KEY_RECORD.size)
    )
    if len(keys) != int(policy["ambiguous_content_key_count"]):
        raise ValueError("ambiguous content index has duplicate or missing keys")
    return keys


def row_is_model_eligible(
    row: dict[str, str], fieldnames: list[str], ambiguous_keys: frozenset[bytes]
) -> bool:
    columns = duplicate_audit.model_content_columns(fieldnames)
    return duplicate_audit.digest_fields(row, columns) not in ambiguous_keys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-manifest", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--scratch", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--buckets", type=int, default=256)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--reuse-partitions", action="store_true")
    parser.add_argument("--repair-proof", type=Path)
    parser.add_argument("--cleanup-owned-scratch", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    policy = build_policy(
        manifest_path=args.dataset_manifest,
        audit_path=args.audit,
        scratch=args.scratch,
        output_dir=args.output_dir,
        workers=args.workers,
        bucket_count=args.buckets,
        resume=args.resume,
        reuse_partitions=args.reuse_partitions,
        repair_proof=args.repair_proof,
        cleanup_owned_scratch=args.cleanup_owned_scratch,
    )
    print(
        json.dumps(
            {
                "dataset_id": policy["dataset_id"],
                "ambiguous_content_key_count": policy["ambiguous_content_key_count"],
                "ambiguous_row_count": policy["ambiguous_row_count"],
                "model_eligible_row_count": policy["model_eligible_row_count"],
                "workers": policy["execution"]["workers"],
                "gate_pass": policy["model_view_gate_pass"],
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
