from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any

from audit_caeos_flow_duplicates import digest_fields, model_content_columns
from repair_caeos_sample_id_collisions import (
    atomic_json,
    canonical_json_hash,
    repaired_sample_id,
    sample_id_bounds,
    sha256_file,
    verified_embedded_hash,
)


csv.field_size_limit(2**31 - 1)

REPAIR_SCHEMA = "caeos_ciciot2023_inplace_sample_id_repair_v1"
PROOF_SCHEMA = "caeos_sample_id_delta_uniqueness_proof_v1"
DATASET_ID = "ciciot2023"
CLASS_NAME = "DDoS"
READ_BYTES = 64 * 1024 * 1024
PROGRESS_BYTES = 16 * 1024 * 1024 * 1024


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def atomic_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def duplicate_ids_from_audit(audit: dict[str, Any]) -> dict[bytes, int]:
    identity = audit.get("identity", {})
    duplicate_keys = int(identity.get("duplicate_key_count", -1))
    duplicate_rows = int(identity.get("duplicate_rows_after_first", -1))
    examples = identity.get("duplicate_examples", [])
    if duplicate_keys < 1 or duplicate_rows < 1:
        raise ValueError("source audit contains no sample_id collision")
    keys = {
        bytes.fromhex(str(item["key_sha256"]))
        for item in examples
        if isinstance(item, dict) and item.get("key_sha256")
    }
    if len(keys) != duplicate_keys:
        raise ValueError("source audit does not retain every duplicate sample_id")
    if duplicate_rows != duplicate_keys:
        raise ValueError(
            "this bounded repair requires exactly two occurrences per duplicate key"
        )
    return {key: 2 for key in keys}


def scan_part(task: tuple[str, tuple[bytes, ...]]) -> list[dict[str, Any]]:
    path_text, targets = task
    path = Path(path_text)
    target_set = set(targets)
    matches: list[dict[str, Any]] = []
    row_index = 0
    with path.open("rb") as handle:
        while True:
            line_offset = handle.tell()
            line = handle.readline()
            if not line:
                break
            if not line.endswith(b"\r\n"):
                raise ValueError(f"part row does not use the frozen CRLF contract: {path}")
            bounds = sample_id_bounds(line, 3)
            start, end = bounds
            sample_id = bytes.fromhex(line[start:end].decode("ascii"))
            if sample_id in target_set:
                values = next(csv.reader([line.decode("utf-8")]))
                matches.append(
                    {
                        "part_path": str(path),
                        "line_offset": line_offset,
                        "row_index": row_index,
                        "sample_offset": line_offset + start,
                        "sample_start_in_line": start,
                        "sample_end_in_line": end,
                        "line": line,
                        "values": values,
                    }
                )
            row_index += 1
    return matches


def scan_parts_parallel(
    part_paths: list[Path], duplicate_ids: dict[bytes, int], workers: int
) -> list[dict[str, Any]]:
    targets = tuple(sorted(duplicate_ids))
    tasks = [(str(path), targets) for path in part_paths]
    matches: list[dict[str, Any]] = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        for result in executor.map(scan_part, tasks):
            matches.extend(result)
    observed: dict[bytes, int] = {}
    for item in matches:
        start = int(item["sample_start_in_line"])
        end = int(item["sample_end_in_line"])
        sample_id = bytes.fromhex(item["line"][start:end].decode("ascii"))
        observed[sample_id] = observed.get(sample_id, 0) + 1
    if observed != duplicate_ids:
        raise ValueError(
            f"part occurrence counts differ from audit: {observed!r} != {duplicate_ids!r}"
        )
    return matches


def part_category(path: Path, category_index: int) -> str:
    with path.open("rb") as handle:
        line = handle.readline()
    if not line.endswith(b"\r\n"):
        raise ValueError(f"part row does not use the frozen CRLF contract: {path}")
    row = next(csv.reader([line.decode("utf-8")]))
    if category_index >= len(row):
        raise ValueError(f"part row is narrower than the final schema: {path}")
    return row[category_index]


