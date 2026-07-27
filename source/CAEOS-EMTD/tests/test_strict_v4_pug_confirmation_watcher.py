from __future__ import annotations

from watch_strict_v4_pug_confirmation import busy_processes


def test_watcher_detects_krc_and_other_training() -> None:
    lines = [
        "10 python run_strict_v4_krc_csr_confirmation.py --workers 4",
        "11 python run_nested_gate_matrix.py --suite cic_iot2023",
        "13 python run_strict_v4_krc_external_malicious.py --capture-workers 4",
        "14 python train_neural_open_set.py --epochs 100",
        "12 python unrelated.py",
    ]

    busy = busy_processes(lines)

    assert len(busy) == 4
    assert all("unrelated.py" not in row for row in busy)


def test_watcher_detects_rrc_waiter_and_execution_chain() -> None:
    lines = [
        "20 bash scripts/wait_and_run_strict_v4_rrc_csr_confirmation.sh",
        "21 python run_strict_v4_rrc_csr_confirmation.py --protocol protocol.json",
        "22 python run_strict_v4_rrc_csr_capture_pipeline.py --scenario x",
        "23 python materialize_rrc_csr_runtime.py --capture-dir x",
        "24 python evaluate_rrc_csr_runtime.py --condition clean",
        "25 python certify_rrc_csr_scenario.py --scenario x",
        "26 python unrelated_rrc_report.py",
    ]

    busy = busy_processes(lines)

    assert len(busy) == 6
    assert all("unrelated_rrc_report.py" not in row for row in busy)


def test_watcher_ignores_its_own_process_name() -> None:
    assert (
        busy_processes(
            ["10 python watch_strict_v4_pug_confirmation.py --once"]
        )
        == []
    )
