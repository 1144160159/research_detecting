from __future__ import annotations

from summarize_selective_missingness_route_confirmation import (
    summarize_confirmation,
)


def test_confirmation_state_uses_prefrozen_gates(monkeypatch, tmp_path) -> None:
    manifest = {
        "evaluation_role": "frozen_disjoint_confirmation",
        "development_source_summary_sha256": "abc",
        "scenarios": ["heldout"],
        "seeds": [23],
        "modalities": [0, 1, 2],
    }
    aggregate_result = {
        "state": "development_candidate_selected",
        "confirmation_status": "not_run",
        "gate_results": {
            "active_modalities_passed": True,
            "inactive_modalities_exactly_preserved": True,
        },
        "by_modality": {},
    }
    monkeypatch.setattr(
        "summarize_selective_missingness_route_confirmation.load_pairs",
        lambda root, candidate_manifest: [],
    )
    monkeypatch.setattr(
        "summarize_selective_missingness_route_confirmation.aggregate",
        lambda pairs, candidate_manifest: dict(aggregate_result),
    )
    result = summarize_confirmation(tmp_path, manifest)
    assert result["state"] == "confirmed"
    assert result["confirmation_status"] == "passed"
    assert result["confirmation_boundary"]["seeds"] == [23]
