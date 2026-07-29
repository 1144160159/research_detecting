from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from summarize_strict_v4_ronetc_full102 import canonical_hash, file_hash
import watch_strict_v4_ronetc_full102 as target


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def canonical(value: dict[str, Any]) -> dict[str, Any]:
    value["manifest_sha256"] = canonical_hash(value)
    return value


def fixture(tmp_path: Path) -> tuple[Path, dict[str, Any]]:
    root = tmp_path / "project"
    result = root / "results/strict_v4_ronetc_full102_seed7"
    run_root = root / "runs/strict_v4_ronetc_full102_seed7"
    tasks = []
    for index in range(102):
        suite = f"suite_{index % 7}"
        scenario = f"scenario_{index:03d}"
        tasks.append(
            {
                "suite": suite,
                "scenario": scenario,
                "model": "ronetc",
                "seed": 7,
                "output_dir": str(
                    run_root / suite / f"{scenario}_seed7_ronetc"
                ),
            }
        )
    protocol = canonical(
        {
            "schema_version": target.PROTOCOL_SCHEMA,
            "state": "frozen_zero_result",
            "tasks": tasks,
            "command": [
                "python",
                "run_neural_baseline_matrix.py",
                "--models",
                "ronetc",
            ],
            "analysis_contract": {
                "opendetect_root": str(root / "opendetect"),
                "baseline_manifest": str(root / "baseline.json"),
                "full103_summary": str(root / "full.json"),
            },
        }
    )
    protocol_path = result / "protocol.json"
    write(protocol_path, protocol)
    audit = {
        "schema_version": target.PROTOCOL_AUDIT_SCHEMA,
        "protocol_file_sha256": file_hash(protocol_path),
        "protocol_manifest_sha256_claimed": protocol["manifest_sha256"],
        "protocol_manifest_sha256_recomputed": protocol["manifest_sha256"],
        "checks": {"manifest_matches": True, "universe_exact": True},
        "passed": True,
    }
    audit["audit_manifest_sha256"] = canonical_hash(
        audit, field="audit_manifest_sha256"
    )
    write(result / "protocol_audit.json", audit)
    return root, protocol


def final_selection(root: Path) -> None:
    value = canonical(
        {
            "schema_version": target.GOAL_SCHEMA,
            "selected_algorithm": "caeos_pairwise",
            "requirements": {
                "best_self_algorithm_finally_selected": {
                    "satisfied": True,
                    "current_incumbent": "caeos_pairwise",
                }
            },
            "evidence": {
                "self_algorithm_selection": {
                    "final": True,
                    "selected_algorithm": "caeos_pairwise",
                }
            },
        }
    )
    write(
        root / "results/strict_v4_current_goal_status_v1/audit.json",
        value,
    )


def test_waits_for_final_self_algorithm_before_resource_gate(
    tmp_path: Path,
) -> None:
    root, _protocol = fixture(tmp_path)
    state, idle = target.inspect_once(
        root,
        commands=[],
        load1=1.0,
        logical_cpu_count=64,
        gpu_pids=[],
    )
    assert idle == 0
    assert state["state"] == "waiting_for_final_self_algorithm_selection"
    assert state["complete_task_count"] == 0
    assert state["absent_task_count"] == 102


def test_resource_gate_requires_three_idle_observable_polls(
    tmp_path: Path,
) -> None:
    root, _protocol = fixture(tmp_path)
    final_selection(root)
    idle = 0
    for expected in (1, 2, 3):
        state, idle = target.inspect_once(
            root,
            prior_idle_count=idle,
            commands=[],
            load1=2.0,
            logical_cpu_count=64,
            gpu_pids=[],
        )
        assert idle == expected
        assert state["launch_admitted"] is (expected == 3)
        assert state["manifest_sha256"] == canonical_hash(state)


def test_resource_gate_fails_closed_when_gpu_is_unobservable(
    tmp_path: Path, monkeypatch,
) -> None:
    root, _protocol = fixture(tmp_path)
    final_selection(root)
    monkeypatch.setattr(target, "gpu_compute_pids", lambda: None)
    state, idle = target.inspect_once(
        root,
        prior_idle_count=2,
        commands=[],
        load1=1.0,
        logical_cpu_count=64,
    )
    assert idle == 0
    assert state["gpu_gate_observable"] is False
    assert state["gpu_gate_passes"] is False


def test_partial_result_without_provenance_requires_intervention(
    tmp_path: Path,
) -> None:
    root, protocol = fixture(tmp_path)
    final_selection(root)
    output = Path(protocol["tasks"][0]["output_dir"])
    write(output / "metrics.json", {"partial": True})
    state, idle = target.inspect_once(
        root,
        commands=[],
        load1=1.0,
        logical_cpu_count=64,
        gpu_pids=[],
    )
    assert idle == 0
    assert state["state"] == "manual_partial_result_intervention_required"
    assert state["invalid_task_count"] == 1


def test_terminal_completion_is_never_relaunched(tmp_path: Path) -> None:
    root, _protocol = fixture(tmp_path)
    result = root / "results/strict_v4_ronetc_full102_seed7"
    completion = canonical(
        {
            "schema_version": target.COMPLETION_SCHEMA,
            "state": "complete",
            "scenario_count": 102,
            "integrity_passes": True,
        }
    )
    write(result / "execution_complete.json", completion)
    state, idle = target.inspect_once(root)
    assert idle == 0
    assert state["state"] == "terminal_completion_present"
    assert state["completion_manifest_sha256"] == completion[
        "manifest_sha256"
    ]


def test_execution_command_replaces_only_python_launcher(
    tmp_path: Path,
) -> None:
    root, protocol = fixture(tmp_path)
    commands = target.execution_commands(root, protocol)
    assert commands[0][0] == target.sys.executable
    assert commands[0][1:] == protocol["command"][1:]
    assert commands[-1][1].endswith(
        "audit_strict_v4_current_goal_status.py"
    )
