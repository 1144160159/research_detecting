"""Collect and verify a public Mendeley Data dataset on the GPU server."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    from collect_zenodo_dataset import atomic_json, digest_file, run_aria2, utc_now
except ModuleNotFoundError:
    from scripts.collect_zenodo_dataset import (
        atomic_json,
        digest_file,
        run_aria2,
        utc_now,
    )


API_ROOT = "https://data.mendeley.com/public-api/datasets"
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--version", required=True, type=int)
    parser.add_argument("--folder-id", default="root")
    parser.add_argument("--root", required=True, type=Path, help="GPU-only dataset root")
    parser.add_argument("--files", nargs="*", default=None)
    parser.add_argument("--expected-files", type=int)
    parser.add_argument("--expected-bytes", type=int)
    parser.add_argument("--connections", type=int, default=2)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--metadata-only", action="store_true")
    return parser.parse_args()


def metadata_url(dataset_id: str, version: int, folder_id: str = "root") -> str:
    query = urlencode({"folder_id": folder_id, "version": version})
    return f"{API_ROOT}/{dataset_id}/files?{query}"


def fetch_files(dataset_id: str, version: int, folder_id: str = "root") -> list[dict[str, Any]]:
    request = Request(
        metadata_url(dataset_id, version, folder_id),
        headers={"User-Agent": "EACR-APT-dataset-collector/1.0"},
    )
    with urlopen(request, timeout=120) as response:
        payload = json.load(response)
    if not isinstance(payload, list):
        raise ValueError("Mendeley files API did not return a JSON list")
    return payload


def safe_filename(value: str) -> str:
    if (
        not value
        or value in {".", ".."}
        or Path(value).name != value
        or "/" in value
        or "\\" in value
    ):
        raise ValueError(f"Unsafe Mendeley filename: {value!r}")
    return value


def normalize_files(payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for source in payload:
        name = safe_filename(str(source.get("filename", "")))
        details = source.get("content_details") or {}
        size = int(details.get("size", source.get("size", 0)))
        outer_size = int(source.get("size", size))
        if size <= 0 or outer_size != size:
            raise ValueError(f"Invalid or inconsistent size for {name!r}")
        digest = str(details.get("sha256_hash", "")).lower()
        if not SHA256.fullmatch(digest):
            raise ValueError(f"Missing or invalid sha256_hash for {name!r}")
        download_url = str(details.get("download_url", ""))
        if not download_url.startswith("https://"):
            raise ValueError(f"Missing HTTPS download_url for {name!r}")
        files.append(
            {
                "name": name,
                "id": str(source.get("id", "")),
                "size": size,
                "sha256": digest,
                "download_url": download_url,
                "content_type": details.get("content_type"),
            }
        )
    names = [item["name"] for item in files]
    if not files:
        raise ValueError("Mendeley dataset resolves to zero files")
    if len(names) != len(set(names)):
        raise ValueError("Mendeley dataset contains duplicate filenames")
    return files


def write_source_files(path: Path, files: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["name", "size_bytes", "source_checksum", "url", "id"])
        for item in files:
            writer.writerow(
                [
                    item["name"],
                    item["size"],
                    f"sha256:{item['sha256']}",
                    item["download_url"],
                    item["id"],
                ]
            )


def load_previous_state(
    path: Path, dataset_id: str, version: int, folder_id: str
) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}
    identity = (value.get("dataset_id"), value.get("version"), value.get("folder_id"))
    return value if identity == (dataset_id, version, folder_id) else {}


def main() -> int:
    args = parse_args()
    if args.version <= 0:
        raise ValueError("--version must be positive")
    root = args.root.resolve()
    raw_dir = root / "raw"
    metadata_dir = root / "metadata"
    manifest_dir = root / "manifests"
    state_path = manifest_dir / "collection_state.json"
    raw_dir.mkdir(parents=True, exist_ok=True)

    payload = fetch_files(args.dataset_id, args.version, args.folder_id)
    files = normalize_files(payload)
    if args.files is not None:
        requested = set(args.files)
        files = [item for item in files if item["name"] in requested]
        missing = requested - {item["name"] for item in files}
        if missing:
            raise SystemExit(f"Files absent from Mendeley dataset: {sorted(missing)}")

    selection_bytes = sum(item["size"] for item in files)
    if args.expected_files is not None and len(files) != args.expected_files:
        raise RuntimeError(
            f"Mendeley file-count drift: expected {args.expected_files}, found {len(files)}"
        )
    if args.expected_bytes is not None and selection_bytes != args.expected_bytes:
        raise RuntimeError(
            f"Mendeley byte-count drift: expected {args.expected_bytes}, found {selection_bytes}"
        )

    atomic_json(metadata_dir / "mendeley_files.json", payload)
    write_source_files(manifest_dir / "source_files.tsv", files)
    previous = load_previous_state(
        state_path, args.dataset_id, args.version, args.folder_id
    )
    previous_files = previous.get("files", {})
    state: dict[str, Any] = {
        "dataset_id": args.dataset_id,
        "version": args.version,
        "folder_id": args.folder_id,
        "metadata_url": metadata_url(args.dataset_id, args.version, args.folder_id),
        "generated_at": utc_now(),
        "root": str(root),
        "expected_file_count": len(files),
        "selection_size_bytes": selection_bytes,
        "parallel_jobs": max(1, args.jobs),
        "connections_per_file": max(1, args.connections),
        "files": {},
    }
    for item in files:
        name = item["name"]
        old = previous_files.get(name, {})
        target = raw_dir / name
        entry: dict[str, Any] = {
            "id": item["id"],
            "url": item["download_url"],
            "size_expected": item["size"],
            "source_checksum": f"sha256:{item['sha256']}",
            "status": "metadata_only" if args.metadata_only else "pending",
        }
        if (
            not args.metadata_only
            and old.get("status") == "verified"
            and old.get("id") == entry["id"]
            and old.get("size_expected") == entry["size_expected"]
            and old.get("source_checksum") == entry["source_checksum"]
            and target.is_file()
            and target.stat().st_size == entry["size_expected"]
            and old.get("digests", {}).get("sha256") == item["sha256"]
        ):
            # Keep the fresh API URL while preserving verified runtime evidence.
            fresh_url = entry["url"]
            entry.update(old)
            entry["url"] = fresh_url
        state["files"][name] = entry

    lock = Lock()

    def save_state() -> None:
        with lock:
            state["generated_at"] = utc_now()
            atomic_json(state_path, state)

    def update(name: str, **values: Any) -> None:
        with lock:
            state["files"][name].update(values)
            state["generated_at"] = utc_now()
            atomic_json(state_path, state)

    save_state()

    def collect(item: dict[str, Any]) -> str:
        name = item["name"]
        entry = state["files"][name]
        target = raw_dir / name
        partial = Path(f"{target}.part")
        if entry.get("status") in {"verified", "metadata_only"}:
            return name

        if target.is_file() and target.stat().st_size < entry["size_expected"]:
            if partial.exists():
                raise RuntimeError(f"Both legacy partial and .part file exist for {target}")
            target.replace(partial)
        if target.is_file() and target.stat().st_size > entry["size_expected"]:
            raise RuntimeError(f"Existing file exceeds expected size: {target}")
        if partial.is_file() and partial.stat().st_size > entry["size_expected"]:
            raise RuntimeError(f"Partial file exceeds expected size: {partial}")

        candidate = target
        if not target.is_file() or target.stat().st_size != entry["size_expected"]:
            candidate = partial
            if not partial.is_file() or partial.stat().st_size != entry["size_expected"]:
                update(name, status="downloading", error=None)
                run_aria2(entry["url"], partial, max(1, args.connections))

        update(name, status="verifying")
        size_actual = candidate.stat().st_size
        digest = digest_file(candidate, ["sha256"])["sha256"]
        verified = size_actual == entry["size_expected"] and digest == item["sha256"]
        rejected_path = None
        if verified and candidate != target:
            os.replace(candidate, target)
        elif not verified:
            rejected = Path(f"{candidate}.checksum_failed-{utc_now().replace(':', '')}")
            candidate.replace(rejected)
            rejected_path = str(rejected)
        update(
            name,
            size_actual=size_actual,
            digests={"sha256": digest},
            verified_at=utc_now(),
            rejected_path=rejected_path,
            status="verified" if verified else "checksum_failed",
        )
        if not verified:
            raise RuntimeError(f"Integrity verification failed for {name}")
        return name

    errors: list[str] = []
    if not args.metadata_only:
        pending = [
            item
            for item in files
            if state["files"][item["name"]].get("status") != "verified"
        ]
        with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as executor:
            futures = {executor.submit(collect, item): item["name"] for item in pending}
            for future in as_completed(futures):
                name = futures[future]
                try:
                    future.result()
                except Exception as exc:
                    update(name, status="failed", error=repr(exc), failed_at=utc_now())
                    errors.append(f"{name}: {exc!r}")

    state["complete"] = not errors and all(
        entry.get("status") in {"verified", "metadata_only"}
        for entry in state["files"].values()
    )
    save_state()
    print(json.dumps({"state": str(state_path), "complete": state["complete"]}))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
