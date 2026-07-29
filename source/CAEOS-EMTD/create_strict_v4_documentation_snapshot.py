from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


SCHEMA = "strict_v4_documentation_snapshot_v1"
REQUIRED_DOCUMENTS = (
    "README.md",
    "02_实验设计/01_核心协议/创新点与基线对比矩阵.md",
    (
        "03_实验报告/01_主线验证/"
        "strict-v4全面SOTA与自有算法优化阶段报告.md"
    ),
    "06_阶段性评价/CAEOS-EMTD评价意见吸收与纠偏记录_2026-07-27.md",
)


def safe_relative_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"unsafe documentation path: {value}")
    return path


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def create_snapshot(
    documentation_root: Path, output_root: Path
) -> dict[str, Any]:
    documentation_root = documentation_root.resolve()
    output_root = output_root.resolve()
    records = []
    for value in REQUIRED_DOCUMENTS:
        relative = safe_relative_path(value)
        source = documentation_root / relative
        if not source.is_file():
            raise FileNotFoundError(f"required documentation is absent: {source}")
        target = output_root / "files" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(target.suffix + ".tmp")
        shutil.copyfile(source, temporary)
        os.replace(temporary, target)
        if file_hash(source) != file_hash(target):
            raise ValueError(f"documentation snapshot copy drifted: {relative}")
        records.append(
            {
                "relative_path": relative.as_posix(),
                "size_bytes": target.stat().st_size,
                "sha256": file_hash(target),
            }
        )
    result: dict[str, Any] = {
        "schema_version": SCHEMA,
        "state": "complete",
        "required_document_count": len(REQUIRED_DOCUMENTS),
        "documents": records,
        "claim_boundary": {
            "snapshot_proves_document_bytes_not_scientific_effect": True,
            "source_machine_path_is_not_part_of_identity": True,
            "all_required_documents_are_copied_and_hash_bound": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    write_json(output_root / "manifest.json", result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--documentation-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = create_snapshot(args.documentation_root, args.output_root)
    print(
        json.dumps(
            {
                "state": result["state"],
                "document_count": len(result["documents"]),
                "manifest_sha256": result["manifest_sha256"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
