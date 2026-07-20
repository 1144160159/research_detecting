"""Parallel, resumable Dataverse collector for large GPU-side datasets."""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from typing import Any

from collect_dataverse_dataset import fetch_dataset, flatten_files, write_source_files
from collect_zenodo_dataset import atomic_json, digest_file, run_aria2, utc_now


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--persistent-id", required=True)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--file-ids", nargs="*", type=int, default=None)
    parser.add_argument("--connections", type=int, default=2)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--metadata-only", action="store_true")
    return parser.parse_args()


def load_previous_state(path: Path, persistent_id: str) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}
    if str(value.get("persistent_id")) != persistent_id:
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

    payload = fetch_dataset(args.base_url, args.persistent_id)
    files = flatten_files(payload)
    if args.file_ids is not None:
        requested = set(args.file_ids)
        files = [item for item in files if int(item["id"]) in requested]
        missing = requested - {int(item["id"]) for item in files}
        if missing:
            raise SystemExit(f"File IDs absent from Dataverse record: {sorted(missing)}")

    atomic_json(metadata_dir / "dataverse_record.json", payload)
    write_source_files(manifest_dir / "source_files.tsv", args.base_url, files)
    previous = load_previous_state(state_path, args.persistent_id)
    previous_files = previous.get("files", {})
    state: dict[str, Any] = {
        "persistent_id": args.persistent_id,
        "generated_at": utc_now(),
        "root": str(root),
        "selection_size_bytes": sum(int(item["filesize"]) for item in files),
        "parallel_jobs": max(1, args.jobs),
        "connections_per_file": max(1, args.connections),
        "files": {},
    }
    for item in files:
        name = str(item["filename"])
        checksum = item["checksum"]
        expected_algorithm = str(checksum["type"]).lower()
        expected_digest = str(checksum["value"]).lower()
        target = raw_dir / name
        old = previous_files.get(name, {})
        entry: dict[str, Any] = {
            "id": int(item["id"]),
            "size_expected": int(item["filesize"]),
            "source_checksum": f"{expected_algorithm}:{expected_digest}",
            "url": f"{args.base_url.rstrip('/')}/api/access/datafile/{item['id']}",
            "status": "metadata_only" if args.metadata_only else "pending",
        }
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

    def update(name: str, **values: Any) -> None:
        with lock:
            state["files"][name].update(values)
            state["generated_at"] = utc_now()
            atomic_json(state_path, state)

    save_state()

    def collect(item: dict[str, Any]) -> str:
        name = str(item["filename"])
        entry = state["files"][name]
        target = raw_dir / name
        checksum = item["checksum"]
        expected_algorithm = str(checksum["type"]).lower()
        expected_digest = str(checksum["value"]).lower()
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
            if state["files"][str(item["filename"])].get("status") != "verified"
        ]
        errors: list[str] = []
        with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as executor:
            futures = {
                executor.submit(collect, item): str(item["filename"]) for item in pending
            }
            for future in as_completed(futures):
                name = futures[future]
                try:
                    future.result()
                except Exception as exc:
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
