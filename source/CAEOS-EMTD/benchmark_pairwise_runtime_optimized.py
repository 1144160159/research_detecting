from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np

from benchmark_pairwise_runtime import benchmark, load_views, peak_host_rss_mb
from caeos.pairwise_runtime import PairwiseRuntime
from caeos.pairwise_runtime_optimized import OptimizedPairwiseRuntime


ABSOLUTE_TOLERANCE = 1e-12


def equivalence(
    runtime: PairwiseRuntime,
    optimized: OptimizedPairwiseRuntime,
    views: list[np.ndarray],
) -> dict[str, object]:
    reference = runtime.predict(views)
    candidate = optimized.predict(views)
    probability_max_abs = float(
        np.max(np.abs(reference["probability"] - candidate["probability"]))
    )
    risk_max_abs = float(np.max(np.abs(reference["risk"] - candidate["risk"])))
    result = {
        "schema_version": "strict_v4_pairwise_optimized_equivalence_v1",
        "prediction_array_equal": bool(
            np.array_equal(reference["prediction"], candidate["prediction"])
        ),
        "probability_max_absolute_difference": probability_max_abs,
        "risk_max_absolute_difference": risk_max_abs,
        "absolute_tolerance": ABSOLUTE_TOLERANCE,
        "sample_count": int(len(views[0])),
        "unknown_or_test_labels_used": False,
    }
    result["passes"] = bool(
        result["prediction_array_equal"]
        and probability_max_abs <= ABSOLUTE_TOLERANCE
        and risk_max_abs <= ABSOLUTE_TOLERANCE
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gate and benchmark the demand-driven pairwise runtime"
    )
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--batch-sizes", default="1,64,512")
    parser.add_argument("--warmups", type=int, default=5)
    parser.add_argument("--repetitions", type=int, default=30)
    args = parser.parse_args()

    runtime = joblib.load(args.runtime)
    if not isinstance(runtime, PairwiseRuntime):
        raise TypeError("runtime artifact is not a PairwiseRuntime")
    views = load_views(args.inputs)
    optimized = OptimizedPairwiseRuntime(runtime)
    gate = equivalence(runtime, optimized, views)
    if not gate["passes"]:
        raise RuntimeError(f"optimized runtime equivalence failed: {gate}")
    batch_sizes = [int(value) for value in args.batch_sizes.split(",") if value]
    records = benchmark(
        optimized, views, batch_sizes, args.warmups, args.repetitions
    )
    payload = {
        "schema_version": "strict_v4_pairwise_optimized_benchmark_v1",
        "method": "caeos_pairwise_demand_driven",
        "input_sample_count": len(views[0]),
        "view_count": len(views),
        "records": records,
        "peak_host_rss_mb": peak_host_rss_mb(),
        "peak_gpu_memory_mb": 0.0,
        "runtime_evidence": optimized.evidence(),
        "equivalence": gate,
        "unknown_or_test_labels_used": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
