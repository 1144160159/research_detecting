from __future__ import annotations

import json
from pathlib import Path

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
import watch_strict_v4_rrc_csr_realtime_progress as target


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    value["manifest_sha256"] = canonical_hash(value)
    path.write_text(json.dumps(value), encoding="utf-8")


def prepare(tmp_path: Path) -> tuple[Path, Path, Path, Path, Path]:
    protocol = tmp_path / "protocol.json"
    write(
        protocol,
        {
            "schema_version": "strict_v4_rrc_csr_execution_protocol_v1",
            "task_counts": {
                "base_csr_captures": 0,
                "rrc_runtime_captures": 0,
                "scenario_certificates": 0,
                "evaluations": 0,
            },
        },
    )
    return (
        protocol,
        tmp_path / "run",
        tmp_path / "result",
        tmp_path / "progress.json",
        tmp_path / "watcher_state.json",
    )


def test_observer_writes_canonical_running_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    protocol, run_root, result_root, output, state = prepare(tmp_path)
    monkeypatch.setattr(target, "runner_pids", lambda: [123])

    value = target.observe_once(
        protocol_path=protocol,
        run_root=run_root,
        result_root=result_root,
        output_path=output,
        state_path=state,
    )

    assert value["state"] == "rrc_running_valid_partial_progress"
    assert value["observed_at_utc"]
    assert value["partial_effect_claim_authorized"] is False
    assert value["manifest_sha256"] == canonical_hash(value)
    assert json.loads(state.read_text(encoding="utf-8")) == value


def test_observer_exits_only_on_three_canonical_terminal_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    protocol, run_root, result_root, output, state = prepare(tmp_path)
    monkeypatch.setattr(target, "runner_pids", lambda: [])
    for name, schema in target.TERMINAL_SCHEMAS.items():
        write(result_root / name, {"schema_version": schema})

    value = target.observe_once(
        protocol_path=protocol,
        run_root=run_root,
        result_root=result_root,
        output_path=output,
        state_path=state,
    )

    assert value["state"] == "terminal_rrc_evidence_available"
    assert value["terminal_evidence"]["complete"] is True
