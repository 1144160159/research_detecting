from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import f1_score

from caeos.data import prepare_tabular_closed_set
from caeos.hybrid import CorruptionRobustHybridClassifier, _normalize_probability
from train_hybrid import parse_max_features


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MC8 modality corruption evaluation")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--benign-class", default="benign")
    parser.add_argument("--max-per-class", type=int, default=500)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--estimators", type=int, default=200)
    parser.add_argument("--jobs", type=int, default=-1)
    parser.add_argument("--global-max-features", default="0.5")
    parser.add_argument("--minimum-robust-gain", type=float, default=0.0005)
    parser.add_argument("--clean-tolerance", type=float, default=0.002)
    parser.add_argument("--advanced-robust-search", action="store_true")
    parser.add_argument(
        "--safety-fallback-mode",
        choices=("none", "validation_minimax"),
        default="none",
    )
    parser.add_argument("--robust-minimum-weight", type=float, default=0.3)
    parser.add_argument(
        "--routing-conflict-mode",
        choices=(
            "global",
            "probabilistic_or",
            "adaptive_missingness",
            "local_max",
            "calibrated_local",
        ),
        default="global",
    )
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument(
        "--split-strategy",
        choices=("random", "fingerprint_grouped", "capture_grouped"),
        default="random",
    )
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def views(dataset) -> list[np.ndarray]:
    return [view.numpy() for view in dataset.views]


def macro_f1(labels: np.ndarray, probability: np.ndarray) -> float:
    return float(
        f1_score(
            labels,
            probability.argmax(axis=1),
            average="macro",
            zero_division=0,
        )
    )


def method_scores(labels: np.ndarray, evidence) -> dict[str, float]:
    uniform = _normalize_probability(evidence["view_probability"].mean(axis=1))
    return {
        "global": macro_f1(labels, evidence["global_probability"]),
        "standard": macro_f1(labels, evidence["standard_final_probability"]),
        "uniform_views": macro_f1(labels, uniform),
        "reliability_views": macro_f1(labels, evidence["view_fused_probability"]),
        "robust_views": macro_f1(labels, evidence["robust_view_probability"]),
        "mc8_robust": macro_f1(labels, evidence["final_probability"]),
    }


def corruption_cases(test_views: list[np.ndarray], seed: int):
    yield "clean", -1, 0.0, [view.copy() for view in test_views]
    for view_index, view in enumerate(test_views):
        rng = np.random.RandomState(seed + 9001 + view_index)
        permutation = rng.permutation(len(view))
        corrupted = [values.copy() for values in test_views]
        corrupted[view_index] = view[permutation]
        yield "permutation", view_index, 1.0, corrupted
        for severity in (0.5, 1.0, 2.0, 4.0):
            corrupted = [values.copy() for values in test_views]
            corrupted[view_index] = view + rng.normal(
                0.0, severity, size=view.shape
            )
            yield "gaussian", view_index, severity, corrupted


def main() -> None:
    args = parse_arguments()
    with open(args.config, "r", encoding="utf-8") as handle:
        config = json.load(handle)
    bundle = prepare_tabular_closed_set(
        args.csv,
        config,
        args.benign_class,
        args.max_per_class,
        args.chunksize,
        args.seed,
        args.split_strategy,
    )
    model = CorruptionRobustHybridClassifier(
        estimators=args.estimators,
        seed=args.seed,
        jobs=args.jobs,
        minimum_view_gain=0.002,
        minimum_robust_gain=args.minimum_robust_gain,
        clean_tolerance=args.clean_tolerance,
        advanced_robust_search=args.advanced_robust_search,
        safety_fallback_mode=args.safety_fallback_mode,
        robust_minimum_weight=args.robust_minimum_weight,
        routing_conflict_mode=args.routing_conflict_mode,
        global_max_features=parse_max_features(args.global_max_features),
        global_seed_offsets=(202, 606),
    )
    model.fit(
        views(bundle.train),
        bundle.train.labels.numpy(),
        views(bundle.validation),
        bundle.validation.labels.numpy(),
    )
    test_views = views(bundle.test)
    labels = bundle.test.labels.numpy()
    rows = []
    for kind, view_index, severity, corrupted in corruption_cases(test_views, args.seed):
        evidence = model.predict_with_evidence(corrupted)
        row = {
            "kind": kind,
            "view_index": view_index,
            "view_name": bundle.modality_names[view_index] if view_index >= 0 else "none",
            "severity": severity,
            **method_scores(labels, evidence),
            "mean_global_conflict": float(evidence["global_conflict"].mean()),
            "mean_global_view_conflict": float(
                evidence["global_view_conflict"].mean()
            ),
            "mean_robust_gate": float(evidence["robust_gate"].mean()),
        }
        if view_index >= 0:
            row["corrupted_view_reliability"] = float(
                evidence["view_reliability"][:, view_index].mean()
            )
            row["corrupted_view_local_conflict"] = float(
                evidence["local_conflict"][:, view_index].mean()
            )
        rows.append(row)
    corrupted_rows = [row for row in rows if row["kind"] != "clean"]
    methods = (
        "global",
        "standard",
        "uniform_views",
        "reliability_views",
        "robust_views",
        "mc8_robust",
    )
    aggregate = {
        method: {
            "mean_corrupted_macro_f1": float(
                np.mean([row[method] for row in corrupted_rows])
            ),
            "minimum_corrupted_macro_f1": float(
                np.min([row[method] for row in corrupted_rows])
            ),
            "clean_macro_f1": rows[0][method],
        }
        for method in methods
    }
    result = {
        "model": "mc8_corruption_robust_hybrid",
        "seed": args.seed,
        "modality_names": bundle.modality_names,
        "split_metadata": bundle.split_metadata,
        "selected_parameters": {
            "discount_scale": model.robust_discount_scale,
            "maximum_view_weight": model.robust_max_view_weight,
            "conflict_threshold": model.robust_conflict_threshold,
            "transition_width": model.robust_transition_width,
            "trim_count": model.robust_trim_count,
            "clean_tolerance": model.clean_tolerance,
            "advanced_robust_search": model.advanced_robust_search,
            "safety_fallback_mode": model.safety_fallback_mode,
            "safety_use_uniform": model.safety_use_uniform,
        },
        "validation_scores": model.robust_validation_scores,
        "aggregate": aggregate,
        "cases": rows,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
