from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_hash(payload: dict[str, Any]) -> str:
    body = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def verify_canonical(payload: dict[str, Any]) -> None:
    declared = payload.get("manifest_sha256")
    body = dict(payload)
    body.pop("manifest_sha256", None)
    if not isinstance(declared, str) or canonical_hash(body) != declared:
        raise ValueError("protocol canonical manifest mismatch")


def snapshot(project_root: Path, protocol_path: Path) -> dict[str, Any]:
    project_root = project_root.resolve()
    protocol = load(protocol_path)
    verify_canonical(protocol)
    run_root = project_root / protocol["execution"]["run_root"]
    result_root = project_root / protocol["execution"]["result_root"]
    cache_root = project_root / protocol["data"]["cache_root"]
    seeds = [int(value) for value in protocol["seeds"]]
    max_per_class = int(protocol["data"]["cache_max_per_class"])
    cache_files = [
        cache_root / f"seed{seed}_max{max_per_class}.csv" for seed in seeds
    ]
    metric_files = list(run_root.rglob("metrics.json")) if run_root.exists() else []
    failure_files = list(run_root.rglob("failure.json")) if run_root.exists() else []
    evidence_files = (
        list(run_root.rglob("evidence_package.npz")) if run_root.exists() else []
    )
    provenance_files = (
        list(run_root.rglob("provenance.json")) if run_root.exists() else []
    )
    expected_tasks = int(protocol["expected_task_count"])
    result_files = {
        name: (result_root / name).is_file()
        for name in ("evaluation.json", "audit.json", "completion.json")
    }
    payload: dict[str, Any] = {
        "schema_version": "strict_v4_core_warning_progress_v1",
        "state": (
            "complete"
            if result_files["completion.json"]
            else "valid_partial_progress"
        ),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "counts": {
            "cache_csv": sum(path.is_file() for path in cache_files),
            "cache_sidecar": sum(
                path.with_suffix(path.suffix + ".json").is_file()
                for path in cache_files
            ),
            "metrics": len(metric_files),
            "evidence_packages": len(evidence_files),
            "provenance": len(provenance_files),
            "failures": len(failure_files),
            "expected_tasks": expected_tasks,
        },
        "result_files": result_files,
        "coverage_valid_so_far": (
            len(failure_files) == 0
            and len(metric_files) <= expected_tasks
            and len(evidence_files) <= expected_tasks
            and len(provenance_files) <= expected_tasks
        ),
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = snapshot(args.project_root, args.protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
