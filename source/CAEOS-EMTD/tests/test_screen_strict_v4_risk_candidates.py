from __future__ import annotations

from screen_strict_v4_risk_candidates import build_manifest, canonical_hash


def test_manifest_freezes_disjoint_confirmation() -> None:
    validation = {
        "run_count": 6,
        "fixed_risk_method_count": 44,
        "source_metrics_combined_sha256": "source",
    }
    screenings = {
        "cic_ton_iot": {
            "selected_candidate": "cauchy_all",
            "selection_rule": {},
        },
        "cic_iot2023": {
            "selected_candidate": "conflict_augmented",
            "selection_rule": {},
        },
    }
    manifest = build_manifest(validation, screenings, "screening", [11, 19])
    assert manifest["confirmation"]["expected_run_count"] == 12
    assert manifest["confirmation"]["scenario_disjoint"] is True
    assert manifest["runtime_policy"]["uses_unknown_or_test_labels"] is False
    assert manifest["manifest_sha256"] == canonical_hash(manifest)
