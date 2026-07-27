from pathlib import Path


def test_watcher_is_conditional_ordered_and_fail_closed():
    path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "wait_and_run_strict_v4_mdr_parrot_safety.sh"
    )
    text = path.read_text(encoding="utf-8")
    assert 'selected" != "mdr_caeos_v1"' in text
    assert "strict_v4_mdr_parrot_safety_not_required_v1" in text
    assert '&& -f "$FEATURE/full_feature_extraction_complete"' in text
    assert '&& -f "$EXTERNAL/branch_complete"' in text
    assert '&& -f "$SYSTEM/branch_complete"' in text
    assert 'idle_samples" -lt 5' in text
    assert "run_strict_v4_mdr_parrot_safety.py" in text
    assert "summarize_strict_v4_mdr_parrot_safety.py" in text
    assert "audit_strict_v4_mdr_parrot_safety.py" in text
    assert 'value.get("passes") is not True' in text
