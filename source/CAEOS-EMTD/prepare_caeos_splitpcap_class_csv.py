from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import json
import math
import os
import shutil
import sqlite3
import subprocess
import tarfile
import time
import zipfile
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from caeos_unified_dataset import atomic_json, canonical_json_hash, sha256_file


PREPROCESSOR_MODULES = {
    "current": "prepare_caeos_unified_multimodal_csv",
    "frozen_7caf": "prepare_caeos_unified_multimodal_csv_frozen_7caf",
    "frozen_87f": "prepare_caeos_unified_multimodal_csv_legacy_cicddos",
    "frozen_87f_tcp_ns_fix": "prepare_caeos_unified_multimodal_csv_frozen_87f_tcp_ns",
}
TCP_NS_FLAG_COMPATIBLE_PREPROCESSOR_MIGRATION = {
    "87f3701cf7f161e358e2d981e9667762140f4b9f3c95892a8b62a6f1d62e9306":
        "b4c010c78fa768d16b348703216802dbaadfe042e9ccf459b1767d228018e9b9",
}
PREPROCESSOR_VARIANT = os.environ.get("CAEOS_PREPROCESSOR_VARIANT", "current")
if PREPROCESSOR_VARIANT not in PREPROCESSOR_MODULES:
    raise ValueError(f"unsupported CAEOS preprocessor variant: {PREPROCESSOR_VARIANT}")
PREPROCESSOR_MODULE_NAME = PREPROCESSOR_MODULES[PREPROCESSOR_VARIANT]
PREPROCESSOR_SOURCE_PATH = Path(__file__).with_name(
    f"{PREPROCESSOR_MODULE_NAME}.py"
)
_preprocessor = importlib.import_module(PREPROCESSOR_MODULE_NAME)
ATTACK_CATEGORIES = _preprocessor.ATTACK_CATEGORIES
SCHEMA_VERSION = _preprocessor.SCHEMA_VERSION
build_processing_policy = _preprocessor.build_processing_policy
load_json = _preprocessor.load_json
process_capture = _preprocessor.process_capture
tshark_identity = _preprocessor.tshark_identity
validate_source_manifest = _preprocessor.validate_source_manifest
verify_csv = _preprocessor.verify_csv
_verify_csv_and_sha256 = getattr(_preprocessor, "verify_csv_and_sha256", None)
_verify_csv_and_sha256_parallel = getattr(
    _preprocessor, "verify_csv_and_sha256_parallel", None
)


def verify_csv_and_sha256(
    path: Path,
    columns: list[str],
    expected_rows: int,
    require_formal_labels: bool = False,
) -> tuple[dict[str, Any], str]:
    if _verify_csv_and_sha256 is not None:
        return _verify_csv_and_sha256(
            path,
            columns,
            expected_rows,
            require_formal_labels=require_formal_labels,
        )
    return (
        verify_csv(
            path,
            columns,
            expected_rows,
            require_formal_labels=require_formal_labels,
        ),
        sha256_file(path),
    )


def verify_csv_and_sha256_parallel(
    path: Path,
    columns: list[str],
    expected_rows: int,
    require_formal_labels: bool = False,
    workers: int = 1,
    batch_rows: int = 2048,
) -> tuple[dict[str, Any], str]:
    if workers > 1 and _verify_csv_and_sha256_parallel is not None:
        return _verify_csv_and_sha256_parallel(
            path,
            columns,
            expected_rows,
            require_formal_labels=require_formal_labels,
            workers=workers,
            batch_rows=batch_rows,
        )
    return verify_csv_and_sha256(
        path,
        columns,
        expected_rows,
        require_formal_labels=require_formal_labels,
    )

DOH_APPROVED_UNMATCHED_REASONS = frozenset(
    {
        "five_tuple_absent_from_official_flow_labels",
        "five_tuple_present_but_time_not_overlapping",
        "protocol_outside_official_tcp_udp_flow_labels",
    }
)

BOT_IOT_APPROVED_UNMATCHED_REASONS = frozenset(
    {
        "five_tuple_absent_from_official_flow_labels",
        "five_tuple_present_but_time_not_overlapping",
        "protocol_outside_official_tcp_udp_flow_labels",
    }
)


UNRAR_BINARY = Path(
    os.environ.get(
        "CAEOS_UNRAR_BINARY",
        "/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/tools/"
        "unrar-rar5-r20/bin/unrar",
    )
)
from scripts.validate_splitpcap_integrity import validate as validate_split
from scripts.repair_truncated_final_pcap_record import (
    inspect_truncated_final_record,
    repair_final_record,
    sha256_prefix,
)
from scripts.validate_splitpcap_integrity import capture_fingerprint


def bounded_workers(
    cpu_cap: int,
    piece_count: int,
    memory_budget_gib: float,
    memory_reserve_gib: float,
    estimated_worker_gib: float,
    safety_factor: float,
) -> int:
    usable = memory_budget_gib - memory_reserve_gib
    if usable <= 0:
        raise ValueError("memory reserve must be smaller than memory budget")
    if estimated_worker_gib <= 0 or safety_factor < 1:
        raise ValueError("invalid worker memory estimate or safety factor")
    memory_cap = max(1, math.floor(usable / (estimated_worker_gib * safety_factor)))
    return max(1, min(cpu_cap, piece_count, memory_cap))


def capture_identity(source_path: str, member: str | None) -> str:
    return hashlib.sha256(f"{source_path}::{member or ''}".encode("utf-8")).hexdigest()


def source_member_name(dataset: dict[str, Any], source: dict[str, Any], member: str | None) -> str:
    if member is not None:
        return member
    return Path(source["path"]).relative_to(Path(dataset["source_root"])).as_posix()


def capture_member_allowlist(
    alignment: dict[str, Any], dataset_id: str
) -> set[str] | None:
    gate_types = set(alignment.get("admission_gate_types", []))
    if "full_capture_member_inventory" not in gate_types:
        return None
    path = Path(alignment["path"])
    uri = f"file:{path.resolve().as_posix()}?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    try:
        metadata = dict(connection.execute("SELECT key, value FROM metadata"))
        if metadata.get("dataset_id") != dataset_id:
            raise ValueError(f"capture-member index dataset mismatch: {dataset_id}")
        rows = connection.execute(
            "SELECT source_member FROM labels WHERE endpoint_a IS NULL "
            "ORDER BY source_member"
        ).fetchall()
    finally:
        connection.close()
    allowlist = {str(row[0]) for row in rows}
    if len(allowlist) != int(alignment["record_count"]):
        raise ValueError(f"capture-member allowlist cardinality mismatch: {dataset_id}")
    return allowlist


def source_capture_bytes(source: dict[str, Any], member_record: Any) -> int:
    if isinstance(member_record, dict):
        return int(member_record.get("size_bytes", 0))
    return int(source.get("size_bytes", 0))


def select_capture_candidates(
    dataset: dict[str, Any],
    source_dataset: dict[str, Any],
    allowlist: set[str] | None,
) -> tuple[list[tuple[dict[str, Any], str | None]], dict[str, Any]]:
    selected: list[tuple[dict[str, Any], str | None]] = []
    excluded_sources: list[dict[str, Any]] = []
    candidate_count = 0
    candidate_bytes = 0
    for source in source_dataset["source_files"]:
        members = source.get("capture_members") or [None]
        archive_member_names: set[str] | None = None
        archive_path = Path(source["path"])
        if source.get("capture_members") and archive_path.suffix.lower() == ".zip":
            with zipfile.ZipFile(archive_path) as archive:
                archive_member_names = set(archive.namelist())
        for member_record in members:
            member = member_record["name"] if isinstance(member_record, dict) else None
            member_name = source_member_name(dataset, source, member)
            member_bytes = source_capture_bytes(source, member_record)
            candidate_count += 1
            candidate_bytes += member_bytes
            if member is None and Path(source["path"]).suffix.lower() not in {
                ".pcap",
                ".pcapng",
            }:
                excluded_sources.append(
                    {
                        "source_member": member_name,
                        "size_bytes": member_bytes,
                        "reason": "non_capture_source_file",
                        "rule": "schedule_only_direct_pcap_or_pcapng_sources",
                    }
                )
                continue
            if (
                member is not None
                and archive_member_names is not None
                and member not in archive_member_names
            ):
                excluded_sources.append(
                    {
                        "source_member": member_name,
                        "size_bytes": member_bytes,
                        "reason": "archive_member_missing_from_current_source",
                        "rule": "exclude_manifest_member_absent_from_current_zip_inventory",
                        "manifest_source_size_bytes": int(source.get("size_bytes", 0)),
                        "current_source_size_bytes": archive_path.stat().st_size,
                    }
                )
                continue
            if allowlist is not None and member_name not in allowlist:
                excluded_sources.append(
                    {
                        "source_member": member_name,
                        "size_bytes": member_bytes,
                        "reason": "outside_frozen_capture_member_label_inventory",
                        "rule": "schedule_only_members_present_in_formal_capture_label_index",
                    }
                )
                continue
            selected.append((source, member))
    excluded_bytes = sum(item["size_bytes"] for item in excluded_sources)
    scope = {
        "candidate_capture_count": candidate_count,
        "candidate_capture_bytes": candidate_bytes,
        "scheduled_capture_count": len(selected),
        "scheduled_capture_bytes": candidate_bytes - excluded_bytes,
        "excluded_capture_count": len(excluded_sources),
        "excluded_capture_bytes": excluded_bytes,
        "excluded_capture_fraction": (
            len(excluded_sources) / candidate_count if candidate_count else 0.0
        ),
        "excluded_reason_counts": dict(
            Counter(item["reason"] for item in excluded_sources)
        ),
        "excluded_sources": excluded_sources,
        "excluded_sources_sha256": canonical_json_hash(excluded_sources),
    }
    return selected, scope


