from __future__ import annotations

import argparse
import json
import os
import shutil
import time
from pathlib import Path
from typing import Any


DATASET_IDS = (
    "ciciot2022",
    "edge_iiotset",
    "cicids2017",
    "cic_ton_iot",
    "cicddos2019",
    "unsw_nb15",
    "5gad_2022",
    "dohbrw2020",
    "ciciot2023",
    "cicids2018",
    "cic_bot_iot",
)


def last_capture_event(path: str) -> dict[str, Any] | None:
    try:
        with Path(path).open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            position = handle.tell()
            pending = b""
            while position > 0:
                size = min(64 * 1024, position)
                position -= size
                handle.seek(position)
                pending = handle.read(size) + pending
                lines = pending.splitlines()
                if position > 0 and lines:
                    pending = lines.pop(0)
                for raw in reversed(lines):
                    try:
                        item = json.loads(raw.decode("utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        continue
                    if item.get("event") == "capture_complete":
                        return item
        return None
    except OSError as error:
        return {"error": f"{type(error).__name__}: {error}"}


def tree_size(path: Path) -> int:
    total = 0
    stack = [path]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as entries:
                for entry in entries:
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(Path(entry.path))
                        elif entry.is_file(follow_symlinks=False):
                            total += entry.stat(follow_symlinks=False).st_size
                    except OSError:
                        continue
        except OSError:
            continue
    return total


def live_state(output_root: Path) -> tuple[dict[str, Any], set[str]]:
    active: dict[str, Any] = {}
    open_paths: set[str] = set()
    for process in Path("/proc").iterdir():
        if not process.name.isdigit():
            continue
        try:
            arguments = [
                value.decode("utf-8", "replace")
                for value in (process / "cmdline").read_bytes().split(b"\0")
                if value
            ]
            if (
                "prepare_caeos_splitpcap_class_csv.py" in arguments
                and "--dataset" in arguments
            ):
                dataset_id = arguments[arguments.index("--dataset") + 1]
                pid = int(process.name)
                if os.getpgid(pid) == pid:
                    log_path = os.readlink(process / "fd" / "1")
                    active[dataset_id] = {
                        "pid": pid,
                        "pgid": os.getpgid(pid),
                        "log_path": log_path,
                        "last_capture": last_capture_event(log_path),
                    }
        except (OSError, ValueError):
            pass
        try:
            for descriptor in (process / "fd").iterdir():
                try:
                    target = os.readlink(descriptor).removesuffix(" (deleted)")
                    if target.startswith(str(output_root)):
                        open_paths.add(target)
                except OSError:
                    continue
        except OSError:
            continue
    return active, open_paths


def manifest_state(output_root: Path) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for dataset_id in DATASET_IDS:
        path = output_root / dataset_id / "dataset.manifest.json"
        if not path.is_file():
            results[dataset_id] = {"complete": False, "path": str(path)}
            continue
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
            results[dataset_id] = {
                "complete": bool(manifest.get("complete")),
                "row_count": manifest.get("row_count"),
                "class_csv_count": len(manifest.get("class_csvs", [])),
                "manifest_sha256": manifest.get("manifest_sha256"),
                "path": str(path),
            }
        except (OSError, json.JSONDecodeError) as error:
            results[dataset_id] = {
                "complete": False,
                "path": str(path),
                "error": f"{type(error).__name__}: {error}",
            }
    return results


def marker_complete(path: Path) -> bool:
    try:
        return bool(json.loads(path.read_text(encoding="utf-8")).get("complete"))
    except (OSError, json.JSONDecodeError):
        return False


def path_is_open(path: Path, open_paths: set[str]) -> bool:
    prefix = f"{path}/"
    return any(item == str(path) or item.startswith(prefix) for item in open_paths)


def cleanup_candidates(
    output_root: Path, open_paths: set[str], minimum_age_seconds: int
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    now = time.time()
    split_root = output_root / "_split_work"
    if split_root.is_dir():
        for dataset_dir in split_root.iterdir():
            if not dataset_dir.is_dir():
                continue
            for capture_dir in dataset_dir.iterdir():
                if not capture_dir.is_dir():
                    continue
                if path_is_open(capture_dir, open_paths):
                    continue
                marker = (
                    output_root
                    / "_captures"
                    / dataset_dir.name
                    / f"{capture_dir.name}.json"
                )
                age_seconds = int(max(0.0, now - capture_dir.stat().st_mtime))
                if marker_complete(marker) and age_seconds >= minimum_age_seconds:
                    candidates.append(
                        {
                            "kind": "completed_capture_split_work",
                            "path": str(capture_dir),
                            "dataset_id": dataset_dir.name,
                            "capture_id": capture_dir.name,
                            "size_bytes": tree_size(capture_dir),
                            "age_seconds": age_seconds,
                            "marker_path": str(marker),
                            "marker_complete": True,
                            "open_by_process": False,
                        }
                    )
    archive_root = output_root / "_archive_work"
    if archive_root.is_dir():
        for dataset_dir in archive_root.iterdir():
            if not dataset_dir.is_dir():
                continue
            for item in dataset_dir.iterdir():
                if not item.is_file() or str(item) in open_paths:
                    continue
                capture_id = item.name.split(".", maxsplit=1)[0]
                marker = (
                    output_root
                    / "_captures"
                    / dataset_dir.name
                    / f"{capture_id}.json"
                )
                age_seconds = int(max(0.0, now - item.stat().st_mtime))
                if marker_complete(marker) and age_seconds >= minimum_age_seconds:
                    candidates.append(
                        {
                            "kind": "completed_capture_archive_work",
                            "path": str(item),
                            "dataset_id": dataset_dir.name,
                            "capture_id": capture_id,
                            "size_bytes": item.stat().st_size,
                            "age_seconds": age_seconds,
                            "marker_path": str(marker),
                            "marker_complete": True,
                            "open_by_process": False,
                        }
                    )
    return candidates


def delete_completed_split_candidates(
    output_root: Path,
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    split_root = (output_root / "_split_work").resolve()
    deleted: list[dict[str, Any]] = []
    for candidate in candidates:
        if candidate["kind"] != "completed_capture_split_work":
            continue
        path = Path(candidate["path"]).resolve()
        marker = Path(candidate["marker_path"])
        try:
            relative = path.relative_to(split_root)
        except ValueError:
            continue
        if len(relative.parts) != 2 or not path.is_dir() or not marker_complete(marker):
            continue
        _, open_paths = live_state(output_root)
        if path_is_open(path, open_paths):
            continue
        shutil.rmtree(path)
        deleted.append(candidate)
    return deleted


def incomplete_outputs(
    output_root: Path,
    manifests: dict[str, dict[str, Any]],
    open_paths: set[str],
) -> dict[str, list[dict[str, Any]]]:
    now = time.time()
    results: dict[str, list[dict[str, Any]]] = {}
    for dataset_id in DATASET_IDS:
        directory = output_root / dataset_id
        if not directory.is_dir() or manifests[dataset_id].get("complete"):
            continue
        files = []
        for item in directory.iterdir():
            if not item.is_file():
                continue
            stat = item.stat()
            files.append(
                {
                    "name": item.name,
                    "size_bytes": stat.st_size,
                    "age_seconds": int(max(0.0, now - stat.st_mtime)),
                    "open_by_process": str(item) in open_paths,
                }
            )
        results[dataset_id] = files
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--minimum-age-hours", type=float, default=1.0)
    parser.add_argument("--delete-completed-splits", action="store_true")
    parser.add_argument("--audit-output", type=Path)
    args = parser.parse_args()
    active, open_paths = live_state(args.output_root)
    manifests = manifest_state(args.output_root)
    candidates = cleanup_candidates(
        args.output_root,
        open_paths,
        int(args.minimum_age_hours * 3600),
    )
    deleted: list[dict[str, Any]] = []
    if args.delete_completed_splits:
        deleted = delete_completed_split_candidates(args.output_root, candidates)
        active, open_paths = live_state(args.output_root)
        candidates = cleanup_candidates(
            args.output_root,
            open_paths,
            int(args.minimum_age_hours * 3600),
        )
    disk = shutil.disk_usage(args.output_root)
    report = {
        "schema_version": "caeos_feature_storage_audit_v1",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "output_root": str(args.output_root),
        "active": active,
        "manifests": manifests,
        "formal_complete_count": sum(
            1 for item in manifests.values() if item.get("complete")
        ),
        "disk": {
            "total_bytes": disk.total,
            "used_bytes": disk.used,
            "free_bytes": disk.free,
        },
        "open_path_count_under_root": len(open_paths),
        "cleanup_candidates": candidates,
        "cleanup_candidate_count": len(candidates),
        "cleanup_candidate_bytes": sum(item["size_bytes"] for item in candidates),
        "deleted_completed_split_count": len(deleted),
        "deleted_completed_split_bytes": sum(
            item["size_bytes"] for item in deleted
        ),
        "deleted_completed_splits": deleted,
        "incomplete_outputs": incomplete_outputs(
            args.output_root, manifests, open_paths
        ),
        "deletion_performed": bool(deleted),
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
