from __future__ import annotations

import argparse
import csv
import hashlib
import ipaddress
import json
import sqlite3
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from build_caeos_ton_iot_label_index import (
    DATASET_ID,
    epoch_ns,
    event_identity,
    normalized_type,
    port_number,
    protocol_number,
)
from caeos_unified_dataset import atomic_json, sha256_file


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ground-truth-dir", required=True, type=Path)
    parser.add_argument("--label-index", required=True, type=Path)
    parser.add_argument("--label-index-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--missing-sample-limit", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=10_000)
    return parser.parse_args()


def numeric_paths(directory: Path, pattern: str) -> list[Path]:
    return sorted(
        directory.glob(pattern), key=lambda path: int(path.stem.rsplit("_", 1)[-1])
    )


def unique_ground_truth_paths(paths: list[Path]) -> tuple[list[Path], list[dict[str, Any]]]:
    seen: dict[str, Path] = {}
    retained: list[Path] = []
    duplicates: list[dict[str, Any]] = []
    for path in paths:
        digest = sha256_file(path)
        if digest in seen:
            duplicates.append(
                {
                    "duplicate_path": str(path),
                    "retained_path": str(seen[digest]),
                    "sha256": digest,
                    "size": path.stat().st_size,
                }
            )
        else:
            seen[digest] = path
            retained.append(path)
    return retained, duplicates


def index_identity(row: tuple[Any, ...]) -> bytes:
    start_ns, endpoint_a, port_a, endpoint_b, port_b, protocol, fine_label = row
    material = "\0".join(
        (
            str(int(start_ns)),
            bytes(endpoint_a).hex(),
            str(int(port_a)),
            bytes(endpoint_b).hex(),
            str(int(port_b)),
            str(int(protocol)),
            str(fine_label),
        )
    )
    return material.encode("ascii") + b"\n"


def flush_processed(
    connection: sqlite3.Connection, batch: list[tuple[bytes, int, None]]
) -> None:
    connection.executemany(
        "INSERT OR IGNORE INTO identities(identity, flags, ground_sample) VALUES (?, ?, ?)",
        batch,
    )
    connection.commit()
    batch.clear()


def load_processed_identities(
    coverage: sqlite3.Connection,
    index_path: Path,
    batch_size: int,
    counters: Counter[str],
) -> None:
    source = sqlite3.connect(
        f"file:{index_path.resolve().as_posix()}?mode=ro&immutable=1", uri=True
    )
    batch: list[tuple[bytes, int, None]] = []
    try:
        rows = source.execute(
            """
            SELECT start_ns, endpoint_a, port_a, endpoint_b, port_b,
                   protocol, fine_label
            FROM labels
            WHERE dataset_id = ? AND binary_label = 1
              AND endpoint_a IS NOT NULL AND start_ns IS NOT NULL
            ORDER BY rowid
            """,
            (DATASET_ID,),
        )
        for row in rows:
            counters["malicious_index_rows"] += 1
            batch.append((hashlib.sha256(index_identity(row)).digest(), 1, None))
            if len(batch) >= batch_size:
                flush_processed(coverage, batch)
        if batch:
            flush_processed(coverage, batch)
    finally:
        source.close()


def flush_ground(
    connection: sqlite3.Connection, batch: list[tuple[bytes, int, str]]
) -> None:
    connection.executemany(
        """
        INSERT INTO identities(identity, flags, ground_sample) VALUES (?, ?, ?)
        ON CONFLICT(identity) DO UPDATE SET
            flags = identities.flags | 2,
            ground_sample = COALESCE(identities.ground_sample, excluded.ground_sample)
        """,
        batch,
    )
    connection.commit()
    batch.clear()


