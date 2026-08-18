from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import os
import re
import shutil
import struct
import tempfile
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any, BinaryIO, Optional


# Payload-bearing flow rows can exceed Python's conservative 128 KiB CSV default.
csv.field_size_limit(2**31 - 1)


IDENTITY_RECORD = struct.Struct("!32s32s32s32s")
CONTENT_RECORD = struct.Struct("!32s32s32s32s")
LEGACY_CONTENT_COLUMNS = (
    "packet_length_seq",
    "packet_iat_us_seq",
    "direction_seq",
    "packet_protocol_seq",
    "tcp_flags_seq",
    "packet_payload_length_seq",
    "payload_b64",
)
LABEL_COLUMNS = (
    "traffic_class",
    "attack_category",
    "attack_subcategory",
    "fine_label",
    "family_label",
    "binary_label",
)
NON_MODEL_COLUMNS = {
    "schema_version",
    "dataset_id",
    "dataset_role",
    "sample_id",
    "capture_id",
    "source_container_sha256",
    "source_member",
    "label_status",
    "label_source",
    "label_mapping_version",
    "dataset_native_label",
    "flow_key_hash",
    "flow_start_ns",
    "flow_end_ns",
    "endpoint_a_hash",
    "endpoint_b_hash",
    "port_a",
    "port_b",
    "application_protocol_hint",
    "flow_segment_index",
    *LABEL_COLUMNS,
}
MAX_EXAMPLES_PER_BUCKET = 8


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def atomic_json(path: Path, value: dict[str, Any]) -> None:
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


def digest_fields(row: dict[str, str], columns: tuple[str, ...]) -> bytes:
    digest = hashlib.sha256()
    for column in columns:
        digest.update(column.encode("ascii"))
        digest.update(b"\0")
        digest.update(row[column].encode("utf-8"))
        digest.update(b"\0")
    return digest.digest()


def model_content_columns(fieldnames: list[str]) -> tuple[str, ...]:
    columns = tuple(column for column in fieldnames if column not in NON_MODEL_COLUMNS)
    if not columns:
        raise ValueError("no model-content columns available for duplicate audit")
    return columns


def parse_sha256(value: str, field: str) -> bytes:
    if len(value) != 64:
        raise ValueError(f"invalid {field} width")
    try:
        return bytes.fromhex(value)
    except ValueError as error:
        raise ValueError(f"invalid {field} hex") from error


class BucketWriters:
    def __init__(self, root: Path, prefix: str, bucket_count: int, limit: int = 32):
        self.root = root
        self.prefix = prefix
        self.bucket_count = bucket_count
        self.limit = limit
        self.handles: OrderedDict[int, BinaryIO] = OrderedDict()
        root.mkdir(parents=True, exist_ok=True)

    def write(self, bucket: int, record: bytes) -> None:
        handle = self.handles.pop(bucket, None)
        if handle is None:
            path = self.root / f"{self.prefix}-{bucket:04d}.bin"
            handle = path.open("ab", buffering=8 * 1024 * 1024)
        self.handles[bucket] = handle
        handle.write(record)
        if len(self.handles) > self.limit:
            _, oldest = self.handles.popitem(last=False)
            oldest.close()

    def close(self) -> None:
        for handle in self.handles.values():
            handle.close()
        self.handles.clear()


def bucket_index(digest: bytes, bucket_count: int) -> int:
    return int.from_bytes(digest[:4], "big") % bucket_count


def partition_rows(
    manifest: dict[str, Any], scratch: Path, bucket_count: int
) -> dict[str, Any]:
    identity = BucketWriters(scratch, "identity", bucket_count)
    content = BucketWriters(scratch, "content", bucket_count)
    rows = 0
    started = time.time()
    try:
        for class_item in manifest["class_csvs"]:
            path = Path(class_item["path"])
            with path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                required = {
                    "sample_id",
                    "capture_id",
                    *LEGACY_CONTENT_COLUMNS,
                    *LABEL_COLUMNS,
                }
                if reader.fieldnames is None or not required.issubset(reader.fieldnames):
                    missing = sorted(required - set(reader.fieldnames or []))
                    raise ValueError(f"duplicate audit columns missing from {path}: {missing}")
                full_columns = model_content_columns(list(reader.fieldnames))
                for row in reader:
                    sample = parse_sha256(row["sample_id"], "sample_id")
                    capture = parse_sha256(row["capture_id"], "capture_id")
                    content_digest = digest_fields(row, full_columns)
                    label_digest = digest_fields(row, LABEL_COLUMNS)
                    record = IDENTITY_RECORD.pack(
                        sample, label_digest, capture, content_digest
                    )
                    identity.write(bucket_index(sample, bucket_count), record)
                    record = CONTENT_RECORD.pack(
                        content_digest, label_digest, capture, sample
                    )
                    content.write(bucket_index(content_digest, bucket_count), record)
                    rows += 1
    finally:
        identity.close()
        content.close()
    return {"rows": rows, "partition_seconds": time.time() - started}


