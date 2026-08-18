from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import tarfile
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def read_member(tar: tarfile.TarFile, name: str) -> bytes:
    handle = tar.extractfile(tar.getmember(name))
    if handle is None:
        raise ValueError(f"cannot read required CERT answer member: {name}")
    return handle.read()


def parse_cert_timestamp(value: str) -> datetime | None:
    try:
        return datetime.strptime(value, "%m/%d/%Y %H:%M:%S")
    except ValueError:
        return None


def detail_interval(
    answers: tarfile.TarFile, detail_name: str, user: str
) -> tuple[str, str] | None:
    member_name = f"answers/{detail_name}"
    timestamps: list[tuple[datetime, str]] = []
    for row in csv.reader(
        io.StringIO(read_member(answers, member_name).decode("utf-8-sig", errors="replace"))
    ):
        if len(row) < 4 or row[3].strip() != user:
            continue
        raw_timestamp = row[2].strip()
        parsed = parse_cert_timestamp(raw_timestamp)
        if parsed is not None:
            timestamps.append((parsed, raw_timestamp))
    if not timestamps:
        return None
    timestamps.sort(key=lambda item: item[0])
    return timestamps[0][1], timestamps[-1][1]


def build(args: argparse.Namespace) -> dict[str, Any]:
    with zipfile.ZipFile(args.archive) as outer:
        outer_names = outer.namelist()
        answer_bytes = outer.read("answers.tar.bz2")
        release_archives = sorted(
            name for name in outer_names if name.startswith("r") and name.endswith(".tar.bz2")
        )
    corrections: list[dict[str, str]] = []
    unresolved_timestamps: list[dict[str, str]] = []
    with tarfile.open(fileobj=io.BytesIO(answer_bytes), mode="r:bz2") as answers:
        members = [member.name for member in answers.getmembers() if member.isfile()]
        insiders_bytes = read_member(answers, "answers/insiders.csv")
        scenarios_bytes = read_member(answers, "answers/scenarios.txt")
        rows = list(
            csv.DictReader(
                io.StringIO(insiders_bytes.decode("utf-8-sig", errors="replace"))
            )
        )
        required = {"dataset", "scenario", "details", "user", "start", "end"}
        rejected = 0
        records: list[dict[str, str]] = []
        scenario_counts: Counter[str] = Counter()
        release_counts: Counter[str] = Counter()
        for ordinal, row in enumerate(rows, start=1):
            if not required.issubset(row) or any(not row[key].strip() for key in required):
                rejected += 1
                continue
            record = {key: row[key].strip() for key in sorted(required)}
            start_valid = parse_cert_timestamp(record["start"]) is not None
            end_valid = parse_cert_timestamp(record["end"]) is not None
            if not start_valid or not end_valid:
                interval = detail_interval(answers, record["details"], record["user"])
                if interval is None:
                    unresolved_timestamps.append(
                        {
                            "details": record["details"],
                            "end": record["end"],
                            "start": record["start"],
                            "user": record["user"],
                        }
                    )
                else:
                    detail_start, detail_end = interval
                    for field, valid, corrected in (
                        ("start", start_valid, detail_start),
                        ("end", end_valid, detail_end),
                    ):
                        if not valid:
                            corrections.append(
                                {
                                    "corrected": corrected,
                                    "details": record["details"],
                                    "field": field,
                                    "original": record[field],
                                    "rule": "matching-user detail CSV boundary",
                                    "user": record["user"],
                                }
                            )
                            record[field] = corrected
            record["record_id"] = hashlib.sha256(
                f"{ordinal}\0{record}".encode("utf-8")
            ).hexdigest()
            record["binary_label"] = "1"
            record["family_label"] = "InsiderThreat"
            records.append(record)
            scenario_counts[record["scenario"]] += 1
            release_counts[record["dataset"]] += 1
    payload: dict[str, Any] = {
        "schema_version": "caeos_cert_insider_label_manifest_v2",
        "dataset_id": "cert_insider_threat",
        "archive": str(args.archive),
        "archive_size_bytes": args.archive.stat().st_size,
        "answers_tar_bz2_sha256": hashlib.sha256(answer_bytes).hexdigest(),
        "scenarios_sha256": hashlib.sha256(scenarios_bytes).hexdigest(),
        "release_archives": release_archives,
        "answer_member_count": len(members),
        "answer_csv_count": sum(name.lower().endswith(".csv") for name in members),
        "malicious_interval_count": len(records),
        "rejected_insider_rows": rejected,
        "timestamp_corrections": corrections,
        "unresolved_timestamp_count": len(unresolved_timestamps),
        "unresolved_timestamps": unresolved_timestamps,
        "release_counts": dict(sorted(release_counts.items())),
        "scenario_counts": dict(sorted(scenario_counts.items())),
        "records": records,
        "label_policy": {
            "malicious": "official answers/insiders.csv user and interval plus referenced detail CSV",
            "benign": "events outside official malicious user/scenario intervals remain benign only after release-log join",
            "modality": "host_user_behavior_logs",
            "network_pcap_features": False,
        },
        "ready_for_release_log_join": (
            len(release_archives) == 10
            and len(records) > 0
            and rejected == 0
            and not unresolved_timestamps
        ),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["manifest_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    atomic_json(args.output, payload)
    return payload


def main() -> None:
    print(json.dumps(build(parse_arguments()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
