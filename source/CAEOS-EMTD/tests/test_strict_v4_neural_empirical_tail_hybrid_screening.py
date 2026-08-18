from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from evaluate_strict_v4_neural_empirical_tail_hybrid_screening import (
    evaluate_configuration,
    prepare_scenario,
    scenario_name,
    scores_for,
)


def write_fixture(root: Path) -> tuple[Path, Path]:
    neural_dir = root / "neural"
    xgboost_dir = root / "xgboost"
    neural_dir.mkdir()
    xgboost_dir.mkdir()
    metrics = {
        "known_class_names": ["Benign", "AttackA", "AttackB"],
        "unknown_classes": ["AttackU"],
    }
    (neural_dir / "metrics.json").write_text(
        json.dumps(metrics), encoding="utf-8"
    )
    (xgboost_dir / "metrics.json").write_text(
        json.dumps(metrics), encoding="utf-8"
    )
    validation_labels = np.array([0, 0, 0, 1, 1, 2, 2])
    test_labels = np.array([0, 0, 1, 2, -1, -1])
    test_unknown = np.array([False, False, False, False, True, True])
    np.savez_compressed(
        neural_dir / "scores.npz",
        validation_labels=validation_labels,
        test_labels=test_labels,
        test_unknown=test_unknown,
        validation_energy=np.array([0.1, 0.2, 0.3, 0.2, 0.3, 0.4, 0.5]),
        test_energy=np.array([0.1, 0.2, 0.3, 0.4, 0.9, 1.0]),
    )
    validation_probability = np.array(
        [
            [0.99, 0.005, 0.005],
            [0.98, 0.01, 0.01],
            [0.97, 0.02, 0.01],
            [0.02, 0.97, 0.01],
            [0.03, 0.96, 0.01],
            [0.02, 0.01, 0.97],
            [0.03, 0.01, 0.96],
        ]
    )
    test_probability = np.array(
        [
            [0.99, 0.005, 0.005],
            [0.98, 0.01, 0.01],
            [0.02, 0.97, 0.01],
            [0.02, 0.01, 0.97],
            [0.01, 0.70, 0.29],
            [0.01, 0.49, 0.50],
        ]
    )
    np.savez_compressed(
        xgboost_dir / "scores.npz",
        validation_probability=validation_probability,
        validation_labels=validation_labels,
        test_probability=test_probability,
        test_labels=test_labels,
        test_unknown=test_unknown,
    )
    return neural_dir, xgboost_dir


def test_prepare_and_score_fixture(tmp_path: Path) -> None:
    neural_dir, xgboost_dir = write_fixture(tmp_path)
    arrays, hashes = prepare_scenario(
        neural_dir, xgboost_dir, ("energy",)
    )
    assert set(hashes) == {
        "neural_metrics",
        "neural_scores",
        "xgboost_metrics",
        "xgboost_scores",
    }
    configuration = {
        "risk_name": "energy",
        "alert_variant": "tail_noisy_or",
        "alert_budget": 0.04,
        "open_variant": "risk_tail",
        "open_budget": 0.04,
    }
    scores = scores_for(arrays, configuration)
    assert len(scores) == 4
    assert all(np.isfinite(value).all() for value in scores)


def test_evaluation_detects_unknown_fixture(tmp_path: Path) -> None:
    neural_dir, xgboost_dir = write_fixture(tmp_path)
    arrays, _ = prepare_scenario(
        neural_dir, xgboost_dir, ("energy",)
    )
    result = evaluate_configuration(
        {"attack_u": arrays},
        {
            "risk_name": "energy",
            "alert_variant": "xgb_attack",
            "alert_budget": 0.04,
            "open_variant": "risk_tail",
            "open_budget": 0.04,
        },
    )
    assert result["macro_mean"]["alert_accuracy"] == 1.0
    assert result["macro_mean"]["unknown_attack_alert_recall"] == 1.0
    assert result["scenario_basic_gate_pass_count"] == 1


def test_scenario_name_requires_suffix() -> None:
    assert scenario_name(Path("bot_seed7_mlp"), "_seed7_mlp") == "bot"
