from pathlib import Path

import pytest

from accelerate_strict_v4_comparative_final_gap import (
    validate_paused_serial_snapshot,
)


def test_paused_serial_snapshot_accepts_only_zombie_children():
    validate_paused_serial_snapshot(
        {
            "state": "T",
            "cmdline": (
                "python run_strict_v4_comparative_corruption.py --protocol x"
            ),
            "direct_children": [{"pid": 7, "state": "Z"}],
        }
    )


def test_paused_serial_snapshot_rejects_running_parent():
    with pytest.raises(ValueError, match="not stopped"):
        validate_paused_serial_snapshot(
            {
                "state": "S",
                "cmdline": "python run_strict_v4_comparative_corruption.py",
                "direct_children": [],
            }
        )


def test_paused_serial_snapshot_rejects_active_child():
    with pytest.raises(ValueError, match="active direct children"):
        validate_paused_serial_snapshot(
            {
                "state": "T",
                "cmdline": "python run_strict_v4_comparative_corruption.py",
                "direct_children": [{"pid": 8, "state": "R"}],
            }
        )


def test_paused_serial_snapshot_rejects_wrong_command():
    with pytest.raises(ValueError, match="unexpected"):
        validate_paused_serial_snapshot(
            {
                "state": "T",
                "cmdline": "python another_experiment.py",
                "direct_children": [],
            }
        )


def test_coordinator_always_has_resume_trap():
    path = (
        Path(__file__).parents[1]
        / "scripts"
        / "run_strict_v4_comparative_final_gap.sh"
    )
    text = path.read_text(encoding="utf-8")
    assert "trap resume_serial EXIT INT TERM" in text
    assert 'kill -STOP "$SERIAL_PID"' in text
    assert 'kill -CONT "$SERIAL_PID"' in text
    assert "minimum_source_index=$((frontier + 1))" in text
