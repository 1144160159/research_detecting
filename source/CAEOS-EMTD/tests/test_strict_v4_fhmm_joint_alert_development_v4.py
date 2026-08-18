from __future__ import annotations

import numpy as np
import pytest

import evaluate_strict_v4_fhmm_joint_alert_development_v4 as joint


def test_combine_alert_rules() -> None:
    attack = np.asarray([0.2, 0.8])
    open_score = np.asarray([0.7, 0.1])
    np.testing.assert_allclose(
        joint.combine_alert(attack, open_score, "attack_only"),
        attack,
    )
    np.testing.assert_allclose(
        joint.combine_alert(attack, open_score, "maximum"),
        [0.7, 0.8],
    )
    np.testing.assert_allclose(
        joint.combine_alert(attack, open_score, "noisy_or"),
        [0.76, 0.82],
    )


def test_combine_alert_rejects_shape_drift() -> None:
    with pytest.raises(ValueError, match="align"):
        joint.combine_alert(
            np.asarray([0.1]),
            np.asarray([0.1, 0.2]),
            "maximum",
        )


def test_configuration_space_is_bounded() -> None:
    values = joint.configurations()
    assert len(values) == 27
    assert {value["attack_source"] for value in values} == {"family"}
    assert {value["attack_aggregation"] for value in values} == {"mean"}
    assert {value["open_budget"] for value in values} == {0.04}
