import json
from pathlib import Path

from launch_strict_v4_core_warning_confirmation import pid_is_alive


def test_pid_is_alive_rejects_nonpositive_values() -> None:
    assert pid_is_alive(0) is False
    assert pid_is_alive(-1) is False


def test_launcher_state_schema_is_json_serializable(tmp_path: Path) -> None:
    state = {
        "schema_version": "strict_v4_core_warning_launcher_state_v1",
        "pid": 123,
        "protocol_manifest_sha256": "a" * 64,
    }
    path = tmp_path / "state.json"
    path.write_text(json.dumps(state), encoding="utf-8")
    assert json.loads(path.read_text(encoding="utf-8")) == state
