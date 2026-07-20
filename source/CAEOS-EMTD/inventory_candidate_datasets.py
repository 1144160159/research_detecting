from __future__ import annotations

import argparse
import csv
import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path
from typing import Iterable


TABULAR_SUFFIXES = {".csv", ".binetflow", ".tsv"}
ARCHIVE_SUFFIXES = {".zip", ".rar", ".7z", ".tar", ".gz"}
PACKET_SUFFIXES = {".pcap", ".pcapng"}
LABEL_COLUMN_PRIORITY = (
    "attack",
    "attack_type",
    "sublabelcat",
    "sub_label_cat",
    "sublabel",
    "sub_label",
    "subcategory",
    "category",
    "label",
    "class",
    "traffic_type",
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read-only inventory of candidate traffic datasets"
    )
    parser.add_argument(
        "--dataset",
        action="append",
        required=True,
        metavar="NAME=PATH",
        help="Candidate name and root directory; repeat for multiple datasets",
    )
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--max-tabular-files", type=int, default=200)
    parser.add_argument("--sample-rows-per-file", type=int, default=5000)
    parser.add_argument("--archive-member-limit", type=int, default=20000)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def parse_dataset(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise ValueError(f"dataset must use NAME=PATH syntax: {value!r}")
    name, raw_path = value.split("=", 1)
    name = name.strip()
    path = Path(raw_path).expanduser()
    if not name:
        raise ValueError(f"dataset name is empty: {value!r}")
    if not path.is_dir():
        raise ValueError(f"dataset root is not a directory: {path}")
    return name, path.resolve()


def normalized_column(value: str) -> str:
    return "_".join(value.strip().lower().replace("-", "_").split())


def select_label_column(fieldnames: Iterable[str]) -> str | None:
    indexed = {normalized_column(value): value for value in fieldnames}
    for candidate in LABEL_COLUMN_PRIORITY:
        if candidate in indexed:
            return indexed[candidate]
    return None


def depth_from(root: Path, path: Path) -> int:
    return len(path.relative_to(root).parts)


def iter_files(root: Path, max_depth: int) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file() and depth_from(root, path) <= max_depth:
            yield path


def sniff_dialect(path: Path) -> csv.Dialect:
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        sample = handle.read(64 * 1024)
    if not sample:
        return csv.excel
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        return csv.excel_tab if path.suffix.lower() == ".tsv" else csv.excel


def profile_tabular(path: Path, root: Path, sample_rows: int) -> dict[str, object]:
    result: dict[str, object] = {
        "path": str(path.relative_to(root)),
        "size_bytes": path.stat().st_size,
    }
    try:
        dialect = sniff_dialect(path)
        with path.open(
            "r", encoding="utf-8-sig", errors="replace", newline=""
        ) as handle:
            reader = csv.DictReader(handle, dialect=dialect)
            fieldnames = [str(value) for value in (reader.fieldnames or [])]
            exact_column_counts = Counter(fieldnames)
            normalized_column_counts = Counter(
                normalized_column(value) for value in fieldnames
            )
            duplicate_columns = {
                value: count
                for value, count in sorted(exact_column_counts.items())
                if count > 1
            }
            normalized_duplicate_columns = {
                value: count
                for value, count in sorted(normalized_column_counts.items())
                if count > 1
            }
            result["delimiter"] = dialect.delimiter
            result["column_count"] = len(fieldnames)
            result["columns"] = fieldnames
            result["duplicate_columns"] = duplicate_columns
            result["normalized_duplicate_columns"] = normalized_duplicate_columns
            result["header_sha256"] = hashlib.sha256(
                json.dumps(fieldnames, ensure_ascii=False, separators=(",", ":")).encode(
                    "utf-8"
                )
            ).hexdigest()
            label_column = select_label_column(fieldnames)
            result["label_column"] = label_column
            result["label_column_ambiguous"] = bool(
                label_column is not None and exact_column_counts[label_column] > 1
            )
            label_counts: Counter[str] = Counter()
            rows_sampled = 0
            for row in reader:
                rows_sampled += 1
                if label_column is not None:
                    raw_label = row.get(label_column)
                    label = "<MISSING>" if raw_label is None else str(raw_label).strip()
                    label_counts[label or "<EMPTY>"] += 1
                if rows_sampled >= sample_rows:
                    break
            result["rows_sampled"] = rows_sampled
            result["sample_label_counts"] = dict(
                sorted(label_counts.items(), key=lambda item: (-item[1], item[0]))
            )
    except (OSError, csv.Error, UnicodeError) as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def profile_zip(path: Path, root: Path, member_limit: int) -> dict[str, object]:
    result: dict[str, object] = {
        "path": str(path.relative_to(root)),
        "size_bytes": path.stat().st_size,
    }
    try:
        with zipfile.ZipFile(path) as archive:
            members = archive.infolist()
            inspected = members[:member_limit]
            suffix_counts = Counter(
                Path(member.filename).suffix.lower() or "<none>" for member in inspected
            )
            result.update(
                {
                    "member_count": len(members),
                    "members_inspected": len(inspected),
                    "uncompressed_size_bytes": sum(member.file_size for member in members),
                    "member_suffix_counts": dict(sorted(suffix_counts.items())),
                    "sample_members": [member.filename for member in inspected[:50]],
                }
            )
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def inventory_dataset(
    name: str,
    root: Path,
    max_depth: int,
    max_tabular_files: int,
    sample_rows: int,
    archive_member_limit: int,
) -> dict[str, object]:
    files = sorted(iter_files(root, max_depth), key=lambda path: str(path).lower())
    suffix_counts = Counter(path.suffix.lower() or "<none>" for path in files)
    total_bytes = sum(path.stat().st_size for path in files)
    tabular_paths = [path for path in files if path.suffix.lower() in TABULAR_SUFFIXES]
    tabular_profiles = [
        profile_tabular(path, root, sample_rows)
        for path in tabular_paths[:max_tabular_files]
    ]
    zip_profiles = [
        profile_zip(path, root, archive_member_limit)
        for path in files
        if path.suffix.lower() == ".zip"
    ]
    header_counts = Counter(
        str(profile["header_sha256"])
        for profile in tabular_profiles
        if "header_sha256" in profile
    )
    label_columns = Counter(
        str(profile["label_column"])
        for profile in tabular_profiles
        if profile.get("label_column") is not None
    )
    parent_counts = Counter(path.parent.name for path in tabular_paths)
    return {
        "name": name,
        "root": str(root),
        "state": "inventoried",
        "file_count": len(files),
        "total_bytes_within_depth": total_bytes,
        "suffix_counts": dict(sorted(suffix_counts.items())),
        "packet_capture_count": sum(
            count for suffix, count in suffix_counts.items() if suffix in PACKET_SUFFIXES
        ),
        "archive_count": sum(
            count for suffix, count in suffix_counts.items() if suffix in ARCHIVE_SUFFIXES
        ),
        "tabular_file_count": len(tabular_paths),
        "tabular_files_profiled": len(tabular_profiles),
        "tabular_files_truncated": len(tabular_paths) > max_tabular_files,
        "header_signature_counts": dict(sorted(header_counts.items())),
        "detected_label_columns": dict(sorted(label_columns.items())),
        "tabular_parent_counts": dict(
            sorted(parent_counts.items(), key=lambda item: (-item[1], item[0]))
        ),
        "tabular_profiles": tabular_profiles,
        "zip_profiles": zip_profiles,
    }


def main() -> None:
    args = parse_arguments()
    datasets = [parse_dataset(value) for value in args.dataset]
    report = {
        "schema_version": "1.0",
        "read_only": True,
        "sampling_contract": {
            "max_depth": args.max_depth,
            "max_tabular_files": args.max_tabular_files,
            "sample_rows_per_file": args.sample_rows_per_file,
            "archive_member_limit": args.archive_member_limit,
            "sample_label_counts_are_not_full_dataset_counts": True,
        },
        "datasets": [
            inventory_dataset(
                name,
                root,
                args.max_depth,
                args.max_tabular_files,
                args.sample_rows_per_file,
                args.archive_member_limit,
            )
            for name, root in datasets
        ],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
