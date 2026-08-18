from __future__ import annotations

import numpy as np
import pytest

from evaluate_strict_v4_fhmm_calibrated_aggregation_development import (
    aggregate,
    empirical_upper_tail,
    macro_f1,
)


def test_empirical_upper_tail_is_monotone_and_validation_only() -> None:
    reference = np.asarray([0.1, 0.2, 0.3, 0.4])
    values = np.asarray([0.05, 0.2, 0.35, 0.9])
    result = empirical_upper_tail(reference, values)
    assert np.all(np.diff(result) >= 0.0)
    assert result.tolist() == pytest.approx([0.1, 0.5, 0.7, 0.9])


def test_aggregate_supports_fixed_robust_rules() -> None:
    values = [
        np.asarray([0.1, 0.9]),
        np.asarray([0.2, 0.8]),
        np.asarray([0.9, 0.7]),
    ]
    assert aggregate(values, "mean").tolist() == pytest.approx(
        [0.4, 0.8]
    )
    assert aggregate(values, "median").tolist() == pytest.approx(
        [0.2, 0.8]
    )
    assert aggregate(values, "maximum").tolist() == pytest.approx(
        [0.9, 0.9]
    )


def test_macro_f1_penalizes_missing_class_predictions() -> None:
    labels = np.asarray([0, 0, 1, 1])
    perfect = macro_f1(labels, labels)
    collapsed = macro_f1(labels, np.zeros(labels.shape, dtype=np.int64))
    assert perfect == 1.0
    assert collapsed == pytest.approx(1.0 / 3.0)


def test_rejects_nonfinite_tail_input() -> None:
    with pytest.raises(ValueError, match="finite"):
        empirical_upper_tail(
            np.asarray([0.1, np.nan]),
            np.asarray([0.2]),
        )

