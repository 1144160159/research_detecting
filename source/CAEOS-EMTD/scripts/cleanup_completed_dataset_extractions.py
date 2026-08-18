from __future__ import annotations

import argparse
import json
import os
import shutil
import tarfile
import time
import zipfile
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


ACTIVE_DATASETS = {"ciciot2023", "cicids2018", "cic_bot_iot"}
ARCHIVE_SUFFIXES = (
    ".zip",
    ".tar",
    ".tar.gz",
    ".tgz",
    ".tar.xz",
    ".txz",
    ".tar.bz2",
    ".tbz2",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_archive(path: Path) -> bool:
    lowered = path.name.lower()
    return path.is_file() and lowered.endswith(ARCHIVE_SUFFIXES)


def normalized_member(name: str) -> PurePosixPath | None:
    clean = name.replace("\\", "/").lstrip("/")
    parts = tuple(part for part in PurePosixPath(clean).parts if part not in ("", "."))
    if not parts or ".." in parts:
        return None
    return PurePosixPath(*parts)


def archive_members(path: Path) -> Iterable[tuple[PurePosixPath, int]]:
    lowered = path.name.lower()
    if lowered.endswith(".zip"):
        with zipfile.ZipFile(path) as archive:
            for member in archive.infolist():
                if member.is_dir():
                    continue
                normalized = normalized_member(member.filename)
                if normalized is not None:
                    yield normalized, member.file_size
        return
    with tarfile.open(path, mode="r:*") as archive:
        for member in archive:
            if not member.isfile():
                continue
            normalized = normalized_member(member.name)
            if normalized is not None:
                yield normalized, member.size


def open_paths() -> set[str]:
    results: set[str] = set()
    for process in Path("/proc").iterdir():
        if not process.name.isdigit():
            continue
        try:
            descriptors = list((process / "fd").iterdir())
        except OSError:
            continue
        for descriptor in descriptors:
            try:
                target = os.readlink(descriptor).removesuffix(" (deleted)")
            except OSError:
                continue
            if target.startswith("/"):
                results.add(target)
    return results


def path_is_open(path: Path, opened: set[str]) -> bool:
    prefix = f"{path}/"
    return any(item == str(path) or item.startswith(prefix) for item in opened)


def physical_tree(path: Path, base: Path) -> tuple[dict[PurePosixPath, int], bool]:
    if path.is_file():
        return {PurePosixPath(path.relative_to(base).as_posix()): path.stat().st_size}, False
    files: dict[PurePosixPath, int] = {}
    has_symlink = False
    for root, directories, names in os.walk(path, followlinks=False):
        root_path = Path(root)
        for directory in directories:
            if (root_path / directory).is_symlink():
                has_symlink = True
        for name in names:
            item = root_path / name
            if item.is_symlink():
                has_symlink = True
                continue
            try:
                files[PurePosixPath(item.relative_to(base).as_posix())] = item.stat().st_size
            except OSError:
                has_symlink = True
    return files, has_symlink


def archive_inventory(
    dataset_id: str,
    archive: Path,
    opened: set[str],
) -> dict[str, Any]:
    base = archive.parent.resolve()
    members: dict[PurePosixPath, int] = {}
    duplicate_members = 0
    try:
        for member, size in archive_members(archive):
            if member in members and members[member] != size:
                duplicate_members += 1
            members[member] = size
    except (OSError, tarfile.TarError, zipfile.BadZipFile) as error:
        return {
            "dataset_id": dataset_id,
            "archive": str(archive),
            "archive_size_bytes": archive.stat().st_size,
            "readable": False,
            "error": f"{type(error).__name__}: {error}",
            "deletion_candidates": [],
        }

    by_top: dict[str, dict[PurePosixPath, int]] = defaultdict(dict)
    for member, size in members.items():
        by_top[member.parts[0]][member] = size

    candidates: list[dict[str, Any]] = []
    top_level: list[dict[str, Any]] = []
    for top_name, expected in sorted(by_top.items()):
        path = (base / top_name).resolve()
        exists = path.exists()
        exact = False
        symlink = False
        physical: dict[PurePosixPath, int] = {}
        if exists and path != archive.resolve():
            physical, symlink = physical_tree(path, base)
            exact = physical == expected and not symlink
        item = {
            "path": str(path),
            "exists": exists,
            "expected_file_count": len(expected),
            "expected_bytes": sum(expected.values()),
            "physical_file_count": len(physical),
            "physical_bytes": sum(physical.values()),
            "exact_archive_mirror": exact,
            "contains_symlink": symlink,
            "open_by_process": exists and path_is_open(path, opened),
        }
        top_level.append(item)
        if exact and not item["open_by_process"]:
            candidates.append(item)

    return {
        "dataset_id": dataset_id,
        "archive": str(archive),
        "archive_size_bytes": archive.stat().st_size,
        "readable": True,
        "member_file_count": len(members),
        "member_bytes": sum(members.values()),
        "duplicate_member_conflicts": duplicate_members,
        "top_level": top_level,
        "deletion_candidates": candidates,
    }


def completed_datasets(catalog: dict[str, Any], output_root: Path) -> list[dict[str, Any]]:
    results = []
    for dataset in catalog["datasets"]:
        dataset_id = dataset["id"]
        if dataset_id in ACTIVE_DATASETS:
            continue
        manifest_path = output_root / dataset_id / "dataset.manifest.json"
        if not manifest_path.is_file():
            continue
        try:
            manifest = load_json(manifest_path)
        except (OSError, json.JSONDecodeError):
            continue
        if manifest.get("complete") is True:
            results.append(dataset)
    return results


def delete_candidates(
    inventories: list[dict[str, Any]],
    allowed_roots: set[Path],
) -> list[dict[str, Any]]:
    deleted = []
    seen: set[Path] = set()
    for inventory in inventories:
        archive = Path(inventory["archive"]).resolve()
        if not archive.is_file():
            continue
        for candidate in inventory["deletion_candidates"]:
            path = Path(candidate["path"]).resolve()
            if path in seen or path == archive or not path.exists():
                continue
            if not any(path == root or root in path.parents for root in allowed_roots):
                continue
            refreshed = archive_inventory(inventory["dataset_id"], archive, open_paths())
            matching = {
                Path(item["path"]).resolve(): item
                for item in refreshed.get("deletion_candidates", [])
            }
            if path not in matching:
                continue
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            deleted.append(
                {
                    "dataset_id": inventory["dataset_id"],
                    "archive": str(archive),
                    **matching[path],
                }
            )
            seen.add(path)
    return deleted


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--metadata-only", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--audit-output", type=Path)
    args = parser.parse_args()
    if args.metadata_only and args.apply:
        parser.error("--metadata-only cannot be combined with --apply")

    catalog = load_json(args.catalog)
    output_root = Path(catalog["remote_output_root"])
    datasets = completed_datasets(catalog, output_root)
    opened = open_paths()
    inventories = []
    allowed_roots: set[Path] = set()
    for dataset in datasets:
        dataset_id = dataset["id"]
        label_root = Path(dataset["label_search_root"]).resolve()
        source_root = Path(dataset["source_root"]).resolve()
        allowed_roots.update((label_root, source_root))
        if not label_root.is_dir():
            continue
        for root, directories, names in os.walk(label_root, followlinks=False):
            root_path = Path(root)
            for name in names:
                archive = root_path / name
                if is_archive(archive):
                    if args.metadata_only:
                        inventories.append(
                            {
                                "dataset_id": dataset_id,
                                "archive": str(archive),
                                "archive_size_bytes": archive.stat().st_size,
                                "readable": None,
                                "metadata_only": True,
                                "deletion_candidates": [],
                            }
                        )
                    else:
                        inventories.append(
                            archive_inventory(dataset_id, archive, opened)
                        )

    deleted = []
    if args.apply:
        deleted = delete_candidates(inventories, allowed_roots)

    disk = shutil.disk_usage(output_root)
    report = {
        "schema_version": "caeos_completed_dataset_extraction_cleanup_v1",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "active_datasets_excluded": sorted(ACTIVE_DATASETS),
        "completed_datasets_scanned": [item["id"] for item in datasets],
        "archive_count": len(inventories),
        "archives": inventories,
        "candidate_count": sum(len(item["deletion_candidates"]) for item in inventories),
        "candidate_bytes": sum(
            candidate["physical_bytes"]
            for item in inventories
            for candidate in item["deletion_candidates"]
        ),
        "deleted_count": len(deleted),
        "deleted_bytes": sum(item["physical_bytes"] for item in deleted),
        "deleted": deleted,
        "disk_free_bytes": disk.free,
        "archives_deleted": False,
        "caeos_feature_outputs_deleted": False,
    }
    rendered = json.dumps(report, ensure_ascii=False, sort_keys=True)
    if args.audit_output:
        args.audit_output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.audit_output.with_suffix(args.audit_output.suffix + ".tmp")
        temporary.write_text(rendered + "\n", encoding="utf-8")
        os.replace(temporary, args.audit_output)
    print(rendered)


if __name__ == "__main__":
    main()
