from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


SCHEMA = "strict_v4_rrc_csr_realtime_progress_snapshot_v1"
ARTIFACTS = {
    "base_csr_captures": (
        "base_csr_captures",
        "capture_manifest.json",
    ),
    "rrc_runtime_captures": (
        "rrc_runtime_captures",
        "capture_manifest.json",
    ),
    "scenario_certificates": (
        "scenario_certificates",
        "certificate.json",
    ),
    "evaluations": ("evaluations", "evaluation.json"),
}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def write_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def inspect_artifacts(
    run_root: Path,
    directory: str,
    filename: str,
) -> dict[str, Any]:
    base = run_root / directory
    records = []
    invalid = []
    pending = []
    for path in sorted(base.rglob(filename)) if base.is_dir() else []:
        relative = path.relative_to(run_root).as_posix()
        try:
            value = load(path)
            if directory == "base_csr_captures":
                execution_path = path.parent / "capture_execution.json"
                if not execution_path.is_file():
                    pending.append(relative)
                    records.append(
                        {
                            "path": relative,
                            "file_sha256": file_hash(path),
                            "size_bytes": path.stat().st_size,
                            "canonical_valid": False,
                            "pending_companion_execution": True,
                        }
                    )
                    continue
                execution = load(execution_path)
                canonical = bool(
                    value.get("schema_version")
                    == "strict_v4_csr_caeos_runtime_capture_v1"
                    and value.get("state") == "complete"
                    and value.get("algorithm") == "csr_caeos_v1"
                    and value.get("test_effect_metrics_computed") is False
                    and execution.get("schema_version")
                    == "strict_v4_rrc_csr_base_capture_execution_v1"
                    and execution.get("manifest_sha256")
                    == canonical_hash(execution)
                    and execution.get("state") == "complete"
                    and execution.get("task") == value.get("task")
                    and int(execution.get("training_seed", -1))
                    == int(value.get("training_seed", -2))
                    and execution.get("capture_manifest_file_sha256")
                    == file_hash(path)
                    and float(
                        execution.get("total_capture_wall_seconds", -1.0)
                    )
                    > 0.0
                )
            else:
                canonical = (
                    value.get("manifest_sha256") == canonical_hash(value)
                )
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
            canonical = False
        record = {
            "path": relative,
            "file_sha256": file_hash(path),
            "size_bytes": path.stat().st_size,
            "canonical_valid": canonical,
        }
        if directory == "base_csr_captures":
            execution_path = path.parent / "capture_execution.json"
            if execution_path.is_file():
                record["companion_execution_path"] = (
                    execution_path.relative_to(run_root).as_posix()
                )
                record["companion_execution_file_sha256"] = file_hash(
                    execution_path
                )
        records.append(record)
        if not canonical:
            invalid.append(relative)
    return {
        "observed_count": len(records),
        "present_count": sum(
            record["canonical_valid"] for record in records
        ),
        "canonical_valid_count": sum(
            record["canonical_valid"] for record in records
        ),
        "pending_count": len(pending),
        "pending_paths": pending,
        "invalid_count": len(invalid),
        "invalid_paths": invalid,
        "records": records,
    }


def build_snapshot(
    protocol_path: Path,
    run_root: Path,
) -> dict[str, Any]:
    protocol = load(protocol_path)
    if (
        protocol.get("schema_version")
        != "strict_v4_rrc_csr_execution_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("canonical RRC execution protocol required")
    expected = protocol.get("task_counts", {})
    inventory = {}
    for name, (directory, filename) in ARTIFACTS.items():
        item = inspect_artifacts(run_root, directory, filename)
        item["expected_count"] = int(expected[name])
        item["complete"] = bool(
            item["present_count"] == item["expected_count"]
            and item["invalid_count"] == 0
            and item["pending_count"] == 0
        )
        inventory[name] = item
    invalid_count = sum(item["invalid_count"] for item in inventory.values())
    all_complete = all(item["complete"] for item in inventory.values())
    result: dict[str, Any] = {
        "schema_version": SCHEMA,
        "state": (
            "complete_filesystem_inventory"
            if all_complete
            else "invalid_partial_progress"
            if invalid_count
            else "valid_partial_progress"
        ),
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "protocol_file_sha256": file_hash(protocol_path),
        "run_root": run_root.resolve().as_posix(),
        "inventory": inventory,
        "invalid_artifact_count": invalid_count,
        "pending_artifact_count": sum(
            item["pending_count"] for item in inventory.values()
        ),
        "all_expected_artifacts_complete": all_complete,
        "effect_aggregation_performed": False,
        "effect_conclusion_available_from_this_snapshot": False,
        "claim_boundary": {
            "partial_counts_are_execution_progress_only": True,
            "formal_summary_and_independent_audit_are_required_for_effect": True,
            "observer_is_not_part_of_the_frozen_rrc_algorithm_closure": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    snapshot = build_snapshot(args.protocol, args.run_root)
    write_atomic(args.output, snapshot)
    print(
        json.dumps(
            {
                "state": snapshot["state"],
                "manifest_sha256": snapshot["manifest_sha256"],
                "output": str(args.output.resolve()),
                "counts": {
                    name: item["present_count"]
                    for name, item in snapshot["inventory"].items()
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
