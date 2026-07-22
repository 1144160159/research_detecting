from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sqlite3
import sys
import tempfile
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from create_gpu_dataset_expansion_protocol import central_directory_identity


MEMBER_SCAN_SCHEMA = "gpu_malicious_dataset_member_scan_v1"


def increase_csv_limit() -> None:
    limit = sys.maxsize
    while True:
        try:
            csv.field_size_limit(limit)
            return
        except OverflowError:
            limit //= 10


increase_csv_limit()


def normalized_header(value: str) -> str:
    return " ".join(value.replace("\ufeff", "").strip().split())


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_hash(parts: Iterable[str]) -> str:
    payload = "\x1f".join(parts).encode("utf-8", errors="replace")
    return hashlib.sha256(payload).hexdigest()


def row_value(row: list[str], columns: dict[str, int], *names: str) -> str:
    for name in names:
        index = columns.get(name)
        if index is not None and index < len(row):
            value = row[index].strip()
            if value:
                return value
    return ""


def endpoint_pair(
    source_address: str,
    source_port: str,
    destination_address: str,
    destination_port: str,
) -> tuple[str, str]:
    source = f"{source_address}:{source_port or '0'}"
    destination = f"{destination_address}:{destination_port or '0'}"
    return tuple(sorted((source, destination)))  # type: ignore[return-value]


def parse_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class LsnmSessionizer:
    def __init__(self, member: str, gap_seconds: float = 120.0) -> None:
        self.member = member
        self.gap_seconds = gap_seconds
        self.state: dict[tuple[str, str, str], tuple[float | None, int]] = {}

    def group(self, row: list[str], columns: dict[str, int]) -> str | None:
        source = row_value(row, columns, "IP Source", "Source")
        destination = row_value(row, columns, "IP Destination", "Destination")
        protocol = row_value(row, columns, "IP Protocol", "Protocol")
        if not source or not destination or not protocol:
            return None
        tcp_source = row_value(row, columns, "TCP Source Port")
        tcp_destination = row_value(row, columns, "TCP Destination Port")
        udp_source = row_value(row, columns, "UDP Source Port")
        udp_destination = row_value(row, columns, "UDP Destination Port")
        endpoint_a, endpoint_b = endpoint_pair(
            source,
            tcp_source or udp_source,
            destination,
            tcp_destination or udp_destination,
        )
        key = (endpoint_a, endpoint_b, protocol)
        timestamp = parse_float(
            row_value(row, columns, "Frame Time (Epoch)", "Time")
        )
        previous_time, session = self.state.get(key, (None, 0))
        if (
            timestamp is not None
            and previous_time is not None
            and (timestamp < previous_time or timestamp - previous_time > self.gap_seconds)
        ):
            session += 1
        self.state[key] = (timestamp if timestamp is not None else previous_time, session)
        return stable_hash(
            ("LSNM2024", self.member, endpoint_a, endpoint_b, protocol, str(session))
        )


def cicddos_group(
    member: str, row: list[str], columns: dict[str, int]
) -> str | None:
    source = row_value(row, columns, "Source IP")
    destination = row_value(row, columns, "Destination IP")
    protocol = row_value(row, columns, "Protocol")
    if not source or not destination or not protocol:
        return None
    endpoint_a, endpoint_b = endpoint_pair(
        source,
        row_value(row, columns, "Source Port"),
        destination,
        row_value(row, columns, "Destination Port"),
    )
    timestamp = row_value(row, columns, "Timestamp")
    return stable_hash(
        ("CICDDoS2019", member, endpoint_a, endpoint_b, protocol, timestamp)
    )


