from __future__ import annotations

import numpy as np

from train_strict_v4_packet_sequence_fusion_task_cuda import (
    class_weights,
    robust_scale_statistics,
    sequence_channels,
    stratified_open_set_split,
    tail_percentile,
)


def synthetic_identity() -> tuple[np.ndarray, np.ndarray]:
    families = np.asarray(
        [
            family
            for family in ("Benign", "Botnet", "DDoS")
            for _ in range(10)
        ]
    )
    flow_ids = np.asarray([f"flow-{index}" for index in range(families.size)])
    return flow_ids, families


def test_open_set_split_keeps_unknown_out_of_train_and_validation() -> None:
    flow_ids, families = synthetic_identity()
    splits = stratified_open_set_split(
        flow_ids, families, unknown_family="Botnet", seed=29
    )
    assert "Botnet" not in set(families[splits["train"]])
    assert "Botnet" not in set(families[splits["validation"]])
    assert set(families[splits["test"]]) == {"Benign", "Botnet", "DDoS"}
    assert set(np.concatenate(list(splits.values()))) == set(range(30))


def test_sequence_channels_preserve_direction_and_mask() -> None:
    lengths = np.asarray([[100, -200, 0]], dtype=np.int16)
    timing = np.asarray([[0.0, 1000.0, 0.0]], dtype=np.float32)
    mask = np.asarray([[True, True, False]])
    channels = sequence_channels(lengths, timing, mask)
    assert channels.shape == (1, 4, 3)
    assert channels[0, 0, 0] > 0
    assert channels[0, 0, 1] < 0
    assert channels[0, 3].tolist() == [1.0, 1.0, 0.0]


def test_class_weights_are_finite_and_mean_one() -> None:
    weights = class_weights(np.asarray([0, 0, 0, 1]), 2)
    assert np.isfinite(weights).all()
    assert np.isclose(weights.mean(), 1.0)
    assert weights[1] > weights[0]


def test_tail_percentile_is_monotonic() -> None:
    values = tail_percentile(
        np.asarray([1.0, 2.0, 3.0]), np.asarray([0.0, 2.5, 4.0])
    )
    assert np.all(np.diff(values) > 0)


def test_flow_statistics_are_scaled_from_training_rows_only() -> None:
    values = np.asarray(
        [[1.0, np.inf], [2.0, 3.0], [1000.0, 999.0]], dtype=np.float32
    )
    scaled, report = robust_scale_statistics(values, np.asarray([0, 1]))
    assert report["fit_on_training_split_only"] is True
    assert report["median"][0] == 1.5
    assert np.isfinite(scaled).all()
    assert scaled[2, 0] == 10.0
