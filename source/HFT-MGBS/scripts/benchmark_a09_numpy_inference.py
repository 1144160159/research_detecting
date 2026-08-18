#!/usr/bin/env python3
"""Benchmark and equivalence-gate the opt-in A09 NumPy tree executor."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import sklearn

from hft_mgbs.a09_numpy_inference import A09NumpyExactPredictor


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def percentile(values, quantile):
    ordered = sorted(values)
    rank = int(np.ceil((len(ordered) - 1) * quantile))
    return float(ordered[rank])


def sklearn_probability(models, positive_indices, matrix):
    return np.mean(
        [
            model.predict_proba(matrix)[:, positive_index]
            for model, positive_index in zip(models, positive_indices)
        ],
        axis=0,
    )


def validation_matrix(models, feature_count, rows, seed):
    rng = np.random.RandomState(seed)
    matrix = rng.normal(size=(rows, feature_count)).astype(np.float32)
    probes = []
    for model in models:
        for estimator in model.estimators_[: min(8, len(model.estimators_))]:
            tree = estimator.tree_
            for node in np.flatnonzero(tree.children_left != -1)[:4]:
                feature = int(tree.feature[node])
                split = np.float32(tree.threshold[node])
                for value in (
                    np.nextafter(split, np.float32(-np.inf), dtype=np.float32),
                    split,
                    np.nextafter(split, np.float32(np.inf), dtype=np.float32),
                ):
                    row = np.zeros(feature_count, dtype=np.float32)
                    row[feature] = value
                    probes.append(row)
    if probes:
        matrix = np.concatenate((matrix, np.asarray(probes, dtype=np.float32)))
    return matrix


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--batch-sizes", type=int, nargs="+", default=[1, 8])
    parser.add_argument("--warmup", type=int, default=25)
    parser.add_argument("--repeats", type=int, default=200)
    parser.add_argument("--validation-rows", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=20260813)
    parser.add_argument("--max-p99-us", type=float, default=10000.0)
    args = parser.parse_args()
    if args.warmup < 1 or args.repeats < 20 or args.validation_rows < 128:
        parser.error("warmup>=1, repeats>=20, and validation-rows>=128 are required")
    if any(batch_size < 1 or batch_size > 8 for batch_size in args.batch_sizes):
        parser.error("this low-latency gate only admits batch sizes 1..8")
    if args.max_p99_us <= 0.0:
        parser.error("max-p99-us must be positive")

    bundle = joblib.load(args.model)
    if bundle.get("candidate_id") != "A09":
        raise ValueError("model bundle candidate_id is not A09")
    models = tuple(bundle.get("models") or ())
    positive_indices = tuple(int(value) for value in bundle.get("positive_indices") or ())
    thresholds = tuple(float(value) for value in bundle.get("thresholds") or ())
    if len(models) != 3 or len(positive_indices) != 3 or len(thresholds) != 3:
        raise ValueError("frozen A09 bundle must contain three models, indices, and thresholds")
    # Match gpu_service's frozen default runtime.  n_jobs changes execution
    # only; it does not alter fitted tree bytes or thresholds.
    for model in models:
        model.set_params(n_jobs=1)
    threshold = float(statistics.median(thresholds))

    compile_started = time.perf_counter_ns()
    predictor = A09NumpyExactPredictor(models, positive_indices)
    compile_us = (time.perf_counter_ns() - compile_started) / 1000.0
    matrix = validation_matrix(
        models, predictor.feature_count, args.validation_rows, args.seed
    )
    expected = sklearn_probability(models, positive_indices, matrix)
    actual = predictor.predict_positive_probability(matrix)
    member_equivalence = []
    for member_index, (model, positive_index, forest) in enumerate(
        zip(models, positive_indices, predictor._forests)
    ):
        member_expected = model.predict_proba(matrix)[:, positive_index]
        member_actual = forest.predict_positive_probability(matrix)
        manual_sklearn = np.zeros(matrix.shape[0], dtype=np.float64)
        compiled_via_sklearn_apply = np.zeros(matrix.shape[0], dtype=np.float64)
        tree_leaf_max_abs_error = 0.0
        direct_value_max_abs_error = 0.0
        normalized_value_max_abs_error = 0.0
        for tree_index, estimator in enumerate(model.estimators_):
            tree_expected = estimator.predict_proba(matrix)[:, positive_index]
            leaves = estimator.apply(matrix)
            compiled_leaf = forest.positive_probability[tree_index, leaves]
            leaf_values = estimator.tree_.value[leaves, 0, :]
            direct_value = leaf_values[:, positive_index]
            normalized_value = direct_value / leaf_values.sum(axis=1)
            tree_leaf_max_abs_error = max(
                tree_leaf_max_abs_error,
                float(np.max(np.abs(tree_expected - compiled_leaf))),
            )
            direct_value_max_abs_error = max(
                direct_value_max_abs_error,
                float(np.max(np.abs(tree_expected - direct_value))),
            )
            normalized_value_max_abs_error = max(
                normalized_value_max_abs_error,
                float(np.max(np.abs(tree_expected - normalized_value))),
            )
            manual_sklearn += tree_expected
            compiled_via_sklearn_apply += compiled_leaf
        manual_sklearn /= len(model.estimators_)
        compiled_via_sklearn_apply /= len(model.estimators_)
        member_equivalence.append(
            {
                "member_index": member_index,
                "probability_max_abs_error": float(
                    np.max(np.abs(member_expected - member_actual))
                ),
                "probability_byte_identical": bool(
                    np.array_equal(member_expected, member_actual)
                ),
                "tree_leaf_max_abs_error": tree_leaf_max_abs_error,
                "direct_value_max_abs_error": direct_value_max_abs_error,
                "normalized_value_max_abs_error": normalized_value_max_abs_error,
                "sklearn_forest_vs_sequential_tree_max_abs_error": float(
                    np.max(np.abs(member_expected - manual_sklearn))
                ),
                "compiled_traversal_vs_sklearn_apply_max_abs_error": float(
                    np.max(np.abs(member_actual - compiled_via_sklearn_apply))
                ),
            }
        )
    max_abs_error = float(np.max(np.abs(expected - actual)))
    byte_identical = bool(np.array_equal(expected, actual))
    label_mismatches = int(np.count_nonzero((expected >= threshold) != (actual >= threshold)))

    rng = np.random.RandomState(args.seed + 1)
    results = []
    for batch_size in args.batch_sizes:
        batch = rng.normal(size=(batch_size, predictor.feature_count)).astype(np.float32)
        for _ in range(args.warmup):
            predictor.predict_positive_probability(batch)
        samples_us = []
        for _ in range(args.repeats):
            started = time.perf_counter_ns()
            predictor.predict_positive_probability(batch)
            samples_us.append((time.perf_counter_ns() - started) / 1000.0)
        results.append(
            {
                "batch_size": batch_size,
                "repeats": args.repeats,
                "latency_p50_us": float(statistics.median(samples_us)),
                "latency_p99_us": percentile(samples_us, 0.99),
                "latency_max_us": float(max(samples_us)),
                "p99_gate_us": args.max_p99_us,
                "p99_gate_passed": percentile(samples_us, 0.99) <= args.max_p99_us,
            }
        )

    module_path = Path(__file__).resolve().parents[1] / "hft_mgbs" / "a09_numpy_inference.py"
    accepted = (
        byte_identical
        and max_abs_error == 0.0
        and label_mismatches == 0
        and all(result["p99_gate_passed"] for result in results)
    )
    payload = {
        "schema_version": 1,
        "scope": "A09_runtime_only_no_model_or_threshold_change",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "candidate_id": "A09",
        "engine": predictor.engine_name,
        "model_sha256": sha256(args.model),
        "engine_sha256": sha256(module_path),
        "numpy_version": np.__version__,
        "sklearn_version": sklearn.__version__,
        "model_count": len(models),
        "tree_counts": list(predictor.tree_counts),
        "feature_count": predictor.feature_count,
        "thresholds": list(thresholds),
        "effective_threshold": threshold,
        "compile_us": compile_us,
        "equivalence": {
            "validation_rows": int(matrix.shape[0]),
            "seed": args.seed,
            "probability_max_abs_error": max_abs_error,
            "probability_byte_identical": byte_identical,
            "threshold_label_mismatches": label_mismatches,
            "members": member_equivalence,
        },
        "latency": results,
        "accepted": accepted,
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_name(args.output.name + ".tmp")
        temporary.write_text(rendered, encoding="utf-8")
        temporary.replace(args.output)
    print(rendered, end="")
    return 0 if accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
