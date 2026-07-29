import json
from pathlib import Path

import pytest

from reschedule_strict_v4_rrc_at_task_boundary import (
    canonical_hash,
    capture_is_complete,
    file_hash,
    process_group_members,
    replace_workers,
)


def test_replace_workers_updates_existing_override() -> None:
    command = ["python", "runner.py", "--workers", "1", "--flag"]
    assert replace_workers(command, 4) == [
        "python",
        "runner.py",
        "--workers",
        "4",
        "--flag",
    ]
    assert command[3] == "1"


def test_replace_workers_appends_missing_override() -> None:
    assert replace_workers(["python", "runner.py"], 4) == [
        "python",
        "runner.py",
        "--workers",
        "4",
    ]


def test_replace_workers_rejects_missing_value() -> None:
    with pytest.raises(ValueError, match="has no value"):
        replace_workers(["python", "runner.py", "--workers"], 4)


def test_capture_completion_uses_execution_file_binding(tmp_path: Path) -> None:
    manifest_path = tmp_path / "capture_manifest.json"
    manifest = {
        "schema_version": "strict_v4_csr_caeos_runtime_capture_v1",
        "state": "complete",
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    execution_path = tmp_path / "capture_execution.json"
    execution = {
        "schema_version": "strict_v4_rrc_csr_base_capture_execution_v1",
        "state": "complete",
        "capture_manifest_file_sha256": file_hash(manifest_path),
    }
    execution["manifest_sha256"] = canonical_hash(execution)
    execution_path.write_text(json.dumps(execution), encoding="utf-8")
    assert capture_is_complete(tmp_path)


def test_process_group_members_returns_a_list() -> None:
    assert process_group_members(-1) == []
