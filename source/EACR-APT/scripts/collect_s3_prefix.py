"""Collect a public S3 prefix into a GPU-only dataset directory.

The collector uses S3's unauthenticated ListObjectsV2 endpoint, preserves the
object hierarchy below ``--prefix``, resumes transfers with aria2, and writes
all runtime metadata below the remote ``--root``.  It is intended for public
research datasets such as Unraveled/DAPT2021; raw data must never be synced
back to the local source tree.
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
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree


S3_NAMESPACE = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, path)


def endpoint(bucket: str) -> str:
    return f"https://{bucket}.s3.amazonaws.com"


def list_objects(bucket: str, prefix: str) -> list[dict[str, Any]]:
    objects: list[dict[str, Any]] = []
    continuation: str | None = None
    while True:
        query: dict[str, str] = {"list-type": "2", "prefix": prefix}
        if continuation:
            query["continuation-token"] = continuation
        url = f"{endpoint(bucket)}/?{urlencode(query)}"
        request = Request(url, headers={"User-Agent": "EACR-APT-dataset-collector/1.0"})
        with urlopen(request, timeout=120) as response:
            document = ElementTree.fromstring(response.read())

        for content in document.findall("s3:Contents", S3_NAMESPACE):
            key = content.findtext("s3:Key", namespaces=S3_NAMESPACE)
            size_text = content.findtext("s3:Size", namespaces=S3_NAMESPACE)
            etag = content.findtext("s3:ETag", namespaces=S3_NAMESPACE)
            if not key or size_text is None or int(size_text) == 0:
                continue
            objects.append(
                {
                    "key": key,
                    "size": int(size_text),
                    "etag": (etag or "").strip('"'),
                    "url": f"{endpoint(bucket)}/{quote(key, safe='/')}",
                }
            )

        truncated = document.findtext("s3:IsTruncated", default="false", namespaces=S3_NAMESPACE)
        if truncated.lower() != "true":
            break
        continuation = document.findtext("s3:NextContinuationToken", namespaces=S3_NAMESPACE)
        if not continuation:
            raise RuntimeError("S3 listing is truncated but has no continuation token")
    return objects


def relative_object_path(key: str, prefix: str) -> Path:
    relative = key[len(prefix) :] if key.startswith(prefix) else key
    relative = relative.lstrip("/")
    parts = PurePosixPath(relative).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"Unsafe S3 object key: {key!r}")
    return Path(*parts)


def digest_file(path: Path, include_md5: bool) -> dict[str, str]:
    hashers = {"sha256": hashlib.sha256()}
    if include_md5:
        hashers["md5"] = hashlib.md5()
    with path.open("rb") as handle:
        while chunk := handle.read(16 * 1024 * 1024):
            for hasher in hashers.values():
                hasher.update(chunk)
    return {name: hasher.hexdigest() for name, hasher in hashers.items()}


def write_source_manifest(path: Path, objects: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["key", "size_bytes", "etag", "url"])
        for item in objects:
            writer.writerow([item["key"], item["size"], item["etag"], item["url"]])


def write_aria2_input(
    path: Path,
    objects: list[dict[str, Any]],
    raw_dir: Path,
    prefix: str,
) -> int:
    pending = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for item in objects:
            target = raw_dir / relative_object_path(item["key"], prefix)
            if target.exists() and target.stat().st_size == item["size"]:
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            handle.write(f"{item['url']}\n")
            handle.write(f"  dir={target.parent}\n")
            handle.write(f"  out={target.name}\n")
            pending += 1
    return pending


def run_aria2(input_file: Path, jobs: int, connections: int) -> None:
    command = [
        "aria2c",
        f"--input-file={input_file}",
        "--continue=true",
        "--auto-file-renaming=false",
        "--allow-overwrite=false",
        "--file-allocation=none",
        f"--max-concurrent-downloads={jobs}",
        f"--max-connection-per-server={connections}",
        f"--split={connections}",
        "--min-split-size=16M",
        "--max-tries=0",
        "--retry-wait=15",
        "--connect-timeout=30",
        "--timeout=120",
        "--summary-interval=60",
    ]
    subprocess.run(command, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--root", required=True, type=Path, help="GPU-only dataset root")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--connections", type=int, default=2)
    parser.add_argument("--expected-bytes", type=int)
    parser.add_argument("--metadata-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    raw_dir = root / "raw"
    manifest_dir = root / "manifests"
    raw_dir.mkdir(parents=True, exist_ok=True)
    manifest_dir.mkdir(parents=True, exist_ok=True)

    objects = list_objects(args.bucket, args.prefix)
    expected_total = sum(item["size"] for item in objects)
    if args.expected_bytes is not None and expected_total != args.expected_bytes:
        raise RuntimeError(
            f"S3 listing drift: expected {args.expected_bytes} bytes, found {expected_total}"
        )
    write_source_manifest(manifest_dir / "source_files.tsv", objects)

    state: dict[str, Any] = {
        "bucket": args.bucket,
        "prefix": args.prefix,
        "source_url": f"{endpoint(args.bucket)}/?{urlencode({'list-type': '2', 'prefix': args.prefix})}",
        "generated_at": utc_now(),
        "root": str(root),
        "expected_bytes": expected_total,
        "files": {},
    }
    state_path = manifest_dir / "collection_state.json"
    for item in objects:
        relative = relative_object_path(item["key"], args.prefix)
        state["files"][relative.as_posix()] = {
            "key": item["key"],
            "url": item["url"],
            "etag": item["etag"],
            "size_expected": item["size"],
            "status": "metadata_only" if args.metadata_only else "pending",
        }
    atomic_json(state_path, state)

    if not args.metadata_only:
        input_file = manifest_dir / "aria2_input.txt"
        pending = write_aria2_input(input_file, objects, raw_dir, args.prefix)
        if pending:
            state["active_downloads"] = pending
            atomic_json(state_path, state)
            run_aria2(input_file, max(1, args.jobs), max(1, args.connections))

        for relative_name, entry in state["files"].items():
            target = raw_dir / Path(relative_name)
            entry["status"] = "verifying"
            atomic_json(state_path, state)
            size_actual = target.stat().st_size
            simple_etag = bool(entry["etag"] and "-" not in entry["etag"])
            digests = digest_file(target, include_md5=simple_etag)
            verified = size_actual == entry["size_expected"]
            if simple_etag:
                verified = verified and digests["md5"].lower() == entry["etag"].lower()
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

    state.pop("active_downloads", None)
    state["generated_at"] = utc_now()
    state["complete"] = all(
        entry["status"] in {"verified", "metadata_only"}
        for entry in state["files"].values()
    )
    atomic_json(state_path, state)
    print(json.dumps({"state": str(state_path), "complete": state["complete"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
