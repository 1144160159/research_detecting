import json
from pathlib import Path

from create_strict_v4_xgboost_warning_protocol import (
    IMPLEMENTATION_FILES,
    canonical_hash,
    create_protocol,
)


def test_xgboost_protocol_is_basic_gate_anchor_only(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    for relative in IMPLEMENTATION_FILES:
        (project / relative).write_text(relative, encoding="utf-8")
    parent = project / "results/core/execution_protocol.json"
    parent.parent.mkdir(parents=True)
    parent_payload = {
        "schema_version": "strict_v4_core_warning_execution_protocol_v1",
        "status": "frozen_zero_result_before_fresh_confirmation",
        "seeds": [907, 911, 919],
        "scenarios": ["bot"],
        "expected_task_count": 3,
        "execution": {"run_root": "runs/pairwise"},
        "data": {"cache_root": "caches/core", "config": "/data/config.json"},
        "development_selection": {
            "selected_validation_benign_fpr_budget": 0.04
        },
    }
    parent_payload["manifest_sha256"] = canonical_hash(parent_payload)
    parent.write_text(json.dumps(parent_payload), encoding="utf-8")
    xgboost_root = tmp_path / "xgboost"
    xgboost_root.mkdir()

    protocol = create_protocol(
        project_root=project,
        parent_protocol_path=parent,
        xgboost_root=xgboost_root,
        xgboost_version="2.1.4",
        run_root=project / "runs/xgboost",
        result_root=project / "results/xgboost",
    )

    assert protocol["expected_task_count"] == 3
    assert protocol["baseline_role"]["eligible_for_basic_warning_gate"] is True
    assert protocol["baseline_role"]["eligible_for_full_open_set_gate"] is False
    assert protocol["anti_leakage"]["same_pairwise_split_arrays_required"]
    assert protocol["execution"]["parallel_tasks"] == 1


def test_xgboost_protocol_can_freeze_parallel_orchestration(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    runner = "run_strict_v4_xgboost_warning_matrix_parallel.py"
    for relative in (
        "train_strict_v4_xgboost_warning_task.py",
        runner,
        "summarize_strict_v4_xgboost_warning.py",
    ):
        (project / relative).write_text(relative, encoding="utf-8")
    parent = project / "results/core/execution_protocol.json"
    parent.parent.mkdir(parents=True)
    parent_payload = {
        "schema_version": "strict_v4_core_warning_execution_protocol_v1",
        "status": "frozen_zero_result_before_fresh_confirmation",
        "seeds": [907, 911, 919],
        "scenarios": ["bot"],
        "expected_task_count": 3,
        "execution": {"run_root": "runs/pairwise"},
        "data": {"cache_root": "caches/core", "config": "/data/config.json"},
        "development_selection": {
            "selected_validation_benign_fpr_budget": 0.04
        },
    }
    parent_payload["manifest_sha256"] = canonical_hash(parent_payload)
    parent.write_text(json.dumps(parent_payload), encoding="utf-8")
    xgboost_root = tmp_path / "xgboost"
    xgboost_root.mkdir()

    protocol = create_protocol(
        project_root=project,
        parent_protocol_path=parent,
        xgboost_root=xgboost_root,
        xgboost_version="2.1.4",
        run_root=project / "runs/xgboost",
        result_root=project / "results/xgboost",
        runner_file=runner,
        parallel_tasks=8,
    )

    assert protocol["execution"]["runner_file"] == runner
    assert protocol["execution"]["declared_cpu_slots"] == 64
    assert runner in protocol["implementation_sha256"]