def inspect_buckets(
    scratch: Path, prefix: str, bucket_count: int
) -> dict[str, Any]:
    duplicate_rows = 0
    duplicate_keys = 0
    cross_label_keys = 0
    cross_capture_keys = 0
    capture_edges: set[tuple[str, str]] = set()
    duplicate_examples: list[dict[str, str]] = []
    cross_label_examples: list[dict[str, str]] = []
    for bucket in range(bucket_count):
        path = scratch / f"{prefix}-{bucket:04d}.bin"
        if not path.exists():
            continue
        seen: dict[
            bytes, tuple[bytes, bytes, bytes, bytes, int, bool, bool]
        ] = {}
        with path.open("rb") as handle:
            while True:
                record = IDENTITY_RECORD if prefix == "identity" else CONTENT_RECORD
                value = handle.read(record.size)
                if not value:
                    break
                if len(value) != record.size:
                    raise ValueError(f"truncated duplicate-audit bucket: {path}")
                if prefix == "identity":
                    key, label, capture, content_detail = record.unpack(value)
                    sample = key
                else:
                    key, label, capture, sample = record.unpack(value)
                    content_detail = key
                previous = seen.get(key)
                if previous is None:
                    seen[key] = (
                        label,
                        capture,
                        sample,
                        content_detail,
                        1,
                        False,
                        False,
                    )
                    continue
                (
                    previous_label,
                    previous_capture,
                    previous_sample,
                    previous_content,
                    count,
                    label_conflict,
                    capture_conflict,
                ) = previous
                if count == 1:
                    duplicate_keys += 1
                    if len(duplicate_examples) < 256:
                        duplicate_examples.append(
                            {
                                "key_sha256": key.hex(),
                                "first_label_sha256": previous_label.hex(),
                                "second_label_sha256": label.hex(),
                                "first_capture_id": previous_capture.hex(),
                                "second_capture_id": capture.hex(),
                                "first_sample_id": previous_sample.hex(),
                                "second_sample_id": sample.hex(),
                                "first_content_sha256": previous_content.hex(),
                                "second_content_sha256": content_detail.hex(),
                            }
                        )
                duplicate_rows += 1
                if label != previous_label and not label_conflict:
                    cross_label_keys += 1
                    label_conflict = True
                    if len(cross_label_examples) < 256:
                        cross_label_examples.append(
                            {
                                "key_sha256": key.hex(),
                                "first_label_sha256": previous_label.hex(),
                                "second_label_sha256": label.hex(),
                                "first_capture_id": previous_capture.hex(),
                                "second_capture_id": capture.hex(),
                                "first_sample_id": previous_sample.hex(),
                                "second_sample_id": sample.hex(),
                                "first_content_sha256": previous_content.hex(),
                                "second_content_sha256": content_detail.hex(),
                            }
                        )
                if capture != previous_capture and not capture_conflict:
                    cross_capture_keys += 1
                    capture_conflict = True
                    left, right = sorted((capture.hex(), previous_capture.hex()))
                    capture_edges.add((left, right))
                seen[key] = (
                    previous_label,
                    previous_capture,
                    previous_sample,
                    previous_content,
                    count + 1,
                    label_conflict,
                    capture_conflict,
                )
    return {
        "duplicate_rows_after_first": duplicate_rows,
        "duplicate_key_count": duplicate_keys,
        "cross_label_key_count": cross_label_keys,
        "cross_capture_key_count": cross_capture_keys,
        "capture_equivalence_edges": [list(item) for item in sorted(capture_edges)],
        "duplicate_examples": duplicate_examples,
        "cross_label_examples": cross_label_examples,
    }


