"""Collect selected Dataverse files on the GPU and verify source checksums."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote
from urllib.request import Request, urlopen

from collect_zenodo_dataset import atomic_json, digest_file, run_aria2, utc_now


def fetch_dataset(base_url: str, persistent_id: str) -> dict[str, Any]:
    encoded = quote(persistent_id, safe="")
    url = f"{base_url.rstrip('/')}/api/datasets/:persistentId/?persistentId={encoded}"
    request = Request(url, headers={"User-Agent": "EACR-APT-dataset-collector/1.0"})
    with urlopen(request, timeout=180) as response:
        payload = json.load(response)
    if payload.get("status") != "OK":
        raise RuntimeError(f"Dataverse API returned {payload.get('status')!r}")
    return payload


def flatten_files(payload: dict[str, Any]) -> list[dict[str, Any]]:
    version = payload["data"]["latestVersion"]
    return [entry["dataFile"] for entry in version.get("files", [])]


def write_source_files(path: Path, base_url: str, files: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["id", "name", "size_bytes", "source_checksum", "url"])
        for item in files:
            checksum = item["checksum"]
            writer.writerow(
                [
                    int(item["id"]),
                    item["filename"],
                    int(item["filesize"]),
                    f"{checksum['type'].lower()}:{checksum['value'].lower()}",
                    f"{base_url.rstrip('/')}/api/access/datafile/{item['id']}",
                ]
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--persistent-id", required=True)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--file-ids", nargs="*", type=int, default=None)
    parser.add_argument("--connections", type=int, default=4)
    parser.add_argument("--metadata-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    raw_dir = root / "raw"
    metadata_dir = root / "metadata"
    manifest_dir = root / "manifests"
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
    state: dict[str, Any] = {
        "persistent_id": args.persistent_id,
        "generated_at": utc_now(),
        "root": str(root),
        "selection_size_bytes": sum(int(item["filesize"]) for item in files),
        "files": {},
    }
    state_path = manifest_dir / "collection_state.json"

    for item in files:
        file_id = int(item["id"])
        name = str(item["filename"])
        checksum = item["checksum"]
        expected_algorithm = str(checksum["type"]).lower()
        expected_digest = str(checksum["value"]).lower()
        target = raw_dir / name
        url = f"{args.base_url.rstrip('/')}/api/access/datafile/{file_id}"
        entry: dict[str, Any] = {
            "id": file_id,
            "size_expected": int(item["filesize"]),
            "source_checksum": f"{expected_algorithm}:{expected_digest}",
            "url": url,
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
            run_aria2(url, target, max(1, args.connections))

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
