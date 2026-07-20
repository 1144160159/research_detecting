from __future__ import annotations

import json
from pathlib import Path

from screen_cross_suite_risk_candidates import (
    LEGACY_CODE_HASH,
    LEGACY_POLICY,
    LEGACY_RULE,
    LEGACY_SELECTION,
    REFERENCE,
    build_manifest,
    canonical_manifest_hash,
    load_development_blocks,
)


def report(auroc: float) -> dict[str, float]:
    return {
        "known_macro_f1": 0.9,
        "unknown_auroc": auroc,
        "unknown_aupr": 0.7,
        "unknown_fpr95": 0.3,
        "oscr": 0.75,
    }


def write_run(root: Path, suite: str, scenario: str) -> None:
    run = root / suite / f"{scenario}_seed7"
    run.mkdir(parents=True)
    payload = {
        "seed": 7,
        "risk_policy": "confirmed",
        "risk_selection_details": {"unknown_or_test_labels_used_for_selection": False},
        "split_metadata": {"split_fingerprint": {"combined": scenario * 8}},
        "selected_risk": "current",
        "selected_report": report(0.8),
        "reports": {"current": report(0.8), "candidate": report(0.85)},
    }
    (run / "metrics.json").write_text(json.dumps(payload), encoding="utf-8")
    for name in ("scores.npz", "evidence_package.npz"):
        (run / name).write_bytes(b"evidence")
    (run / "provenance.json").write_text(
        json.dumps({"code": {"sha256": "explicit-test-code"}}), encoding="utf-8"
    )


def test_loads_current_policy_as_reference_and_freezes_manifest(tmp_path: Path) -> None:
    write_run(tmp_path, "nf_cse", "a")
    write_run(tmp_path, "nf_cse", "b")
    write_run(tmp_path, "ustc_tfc2016", "c")

    blocks, validation = load_development_blocks(
        tmp_path, {"nf_cse": 2, "ustc_tfc2016": 1}, 7
    )

    assert validation["scenario_count"] == 3
    assert validation["artifact_checks"] == 12
    assert validation["explicit_no_leakage_guard_count"] == 3
    assert validation["legacy_inferred_no_leakage_guard_count"] == 0
    assert blocks["nf_cse"]["nf_cse/a"][REFERENCE]["unknown_auroc"] == 0.8

    screenings = {
        "nf_cse": {"selected_candidate": "candidate", "selection_rule": {"x": 1}},
        "ustc_tfc2016": {
            "selected_candidate": "candidate",
            "selection_rule": {"x": 1},
        },
    }
    manifest = build_manifest(validation, screenings, {83, 89})
    assert manifest["status"] == "frozen_unconfirmed"
    assert manifest["selected_suite_risks"] == {
        "nf_cse": "candidate",
        "ustc_tfc2016": "candidate",
    }
    assert manifest["manifest_sha256"] == canonical_manifest_hash(manifest)


def test_accepts_only_exact_legacy_no_leakage_contract(tmp_path: Path) -> None:
    write_run(tmp_path, "nf_cse", "legacy")
    run = tmp_path / "nf_cse" / "legacy_seed7"
    payload = json.loads((run / "metrics.json").read_text("utf-8"))
    payload["risk_policy"] = LEGACY_POLICY
    payload["risk_selection"] = LEGACY_SELECTION
    payload["risk_selection_details"] = {"selection_rule": LEGACY_RULE}
    (run / "metrics.json").write_text(json.dumps(payload), encoding="utf-8")
    (run / "provenance.json").write_text(
        json.dumps({"code": {"sha256": LEGACY_CODE_HASH}}), encoding="utf-8"
    )

    _, validation = load_development_blocks(tmp_path, {"nf_cse": 1}, 7)

    assert validation["explicit_no_leakage_guard_count"] == 0
    assert validation["legacy_inferred_no_leakage_guard_count"] == 1


def test_manifest_rejects_development_seed_reuse() -> None:
    validation = {
        "development_seed": 7,
        "scenario_count": 2,
        "source_metrics_combined_sha256": "a" * 64,
    }
    screenings = {
        "nf_cse": {"selected_candidate": "candidate", "selection_rule": {}}
    }
    try:
        build_manifest(validation, screenings, {7, 83})
    except ValueError as error:
        assert "development seed" in str(error)
    else:
        raise AssertionError("confirmation must not reuse the development seed")
