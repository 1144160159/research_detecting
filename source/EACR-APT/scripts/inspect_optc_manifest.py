#!/usr/bin/env python3
"""Print the shape and a small sample of the saved OpTC Drive manifest."""

import json
from pathlib import Path


MANIFEST = Path(
    "/opt/data/private/wangwt/ParkAttackKE/datasets/apt_public/optc/"
    "manifests/gdrive_file_tree.json"
)
DOWNLOAD_ROOT = Path(
    "/opt/data/private/wangwt/ParkAttackKE/datasets/apt_public/optc/raw_original"
)


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    print("type", type(data).__name__)
    if isinstance(data, dict):
        print("keys", sorted(data))
        for key, value in data.items():
            if isinstance(value, list):
                print("list", key, len(value))
                if value:
                    print("sample", json.dumps(value[0], ensure_ascii=False)[:3000])
                break
    elif isinstance(data, list):
        print("length", len(data))
        if data:
            print("sample", json.dumps(data[0], ensure_ascii=False)[:3000])

    if not isinstance(data, dict) or not isinstance(data.get("files"), list):
        return

    root_only = 0
    nested_only = 0
    both = 0
    missing: list[str] = []
    expected_locations: set[Path] = set()
    for item in data["files"]:
        relative = Path(item["path"])
        root_path = DOWNLOAD_ROOT / relative
        nested_path = DOWNLOAD_ROOT / "OpTCNCR" / relative
        expected_locations.update((root_path, nested_path))
        at_root = root_path.is_file()
        at_nested = nested_path.is_file()
        if at_root and at_nested:
            both += 1
        elif at_root:
            root_only += 1
        elif at_nested:
            nested_only += 1
        else:
            missing.append(item["path"])

    actual_files = [path for path in DOWNLOAD_ROOT.rglob("*") if path.is_file()]
    extras = [path for path in actual_files if path not in expected_locations]
    covered = len(data["files"]) - len(missing)
    print("covered", covered)
    print("missing", len(missing))
    print("root_only", root_only)
    print("nested_only", nested_only)
    print("both", both)
    print("actual_files", len(actual_files))
    print("extras", len(extras))
    print("missing_sample", json.dumps(missing[:20], ensure_ascii=False))
    print(
        "extras_sample",
        json.dumps(
            [str(path.relative_to(DOWNLOAD_ROOT)) for path in extras[:20]],
            ensure_ascii=False,
        ),
    )


if __name__ == "__main__":
    main()
