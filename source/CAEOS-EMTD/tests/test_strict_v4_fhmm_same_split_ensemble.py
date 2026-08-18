from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pytest

import evaluate_strict_v4_fhmm_same_split_ensemble as ensemble


def test_majority_vote_uses_lowest_class_for_three_way_tie() -> None:
    result = ensemble.majority_vote(
        [
            np.asarray([0, 0, 2]),
            np.asarray([0, 1, 1]),
            np.asarray([1, 2, 0]),
        ],
        class_count=3,
    )
    assert result.tolist() == [0, 0, 0]


def _member_arrays(offset: float = 0.0) -> dict[str, np.ndarray]:
    validation_labels = np.asarray([0] * 100 + [1] * 100)
    test_labels = np.asarray([0] * 20 + [1] * 20 + [-1] * 20)
    test_unknown = np.asarray([False] * 40 + [True] * 20)
    return {
        "known_class_names": np.asarray(["Benign", "KnownAttack"]),
        "validation_labels": validation_labels,
        "validation_attack_head_attack_probability": np.asarray(
            [0.01 + offset] * 100 + [0.99 - offset] * 100
        ),
        "validation_open_max": np.asarray(
            [0.05 + offset] * 100 + [0.10 + offset] * 100
        ),
        "validation_type_prediction": validation_labels.copy(),
        "test_labels": test_labels,
        "test_unknown": test_unknown,
        "test_attack_head_attack_probability": np.asarray(
            [0.01 + offset] * 20
            + [0.99 - offset] * 20
            + [0.98 - offset] * 20
        ),
        "test_open_max": np.asarray(
            [0.05 + offset] * 20
            + [0.10 + offset] * 20
            + [0.90 - offset] * 20
        ),
        "test_type_prediction": np.asarray([0] * 20 + [1] * 40),
    }


def test_fixed_ensemble_evaluates_without_unknown_tuning(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    loaded: dict[Path, tuple[dict[str, Any], dict[str, np.ndarray]]] = {}
    member_dirs = []
    for index, seed in enumerate((101, 103, 107)):
        task_dir = tmp_path / f"member_{seed}"
        task_dir.mkdir()
        for name in ("metrics.json", "scores.npz", "gpu_execution.json"):
            (task_dir / name).write_bytes(f"{seed}-{name}".encode("ascii"))
        report = {
            "model": {"name": "FHMM-CAEOS member"},
            "training": {"meta_heldout_loss_weight": 1.0},
            "task": {
                "unknown_family": "Botnet",
                "split_seed": 37,
                "model_seed": seed,
            },
            "benign_index": 0,
            "source": {"sequence_dataset_sha256": "dataset"},
        }
        loaded[task_dir.resolve()] = (
            report,
            _member_arrays(index * 0.001),
        )
        member_dirs.append(task_dir)

    monkeypatch.setattr(
        ensemble,
        "verify_task",
        lambda path: loaded[path.resolve()],
    )
    result = ensemble.evaluate_members(member_dirs)

    assert result["fixed_configuration"]["configuration_selection"] == (
        "none_fixed_before_test"
    )
    assert result["operational_metrics"]["alert_accuracy"] == 1.0
    assert result["operational_metrics"]["benign_fpr"] == 0.0
    assert result["operational_metrics"][
        "known_attack_type_accuracy"
    ] == 1.0
    assert result["research_metric_contract"]["unknown_detection"][
        "unknown_auroc"
    ] == 1.0
    assert result["expansion_gate"]["expand_to_seven_scenarios"] is True


def test_fixed_ensemble_rejects_duplicate_model_seeds(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    task_dirs = []
    loaded = {}
    for index in range(3):
        task_dir = tmp_path / f"member_{index}"
        task_dir.mkdir()
        report = {
            "model": {"name": "FHMM-CAEOS member"},
            "training": {"meta_heldout_loss_weight": 1.0},
            "task": {
                "unknown_family": "Botnet",
                "split_seed": 37,
                "model_seed": 101,
            },
            "benign_index": 0,
            "source": {"sequence_dataset_sha256": "dataset"},
        }
        loaded[task_dir.resolve()] = (report, _member_arrays())
        task_dirs.append(task_dir)
    monkeypatch.setattr(
        ensemble,
        "verify_task",
        lambda path: loaded[path.resolve()],
    )
    with pytest.raises(ValueError, match="model seeds must be distinct"):
        ensemble.evaluate_members(task_dirs)

