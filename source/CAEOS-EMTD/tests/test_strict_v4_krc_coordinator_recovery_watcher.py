from __future__ import annotations

from watch_strict_v4_krc_coordinator_recovery import (
    recovery_decision,
    relevant_commands,
)


def captures(
    *,
    complete: int = 170,
    absent: int = 136,
    partial: list[str] | None = None,
) -> dict:
    paths = [] if partial is None else partial
    return {
        "expected_capture_count": 306,
        "complete_capture_count": complete,
        "absent_capture_count": absent,
        "partial_capture_count": len(paths),
        "partial_capture_paths": paths,
    }


def test_existing_coordinator_and_workers_must_drain() -> None:
    processes = relevant_commands(
        [
            "python run_strict_v4_krc_csr_confirmation.py --workers 4",
            "python capture_krc_csr_confirmation_runtime.py",
            "python watch_strict_v4_krc_coordinator_recovery.py",
        ]
    )
    state, idle = recovery_decision(
        process_state=processes,
        capture_state=captures(),
        terminal_outputs_present=False,
        prior_idle_count=2,
        required_idle_polls=3,
    )
    assert state["state"] == (
        "waiting_for_existing_krc_processes_to_drain"
    )
    assert state["restart_admitted"] is False
    assert idle == 0


def test_true_partial_capture_fails_closed_without_restart() -> None:
    state, idle = recovery_decision(
        process_state={"coordinator": [], "workers": []},
        capture_state=captures(
            complete=169,
            absent=136,
            partial=["captures/cicids2017/portscan/seed659"],
        ),
        terminal_outputs_present=False,
        prior_idle_count=2,
        required_idle_polls=3,
    )
    assert state["state"] == (
        "manual_partial_capture_intervention_required"
    )
    assert state["restart_admitted"] is False
    assert idle == 0


def test_restart_requires_three_consecutive_clean_polls() -> None:
    process_state = {"coordinator": [], "workers": []}
    state, idle = recovery_decision(
        process_state=process_state,
        capture_state=captures(),
        terminal_outputs_present=False,
        prior_idle_count=1,
        required_idle_polls=3,
    )
    assert state["state"] == "clean_drain_waiting_for_stability"
    assert idle == 2

    state, idle = recovery_decision(
        process_state=process_state,
        capture_state=captures(),
        terminal_outputs_present=False,
        prior_idle_count=idle,
        required_idle_polls=3,
    )
    assert state["state"] == "clean_drain_restart_admitted"
    assert state["restart_admitted"] is True
    assert idle == 3


def test_terminal_outputs_never_restart() -> None:
    state, idle = recovery_decision(
        process_state={"coordinator": [], "workers": []},
        capture_state=captures(complete=306, absent=0),
        terminal_outputs_present=True,
        prior_idle_count=2,
        required_idle_polls=3,
    )
    assert state["state"] == "terminal_krc_outputs_present_no_restart"
    assert state["restart_admitted"] is False
    assert idle == 0
