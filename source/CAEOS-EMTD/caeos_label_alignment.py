from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import shutil
import sqlite3
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "caeos_label_alignment_sqlite_v1"


@dataclass(frozen=True)
class LabelResolution:
    status: str
    fine_label: str
    family_label: str
    binary_label: int
    label_source: str
    record_ids: tuple[str, ...] = ()


def label_index_registry_sha256(path: Path, dataset_id: str) -> str:
    """Return the immutable registry identity embedded in a label index."""
    path = Path(path)
    uri = f"file:{path.resolve().as_posix()}?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    try:
        metadata = dict(connection.execute("SELECT key, value FROM metadata"))
    finally:
        connection.close()
    if metadata.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"unsupported label index schema: {path}")
    if metadata.get("dataset_id") != dataset_id:
        raise ValueError(f"label index dataset mismatch: {dataset_id}")
    registry_sha256 = metadata.get("registry_sha256", "")
    if len(registry_sha256) != 64 or any(
        character not in "0123456789abcdef" for character in registry_sha256.lower()
    ):
        raise ValueError(f"invalid label index registry SHA-256: {path}")
    return registry_sha256.lower()


def canonical_endpoints(
    first_ip: bytes, first_port: int, second_ip: bytes, second_port: int
) -> tuple[bytes, int, bytes, int]:
    first = (bytes(first_ip), int(first_port))
    second = (bytes(second_ip), int(second_port))
    if first <= second:
        return first[0], first[1], second[0], second[1]
    return second[0], second[1], first[0], first[1]


def packed_ip(value: str | bytes) -> bytes:
    if isinstance(value, bytes):
        return value
    return ipaddress.ip_address(value.strip()).packed


