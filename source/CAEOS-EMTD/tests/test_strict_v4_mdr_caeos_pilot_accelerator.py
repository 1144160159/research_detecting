from pathlib import Path

import pytest

from accelerate_strict_v4_mdr_caeos_pilot_captures import (
    validate_paused_pilot_snapshot,
)


def test_paused_pilot_snapshot_accepts_only_zombie_child():
    validate_paused_pilot_snapshot(
        {
            "state": "T",
            "cmdline": "python run_strict_v4_mdr_caeos_pilot.py",
            "direct_children": [{"pid": 9, "state": "Z"}],
        }
    )


def test_paused_pilot_snapshot_rejects_active_child():
    with pytest.raises(ValueError, match="active children"):
        validate_paused_pilot_snapshot(
            {
                "state": "T",
                "cmdline": "python run_strict_v4_mdr_caeos_pilot.py",
                "direct_children": [{"pid": 9, "state": "R"}],
            }
        )


def test_paused_pilot_snapshot_rejects_wrong_process():
    with pytest.raises(ValueError, match="unexpected"):
        validate_paused_pilot_snapshot(
            {
                "state": "T",
                "cmdline": "python another_runner.py",
                "direct_children": [],
            }
        )


def test_coordinator_restores_authoritative_runner():
    path = (
        Path(__file__).parents[1]
        / "scripts"
        / "run_strict_v4_mdr_caeos_pilot_capture_accelerator.sh"
    )
    text = path.read_text(encoding="utf-8")
    assert "trap resume_serial EXIT INT TERM" in text
    assert 'kill -STOP "$SERIAL_PID"' in text
    assert 'kill -CONT "$SERIAL_PID"' in text
    assert "changes_training_arguments" not in text
