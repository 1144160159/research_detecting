from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
from pathlib import Path
from typing import Any


CODE_DIRECTORIES = (
    "caeos",
    "configs",
    "contracts",
    "docs",
    "reproducibility",
    "scripts",
    "tests",
)
ROOT_SUFFIXES = {
    ".cmd",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory(root: Path) -> dict[str, str]:
    source_root = root.resolve()
    files: list[Path] = [
        path
        for path in source_root.iterdir()
        if path.is_file() and path.suffix.lower() in ROOT_SUFFIXES
    ]
    for directory_name in CODE_DIRECTORIES:
        directory = source_root / directory_name
        if directory.is_dir():
            files.extend(
                path
                for path in directory.rglob("*")
                if path.is_file() and path.suffix.lower() in ROOT_SUFFIXES
            )
    return {
        path.relative_to(source_root).as_posix(): sha256_file(path)
        for path in sorted(set(files))
    }


def compare_workspaces(current_root: Path, legacy_root: Path) -> dict[str, Any]:
    current = inventory(current_root)
    legacy = inventory(legacy_root)
    current_paths = set(current)
    legacy_paths = set(legacy)
    common_paths = current_paths & legacy_paths
    mismatch = sorted(
        path for path in common_paths if current[path] != legacy[path]
    )
    identical = sorted(
        path for path in common_paths if current[path] == legacy[path]
    )
    return {
        "schema_version": "caeos_workspace_diff_v1",
        "current_root": str(current_root.resolve()),
        "legacy_root": str(legacy_root.resolve()),
        "counts": {
            "current_files": len(current),
            "legacy_files": len(legacy),
            "identical": len(identical),
            "content_mismatch": len(mismatch),
            "current_only": len(current_paths - legacy_paths),
            "legacy_only": len(legacy_paths - current_paths),
        },
        "legacy_only": [
            {"path": path, "sha256": legacy[path]}
            for path in sorted(legacy_paths - current_paths)
        ],
        "current_only": [
            {"path": path, "sha256": current[path]}
            for path in sorted(current_paths - legacy_paths)
        ],
        "content_mismatch": [
            {
                "path": path,
                "current_sha256": current[path],
                "legacy_sha256": legacy[path],
            }
            for path in mismatch
        ],
    }


def create_legacy_quarantine(
    legacy_root: Path,
    report: dict[str, Any],
    archive_path: Path,
) -> None:
    paths = [
        item["path"]
        for key in ("legacy_only", "content_mismatch")
        for item in report[key]
    ]
    with tarfile.open(archive_path, "w:gz") as archive:
        for relative_path in paths:
            source = legacy_root.resolve() / relative_path
            archive.add(
                source,
                arcname=f"legacy/{relative_path}",
                recursive=False,
            )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare code-relevant files in two CAEOS workspaces."
    )
    parser.add_argument("--current-root", required=True)
    parser.add_argument("--legacy-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--archive-legacy-differences")
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    current_root = Path(args.current_root)
    legacy_root = Path(args.legacy_root)
    report = compare_workspaces(current_root, legacy_root)
    if args.archive_legacy_differences:
        archive_path = Path(args.archive_legacy_differences)
        create_legacy_quarantine(legacy_root, report, archive_path)
        report["legacy_quarantine"] = {
            "path": str(archive_path.resolve()),
            "sha256": sha256_file(archive_path),
            "file_count": (
                report["counts"]["legacy_only"]
                + report["counts"]["content_mismatch"]
            ),
        }
    output_path = Path(args.output)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report["counts"], sort_keys=True))
    if "legacy_quarantine" in report:
        print(json.dumps(report["legacy_quarantine"], sort_keys=True))


if __name__ == "__main__":
    main()
