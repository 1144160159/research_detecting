from __future__ import annotations

from pathlib import Path

import pytest

import resume_paused_medaf_after_mdr_confirmation as module


def test_validate_paused_medaf_requires_command_and_stopped_state(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        module,
        "process_command",
        lambda pid: (
            "bash scripts/wait_and_run_strict_v4_medaf_tabular_pilot.sh"
        ),
    )
    monkeypatch.setattr(module, "process_state", lambda pid: "T")
    value = module.validate_paused_medaf(123)
    assert value["state"] == "T"

    monkeypatch.setattr(module, "process_state", lambda pid: "S")
    with pytest.raises(ValueError, match="must be stopped"):
        module.validate_paused_medaf(123)


def test_validate_paused_medaf_rejects_wrong_process(monkeypatch) -> None:
    monkeypatch.setattr(
        module, "process_command", lambda pid: "bash unrelated.sh"
    )
    monkeypatch.setattr(module, "process_state", lambda pid: "T")
    with pytest.raises(ValueError, match="not the MEDAF watcher"):
        module.validate_paused_medaf(123)


def test_expected_marker_is_explicit(tmp_path: Path) -> None:
    marker = tmp_path / "branch_complete"
    assert not marker.exists()
    marker.write_text("audit-sha\n", encoding="utf-8")
    assert marker.is_file()