def shard_directory(scratch: Path, class_index: int, category: str, shard: int) -> Path:
    safe_category = re.sub(r"[^A-Za-z0-9_.-]+", "_", category).strip("_")
    return scratch / "partitions" / f"class-{class_index:04d}-{safe_category}" / f"shard-{shard:04d}"


def byte_range(path: Path, shard: int, shard_count: int) -> tuple[int, int, int]:
    size = path.stat().st_size
    with path.open("rb") as handle:
        header_end = len(handle.readline())
    payload_bytes = size - header_end
    start = header_end + payload_bytes * shard // shard_count
    end = header_end + payload_bytes * (shard + 1) // shard_count
    return header_end, start, end


def aligned_start(handle: BinaryIO, header_end: int, start: int) -> int:
    if start <= header_end:
        handle.seek(header_end)
        return header_end
    handle.seek(start - 1)
    if handle.read(1) != b"\n":
        handle.readline()
    return handle.tell()


def shard_contract(
    class_item: dict[str, Any],
    class_index: int,
    shard: int,
    shard_count: int,
    bucket_count: int,
) -> dict[str, Any]:
    path = Path(class_item["path"])
    header_end, start, end = byte_range(path, shard, shard_count)
    return {
        "class_index": class_index,
        "attack_category": class_item["attack_category"],
        "source_path": str(path),
        "source_size_bytes": path.stat().st_size,
        "source_sha256": class_item["sha256"],
        "header_end": header_end,
        "range_start": start,
        "range_end": end,
        "shard": shard,
        "shard_count": shard_count,
        "bucket_count": bucket_count,
    }


def completed_shard(path: Path, contract: dict[str, Any]) -> Optional[dict[str, Any]]:
    done = path / "done.json"
    if not done.exists():
        return None
    value = load_json(done)
    if value.get("contract") != contract or not value.get("complete"):
        return None
    return value


def parse_csv_line(line: bytes, fieldnames: list[str], source: Path) -> dict[str, str]:
    try:
        values = next(csv.reader([line.decode("utf-8")]))
    except (UnicodeDecodeError, csv.Error) as error:
        raise ValueError(f"invalid CSV record in {source}") from error
    if len(values) != len(fieldnames):
        raise ValueError(
            f"CSV column count differs in {source}: {len(values)} != {len(fieldnames)}"
        )
    return dict(zip(fieldnames, values))


def partition_class_shard(task: tuple[dict[str, Any], int, int, int, int, str]) -> dict[str, Any]:
    class_item, class_index, shard, shard_count, bucket_count, scratch_text = task
    scratch = Path(scratch_text)
    contract = shard_contract(class_item, class_index, shard, shard_count, bucket_count)
    output = shard_directory(
        scratch, class_index, class_item["attack_category"], shard
    )
    existing = completed_shard(output, contract)
    if existing is not None:
        return existing
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    path = Path(class_item["path"])
    identity = BucketWriters(output, "identity", bucket_count)
    content = BucketWriters(output, "content", bucket_count)
    rows = 0
    started = time.time()
    last_progress_position = contract["range_start"]
    try:
        with path.open("rb") as handle:
            header = handle.readline()
            try:
                fieldnames = next(csv.reader([header.decode("utf-8")]))
            except (UnicodeDecodeError, csv.Error) as error:
                raise ValueError(f"invalid CSV header in {path}") from error
            required = {
                "sample_id",
                "capture_id",
                *LEGACY_CONTENT_COLUMNS,
                *LABEL_COLUMNS,
            }
            if not required.issubset(fieldnames):
                missing = sorted(required - set(fieldnames))
                raise ValueError(f"duplicate audit columns missing from {path}: {missing}")
            full_columns = model_content_columns(fieldnames)
            position = aligned_start(
                handle, contract["header_end"], contract["range_start"]
            )
            aligned_range_start = position
            while position < contract["range_end"]:
                line = handle.readline()
                if not line:
                    break
                row = parse_csv_line(line, fieldnames, path)
                sample = parse_sha256(row["sample_id"], "sample_id")
                capture = parse_sha256(row["capture_id"], "capture_id")
                content_digest = digest_fields(row, full_columns)
                label_digest = digest_fields(row, LABEL_COLUMNS)
                identity.write(
                    bucket_index(sample, bucket_count),
                    IDENTITY_RECORD.pack(
                        sample, label_digest, capture, content_digest
                    ),
                )
                content.write(
                    bucket_index(content_digest, bucket_count),
                    CONTENT_RECORD.pack(
                        content_digest, label_digest, capture, sample
                    ),
                )
                rows += 1
                position = handle.tell()
                if position - last_progress_position >= 512 * 1024 * 1024:
                    atomic_json(
                        output / "progress.json",
                        {
                            "contract": contract,
                            "complete": False,
                            "aligned_range_start": aligned_range_start,
                            "position": position,
                            "rows": rows,
                            "elapsed_seconds": time.time() - started,
                        },
                    )
                    last_progress_position = position
    finally:
        identity.close()
        content.close()
    result = {
        "contract": contract,
        "complete": True,
        "aligned_range_start": aligned_range_start,
        "position": position,
        "rows": rows,
        "elapsed_seconds": time.time() - started,
    }
    atomic_json(output / "done.json", result)
    try:
        (output / "progress.json").unlink()
    except FileNotFoundError:
        pass
    return result


