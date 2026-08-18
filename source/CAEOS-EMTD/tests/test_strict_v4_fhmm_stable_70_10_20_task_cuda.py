from __future__ import annotations

import numpy as np

from train_strict_v4_fhmm_stable_70_10_20_task_cuda import (
    stratified_open_set_split_70_10_20,
)


def test_split_preserves_unknown_only_test_and_known_ratios() -> None:
    flow_ids = np.asarray([f"flow-{index}" for index in range(220)])
    families = np.asarray(
        ["Benign"] * 100 + ["DDoS"] * 100 + ["Botnet"] * 20
    )
    splits = stratified_open_set_split_70_10_20(
        flow_ids,
        families,
        unknown_family="Botnet",
        seed=43,
    )
    assert len(splits["train"]) == 140
    assert len(splits["validation"]) == 20
    assert len(splits["test"]) == 60
    assert set(np.flatnonzero(families == "Botnet")) <= set(splits["test"])
    assert not (
        set(splits["train"])
        & set(splits["validation"])
        or set(splits["train"]) & set(splits["test"])
        or set(splits["validation"]) & set(splits["test"])
    )


def test_split_is_deterministic_and_seed_sensitive() -> None:
    flow_ids = np.asarray([f"flow-{index}" for index in range(120)])
    families = np.asarray(
        ["Benign"] * 50 + ["DDoS"] * 50 + ["Botnet"] * 20
    )
    first = stratified_open_set_split_70_10_20(
        flow_ids,
        families,
        unknown_family="Botnet",
        seed=43,
    )
    repeated = stratified_open_set_split_70_10_20(
        flow_ids,
        families,
        unknown_family="Botnet",
        seed=43,
    )
    changed = stratified_open_set_split_70_10_20(
        flow_ids,
        families,
        unknown_family="Botnet",
        seed=47,
    )
    np.testing.assert_array_equal(first["train"], repeated["train"])
    assert not np.array_equal(first["train"], changed["train"])
