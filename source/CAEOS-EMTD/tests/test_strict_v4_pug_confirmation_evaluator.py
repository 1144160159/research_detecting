from __future__ import annotations

import pytest

from evaluate_strict_v4_pug_confirmation import aggregate


def test_aggregate_orients_fpr95_as_lower_is_better() -> None:
    rows = [
        {
            "caeos_pug": {
                "known_macro_f1": 0.8,
                "unknown_auroc": 0.7,
                "unknown_aupr": 0.6,
                "unknown_fpr95": 0.4,
                "oscr": 0.5,
            },
            "pairwise": {
                "known_macro_f1": 0.8,
                "unknown_auroc": 0.7,
                "unknown_aupr": 0.6,
                "unknown_fpr95": 0.5,
                "oscr": 0.5,
            },
        }
    ]

    result = aggregate(rows, "caeos_pug", "pairwise")

    assert result["metrics"]["unknown_fpr95"][
        "oriented_mean_delta"
    ] == pytest.approx(0.1)
    assert result["metrics"]["unknown_fpr95"]["win_count"] == 1
    assert result["metrics"]["known_macro_f1"]["tie_count"] == 1
