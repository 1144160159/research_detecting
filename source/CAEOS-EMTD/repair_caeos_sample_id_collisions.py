from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import struct
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO

from audit_caeos_flow_duplicates import digest_fields, model_content_columns


csv.field_size_limit(2**31 - 1)

IDENTITY_RECORD = struct.Struct("!32s32s32s32s")
ID_DOMAIN = b"caeos_sample_id_v2\0"
REPAIR_SCHEMA = "caeos_sample_id_collision_repair_v1"
REPAIR_RULE = "duplicate_only_content_ordinal_rekey_v1"
ZERO_SAMPLE_ID = b"0" * 64


def canonical_json_hash(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sha256_file(path: Path, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_bytes):
            digest.update(chunk)
    return digest.hexdigest()


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


def verified_embedded_hash(value: dict[str, Any], field: str) -> str:
    expected = value.get(field)
    if not isinstance(expected, str) or len(expected) != 64:
        raise ValueError(f"missing or invalid {field}")
    payload = dict(value)
    del payload[field]
    actual = canonical_json_hash(payload)
    if actual != expected:
        raise ValueError(f"{field} mismatch: expected {expected}, calculated {actual}")
    return expected


def collect_duplicate_ids(scratch: Path) -> dict[bytes, int]:
    paths = sorted(scratch.glob("partitions/class-*/shard-*/identity-*.bin"))
    if not paths:
        raise ValueError(f"no retained identity partitions under {scratch}")

    by_bucket: dict[str, list[Path]] = defaultdict(list)
    for path in paths:
        by_bucket[path.name].append(path)

    duplicates: dict[bytes, int] = {}
    for name in sorted(by_bucket):
        counts: dict[bytes, int] = {}
        for path in by_bucket[name]:
            if path.stat().st_size % IDENTITY_RECORD.size:
                raise ValueError(f"truncated identity partition: {path}")
            with path.open("rb") as handle:
                while value := handle.read(IDENTITY_RECORD.size):
                    sample_id, _label, _capture, _content = IDENTITY_RECORD.unpack(value)
                    counts[sample_id] = counts.get(sample_id, 0) + 1
        duplicates.update(
            (sample_id, count) for sample_id, count in counts.items() if count > 1
        )
    if not duplicates:
        raise ValueError("retained audit has no duplicate sample_id values")
    return duplicates


def sample_id_bounds(line: bytes, index: int) -> tuple[int, int]:
    start = 0
    for _ in range(index):
        comma = line.find(b",", start)
        if comma < 0:
            raise ValueError("CSV row ends before sample_id column")
        start = comma + 1
    end = line.find(b",", start)
    if end < 0:
        end = len(line.rstrip(b"\r\n"))
    token = line[start:end]
    if len(token) != 64:
        raise ValueError(f"sample_id is not fixed-width hex: {token[:80]!r}")
    try:
        bytes.fromhex(token.decode("ascii"))
    except (UnicodeDecodeError, ValueError) as error:
        raise ValueError("sample_id is not hexadecimal") from error
    return start, end


def parse_csv_line(line: bytes, fieldnames: list[str]) -> dict[str, str]:
    values = next(csv.reader([line.decode("utf-8")]))
    if len(values) != len(fieldnames):
        raise ValueError(
            f"CSV column count mismatch: expected {len(fieldnames)}, observed {len(values)}"
        )
    return dict(zip(fieldnames, values))


def repaired_sample_id(
    old_sample_id: bytes, content_sha256: bytes, occurrence_ordinal: int
) -> bytes:
    if occurrence_ordinal < 1:
        raise ValueError("occurrence ordinal must be positive")
    digest = hashlib.sha256()
    digest.update(ID_DOMAIN)
    digest.update(old_sample_id)
    digest.update(content_sha256)
    digest.update(struct.pack("!Q", occurrence_ordinal))
    return digest.hexdigest().encode("ascii")


def update_zeroed_digest(
    digest: Any, line: bytes, bounds: tuple[int, int]
) -> None:
    start, end = bounds
    digest.update(line[:start])
    digest.update(ZERO_SAMPLE_ID)
    digest.update(line[end:])


def rewrite_class_csv(
    source: Path,
    target: Path,
    manifest_entry: dict[str, Any],
    duplicate_ids: dict[bytes, int],
    observed: dict[bytes, int],
    generated_ids: set[bytes],
    mapping: BinaryIO,
) -> dict[str, Any]:
    source_hash = hashlib.sha256()
    target_hash = hashlib.sha256()
    source_zeroed_hash = hashlib.sha256()
    row_count = 0
    rewritten_rows = 0

    target.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as reader, target.open("wb") as writer:
        header = reader.readline()
        if not header:
            raise ValueError(f"empty CSV: {source}")
        fieldnames = next(csv.reader([header.decode("utf-8-sig")]))
        if "sample_id" not in fieldnames:
            raise ValueError(f"sample_id column missing: {source}")
        sample_index = fieldnames.index("sample_id")
        if fieldnames[:sample_index] != ["schema_version", "dataset_id", "dataset_role"]:
            raise ValueError(
                f"sample_id fast-path prefix changed in {source}: "
                f"{fieldnames[:sample_index]!r}"
            )
        content_columns = model_content_columns(fieldnames)
        source_hash.update(header)
        target_hash.update(header)
        source_zeroed_hash.update(header)
        writer.write(header)

        for line in reader:
            row_count += 1
            source_hash.update(line)
            bounds = sample_id_bounds(line, sample_index)
            update_zeroed_digest(source_zeroed_hash, line, bounds)
            start, end = bounds
            old_sample_id = bytes.fromhex(line[start:end].decode("ascii"))

            expected_count = duplicate_ids.get(old_sample_id)
            if expected_count is None:
                writer.write(line)
                target_hash.update(line)
                continue

            row = parse_csv_line(line, fieldnames)
            if row["sample_id"] != old_sample_id.hex():
                raise ValueError(f"sample_id parser disagreement in {source}:{row_count + 1}")
            content_sha256 = digest_fields(row, content_columns)
            ordinal = observed.get(old_sample_id, 0) + 1
            if ordinal > expected_count:
                raise ValueError(f"sample_id multiplicity exceeds retained audit in {source}")
            observed[old_sample_id] = ordinal
            new_sample_id = repaired_sample_id(old_sample_id, content_sha256, ordinal)
            if new_sample_id in generated_ids:
                raise ValueError("repair generated duplicate replacement sample_id")
            generated_ids.add(new_sample_id)

            repaired_line = line[:start] + new_sample_id + line[end:]
            if len(repaired_line) != len(line):
                raise ValueError("sample_id repair changed CSV byte length")
            writer.write(repaired_line)
            target_hash.update(repaired_line)
            rewritten_rows += 1
            record = {
                "attack_category": manifest_entry["attack_category"],
                "content_sha256": content_sha256.hex(),
                "new_sample_id": new_sample_id.decode("ascii"),
                "occurrence_ordinal": ordinal,
                "old_sample_id": old_sample_id.hex(),
                "row_number": row_count + 1,
                "source_file": source.name,
            }
            mapping.write(
                (json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n").encode(
                    "utf-8"
                )
            )

        writer.flush()
        os.fsync(writer.fileno())

    expected_rows = int(manifest_entry["rows"])
    if row_count != expected_rows:
        raise ValueError(
            f"row count mismatch for {source}: expected {expected_rows}, observed {row_count}"
        )
    expected_size = int(manifest_entry["size_bytes"])
    source_size = source.stat().st_size
    target_size = target.stat().st_size
    if source_size != expected_size or target_size != source_size:
        raise ValueError(f"size mismatch while repairing {source}")
    old_sha256 = source_hash.hexdigest()
    if old_sha256 != manifest_entry["sha256"]:
        raise ValueError(f"source SHA-256 mismatch for {source}")
    shutil.copymode(source, target)
    return {
        "attack_category": manifest_entry["attack_category"],
        "new_sha256": target_hash.hexdigest(),
        "normalized_sample_id_zeroed_sha256": source_zeroed_hash.hexdigest(),
        "old_sha256": old_sha256,
        "path": str(source),
        "rewritten_rows": rewritten_rows,
        "rows": row_count,
        "size_bytes": source_size,
    }


def verify_class_csv_pair(
    source: Path,
    repaired: Path,
    duplicate_ids: dict[bytes, int],
) -> dict[str, Any]:
    source_zeroed = hashlib.sha256()
    repaired_zeroed = hashlib.sha256()
    changed_rows = 0
    rows = 0
    with source.open("rb") as left, repaired.open("rb") as right:
        left_header = left.readline()
        right_header = right.readline()
        if left_header != right_header:
            raise ValueError(f"header changed: {source}")
        fieldnames = next(csv.reader([left_header.decode("utf-8-sig")]))
        sample_index = fieldnames.index("sample_id")
        source_zeroed.update(left_header)
        repaired_zeroed.update(right_header)
        while True:
            left_line = left.readline()
            right_line = right.readline()
            if not left_line and not right_line:
                break
            if not left_line or not right_line:
                raise ValueError(f"line count changed: {source}")
            rows += 1
            left_bounds = sample_id_bounds(left_line, sample_index)
            right_bounds = sample_id_bounds(right_line, sample_index)
            update_zeroed_digest(source_zeroed, left_line, left_bounds)
            update_zeroed_digest(repaired_zeroed, right_line, right_bounds)
            left_start, left_end = left_bounds
            right_start, right_end = right_bounds
            if left_line[:left_start] != right_line[:right_start]:
                raise ValueError(f"bytes before sample_id changed: {source}:{rows + 1}")
            if left_line[left_end:] != right_line[right_end:]:
                raise ValueError(f"bytes after sample_id changed: {source}:{rows + 1}")
            old_id = bytes.fromhex(left_line[left_start:left_end].decode("ascii"))
            new_id = right_line[right_start:right_end]
            if old_id in duplicate_ids:
                if new_id == left_line[left_start:left_end]:
                    raise ValueError(f"duplicate sample_id was not repaired: {source}:{rows + 1}")
                changed_rows += 1
            elif new_id != left_line[left_start:left_end]:
                raise ValueError(f"non-duplicate sample_id changed: {source}:{rows + 1}")
    source_digest = source_zeroed.hexdigest()
    repaired_digest = repaired_zeroed.hexdigest()
    if source_digest != repaired_digest:
        raise ValueError(f"non-sample_id byte digest mismatch: {source}")
    return {
        "changed_rows": changed_rows,
        "normalized_sample_id_zeroed_sha256": source_digest,
        "rows": rows,
    }


def repair_dataset(
    dataset_manifest_path: Path,
    completion_path: Path,
    scratch: Path,
    diagnosis_path: Path,
    source_audit_path: Path,
    repair_root: Path,
    expected_dataset_id: str,
    transaction_id: str,
) -> dict[str, Any]:
    manifest = load_json(dataset_manifest_path)
    old_manifest_sha256 = verified_embedded_hash(manifest, "manifest_sha256")
    completion = load_json(completion_path)
    old_completion_sha256 = verified_embedded_hash(completion, "completion_sha256")
    if manifest.get("dataset_id") != expected_dataset_id:
        raise ValueError("dataset manifest identity mismatch")
    if not manifest.get("complete") or not completion.get("all_complete"):
        raise ValueError("repair requires completed source artifacts")

    dataset_dir = dataset_manifest_path.parent.resolve()
    if dataset_manifest_path.resolve() != dataset_dir / "dataset.manifest.json":
        raise ValueError("dataset manifest must be dataset_dir/dataset.manifest.json")
    data_root = dataset_dir.parent
    staging_dir = data_root / f".{expected_dataset_id}.sample-id-v2.{transaction_id}.staging"
    backup_dir = data_root / f"{expected_dataset_id}.pre-sample-id-v2.{transaction_id}"
    repair_staging = repair_root / f".{transaction_id}.staging"
    repair_final = repair_root / transaction_id
    completion_staging = completion_path.with_name(
        f".{completion_path.name}.sample-id-v2.{transaction_id}.staging"
    )
    completion_backup = completion_path.with_name(
        f"{completion_path.name}.pre-sample-id-v2.{transaction_id}"
    )
    for path in (
        staging_dir,
        backup_dir,
        repair_staging,
        repair_final,
        completion_staging,
        completion_backup,
    ):
        if path.exists():
            raise FileExistsError(f"transaction target already exists: {path}")

    diagnosis = load_json(diagnosis_path)
    duplicate_ids = collect_duplicate_ids(scratch)
    duplicate_keys = len(duplicate_ids)
    duplicate_rows_after_first = sum(count - 1 for count in duplicate_ids.values())
    if duplicate_keys != int(diagnosis["duplicate_keys"]):
        raise ValueError("duplicate key count disagrees with diagnosis")
    if duplicate_rows_after_first != int(diagnosis["duplicate_rows_after_first"]):
        raise ValueError("duplicate row count disagrees with diagnosis")

    manifest_entries = manifest.get("class_csvs")
    if not isinstance(manifest_entries, list) or not manifest_entries:
        raise ValueError("manifest class_csvs missing")
    completion_matches = [
        (index, item)
        for index, item in enumerate(completion.get("datasets", []))
        if item.get("dataset_id") == expected_dataset_id
    ]
    if len(completion_matches) != 1 or completion_matches[0][1] != manifest:
        raise ValueError("completion dataset record is not the exact source manifest")

    applied_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    observed: dict[bytes, int] = {}
    generated_ids: set[bytes] = set()
    class_results: list[dict[str, Any]] = []
    verification_results: list[dict[str, Any]] = []
    repair_staging.mkdir(parents=True)
    staging_dir.mkdir(parents=True)
    mapping_path = repair_staging / "sample_id_mapping.jsonl"

    try:
        with mapping_path.open("wb") as mapping:
            for entry in manifest_entries:
                source = Path(entry["path"]).resolve()
                if source.parent != dataset_dir or source.name == "dataset.manifest.json":
                    raise ValueError(f"class CSV escapes dataset directory: {source}")
                target = staging_dir / source.name
                result = rewrite_class_csv(
                    source,
                    target,
                    entry,
                    duplicate_ids,
                    observed,
                    generated_ids,
                    mapping,
                )
                class_results.append(result)
            mapping.flush()
            os.fsync(mapping.fileno())

        missing = {
            sample_id.hex(): {"expected": count, "observed": observed.get(sample_id, 0)}
            for sample_id, count in duplicate_ids.items()
            if observed.get(sample_id, 0) != count
        }
        if missing:
            raise ValueError(f"duplicate sample_id occurrence mismatch: {len(missing)} keys")

        expected_rewritten_rows = sum(duplicate_ids.values())
        actual_rewritten_rows = sum(item["rewritten_rows"] for item in class_results)
        if actual_rewritten_rows != expected_rewritten_rows:
            raise ValueError("rewritten row total mismatch")

        for entry, result in zip(manifest_entries, class_results):
            verification = verify_class_csv_pair(
                Path(entry["path"]), staging_dir / Path(entry["path"]).name, duplicate_ids
            )
            if verification["changed_rows"] != result["rewritten_rows"]:
                raise ValueError("independent changed-row count mismatch")
            if (
                verification["normalized_sample_id_zeroed_sha256"]
                != result["normalized_sample_id_zeroed_sha256"]
            ):
                raise ValueError("independent non-sample_id digest mismatch")
            verification_results.append(verification)

        mapping_sha256 = sha256_file(mapping_path)
        final_mapping_path = repair_final / mapping_path.name
        identity_repair = {
            "applied_at_utc": applied_at,
            "duplicate_keys": duplicate_keys,
            "duplicate_rows_after_first": duplicate_rows_after_first,
            "feature_columns_modified": False,
            "label_columns_modified": False,
            "mapping_path": str(final_mapping_path),
            "mapping_sha256": mapping_sha256,
            "modified_columns": ["sample_id"],
            "new_id_contract": (
                "SHA-256(UTF8('caeos_sample_id_v2\\0') || old_sample_id_raw32 || "
                "model_content_sha256_raw32 || uint64_be(occurrence_ordinal))"
            ),
            "old_manifest_sha256": old_manifest_sha256,
            "repair_rule": REPAIR_RULE,
            "rewritten_rows": actual_rewritten_rows,
            "rows_deleted": 0,
            "schema_version": REPAIR_SCHEMA,
            "source_audit_path": str(source_audit_path),
            "source_audit_sha256": sha256_file(source_audit_path),
            "source_diagnosis_path": str(diagnosis_path),
            "source_diagnosis_sha256": sha256_file(diagnosis_path),
            "transaction_id": transaction_id,
        }

        new_manifest = dict(manifest)
        new_entries: list[dict[str, Any]] = []
        for entry, result in zip(manifest_entries, class_results):
            updated = dict(entry)
            updated["sha256"] = result["new_sha256"]
            updated["size_bytes"] = result["size_bytes"]
            new_entries.append(updated)
        new_manifest["class_csvs"] = new_entries
        new_manifest["identity_repair"] = identity_repair
        new_manifest.pop("manifest_sha256", None)
        new_manifest["manifest_sha256"] = canonical_json_hash(new_manifest)
        atomic_json(staging_dir / "dataset.manifest.json", new_manifest)

        completion_index = completion_matches[0][0]
        new_completion = dict(completion)
        new_datasets = list(completion["datasets"])
        new_datasets[completion_index] = new_manifest
        new_completion["datasets"] = new_datasets
        new_completion.pop("completion_sha256", None)
        new_completion["completion_sha256"] = canonical_json_hash(new_completion)
        atomic_json(completion_staging, new_completion)

        report = {
            "applied_at_utc": applied_at,
            "class_files": class_results,
            "dataset_id": expected_dataset_id,
            "duplicate_keys": duplicate_keys,
            "duplicate_rows_after_first": duplicate_rows_after_first,
            "feature_columns_modified": False,
            "independent_byte_preservation_verification": verification_results,
            "label_columns_modified": False,
            "mapping_sha256": mapping_sha256,
            "modified_columns": ["sample_id"],
            "new_completion_sha256": new_completion["completion_sha256"],
            "new_manifest_sha256": new_manifest["manifest_sha256"],
            "old_completion_sha256": old_completion_sha256,
            "old_manifest_sha256": old_manifest_sha256,
            "repair_rule": REPAIR_RULE,
            "rewritten_rows": actual_rewritten_rows,
            "rows_deleted": 0,
            "schema_version": REPAIR_SCHEMA,
            "transaction_id": transaction_id,
        }
        atomic_json(repair_staging / "repair_report.json", report)

        repair_root.mkdir(parents=True, exist_ok=True)
        os.replace(repair_staging, repair_final)
        dataset_swapped = False
        completion_swapped = False
        try:
            os.replace(dataset_dir, backup_dir)
            os.replace(staging_dir, dataset_dir)
            dataset_swapped = True
            os.replace(completion_path, completion_backup)
            os.replace(completion_staging, completion_path)
            completion_swapped = True
        except BaseException:
            if completion_swapped:
                os.replace(completion_path, completion_staging)
            if completion_backup.exists():
                os.replace(completion_backup, completion_path)
            if dataset_swapped:
                os.replace(dataset_dir, staging_dir)
            if backup_dir.exists():
                os.replace(backup_dir, dataset_dir)
            raise

        receipt = {
            "backup_completion_path": str(completion_backup),
            "backup_dataset_path": str(backup_dir),
            "completion_path": str(completion_path),
            "dataset_id": expected_dataset_id,
            "dataset_manifest_path": str(dataset_manifest_path),
            "new_completion_sha256": new_completion["completion_sha256"],
            "new_manifest_sha256": new_manifest["manifest_sha256"],
            "repair_report_sha256": sha256_file(repair_final / "repair_report.json"),
            "schema_version": REPAIR_SCHEMA,
            "status": "applied",
            "transaction_id": transaction_id,
        }
        atomic_json(repair_final / "application_receipt.json", receipt)
        return receipt
    except BaseException:
        if staging_dir.exists():
            shutil.rmtree(staging_dir)
        if completion_staging.exists():
            completion_staging.unlink()
        if repair_staging.exists():
            shutil.rmtree(repair_staging)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Repair only sample_id collisions proven by a retained full audit."
    )
    parser.add_argument("--dataset-manifest", required=True, type=Path)
    parser.add_argument("--completion", required=True, type=Path)
    parser.add_argument("--scratch", required=True, type=Path)
    parser.add_argument("--diagnosis", required=True, type=Path)
    parser.add_argument("--source-audit", required=True, type=Path)
    parser.add_argument("--repair-root", required=True, type=Path)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--transaction-id", required=True)
    args = parser.parse_args()
    receipt = repair_dataset(
        args.dataset_manifest,
        args.completion,
        args.scratch,
        args.diagnosis,
        args.source_audit,
        args.repair_root,
        args.dataset_id,
        args.transaction_id,
    )
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
