from __future__ import annotations

from watch_strict_v4_comp_cross_suite_confirmation import busy_commands


def test_busy_commands_detects_training_and_ignores_watcher() -> None:
    commands = [
        "python run_nested_gate_matrix.py --suite edge_iiot",
        "python train_neural_open_set.py --model opendetect",
        "python watch_strict_v4_comp_cross_suite_confirmation.py",
        "bash wait_and_run_strict_v4_krc_downstream.sh",
    ]

    busy = busy_commands(commands)

    assert len(busy) == 2
    assert any("run_nested_gate_matrix.py" in value for value in busy)
    assert any("train_neural_open_set.py" in value for value in busy)
    assert not any("watch_strict" in value for value in busy)


def test_busy_commands_detects_krc_coordinator() -> None:
    assert busy_commands(
        ["python run_strict_v4_krc_csr_confirmation.py --workers 4"]
    )
