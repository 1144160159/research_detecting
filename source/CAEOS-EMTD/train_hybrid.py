from __future__ import annotations

import argparse
import json
import pickle
import time
from pathlib import Path

import numpy as np
import torch

from caeos.data import prepare_tabular_closed_set
from caeos.hybrid import (
    ConflictAwareHybridClassifier,
    PairwiseSpecialistHybridClassifier,
)
from caeos.multiclass import multiclass_report


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Conflict-aware dual-path tabular traffic classifier"
    )
    parser.add_argument("--csv", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--benign-class", default="benign")
    parser.add_argument("--max-per-class", type=int, default=500)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--estimators", type=int, default=200)
    parser.add_argument("--jobs", type=int, default=-1)
    parser.add_argument("--minimum-view-gain", type=float, default=0.002)
    parser.add_argument("--global-max-features", default="sqrt")
    parser.add_argument("--diverse-global-seeds", action="store_true")
    parser.add_argument("--specialists", type=int, default=0)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument(
        "--split-strategy",
        choices=("random", "fingerprint_grouped", "capture_grouped"),
        default="random",
    )
    parser.add_argument("--output-dir", default="runs/hybrid/latest")
    return parser.parse_args()


def views(dataset) -> list[np.ndarray]:
    return [view.numpy() for view in dataset.views]


def dump_json(path: Path, value: object) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)


def parse_max_features(value: str) -> str | float:
    return value if value in {"sqrt", "log2"} else float(value)


def compact_report(labels, probability, class_names) -> dict[str, float]:
    report = multiclass_report(
        labels,
        torch.as_tensor(probability, dtype=torch.float32),
        class_names,
    )
    return {
        "accuracy": float(report["accuracy"]),
        "macro_f1": float(report["f1_macro"]),
        "ece": float(report["ece"]),
        "nll": float(report["nll"]),
    }


def main() -> None:
    args = parse_arguments()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
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
    model_class = (
        PairwiseSpecialistHybridClassifier
        if args.specialists > 0
        else ConflictAwareHybridClassifier
    )
    model = model_class(
        estimators=args.estimators,
        seed=args.seed,
        jobs=args.jobs,
        minimum_view_gain=args.minimum_view_gain,
        global_max_features=parse_max_features(args.global_max_features),
        global_seed_offsets=(202, 606) if args.diverse_global_seeds else (0, 0),
        **({"max_specialists": args.specialists} if args.specialists > 0 else {}),
    )
    start = time.perf_counter()
    model.fit(
        views(bundle.train),
        bundle.train.labels.numpy(),
        views(bundle.validation),
        bundle.validation.labels.numpy(),
    )
    training_seconds = time.perf_counter() - start

    start = time.perf_counter()
    test_views = views(bundle.test)
    evidence = model.predict_with_evidence(test_views)
    inference_seconds = time.perf_counter() - start
    report = multiclass_report(
        bundle.test.labels,
        torch.as_tensor(evidence["final_probability"], dtype=torch.float32),
        bundle.class_names,
    )
    test_values = np.concatenate(test_views, axis=1)
    rf_probability = model.random_forest.predict_proba(test_values)
    et_probability = model.extra_trees.predict_proba(test_values)
    global_probability = evidence["global_probability"]
    test_ablation = {
        "random_forest": compact_report(
            bundle.test.labels, rf_probability, bundle.class_names
        ),
        "extra_trees": compact_report(
            bundle.test.labels, et_probability, bundle.class_names
        ),
        "validation_weighted_global": compact_report(
            bundle.test.labels, global_probability, bundle.class_names
        ),
        "conflict_gated_final": compact_report(
            bundle.test.labels, evidence["final_probability"], bundle.class_names
        ),
    }
    report.update(
        {
            "model": (
                "mc6_pairwise_specialist_hybrid"
                if args.specialists > 0
                else (
                    "mc7_tree_diversity_hybrid"
                    if args.global_max_features != "sqrt"
                    else "mc5_conflict_aware_hybrid"
                )
            ),
            "estimators_per_learner": args.estimators,
            "global_max_features": model.global_max_features,
            "global_seed_offsets": model.global_seed_offsets,
            "global_rf_weight": model.global_rf_weight,
            "global_et_weight": 1.0 - model.global_rf_weight,
            "view_weight": model.view_weight,
            "conflict_scale": model.conflict_scale,
            "temperature": model.temperature,
            "view_validation_reliability": model.view_validation_reliability.tolist(),
            "validation_scores": model.validation_scores,
            "specialists": (
                model.specialist_metadata()
                if isinstance(model, PairwiseSpecialistHybridClassifier)
                else []
            ),
            "test_ablation": test_ablation,
            "mean_test_conflict": float(evidence["global_conflict"].mean()),
            "mean_test_uncertainty": float(evidence["uncertainty"].mean()),
            "mean_test_gate": float(evidence["gate"].mean()),
            "training_seconds": training_seconds,
            "inference_seconds": inference_seconds,
            "inference_samples_per_second": len(bundle.test) / max(inference_seconds, 1e-9),
        }
    )
    print("metrics=" + json.dumps(report, ensure_ascii=False, sort_keys=True))
    with (output_dir / "model.pkl").open("wb") as handle:
        pickle.dump(model, handle, protocol=pickle.HIGHEST_PROTOCOL)
    dump_json(output_dir / "metrics.json", report)
    dump_json(
        output_dir / "data_metadata.json",
        {
            "class_names": bundle.class_names,
            "modality_names": bundle.modality_names,
            "input_dims": bundle.input_dims,
            "sample_counts": bundle.sample_counts,
            "split_sizes": {
                "train": len(bundle.train),
                "validation": len(bundle.validation),
                "test": len(bundle.test),
            },
            "split_metadata": bundle.split_metadata,
        },
    )


if __name__ == "__main__":
    main()