def load_ground_identities(
    coverage: sqlite3.Connection,
    paths: list[Path],
    batch_size: int,
    counters: Counter[str],
) -> None:
    batch: list[tuple[bytes, int, str]] = []
    for path in paths:
        with path.open(
            "r", encoding="utf-8-sig", errors="replace", newline=""
        ) as handle:
            reader = csv.DictReader(handle)
            for row_number, row in enumerate(reader, start=2):
                counters["ground_truth_rows"] += 1
                try:
                    fine, _, binary = normalized_type(row["type"])
                    if binary != 1:
                        raise ValueError("official event row is not malicious")
                    timestamp = epoch_ns(row["ts"])
                    src_ip = str(ipaddress.ip_address(row["src_ip"].strip()))
                    dst_ip = str(ipaddress.ip_address(row["dst_ip"].strip()))
                    src_port = port_number(row["src_port"])
                    dst_port = port_number(row["dst_port"])
                    protocol = protocol_number(row["proto"])
                except (KeyError, ValueError, TypeError, OverflowError):
                    counters["invalid_ground_truth_rows"] += 1
                    continue
                identity = event_identity(
                    start_ns=timestamp,
                    src_ip=src_ip,
                    src_port=src_port,
                    dst_ip=dst_ip,
                    dst_port=dst_port,
                    protocol=protocol,
                    fine_label=fine,
                )
                sample = json.dumps(
                    {
                        "source": str(path),
                        "row": row_number,
                        "ts": row["ts"],
                        "src_ip": src_ip,
                        "src_port": src_port,
                        "dst_ip": dst_ip,
                        "dst_port": dst_port,
                        "proto": row["proto"],
                        "fine_label": fine,
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                )
                batch.append((hashlib.sha256(identity).digest(), 2, sample))
                counters["valid_ground_truth_rows"] += 1
                counters[f"fine::{fine}"] += 1
                if len(batch) >= batch_size:
                    flush_ground(coverage, batch)
        if batch:
            flush_ground(coverage, batch)


def audit(args: argparse.Namespace) -> dict[str, Any]:
    all_ground_paths = numeric_paths(
        args.ground_truth_dir, "GroundTruth_Network_*.csv"
    )
    if not all_ground_paths:
        raise FileNotFoundError("ToN-IoT official ground truth CSVs are missing")
    actual_index_sha256 = sha256_file(args.label_index)
    if actual_index_sha256 != args.label_index_sha256:
        raise ValueError(
            f"label index SHA-256 mismatch: {actual_index_sha256} != "
            f"{args.label_index_sha256}"
        )
    ground_paths, duplicate_files = unique_ground_truth_paths(all_ground_paths)
    processed_counters: Counter[str] = Counter()
    ground_counters: Counter[str] = Counter()
    with tempfile.TemporaryDirectory(prefix="caeos-ton-event-coverage-") as temporary:
        coverage_path = Path(temporary) / "coverage.sqlite"
        connection = sqlite3.connect(str(coverage_path))
        try:
            connection.executescript(
                """
                PRAGMA journal_mode=OFF;
                PRAGMA synchronous=OFF;
                PRAGMA temp_store=FILE;
                PRAGMA cache_size=-524288;
                CREATE TABLE identities (
                    identity BLOB PRIMARY KEY,
                    flags INTEGER NOT NULL,
                    ground_sample TEXT
                ) WITHOUT ROWID;
                """
            )
            load_processed_identities(
                connection,
                args.label_index,
                args.batch_size,
                processed_counters,
            )
            load_ground_identities(
                connection,
                ground_paths,
                args.batch_size,
                ground_counters,
            )
            processed_unique = int(
                connection.execute(
                    "SELECT COUNT(*) FROM identities WHERE (flags & 1) != 0"
                ).fetchone()[0]
            )
            ground_unique = int(
                connection.execute(
                    "SELECT COUNT(*) FROM identities WHERE (flags & 2) != 0"
                ).fetchone()[0]
            )
            covered = int(
                connection.execute(
                    "SELECT COUNT(*) FROM identities WHERE flags = 3"
                ).fetchone()[0]
            )
            missing = ground_unique - covered
            samples = [
                json.loads(row[0])
                for row in connection.execute(
                    "SELECT ground_sample FROM identities WHERE flags = 2 LIMIT ?",
                    (args.missing_sample_limit,),
                )
            ]
        finally:
            connection.close()
    coverage = covered / ground_unique if ground_unique else 0.0
    result = {
        "schema_version": "caeos_ton_iot_official_event_coverage_v2",
        "dataset_id": DATASET_ID,
        "scope": "full_deduplicated_official_security_event_identity_set",
        "label_index": str(args.label_index),
        "label_index_sha256": actual_index_sha256,
        "ground_truth_files_all": [str(path) for path in all_ground_paths],
        "ground_truth_files_retained": [str(path) for path in ground_paths],
        "duplicate_ground_truth_files": duplicate_files,
        "processed_counters": dict(sorted(processed_counters.items())),
        "ground_truth_counters": dict(sorted(ground_counters.items())),
        "processed_unique_malicious_events": processed_unique,
        "official_unique_events": ground_unique,
        "covered_unique_events": covered,
        "missing_unique_events": missing,
        "coverage_fraction": coverage,
        "missing_samples": samples,
        "missing_samples_truncated": missing > len(samples),
        "coverage_method": (
            "disk-backed exact set inclusion over SHA-256 of canonical "
            "bidirectional five-tuple, epoch timestamp, and official fine label"
        ),
        "formal_gate_passed": False,
        "formal_gate_reason": (
            "full official event coverage does not replace all-PCAP flow coverage"
        ),
    }
    result["audit_sha256"] = hashlib.sha256(
        json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    atomic_json(args.output, result)
    return result


def main() -> None:
    print(json.dumps(audit(parse_arguments()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