def create_label_index(
    path: Path,
    dataset_id: str,
    records: Iterable[dict[str, Any]],
    registry_sha256: str,
) -> dict[str, Any]:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    destination_temporary = path.with_suffix(path.suffix + ".partial")
    destination_temporary.unlink(missing_ok=True)
    staging_dir = Path(tempfile.mkdtemp(prefix="caeos-label-index-"))
    staged_path = staging_dir / "labels.sqlite"
    build_complete = False
    published = False
    publication_attempts = 0
    try:
        connection = sqlite3.connect(str(staged_path))
        try:
            connection.executescript(
            """
            PRAGMA journal_mode=OFF;
            PRAGMA synchronous=FULL;
            PRAGMA temp_store=FILE;
            PRAGMA threads=8;
            CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE labels (
                record_id TEXT PRIMARY KEY,
                dataset_id TEXT NOT NULL,
                source_member TEXT,
                endpoint_a BLOB,
                port_a INTEGER,
                endpoint_b BLOB,
                port_b INTEGER,
                protocol INTEGER,
                start_ns INTEGER,
                end_ns INTEGER,
                fine_label TEXT NOT NULL,
                family_label TEXT NOT NULL,
                binary_label INTEGER NOT NULL CHECK(binary_label IN (0, 1)),
                label_source TEXT NOT NULL,
                CHECK(
                    (endpoint_a IS NULL AND endpoint_b IS NULL) OR
                    (endpoint_a IS NOT NULL AND endpoint_b IS NOT NULL AND
                     ((port_a IS NULL AND port_b IS NULL) OR
                      (port_a IS NOT NULL AND port_b IS NOT NULL AND protocol IS NOT NULL)))
                )
            );
            """
        )
            connection.executemany(
            "INSERT INTO metadata(key, value) VALUES (?, ?)",
            (
                ("schema_version", SCHEMA_VERSION),
                ("dataset_id", dataset_id),
                ("registry_sha256", registry_sha256),
            ),
        )
            insert_sql = """
                INSERT INTO labels(
                    record_id, dataset_id, source_member,
                    endpoint_a, port_a, endpoint_b, port_b, protocol,
                    start_ns, end_ns, fine_label, family_label,
                    binary_label, label_source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            batch: list[tuple[Any, ...]] = []
            count = 0
            for record in records:
                source_member = record.get("source_member") or None
                if record.get("src_ip") is None:
                    endpoints: tuple[Any, ...] = (
                        None,
                        None,
                        None,
                        None,
                        (
                            int(record["protocol"])
                            if record.get("protocol") is not None
                            else None
                        ),
                    )
                elif record.get("src_port") is None:
                    first = packed_ip(record["src_ip"])
                    second = packed_ip(record["dst_ip"])
                    a_ip, b_ip = (first, second) if first <= second else (second, first)
                    endpoints = (
                        a_ip,
                        None,
                        b_ip,
                        None,
                        (
                            int(record["protocol"])
                            if record.get("protocol") is not None
                            else None
                        ),
                    )
                else:
                    a_ip, a_port, b_ip, b_port = canonical_endpoints(
                        packed_ip(record["src_ip"]),
                        int(record["src_port"]),
                        packed_ip(record["dst_ip"]),
                        int(record["dst_port"]),
                    )
                    endpoints = (a_ip, a_port, b_ip, b_port, int(record["protocol"]))
                binary_label = int(record["binary_label"])
                if binary_label not in {0, 1}:
                    raise ValueError(f"non-formal binary label: {binary_label}")
                record_id = str(record.get("record_id") or "").strip()
                if not record_id:
                    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"))
                    record_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
                batch.append(
                    (
                    record_id,
                    dataset_id,
                    source_member,
                    *endpoints,
                    record.get("start_ns"),
                    record.get("end_ns"),
                    str(record["fine_label"]),
                    str(record["family_label"]),
                    binary_label,
                    str(record["label_source"]),
                    )
                )
                count += 1
                if len(batch) >= 10_000:
                    connection.executemany(insert_sql, batch)
                    batch.clear()
            if batch:
                connection.executemany(insert_sql, batch)
            connection.executescript(
                """
                PRAGMA threads=8;
                CREATE INDEX labels_flow_lookup ON labels(
                    dataset_id, endpoint_a, port_a, endpoint_b, port_b, protocol
                );
                CREATE INDEX labels_capture_lookup ON labels(dataset_id, source_member);
                CREATE INDEX labels_time_lookup ON labels(dataset_id, start_ns, end_ns);
                """
            )
            connection.execute(
                "INSERT INTO metadata(key, value) VALUES (?, ?)",
                ("record_count", str(count)),
            )
            connection.commit()
            connection.execute("PRAGMA optimize")
        finally:
            connection.close()
        build_complete = True
        last_error: BaseException | None = None
        digest_hex = ""
        publication_fsync_errors: list[str] = []
        publication_fsync_confirmed = False
        for publication_attempts in range(1, 4):
            destination_temporary.unlink(missing_ok=True)
            digest = hashlib.sha256()
            fsync_error: OSError | None = None
            try:
                with staged_path.open("rb") as source, destination_temporary.open(
                    "wb"
                ) as target:
                    while True:
                        block = source.read(16 * 1024 * 1024)
                        if not block:
                            break
                        digest.update(block)
                        target.write(block)
                    target.flush()
                    try:
                        os.fsync(target.fileno())
                    except OSError as error:
                        # Some NFS mounts return EIO after accepting the full write.
                        # A complete target-side reread and digest comparison remains
                        # the publication authority in that case.
                        fsync_error = error
                digest_hex = digest.hexdigest()
                published_digest = hashlib.sha256()
                with destination_temporary.open("rb") as published_handle:
                    for block in iter(
                        lambda: published_handle.read(16 * 1024 * 1024), b""
                    ):
                        published_digest.update(block)
                if published_digest.hexdigest() != digest_hex:
                    raise OSError("published label index SHA-256 mismatch")
                if fsync_error is not None:
                    publication_fsync_errors.append(repr(fsync_error))
                else:
                    publication_fsync_confirmed = True
                os.replace(destination_temporary, path)
                published = True
                break
            except OSError as error:
                last_error = error
                destination_temporary.unlink(missing_ok=True)
                if publication_attempts < 3:
                    time.sleep(5 * publication_attempts)
        if not published:
            raise OSError(
                f"label index publication failed after 3 attempts; complete "
                f"staging index retained at {staged_path}: {last_error}"
            ) from last_error
    finally:
        if published or not build_complete:
            shutil.rmtree(staging_dir, ignore_errors=True)
    return {
        "schema_version": SCHEMA_VERSION,
        "dataset_id": dataset_id,
        "record_count": count,
        "registry_sha256": registry_sha256,
        "path": str(path),
        "sha256": digest_hex,
        "publication_attempts": publication_attempts,
        "publication_verified_by_target_reread": True,
        "publication_fsync_confirmed": publication_fsync_confirmed,
        "publication_fsync_errors": publication_fsync_errors,
        "publication_integrity_basis": (
            "fsync_and_target_reread_sha256"
            if publication_fsync_confirmed
            else "target_reread_sha256_after_fsync_error"
        ),
    }


class LabelResolver:
    def __init__(
        self,
        path: Path,
        dataset_id: str,
        expected_sha256: str,
        tolerance_ns: int = 0,
        conflict_policy: str = "reject",
        time_nonoverlap_policy: str = "reject",
    ) -> None:
        self.path = Path(path)
        self.dataset_id = dataset_id
        self.tolerance_ns = int(tolerance_ns)
        if conflict_policy not in {"reject", "malicious_over_benign_bidirectional"}:
            raise ValueError(f"unsupported label conflict policy: {conflict_policy}")
        self.conflict_policy = conflict_policy
        if time_nonoverlap_policy not in {"reject", "nearest_official_same_tuple"}:
            raise ValueError(
                f"unsupported time nonoverlap policy: {time_nonoverlap_policy}"
            )
        self.time_nonoverlap_policy = time_nonoverlap_policy
        digest = hashlib.sha256()
        with self.path.open("rb") as handle:
            for block in iter(lambda: handle.read(16 * 1024 * 1024), b""):
                digest.update(block)
        actual_sha256 = digest.hexdigest()
        if actual_sha256 != expected_sha256:
            raise ValueError(
                f"label index SHA-256 mismatch: {actual_sha256} != {expected_sha256}"
            )
        uri = f"file:{self.path.resolve().as_posix()}?mode=ro&immutable=1"
        self.connection = sqlite3.connect(uri, uri=True, cached_statements=512)
        mmap_bytes = int(
            os.environ.get("CAEOS_LABEL_INDEX_MMAP_BYTES", str(64 * 1024**3))
        )
        cache_kib = int(
            os.environ.get("CAEOS_LABEL_INDEX_CACHE_KIB", str(512 * 1024))
        )
        if mmap_bytes < 0 or cache_kib < 1:
            raise ValueError("SQLite mmap and cache settings must be non-negative")
        self.connection.execute("PRAGMA query_only=ON")
        self.connection.execute("PRAGMA temp_store=MEMORY")
        self.connection.execute(f"PRAGMA mmap_size={mmap_bytes}")
        self.connection.execute(f"PRAGMA cache_size={-cache_kib}")
        self.sqlite_mmap_size = int(
            self.connection.execute("PRAGMA mmap_size").fetchone()[0]
        )
        self.sqlite_cache_kib = cache_kib
        metadata = dict(self.connection.execute("SELECT key, value FROM metadata"))
        if metadata.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("unsupported label index schema")
        if metadata.get("dataset_id") != dataset_id:
            raise ValueError("label index dataset mismatch")
        self.official_protocols = frozenset(
            int(row[0])
            for row in self.connection.execute(
                "SELECT DISTINCT protocol FROM labels "
                "WHERE dataset_id = ? AND protocol IS NOT NULL",
                (self.dataset_id,),
            )
        )
        self.has_capture_labels = bool(
            self.connection.execute(
                "SELECT 1 FROM labels WHERE dataset_id = ? "
                "AND endpoint_a IS NULL LIMIT 1",
                (self.dataset_id,),
            ).fetchone()
        )
        self.has_endpoint_time_rules = bool(
            self.connection.execute(
                "SELECT 1 FROM labels WHERE dataset_id = ? "
                "AND endpoint_a IS NOT NULL AND port_a IS NULL LIMIT 1",
                (self.dataset_id,),
            ).fetchone()
        )
        self._last_flow_key: tuple[bytes, int, bytes, int, int] | None = None
        self._last_flow_rows: tuple[tuple[Any, ...], ...] = ()
        self.flow_candidate_queries = 0
        self.flow_candidate_cache_hits = 0

    def close(self) -> None:
        self.connection.close()

    def _flow_candidates(
        self,
        endpoint_a: bytes,
        port_a: int,
        endpoint_b: bytes,
        port_b: int,
        protocol: int,
    ) -> tuple[tuple[Any, ...], ...]:
        key = (
            bytes(endpoint_a),
            int(port_a),
            bytes(endpoint_b),
            int(port_b),
            int(protocol),
        )
        if key == self._last_flow_key:
            self.flow_candidate_cache_hits += 1
            return self._last_flow_rows
        rows = list(
            self.connection.execute(
                """
                SELECT record_id, source_member, start_ns, end_ns, fine_label,
                       family_label, binary_label, label_source
                FROM labels
                WHERE dataset_id = ? AND endpoint_a = ? AND port_a = ?
                  AND endpoint_b = ? AND port_b = ? AND protocol = ?
                ORDER BY record_id
                """,
                (self.dataset_id, *key),
            ).fetchall()
        )
        if self.has_endpoint_time_rules:
            rows.extend(
                self.connection.execute(
                    """
                    SELECT record_id, source_member, start_ns, end_ns, fine_label,
                           family_label, binary_label, label_source
                    FROM labels
                    WHERE dataset_id = ? AND endpoint_a = ? AND port_a IS NULL
                      AND endpoint_b = ? AND port_b IS NULL
                      AND (protocol IS NULL OR protocol = ?)
                    ORDER BY record_id
                    """,
                    (self.dataset_id, key[0], key[2], key[4]),
                ).fetchall()
            )
        resolved_rows = tuple(rows)
        self.flow_candidate_queries += 1
        self._last_flow_key = key
        self._last_flow_rows = resolved_rows
        return resolved_rows

    def _applicable_flow_rows(
        self,
        rows: tuple[tuple[Any, ...], ...],
        source_member: str,
        flow_start_ns: int,
        flow_end_ns: int,
    ) -> list[tuple[Any, ...]]:
        lower = int(flow_start_ns) - self.tolerance_ns
        upper = int(flow_end_ns) + self.tolerance_ns
        return [
            row
            for row in rows
            if (row[1] is None or str(row[1]) == source_member)
            and (row[2] is None or int(row[2]) <= upper)
            and (row[3] is None or int(row[3]) >= lower)
        ]

    def _capture_candidates(
        self,
        source_member: str,
        protocol: int,
        flow_start_ns: int,
        flow_end_ns: int,
    ) -> list[tuple[Any, ...]]:
        if not self.has_capture_labels:
            return []
        return self.connection.execute(
            """
            SELECT record_id, source_member, start_ns, end_ns, fine_label,
                   family_label, binary_label, label_source
            FROM labels
            WHERE dataset_id = ? AND endpoint_a IS NULL
              AND (source_member IS NULL OR source_member = ?)
              AND (protocol IS NULL OR protocol = ?)
              AND (start_ns IS NULL OR start_ns <= ?)
              AND (end_ns IS NULL OR end_ns >= ?)
            ORDER BY record_id
            """,
            (
                self.dataset_id,
                source_member,
                int(protocol),
                int(flow_end_ns) + self.tolerance_ns,
                int(flow_start_ns) - self.tolerance_ns,
            ),
        ).fetchall()

    def _resolution_from_rows(
        self, rows: list[tuple[Any, ...]], alignment: str
    ) -> LabelResolution:
        labels = {(str(row[4]), str(row[5]), int(row[6])) for row in rows}
        record_ids = tuple(sorted(str(row[0]) for row in rows))
        sources = tuple(sorted({str(row[7]) for row in rows}))
        if len(labels) != 1:
            malicious = {label for label in labels if label[2] == 1}
            benign = {label for label in labels if label[2] == 0}
            if (
                self.conflict_policy == "malicious_over_benign_bidirectional"
                and len(malicious) == 1
                and benign == {("Benign", "Benign", 0)}
            ):
                fine_label, family_label, binary_label = next(iter(malicious))
                return LabelResolution(
                    f"aligned_unique_{alignment}_malicious_over_benign",
                    fine_label,
                    family_label,
                    binary_label,
                    ";".join(sources) + "#" + ",".join(record_ids),
                    record_ids,
                )
            return LabelResolution(
                "conflicting_label",
                "",
                "",
                -1,
                ";".join(sources),
                record_ids,
            )
        fine_label, family_label, binary_label = next(iter(labels))
        return LabelResolution(
            f"aligned_unique_{alignment}",
            fine_label,
            family_label,
            binary_label,
            ";".join(sources) + "#" + ",".join(record_ids),
            record_ids,
        )

    def resolve(
        self,
        source_member: str,
        endpoint_a: bytes,
        port_a: int,
        endpoint_b: bytes,
        port_b: int,
        protocol: int,
        flow_start_ns: int,
        flow_end_ns: int,
    ) -> LabelResolution:
        a_ip, a_port, b_ip, b_port = canonical_endpoints(
            endpoint_a, port_a, endpoint_b, port_b
        )
        candidates = self._flow_candidates(
            a_ip, a_port, b_ip, b_port, int(protocol)
        )
        rows = self._applicable_flow_rows(
            candidates, source_member, flow_start_ns, flow_end_ns
        )
        if rows:
            return self._resolution_from_rows(rows, "flow")
        capture_rows = self._capture_candidates(
            source_member, int(protocol), flow_start_ns, flow_end_ns
        )
        if not capture_rows:
            if self.time_nonoverlap_policy == "nearest_official_same_tuple":
                nearest = self.resolve_nearest_official(
                    source_member,
                    endpoint_a,
                    port_a,
                    endpoint_b,
                    port_b,
                    protocol,
                    flow_start_ns,
                    flow_end_ns,
                )
                if nearest is not None:
                    return nearest
            return LabelResolution("unmatched_label", "", "", -1, "", ())
        return self._resolution_from_rows(capture_rows, "capture")

    def resolve_nearest_official(
        self,
        source_member: str,
        endpoint_a: bytes,
        port_a: int,
        endpoint_b: bytes,
        port_b: int,
        protocol: int,
        flow_start_ns: int,
        flow_end_ns: int,
    ) -> LabelResolution | None:
        if int(protocol) not in {6, 17}:
            return None
        a_ip, a_port, b_ip, b_port = canonical_endpoints(
            endpoint_a, port_a, endpoint_b, port_b
        )
        rows = [
            row
            for row in self._flow_candidates(
                a_ip, a_port, b_ip, b_port, int(protocol)
            )
            if row[1] is None or str(row[1]) == source_member
        ]
        if not rows:
            return None

        best_scope = max(int(row[1] is not None) for row in rows)
        rows = [row for row in rows if int(row[1] is not None) == best_scope]

        def gap(row: tuple[Any, ...]) -> int:
            start_ns = int(row[2])
            end_ns = int(row[3])
            if end_ns < flow_start_ns:
                return int(flow_start_ns) - end_ns
            if start_ns > flow_end_ns:
                return start_ns - int(flow_end_ns)
            return 0

        minimum_gap = min(gap(row) for row in rows)
        nearest = [row for row in rows if gap(row) == minimum_gap]
        labels = {(str(row[4]), str(row[5]), int(row[6])) for row in nearest}
        record_ids = tuple(sorted(str(row[0]) for row in nearest))
        sources = tuple(sorted({str(row[7]) for row in nearest}))
        if len(labels) != 1:
            return LabelResolution(
                "conflicting_nearest_official_label",
                "",
                "",
                -1,
                ";".join(sources) + f"#nearest_gap_ns={minimum_gap}",
                record_ids,
            )
        fine_label, family_label, binary_label = next(iter(labels))
        return LabelResolution(
            "aligned_unique_flow_nearest_official_time_nonoverlap",
            fine_label,
            family_label,
            binary_label,
            ";".join(sources)
            + "#"
            + ",".join(record_ids)
            + f";nearest_gap_ns={minimum_gap}",
            record_ids,
        )

    def diagnose_unmatched(
        self,
        source_member: str,
        endpoint_a: bytes,
        port_a: int,
        endpoint_b: bytes,
        port_b: int,
        protocol: int,
        flow_start_ns: int,
        flow_end_ns: int,
    ) -> dict[str, Any]:
        a_ip, a_port, b_ip, b_port = canonical_endpoints(
            endpoint_a, port_a, endpoint_b, port_b
        )
        if int(protocol) not in self.official_protocols:
            return {
                "reason": "protocol_outside_official_tcp_udp_flow_labels",
                "protocol": int(protocol),
                "official_protocols": sorted(self.official_protocols),
            }

        parameters = (
            self.dataset_id,
            a_ip,
            a_port,
            b_ip,
            b_port,
            int(protocol),
        )
        candidates = self._flow_candidates(
            a_ip, a_port, b_ip, b_port, int(protocol)
        )

        def gap(row: tuple[Any, ...]) -> int:
            candidate_start = int(row[2])
            candidate_end = int(row[3])
            if candidate_end < flow_start_ns:
                return int(flow_start_ns) - candidate_end
            if candidate_start > flow_end_ns:
                return candidate_start - int(flow_end_ns)
            return 0

        same_capture_rows = [
            row
            for row in candidates
            if row[1] is None or str(row[1]) == source_member
        ]
        same_capture = (
            min(same_capture_rows, key=lambda row: (gap(row), str(row[0])))
            if same_capture_rows
            else None
        )
        if same_capture is not None:
            candidate_start = int(same_capture[2])
            candidate_end = int(same_capture[3])
            if candidate_end < flow_start_ns:
                gap_ns = int(flow_start_ns) - candidate_end
            elif candidate_start > flow_end_ns:
                gap_ns = candidate_start - int(flow_end_ns)
            else:
                gap_ns = 0
            return {
                "reason": "five_tuple_present_but_time_not_overlapping",
                "protocol": int(protocol),
                "nearest_gap_ns": gap_ns,
                "nearest_record_id": str(same_capture[0]),
                "nearest_start_ns": candidate_start,
                "nearest_end_ns": candidate_end,
                "nearest_fine_label": str(same_capture[4]),
                "nearest_family_label": str(same_capture[5]),
                "nearest_binary_label": int(same_capture[6]),
                "nearest_label_source": str(same_capture[7]),
            }
        other_capture = min(candidates, key=lambda row: str(row[0])) if candidates else None
        if other_capture is not None:
            return {
                "reason": "five_tuple_present_only_in_other_capture_scope",
                "protocol": int(protocol),
                "nearest_record_id": str(other_capture[0]),
                "nearest_source_member": str(other_capture[1]),
                "nearest_start_ns": int(other_capture[2]),
                "nearest_end_ns": int(other_capture[3]),
                "nearest_fine_label": str(other_capture[4]),
                "nearest_family_label": str(other_capture[5]),
                "nearest_binary_label": int(other_capture[6]),
                "nearest_label_source": str(other_capture[7]),
            }
        return {
            "reason": "five_tuple_absent_from_official_flow_labels",
            "protocol": int(protocol),
        }

    def diagnose_conflict(
        self,
        source_member: str,
        endpoint_a: bytes,
        port_a: int,
        endpoint_b: bytes,
        port_b: int,
        protocol: int,
        flow_start_ns: int,
        flow_end_ns: int,
    ) -> dict[str, Any]:
        a_ip, a_port, b_ip, b_port = canonical_endpoints(
            endpoint_a, port_a, endpoint_b, port_b
        )
        rows = [
            row
            for row in self._flow_candidates(
                a_ip, a_port, b_ip, b_port, int(protocol)
            )
            if (row[1] is None or str(row[1]) == source_member)
            and (row[2] is None or int(row[2]) <= int(flow_end_ns) + self.tolerance_ns)
            and (row[3] is None or int(row[3]) >= int(flow_start_ns) - self.tolerance_ns)
        ]
        rows.sort(
            key=lambda row: (
                -1 if row[2] is None else int(row[2]),
                -1 if row[3] is None else int(row[3]),
                str(row[0]),
            )
        )
        label_counts: dict[str, int] = {}
        records: list[dict[str, Any]] = []
        for row in rows:
            label_key = f"{row[5]}::{row[4]}::binary={int(row[6])}"
            label_counts[label_key] = label_counts.get(label_key, 0) + 1
            if len(records) < 20:
                records.append(
                    {
                        "record_id": str(row[0]),
                        "start_ns": int(row[2]),
                        "end_ns": int(row[3]),
                        "fine_label": str(row[4]),
                        "family_label": str(row[5]),
                        "binary_label": int(row[6]),
                        "label_source": str(row[7]),
                    }
                )
        return {
            "reason": "overlapping_external_records_have_different_labels",
            "protocol": int(protocol),
            "candidate_record_count": len(rows),
            "candidate_label_counts": dict(sorted(label_counts.items())),
            "candidate_records": records,
            "candidate_records_truncated": len(rows) > len(records),
        }

    def split_packet_observations_by_official_labels(
        self,
        source_member: str,
        endpoint_a: bytes,
        port_a: int,
        endpoint_b: bytes,
        port_b: int,
        protocol: int,
        observations: list[tuple[int, int]],
    ) -> dict[str, Any]:
        """Build consecutive packet segments from authoritative flow intervals."""
        if not observations:
            return {"resolved": False, "reason": "no_packet_observations"}
        a_ip, a_port, b_ip, b_port = canonical_endpoints(
            endpoint_a, port_a, endpoint_b, port_b
        )
        flow_start_ns = min(timestamp for timestamp, _ in observations)
        flow_end_ns = max(timestamp for timestamp, _ in observations)
        rows = [
            row
            for row in self._flow_candidates(
                a_ip, a_port, b_ip, b_port, int(protocol)
            )
            if (row[1] is None or str(row[1]) == source_member)
            and row[2] is not None
            and row[3] is not None
            and int(row[2]) <= flow_end_ns + self.tolerance_ns
            and int(row[3]) >= flow_start_ns - self.tolerance_ns
        ]
        if not rows:
            return {
                "resolved": False,
                "reason": "no_authoritative_intervals_for_flow",
            }

        segments: list[dict[str, Any]] = []
        unassigned_packets = 0
        ambiguous_packets = 0
        for observation_index, (timestamp_ns, packet_bytes) in enumerate(observations):
            def gap(row: tuple[Any, ...]) -> int:
                start_ns = int(row[2])
                end_ns = int(row[3])
                if timestamp_ns < start_ns:
                    return start_ns - timestamp_ns
                if timestamp_ns > end_ns:
                    return timestamp_ns - end_ns
                return 0

            minimum_gap = min(gap(row) for row in rows)
            if minimum_gap > self.tolerance_ns:
                unassigned_packets += 1
                continue
            nearest = [row for row in rows if gap(row) == minimum_gap]
            labels = {(str(row[4]), str(row[5]), int(row[6])) for row in nearest}
            if len(labels) != 1:
                ambiguous_packets += 1
                continue
            fine_label, family_label, binary_label = next(iter(labels))
            record_ids = sorted(str(row[0]) for row in nearest)
            label_sources = sorted({str(row[7]) for row in nearest})
            label_key = (fine_label, family_label, binary_label)
            if segments and tuple(segments[-1]["label_key"]) == label_key:
                segment = segments[-1]
                segment["end_ns"] = max(int(segment["end_ns"]), timestamp_ns)
                segment["start_ns"] = min(int(segment["start_ns"]), timestamp_ns)
                segment["packet_count"] += 1
                segment["packet_bytes"] += int(packet_bytes)
                segment["observation_end_index"] = observation_index + 1
                segment["record_ids"] = sorted(
                    set(segment["record_ids"]) | set(record_ids)
                )
                segment["label_sources"] = sorted(
                    set(segment["label_sources"]) | set(label_sources)
                )
            else:
                segments.append(
                    {
                        "label_key": list(label_key),
                        "fine_label": fine_label,
                        "family_label": family_label,
                        "binary_label": binary_label,
                        "start_ns": timestamp_ns,
                        "end_ns": timestamp_ns,
                        "packet_count": 1,
                        "packet_bytes": int(packet_bytes),
                        "observation_start_index": observation_index,
                        "observation_end_index": observation_index + 1,
                        "record_ids": record_ids,
                        "label_sources": label_sources,
                    }
                )
        resolved = bool(
            len(segments) >= 2
            and unassigned_packets == 0
            and ambiguous_packets == 0
            and sum(int(segment["packet_count"]) for segment in segments)
            == len(observations)
        )
        return {
            "resolved": resolved,
            "reason": (
                "official_time_boundary_split"
                if resolved
                else "official_time_boundary_split_incomplete"
            ),
            "source_packet_count": len(observations),
            "source_packet_bytes": sum(value for _, value in observations),
            "unassigned_packets": unassigned_packets,
            "ambiguous_packets": ambiguous_packets,
            "segments": segments,
        }
