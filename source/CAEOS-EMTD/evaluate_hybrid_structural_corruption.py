from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from caeos.data import prepare_tabular_closed_set
from caeos.hybrid import CorruptionRobustHybridClassifier
from evaluate_hybrid_corruption import method_scores, views
from train_hybrid import parse_max_features


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="MC8 structural modality-corruption evaluation"
    )
    parser.add_argument("--csv", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--benign-class", default="benign")
    parser.add_argument("--max-per-class", type=int, default=500)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--estimators", type=int, default=200)
    parser.add_argument("--global-max-features", default="0.5")
    parser.add_argument("--robust-minimum-weight", type=float, default=0.3)
    parser.add_argument(
        "--routing-conflict-mode",
        choices=("global", "probabilistic_or", "adaptive_missingness"),
        default="global",
    )
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def structural_corruption_cases(
    test_views: list[np.ndarray], modality_names: list[str], seed: int
):
    yield "clean", -1, 0.0, [view.copy() for view in test_views]
    for view_index, view in enumerate(test_views):
        rng = np.random.RandomState(seed + 12001 + view_index)

        corrupted = [values.copy() for values in test_views]
        corrupted[view_index] = np.zeros_like(view)
        yield "modality_missing", view_index, 1.0, corrupted

        for severity in (0.25, 0.50, 0.75):
            corrupted = [values.copy() for values in test_views]
            missing = rng.rand(*view.shape) < severity
            corrupted[view_index] = np.where(missing, 0.0, view)
            yield "field_missing", view_index, severity, corrupted

        for severity in (0.25, 0.50, 0.75):
            corrupted = [values.copy() for values in test_views]
            missing_rows = rng.rand(len(view)) < severity
            corrupted[view_index][missing_rows] = 0.0
            yield "intermittent_missing", view_index, severity, corrupted

        if modality_names[view_index] == "packet_sequence":
            for severity in (0.25, 0.50, 0.75):
                corrupted = [values.copy() for values in test_views]
                retained = max(1, int(round(view.shape[1] * (1.0 - severity))))
                corrupted[view_index][:, retained:] = 0.0
                yield "sequence_truncation", view_index, severity, corrupted


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
    )
    model = CorruptionRobustHybridClassifier(
        estimators=args.estimators,
        seed=args.seed,
        minimum_view_gain=0.002,
        minimum_robust_gain=0.0005,
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
    for kind, view_index, severity, corrupted in structural_corruption_cases(
        test_views, bundle.modality_names, args.seed
    ):
        evidence = model.predict_with_evidence(corrupted)
        row = {
            "kind": kind,
            "view_index": view_index,
            "view_name": (
                bundle.modality_names[view_index] if view_index >= 0 else "none"
            ),
            "severity": severity,
            **method_scores(labels, evidence),
            "mean_global_conflict": float(evidence["global_conflict"].mean()),
            "mean_global_view_conflict": float(
                evidence["global_view_conflict"].mean()
            ),
            "mean_robust_gate": float(evidence["robust_gate"].mean()),
            "mean_missingness_score": float(evidence["missingness_score"].mean()),
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
    by_kind = {
        kind: {
            method: float(
                np.mean(
                    [
                        row[method]
                        for row in corrupted_rows
                        if row["kind"] == kind
                    ]
                )
            )
            for method in methods
        }
        for kind in sorted({row["kind"] for row in corrupted_rows})
    }
    result = {
        "model": "mc8_v2_structural_corruption",
        "seed": args.seed,
        "modality_names": bundle.modality_names,
        "selected_parameters": {
            "discount_scale": model.robust_discount_scale,
            "maximum_view_weight": model.robust_max_view_weight,
            "conflict_threshold": model.robust_conflict_threshold,
            "transition_width": model.robust_transition_width,
        },
        "validation_scores": model.robust_validation_scores,
        "aggregate": aggregate,
        "by_kind": by_kind,
        "cases": rows,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