def build_part_offsets(
    output_root: Path,
    manifest: dict[str, Any],
    columns: list[str],
) -> tuple[dict[str, int], dict[str, dict[str, Any]], bytes]:
    class_entries = {
        str(item["attack_category"]): item for item in manifest["class_csvs"]
    }
    if CLASS_NAME not in class_entries:
        raise ValueError(f"{CLASS_NAME} class is absent from the dataset manifest")
    header = (",".join(columns) + "\n").encode("utf-8")
    offsets = {category: len(header) for category in class_entries}
    part_map: dict[str, dict[str, Any]] = {}
    marker_root = output_root / "_captures" / DATASET_ID
    marker_paths = sorted(marker_root.glob("*.json"), key=lambda path: path.stem)
    if len(marker_paths) != int(manifest["capture_count"]):
        raise ValueError("capture marker count differs from the dataset manifest")
    category_index = columns.index("attack_category")
    for marker_path in marker_paths:
        marker = load_json(marker_path)
        if marker.get("capture_id") != marker_path.stem or not marker.get("complete"):
            raise ValueError(f"invalid capture marker: {marker_path}")
        parts = sorted(marker["parts"], key=lambda item: item["part_path"])
        if not parts:
            raise ValueError(f"capture marker has no parts: {marker_path}")
        category = part_category(Path(parts[0]["part_path"]), category_index)
        label_signatures = {
            (
                item["label"]["fine_label"],
                item["label"]["family_label"],
                int(item["label"]["binary_label"]),
            )
            for item in parts
        }
        if len(label_signatures) != 1:
            raise ValueError(f"CICIoT2023 capture contains mixed part labels: {marker_path}")
        for part in parts:
            path = Path(part["part_path"])
            size = path.stat().st_size
            if size != int(part["part_size_bytes"]):
                raise ValueError(f"part size differs from marker: {path}")
            if category not in offsets:
                raise ValueError(f"part category is absent from final classes: {category}")
            rows = int(part["counters"]["rows"])
            normalized_size = size - rows
            if normalized_size < 1:
                raise ValueError(f"invalid normalized part size: {path}")
            part_map[str(path)] = {
                "base_offset": offsets[category],
                "category": category,
                "marker": marker,
                "marker_path": marker_path,
                "part": part,
                "normalized_size_bytes": normalized_size,
            }
            offsets[category] += normalized_size
    for category, entry in class_entries.items():
        if offsets[category] != int(entry["size_bytes"]):
            raise ValueError(
                f"part concatenation size differs for {category}: "
                f"{offsets[category]} != {entry['size_bytes']}"
            )
    return offsets, part_map, header


