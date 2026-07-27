from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from caeos.pseudo_unknown_gated_continuous import (
    PAIRWISE_REFERENCE_RISK,
    PUG_RISK_NAME,
    PUG_SELECTION_NAME,
)
from inspect_strict_v4_pug_run import inspect_run


def write_run(root: Path, gate_passes: bool = False) -> Path:
    selected = PUG_RISK_NAME if gate_passes else PAIRWISE_REFERENCE_RISK
    validation_reference = np.asarray([0.1, 0.2, 0.3])
    test_reference = np.asarray([0.2, 0.4, 0.8])
    validation_pug = np.asarray([0.15, 0.25, 0.35])
    test_pug = np.asarray([0.1, 0.5, 0.9])
    selected_validation = (
        validation_pug if gate_passes else validation_reference
    )
    selected_test = test_pug if gate_passes else test_reference
    threshold = 0.45
    report = {"known_macro_f1": 0.8, "unknown_auroc": 0.7}
    metrics = {
        "selected_risk": selected,
        "risk_selection": PUG_SELECTION_NAME,
        "selected_report": report,
        "reports": {selected: report},
        "risk_selection_details": {
            "pug_continuous_outer_gate": {
                "fold_count": 6,
                "passes": gate_passes,
                "checks": {"minimum_fold_count": True},
                "aggregates": {},
                "selection_uses_unknown_or_test_labels": False,
            },
            "pairwise_base_selected_risk": PAIRWISE_REFERENCE_RISK,
            "pug_base_route_eligible": True,
            "pug_selected": gate_passes,
            "selected_risk": selected,
            "unknown_or_test_labels_used_for_selection": False,
        },
    }
    (root / "metrics.json").write_text(
        json.dumps(metrics), encoding="utf-8"
    )
    np.savez_compressed(
        root / "scores.npz",
        **{
            f"validation_{PAIRWISE_REFERENCE_RISK}": validation_reference,
            f"test_{PAIRWISE_REFERENCE_RISK}": test_reference,
            f"validation_{PUG_RISK_NAME}": validation_pug,
            f"test_{PUG_RISK_NAME}": test_pug,
        },
    )
    np.savez_compressed(
        root / "evidence_package.npz",
        selected_risk_name=np.asarray(selected),
        selected_threshold=np.asarray(threshold),
        validation_selected_risk=selected_validation,
        test_selected_risk=selected_test,
        test_rejected=selected_test > threshold,
    )
    return root


@pytest.mark.parametrize("gate_passes", [False, True])
def test_inspector_accepts_exact_fallback_and_pug_selection(
    tmp_path: Path, gate_passes: bool
) -> None:
    result = inspect_run(write_run(tmp_path, gate_passes))

    assert result["inspection_passes"] is True
    assert result["pug_selected"] is gate_passes
    assert result["selected_arrays_exact"] is True
    assert result["unknown_or_test_labels_used_for_selection"] is False


def test_inspector_rejects_evidence_selected_array_mismatch(
    tmp_path: Path,
) -> None:
    write_run(tmp_path)
    np.savez_compressed(
        tmp_path / "evidence_package.npz",
        selected_risk_name=np.asarray(PAIRWISE_REFERENCE_RISK),
        selected_threshold=np.asarray(0.45),
        validation_selected_risk=np.asarray([9.0, 9.0, 9.0]),
        test_selected_risk=np.asarray([0.2, 0.4, 0.8]),
        test_rejected=np.asarray([False, False, True]),
    )

    with pytest.raises(ValueError, match="validation selected-risk arrays"):
        inspect_run(tmp_path)
