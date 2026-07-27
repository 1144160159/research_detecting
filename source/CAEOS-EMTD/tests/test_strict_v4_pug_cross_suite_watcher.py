from __future__ import annotations

from pathlib import Path

from create_strict_v4_external_confirmation_protocol import canonical_hash
from watch_strict_v4_pug_cross_suite_confirmation import (
    busy_commands,
    inspect_once,
    pilot_confirmation_ready,
    resource_state,
    validate_activation,
)


def test_busy_commands_cover_krc_rrc_pug_and_ignore_self() -> None:
    commands = [
        "python run_strict_v4_krc_csr_confirmation.py --workers 4",
        "bash wait_and_run_strict_v4_rrc_csr_confirmation.sh",
        "python materialize_rrc_csr_runtime.py",
        "bash run_strict_v4_pug_confirmation.sh",
        "python run_nested_gate_matrix.py --suite edge_iiot",
        "python watch_strict_v4_pug_cross_suite_confirmation.py",
    ]

    busy = busy_commands(commands)

    assert len(busy) == 5
    assert not any(
        "watch_strict_v4_pug_cross_suite_confirmation.py" in value
        for value in busy
    )


def test_resource_state_requires_consecutive_idle_polls() -> None:
    state, idle = resource_state(
        prior_idle_count=1,
        required_idle_polls=3,
        commands=[],
    )

    assert state["state"] == "resources_idle"
    assert idle == 2
    assert state["launched"] is False


def test_inspect_once_waits_for_pilot_without_writes(
    tmp_path: Path,
) -> None:
    state, idle = inspect_once(tmp_path, commands=[])

    assert state["state"] == "waiting_for_pilot_confirmation"
    assert state["launched"] is False
    assert idle == 0


def test_negative_activation_retains_upstream_incumbent(
    tmp_path: Path,
) -> None:
    value = {
        "schema_version": "strict_v4_pug_cross_suite_activation_v1",
        "state": "negative_not_required_retain_upstream_incumbent",
    }
    value["manifest_sha256"] = canonical_hash(value)
    path = tmp_path / "activation.json"
    path.write_text(__import__("json").dumps(value), encoding="utf-8")

    assert (
        validate_activation(path)
        == "negative_not_required_retain_upstream_incumbent"
    )


def test_pilot_readiness_rejects_partial_then_accepts_canonical(
    tmp_path: Path,
) -> None:
    path = tmp_path / "confirmation.json"
    path.write_text('{"schema_version":', encoding="utf-8")
    assert pilot_confirmation_ready(path) is False

    value = {
        "schema_version": "strict_v4_pug_confirmation_v1",
        "task_count": 18,
        "decision": {"passes": False},
    }
    value["manifest_sha256"] = canonical_hash(value)
    path.write_text(__import__("json").dumps(value), encoding="utf-8")

    assert pilot_confirmation_ready(path) is True