def new_ids_absent_from_old_audit(
    scratch: Path, new_ids: list[bytes], bucket_count: int, workers: int
) -> None:
    def scan_bucket(task: tuple[int, tuple[bytes, ...]]) -> list[str]:
        bucket, targets = task
        found: set[bytes] = set()
        for path in scratch.glob(
            f"partitions/class-*/shard-*/identity-{bucket:04d}.bin"
        ):
            with path.open("rb") as handle:
                while value := handle.read(128):
                    if len(value) != 128:
                        raise ValueError(f"truncated identity audit partition: {path}")
                    sample_id = value[:32]
                    if sample_id in targets:
                        found.add(sample_id)
        return [item.hex() for item in sorted(found)]

    by_bucket: dict[int, list[bytes]] = {}
    for sample_id in new_ids:
        bucket = int.from_bytes(sample_id[:4], "big") % bucket_count
        by_bucket.setdefault(bucket, []).append(sample_id)
    tasks = [(bucket, tuple(values)) for bucket, values in sorted(by_bucket.items())]
    found: list[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        for result in executor.map(scan_bucket, tasks):
            found.extend(result)
    if found:
        raise ValueError(f"replacement sample_id already exists: {found}")


def hash_with_substitutions(
    path: Path,
    patches: list[dict[str, Any]],
    progress_path: Path,
) -> tuple[str, str]:
    old_digest = hashlib.sha256()
    new_digest = hashlib.sha256()
    size = path.stat().st_size
    started = time.time()
    last_progress = 0
    position = 0

    def consume(handle: Any, length: int) -> None:
        nonlocal position, last_progress
        remaining = length
        while remaining:
            chunk = handle.read(min(READ_BYTES, remaining))
            if not chunk:
                raise ValueError(f"unexpected EOF while hashing {path}")
            old_digest.update(chunk)
            new_digest.update(chunk)
            position += len(chunk)
            remaining -= len(chunk)
            if position - last_progress >= PROGRESS_BYTES:
                elapsed = max(time.time() - started, 1e-9)
                atomic_json(
                    progress_path,
                    {
                        "complete": False,
                        "bytes": position,
                        "size_bytes": size,
                        "fraction": position / size,
                        "elapsed_seconds": elapsed,
                        "bytes_per_second": position / elapsed,
                        "eta_seconds": (size - position) / (position / elapsed),
                    },
                )
                last_progress = position

    with path.open("rb") as handle:
        for patch in sorted(patches, key=lambda item: int(item["final_sample_offset"])):
            offset = int(patch["final_sample_offset"])
            if offset < position:
                raise ValueError("overlapping or unsorted substitutions")
            consume(handle, offset - position)
            old_value = handle.read(64)
            if old_value != patch["old_sample_id"].encode("ascii"):
                raise ValueError(f"source token changed before hash: offset={offset}")
            old_digest.update(old_value)
            new_digest.update(patch["new_sample_id"].encode("ascii"))
            position += 64
        consume(handle, size - position)
        if handle.read(1):
            raise ValueError("file grew during substitution hash")
    elapsed = time.time() - started
    atomic_json(
        progress_path,
        {
            "complete": True,
            "bytes": size,
            "size_bytes": size,
            "fraction": 1.0,
            "elapsed_seconds": elapsed,
            "bytes_per_second": size / max(elapsed, 1e-9),
            "eta_seconds": 0.0,
        },
    )
    return old_digest.hexdigest(), new_digest.hexdigest()


def apply_fixed_width_patches(
    path: Path,
    patches: list[dict[str, Any]],
    offset_key: str,
) -> None:
    descriptor = os.open(path, os.O_RDWR)
    applied: list[dict[str, Any]] = []
    try:
        for patch in sorted(patches, key=lambda item: int(item[offset_key])):
            offset = int(patch[offset_key])
            old_value = patch["old_sample_id"].encode("ascii")
            new_value = patch["new_sample_id"].encode("ascii")
            if len(old_value) != 64 or len(new_value) != 64:
                raise ValueError("sample_id patch is not fixed width")
            if os.pread(descriptor, 64, offset) != old_value:
                raise ValueError(f"patch precondition failed: {path}:{offset}")
            if os.pwrite(descriptor, new_value, offset) != 64:
                raise OSError(f"short pwrite: {path}:{offset}")
            applied.append(patch)
        os.fsync(descriptor)
        for patch in applied:
            offset = int(patch[offset_key])
            if os.pread(descriptor, 64, offset) != patch["new_sample_id"].encode(
                "ascii"
            ):
                raise ValueError(f"patch verification failed: {path}:{offset}")
    except BaseException:
        for patch in reversed(applied):
            os.pwrite(
                descriptor,
                patch["old_sample_id"].encode("ascii"),
                int(patch[offset_key]),
            )
        os.fsync(descriptor)
        raise
    finally:
        os.close(descriptor)


def build_plan(
    output_root: Path,
    manifest: dict[str, Any],
    audit: dict[str, Any],
    scratch: Path,
    workers: int,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], bytes]:
    duplicate_ids = duplicate_ids_from_audit(audit)
    if audit.get("dataset_id") != DATASET_ID:
        raise ValueError("source audit dataset mismatch")
    if audit.get("dataset_manifest_sha256") != manifest.get("manifest_sha256"):
        raise ValueError("source audit does not bind the current dataset manifest")
    class_entry = next(
        item for item in manifest["class_csvs"] if item["attack_category"] == CLASS_NAME
    )
    class_path = Path(class_entry["path"])
    with class_path.open("rb") as handle:
        raw_header = handle.readline()
    columns = next(csv.reader([raw_header.decode("utf-8")]))
    _, part_map, expected_header = build_part_offsets(output_root, manifest, columns)
    if raw_header != expected_header:
        raise ValueError("final class header differs from the part concatenation contract")

    example_captures = {
        str(item["first_capture_id"])
        for item in audit["identity"]["duplicate_examples"]
    }
    example_captures.update(
        str(item["second_capture_id"])
        for item in audit["identity"]["duplicate_examples"]
    )
    if len(example_captures) != 1:
        raise ValueError("bounded CICIoT2023 repair expects one affected capture")
    capture_id = next(iter(example_captures))
    marker_path = output_root / "_captures" / DATASET_ID / f"{capture_id}.json"
    marker = load_json(marker_path)
    part_paths = [Path(item["part_path"]) for item in marker["parts"]]
    matches = scan_parts_parallel(part_paths, duplicate_ids, workers)

    grouped: dict[bytes, list[dict[str, Any]]] = {}
    for item in matches:
        start = int(item["sample_start_in_line"])
        end = int(item["sample_end_in_line"])
        old_id = bytes.fromhex(item["line"][start:end].decode("ascii"))
        grouped.setdefault(old_id, []).append(item)

    plan: list[dict[str, Any]] = []
    fieldnames = columns
    content_columns = model_content_columns(fieldnames)
    class_descriptor = os.open(class_path, os.O_RDONLY)
    try:
        for old_id, occurrences in sorted(grouped.items()):
            occurrences.sort(key=lambda item: (item["part_path"], item["line_offset"]))
            for ordinal, item in enumerate(occurrences, start=1):
                values = item["values"]
                if len(values) != len(fieldnames):
                    raise ValueError("affected part row width differs from final schema")
                row = dict(zip(fieldnames, values))
                content_sha256 = digest_fields(row, content_columns)
                new_id = repaired_sample_id(old_id, content_sha256, ordinal)
                mapping = part_map[item["part_path"]]
                if mapping["category"] != CLASS_NAME:
                    raise ValueError("duplicate sample_id is outside the expected DDoS class")
                row_index = int(item["row_index"])
                final_line_offset = (
                    int(mapping["base_offset"])
                    + int(item["line_offset"])
                    - row_index
                )
                final_sample_offset = (
                    int(mapping["base_offset"])
                    + int(item["sample_offset"])
                    - row_index
                )
                part_line = item["line"]
                if not part_line.endswith(b"\r\n"):
                    raise ValueError("affected part row does not use CRLF")
                expected_final_line = part_line[:-2] + b"\n"
                final_line = os.pread(
                    class_descriptor, len(expected_final_line), final_line_offset
                )
                if final_line != expected_final_line:
                    raise ValueError(
                        "target part row is not byte-identical to the final class CSV"
                    )
                plan.append(
                    {
                        "capture_id": capture_id,
                        "class_path": str(class_path),
                        "content_sha256": content_sha256.hex(),
                        "final_line_offset": final_line_offset,
                        "final_sample_offset": final_sample_offset,
                        "final_line_sha256": hashlib.sha256(
                            expected_final_line
                        ).hexdigest(),
                        "new_sample_id": new_id.decode("ascii"),
                        "occurrence_ordinal": ordinal,
                        "old_sample_id": old_id.hex(),
                        "part_line_offset": int(item["line_offset"]),
                        "part_line_sha256": hashlib.sha256(part_line).hexdigest(),
                        "part_path": item["part_path"],
                        "part_sample_offset": int(item["sample_offset"]),
                    }
                )
    finally:
        os.close(class_descriptor)
    new_ids = [bytes.fromhex(item["new_sample_id"]) for item in plan]
    if len(new_ids) != len(set(new_ids)):
        raise ValueError("repair generated duplicate replacement sample_id values")
    identity_paths = list(
        (scratch / "partitions").glob("class-*/shard-*/identity-*.bin")
    )
    if not identity_paths:
        raise ValueError("cannot infer retained audit bucket count")
    bucket_count = (
        max(int(path.stem.rsplit("-", 1)[1]) for path in identity_paths) + 1
    )
    if bucket_count < 2:
        raise ValueError("retained audit has fewer than two identity buckets")
    new_ids_absent_from_old_audit(scratch, new_ids, bucket_count, workers)
    return plan, part_map, raw_header


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.workers != 8:
        raise ValueError("this repair is frozen to exactly eight worker processes")
    manifest_path = args.output_root / DATASET_ID / "dataset.manifest.json"
    manifest = load_json(manifest_path)
    old_manifest_sha256 = verified_embedded_hash(manifest, "manifest_sha256")
    if manifest.get("dataset_id") != DATASET_ID or not manifest.get("complete"):
        raise ValueError("completed CICIoT2023 manifest required")
    completion = load_json(args.completion)
    old_completion_sha256 = verified_embedded_hash(completion, "completion_sha256")
    audit = load_json(args.audit)
    plan, part_map, _ = build_plan(
        args.output_root, manifest, audit, args.scratch, args.workers
    )
    if len(plan) != 4:
        raise ValueError(f"expected four affected rows, observed {len(plan)}")

    transaction = args.repair_root / args.transaction_id
    if transaction.exists():
        raise FileExistsError(transaction)
    transaction.mkdir(parents=True)
    serializable_plan = [dict(item) for item in plan]
    atomic_json(
        transaction / "repair_plan.json",
        {
            "schema_version": REPAIR_SCHEMA,
            "dataset_id": DATASET_ID,
            "transaction_id": args.transaction_id,
            "workers": args.workers,
            "patches": serializable_plan,
            "source_audit_path": str(args.audit),
            "source_audit_sha256": sha256_file(args.audit),
            "old_manifest_sha256": old_manifest_sha256,
            "old_completion_sha256": old_completion_sha256,
        },
    )
    if not args.apply:
        return {
            "status": "dry_run_complete",
            "transaction_id": args.transaction_id,
            "patch_count": len(plan),
            "workers": args.workers,
        }

    atomic_bytes(transaction / "dataset.manifest.pre_repair.json", manifest_path.read_bytes())
    atomic_bytes(transaction / "completion.pre_repair.json", args.completion.read_bytes())
    affected_marker_paths = sorted(
        {Path(part_map[item["part_path"]]["marker_path"]) for item in plan}
    )
    for marker_path in affected_marker_paths:
        atomic_bytes(
            transaction / f"{marker_path.stem}.marker.pre_repair.json",
            marker_path.read_bytes(),
        )

    class_entry = next(
        item for item in manifest["class_csvs"] if item["attack_category"] == CLASS_NAME
    )
    class_path = Path(class_entry["path"])
    before = class_path.stat()
    old_sha256, new_sha256 = hash_with_substitutions(
        class_path, plan, transaction / "hash_progress.json"
    )
    after_hash = class_path.stat()
    if (before.st_size, before.st_mtime_ns) != (
        after_hash.st_size,
        after_hash.st_mtime_ns,
    ):
        raise ValueError("DDoS CSV changed during substitution hashing")
    if old_sha256 != class_entry["sha256"]:
        raise ValueError("DDoS CSV SHA-256 differs from the source manifest")

    part_groups: dict[Path, list[dict[str, Any]]] = {}
    for item in plan:
        part_groups.setdefault(Path(item["part_path"]), []).append(item)
    old_part_hashes: dict[str, str] = {}
    new_part_hashes: dict[str, str] = {}
    for path, patches in sorted(part_groups.items(), key=lambda item: str(item[0])):
        marker_part = part_map[str(path)]["part"]
        old_part_hashes[str(path)] = sha256_file(path)
        if old_part_hashes[str(path)] != marker_part["part_sha256"]:
            raise ValueError(f"part SHA-256 differs from marker: {path}")

    applied_parts: list[Path] = []
    class_applied = False
    try:
        for path, patches in sorted(part_groups.items(), key=lambda item: str(item[0])):
            apply_fixed_width_patches(path, patches, "part_sample_offset")
            applied_parts.append(path)
            new_part_hashes[str(path)] = sha256_file(path)
        apply_fixed_width_patches(class_path, plan, "final_sample_offset")
        class_applied = True
        if class_path.stat().st_size != before.st_size:
            raise ValueError("in-place repair changed DDoS CSV size")

        marker_updates: dict[Path, dict[str, Any]] = {}
        for marker_path in affected_marker_paths:
            marker = load_json(marker_path)
            for part in marker["parts"]:
                path_text = str(part["part_path"])
                if path_text in new_part_hashes:
                    part["part_sha256"] = new_part_hashes[path_text]
            marker["identity_repair"] = {
                "schema_version": REPAIR_SCHEMA,
                "transaction_id": args.transaction_id,
                "modified_columns": ["sample_id"],
                "rewritten_rows": len(plan),
                "rows_deleted": 0,
                "feature_columns_modified": False,
                "label_columns_modified": False,
            }
            marker.pop("marker_sha256", None)
            marker["marker_sha256"] = canonical_json_hash(marker)
            marker_updates[marker_path] = marker

        new_manifest = json.loads(json.dumps(manifest))
        new_entry = next(
            item
            for item in new_manifest["class_csvs"]
            if item["attack_category"] == CLASS_NAME
        )
        new_entry["sha256"] = new_sha256
        repair_metadata = {
            "schema_version": REPAIR_SCHEMA,
            "transaction_id": args.transaction_id,
            "duplicate_keys": 2,
            "duplicate_rows_after_first": 2,
            "rewritten_rows": len(plan),
            "rows_deleted": 0,
            "modified_columns": ["sample_id"],
            "feature_columns_modified": False,
            "label_columns_modified": False,
            "source_parts_modified": True,
            "source_audit_path": str(args.audit),
            "source_audit_sha256": sha256_file(args.audit),
            "repair_plan_path": str(transaction / "repair_plan.json"),
            "repair_rule": "duplicate_only_content_ordinal_rekey_v1",
        }
        new_manifest["identity_repair"] = repair_metadata
        new_manifest.pop("manifest_sha256", None)
        new_manifest["manifest_sha256"] = canonical_json_hash(new_manifest)

        completion_matches = [
            index
            for index, item in enumerate(completion.get("datasets", []))
            if item.get("dataset_id") == DATASET_ID
        ]
        if len(completion_matches) != 1:
            raise ValueError("completion does not contain exactly one CICIoT2023 record")
        if completion["datasets"][completion_matches[0]] != manifest:
            raise ValueError("completion record is not the exact source manifest")
        new_completion = json.loads(json.dumps(completion))
        new_completion["datasets"][completion_matches[0]] = new_manifest
        new_completion.pop("completion_sha256", None)
        new_completion["completion_sha256"] = canonical_json_hash(new_completion)

        for path, marker in marker_updates.items():
            atomic_json(path, marker)
        atomic_json(manifest_path, new_manifest)
        atomic_json(args.completion, new_completion)

        proof = {
            "schema_version": PROOF_SCHEMA,
            "dataset_id": DATASET_ID,
            "transaction_id": args.transaction_id,
            "source_audit_path": str(args.audit),
            "source_audit_sha256": sha256_file(args.audit),
            "source_duplicate_key_count": 2,
            "source_duplicate_rows_after_first": 2,
            "replacement_count": len(plan),
            "replacement_ids_distinct": True,
            "replacement_ids_absent_from_source_identity_set": True,
            "post_repair_duplicate_key_count": 0,
            "post_repair_duplicate_rows_after_first": 0,
            "proof_rule": (
                "the full source audit found exactly two duplicate keys with two "
                "occurrences each; all four occurrences were replaced by distinct "
                "IDs proven absent from the retained full identity partitions"
            ),
            "new_manifest_sha256": new_manifest["manifest_sha256"],
            "new_completion_sha256": new_completion["completion_sha256"],
            "old_ddos_sha256": old_sha256,
            "new_ddos_sha256": new_sha256,
            "features_modified": False,
            "labels_modified": False,
            "rows_deleted": 0,
        }
        atomic_json(transaction / "delta_uniqueness_proof.json", proof)
        receipt = {
            "schema_version": REPAIR_SCHEMA,
            "status": "applied",
            "dataset_id": DATASET_ID,
            "transaction_id": args.transaction_id,
            "patch_count": len(plan),
            "workers": args.workers,
            "new_manifest_sha256": new_manifest["manifest_sha256"],
            "new_completion_sha256": new_completion["completion_sha256"],
            "new_ddos_sha256": new_sha256,
            "proof_path": str(transaction / "delta_uniqueness_proof.json"),
        }
        atomic_json(transaction / "application_receipt.json", receipt)
        return receipt
    except BaseException as error:
        if class_applied:
            apply_fixed_width_patches(
                class_path,
                [
                    {
                        **item,
                        "old_sample_id": item["new_sample_id"],
                        "new_sample_id": item["old_sample_id"],
                    }
                    for item in plan
                ],
                "final_sample_offset",
            )
        for path in reversed(applied_parts):
            patches = part_groups[path]
            apply_fixed_width_patches(
                path,
                [
                    {
                        **item,
                        "old_sample_id": item["new_sample_id"],
                        "new_sample_id": item["old_sample_id"],
                    }
                    for item in patches
                ],
                "part_sample_offset",
            )
        for marker_path in affected_marker_paths:
            marker_backup = (
                transaction / f"{marker_path.stem}.marker.pre_repair.json"
            )
            atomic_bytes(marker_path, marker_backup.read_bytes())
        atomic_bytes(
            manifest_path,
            (transaction / "dataset.manifest.pre_repair.json").read_bytes(),
        )
        atomic_bytes(
            args.completion,
            (transaction / "completion.pre_repair.json").read_bytes(),
        )
        atomic_json(
            transaction / "rollback_receipt.json",
            {
                "schema_version": REPAIR_SCHEMA,
                "status": "rolled_back",
                "dataset_id": DATASET_ID,
                "transaction_id": args.transaction_id,
                "error_type": type(error).__name__,
                "error": str(error),
                "data_patches_reverted": True,
                "control_files_restored": True,
            },
        )
        raise


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Repair the bounded CICIoT2023 sample_id collisions without copying the 2.8 TB class CSV."
    )
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--completion", required=True, type=Path)
    parser.add_argument("--audit", required=True, type=Path)
    parser.add_argument("--scratch", required=True, type=Path)
    parser.add_argument("--repair-root", required=True, type=Path)
    parser.add_argument("--transaction-id", required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--apply", action="store_true")
    return parser.parse_args()


def main() -> None:
    result = run(parse_arguments())
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
