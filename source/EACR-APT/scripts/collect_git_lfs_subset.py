"""Collect a pinned Git LFS subset without pulling the full upstream payload.

The default mode clones only Git metadata (``GIT_LFS_SKIP_SMUDGE=1``),
enumerates LFS pointers from the pinned Git object tree, and writes a selection
plan.  Payload transfer requires the explicit ``--download-selected`` flag.
All runtime artifacts are written below ``--root``; source and configuration
files contain no credentials or dataset payloads.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import urlparse


LFS_HEADER = b"version https://git-lfs.github.com/spec/v1\n"
LFS_OID = re.compile(br"^oid sha256:([0-9a-f]{64})$", re.MULTILINE)
LFS_SIZE = re.compile(br"^size ([1-9][0-9]*)$", re.MULTILINE)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def safe_relative_path(value: str) -> str:
    candidate = PurePosixPath(value.replace("\\", "/"))
    if not value or candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"Unsafe repository path: {value!r}")
    normalized = candidate.as_posix()
    if normalized in {"", "."}:
        raise ValueError(f"Unsafe repository path: {value!r}")
    return normalized


def parse_lfs_pointer(data: bytes) -> dict[str, Any] | None:
    """Return the SHA-256 object id and size for a strict Git LFS pointer."""

    if not data.startswith(LFS_HEADER):
        return None
    oid = LFS_OID.search(data)
    size = LFS_SIZE.search(data)
    if not oid or not size:
        raise ValueError("Malformed Git LFS pointer")
    return {"oid_sha256": oid.group(1).decode("ascii"), "size": int(size.group(1))}


def _git_blob_entries(repository: Path) -> list[tuple[str, str]]:
    output = subprocess.run(
        ["git", "-C", str(repository), "ls-tree", "-r", "-z", "HEAD"],
        check=True,
        capture_output=True,
    ).stdout
    entries: list[tuple[str, str]] = []
    for record in output.split(b"\0"):
        if not record:
            continue
        metadata, separator, raw_path = record.partition(b"\t")
        if not separator:
            raise RuntimeError("Unexpected git ls-tree record")
        fields = metadata.split()
        if len(fields) != 3 or fields[1] != b"blob":
            continue
        path = safe_relative_path(raw_path.decode("utf-8", errors="surrogateescape"))
        entries.append((fields[2].decode("ascii"), path))
    return entries


def _read_git_blobs(repository: Path, entries: list[tuple[str, str]]) -> list[bytes]:
    query = b"".join(oid.encode("ascii") + b"\n" for oid, _path in entries)
    output = subprocess.run(
        ["git", "-C", str(repository), "cat-file", "--batch"],
        input=query,
        check=True,
        capture_output=True,
    ).stdout
    blobs: list[bytes] = []
    offset = 0
    for expected_oid, _path in entries:
        line_end = output.find(b"\n", offset)
        if line_end < 0:
            raise RuntimeError("Truncated git cat-file header")
        header = output[offset:line_end].split()
        if len(header) != 3 or header[0].decode("ascii") != expected_oid:
            raise RuntimeError("Unexpected git cat-file response")
        size = int(header[2])
        start = line_end + 1
        end = start + size
        if end >= len(output) or output[end : end + 1] != b"\n":
            raise RuntimeError("Truncated git cat-file payload")
        blobs.append(output[start:end])
        offset = end + 1
    if offset != len(output):
        raise RuntimeError("Unexpected trailing git cat-file output")
    return blobs


def enumerate_lfs_pointers(repository: Path) -> list[dict[str, Any]]:
    """Enumerate pointers from committed blobs, even after selected files are smudged."""

    entries = _git_blob_entries(repository)
    rows: list[dict[str, Any]] = []
    for (_oid, path), data in zip(entries, _read_git_blobs(repository, entries)):
        pointer = parse_lfs_pointer(data)
        if pointer:
            rows.append({"path": path, **pointer})
    return sorted(rows, key=lambda row: row["path"])


def select_inventory(
    inventory: Iterable[dict[str, Any]],
    include_globs: list[str],
    exclude_globs: list[str] | None = None,
) -> list[dict[str, Any]]:
    if not include_globs:
        raise ValueError("At least one include_glob is required")
    includes = [safe_relative_path(pattern) for pattern in include_globs]
    excludes = [safe_relative_path(pattern) for pattern in (exclude_globs or [])]
    selected = []
    for row in inventory:
        path = safe_relative_path(str(row["path"]))
        if not any(fnmatch.fnmatchcase(path, pattern) for pattern in includes):
            continue
        if any(fnmatch.fnmatchcase(path, pattern) for pattern in excludes):
            continue
        selected.append(dict(row))
    return sorted(selected, key=lambda row: row["path"])


def _proxy_args(proxy: str | None) -> list[str]:
    if not proxy:
        return []
    parsed = urlparse(proxy)
    if parsed.scheme not in {"socks5", "socks5h", "http", "https"} or not parsed.hostname:
        raise ValueError("Proxy must be socks5[h]://HOST:PORT or http[s]://HOST:PORT")
    return ["-c", f"http.proxy={proxy}", "-c", "http.version=HTTP/1.1"]


def clone_pinned_metadata(
    source_repository: str,
    commit: str,
    repository: Path,
    proxy: str | None,
) -> None:
    """Fetch exactly one commit with LFS smudging disabled."""

    if repository.joinpath(".git").is_dir():
        actual = subprocess.check_output(
            ["git", "-C", str(repository), "rev-parse", "HEAD"], text=True
        ).strip()
        if actual != commit:
            raise RuntimeError(f"Repository commit drift: {actual} != {commit}")
        return
    if repository.exists():
        raise RuntimeError(f"Repository path exists but is not a Git checkout: {repository}")

    staging = repository.with_name(repository.name + f".tmp-{os.getpid()}")
    if staging.exists():
        shutil.rmtree(staging)
    staging.parent.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1", GIT_TERMINAL_PROMPT="0")
    try:
        subprocess.run(["git", "init", str(staging)], check=True, capture_output=True)
        subprocess.run(
            ["git", "-C", str(staging), "remote", "add", "origin", source_repository],
            check=True,
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(staging),
                *_proxy_args(proxy),
                "fetch",
                "--depth=1",
                "origin",
                commit,
            ],
            check=True,
            env=environment,
        )
        subprocess.run(
            ["git", "-C", str(staging), "checkout", "--detach", "FETCH_HEAD"],
            check=True,
            env=environment,
        )
        os.replace(staging, repository)
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise


def verify_payload(repository: Path, selected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    verified: list[dict[str, Any]] = []
    for row in selected:
        path = repository.joinpath(*PurePosixPath(row["path"]).parts)
        digest = hashlib.sha256()
        size = 0
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
                digest.update(block)
                size += len(block)
        actual = digest.hexdigest()
        good = size == row["size"] and actual == row["oid_sha256"]
        verified.append(
            {
                **row,
                "actual_size": size,
                "actual_sha256": actual,
                "verified": good,
            }
        )
    return verified


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    os.replace(temporary, path)


def write_sha256(path: Path) -> None:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    path.with_name(path.name + ".sha256").write_text(
        f"{digest}  {path.name}\n", encoding="utf-8"
    )


def _enforce_count_and_bytes(
    label: str,
    rows: list[dict[str, Any]],
    expected_count: int | None,
    expected_bytes: int | None,
) -> None:
    count = len(rows)
    size = sum(int(row["size"]) for row in rows)
    if expected_count is not None and count != expected_count:
        raise RuntimeError(f"{label} object-count drift: {count} != {expected_count}")
    if expected_bytes is not None and size != expected_bytes:
        raise RuntimeError(f"{label} byte-count drift: {size} != {expected_bytes}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--root", required=True, type=Path, help="GPU-only dataset root")
    parser.add_argument("--proxy", default=os.environ.get("EACR_DATASET_PROXY"))
    parser.add_argument("--download-selected", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if int(config.get("schema_version", 0)) != 1:
        raise ValueError("Only Git LFS subset schema_version=1 is supported")

    root = args.root.resolve()
    allowed = Path(config["allowed_root_prefix"]).resolve()
    if root != allowed and allowed not in root.parents:
        raise ValueError(f"--root must be below the GPU dataset prefix {allowed}")
    repository = root / "repository"
    manifests = root / "manifests"
    clone_pinned_metadata(
        config["source_repository"], config["source_commit"], repository, args.proxy
    )
    actual_commit = subprocess.check_output(
        ["git", "-C", str(repository), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual_commit != config["source_commit"]:
        raise RuntimeError("Pinned commit verification failed")

    inventory = enumerate_lfs_pointers(repository)
    selected = select_inventory(
        inventory, config["include_globs"], config.get("exclude_globs", [])
    )
    _enforce_count_and_bytes(
        "upstream",
        inventory,
        config.get("expected_upstream_lfs_objects"),
        config.get("expected_upstream_lfs_bytes"),
    )
    _enforce_count_and_bytes(
        "selection",
        selected,
        config.get("expected_selected_lfs_objects"),
        config.get("expected_selected_lfs_bytes"),
    )
    selected_bytes = sum(int(row["size"]) for row in selected)
    if not selected:
        raise RuntimeError("Selection resolves to zero Git LFS objects")
    if selected_bytes > int(config["max_selected_lfs_bytes"]):
        raise RuntimeError("Selection exceeds max_selected_lfs_bytes safety gate")

    inventory_path = manifests / "lfs_inventory.jsonl"
    selection_plan_path = manifests / "selected_payload_plan.jsonl"
    selected_payload_path = manifests / "selected_payload.jsonl"
    _write_jsonl(inventory_path, inventory)
    _write_jsonl(selection_plan_path, selected)
    write_sha256(inventory_path)
    write_sha256(selection_plan_path)
    verified: list[dict[str, Any]] = []
    if args.download_selected:
        environment = dict(os.environ, GIT_TERMINAL_PROMPT="0")
        subprocess.run(
            [
                "git",
                "-C",
                str(repository),
                *_proxy_args(args.proxy),
                "lfs",
                "pull",
                f"--include={','.join(config['include_globs'])}",
                "--exclude=",
            ],
            check=True,
            env=environment,
        )
        verified = verify_payload(repository, selected)
        if not all(row["verified"] for row in verified):
            raise RuntimeError("Selected payload failed size/SHA-256 verification")
        _write_jsonl(selected_payload_path, verified)
        write_sha256(selected_payload_path)

    full_complete = bool(verified) and len(selected) == len(inventory)
    state = {
        "schema_version": 1,
        "dataset_id": config["dataset_id"],
        "source_repository": config["source_repository"],
        "pinned_commit": actual_commit,
        "license": config.get("license"),
        "generated_at": utc_now(),
        "complete": True,
        "collection_complete": True,
        "metadata_complete": True,
        "metadata_only": not args.download_selected,
        "data_payload_complete": full_complete,
        "full_dataset_payload_complete": full_complete,
        "selected_subset_payload_complete": bool(verified),
        "upstream_lfs": {
            "object_count": len(inventory),
            "payload_bytes": sum(int(row["size"]) for row in inventory),
        },
        "selection": {
            "include_globs": config["include_globs"],
            "exclude_globs": config.get("exclude_globs", []),
            "selection_reason": config.get("selection_reason"),
            "object_count": len(selected),
            "payload_bytes": selected_bytes,
            "verified_object_count": sum(bool(row["verified"]) for row in verified),
        },
        "integrity": {
            "repository_commit_matches_pin": True,
            "all_selected_size_and_sha256_match_lfs_oid": bool(verified)
            and all(row["verified"] for row in verified),
            "lfs_inventory_manifest": "manifests/lfs_inventory.jsonl",
            "selection_plan_manifest": "manifests/selected_payload_plan.jsonl",
            "selected_payload_manifest": (
                "manifests/selected_payload.jsonl" if verified else None
            ),
        },
        "active_downloads": False,
        "payload_stored_only_below_gpu_root": True,
    }
    state_path = manifests / "state.json"
    atomic_json(state_path, state)
    write_sha256(state_path)
    print(json.dumps(state, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
