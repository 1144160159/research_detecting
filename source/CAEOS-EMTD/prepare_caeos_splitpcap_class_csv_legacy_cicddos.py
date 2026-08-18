from __future__ import annotations

import argparse
import csv
import hashlib
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
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from caeos_label_alignment import label_index_registry_sha256
from caeos_unified_dataset import atomic_json, canonical_json_hash, sha256_file
from prepare_caeos_unified_multimodal_csv_legacy_cicddos import (
    ATTACK_CATEGORIES,
    SCHEMA_VERSION,
    build_processing_policy,
    load_json,
    process_capture,
    tshark_identity,
    validate_source_manifest,
    verify_csv,
)
from scripts.validate_splitpcap_integrity import validate as validate_split


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
    source_path: Path,
    split_root: Path,
    target_piece_bytes: int,
    maximum_pieces: int,
) -> tuple[list[Path], dict[str, Any]]:
    requested_pieces = min(
        maximum_pieces,
        max(2, math.ceil(source_path.stat().st_size / target_piece_bytes)),
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
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(
            f"splitpcap failed ({result.returncode}): {detail[-2000:]}"
        )
    pieces = sorted(
        path for path in split_root.iterdir() if path.is_file() and path.stat().st_size > 24
    )
    integrity = validate_split(source_path, pieces)
    integrity.update(
        {
            "requested_piece_count": requested_pieces,
            "nonempty_piece_count": len(pieces),
            "split_seconds": time.time() - started,
            "maximum_pieces": maximum_pieces,
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
        path = Path(part["part_path"])
        if not path.is_file() or sha256_file(path) != part["part_sha256"]:
            raise ValueError(f"capture marker part identity mismatch: {path}")
        if part.get("schema_sha256") != schema_sha256:
            raise ValueError("stale capture marker schema")
        if part.get("processing_policy_sha256") != policy_sha256:
            raise ValueError("stale capture marker processing policy")
    return parts


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


def load_label_boundary_repairs(
    path: Path | None,
) -> tuple[dict[str, dict[str, Any]], str | None]:
    if path is None:
        return {}, None
    manifest = load_json(path)
    if manifest.get("schema_version") != "caeos_label_boundary_repair_manifest_v1":
        raise ValueError("unsupported label boundary repair manifest")
    repairs: dict[str, dict[str, Any]] = {}
    for entry in manifest.get("repairs", []):
        capture_id = str(entry.get("capture_id", ""))
        tolerance_ns = int(entry.get("boundary_tolerance_ns", 0))
        if len(capture_id) != 64:
            raise ValueError("invalid label boundary repair capture identity")
        if not 0 < tolerance_ns <= 1_000_000:
            raise ValueError("invalid label boundary repair tolerance")
        if int(entry.get("maximum_official_gap_ns", tolerance_ns + 1)) > tolerance_ns:
            raise ValueError("label boundary repair tolerance does not cover evidence")
        if entry.get("dataset_id") != "cicddos2019":
            raise ValueError("label boundary repair dataset mismatch")
        if not entry.get("official_record_ids"):
            raise ValueError("label boundary repair lacks official record evidence")
        if capture_id in repairs:
            raise ValueError(f"duplicate label boundary repair entry: {capture_id}")
        repairs[capture_id] = entry
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


def capture_processing_policy(
    policy: dict[str, Any],
    repair: dict[str, Any] | None,
    label_boundary_repair: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if repair is None and label_boundary_repair is None:
        return policy
    effective = json.loads(json.dumps(policy))
    if repair is not None:
        effective["capture_specific_pcap_repair"] = {
            "schema_version": "caeos_capture_pcap_repair_v1",
            "source_path": repair["source_path"],
            "source_member": repair.get("source_member"),
            "original_sha256": repair["original_sha256"],
            "repaired_sha256": repair["repaired_sha256"],
            "repair_mode": repair["repair_mode"],
            "exact_captured_packet_multiset_preserved": bool(
                repair.get("exact_captured_packet_multiset_preserved", False)
            ),
            "full_tshark_scan_passed": bool(
                repair.get("full_tshark_scan_passed", False)
            ),
        }
    if label_boundary_repair is not None:
        tolerance_ns = int(label_boundary_repair["boundary_tolerance_ns"])
        effective["label_alignment"]["tolerance_ns"] = tolerance_ns
        effective["capture_specific_label_boundary_repair"] = {
            "schema_version": "caeos_capture_label_boundary_repair_v1",
            "capture_id": label_boundary_repair["capture_id"],
            "source_path": label_boundary_repair["source_path"],
            "source_member": label_boundary_repair["source_member"],
            "boundary_tolerance_ns": tolerance_ns,
            "maximum_official_gap_ns": int(
                label_boundary_repair["maximum_official_gap_ns"]
            ),
            "official_record_ids": sorted(
                str(value) for value in label_boundary_repair["official_record_ids"]
            ),
            "evidence_sha256": label_boundary_repair["evidence_sha256"],
            "repair_rule": label_boundary_repair["repair_rule"],
        }
    return effective


def archive_capture_for_label_boundary_repair(
    marker_path: Path,
    part_root: Path,
    output_root: Path,
    dataset_id: str,
    capture_id: str,
    marker: dict[str, Any],
    repair: dict[str, Any],
) -> None:
    if marker.get("marker_sha256") != repair.get("original_marker_sha256"):
        raise ValueError("label boundary repair original marker identity mismatch")
    backup_root = (
        output_root
        / "_control"
        / "label_boundary_repair_backups"
        / dataset_id
        / capture_id
    )
    if backup_root.exists():
        raise ValueError(f"label boundary repair backup already exists: {backup_root}")
    backup_root.mkdir(parents=True)
    os.replace(marker_path, backup_root / "capture.marker.before.json")
    if part_root.exists():
        os.replace(part_root, backup_root / "parts.before")
    atomic_json(
        backup_root / "repair.evidence.json",
        {
            "schema_version": "caeos_label_boundary_repair_backup_v1",
            "dataset_id": dataset_id,
            "capture_id": capture_id,
            "original_marker_sha256": marker["marker_sha256"],
            "repair": repair,
        },
    )


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
    label_boundary_repair: dict[str, Any] | None = None,
) -> dict[str, Any]:
    capture_id = capture_identity(source["path"], member)
    if repair is not None:
        if repair["source_path"] != source["path"]:
            raise ValueError("PCAP repair source path mismatch")
        if repair.get("source_member") != member:
            raise ValueError("PCAP repair source member mismatch")
        if repair["original_sha256"] != source["sha256"]:
            raise ValueError("PCAP repair original identity mismatch")
        if not repair.get("exact_captured_packet_multiset_preserved", False):
            raise ValueError("PCAP repair lacks exact packet preservation evidence")
        if not repair.get("full_tshark_scan_passed", False):
            raise ValueError("PCAP repair lacks a successful full tshark scan")
    if label_boundary_repair is not None:
        if label_boundary_repair["capture_id"] != capture_id:
            raise ValueError("label boundary repair capture identity mismatch")
        if label_boundary_repair["source_path"] != source["path"]:
            raise ValueError("label boundary repair source path mismatch")
        if label_boundary_repair.get("source_member") != member:
            raise ValueError("label boundary repair source member mismatch")
    effective_policy = capture_processing_policy(
        policy, repair, label_boundary_repair
    )
    marker_path = output_root / "_captures" / dataset["id"] / f"{capture_id}.json"
    part_root = output_root / "_parts" / dataset["id"] / capture_id
    if marker_path.exists():
        marker = load_json(marker_path)
        try:
            verify_reusable_capture(
                marker,
                canonical_json_hash(schema),
                canonical_json_hash(effective_policy),
            )
        except ValueError as error:
            if (
                label_boundary_repair is None
                or str(error) != "stale capture marker processing policy"
            ):
                raise
            archive_capture_for_label_boundary_repair(
                marker_path,
                part_root,
                output_root,
                dataset["id"],
                capture_id,
                marker,
                label_boundary_repair,
            )
        else:
            marker["reused"] = True
            return marker
    source_member = source_member_name(dataset, source, member)
    split_root = output_root / "_split_work" / dataset["id"] / capture_id
    staging_root = output_root / "_archive_work" / dataset["id"]
    started = time.time()
    try:
        with materialized_capture(source, member, staging_root, capture_id) as original_path:
            capture_path = Path(repair["repaired_path"]) if repair else original_path
            if capture_path.stat().st_size > args.split_threshold_bytes:
                pieces, integrity = split_capture(
                    args.splitpcap_binary,
                    capture_path,
                    split_root,
                    args.target_piece_bytes,
                    args.maximum_pieces_per_capture,
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
                    effective_policy,
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
                "pcap_repair": repair,
                "label_boundary_repair": label_boundary_repair,
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


def merge_class_csvs(
    dataset: dict[str, Any],
    capture_markers: list[dict[str, Any]],
    output_root: Path,
    columns: list[str],
    schema_sha256: str,
    source_manifest_sha256: str,
    policy: dict[str, Any],
    scheduling_scope: dict[str, Any],
) -> dict[str, Any]:
    dataset_dir = output_root / dataset["id"]
    reusable = reuse_dataset(dataset_dir, dataset["id"])
    if reusable is not None:
        return reusable
    label_exclusion_summary = aggregate_label_exclusion(capture_markers)
    capture_policy_counts = Counter(
        part["processing_policy_sha256"]
        for marker in capture_markers
        for part in marker.get("parts", [])
    )
    applied_repairs = [
        marker["pcap_repair"]
        for marker in capture_markers
        if marker.get("pcap_repair") is not None
    ]
    applied_label_boundary_repairs = [
        marker["label_boundary_repair"]
        for marker in capture_markers
        if marker.get("label_boundary_repair") is not None
    ]
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
    dataset_dir.mkdir(parents=True, exist_ok=True)
    category_index = columns.index("attack_category")
    binary_index = columns.index("binary_label")
    label_status_index = columns.index("label_status")
    handles: dict[str, Any] = {}
    writers: dict[str, csv.writer] = {}
    rows: dict[str, int] = {}
    temporary_paths: dict[str, Path] = {}
    try:
        for marker in sorted(capture_markers, key=lambda item: item["capture_id"]):
            for part in sorted(marker["parts"], key=lambda item: item["part_path"]):
                with Path(part["part_path"]).open("r", encoding="utf-8", newline="") as src:
                    for row in csv.reader(src):
                        if len(row) != len(columns):
                            raise ValueError(f"part row width mismatch: {part['part_path']}")
                        category = row[category_index]
                        if category not in ATTACK_CATEGORIES or category == "Pending":
                            raise ValueError(
                                f"formal attack category unavailable for {dataset['id']}: {category}"
                            )
                        if int(row[binary_index]) not in {0, 1}:
                            raise ValueError(f"formal binary label unavailable for {dataset['id']}")
                        label_status = row[label_status_index].lower()
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
        if not writers:
            raise ValueError(f"dataset produced no formal rows: {dataset['id']}")
        for handle in handles.values():
            handle.flush()
            os.fsync(handle.fileno())
            handle.close()
        handles.clear()
        class_csvs: list[dict[str, Any]] = []
        for category in sorted(temporary_paths):
            final_path = dataset_dir / f"{category}.csv"
            if final_path.exists():
                raise ValueError(f"refusing to overwrite class CSV: {final_path}")
            os.replace(temporary_paths[category], final_path)
            verification = verify_csv(final_path, columns, rows[category], require_formal_labels=True)
            class_csvs.append(
                {
                    "attack_category": category,
                    "path": str(final_path),
                    "rows": rows[category],
                    "size_bytes": final_path.stat().st_size,
                    "sha256": sha256_file(final_path),
                    "verification": verification,
                }
            )
        manifest = {
            "schema_version": "caeos_dataset_class_csv_manifest_v1",
            "dataset_id": dataset["id"],
            "dataset_role": dataset["role"],
            "schema_sha256": schema_sha256,
            "source_manifest_sha256": source_manifest_sha256,
            "processing_policy": policy,
            "processing_policy_sha256": canonical_json_hash(policy),
            "capture_processing_policy_sha256_counts": dict(
                sorted(capture_policy_counts.items())
            ),
            "applied_pcap_repairs": applied_repairs,
            "applied_label_boundary_repairs": applied_label_boundary_repairs,
            "scheduling_scope": scheduling_scope,
            "capture_count": len(capture_markers),
            "row_count": sum(rows.values()),
            "label_exclusion_summary": label_exclusion_summary,
            "class_csvs": class_csvs,
            "complete": True,
            "reused": False,
        }
        manifest["manifest_sha256"] = canonical_json_hash(manifest)
        atomic_json(dataset_dir / "dataset.manifest.json", manifest)
        return manifest
    finally:
        for handle in handles.values():
            handle.close()
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
    parser.add_argument("--label-boundary-repair-manifest", type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--completion-path", type=Path)
    parser.add_argument("--dataset", action="append", required=True)
    parser.add_argument("--splitpcap-binary", required=True, type=Path)
    parser.add_argument("--splitpcap-commit", required=True)
    parser.add_argument("--target-piece-bytes", type=int, default=128 * 1024 * 1024)
    parser.add_argument("--split-threshold-bytes", type=int, default=256 * 1024 * 1024)
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
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    if args.target_piece_bytes <= 0 or args.split_threshold_bytes <= 0:
        raise ValueError("split byte thresholds must be positive")
    if args.maximum_pieces_per_capture < 2:
        raise ValueError("maximum pieces per capture must be at least two")
    if not args.splitpcap_binary.is_file():
        raise FileNotFoundError(args.splitpcap_binary)
    catalog = load_json(args.catalog)
    schema = load_json(args.schema)
    source_manifest = load_json(args.source_manifest)
    label_index_manifest = load_json(args.label_index_manifest)
    repairs, repair_manifest_sha256 = load_pcap_repairs(args.pcap_repair_manifest)
    label_boundary_repairs, label_boundary_repair_manifest_sha256 = (
        load_label_boundary_repairs(args.label_boundary_repair_manifest)
    )
    if args.dataset != ["cicddos2019"]:
        raise ValueError("legacy continuation is restricted to CICDDoS2019")
    if schema.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported unified CSV schema")
    validate_source_manifest(catalog, source_manifest)
    args.packet_decoder_identity = (
        tshark_identity(args.tshark_binary)
        if args.packet_decoder == "tshark"
        else __import__("dpkt").__version__
    )
    preprocessor_code_sha256 = sha256_file(
        Path(__file__).with_name("prepare_caeos_unified_multimodal_csv_legacy_cicddos.py")
    )
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
    )
    base_policy["pcap_repair_manifest_sha256"] = (
        "87847e5e61ef875e2c44c0e2785f9b6073c8aca922bb87040775368c2b184781"
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
        _, dataset_repairs = dataset_pcap_repair_policy(repairs, dataset_id)
        alignment = label_index_by_id.get(dataset_id)
        if alignment is None or alignment.get("status") != "ready":
            raise ValueError(f"formal label index is not ready: {dataset_id}")
        index_path = Path(alignment["path"])
        if not index_path.is_file() or sha256_file(index_path) != alignment["sha256"]:
            raise ValueError(f"label index identity mismatch: {dataset_id}")
        policy = json.loads(json.dumps(base_policy))
        policy["label_alignment"] = {
            "path": str(index_path),
            "sha256": alignment["sha256"],
            "record_count": int(alignment["record_count"]),
            "registry_sha256": label_index_registry_sha256(index_path, dataset_id),
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
                label_boundary_repairs.get(capture_identity(source["path"], member)),
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
        "label_boundary_repair_manifest_sha256_at_start": (
            label_boundary_repair_manifest_sha256
        ),
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
