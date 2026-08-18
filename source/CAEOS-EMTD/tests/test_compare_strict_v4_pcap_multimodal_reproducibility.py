from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from compare_strict_v4_pcap_multimodal_reproducibility import compare_roots


def write_task(
    root: Path,
    *,
    risk: np.ndarray,
    elapsed: float,
    output_path: str,
) -> None:
    root.mkdir(parents=True, exist_ok=True)
    metrics = {
        "elapsed_seconds": elapsed,
        "manifest_sha256": "runtime-dependent",
        "cache": {"path": output_path, "sha256": "stable"},
        "gpu_execution": {"peak_allocated_bytes": 123},
        "three_layer_metrics": {"known_macro_f1": 0.9},
        "training": {"history": [{"epoch": 1, "loss": 0.25}]},
        "operational_95_5": {
            "family_crossfit_model_path": output_path,
            "family_crossfit_model_sha256": "archive-dependent",
            "alert_accuracy": 0.95,
        },
    }
    (root / "ddos_metrics.json").write_text(
        json.dumps(metrics), encoding="utf-8"
    )
    np.savez_compressed(
        root / "ddos_scores.npz",
        risk=risk,
        alert=risk >= 0.5,
    )


def test_runtime_paths_and_elapsed_time_are_excluded(tmp_path: Path) -> None:
    left = tmp_path / "left"
    right = tmp_path / "right"
    values = np.asarray([0.1, 0.9], dtype=np.float32)
    write_task(left, risk=values, elapsed=10.0, output_path="/left/model.pt")
    write_task(right, risk=values, elapsed=20.0, output_path="/right/model.pt")
    result = compare_roots(left, right)
    assert result["reproducibility_passed"] is True
    assert result["scenarios"]["ddos"]["metrics"]["core_metrics_exact"] is True
    assert result["scenarios"]["ddos"]["scores"]["all_arrays_exact"] is True


def test_score_difference_fails_reproducibility(tmp_path: Path) -> None:
    left = tmp_path / "left"
    right = tmp_path / "right"
    write_task(
        left,
        risk=np.asarray([0.1, 0.9], dtype=np.float32),
        elapsed=10.0,
        output_path="/left/model.pt",
    )
    write_task(
        right,
        risk=np.asarray([0.1, 0.8], dtype=np.float32),
        elapsed=10.0,
        output_path="/right/model.pt",
    )
    result = compare_roots(left, right)
    score_result = result["scenarios"]["ddos"]["scores"]
    assert result["reproducibility_passed"] is False
    assert score_result["all_arrays_exact"] is False
    assert (
        score_result["arrays"]["risk"]["maximum_absolute_difference"] > 0.0
    )
