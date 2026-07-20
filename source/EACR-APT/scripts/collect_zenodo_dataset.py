"""Collect and verify a Zenodo dataset on the GPU server.

This script is intentionally dependency-free.  It stores raw archives and
runtime manifests under the server-side destination supplied with ``--root``;
those artifacts must not be synchronized back into the local source tree.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.request import Request, urlopen


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, path)


def fetch_record(record_id: str) -> dict[str, Any]:
    url = f"https://zenodo.org/api/records/{record_id}"
    request = Request(url, headers={"User-Agent": "EACR-APT-dataset-collector/1.0"})
    with urlopen(request, timeout=120) as response:
        return json.load(response)


def digest_file(path: Path, algorithms: Iterable[str]) -> dict[str, str]:
    hashers = {name: hashlib.new(name) for name in algorithms}
    with path.open("rb") as handle:
        while chunk := handle.read(16 * 1024 * 1024):
            for hasher in hashers.values():
                hasher.update(chunk)
    return {name: hasher.hexdigest() for name, hasher in hashers.items()}


def expected_checksum(file_record: dict[str, Any]) -> tuple[str, str]:
    value = str(file_record.get("checksum", ""))
    if ":" not in value:
        raise ValueError(f"Unsupported Zenodo checksum: {value!r}")
    algorithm, digest = value.split(":", 1)
    return algorithm.lower(), digest.lower()


def content_url(file_record: dict[str, Any]) -> str:
    links = file_record.get("links", {})
    url = links.get("content") or links.get("self")
    if not url:
        raise ValueError(f"No content URL for {file_record.get('key')!r}")
    return str(url)


def write_source_files(path: Path, files: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["name", "size_bytes", "source_checksum", "url"])
        for item in files:
            writer.writerow(
                [item["key"], int(item["size"]), item["checksum"], content_url(item)]
            )


def run_aria2(url: str, destination: Path, connections: int) -> None:
    command = [
        "aria2c",
        "--continue=true",
        "--auto-file-renaming=false",
        "--allow-overwrite=false",
        "--file-allocation=none",
        f"--max-connection-per-server={connections}",
        f"--split={connections}",
        "--min-split-size=64M",
        "--max-tries=0",
        "--retry-wait=15",
        "--connect-timeout=30",
        "--timeout=120",
        "--summary-interval=60",
        f"--dir={destination.parent}",
        f"--out={destination.name}",
        url,
    ]
    subprocess.run(command, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", required=True, help="Zenodo record identifier")
    parser.add_argument("--root", required=True, type=Path, help="GPU-only dataset root")
    parser.add_argument(
        "--files",
        nargs="*",
        default=None,
        help="Optional exact filenames; default collects every file in the record",
    )
    parser.add_argument("--connections", type=int, default=4)
    parser.add_argument(
        "--metadata-only", action="store_true", help="Write official metadata without archives"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    raw_dir = root / "raw"
    metadata_dir = root / "metadata"
    manifest_dir = root / "manifests"
    raw_dir.mkdir(parents=True, exist_ok=True)

    record = fetch_record(args.record)
    files = list(record.get("files", []))
    if args.files is not None:
        requested = set(args.files)
        files = [item for item in files if item.get("key") in requested]
        missing = requested - {str(item.get("key")) for item in files}
        if missing:
            raise SystemExit(f"Files absent from Zenodo record: {sorted(missing)}")

    atomic_json(metadata_dir / "zenodo_record.json", record)
    write_source_files(manifest_dir / "source_files.tsv", files)

    state: dict[str, Any] = {
        "record_id": str(args.record),
        "record_url": record.get("links", {}).get("html"),
        "generated_at": utc_now(),
        "root": str(root),
        "files": {},
    }
    state_path = manifest_dir / "collection_state.json"

    for item in files:
        name = str(item["key"])
        target = raw_dir / name
        expected_algorithm, expected_digest = expected_checksum(item)
        entry: dict[str, Any] = {
            "size_expected": int(item["size"]),
            "source_checksum": str(item["checksum"]),
            "url": content_url(item),
            "status": "metadata_only" if args.metadata_only else "pending",
        }
        state["files"][name] = entry
        atomic_json(state_path, state)

        if args.metadata_only:
            continue

        control_file = Path(str(target) + ".aria2")
        if not target.exists() or control_file.exists():
            entry["status"] = "downloading"
            atomic_json(state_path, state)
            run_aria2(entry["url"], target, max(1, args.connections))

        entry["status"] = "verifying"
        atomic_json(state_path, state)
        algorithms = list(dict.fromkeys([expected_algorithm, "sha256"]))
        digests = digest_file(target, algorithms)
        size_actual = target.stat().st_size
        verified = (
            size_actual == entry["size_expected"]
            and digests[expected_algorithm].lower() == expected_digest
        )
        entry.update(
            {
                "size_actual": size_actual,
                "digests": digests,
                "verified_at": utc_now(),
                "status": "verified" if verified else "checksum_failed",
            }
        )
        atomic_json(state_path, state)
        if not verified:
            raise RuntimeError(f"Integrity verification failed for {target}")

    state["generated_at"] = utc_now()
    state["complete"] = all(
        value["status"] in {"verified", "metadata_only"}
        for value in state["files"].values()
    )
    atomic_json(state_path, state)
    print(json.dumps({"state": str(state_path), "complete": state["complete"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