class ExactGroupStore:
    def __init__(self, path: Path) -> None:
        self.connection = sqlite3.connect(path)
        self.connection.execute("PRAGMA journal_mode=OFF")
        self.connection.execute("PRAGMA synchronous=OFF")
        self.connection.execute("PRAGMA temp_store=FILE")
        self.connection.execute(
            """
            CREATE TABLE groups (
                group_hash TEXT PRIMARY KEY,
                first_label TEXT NOT NULL,
                rows INTEGER NOT NULL,
                conflict INTEGER NOT NULL
            ) WITHOUT ROWID
            """
        )

    def add_many(self, rows: list[tuple[str, str]]) -> None:
        self.connection.executemany(
            """
            INSERT INTO groups(group_hash, first_label, rows, conflict)
            VALUES (?, ?, 1, 0)
            ON CONFLICT(group_hash) DO UPDATE SET
              rows = rows + 1,
              conflict = MAX(conflict, first_label <> excluded.first_label)
            """,
            rows,
        )
        self.connection.commit()

    def summary(self) -> dict[str, Any]:
        group_counts = {
            str(label): int(count)
            for label, count in self.connection.execute(
                "SELECT first_label, COUNT(*) FROM groups GROUP BY first_label"
            )
        }
        total_groups, duplicate_groups, cross_label_groups = self.connection.execute(
            """
            SELECT COUNT(*),
                   COALESCE(SUM(CASE WHEN rows > 1 THEN 1 ELSE 0 END), 0),
                   COALESCE(SUM(conflict), 0)
            FROM groups
            """
        ).fetchone()
        return {
            "groups": int(total_groups),
            "duplicate_groups": int(duplicate_groups),
            "cross_label_groups": int(cross_label_groups),
            "groups_by_first_label": group_counts,
        }

    def close(self) -> None:
        self.connection.close()


def lsnm_path_label(member: str) -> str:
    parts = Path(member).parts
    if "Benign" in parts:
        return "normal"
    if "Malicious" not in parts:
        raise ValueError(f"LSNM member is outside Benign/Malicious: {member}")
    index = parts.index("Malicious")
    if index + 1 >= len(parts):
        raise ValueError(f"LSNM malicious member has no family: {member}")
    return parts[index + 1]


