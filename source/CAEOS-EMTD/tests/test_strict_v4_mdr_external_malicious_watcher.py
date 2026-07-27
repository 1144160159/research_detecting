from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def watcher():
    return (
        ROOT
        / "scripts/wait_and_run_strict_v4_mdr_external_malicious.sh"
    ).read_text(encoding="utf-8")


def test_watcher_has_canonical_negative_branch():
    text = watcher()
    assert "strict_v4_mdr_external_malicious_not_required_v1" in text
    assert "final_reserved_confirmation_did_not_select_mdr" in text
    assert 'touch "$ROOT/branch_complete"' in text


def test_watcher_requires_positive_branch_and_preparation():
    text = watcher()
    assert '"$MDR/branch_complete"' in text
    assert '"$PREPARATION/preparation_complete"' in text
    assert "five consecutive idle samples passed" in text


def test_watcher_runs_full_frozen_chain():
    text = watcher()
    for name in (
        "create_strict_v4_mdr_external_malicious_protocol.py",
        "run_strict_v4_mdr_external_malicious.py",
        "summarize_strict_v4_mdr_external_malicious.py",
        "audit_strict_v4_mdr_external_malicious.py",
    ):
        assert name in text


def test_watcher_does_not_claim_sota_from_negative_branch():
    text = watcher()
    assert '"comprehensive_sota_confirmed": False' in text
