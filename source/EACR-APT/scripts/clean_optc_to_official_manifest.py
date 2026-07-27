#!/usr/bin/env python3
"""Canonicalize OpTC and retain only the 1,277 manifest-listed files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


EXPECTED_ROOT = Path(
    "/opt/data/private/wangwt/ParkAttackKE/datasets/apt_public/optc"
)
DEFAULT_RECEIPT_DIR = Path(
    "/opt/data/private/wangwt/ParkAttackKE/APT-Chain-Reconstruction/"
    "output/trace/dataset_cleanup"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def all_files(root: Path) -> list[Path]:
    result: list[Path] = []
    for directory, dirnames, filenames in os.walk(root, followlinks=False):
        base = Path(directory)
        for name in list(dirnames):
            candidate = base / name
            if candidate.is_symlink():
                result.append(candidate)
                dirnames.remove(name)
        result.extend(base / name for name in filenames)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=EXPECTED_ROOT)
    parser.add_argument("--receipt-dir", type=Path, default=DEFAULT_RECEIPT_DIR)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve(strict=True)
    if root != EXPECTED_ROOT:
        raise SystemExit(f"refusing unexpected root: {root}")

    data_root = root / "raw_original"
    manifest_path = root / "manifests" / "gdrive_file_tree.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest.get("files")
    if manifest.get("file_count") != 1277 or not isinstance(entries, list):
        raise SystemExit("manifest is not the expected 1,277-file OpTC manifest")
    if len(entries) != 1277:
        raise SystemExit(f"manifest list length mismatch: {len(entries)}")

    canonical_paths: set[Path] = set()
    moves: list[tuple[Path, Path]] = []
    duplicate_paths: list[Path] = []
    missing: list[str] = []
    empty: list[str] = []
    duplicate_conflicts: list[dict[str, object]] = []

    for item in entries:
        relative = Path(item["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise SystemExit(f"unsafe manifest path: {relative}")
        canonical = data_root / relative
        legacy = data_root / "OpTCNCR" / relative
        canonical_paths.add(canonical)
        at_canonical = canonical.is_file() and not canonical.is_symlink()
        at_legacy = legacy.is_file() and not legacy.is_symlink()
        if not at_canonical and not at_legacy:
            missing.append(item["path"])
            continue
        selected = canonical if at_canonical else legacy
        if selected.stat().st_size == 0:
            empty.append(item["path"])
        if at_canonical and at_legacy:
            canonical_size = canonical.stat().st_size
            legacy_size = legacy.stat().st_size
            if canonical_size != legacy_size:
                duplicate_conflicts.append(
                    {
                        "path": item["path"],
                        "canonical_size": canonical_size,
                        "legacy_size": legacy_size,
                        "reason": "size",
                    }
                )
            elif sha256(canonical) != sha256(legacy):
                duplicate_conflicts.append(
                    {
                        "path": item["path"],
                        "canonical_size": canonical_size,
                        "legacy_size": legacy_size,
                        "reason": "sha256",
                    }
                )
            duplicate_paths.append(legacy)
        elif at_legacy:
            moves.append((legacy, canonical))

    before_files = all_files(root)
    before_bytes = sum(path.stat().st_size for path in before_files if path.is_file())
    summary: dict[str, object] = {
        "time": utc_now(),
        "root": str(root),
        "manifest_files": len(entries),
        "canonical_present": len(entries) - len(moves) - len(missing),
        "legacy_to_move": len(moves),
        "duplicate_legacy_to_delete": len(duplicate_paths),
        "missing": len(missing),
        "empty": len(empty),
        "duplicate_conflicts": len(duplicate_conflicts),
        "files_before": len(before_files),
        "bytes_before": before_bytes,
        "execute": args.execute,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)

    if missing or empty or duplicate_conflicts:
        details = {
            "missing": missing[:20],
            "empty": empty[:20],
            "duplicate_conflicts": duplicate_conflicts[:20],
        }
        print(json.dumps(details, ensure_ascii=False, indent=2), flush=True)
        raise SystemExit("preflight failed; nothing was deleted")
    if not args.execute:
        return 0

    for source, destination in moves:
        destination.parent.mkdir(parents=True, exist_ok=True)
        os.replace(source, destination)

    missing_after_move = [
        str(path.relative_to(data_root))
        for path in canonical_paths
        if not path.is_file() or path.is_symlink()
    ]
    if missing_after_move:
        raise SystemExit(
            f"canonicalization failed; nothing deleted: {missing_after_move[:20]}"
        )

    deletion_candidates = [path for path in all_files(root) if path not in canonical_paths]
    deleted_bytes = 0
    deleted_paths: list[str] = []
    for path in deletion_candidates:
        if path.is_file() and not path.is_symlink():
            deleted_bytes += path.stat().st_size
        deleted_paths.append(str(path.relative_to(root)))
        path.unlink()

    for directory, dirnames, filenames in os.walk(root, topdown=False):
        candidate = Path(directory)
        if candidate in {root, data_root}:
            continue
        if not dirnames and not filenames:
            candidate.rmdir()
        elif candidate.exists() and not any(candidate.iterdir()):
            candidate.rmdir()

    after_files = all_files(root)
    after_set = set(after_files)
    missing_final = canonical_paths - after_set
    extras_final = after_set - canonical_paths
    if len(after_files) != 1277 or missing_final or extras_final:
        raise SystemExit(
            "final verification failed: "
            f"files={len(after_files)} missing={len(missing_final)} "
            f"extras={len(extras_final)}"
        )

    after_bytes = sum(path.stat().st_size for path in after_files)
    receipt = {
        **summary,
        "finished_at": utc_now(),
        "moved": len(moves),
        "deleted": len(deletion_candidates),
        "deleted_bytes": deleted_bytes,
        "files_after": len(after_files),
        "bytes_after": after_bytes,
        "missing_after": 0,
        "extras_after": 0,
        "deleted_paths": deleted_paths,
    }
    args.receipt_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = args.receipt_dir / (
        "optc_cleanup_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + ".json"
    )
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"receipt": str(receipt_path), **receipt}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
