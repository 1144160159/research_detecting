from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from caeos_unified_dataset import atomic_json, sha256_file


def replace_paths(value: Any, replacements: list[tuple[str, str]]) -> Any:
    if isinstance(value, dict):
        return {key: replace_paths(item, replacements) for key, item in value.items()}
    if isinstance(value, list):
        return [replace_paths(item, replacements) for item in value]
    if isinstance(value, str):
        for old, new in replacements:
            if value == old or value.startswith(old + "/"):
                return new + value[len(old) :]
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-run", required=True, type=Path)
    parser.add_argument("--destination-run", required=True, type=Path)
    parser.add_argument("--source-index", required=True, type=Path)
    parser.add_argument("--destination-index", required=True, type=Path)
    parser.add_argument("--index-audit-name", required=True)
    parser.add_argument("--extra-root", action="append", default=[], type=Path)
    args = parser.parse_args()
    args.destination_run.mkdir(parents=True, exist_ok=True)
    args.destination_index.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.source_index, args.destination_index)
    source_sha = sha256_file(args.source_index)
    destination_sha = sha256_file(args.destination_index)
    if source_sha != destination_sha:
        raise ValueError("persisted label index checksum mismatch")
    for name in ("audits", "logs"):
        source = args.source_run / name
        if source.exists():
            shutil.copytree(source, args.destination_run / name, dirs_exist_ok=True)
    for name in ("inventory.json", "summary.json"):
        source = args.source_run / name
        if source.exists():
            shutil.copy2(source, args.destination_run / name)
    replacements = [
        (str(args.source_index), str(args.destination_index)),
        (str(args.source_run), str(args.destination_run)),
    ]
    for extra in args.extra_root:
        destination = args.destination_run / "external_evidence" / extra.name
        shutil.copytree(extra, destination, dirs_exist_ok=True)
        replacements.append((str(extra), str(destination)))
    for path in args.destination_run.rglob("*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        atomic_json(path, replace_paths(payload, replacements))
    index_audit = args.destination_run / "audits" / args.index_audit_name
    payload = json.loads(index_audit.read_text(encoding="utf-8"))
    label_index = payload["label_index"]
    label_index["path"] = str(args.destination_index)
    label_index["sha256"] = destination_sha
    label_index["size_bytes"] = args.destination_index.stat().st_size
    atomic_json(index_audit, payload)
    print(
        json.dumps(
            {
                "destination_index": str(args.destination_index),
                "destination_index_sha256": destination_sha,
                "destination_run": str(args.destination_run),
                "index_audit": str(index_audit),
                "summary": str(args.destination_run / "summary.json"),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