def inspect_archive_member_for_runtime_repair(
    dataset_id: str, source: Path
) -> dict[str, int | str] | None:
    try:
        return inspect_truncated_final_record(source)
    except ValueError as error:
        if dataset_id != "cicids2018":
            raise
        return {
            "repair_kind": "pcapfix_deep_scan_required",
            "inspection_error": str(error),
        }


@contextmanager
def materialized_capture(
    source: dict[str, Any], member: str | None, staging_root: Path, capture_id: str
) -> Iterator[Path]:
    if member is None:
        yield Path(source["path"])
        return
    staging_root.mkdir(parents=True, exist_ok=True)
    target = staging_root / f"{capture_id}.capture"
    temporary = target.with_suffix(".partial")
    archive_path = Path(source["path"])
    try:
        if zipfile.is_zipfile(archive_path):
            with zipfile.ZipFile(archive_path) as archive, archive.open(member) as src:
                with temporary.open("wb") as dst:
                    shutil.copyfileobj(src, dst, length=16 * 1024 * 1024)
                    dst.flush()
                    os.fsync(dst.fileno())
        elif archive_path.name.lower().endswith(".rar"):
            if not UNRAR_BINARY.is_file():
                raise FileNotFoundError(f"RAR5 decoder unavailable: {UNRAR_BINARY}")
            with temporary.open("wb") as dst:
                result = subprocess.run(
                    [str(UNRAR_BINARY), "p", "-inul", str(archive_path), member],
                    check=False,
                    stdout=dst,
                    stderr=subprocess.PIPE,
                )
                dst.flush()
                os.fsync(dst.fileno())
            if result.returncode != 0:
                detail = result.stderr.decode("utf-8", errors="replace").strip()
                raise ValueError(f"cannot extract RAR capture member: {detail[-2000:]}")
        elif tarfile.is_tarfile(archive_path):
            with tarfile.open(archive_path, "r:*") as archive:
                src = archive.extractfile(member)
                if src is None:
                    raise ValueError(f"archive member cannot be extracted: {member}")
                with src, temporary.open("wb") as dst:
                    shutil.copyfileobj(src, dst, length=16 * 1024 * 1024)
                    dst.flush()
                    os.fsync(dst.fileno())
        else:
            raise ValueError(f"unsupported capture archive: {archive_path}")
        os.replace(temporary, target)
        yield target
    finally:
        temporary.unlink(missing_ok=True)
        target.unlink(missing_ok=True)


