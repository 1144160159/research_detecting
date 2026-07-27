from pathlib import Path


def test_watcher_is_conditional_serial_and_fail_closed():
    path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "wait_and_run_strict_v4_mdr_selected_system.sh"
    )
    text = path.read_text(encoding="utf-8")
    assert 'selected" != "mdr_caeos_v1"' in text
    assert "strict_v4_mdr_selected_system_not_required_v1" in text
    assert '&& -f "$EXTERNAL/branch_complete"' in text
    assert 'idle_samples" -lt 5' in text
    assert "OPENBLAS_NUM_THREADS=1" in text
    assert "run_strict_v4_mdr_selected_system.py" in text
    assert "summarize_strict_v4_mdr_selected_system.py" in text
    assert "audit_strict_v4_mdr_selected_system.py" in text
    assert 'value.get("passes") is not True' in text
    assert text.index("create_strict_v4_mdr_selected_system_protocol.py") < (
        text.index("run_strict_v4_mdr_selected_system.py")
    )