def partition_rows_parallel(
    manifest: dict[str, Any],
    scratch: Path,
    bucket_count: int,
    class_parallelism: int,
    shards_per_class: int,
) -> dict[str, Any]:
    started = time.time()
    indexed_classes = list(enumerate(manifest["class_csvs"]))
    indexed_classes.sort(key=lambda item: int(item[1]["size_bytes"]), reverse=True)
    completed_rows = 0
    class_rows: dict[str, int] = {}
    for offset in range(0, len(indexed_classes), class_parallelism):
        batch = indexed_classes[offset : offset + class_parallelism]
        tasks = [
            (
                class_item,
                class_index,
                shard,
                shards_per_class,
                bucket_count,
                str(scratch),
            )
            for class_index, class_item in batch
            for shard in range(shards_per_class)
        ]
        workers = min(len(tasks), class_parallelism * shards_per_class)
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
            results = list(executor.map(partition_class_shard, tasks))
        for (class_index, class_item), expected_rows in (
            (
                indexed,
                sum(
                    int(item["rows"])
                    for item in results
                    if int(item["contract"]["class_index"]) == indexed[0]
                ),
            )
            for indexed in batch
        ):
            if expected_rows != int(class_item["rows"]):
                raise ValueError(
                    f"parallel shard rows differ for {class_item['attack_category']}: "
                    f"{expected_rows} != {class_item['rows']}"
                )
            class_rows[class_item["attack_category"]] = expected_rows
            completed_rows += expected_rows
        atomic_json(
            scratch / "partition-progress.json",
            {
                "dataset_id": manifest["dataset_id"],
                "complete": False,
                "rows": completed_rows,
                "expected_rows": manifest["row_count"],
                "class_rows": class_rows,
                "class_parallelism": class_parallelism,
                "shards_per_class": shards_per_class,
                "elapsed_seconds": time.time() - started,
            },
        )
    return {
        "rows": completed_rows,
        "class_rows": class_rows,
        "partition_seconds": time.time() - started,
    }


