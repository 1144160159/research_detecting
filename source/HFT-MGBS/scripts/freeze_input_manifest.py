"""Freeze hashes for every file referenced by experiment manifests."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def referenced_paths(manifest_paths):
    paths = set()
    for manifest_path in manifest_paths:
        manifest_path = Path(manifest_path).resolve()
        paths.add(manifest_path)
        with manifest_path.open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)
        ground_truth = manifest.get("ground_truth_csv")
        if ground_truth:
            paths.add(Path(ground_truth).resolve())
        for sample in manifest.get("samples", []):
            paths.add(Path(sample["path"]).resolve())
    return sorted(paths, key=str)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifests", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    entries = []
    for path in referenced_paths(args.manifests):
        if not path.is_file():
            parser.error("referenced input is not a file: {}".format(path))
        entries.append(
            {
                "path": str(path),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    output = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "algorithm": "sha256",
        "entry_count": len(entries),
        "entries": entries,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
