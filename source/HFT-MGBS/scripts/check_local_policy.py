"""Fail when GPU-only artifacts appear in the local code repository."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_DIRS = {
    "data",
    "dataset",
    "datasets",
    "captures",
    "features",
    "weights",
    "models",
    "checkpoints",
    "model_artifacts",
    "runs",
    "results",
    "artifacts",
    "outputs",
    "logs",
    "profiles",
}
IGNORED_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "build", "dist"}
FORBIDDEN_SUFFIXES = {
    ".pt", ".pth", ".ckpt", ".onnx", ".safetensors", ".h5",
    ".pkl", ".pickle", ".joblib", ".npy", ".npz", ".parquet",
    ".feather", ".arrow", ".pcap", ".pcapng", ".csv", ".tsv",
    ".jsonl", ".zip", ".7z", ".rar",
}
MAX_LOCAL_FILE_BYTES = 10 * 1024 * 1024


def find_violations(root: Path = ROOT):
    violations = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        lowered_parts = {part.lower() for part in relative.parts}
        if lowered_parts & IGNORED_DIRS:
            continue
        if lowered_parts & FORBIDDEN_DIRS:
            if path.is_file():
                violations.append({"path": relative.as_posix(), "reason": "forbidden_directory"})
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            violations.append({"path": relative.as_posix(), "reason": "forbidden_suffix"})
        elif path.stat().st_size > MAX_LOCAL_FILE_BYTES:
            violations.append({"path": relative.as_posix(), "reason": "file_over_10MiB"})
    return violations


def main() -> int:
    violations = find_violations()
    print(json.dumps({"root": str(ROOT), "violations": violations}, ensure_ascii=False, indent=2))
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
