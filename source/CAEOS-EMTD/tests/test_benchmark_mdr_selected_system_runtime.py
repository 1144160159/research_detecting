import numpy as np
import pytest

from benchmark_mdr_selected_system_runtime import (
    exact_batch,
    execution_context,
    peak_rss_mb,
    timing_summary,
)


def test_exact_batch_cycles_without_changing_alignment():
    views = [
        np.asarray([[1], [2], [3]]),
        np.asarray([[10], [20], [30]]),
    ]
    batch = exact_batch(views, 5)
    assert batch[0].ravel().tolist() == [1, 2, 3, 1, 2]
    assert batch[1].ravel().tolist() == [10, 20, 30, 10, 20]


def test_exact_batch_rejects_misalignment():
    with pytest.raises(ValueError, match="aligned"):
        exact_batch([np.zeros((2, 1)), np.zeros((3, 1))], 2)


def test_timing_summary_reports_oriented_throughput():
    result = timing_summary([0.01, 0.02, 0.03], 10)
    assert result["latency_p50_ms"] == pytest.approx(20.0)
    assert result["samples_per_second"] == pytest.approx(500.0)


def test_timing_summary_rejects_nonpositive_values():
    with pytest.raises(ValueError, match="positive"):
        timing_summary([0.0], 1)


def test_peak_rss_mb_and_execution_context_are_explicit():
    assert peak_rss_mb(None) is None
    assert peak_rss_mb(2048) is not None
    context = execution_context()
    assert context["gpu_used"] is False
    assert set(context["thread_environment"]) == {
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    }
