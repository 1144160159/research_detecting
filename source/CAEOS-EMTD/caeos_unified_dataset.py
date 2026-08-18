from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tarfile
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable


PCAP_SUFFIXES = (".pcap", ".pcapng", ".cap")
ARCHIVE_SUFFIXES = (".zip", ".rar", ".tar", ".tar.gz", ".tgz", ".tar.xz", ".txz")
UNRAR_BINARY = Path(
    os.environ.get(
        "CAEOS_UNRAR_BINARY",
        "/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/tools/"
        "unrar-rar5-r20/bin/unrar",
    )
)
CAPTURE_MAGICS = {
    b"\xd4\xc3\xb2\xa1",
    b"\xa1\xb2\xc3\xd4",
    b"\x4d\x3c\xb2\xa1",
    b"\xa1\xb2\x3c\x4d",
    b"\x0a\x0d\x0d\x0a",
}


def canonical_json_hash(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sha256_file(path: Path, chunk_bytes: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_bytes), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, value: Any) -> None:
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


def load_catalog(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        catalog = json.load(handle)
    validate_catalog(catalog)
    return catalog


def validate_catalog(catalog: dict[str, Any]) -> None:
    if catalog.get("schema_version") not in {
        "caeos_unified_multimodal_catalog_v1",
        "caeos_unified_multimodal_catalog_v5",
    }:
        raise ValueError("unsupported unified dataset catalog schema")
    datasets = catalog.get("datasets")
    if not isinstance(datasets, list) or not datasets:
        raise ValueError("catalog datasets must be a non-empty list")
    identifiers = [str(item.get("id", "")) for item in datasets]
    if any(not identifier for identifier in identifiers):
        raise ValueError("every dataset needs a non-empty id")
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("dataset ids must be unique")
    for item in datasets:
        if not item.get("source_root"):
            raise ValueError(f"{item['id']} has no source_root")
        if not item.get("include_globs"):
            raise ValueError(f"{item['id']} has no include_globs")


def is_pcap_name(name: str) -> bool:
    lowered = name.lower()
    return lowered.endswith(PCAP_SUFFIXES)


def is_archive_path(path: Path) -> bool:
    lowered = path.name.lower()
    return lowered.endswith(ARCHIVE_SUFFIXES)


def is_capture_magic(value: bytes) -> bool:
    return value[:4] in CAPTURE_MAGICS


def parse_unrar_verbose_list(output: str) -> list[dict[str, Any]]:
    records: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for raw_line in output.splitlines() + [""]:
        line = raw_line.strip()
        if not line:
            if current.get("Type") == "File" and current.get("Name"):
                records.append(current)
            current = {}
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        if key in {"Name", "Type", "Size", "Packed size", "CRC32"}:
            current[key] = value.strip()
    return [
        {
            "name": record["Name"],
            "size_bytes": int(record["Size"]),
            "compressed_size_bytes": int(record.get("Packed size", "0")),
            "crc32": record.get("CRC32", "").lower(),
            "capture_detection": "dataset_contract_all_rar_files",
        }
        for record in records
    ]


def rar_capture_members(path: Path) -> list[dict[str, Any]]:
    if not UNRAR_BINARY.is_file():
        raise FileNotFoundError(f"RAR5 decoder unavailable: {UNRAR_BINARY}")
    result = subprocess.run(
        [str(UNRAR_BINARY), "lt", "-v", str(path)],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise ValueError(f"cannot enumerate RAR capture archive: {detail[-2000:]}")
    members = parse_unrar_verbose_list(result.stdout)
    if not members:
        raise ValueError(f"RAR capture archive contains no file members: {path}")
    return members


def discover_files(dataset: dict[str, Any]) -> list[Path]:
    root = Path(dataset["source_root"])
    paths: dict[str, Path] = {}
    for pattern in dataset["include_globs"]:
        for path in root.glob(pattern):
            if path.is_file():
                resolved = path.resolve()
                paths[str(resolved)] = resolved
    return [paths[key] for key in sorted(paths)]


def archive_capture_members(path: Path) -> list[dict[str, Any]]:
    members: list[dict[str, Any]] = []
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                detection = "suffix" if is_pcap_name(info.filename) else None
                if detection is None:
                    with archive.open(info, "r") as handle:
                        if is_capture_magic(handle.read(4)):
                            detection = "magic"
                if detection is not None:
                    members.append(
                        {
                            "name": info.filename,
                            "size_bytes": int(info.file_size),
                            "compressed_size_bytes": int(info.compress_size),
                            "crc32": f"{info.CRC:08x}",
                            "capture_detection": detection,
                        }
                    )
    elif path.name.lower().endswith(".rar"):
        members.extend(rar_capture_members(path))
    elif tarfile.is_tarfile(path):
        with tarfile.open(path, "r:*") as archive:
            for info in archive.getmembers():
                if not info.isfile():
                    continue
                detection = "suffix" if is_pcap_name(info.name) else None
                if detection is None:
                    handle = archive.extractfile(info)
                    if handle is not None:
                        with handle:
                            if is_capture_magic(handle.read(4)):
                                detection = "magic"
                if detection is not None:
                    members.append(
                        {
                            "name": info.name,
                            "size_bytes": int(info.size),
                            "capture_detection": detection,
                        }
                    )
    else:
        raise ValueError(f"unsupported or invalid capture archive: {path}")
    return sorted(members, key=lambda item: item["name"])


def inspect_source(path: Path, compute_hash: bool) -> dict[str, Any]:
    stat = path.stat()
    record: dict[str, Any] = {
        "path": str(path),
        "size_bytes": int(stat.st_size),
        "mtime_ns": int(stat.st_mtime_ns),
        "kind": "archive" if is_archive_path(path) else "pcap",
    }
    if compute_hash:
        record["sha256"] = sha256_file(path)
    if record["kind"] == "archive":
        record["capture_members"] = archive_capture_members(path)
        record["capture_member_count"] = len(record["capture_members"])
    else:
        record["capture_member_count"] = 1 if is_pcap_name(path.name) else 0
    return record


def selected_datasets(
    catalog: dict[str, Any], dataset_ids: Iterable[str] | None
) -> list[dict[str, Any]]:
    enabled = [item for item in catalog["datasets"] if item["preprocess_enabled"]]
    if dataset_ids is None:
        return enabled
    requested = set(dataset_ids)
    available = {item["id"] for item in enabled}
    missing = sorted(requested - available)
    if missing:
        raise ValueError(f"unknown or disabled dataset ids: {missing}")
    return [item for item in enabled if item["id"] in requested]


def build_source_manifest(
    catalog: dict[str, Any],
    io_threads: int,
    dataset_ids: Iterable[str] | None = None,
    compute_hashes: bool = True,
) -> dict[str, Any]:
    if io_threads < 1:
        raise ValueError("io_threads must be positive")
    dataset_records: list[dict[str, Any]] = []
    for dataset in selected_datasets(catalog, dataset_ids):
        source_root = Path(dataset["source_root"])
        if not source_root.is_dir():
            raise FileNotFoundError(f"missing source root: {source_root}")
        paths = discover_files(dataset)
        if not paths:
            raise FileNotFoundError(f"no source files for dataset {dataset['id']}")
        source_records: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=io_threads) as executor:
            futures = {
                executor.submit(inspect_source, path, compute_hashes): path
                for path in paths
            }
            for future in as_completed(futures):
                source_records.append(future.result())
        source_records.sort(key=lambda item: item["path"])
        capture_count = sum(
            int(record["capture_member_count"]) for record in source_records
        )
        dataset_records.append(
            {
                "id": dataset["id"],
                "priority": dataset["priority"],
                "role": dataset["role"],
                "source_root": str(source_root.resolve()),
                "source_kind": dataset["source_kind"],
                "label_policy": dataset["label_policy"],
                "label_binding": dataset["label_binding"],
                "source_file_count": len(source_records),
                "capture_count": capture_count,
                "source_size_bytes": sum(
                    int(record["size_bytes"]) for record in source_records
                ),
                "source_files": source_records,
            }
        )
    manifest: dict[str, Any] = {
        "schema_version": "caeos_unified_source_manifest_v1",
        "catalog_schema_version": catalog["schema_version"],
        "catalog_sha256": canonical_json_hash(catalog),
        "hash_algorithm": "sha256" if compute_hashes else None,
        "full_source_hashes_computed": bool(compute_hashes),
        "io_threads": io_threads,
        "datasets": dataset_records,
        "dataset_count": len(dataset_records),
        "capture_count": sum(item["capture_count"] for item in dataset_records),
        "source_size_bytes": sum(
            item["source_size_bytes"] for item in dataset_records
        ),
    }
    manifest["manifest_sha256"] = canonical_json_hash(manifest)
    return manifest


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dataset", action="append", default=None)
    parser.add_argument("--io-threads", type=int, default=16)
    parser.add_argument("--skip-hash", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    if args.output.exists():
        raise ValueError(f"refusing to overwrite source manifest: {args.output}")
    catalog = load_catalog(args.catalog)
    manifest = build_source_manifest(
        catalog,
        io_threads=args.io_threads,
        dataset_ids=args.dataset,
        compute_hashes=not args.skip_hash,
    )
    atomic_json(args.output, manifest)
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
