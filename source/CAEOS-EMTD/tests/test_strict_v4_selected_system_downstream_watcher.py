from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
import watch_strict_v4_selected_system_downstream as target


def canonical(value: dict[str, Any]) -> dict[str, Any]:
    value["manifest_sha256"] = canonical_hash(value)
    return value


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def goal() -> dict[str, Any]:
    return canonical(
        {
            "schema_version": "strict_v4_current_goal_status_audit_v1",
            "selected_algorithm": "caeos_pairwise",
        }
    )


def activation(
    goal_value: dict[str, Any], goal_file_sha256: str
) -> dict[str, Any]:
    snapshot = {
        "final": True,
        "selected_algorithm": "caeos_pairwise",
    }
    return canonical(
        {
            "schema_version": "strict_v4_selected_system_activation_v1",
            "execution_admitted": True,
            "selected_algorithm": "caeos_pairwise",
            "selection_snapshot": snapshot,
            "selection_snapshot_sha256": canonical_hash(snapshot),
            "input_manifest_sha256": {
                "current_goal_audit": goal_value["manifest_sha256"]
            },
            "input_file_sha256": {
                "current_goal_audit": goal_file_sha256
            },
        }
    )


def roots(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "project"
    result = (
        root / "results/strict_v4_selected_system_downstream_adapter_v1"
    )
    result.mkdir(parents=True)
    return root, result


def test_busy_process_detection_excludes_watcher_itself() -> None:
    commands = [
        "python train_hybrid_open_set.py --seed 1",
        (
            "python watch_strict_v4_selected_system_downstream.py "
            "--project-root /x"
        ),
        "python unrelated.py",
    ]
    assert target.busy_commands(commands) == [
        "python train_hybrid_open_set.py --seed 1"
    ]


def test_goal_audit_refresh_precedes_final_activation() -> None:
    root = Path("/tmp/project")
    command = target.goal_audit_refresh_command(root)
    assert command[1:] == [
        str(root / "audit_strict_v4_current_goal_status.py"),
        "--project-root",
        str(root),
        "--output",
        str(root / "results/strict_v4_current_goal_status_v1/audit.json"),
    ]


def test_resource_gate_requires_three_complete_idle_samples() -> None:
    idle = 0
    for expected in (1, 2, 3):
        state, idle = target.resource_state(
            prior_idle_count=idle,
            required_idle_polls=3,
            max_load_fraction=0.25,
            commands=[],
            load1=2.0,
            logical_cpu_count=64,
            gpu_pids=[],
        )
        assert idle == expected
        assert state["launch_admitted"] is (expected == 3)
        assert state["manifest_sha256"] == canonical_hash(state)


def test_resource_gate_fails_closed_on_load_gpu_or_observability(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    high_load, count = target.resource_state(
        prior_idle_count=2,
        required_idle_polls=3,
        max_load_fraction=0.25,
        commands=[],
        load1=20.0,
        logical_cpu_count=64,
        gpu_pids=[],
    )
    assert count == 0
    assert high_load["load_gate_passes"] is False
    gpu_busy, count = target.resource_state(
        prior_idle_count=2,
        required_idle_polls=3,
        max_load_fraction=0.25,
        commands=[],
        load1=1.0,
        logical_cpu_count=64,
        gpu_pids=[123],
    )
    assert count == 0
    assert gpu_busy["gpu_gate_passes"] is False
    monkeypatch.setattr(target, "gpu_compute_pids", lambda: None)
    unobservable, count = target.resource_state(
        prior_idle_count=2,
        required_idle_polls=3,
        max_load_fraction=0.25,
        commands=[],
        load1=1.0,
        logical_cpu_count=64,
    )
    assert count == 0
    assert unobservable["gpu_gate_observable"] is False
    assert unobservable["gpu_gate_passes"] is False


def test_inspect_once_is_read_only_without_activation(
    tmp_path: Path,
) -> None:
    root, _result = roots(tmp_path)
    state, idle = target.inspect_once(
        root,
        commands=[],
        load1=1.0,
        logical_cpu_count=64,
        gpu_pids=[],
    )
    assert idle == 0
    assert state == {
        "state": "waiting_for_final_selection_activation",
        "launch_admitted": False,
    }


def test_activation_goal_snapshot_is_byte_exact(
    tmp_path: Path,
) -> None:
    root, result = roots(tmp_path)
    goal_path = root / "results/strict_v4_current_goal_status_v1/audit.json"
    goal_value = goal()
    write(goal_path, goal_value)
    activation_value = activation(goal_value, file_hash(goal_path))
    write(result / "activation.json", activation_value)
    snapshot = target.freeze_goal_snapshot(
        root, result, activation_value
    )
    assert snapshot.read_bytes() == goal_path.read_bytes()
    state = target.prerequisite_state(root, result)
    assert state == {
        "state": "waiting_for_external_input_protocol",
        "launch_admitted": False,
    }


def test_goal_snapshot_drift_fails_closed(tmp_path: Path) -> None:
    root, result = roots(tmp_path)
    goal_path = root / "results/strict_v4_current_goal_status_v1/audit.json"
    goal_value = goal()
    write(goal_path, goal_value)
    activation_value = activation(goal_value, "0" * 64)
    with pytest.raises(ValueError, match="no longer matches"):
        target.freeze_goal_snapshot(root, result, activation_value)


def test_terminal_completion_is_retained(tmp_path: Path) -> None:
    root, result = roots(tmp_path)
    completion = canonical(
        {
            "schema_version": target.COMPLETION_SCHEMA,
            "state": "complete",
        }
    )
    write(result / "execution_complete.json", completion)
    state = target.prerequisite_state(root, result)
    assert state == {
        "state": "terminal_completion_present",
        "launch_admitted": False,
    }
