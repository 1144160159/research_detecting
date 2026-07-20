"""Parallel, resumable Zenodo collector for large GPU-side datasets."""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from typing import Any

from collect_zenodo_dataset import (
    atomic_json,
    content_url,
    digest_file,
    expected_checksum,
    fetch_record,
    run_aria2,
    utc_now,
    write_source_files,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", required=True)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--files", nargs="*", default=None)
    parser.add_argument("--connections", type=int, default=2)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--expected-files", type=int)
    parser.add_argument("--expected-bytes", type=int)
    parser.add_argument("--metadata-only", action="store_true")
    return parser.parse_args()


def load_previous_state(path: Path, record_id: str) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}
    if str(value.get("record_id")) != record_id:
        return {}
    return value


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    raw_dir = root / "raw"
    metadata_dir = root / "metadata"
    manifest_dir = root / "manifests"
    state_path = manifest_dir / "collection_state.json"
    raw_dir.mkdir(parents=True, exist_ok=True)

    record = fetch_record(args.record)
    files = list(record.get("files", []))
    if args.files is not None:
        requested = set(args.files)
        files = [item for item in files if item.get("key") in requested]
        missing = requested - {str(item.get("key")) for item in files}
        if missing:
            raise SystemExit(f"Files absent from Zenodo record: {sorted(missing)}")

    selection_size_bytes = sum(int(item["size"]) for item in files)
    if args.expected_files is not None and len(files) != args.expected_files:
        raise RuntimeError(
            f"Zenodo file-count drift: expected {args.expected_files}, found {len(files)}"
        )
    if args.expected_bytes is not None and selection_size_bytes != args.expected_bytes:
        raise RuntimeError(
            f"Zenodo byte-count drift: expected {args.expected_bytes}, "
            f"found {selection_size_bytes}"
        )

    atomic_json(metadata_dir / "zenodo_record.json", record)
    write_source_files(manifest_dir / "source_files.tsv", files)
    previous = load_previous_state(state_path, str(args.record))
    previous_files = previous.get("files", {})
    state: dict[str, Any] = {
        "record_id": str(args.record),
        "record_url": record.get("links", {}).get("html"),
        "generated_at": utc_now(),
        "root": str(root),
        "expected_file_count": len(files),
        "selection_size_bytes": selection_size_bytes,
        "parallel_jobs": max(1, args.jobs),
        "connections_per_file": max(1, args.connections),
        "files": {},
    }
    for item in files:
        name = str(item["key"])
        old = previous_files.get(name, {})
        entry: dict[str, Any] = {
            "size_expected": int(item["size"]),
            "source_checksum": str(item["checksum"]),
            "url": content_url(item),
            "status": "metadata_only" if args.metadata_only else "pending",
        }
        target = raw_dir / name
        if (
            old.get("status") == "verified"
            and target.is_file()
            and target.stat().st_size == entry["size_expected"]
            and old.get("digests")
        ):
            entry.update(old)
        state["files"][name] = entry

    lock = Lock()

    def save_state() -> None:
        with lock:
            state["generated_at"] = utc_now()
            atomic_json(state_path, state)

    save_state()

    def update(name: str, **values: Any) -> None:
        with lock:
            state["files"][name].update(values)
            state["generated_at"] = utc_now()
            atomic_json(state_path, state)

    def collect(item: dict[str, Any]) -> str:
        name = str(item["key"])
        entry = state["files"][name]
        target = raw_dir / name
        expected_algorithm, expected_digest = expected_checksum(item)
        if entry.get("status") in {"verified", "metadata_only"}:
            return name

        control_file = Path(str(target) + ".aria2")
        if not target.exists() or control_file.exists():
            update(name, status="downloading")
            run_aria2(entry["url"], target, max(1, args.connections))

        update(name, status="verifying")
        algorithms = list(dict.fromkeys([expected_algorithm, "sha256"]))
        digests = digest_file(target, algorithms)
        size_actual = target.stat().st_size
        verified = (
            size_actual == entry["size_expected"]
            and digests[expected_algorithm].lower() == expected_digest
        )
        update(
            name,
            size_actual=size_actual,
            digests=digests,
            verified_at=utc_now(),
            status="verified" if verified else "checksum_failed",
        )
        if not verified:
            raise RuntimeError(f"Integrity verification failed for {target}")
        return name

    if not args.metadata_only:
        pending = [
            item
            for item in files
            if state["files"][str(item["key"])].get("status") != "verified"
        ]
        errors: list[str] = []
        with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as executor:
            futures = {executor.submit(collect, item): str(item["key"]) for item in pending}
            for future in as_completed(futures):
                name = futures[future]
                try:
                    future.result()
                except Exception as exc:  # preserve every worker failure in the manifest
                    update(name, status="failed", error=repr(exc), failed_at=utc_now())
                    errors.append(f"{name}: {exc!r}")
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1

    state["complete"] = all(
        value.get("status") in {"verified", "metadata_only"}
        for value in state["files"].values()
    )
    save_state()
    print(json.dumps({"state": str(state_path), "complete": state["complete"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
