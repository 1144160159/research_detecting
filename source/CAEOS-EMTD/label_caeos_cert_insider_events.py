from __future__ import annotations

import argparse
import bz2
import csv
import gzip
import io
import json
import os
import re
import tarfile
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


TIMESTAMP_FORMAT = "%m/%d/%Y %H:%M:%S"
LABEL_COLUMNS = (
    "caeos_binary_label",
    "caeos_fine_label",
    "caeos_family_label",
    "caeos_scenario",
    "caeos_label_record_id",
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--label-manifest", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--checkpoint", required=True, type=Path)
    return parser.parse_args()


def normalized_header(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.strip().lower())


def timestamp(value: str) -> datetime | None:
    try:
        return datetime.strptime(value.strip(), TIMESTAMP_FORMAT)
    except ValueError:
        return None


def safe_member_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "__", name.strip("/"))


def main() -> None:
    args = arguments()
    manifest = json.loads(args.label_manifest.read_text(encoding="utf-8"))
    if not manifest.get("ready_for_release_log_join"):
        raise ValueError("CERT label manifest did not pass its intake gate")

    intervals: dict[tuple[str, str], list[tuple[datetime, datetime, dict[str, str]]]] = defaultdict(list)
    for record in manifest["records"]:
        start = timestamp(record["start"])
        end = timestamp(record["end"])
        if start is None or end is None or end < start:
            raise ValueError(f"invalid certified interval: {record}")
        release = "r" + record["dataset"]
        intervals[(release, record["user"])].append((start, end, record))

    checkpoint: dict[str, Any] = {
        "schema_version": "caeos_cert_insider_event_join_v1",
        "dataset_id": "cert_insider_threat",
        "manifest_sha256": manifest["manifest_sha256"],
        "state": "running",
        "members": {},
    }
    if args.checkpoint.exists():
        previous = json.loads(args.checkpoint.read_text(encoding="utf-8"))
        if previous.get("manifest_sha256") == manifest["manifest_sha256"]:
            checkpoint = previous
            checkpoint["state"] = "running"

    args.output_root.mkdir(parents=True, exist_ok=True)
    atomic_json(args.checkpoint, checkpoint)

    with zipfile.ZipFile(args.archive) as outer:
        for release_archive in manifest["release_archives"]:
            release = release_archive.removesuffix(".tar.bz2")
            release_root = args.output_root / release
            release_root.mkdir(parents=True, exist_ok=True)
            with outer.open(release_archive) as compressed:
                # Decompress outside tarfile.  Python 3.9 tarfile's internal
                # streaming bzip2 reader can raise EOFError after an exactly
                # consumed large member when its source is a ZipExtFile.
                with bz2.BZ2File(compressed, mode="rb") as decompressed:
                    with tarfile.open(fileobj=decompressed, mode="r|") as inner:
                        for member in inner:
                            if not member.isfile() or not member.name.lower().endswith(".csv"):
                                continue
                            key = f"{release_archive}:{member.name}"
                            final_path = release_root / (safe_member_name(member.name) + ".labeled.csv.gz")
                            prior = checkpoint["members"].get(key)
                            if prior and prior.get("state") == "complete" and final_path.is_file():
                                continue
                            source = inner.extractfile(member)
                            if source is None:
                                raise ValueError(f"cannot stream CERT member: {key}")
                            reader = csv.DictReader(
                                (
                                    line.decode("utf-8-sig", errors="replace")
                                    for line in source
                                )
                            )
                            fields = reader.fieldnames or []
                            normalized = {normalized_header(field): field for field in fields}
                            date_field = normalized.get("date") or normalized.get("timestamp") or normalized.get("datetime")
                            user_field = normalized.get("user")
                            if not date_field or not user_field:
                                checkpoint["members"][key] = {
                                    "state": "skipped_non_event_table",
                                    "reason": "missing user or timestamp column",
                                }
                                atomic_json(args.checkpoint, checkpoint)
                                continue

                            partial = final_path.with_suffix(final_path.suffix + ".partial")
                            counts: Counter[str] = Counter()
                            with gzip.open(partial, "wt", encoding="utf-8", newline="", compresslevel=1) as output:
                                writer = csv.DictWriter(output, fieldnames=[*fields, *LABEL_COLUMNS])
                                writer.writeheader()
                                for row in reader:
                                    counts["rows"] += 1
                                    when = timestamp(row.get(date_field, ""))
                                    user = row.get(user_field, "").strip()
                                    matches = []
                                    if when is not None and user:
                                        matches = [
                                            record
                                            for start, end, record in intervals.get((release, user), [])
                                            if start <= when <= end
                                        ]
                                    if len(matches) > 1:
                                        counts["ambiguous_rows"] += 1
                                    if when is None or not user:
                                        row.update(
                                            {
                                                "caeos_binary_label": "",
                                                "caeos_fine_label": "Unresolved",
                                                "caeos_family_label": "Unresolved",
                                                "caeos_scenario": "",
                                                "caeos_label_record_id": "",
                                            }
                                        )
                                        counts["unresolved_rows"] += 1
                                    elif matches:
                                        selected = sorted(matches, key=lambda item: item["record_id"])[0]
                                        row.update(
                                            {
                                                "caeos_binary_label": "1",
                                                "caeos_fine_label": f"InsiderThreat_Scenario_{selected['scenario']}",
                                                "caeos_family_label": "InsiderThreat",
                                                "caeos_scenario": selected["scenario"],
                                                "caeos_label_record_id": selected["record_id"],
                                            }
                                        )
                                        counts["malicious_rows"] += 1
                                    else:
                                        row.update(
                                            {
                                                "caeos_binary_label": "0",
                                                "caeos_fine_label": "Benign",
                                                "caeos_family_label": "Benign",
                                                "caeos_scenario": "",
                                                "caeos_label_record_id": "",
                                            }
                                        )
                                        counts["benign_rows"] += 1
                                    writer.writerow(row)
                            os.replace(partial, final_path)
                            checkpoint["members"][key] = {
                                "state": "complete",
                                "output": str(final_path),
                                **dict(counts),
                            }
                            atomic_json(args.checkpoint, checkpoint)

    totals: Counter[str] = Counter()
    states: Counter[str] = Counter()
    for result in checkpoint["members"].values():
        states[result["state"]] += 1
        if result["state"] == "complete":
            for name in ("rows", "malicious_rows", "benign_rows", "ambiguous_rows", "unresolved_rows"):
                totals[name] += int(result.get(name, 0))
    checkpoint["member_state_counts"] = dict(states)
    checkpoint["totals"] = dict(totals)
    checkpoint["state"] = "complete" if states.get("complete", 0) else "failed_no_event_tables"
    atomic_json(args.checkpoint, checkpoint)
    if (
        checkpoint["state"] != "complete"
        or totals.get("ambiguous_rows", 0)
        or totals.get("unresolved_rows", 0)
    ):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
