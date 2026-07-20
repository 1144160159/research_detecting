from __future__ import annotations

import json
from pathlib import Path

from confirm_cross_suite_fixed_reports import build_same_run_rows
from summarize_paired_confirmation import METRICS, REQUIRED_ARTIFACTS


def report(value: float) -> dict[str, float]:
    return {metric: value for metric in METRICS}


def write_run(root: Path, suite: str, risk: str) -> None:
    run = root / suite / "scenario_seed83"
    run.mkdir(parents=True)
    payload = {
        "risk_policy": "reference",
        "selected_risk": "current",
        "selected_report": report(0.5),
        "reports": {risk: report(0.6)},
        "validation_thresholds": {risk: 0.95},
        "risk_selection_details": {
            "unknown_or_test_labels_used_for_selection": False,
        },
        "split_metadata": {"split_fingerprint": {"combined": f"{suite}-83"}},
    }
    (run / "metrics.json").write_text(json.dumps(payload), encoding="utf-8")
    for name in REQUIRED_ARTIFACTS:
        (run / name).touch(exist_ok=True)


def test_same_run_confirmation_uses_frozen_suite_report_and_threshold(tmp_path: Path) -> None:
    write_run(tmp_path, "nf_cse", "disagreement_augmented")
    write_run(tmp_path, "ustc_tfc2016", "cauchy_conflict")
    manifest = {
        "confirmation_seeds": [83],
        "selected_suite_risks": {
            "nf_cse": "disagreement_augmented",
            "ustc_tfc2016": "cauchy_conflict",
        },
    }

    rows, validation = build_same_run_rows(tmp_path, manifest, 2, "reference")

    assert len(rows) == 2
    assert validation["candidate_reports_extracted_from_same_model_run"] is True
    assert validation["candidate_thresholds_fitted_on_known_validation"] is True
    assert {row["candidate_selected"] for row in rows} == {
        "disagreement_augmented",
        "cauchy_conflict",
    }