def split_capture(
    splitpcap_binary: Path,
    editcap_binary: Path,
    source_path: Path,
    split_root: Path,
    target_piece_bytes: int,
    maximum_pieces: int,
    minimum_pieces: int = 2,
) -> tuple[list[Path], dict[str, Any]]:
    requested_pieces = min(
        maximum_pieces,
        max(
            minimum_pieces,
            math.ceil(source_path.stat().st_size / target_piece_bytes),
        ),
    )
    split_root.mkdir(parents=True, exist_ok=False)
    started = time.time()
    result = subprocess.run(
        [str(splitpcap_binary), str(source_path), str(split_root), str(requested_pieces)],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    split_tool = "splitpcap"
    detail = (result.stderr or result.stdout).strip()
    fallback_reason: str | None = None

    def editcap_packet_count_split(reason: str, tool_name: str) -> list[Path]:
        shutil.rmtree(split_root)
        split_root.mkdir(parents=True, exist_ok=False)
        packet_info = subprocess.run(
            ["/usr/bin/capinfos", "-c", "-M", str(source_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        packet_line = next(
            line
            for line in packet_info.stdout.splitlines()
            if line.startswith("Number of packets:")
        )
        packet_count = int(packet_line.rsplit(maxsplit=1)[-1])
        packets_per_piece = max(1, math.ceil(packet_count / requested_pieces))
        editcap = subprocess.run(
            [
                str(editcap_binary),
                "-c",
                str(packets_per_piece),
                str(source_path),
                str(split_root / "piece.pcapng"),
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if editcap.returncode != 0:
            editcap_detail = (editcap.stderr or editcap.stdout).strip()
            raise RuntimeError(
                f"editcap PCAPNG split failed ({editcap.returncode}): "
                f"{editcap_detail[-2000:]}"
            )
        nonempty = sorted(
            path
            for path in split_root.iterdir()
            if path.is_file() and path.stat().st_size > 24
        )
        if not nonempty:
            raise ValueError("editcap produced no non-empty pieces")
        return nonempty

    if result.returncode != 0:
        mixed_linktype = "different from the type of the first interface" in detail
        if not mixed_linktype:
            raise RuntimeError(
                f"splitpcap failed ({result.returncode}): {detail[-2000:]}"
            )
        fallback_reason = detail
        split_tool = "editcap_packet_count_mixed_linktype_pcapng"
        pieces = editcap_packet_count_split(fallback_reason, split_tool)
    else:
        pieces = sorted(
            path
            for path in split_root.iterdir()
            if path.is_file() and path.stat().st_size > 24
        )
    try:
        integrity = validate_split(source_path, pieces)
    except ValueError as error:
        if split_tool != "splitpcap" or "packet integrity mismatch" not in str(error):
            raise
        fallback_reason = str(error)
        split_tool = "editcap_packet_count_after_splitpcap_integrity_mismatch"
        pieces = editcap_packet_count_split(fallback_reason, split_tool)
        integrity = validate_split(source_path, pieces)
    integrity.update(
        {
            "requested_piece_count": requested_pieces,
            "nonempty_piece_count": len(pieces),
            "split_seconds": time.time() - started,
            "minimum_pieces": minimum_pieces,
            "maximum_pieces": maximum_pieces,
            "split_tool": split_tool,
            "splitpcap_fallback_reason": fallback_reason,
        }
    )
    return pieces, integrity


def processing_policy(
    reservoir: dict[str, Any],
    maximum_active_flows: int,
    packet_decoder: str,
    packet_decoder_identity: str,
    tshark_session_reset_packets: int,
    preprocessor_code_sha256: str,
    splitpcap_binary: Path,
    splitpcap_commit: str,
    target_piece_bytes: int,
    minimum_pieces_per_capture: int,
    maximum_pieces_per_capture: int,
) -> dict[str, Any]:
    policy = build_processing_policy(
        idle_seconds=float(reservoir["flow_idle_timeout_seconds"]),
        maximum_packets=int(reservoir["maximum_packets"]),
        payload_prefix_bytes=int(reservoir["payload_prefix_bytes"]),
        sanitized_l4_prefix_bytes=int(reservoir.get("sanitized_l4_prefix_bytes", 2048)),
        maximum_active_flows=maximum_active_flows,
        packet_decoder=packet_decoder,
        packet_decoder_identity=packet_decoder_identity,
        tshark_session_reset_packets=tshark_session_reset_packets,
        preprocessor_code_sha256=preprocessor_code_sha256,
    )
    policy["capture_scheduling"] = {
        "dataset_concurrency": 1,
        "original_capture_concurrency": 1,
        "piece_parallelism_only": True,
        "delete_split_pcap_after_capture": True,
    }
    policy["splitpcap"] = {
        "commit": splitpcap_commit,
        "binary": str(splitpcap_binary),
        "binary_sha256": sha256_file(splitpcap_binary),
        "target_piece_bytes": target_piece_bytes,
        "minimum_pieces_per_capture": minimum_pieces_per_capture,
        "maximum_pieces_per_capture": maximum_pieces_per_capture,
        "exact_packet_multiset_validation": True,
    }
    return policy


def task_for_piece(
    dataset: dict[str, Any],
    source: dict[str, Any],
    source_member: str,
    capture_id: str,
    piece: Path,
    piece_index: int,
    output_root: Path,
    schema: dict[str, Any],
    reservoir: dict[str, Any],
    maximum_active_flows: int,
    packet_decoder: str,
    tshark_binary: str,
    packet_decoder_identity: str,
    tshark_session_reset_packets: int,
    policy: dict[str, Any],
) -> dict[str, Any]:
    part_path = output_root / "_parts" / dataset["id"] / capture_id / f"piece-{piece_index:05d}.part"
    task = {
        "dataset": dataset,
        "path": str(piece),
        "member": None,
        "source_member_override": source_member,
        "original_source_path": source["path"],
        "capture_id": capture_id,
        "source_sha256": source["sha256"],
        "piece_index": piece_index,
        "part_path": str(part_path),
        "schema_sha256": canonical_json_hash(schema),
        "columns": [item["name"] for item in schema["columns"]],
        "idle_seconds": reservoir["flow_idle_timeout_seconds"],
        "maximum_packets": reservoir["maximum_packets"],
        "payload_prefix_bytes": reservoir["payload_prefix_bytes"],
        "sanitized_l4_prefix_bytes": reservoir.get("sanitized_l4_prefix_bytes", 2048),
        "maximum_active_flows": maximum_active_flows,
        "packet_decoder": packet_decoder,
        "tshark_binary": tshark_binary,
        "packet_decoder_identity": packet_decoder_identity,
        "tshark_session_reset_packets": tshark_session_reset_packets,
        "processing_policy": policy,
        "processing_policy_sha256": canonical_json_hash(policy),
    }
    if "label_alignment" in policy:
        task["label_alignment"] = policy["label_alignment"]
    return task


def verify_reusable_capture(
    marker: dict[str, Any], schema_sha256: str, policy_sha256: str
) -> list[dict[str, Any]]:
    parts = marker.get("parts", [])
    if not marker.get("complete") or not parts:
        raise ValueError("invalid capture completion marker")
    for part in parts:
        if part.get("schema_sha256") != schema_sha256:
            raise ValueError("stale capture marker schema")
        if part.get("processing_policy_sha256") != policy_sha256:
            raise ValueError("stale capture marker processing policy")
        path = Path(part["part_path"])
        if not path.is_file() or sha256_file(path) != part["part_sha256"]:
            raise ValueError(f"capture marker part identity mismatch: {path}")
    return parts


def policy_changed_paths(left: Any, right: Any, prefix: str = "") -> set[str]:
    if isinstance(left, dict) and isinstance(right, dict):
        paths: set[str] = set()
        for key in sorted(set(left) | set(right)):
            path = f"{prefix}.{key}" if prefix else key
            if key not in left or key not in right:
                paths.add(path)
            else:
                paths.update(policy_changed_paths(left[key], right[key], path))
        return paths
    if isinstance(left, list) and isinstance(right, list):
        return set() if left == right else {prefix}
    return set() if left == right else {prefix}


def migrate_capture_marker_registry_rollup(
    marker_path: Path,
    marker: dict[str, Any],
    schema_sha256: str,
    expected_policy: dict[str, Any],
    current_repair: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Migrate content-neutral policy metadata after verifying all part identities."""
    parts = marker.get("parts", [])
    if not marker.get("complete") or not parts:
        raise ValueError("invalid capture completion marker")
    previous_hashes: set[str] = set()
    previous_policies: dict[str, dict[str, Any]] = {}
    for part in parts:
        path = Path(part["part_path"])
        if not path.is_file() or sha256_file(path) != part["part_sha256"]:
            raise ValueError(f"capture marker part identity mismatch: {path}")
        if part.get("schema_sha256") != schema_sha256:
            raise ValueError("stale capture marker schema")
        previous_hash = str(part.get("processing_policy_sha256", ""))
        previous_policy = part.get("processing_policy")
        if not isinstance(previous_policy, dict):
            raise ValueError("capture marker lacks embedded processing policy")
        if canonical_json_hash(previous_policy) != previous_hash:
            raise ValueError("capture marker embedded policy identity mismatch")
        previous_hashes.add(previous_hash)
        previous_policies[previous_hash] = previous_policy
    if len(previous_hashes) != 1:
        raise ValueError("capture marker contains mixed processing policies")
    previous_hash = next(iter(previous_hashes))
    previous_policy = previous_policies[previous_hash]
    previous_alignment = previous_policy.get("label_alignment")
    expected_alignment = expected_policy.get("label_alignment")
    if not isinstance(previous_alignment, dict) or not isinstance(
        expected_alignment, dict
    ):
        raise ValueError("processing policy lacks label alignment identity")
    previous_registry = previous_alignment.get("registry_sha256")
    expected_registry = expected_alignment.get("registry_sha256")
    changed = sorted(policy_changed_paths(previous_policy, expected_policy))
    allowed_changes = {
        "label_alignment.registry_sha256",
        "pcap_repair_manifest_sha256",
        "pcap_repair_set",
        "pcap_repair_set.repair_count",
        "pcap_repair_set.repairs_sha256",
        "splitpcap.target_piece_bytes",
    }
    repair_rollup_changes = {
        path
        for path in changed
        if path == "pcap_repair_manifest_sha256"
        or path == "pcap_repair_set"
        or path.startswith("pcap_repair_set.")
    }
    tcp_ns_flag_migration = (
        changed == ["preprocessor_code_sha256"]
        and TCP_NS_FLAG_COMPATIBLE_PREPROCESSOR_MIGRATION.get(
            str(previous_policy.get("preprocessor_code_sha256", ""))
        )
        == str(expected_policy.get("preprocessor_code_sha256", ""))
    )
    content_neutral_migration = (
        bool(changed)
        and set(changed).issubset(allowed_changes)
        and not (
            repair_rollup_changes
            and (current_repair is not None or marker.get("pcap_repair") is not None)
        )
    )
    if (
        not content_neutral_migration
        and not tcp_ns_flag_migration
    ):
        raise ValueError(
            "stale capture marker processing policy; changed_paths="
            + json.dumps(changed, separators=(",", ":"))
        )
    expected_hash = canonical_json_hash(expected_policy)
    for part in parts:
        part["processing_policy"] = json.loads(json.dumps(expected_policy))
        part["processing_policy_sha256"] = expected_hash
        if isinstance(part.get("label_alignment"), dict):
            part["label_alignment"]["registry_sha256"] = expected_registry
    migrations = marker.setdefault("policy_migrations", [])
    migration = {
        "schema_version": "caeos_capture_policy_metadata_migration_v1",
        "reason": (
            "completed_capture_tcp_ns_flag_compatibility_fix"
            if tcp_ns_flag_migration
            else "content_neutral_processing_policy_metadata_change"
        ),
        "previous_processing_policy_sha256": previous_hash,
        "processing_policy_sha256": expected_hash,
        "previous_registry_sha256": previous_registry,
        "registry_sha256": expected_registry,
        "label_index_sha256": expected_alignment["sha256"],
        "changed_paths": changed,
        "previous_pcap_repair_set": previous_policy.get("pcap_repair_set"),
        "pcap_repair_set": expected_policy.get("pcap_repair_set"),
        "verified_part_count": len(parts),
        "part_content_sha256_unchanged": True,
    }
    if tcp_ns_flag_migration:
        migration["compatibility_proof"] = (
            "the old serializer completed this capture, so no TCP packet supplied "
            "flags above 255; the patched serializer is byte-identical for all "
            "flags in the completed input domain"
        )
    if migration not in migrations:
        migrations.append(migration)
    marker.pop("marker_sha256", None)
    marker["marker_sha256"] = canonical_json_hash(marker)
    atomic_json(marker_path, marker)
    return marker


def load_pcap_repairs(path: Path) -> tuple[dict[str, dict[str, Any]], str]:
    manifest = load_json(path)
    repairs: dict[str, dict[str, Any]] = {}
    for entry in manifest.get("repairs", []):
        repaired_path = Path(entry["repaired_path"])
        if not repaired_path.is_file():
            raise FileNotFoundError(repaired_path)
        if sha256_file(repaired_path) != entry["repaired_sha256"]:
            raise ValueError(f"repaired PCAP identity mismatch: {repaired_path}")
        key = capture_identity(entry["source_path"], entry.get("source_member"))
        if key in repairs:
            raise ValueError(f"duplicate PCAP repair entry: {key}")
        repairs[key] = entry
    return repairs, sha256_file(path)


def dataset_pcap_repair_policy(
    repairs: dict[str, dict[str, Any]], dataset_id: str
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    dataset_repairs = {
        key: entry
        for key, entry in repairs.items()
        if entry.get("dataset_id") == dataset_id
    }
    ordered_entries = [dataset_repairs[key] for key in sorted(dataset_repairs)]
    policy = {
        "schema_version": "caeos_dataset_pcap_repair_set_v1",
        "dataset_id": dataset_id,
        "repair_count": len(ordered_entries),
        "repairs_sha256": canonical_json_hash(ordered_entries),
    }
    return policy, dataset_repairs


def aggregate_label_exclusion(items: list[dict[str, Any]]) -> dict[str, Any]:
    total = 0
    excluded = 0
    packets = 0
    packet_bytes = 0
    total_packets = 0
    total_packet_bytes = 0
    reasons: Counter[str] = Counter()
    approved_reasons: set[str] = set()
    for item in items:
        summary = item.get("label_exclusion_summary", {})
        total += int(summary.get("total_finalized_flows", 0))
        excluded += int(summary.get("excluded_flows", 0))
        packets += int(summary.get("excluded_packets", 0))
        packet_bytes += int(summary.get("excluded_packet_bytes", 0))
        total_packets += int(summary.get("total_parsed_packets", 0))
        total_packet_bytes += int(summary.get("total_parsed_packet_bytes", 0))
        reasons.update(
            {key: int(value) for key, value in summary.get("reason_counts", {}).items()}
        )
        approved_reasons.update(summary.get("approved_reasons", []))
    return {
        "rule_version": "caeos_label_exclusion_v1",
        "approved_reasons": sorted(approved_reasons),
        "total_finalized_flows": total,
        "excluded_flows": excluded,
        "excluded_flow_fraction": excluded / total if total else 0.0,
        "excluded_packets": packets,
        "total_parsed_packets": total_packets,
        "excluded_packet_fraction": packets / total_packets if total_packets else 0.0,
        "excluded_packet_bytes": packet_bytes,
        "total_parsed_packet_bytes": total_packet_bytes,
        "excluded_packet_byte_fraction": (
            packet_bytes / total_packet_bytes if total_packet_bytes else 0.0
        ),
        "reason_counts": dict(sorted(reasons.items())),
        "source_pcaps_modified": False,
    }


def process_original_capture(
    dataset: dict[str, Any],
    source: dict[str, Any],
    member: str | None,
    args: argparse.Namespace,
    output_root: Path,
    schema: dict[str, Any],
    reservoir: dict[str, Any],
    policy: dict[str, Any],
    repair: dict[str, Any] | None = None,
) -> dict[str, Any]:
    capture_id = capture_identity(source["path"], member)
    marker_path = output_root / "_captures" / dataset["id"] / f"{capture_id}.json"
    if marker_path.exists():
        marker = load_json(marker_path)
        schema_sha256 = canonical_json_hash(schema)
        policy_sha256 = canonical_json_hash(policy)
        try:
            verify_reusable_capture(marker, schema_sha256, policy_sha256)
        except ValueError as error:
            if str(error) != "stale capture marker processing policy":
                raise
            marker = migrate_capture_marker_registry_rollup(
                marker_path, marker, schema_sha256, policy, repair
            )
        marker["reused"] = True
        return marker
    source_member = source_member_name(dataset, source, member)
    split_root = output_root / "_split_work" / dataset["id"] / capture_id
    staging_root = output_root / "_archive_work" / dataset["id"]
    part_root = output_root / "_parts" / dataset["id"] / capture_id
    runtime_repair_path = staging_root / f"{capture_id}.runtime-repaired.pcap"
    pcapfix_repair_path = staging_root / f"{capture_id}.pcapfix-repaired.pcap"
    started = time.time()
    try:
        with materialized_capture(source, member, staging_root, capture_id) as original_path:
            runtime_repair: dict[str, Any] | None = None
            if repair is None and member is not None:
                truncated = inspect_archive_member_for_runtime_repair(
                    dataset["id"], original_path
                )
                if truncated is not None and truncated.get("repair_kind") != (
                    "pcapfix_deep_scan_required"
                ):
                    repaired_details = repair_final_record(
                        original_path, runtime_repair_path
                    )
                    repaired_fingerprint = capture_fingerprint([runtime_repair_path])
                    if (
                        repaired_details.get("repair_kind")
                        == "drop_incomplete_final_record_header"
                    ):
                        if sha256_prefix(
                            original_path, runtime_repair_path.stat().st_size
                        ) != sha256_file(runtime_repair_path):
                            raise RuntimeError(
                                "runtime repair changed the valid PCAP prefix"
                            )
                        original_fingerprint = repaired_fingerprint
                        fingerprint_validation = (
                            "exact_source_prefix_and_nonpacket_tail_removal"
                        )
                    else:
                        original_fingerprint = capture_fingerprint([original_path])
                        if original_fingerprint != repaired_fingerprint:
                            raise RuntimeError(
                                "runtime final-record repair changed captured packet multiset"
                            )
                        fingerprint_validation = (
                            "original_and_repaired_packet_fingerprint_equal"
                        )
                    runtime_repair = {
                        "dataset_id": dataset["id"],
                        "source_path": source["path"],
                        "source_member": member,
                        "original_sha256": source["sha256"],
                        "materialized_member_sha256": sha256_file(original_path),
                        "materialized_member_size_bytes": original_path.stat().st_size,
                        "repaired_sha256": sha256_file(runtime_repair_path),
                        "repaired_size_bytes": runtime_repair_path.stat().st_size,
                        "repair_tool": "caeos_truncated_final_record_repair_v1",
                        "repair_mode": (
                            "drop_incomplete_final_record_header_without_packet_payload"
                            if repaired_details.get("repair_kind")
                            == "drop_incomplete_final_record_header"
                            else "correct_final_record_incl_len_to_available_bytes"
                        ),
                        "repair_details": repaired_details,
                        "captured_packet_fingerprint": original_fingerprint,
                        "fingerprint_validation": fingerprint_validation,
                        "exact_captured_packet_multiset_preserved": True,
                        "runtime_materialized_repair": True,
                    }
            applied_repair = repair or runtime_repair
            capture_path = (
                Path(repair["repaired_path"])
                if repair
                else runtime_repair_path
                if runtime_repair is not None
                else original_path
            )
            if repair is not None:
                if repair["source_path"] != source["path"]:
                    raise ValueError("PCAP repair source path mismatch")
                if repair.get("source_member") != member:
                    raise ValueError("PCAP repair source member mismatch")
                if repair["original_sha256"] != source["sha256"]:
                    raise ValueError("PCAP repair original identity mismatch")
            if dataset["id"] == "cicids2018":
                preflight = subprocess.run(
                    ["/usr/bin/capinfos", "-c", str(capture_path)],
                    check=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                if preflight.returncode != 0:
                    pcapfix_log = subprocess.run(
                        [
                            "/usr/bin/pcapfix",
                            "-d",
                            "-k",
                            "-o",
                            str(pcapfix_repair_path),
                            str(capture_path),
                        ],
                        check=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                    )
                    if pcapfix_log.returncode != 0 or not pcapfix_repair_path.is_file():
                        raise RuntimeError(
                            "pcapfix deep recovery failed: "
                            f"{pcapfix_log.stdout[-4000:]}"
                        )
                    repaired_preflight = subprocess.run(
                        ["/usr/bin/capinfos", "-c", str(pcapfix_repair_path)],
                        check=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    if repaired_preflight.returncode != 0:
                        raise RuntimeError(
                            "pcapfix output failed capinfos validation: "
                            f"{repaired_preflight.stderr[-2000:]}"
                        )
                    repair_chain = [runtime_repair] if runtime_repair else []
                    pcapfix_output = pcapfix_log.stdout
                    runtime_repair = {
                        "dataset_id": dataset["id"],
                        "source_path": source["path"],
                        "source_member": member,
                        "original_sha256": source["sha256"],
                        "repair_tool": "pcapfix 1.1.7",
                        "repair_mode": "deep_scan_keep_outfile",
                        "repair_trigger": (
                            truncated
                            if truncated is not None
                            else preflight.stderr[-2000:]
                        ),
                        "repair_chain": repair_chain,
                        "pcapfix_log": pcapfix_output,
                        "pcapfix_log_sha256": hashlib.sha256(
                            pcapfix_output.encode("utf-8")
                        ).hexdigest(),
                        "repaired_sha256": sha256_file(pcapfix_repair_path),
                        "repaired_size_bytes": pcapfix_repair_path.stat().st_size,
                        "captured_packet_fingerprint": capture_fingerprint(
                            [pcapfix_repair_path]
                        ),
                        "full_capinfos_scan_passed": True,
                        "recognized_packet_recovery": True,
                        "exact_original_packet_multiset_claimed": False,
                        "source_corruption_caveat": (
                            "invalid source structure prevents an exact original packet "
                            "multiset claim; all records recognized by pcapfix deep scan "
                            "are retained"
                        ),
                        "runtime_materialized_repair": True,
                    }
                    applied_repair = runtime_repair
                    capture_path = pcapfix_repair_path
            if capture_path.stat().st_size > args.split_threshold_bytes:
                pieces, integrity = split_capture(
                    args.splitpcap_binary,
                    args.editcap_binary,
                    capture_path,
                    split_root,
                    args.target_piece_bytes,
                    args.maximum_pieces_per_capture,
                    args.minimum_pieces_per_capture,
                )
            else:
                pieces = [capture_path]
                integrity = {
                    "schema_version": "caeos_splitpcap_integrity_v1",
                    "piece_count": 1,
                    "exact_multiset_match": True,
                    "split_skipped_below_threshold": True,
                }
            workers = bounded_workers(
                args.cpu_worker_cap,
                len(pieces),
                args.memory_budget_gib,
                args.memory_reserve_gib,
                args.estimated_worker_gib,
                args.memory_safety_factor,
            )
            tasks = [
                task_for_piece(
                    dataset,
                    source,
                    source_member,
                    capture_id,
                    piece,
                    index,
                    output_root,
                    schema,
                    reservoir,
                    args.maximum_active_flows,
                    args.packet_decoder,
                    args.tshark_binary,
                    args.packet_decoder_identity,
                    args.tshark_session_reset_packets,
                    policy,
                )
                for index, piece in enumerate(pieces)
            ]
            if workers == 1:
                parts = [process_capture(task) for task in tasks]
            else:
                parts = []
                with ProcessPoolExecutor(max_workers=workers) as executor:
                    futures = [executor.submit(process_capture, task) for task in tasks]
                    for future in as_completed(futures):
                        parts.append(future.result())
            parts.sort(key=lambda item: item["part_path"])
            exclusion_summary = aggregate_label_exclusion(parts)
            marker = {
                "schema_version": "caeos_original_capture_completion_v1",
                "dataset_id": dataset["id"],
                "capture_id": capture_id,
                "source_path": source["path"],
                "source_member": member,
                "source_container_sha256": source["sha256"],
                "source_capture_size_bytes": capture_path.stat().st_size,
                "pcap_repair": applied_repair,
                "workers": workers,
                "integrity": integrity,
                "parts": parts,
                "rows": sum(int(item["counters"].get("rows", 0)) for item in parts),
                "label_exclusion_summary": exclusion_summary,
                "elapsed_seconds": time.time() - started,
                "complete": True,
                "reused": False,
            }
            marker["marker_sha256"] = canonical_json_hash(marker)
            atomic_json(marker_path, marker)
            return marker
    except Exception:
        if part_root.exists():
            shutil.rmtree(part_root)
        marker_path.unlink(missing_ok=True)
        raise
    finally:
        runtime_repair_path.unlink(missing_ok=True)
        pcapfix_repair_path.unlink(missing_ok=True)
        if split_root.exists():
            shutil.rmtree(split_root)


def reuse_dataset(dataset_dir: Path, dataset_id: str) -> dict[str, Any] | None:
    manifest_path = dataset_dir / "dataset.manifest.json"
    if not manifest_path.exists():
        return None
    manifest = load_json(manifest_path)
    if manifest.get("dataset_id") != dataset_id or not manifest.get("complete"):
        raise ValueError(f"invalid dataset completion manifest: {manifest_path}")
    for item in manifest["class_csvs"]:
        path = Path(item["path"])
        if not path.is_file() or sha256_file(path) != item["sha256"]:
            raise ValueError(f"dataset CSV identity mismatch: {path}")
    manifest["reused"] = True
    return manifest


def final_merge_conflict_exclusion_reason(
    dataset_id: str,
    category: str,
    binary_label: int,
    label_status: str,
    label_source: str,
) -> str | None:
    if (
        dataset_id == "unsw_nb15"
        and category == "Pending"
        and binary_label == -1
        and label_status.lower() == "conflicting_label"
        and ";" in label_source
    ):
        return "official_label_conflict"
    return None


def load_doh_source_quality_gate(
    alignment_registration: dict[str, Any],
) -> dict[str, Any]:
    if alignment_registration.get("id") != "dohbrw2020":
        raise ValueError("DoH source-quality gate received another dataset")
    if not alignment_registration.get("admission_gate_passed"):
        raise ValueError("DoH source-quality admission gate is not passed")
    if "source_quality_adjusted_flow_label" not in set(
        alignment_registration.get("admission_gate_types", [])
    ):
        raise ValueError("DoH source-quality admission gate is not registered")
    evidence_items = [
        item
        for item in alignment_registration.get("coverage_evidence", [])
        if item.get("gate_type") == "source_quality_adjusted_flow_label"
    ]
    if len(evidence_items) != 1:
        raise ValueError("DoH requires exactly one source-quality coverage evidence")
    evidence = evidence_items[0]
    if not evidence.get("admission_gate_passed"):
        raise ValueError("DoH source-quality coverage evidence is not passed")
    evidence_path = Path(evidence["path"])
    evidence_sha256 = str(evidence["sha256"])
    if not evidence_path.is_file() or sha256_file(evidence_path) != evidence_sha256:
        raise ValueError("DoH source-quality coverage evidence identity mismatch")
    audit = load_json(evidence_path)
    if audit.get("dataset_id") != "dohbrw2020":
        raise ValueError("DoH source-quality audit dataset mismatch")
    if not audit.get("source_quality_adjusted_gate_passed"):
        raise ValueError("DoH source-quality adjusted gate is not passed")
    if not audit.get("all_sources_usable_or_quarantined"):
        raise ValueError("DoH source inventory is not fully resolved")
    if not audit.get("all_unmatched_flows_have_approved_exclusion_reason"):
        raise ValueError("DoH has unmatched flows without an approved reason")
    if audit.get("source_quality_unresolved"):
        raise ValueError("DoH source-quality audit contains unresolved sources")
    if audit.get("source_quality_pending_allowlist_sources"):
        raise ValueError("DoH source-quality audit contains pending allowlist sources")
    approved_reasons = frozenset(audit.get("approved_exclusion_reasons", []))
    if approved_reasons != DOH_APPROVED_UNMATCHED_REASONS:
        raise ValueError("DoH approved unmatched reason set differs from frozen policy")
    source_count = int(audit.get("source_count", -1))
    processed_source_count = int(audit.get("processed_source_count", -1))
    if source_count <= 0 or processed_source_count != source_count:
        raise ValueError("DoH source-quality audit does not cover the full inventory")
    if audit.get("label_index_sha256") != alignment_registration.get("sha256"):
        raise ValueError("DoH source-quality audit label-index identity mismatch")
    if float(audit.get("effective_coverage_fraction", 0.0)) != 1.0:
        raise ValueError("DoH effective source-quality coverage is not complete")
    if evidence.get("source_quality_policy_sha256") != audit.get(
        "source_quality_policy_sha256"
    ):
        raise ValueError("DoH source-quality policy identity mismatch")
    return {
        "audit_path": str(evidence_path),
        "audit_sha256": evidence_sha256,
        "source_quality_policy_sha256": audit["source_quality_policy_sha256"],
        "approved_unmatched_reasons": sorted(approved_reasons),
        "source_count": source_count,
        "processed_source_count": processed_source_count,
        "raw_coverage_fraction": float(audit["raw_coverage_fraction"]),
        "effective_coverage_fraction": float(audit["effective_coverage_fraction"]),
        "audited_unmatched_flows": int(audit["unmatched_flows"]),
        "audited_policy_excluded_unmatched_flows": int(
            audit["policy_excluded_unmatched_flows"]
        ),
        "audited_policy_excluded_matched_flows": int(
            audit["policy_excluded_matched_flows"]
        ),
        "official_label_index_sha256": str(alignment_registration["sha256"]),
    }


def load_bot_iot_strict_label_gate(
    alignment_registration: dict[str, Any],
) -> dict[str, Any]:
    if alignment_registration.get("id") != "cic_bot_iot":
        raise ValueError("BoT-IoT strict label gate received another dataset")
    if not alignment_registration.get("admission_gate_passed"):
        raise ValueError("BoT-IoT label admission gate is not passed")
    if not alignment_registration.get("formal_gate_passed"):
        raise ValueError("BoT-IoT formal label gate is not passed")
    if "strict_flow_label" not in set(
        alignment_registration.get("admission_gate_types", [])
    ):
        raise ValueError("BoT-IoT strict flow-label gate is not registered")
    evidence_items = [
        item
        for item in alignment_registration.get("coverage_evidence", [])
        if item.get("gate_type") == "strict_flow_label"
    ]
    if len(evidence_items) != 1:
        raise ValueError("BoT-IoT requires exactly one strict label coverage evidence")
    evidence = evidence_items[0]
    if not evidence.get("admission_gate_passed") or not evidence.get(
        "formal_gate_passed"
    ):
        raise ValueError("BoT-IoT strict label coverage evidence is not passed")
    evidence_path = Path(evidence["path"])
    evidence_sha256 = str(evidence["sha256"])
    if not evidence_path.is_file() or sha256_file(evidence_path) != evidence_sha256:
        raise ValueError("BoT-IoT strict label coverage evidence identity mismatch")
    audit = load_json(evidence_path)
    if audit.get("dataset_id") != "cic_bot_iot":
        raise ValueError("BoT-IoT strict label audit dataset mismatch")
    if not audit.get("formal_label_gate_passed"):
        raise ValueError("BoT-IoT strict formal label gate is not passed")
    if not audit.get("all_pcaps_complete"):
        raise ValueError("BoT-IoT strict audit does not cover all PCAP files")
    if not audit.get("all_unmatched_flows_have_approved_exclusion_reason"):
        raise ValueError("BoT-IoT has unmatched flows without an approved reason")
    approved_reasons = frozenset(audit.get("approved_exclusion_reasons", []))
    if approved_reasons != BOT_IOT_APPROVED_UNMATCHED_REASONS:
        raise ValueError("BoT-IoT approved unmatched reason set differs from frozen policy")
    pcap_count = int(audit.get("pcap_file_count", -1))
    processed_pcap_count = int(audit.get("processed_pcap_file_count", -1))
    if pcap_count <= 0 or processed_pcap_count != pcap_count:
        raise ValueError("BoT-IoT strict audit does not cover the full PCAP inventory")
    conflicting_flows = int(audit.get("conflicting_flows", -1))
    unmatched_flows = int(audit.get("unmatched_flows", -1))
    excluded_flows = int(audit.get("excluded_flows", -1))
    if conflicting_flows != 0 or unmatched_flows != excluded_flows:
        raise ValueError("BoT-IoT strict audit contains unresolved retained flows")
    if audit.get("label_index_sha256") != alignment_registration.get("sha256"):
        raise ValueError("BoT-IoT strict audit label-index identity mismatch")
    if float(audit.get("effective_coverage_fraction", 0.0)) != 1.0:
        raise ValueError("BoT-IoT effective strict label coverage is not complete")
    counters = audit.get("counters", {})
    audited_reason_counts = {
        key.removeprefix("policy_exclusion_reason::"): int(value)
        for key, value in counters.items()
        if key.startswith("policy_exclusion_reason::") and int(value) > 0
    }
    if set(audited_reason_counts) - approved_reasons:
        raise ValueError("BoT-IoT strict audit contains an unapproved deletion reason")
    if sum(audited_reason_counts.values()) != excluded_flows:
        raise ValueError("BoT-IoT strict audit deletion reasons do not cover all exclusions")
    return {
        "audit_path": str(evidence_path),
        "audit_sha256": evidence_sha256,
        "approved_unmatched_reasons": sorted(approved_reasons),
        "audited_reason_counts": dict(sorted(audited_reason_counts.items())),
        "pcap_file_count": pcap_count,
        "processed_pcap_file_count": processed_pcap_count,
        "raw_coverage_fraction": float(audit["raw_coverage_fraction"]),
        "effective_coverage_fraction": float(audit["effective_coverage_fraction"]),
        "audited_matched_flows": int(audit["matched_flows"]),
        "audited_unmatched_flows": unmatched_flows,
        "audited_excluded_flows": excluded_flows,
        "official_label_index_sha256": str(alignment_registration["sha256"]),
    }


def official_record_ids(label_source: str) -> tuple[str, ...]:
    record_ids: set[str] = set()
    for item in label_source.replace(",", ";").split(";"):
        candidate = item.rsplit("#", maxsplit=1)[-1].strip().lower()
        if len(candidate) == 64 and all(
            character in "0123456789abcdef" for character in candidate
        ):
            record_ids.add(candidate)
    return tuple(sorted(record_ids))


def load_official_label_lookup(index_path: Path) -> dict[str, tuple[str, str, int]]:
    uri = f"file:{index_path.resolve().as_posix()}?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    try:
        rows = connection.execute(
            "SELECT record_id, fine_label, family_label, binary_label FROM labels"
        )
        lookup: dict[str, tuple[str, str, int]] = {}
        label_pool: dict[tuple[str, str, int], tuple[str, str, int]] = {}
        for record_id, fine_label, family_label, binary_label in rows:
            label = (str(fine_label), str(family_label), int(binary_label))
            lookup[str(record_id).lower()] = label_pool.setdefault(label, label)
    finally:
        connection.close()
    if not lookup:
        raise ValueError("official label index contains no flow records")
    return lookup


def official_label_for_source(
    dataset_label: str,
    label_source: str,
    official_lookup: dict[str, tuple[str, str, int]],
) -> tuple[str, str, int, tuple[str, ...]]:
    record_ids = official_record_ids(label_source)
    if not record_ids:
        raise ValueError(f"{dataset_label} conflicting row contains no official record id")
    missing = [record_id for record_id in record_ids if record_id not in official_lookup]
    if missing:
        raise ValueError(
            f"{dataset_label} official record id is absent from the frozen index: {missing[0]}"
        )
    labels = {official_lookup[record_id] for record_id in record_ids}
    if len(labels) != 1:
        raise ValueError(
            f"{dataset_label} official records assign incompatible labels to one flow"
        )
    fine_label, family_label, binary_label = next(iter(labels))
    if not fine_label or not family_label or binary_label not in {0, 1}:
        raise ValueError(f"{dataset_label} official record does not provide a formal label")
    return fine_label, family_label, binary_label, record_ids


def doh_official_label_for_source(
    label_source: str,
    official_lookup: dict[str, tuple[str, str, int]],
) -> tuple[str, str, int, tuple[str, ...]]:
    return official_label_for_source("DoH", label_source, official_lookup)


def add_final_merge_exclusion(
    summary: dict[str, Any],
    reason: str,
    excluded_flows: int,
    excluded_packets: int,
    excluded_packet_bytes: int,
    label_source_sha256: str,
    *,
    metadata_key: str = "final_merge_conflict_exclusion",
    rule: str = (
        "exclude only UNSW-NB15 rows whose official flow records assign "
        "multiple incompatible labels to the same resolved flow"
    ),
    extra_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    updated = json.loads(json.dumps(summary))
    updated["excluded_flows"] += excluded_flows
    updated["excluded_packets"] += excluded_packets
    updated["excluded_packet_bytes"] += excluded_packet_bytes
    updated["excluded_flow_fraction"] = (
        updated["excluded_flows"] / updated["total_finalized_flows"]
        if updated["total_finalized_flows"]
        else 0.0
    )
    updated["excluded_packet_fraction"] = (
        updated["excluded_packets"] / updated["total_parsed_packets"]
        if updated["total_parsed_packets"]
        else 0.0
    )
    updated["excluded_packet_byte_fraction"] = (
        updated["excluded_packet_bytes"] / updated["total_parsed_packet_bytes"]
        if updated["total_parsed_packet_bytes"]
        else 0.0
    )
    updated["reason_counts"][reason] = (
        int(updated["reason_counts"].get(reason, 0)) + excluded_flows
    )
    updated["approved_reasons"] = sorted(
        set(updated["approved_reasons"]) | {reason}
    )
    updated[metadata_key] = {
        "reason": reason,
        "rule": rule,
        "excluded_flows": excluded_flows,
        "excluded_packets": excluded_packets,
        "excluded_packet_bytes": excluded_packet_bytes,
        "label_source_sha256": label_source_sha256,
        "official_label_records_modified": False,
        "formal_output_contains_pending_labels": False,
    }
    if extra_evidence:
        updated[metadata_key].update(extra_evidence)
    return updated


def finalize_class_csv(
    category: str,
    dataset_dir: Path,
    temporary_path: Path,
    columns: list[str],
    expected_rows: int,
    row_validation_workers: int = 1,
    row_validation_batch_rows: int = 2048,
) -> dict[str, Any]:
    final_path = dataset_dir / f"{category}.csv"
    if final_path.exists():
        raise ValueError(f"refusing to overwrite class CSV: {final_path}")
    verification, digest = verify_csv_and_sha256_parallel(
        temporary_path,
        columns,
        expected_rows,
        require_formal_labels=True,
        workers=row_validation_workers,
        batch_rows=row_validation_batch_rows,
    )
    return {
        "attack_category": category,
        "path": str(final_path),
        "temporary_path": str(temporary_path),
        "rows": expected_rows,
        "size_bytes": temporary_path.stat().st_size,
        "sha256": digest,
        "verification": verification,
    }


def merge_class_csvs(
    dataset: dict[str, Any],
    capture_markers: list[dict[str, Any]],
    output_root: Path,
    columns: list[str],
    schema_sha256: str,
    source_manifest_sha256: str,
    policy: dict[str, Any],
    scheduling_scope: dict[str, Any],
    alignment_registration: dict[str, Any] | None = None,
    finalize_workers: int = 1,
    finalize_row_workers: int = 1,
    finalize_batch_rows: int = 2048,
) -> dict[str, Any]:
    dataset_dir = output_root / dataset["id"]
    reusable = reuse_dataset(dataset_dir, dataset["id"])
    if reusable is not None:
        return reusable
    label_exclusion_summary = aggregate_label_exclusion(capture_markers)
    dataset_dir.mkdir(parents=True, exist_ok=True)
    category_index = columns.index("attack_category")
    native_label_index = columns.index("dataset_native_label")
    traffic_class_index = columns.index("traffic_class")
    attack_subcategory_index = columns.index("attack_subcategory")
    fine_label_index = columns.index("fine_label")
    family_label_index = columns.index("family_label")
    binary_index = columns.index("binary_label")
    label_status_index = columns.index("label_status")
    label_source_index = columns.index("label_source")
    packet_count_index = columns.index("packet_count_total")
    packet_bytes_index = columns.index("packet_bytes_total")
    handles: dict[str, Any] = {}
    writers: dict[str, csv.writer] = {}
    rows: dict[str, int] = {}
    temporary_paths: dict[str, Path] = {}
    conflict_exclusion = Counter()
    conflict_sources = hashlib.sha256()
    doh_gate: dict[str, Any] | None = None
    doh_official_lookup: dict[str, tuple[str, str, int]] | None = None
    doh_unmatched_exclusion = Counter()
    doh_unmatched_sources = hashlib.sha256()
    doh_official_precedence = Counter()
    doh_official_sources = hashlib.sha256()
    doh_official_record_ids = hashlib.sha256()
    bot_gate: dict[str, Any] | None = None
    bot_official_lookup: dict[str, tuple[str, str, int]] | None = None
    bot_unmatched_exclusion = Counter()
    bot_unmatched_sources = hashlib.sha256()
    bot_official_precedence = Counter()
    bot_official_sources = hashlib.sha256()
    bot_official_record_ids = hashlib.sha256()
    merged_outputs_ready = False
    if finalize_workers < 1:
        raise ValueError("finalize workers must be positive")
    if finalize_row_workers < 1:
        raise ValueError("finalize row workers must be positive")
    if finalize_batch_rows < 1:
        raise ValueError("finalize batch rows must be positive")
    if dataset["id"] == "dohbrw2020":
        if alignment_registration is None:
            raise ValueError("DoH final merge requires its label-index registration")
        doh_gate = load_doh_source_quality_gate(alignment_registration)
        index_path = Path(alignment_registration["path"])
        if not index_path.is_file() or sha256_file(index_path) != alignment_registration["sha256"]:
            raise ValueError("DoH official label-index identity mismatch at final merge")
        doh_official_lookup = load_official_label_lookup(index_path)
    elif dataset["id"] == "cic_bot_iot":
        if alignment_registration is None:
            raise ValueError("BoT-IoT final merge requires its label-index registration")
        bot_gate = load_bot_iot_strict_label_gate(alignment_registration)
        index_path = Path(alignment_registration["path"])
        if not index_path.is_file() or sha256_file(index_path) != alignment_registration["sha256"]:
            raise ValueError("BoT-IoT official label-index identity mismatch at final merge")
        bot_official_lookup = load_official_label_lookup(index_path)
    try:
        for marker in sorted(capture_markers, key=lambda item: item["capture_id"]):
            for part in sorted(marker["parts"], key=lambda item: item["part_path"]):
                with Path(part["part_path"]).open("r", encoding="utf-8", newline="") as src:
                    for row in csv.reader(src):
                        if len(row) != len(columns):
                            raise ValueError(f"part row width mismatch: {part['part_path']}")
                        category = row[category_index]
                        binary_label = int(row[binary_index])
                        label_status = row[label_status_index].lower()
                        if (
                            dataset["id"] == "dohbrw2020"
                            and label_status == "conflicting_path_and_external_label"
                        ):
                            assert doh_official_lookup is not None
                            fine_label, family_label, binary_label, record_ids = (
                                doh_official_label_for_source(
                                    row[label_source_index], doh_official_lookup
                                )
                            )
                            official = _preprocessor.LabelRecord(
                                "aligned_unique_flow_official_precedence",
                                fine_label,
                                family_label,
                                binary_label,
                            )
                            row[label_status_index] = official.status
                            row[native_label_index] = official.fine_label
                            row[traffic_class_index] = official.traffic_class
                            row[category_index] = official.attack_category
                            row[attack_subcategory_index] = official.attack_subcategory
                            row[fine_label_index] = official.fine_label
                            row[family_label_index] = official.family_label
                            row[binary_index] = str(official.binary_label)
                            category = official.attack_category
                            label_status = official.status
                            doh_official_precedence["flows"] += 1
                            doh_official_precedence["packets"] += int(
                                row[packet_count_index]
                            )
                            doh_official_precedence["packet_bytes"] += int(
                                row[packet_bytes_index]
                            )
                            doh_official_sources.update(
                                (row[label_source_index] + "\n").encode("utf-8")
                            )
                            for record_id in record_ids:
                                doh_official_record_ids.update(
                                    (record_id + "\n").encode("ascii")
                                )
                        elif (
                            dataset["id"] == "cic_bot_iot"
                            and label_status == "conflicting_path_and_external_label"
                        ):
                            assert bot_official_lookup is not None
                            fine_label, family_label, binary_label, record_ids = (
                                official_label_for_source(
                                    "BoT-IoT",
                                    row[label_source_index],
                                    bot_official_lookup,
                                )
                            )
                            official = _preprocessor.LabelRecord(
                                "aligned_unique_flow_official_precedence",
                                fine_label,
                                family_label,
                                binary_label,
                            )
                            row[label_status_index] = official.status
                            row[native_label_index] = official.fine_label
                            row[traffic_class_index] = official.traffic_class
                            row[category_index] = official.attack_category
                            row[attack_subcategory_index] = official.attack_subcategory
                            row[fine_label_index] = official.fine_label
                            row[family_label_index] = official.family_label
                            row[binary_index] = str(official.binary_label)
                            category = official.attack_category
                            label_status = official.status
                            bot_official_precedence["flows"] += 1
                            bot_official_precedence["packets"] += int(
                                row[packet_count_index]
                            )
                            bot_official_precedence["packet_bytes"] += int(
                                row[packet_bytes_index]
                            )
                            bot_official_sources.update(
                                (row[label_source_index] + "\n").encode("utf-8")
                            )
                            for record_id in record_ids:
                                bot_official_record_ids.update(
                                    (record_id + "\n").encode("ascii")
                                )
                        elif (
                            dataset["id"] == "dohbrw2020"
                            and category == "Pending"
                            and binary_label == -1
                            and label_status == "unmatched_label"
                        ):
                            doh_unmatched_exclusion["flows"] += 1
                            doh_unmatched_exclusion["packets"] += int(
                                row[packet_count_index]
                            )
                            doh_unmatched_exclusion["packet_bytes"] += int(
                                row[packet_bytes_index]
                            )
                            doh_unmatched_sources.update(
                                (row[label_source_index] + "\n").encode("utf-8")
                            )
                            continue
                        elif (
                            dataset["id"] == "cic_bot_iot"
                            and category == "Pending"
                            and binary_label == -1
                            and label_status == "unmatched_label"
                        ):
                            bot_unmatched_exclusion["flows"] += 1
                            bot_unmatched_exclusion["packets"] += int(
                                row[packet_count_index]
                            )
                            bot_unmatched_exclusion["packet_bytes"] += int(
                                row[packet_bytes_index]
                            )
                            bot_unmatched_sources.update(
                                (row[label_source_index] + "\n").encode("utf-8")
                            )
                            continue
                        exclusion_reason = final_merge_conflict_exclusion_reason(
                            dataset["id"],
                            category,
                            binary_label,
                            label_status,
                            row[label_source_index],
                        )
                        if exclusion_reason is not None:
                            conflict_exclusion["flows"] += 1
                            conflict_exclusion["packets"] += int(row[packet_count_index])
                            conflict_exclusion["packet_bytes"] += int(
                                row[packet_bytes_index]
                            )
                            conflict_sources.update(
                                (row[label_source_index] + "\n").encode("utf-8")
                            )
                            continue
                        if category not in ATTACK_CATEGORIES or category == "Pending":
                            raise ValueError(
                                f"formal attack category unavailable for {dataset['id']}: {category}"
                            )
                        if binary_label not in {0, 1}:
                            raise ValueError(f"formal binary label unavailable for {dataset['id']}")
                        if not label_status.startswith("aligned_unique_"):
                            raise ValueError(
                                f"formal label binding unavailable for {dataset['id']}: {label_status}"
                            )
                        if category not in writers:
                            temporary = dataset_dir / f"{category}.csv.partial"
                            handle = temporary.open("w", encoding="utf-8", newline="")
                            writer = csv.writer(handle, lineterminator="\n")
                            writer.writerow(columns)
                            handles[category] = handle
                            writers[category] = writer
                            temporary_paths[category] = temporary
                            rows[category] = 0
                        writers[category].writerow(row)
                        rows[category] += 1
        if conflict_exclusion["flows"]:
            label_exclusion_summary = add_final_merge_exclusion(
                label_exclusion_summary,
                "official_label_conflict",
                conflict_exclusion["flows"],
                conflict_exclusion["packets"],
                conflict_exclusion["packet_bytes"],
                conflict_sources.hexdigest(),
            )
        if doh_unmatched_exclusion["flows"]:
            assert doh_gate is not None
            label_exclusion_summary = add_final_merge_exclusion(
                label_exclusion_summary,
                "official_unmatched_flow_exclusion_under_source_quality_adjusted_gate",
                doh_unmatched_exclusion["flows"],
                doh_unmatched_exclusion["packets"],
                doh_unmatched_exclusion["packet_bytes"],
                doh_unmatched_sources.hexdigest(),
                metadata_key="final_merge_doh_source_quality_exclusion",
                rule=(
                    "exclude only rows unresolved by the frozen official DoH flow index; "
                    "the full-source audit proves every unmatched flow has one of the "
                    "approved deletion reasons"
                ),
                extra_evidence=doh_gate,
            )
        if bot_unmatched_exclusion["flows"]:
            assert bot_gate is not None
            label_exclusion_summary = add_final_merge_exclusion(
                label_exclusion_summary,
                "official_unmatched_flow_exclusion_under_strict_full_pcap_gate",
                bot_unmatched_exclusion["flows"],
                bot_unmatched_exclusion["packets"],
                bot_unmatched_exclusion["packet_bytes"],
                bot_unmatched_sources.hexdigest(),
                metadata_key="final_merge_bot_iot_strict_label_exclusion",
                rule=(
                    "exclude only BoT-IoT feature rows unresolved by the frozen official "
                    "flow index; the full-PCAP strict audit proves every unmatched flow "
                    "has one of the frozen approved deletion reasons"
                ),
                extra_evidence=bot_gate,
            )
        maximum_excluded_fraction = float(
            policy.get("label_alignment", {}).get(
                "maximum_excluded_packet_fraction", 1.0
            )
        )
        if not 0.0 <= maximum_excluded_fraction <= 1.0:
            raise ValueError("maximum excluded packet fraction must be within [0, 1]")
        if (
            label_exclusion_summary["excluded_packet_fraction"]
            > maximum_excluded_fraction
        ):
            raise ValueError(
                "formal label excluded packet fraction exceeds frozen limit: "
                f"{dataset['id']} "
                f"{label_exclusion_summary['excluded_packet_fraction']:.9f} > "
                f"{maximum_excluded_fraction:.9f}"
            )
        if not writers:
            raise ValueError(f"dataset produced no formal rows: {dataset['id']}")
        for handle in handles.values():
            handle.flush()
            os.fsync(handle.fileno())
            handle.close()
        handles.clear()
        merged_outputs_ready = True
        categories = sorted(temporary_paths)
        worker_count = min(finalize_workers, len(categories))
        tasks = [
            (
                category,
                dataset_dir,
                temporary_paths[category],
                columns,
                rows[category],
                finalize_row_workers,
                finalize_batch_rows,
            )
            for category in categories
        ]
        if worker_count == 1:
            class_csvs = [finalize_class_csv(*task) for task in tasks]
        else:
            with ThreadPoolExecutor(max_workers=worker_count) as executor:
                class_csvs = list(executor.map(finalize_class_csv, *zip(*tasks)))
        for item in class_csvs:
            os.replace(Path(item["temporary_path"]), Path(item["path"]))
        for item in class_csvs:
            item.pop("temporary_path")
        manifest = {
            "schema_version": "caeos_dataset_class_csv_manifest_v1",
            "dataset_id": dataset["id"],
            "dataset_role": dataset["role"],
            "schema_sha256": schema_sha256,
            "source_manifest_sha256": source_manifest_sha256,
            "processing_policy": policy,
            "processing_policy_sha256": canonical_json_hash(policy),
            "scheduling_scope": scheduling_scope,
            "capture_count": len(capture_markers),
            "row_count": sum(rows.values()),
            "label_exclusion_summary": label_exclusion_summary,
            "official_label_precedence_summary": (
                {
                    "rule": "frozen official DoH flow labels override capture-path labels",
                    "remapped_flows": doh_official_precedence["flows"],
                    "remapped_packets": doh_official_precedence["packets"],
                    "remapped_packet_bytes": doh_official_precedence["packet_bytes"],
                    "label_source_sha256": doh_official_sources.hexdigest(),
                    "official_record_ids_sha256": doh_official_record_ids.hexdigest(),
                    "official_label_index_sha256": doh_gate[
                        "official_label_index_sha256"
                    ],
                    "source_quality_audit_sha256": doh_gate["audit_sha256"],
                    "modified_columns": [
                        "label_status",
                        "dataset_native_label",
                        "traffic_class",
                        "attack_category",
                        "attack_subcategory",
                        "fine_label",
                        "family_label",
                        "binary_label",
                    ],
                    "feature_columns_modified": False,
                    "official_label_records_modified": False,
                }
                if doh_gate is not None
                else (
                    {
                        "rule": "frozen official BoT-IoT flow labels override capture-path labels",
                        "remapped_flows": bot_official_precedence["flows"],
                        "remapped_packets": bot_official_precedence["packets"],
                        "remapped_packet_bytes": bot_official_precedence["packet_bytes"],
                        "label_source_sha256": bot_official_sources.hexdigest(),
                        "official_record_ids_sha256": bot_official_record_ids.hexdigest(),
                        "official_label_index_sha256": bot_gate[
                            "official_label_index_sha256"
                        ],
                        "strict_full_pcap_audit_sha256": bot_gate["audit_sha256"],
                        "modified_columns": [
                            "label_status",
                            "dataset_native_label",
                            "traffic_class",
                            "attack_category",
                            "attack_subcategory",
                            "fine_label",
                            "family_label",
                            "binary_label",
                        ],
                        "feature_columns_modified": False,
                        "official_label_records_modified": False,
                    }
                    if bot_gate is not None
                    else None
                )
            ),
            "class_csvs": class_csvs,
            "finalization": {
                "class_parallelism": worker_count,
                "full_validation": True,
                "sha256": True,
                "validation_and_sha256_single_pass": (
                    _verify_csv_and_sha256 is not None
                ),
                "row_validation_parallelism_per_class": finalize_row_workers,
                "row_validation_batch_rows": finalize_batch_rows,
                "all_classes_validated_before_rename": True,
            },
            "complete": True,
            "reused": False,
        }
        manifest["manifest_sha256"] = canonical_json_hash(manifest)
        atomic_json(dataset_dir / "dataset.manifest.json", manifest)
        return manifest
    finally:
        for handle in handles.values():
            handle.close()
        if not merged_outputs_ready:
            for path in temporary_paths.values():
                path.unlink(missing_ok=True)


def cleanup_dataset_intermediates(output_root: Path, dataset_id: str) -> None:
    for name in ("_parts", "_captures", "_split_work", "_archive_work"):
        path = output_root / name / dataset_id
        if path.exists():
            shutil.rmtree(path)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--source-manifest", required=True, type=Path)
    parser.add_argument("--label-index-manifest", required=True, type=Path)
    parser.add_argument("--pcap-repair-manifest", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--completion-path", type=Path)
    parser.add_argument("--dataset", action="append", required=True)
    parser.add_argument("--splitpcap-binary", required=True, type=Path)
    parser.add_argument("--editcap-binary", type=Path, default=Path("/usr/bin/editcap"))
    parser.add_argument("--splitpcap-commit", required=True)
    parser.add_argument("--target-piece-bytes", type=int, default=128 * 1024 * 1024)
    parser.add_argument("--split-threshold-bytes", type=int, default=256 * 1024 * 1024)
    parser.add_argument("--minimum-pieces-per-capture", type=int, default=2)
    parser.add_argument("--maximum-pieces-per-capture", type=int, default=256)
    parser.add_argument("--cpu-worker-cap", type=int, default=24)
    parser.add_argument("--memory-budget-gib", type=float, default=190.0)
    parser.add_argument("--memory-reserve-gib", type=float, default=46.0)
    parser.add_argument("--estimated-worker-gib", type=float, default=6.0)
    parser.add_argument("--memory-safety-factor", type=float, default=2.0)
    parser.add_argument("--maximum-active-flows", type=int, default=6000)
    parser.add_argument("--packet-decoder", choices=("tshark", "dpkt"), default="tshark")
    parser.add_argument("--tshark-binary", default="/usr/bin/tshark")
    parser.add_argument("--tshark-session-reset-packets", type=int, default=0)
    parser.add_argument("--finalize-workers", type=int, default=2)
    parser.add_argument("--finalize-row-workers", type=int, default=8)
    parser.add_argument("--finalize-batch-rows", type=int, default=2048)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    if args.target_piece_bytes <= 0 or args.split_threshold_bytes <= 0:
        raise ValueError("split byte thresholds must be positive")
    if args.minimum_pieces_per_capture < 2:
        raise ValueError("minimum pieces per capture must be at least two")
    if args.maximum_pieces_per_capture < args.minimum_pieces_per_capture:
        raise ValueError(
            "maximum pieces per capture must not be below the minimum"
        )
    if args.finalize_workers < 1:
        raise ValueError("finalize workers must be positive")
    if args.finalize_row_workers < 1:
        raise ValueError("finalize row workers must be positive")
    if args.finalize_batch_rows < 1:
        raise ValueError("finalize batch rows must be positive")
    if not args.splitpcap_binary.is_file():
        raise FileNotFoundError(args.splitpcap_binary)
    if not args.editcap_binary.is_file():
        raise FileNotFoundError(args.editcap_binary)
    catalog = load_json(args.catalog)
    schema = load_json(args.schema)
    source_manifest = load_json(args.source_manifest)
    label_index_manifest = load_json(args.label_index_manifest)
    repairs, repair_manifest_sha256 = load_pcap_repairs(args.pcap_repair_manifest)
    if schema.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported unified CSV schema")
    validate_source_manifest(catalog, source_manifest)
    args.packet_decoder_identity = (
        tshark_identity(args.tshark_binary)
        if args.packet_decoder == "tshark"
        else __import__("dpkt").__version__
    )
    preprocessor_code_sha256 = sha256_file(PREPROCESSOR_SOURCE_PATH)
    base_policy = processing_policy(
        catalog["feature_reservoir"],
        args.maximum_active_flows,
        args.packet_decoder,
        args.packet_decoder_identity,
        args.tshark_session_reset_packets,
        preprocessor_code_sha256,
        args.splitpcap_binary,
        args.splitpcap_commit,
        args.target_piece_bytes,
        args.minimum_pieces_per_capture,
        args.maximum_pieces_per_capture,
    )
    catalog_by_id = {item["id"]: item for item in catalog["datasets"]}
    source_by_id = {item["id"]: item for item in source_manifest["datasets"]}
    if label_index_manifest.get("schema_version") != "caeos_label_index_manifest_v1":
        raise ValueError("unsupported label index manifest")
    label_index_by_id = {
        item["id"]: item for item in label_index_manifest.get("datasets", [])
    }
    summaries: list[dict[str, Any]] = []
    for dataset_id in args.dataset:
        dataset = catalog_by_id[dataset_id]
        source_dataset = source_by_id[dataset_id]
        repair_policy, dataset_repairs = dataset_pcap_repair_policy(
            repairs, dataset_id
        )
        alignment = label_index_by_id.get(dataset_id)
        if alignment is None or alignment.get("status") != "ready":
            raise ValueError(f"formal label index is not ready: {dataset_id}")
        index_path = Path(alignment["path"])
        if not index_path.is_file() or sha256_file(index_path) != alignment["sha256"]:
            raise ValueError(f"label index identity mismatch: {dataset_id}")
        policy = json.loads(json.dumps(base_policy))
        if dataset_id == "cicids2018":
            policy["archive_member_tail_repair"] = {
                "mode": "correct_final_record_incl_len_to_available_bytes",
                "trigger": "single_recoverable_truncated_final_classic_pcap_record",
                "repair_script_sha256": sha256_file(
                    Path(__file__).parent
                    / "scripts"
                    / "repair_truncated_final_pcap_record.py"
                ),
                "deep_recovery": {
                    "trigger": "capinfos_full_scan_failure",
                    "tool": "pcapfix 1.1.7 deep scan",
                    "binary": "/usr/bin/pcapfix",
                    "binary_sha256": sha256_file(Path("/usr/bin/pcapfix")),
                    "exact_original_packet_multiset_claimed": False,
                },
            }
        policy["pcap_repair_set"] = repair_policy
        policy["label_alignment"] = {
            "path": str(index_path),
            "sha256": alignment["sha256"],
            "record_count": int(alignment["record_count"]),
            "registry_sha256": label_index_manifest["registry_sha256"],
            "tolerance_ns": int(alignment.get("tolerance_ns", 0)),
            "conflict_policy": str(alignment.get("conflict_policy", "reject")),
            "time_nonoverlap_policy": str(
                alignment.get("time_nonoverlap_policy", "reject")
            ),
            "official_boundary_split": bool(
                alignment.get("official_boundary_split", False)
            ),
            "external_label_precedence": bool(
                alignment.get("external_label_precedence", False)
            ),
            "maximum_excluded_packet_fraction": float(
                alignment.get("maximum_excluded_packet_fraction", 1.0)
            ),
            "drop_unmatched_reasons": sorted(
                alignment.get("drop_unmatched_reasons", [])
            ),
            "label_exclusion_rule_version": "caeos_label_exclusion_v1",
            "required_status_prefix": "aligned_unique_",
            "unmatched_allowed": 0,
            "conflicts_allowed": 0,
        }
        if dataset_id == "5gad_2022":
            policy["mixed_linktype_pcapng_split"] = {
                "mode": "editcap_packet_count_split_with_exact_packet_multiset_validation",
                "binary": str(args.editcap_binary),
                "binary_sha256": sha256_file(args.editcap_binary),
            }
        allowlist = capture_member_allowlist(alignment, dataset_id)
        if allowlist is not None:
            policy["capture_member_inventory_scope"] = {
                "rule": "schedule_only_members_present_in_formal_capture_label_index",
                "source_member_count": len(allowlist),
                "source_member_sha256": canonical_json_hash(sorted(allowlist)),
            }
        reusable = reuse_dataset(args.output_root / dataset_id, dataset_id)
        if reusable is not None:
            summaries.append(reusable)
            continue
        selected, scheduling_scope = select_capture_candidates(
            dataset, source_dataset, allowlist
        )
        print(
            json.dumps(
                {
                    "event": "dataset_start",
                    "dataset_id": dataset_id,
                    "scheduling_scope": scheduling_scope,
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            flush=True,
        )
        markers: list[dict[str, Any]] = []
        for capture_number, (source, member) in enumerate(selected, start=1):
            marker = process_original_capture(
                dataset,
                source,
                member,
                args,
                args.output_root,
                schema,
                catalog["feature_reservoir"],
                policy,
                dataset_repairs.get(capture_identity(source["path"], member)),
            )
            markers.append(marker)
            print(
                json.dumps(
                    {
                        "event": "capture_complete",
                        "dataset_id": dataset_id,
                        "capture_number": capture_number,
                        "capture_total": len(selected),
                        "capture_id": marker["capture_id"],
                        "source_member": source_member_name(dataset, source, member),
                        "reused": bool(marker.get("reused", False)),
                        "workers": marker["workers"],
                        "piece_count": marker["integrity"]["piece_count"],
                        "row_count": marker["rows"],
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                flush=True,
            )
        if allowlist is not None and len(markers) != len(allowlist):
            raise ValueError(
                f"frozen capture-member scheduling coverage mismatch: "
                f"{dataset_id} {len(markers)} != {len(allowlist)}"
            )
        summary = merge_class_csvs(
            dataset,
            markers,
            args.output_root,
            [item["name"] for item in schema["columns"]],
            canonical_json_hash(schema),
            source_manifest["manifest_sha256"],
            policy,
            scheduling_scope,
            alignment,
            args.finalize_workers,
            args.finalize_row_workers,
            args.finalize_batch_rows,
        )
        cleanup_dataset_intermediates(args.output_root, dataset_id)
        summaries.append(summary)
        print(
            json.dumps(
                {
                    "event": "dataset_complete",
                    "dataset_id": dataset_id,
                    "row_count": summary["row_count"],
                    "class_csv_count": len(summary["class_csvs"]),
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            flush=True,
        )
    completion = {
        "schema_version": "caeos_split_class_preprocessing_completion_v1",
        "catalog_sha256": canonical_json_hash(catalog),
        "schema_sha256": canonical_json_hash(schema),
        "source_manifest_sha256": source_manifest["manifest_sha256"],
        "pcap_repair_manifest_sha256_at_start": repair_manifest_sha256,
        "processing_policy_sha256_by_dataset": {
            item["dataset_id"]: item["processing_policy_sha256"] for item in summaries
        },
        "label_index_manifest_sha256": canonical_json_hash(label_index_manifest),
        "datasets": summaries,
        "dataset_count": len(summaries),
        "all_complete": all(item["complete"] for item in summaries),
    }
    completion["completion_sha256"] = canonical_json_hash(completion)
    completion_path = args.completion_path or args.output_root / "completion.json"
    atomic_json(completion_path, completion)
    print(json.dumps(completion, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