def inspect_bucket_parallel(task: tuple[str, str, int]) -> dict[str, Any]:
    scratch_text, prefix, bucket = task
    scratch = Path(scratch_text)
    duplicate_rows = 0
    duplicate_keys = 0
    cross_label_keys = 0
    cross_capture_keys = 0
    capture_edges: set[tuple[str, str]] = set()
    examples: list[dict[str, str]] = []
    duplicate_examples: list[dict[str, str]] = []
    seen: dict[bytes, tuple[bytes, bytes, bytes, bytes, int, bool, bool]] = {}
    record = IDENTITY_RECORD if prefix == "identity" else CONTENT_RECORD
    pattern = f"partitions/class-*/shard-*/{prefix}-{bucket:04d}.bin"
    for path in sorted(scratch.glob(pattern)):
        with path.open("rb") as handle:
            while True:
                value = handle.read(record.size)
                if not value:
                    break
                if len(value) != record.size:
                    raise ValueError(f"truncated duplicate-audit bucket: {path}")
                if prefix == "identity":
                    key, label, capture, content_detail = record.unpack(value)
                    sample = key
                else:
                    key, label, capture, sample = record.unpack(value)
                    content_detail = key
                previous = seen.get(key)
                if previous is None:
                    seen[key] = (
                        label,
                        capture,
                        sample,
                        content_detail,
                        1,
                        False,
                        False,
                    )
                    continue
                (
                    previous_label,
                    previous_capture,
                    previous_sample,
                    previous_content,
                    count,
                    label_conflict,
                    capture_conflict,
                ) = previous
                if count == 1:
                    duplicate_keys += 1
                    if len(duplicate_examples) < MAX_EXAMPLES_PER_BUCKET:
                        duplicate_examples.append(
                            {
                                "key_sha256": key.hex(),
                                "first_label_sha256": previous_label.hex(),
                                "second_label_sha256": label.hex(),
                                "first_capture_id": previous_capture.hex(),
                                "second_capture_id": capture.hex(),
                                "first_sample_id": previous_sample.hex(),
                                "second_sample_id": sample.hex(),
                                "first_content_sha256": previous_content.hex(),
                                "second_content_sha256": content_detail.hex(),
                            }
                        )
                duplicate_rows += 1
                if label != previous_label and not label_conflict:
                    cross_label_keys += 1
                    label_conflict = True
                    if len(examples) < MAX_EXAMPLES_PER_BUCKET:
                        examples.append(
                            {
                                "key_sha256": key.hex(),
                                "first_label_sha256": previous_label.hex(),
                                "second_label_sha256": label.hex(),
                                "first_capture_id": previous_capture.hex(),
                                "second_capture_id": capture.hex(),
                                "first_sample_id": previous_sample.hex(),
                                "second_sample_id": sample.hex(),
                                "first_content_sha256": previous_content.hex(),
                                "second_content_sha256": content_detail.hex(),
                            }
                        )
                if capture != previous_capture and not capture_conflict:
                    cross_capture_keys += 1
                    capture_conflict = True
                    left, right = sorted((capture.hex(), previous_capture.hex()))
                    capture_edges.add((left, right))
                seen[key] = (
                    previous_label,
                    previous_capture,
                    previous_sample,
                    previous_content,
                    count + 1,
                    label_conflict,
                    capture_conflict,
                )
    return {
        "bucket": bucket,
        "duplicate_rows_after_first": duplicate_rows,
        "duplicate_key_count": duplicate_keys,
        "cross_label_key_count": cross_label_keys,
        "cross_capture_key_count": cross_capture_keys,
        "capture_equivalence_edges": [list(item) for item in sorted(capture_edges)],
        "duplicate_examples": duplicate_examples,
        "cross_label_examples": examples,
    }


def inspect_buckets_parallel(
    scratch: Path, prefix: str, bucket_count: int, workers: int
) -> dict[str, Any]:
    tasks = [(str(scratch), prefix, bucket) for bucket in range(bucket_count)]
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(inspect_bucket_parallel, tasks))
    capture_edges: set[tuple[str, str]] = set()
    examples: list[dict[str, str]] = []
    duplicate_examples: list[dict[str, str]] = []
    combined = {
        "duplicate_rows_after_first": 0,
        "duplicate_key_count": 0,
        "cross_label_key_count": 0,
        "cross_capture_key_count": 0,
    }
    for result in results:
        for key in combined:
            combined[key] += int(result[key])
        capture_edges.update(tuple(item) for item in result["capture_equivalence_edges"])
        duplicate_examples.extend(result["duplicate_examples"])
        examples.extend(result["cross_label_examples"])
    combined["capture_equivalence_edges"] = [
        list(item) for item in sorted(capture_edges)
    ]
    combined["cross_label_examples"] = examples[:256]
    combined["duplicate_examples"] = duplicate_examples[:256]
    return combined


