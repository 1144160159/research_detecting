from __future__ import annotations

import numpy as np

from evaluate_strict_v4_packet_sequence_fusion_development import (
    alert_score,
    add_benign_reference_distance_tail,
    configurations,
)


def arrays() -> dict[str, np.ndarray]:
    return {
        "validation_attack_probability": np.asarray([0.1, 0.8]),
        "validation_open_max": np.asarray([0.2, 0.7]),
        "test_attack_probability": np.asarray([0.3, 0.6]),
        "test_open_max": np.asarray([0.4, 0.9]),
    }


def test_binary_open_max_uses_both_heads() -> None:
    value = alert_score(
        arrays(),
        split="test",
        combination="binary_open_max",
        auxiliary_variant="open_max",
    )
    assert np.allclose(value, [0.4, 0.9])


def test_binary_open_noisy_or_is_at_least_each_input() -> None:
    value = alert_score(
        arrays(),
        split="validation",
        combination="binary_open_noisy_or",
        auxiliary_variant="open_max",
    )
    assert np.all(value >= arrays()["validation_attack_probability"])
    assert np.all(value >= arrays()["validation_open_max"])


def test_configuration_grid_is_bounded_and_unique() -> None:
    values = configurations()
    identities = {
        tuple(sorted(configuration.items())) for configuration in values
    }
    assert len(values) == len(identities)
    assert 100 < len(values) < 1000


def test_benign_reference_tail_uses_only_validation_benign_rows() -> None:
    values = {
        "validation_labels": np.asarray([0, 1, 0]),
        "validation_benign_distance_tail": np.asarray([0.1, 0.9, 0.2]),
        "test_benign_distance_tail": np.asarray([0.15, 0.8]),
    }
    add_benign_reference_distance_tail({"benign_index": 0}, values)
    assert np.allclose(
        values["test_benign_reference_distance_tail"], [0.5, 5.0 / 6.0]
    )