def scan_member(
    *,
    dataset: str,
    archive: zipfile.ZipFile,
    info: zipfile.ZipInfo,
    sqlite_path: Path,
    batch_size: int = 50_000,
) -> dict[str, Any]:
    store = ExactGroupStore(sqlite_path)
    label_counts: Counter[str] = Counter()
    explicit_labels: Counter[str] = Counter()
    malformed_rows = 0
    missing_group_rows = 0
    rows = 0
    try:
        with archive.open(info) as raw:
            text = io.TextIOWrapper(
                raw, encoding="utf-8-sig", errors="replace", newline=""
            )
            reader = csv.reader(text)
            raw_header = next(reader, [])
            header = [normalized_header(value) for value in raw_header]
            columns = {name: index for index, name in enumerate(header)}
            if len(columns) != len(header):
                raise ValueError(f"duplicate normalized headers in {info.filename}")
            sessionizer = LsnmSessionizer(info.filename) if dataset == "LSNM2024" else None
            batch: list[tuple[str, str]] = []
            for row in reader:
                if not row:
                    continue
                rows += 1
                if len(row) != len(header):
                    malformed_rows += 1
                if dataset == "LSNM2024":
                    label = lsnm_path_label(info.filename)
                    explicit = row_value(row, columns, "label")
                    group = sessionizer.group(row, columns) if sessionizer else None
                else:
                    label = row_value(row, columns, "Label")
                    explicit = label
                    group = cicddos_group(info.filename, row, columns)
                if not label:
                    label = "__MISSING_LABEL__"
                label_counts[label] += 1
                if explicit:
                    explicit_labels[explicit] += 1
                if group is None:
                    missing_group_rows += 1
                    continue
                batch.append((group, label))
                if len(batch) >= batch_size:
                    store.add_many(batch)
                    batch.clear()
            if batch:
                store.add_many(batch)
        return {
            "schema_version": MEMBER_SCAN_SCHEMA,
            "member": info.filename,
            "member_crc32": f"{info.CRC:08x}",
            "member_uncompressed_size": info.file_size,
            "header": header,
            "rows": rows,
            "malformed_rows": malformed_rows,
            "missing_group_rows": missing_group_rows,
            "label_counts": dict(sorted(label_counts.items())),
            "explicit_label_counts": dict(sorted(explicit_labels.items())),
            "group_summary": store.summary(),
        }
    finally:
        store.close()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def unlink_if_present(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def member_result_path(work_dir: Path, dataset: str, archive: Path, member: str) -> Path:
    key = stable_hash((str(archive), member))[:24]
    return work_dir / dataset / f"{key}.json"


def scan_archive(
    *, dataset: str, archive_path: Path, work_dir: Path
) -> list[dict[str, Any]]:
    destination = work_dir / dataset
    destination.mkdir(parents=True, exist_ok=True)
    results = []
    with zipfile.ZipFile(archive_path) as archive:
        members = sorted(
            (
                info
                for info in archive.infolist()
                if not info.is_dir() and info.filename.lower().endswith(".csv")
            ),
            key=lambda item: item.filename,
        )
        for info in members:
            result_path = member_result_path(
                work_dir, dataset, archive_path, info.filename
            )
            if result_path.is_file():
                cached = json.loads(result_path.read_text(encoding="utf-8"))
                if (
                    cached.get("schema_version") == MEMBER_SCAN_SCHEMA
                    and cached.get("member_crc32") == f"{info.CRC:08x}"
                    and cached.get("member_uncompressed_size") == info.file_size
                ):
                    results.append(cached)
                    continue
            sqlite_path = result_path.with_suffix(".sqlite")
            unlink_if_present(sqlite_path)
            result = scan_member(
                dataset=dataset,
                archive=archive,
                info=info,
                sqlite_path=sqlite_path,
            )
            unlink_if_present(sqlite_path)
            atomic_json(result_path, result)
            results.append(result)
    return results


def aggregate_dataset(
    dataset: str,
    members: list[dict[str, Any]],
    expected_families: list[str],
    required_features: list[str],
) -> dict[str, Any]:
    labels: Counter[str] = Counter()
    groups: Counter[str] = Counter()
    missing_features: dict[str, list[str]] = {}
    cross_label_groups = 0
    rows = 0
    malformed_rows = 0
    missing_group_rows = 0
    for member in members:
        rows += int(member["rows"])
        malformed_rows += int(member["malformed_rows"])
        missing_group_rows += int(member["missing_group_rows"])
        labels.update(member["label_counts"])
        groups.update(member["group_summary"]["groups_by_first_label"])
        cross_label_groups += int(member["group_summary"]["cross_label_groups"])
        header = set(member["header"])
        missing = sorted(set(required_features) - header)
        if missing:
            missing_features[member["member"]] = missing
    expected = set(expected_families)
    observed_attacks = set(labels) - {"normal", "BENIGN", "Benign", "benign"}
    checks = {
        "has_rows": rows > 0,
        "has_benign": bool(set(labels) & {"normal", "BENIGN", "Benign", "benign"}),
        "all_expected_attack_families_observed": expected <= observed_attacks,
        "no_unexpected_attack_labels": observed_attacks <= expected,
        "no_missing_labels": "__MISSING_LABEL__" not in labels,
        "minimum_three_groups_per_label": bool(groups)
        and min(groups.values(), default=0) >= 3,
        "zero_cross_label_groups": cross_label_groups == 0,
        "zero_missing_group_rows": missing_group_rows == 0,
        "required_features_present_in_every_member": not missing_features,
    }
    return {
        "dataset": dataset,
        "member_count": len(members),
        "rows": rows,
        "malformed_rows": malformed_rows,
        "missing_group_rows": missing_group_rows,
        "label_counts": dict(sorted(labels.items())),
        "groups_by_label": dict(sorted(groups.items())),
        "cross_label_groups": cross_label_groups,
        "missing_features_by_member": missing_features,
        "checks": checks,
        "admission_passed": all(checks.values()),
    }


def build_audit(
    protocol: dict[str, Any],
    lsnm_config: dict[str, Any],
    cic_config: dict[str, Any],
    work_dir: Path,
    include_full_source_hashes: bool = True,
) -> dict[str, Any]:
    if protocol.get("status") != "frozen_before_full_scan_and_training":
        raise ValueError("dataset expansion protocol is not frozen")
    identities = protocol["source_identity"]
    for identity in identities:
        actual = central_directory_identity(Path(identity["path"]))
        if actual != identity:
            raise ValueError(f"source identity changed: {identity['path']}")
    lsnm_paths = [Path(item["path"]) for item in identities if "LSNM2024" in item["path"]]
    ddos_paths = [Path(item["path"]) for item in identities if "CICDDoS2019" in item["path"]]
    if len(lsnm_paths) != 1 or len(ddos_paths) != 2:
        raise ValueError("protocol must bind one LSNM and two CICDDoS archives")
    lsnm_members = scan_archive(
        dataset="LSNM2024", archive_path=lsnm_paths[0], work_dir=work_dir
    )
    ddos_members = [
        member
        for path in ddos_paths
        for member in scan_archive(
            dataset="CICDDoS2019", archive_path=path, work_dir=work_dir
        )
    ]
    lsnm_source_features = [
        feature
        for features in lsnm_config["modalities"].values()
        for feature in features
        if feature
        not in {
            "Packet Time Delta",
            "Has HTTP Method",
            "Has HTTP URI",
            "Has HTTP Host",
            "Has HTTP Cookie",
            "Has DNS Query",
        }
    ]
    cic_features = [
        feature
        for features in cic_config["modalities"].values()
        for feature in features
    ]
    datasets = {
        "LSNM2024": aggregate_dataset(
            "LSNM2024",
            lsnm_members,
            protocol["datasets"]["LSNM2024"]["families"],
            lsnm_source_features,
        ),
        "CICDDoS2019": aggregate_dataset(
            "CICDDoS2019",
            ddos_members,
            protocol["datasets"]["CICDDoS2019"]["families"],
            cic_features,
        ),
    }
    source_hashes = (
        {str(path): sha256_file(path) for path in lsnm_paths + ddos_paths}
        if include_full_source_hashes
        else {}
    )
    checks = {
        "protocol_sources_unchanged": True,
        "full_source_sha256_recorded": len(source_hashes) == 3,
        "lsnm_admission_passed": datasets["LSNM2024"]["admission_passed"],
        "cicddos_admission_passed": datasets["CICDDoS2019"]["admission_passed"],
    }
    return {
        "schema_version": "gpu_malicious_dataset_full_admission_audit_v1",
        "status": "complete",
        "formal_selection_evidence": False,
        "protocol_schema": protocol["schema_version"],
        "source_sha256": source_hashes,
        "datasets": datasets,
        "checks": checks,
        "admission_passed": all(checks.values()),
        "next_step": (
            "freeze_normalized_dataset_manifest"
            if all(checks.values())
            else "repair_schema_label_or_group_failures_before_preparation"
        ),
    }


def render(audit: dict[str, Any]) -> str:
    lines = [
        "# GPU malicious-dataset full admission audit",
        "",
        f"- Admission passed: `{audit['admission_passed']}`",
        "- Scope: full streaming scan; no model training or hyperparameter selection",
        "",
        "| Dataset | Rows | Labels | Cross-label groups | Passed |",
        "|---|---:|---:|---:|---|",
    ]
    for name, dataset in audit["datasets"].items():
        lines.append(
            f"| {name} | {dataset['rows']} | {len(dataset['label_counts'])} | "
            f"{dataset['cross_label_groups']} | `{dataset['admission_passed']}` |"
        )
    lines.extend(["", f"Next: `{audit['next_step']}`", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--lsnm-config", type=Path, required=True)
    parser.add_argument("--cic-config", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--skip-full-source-sha256", action="store_true")
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    lsnm_config = json.loads(args.lsnm_config.read_text(encoding="utf-8"))
    cic_config = json.loads(args.cic_config.read_text(encoding="utf-8"))
    audit = build_audit(
        protocol,
        lsnm_config,
        cic_config,
        args.work_dir,
        include_full_source_hashes=not args.skip_full_source_sha256,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    atomic_json(args.output_dir / "admission_audit.json", audit)
    (args.output_dir / "admission_audit.md").write_text(
        render(audit), encoding="utf-8"
    )
    (args.output_dir / "audit_complete").touch()
    if audit["admission_passed"]:
        (args.output_dir / "admission_passed").touch()
    print(render(audit), end="")


if __name__ == "__main__":
    main()