def build_report_parallel(
    manifest: dict[str, Any],
    scratch: Path,
    bucket_count: int,
    class_parallelism: int,
    shards_per_class: int,
    resume: bool,
) -> dict[str, Any]:
    if not manifest.get("complete"):
        raise ValueError("dataset manifest is not complete")
    if bucket_count < 2:
        raise ValueError("bucket count must be at least two")
    if class_parallelism < 1 or shards_per_class < 1:
        raise ValueError("parallelism must be positive")
    if scratch.exists() and any(scratch.iterdir()) and not resume:
        raise ValueError(f"scratch directory is not empty: {scratch}")
    scratch.mkdir(parents=True, exist_ok=True)
    started = time.time()
    partition = partition_rows_parallel(
        manifest,
        scratch,
        bucket_count,
        class_parallelism,
        shards_per_class,
    )
    if partition["rows"] != int(manifest["row_count"]):
        raise ValueError("duplicate audit row count differs from dataset manifest")
    inspection_workers = class_parallelism * shards_per_class
    identity = inspect_buckets_parallel(
        scratch, "identity", bucket_count, inspection_workers
    )
    content = inspect_buckets_parallel(
        scratch, "content", bucket_count, inspection_workers
    )
    gate_pass = (
        identity["duplicate_key_count"] == 0
        and content["cross_label_key_count"] == 0
    )
    return {
        "schema_version": "caeos_flow_duplicate_audit_v2",
        "dataset_id": manifest["dataset_id"],
        "dataset_manifest_sha256": manifest["manifest_sha256"],
        "row_count": partition["rows"],
        "fingerprint_contract": {
            "identity": "sample_id",
            "content_sha256_scope": "all_model_eligible_source_columns",
            "excluded_non_model_columns": sorted(NON_MODEL_COLUMNS),
            "label_sha256_columns": list(LABEL_COLUMNS),
            "capture_group": "capture_id",
        },
        "identity": identity,
        "content": content,
        "partition_seconds": partition["partition_seconds"],
        "elapsed_seconds": time.time() - started,
        "execution": {
            "mode": "byte_range_parallel_v1",
            "class_parallelism": class_parallelism,
            "shards_per_class": shards_per_class,
            "maximum_worker_processes": class_parallelism * shards_per_class,
            "resume_enabled": resume,
        },
        "gate_pass": gate_pass,
    }


def build_report(
    manifest: dict[str, Any], scratch: Path, bucket_count: int
) -> dict[str, Any]:
    if not manifest.get("complete"):
        raise ValueError("dataset manifest is not complete")
    if bucket_count < 2:
        raise ValueError("bucket count must be at least two")
    if scratch.exists() and any(scratch.iterdir()):
        raise ValueError(f"scratch directory is not empty: {scratch}")
    scratch.mkdir(parents=True, exist_ok=True)
    started = time.time()
    partition = partition_rows(manifest, scratch, bucket_count)
    if partition["rows"] != int(manifest["row_count"]):
        raise ValueError("duplicate audit row count differs from dataset manifest")
    identity = inspect_buckets(scratch, "identity", bucket_count)
    content = inspect_buckets(scratch, "content", bucket_count)
    gate_pass = (
        identity["duplicate_key_count"] == 0
        and content["cross_label_key_count"] == 0
    )
    return {
        "schema_version": "caeos_flow_duplicate_audit_v2",
        "dataset_id": manifest["dataset_id"],
        "dataset_manifest_sha256": manifest["manifest_sha256"],
        "row_count": partition["rows"],
        "fingerprint_contract": {
            "identity": "sample_id",
            "content_sha256_scope": "all_model_eligible_source_columns",
            "excluded_non_model_columns": sorted(NON_MODEL_COLUMNS),
            "label_sha256_columns": list(LABEL_COLUMNS),
            "capture_group": "capture_id",
        },
        "identity": identity,
        "content": content,
        "partition_seconds": partition["partition_seconds"],
        "elapsed_seconds": time.time() - started,
        "gate_pass": gate_pass,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-manifest", required=True, type=Path)
    parser.add_argument("--scratch", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--buckets", type=int, default=256)
    parser.add_argument("--class-parallelism", type=int, default=1)
    parser.add_argument("--shards-per-class", type=int, default=1)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--keep-scratch", action="store_true")
    args = parser.parse_args()
    manifest = load_json(args.dataset_manifest)
    if args.class_parallelism == 1 and args.shards_per_class == 1:
        report = build_report(manifest, args.scratch, args.buckets)
    else:
        report = build_report_parallel(
            manifest,
            args.scratch,
            args.buckets,
            args.class_parallelism,
            args.shards_per_class,
            args.resume,
        )
    atomic_json(args.output, report)
    if not args.keep_scratch:
        shutil.rmtree(args.scratch)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
