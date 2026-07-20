from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

from caeos.data import make_synthetic_open_set, prepare_tabular_open_set
from caeos.hybrid_open_set import evaluate_hybrid_open_set
from caeos.m3s_upd import (
    M3SClassifier,
    align_unlabeled_clusters,
    alignment_threshold,
    class_centroids,
    consistency_selection,
    standardize_embeddings,
)
from caeos.multiclass import count_trainable_parameters
from train_m3s_upd import infer, set_seed, train_classifier, transductive_predict
from train_multiclass import choose_device


PAPER_URL = "https://arxiv.org/abs/2505.21462"
PAPER_DOI = "10.48550/arXiv.2505.21462"
METHOD = "m3s_upd_transductive"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="M3S-UPD paper-formula adapter for strict-v2 shared splits"
    )
    parser.add_argument("--dataset", choices=("synthetic", "tabular"), default="tabular")
    parser.add_argument("--csv")
    parser.add_argument("--config", default="configs/hikari2021.json")
    parser.add_argument("--unknown-classes", required=True)
    parser.add_argument("--benign-class", default="Benign")
    parser.add_argument(
        "--split-strategy",
        choices=("random", "fingerprint_grouped", "capture_grouped"),
        default="random",
    )
    parser.add_argument("--max-per-class", type=int, default=500)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--labeled-fraction", type=float, default=0.30)
    parser.add_argument("--embedding-dim", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--update-rounds", type=int, default=10)
    parser.add_argument("--update-validation-tolerance", type=float, default=5e-4)
    parser.add_argument("--inference-rounds", type=int, default=20)
    parser.add_argument("--dbscan-min-samples", type=int, default=5)
    parser.add_argument("--dbscan-eps-quantile", type=float, default=0.90)
    parser.add_argument("--distance-quantile", type=float, default=0.95)
    parser.add_argument("--top-fraction", type=float, default=0.10)
    parser.add_argument("--bottom-fraction", type=float, default=0.10)
    parser.add_argument("--known-acceptance", type=float, default=0.95)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def dataset_arrays(dataset) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    values = np.concatenate([view.cpu().numpy() for view in dataset.views], axis=1)
    return (
        values.astype(np.float32, copy=False),
        dataset.labels.cpu().numpy().astype(np.int64, copy=False),
        dataset.is_unknown.cpu().numpy().astype(bool, copy=False),
    )


def initial_labeled_indices(
    labels: np.ndarray, labeled_fraction: float, seed: int
) -> np.ndarray:
    if not 0.0 < labeled_fraction <= 1.0:
        raise ValueError("--labeled-fraction must be in (0, 1]")
    rng = np.random.RandomState(seed)
    selected: list[np.ndarray] = []
    for label in sorted(np.unique(labels)):
        indices = np.where(labels == label)[0]
        rng.shuffle(indices)
        count = max(1, int(round(len(indices) * labeled_fraction)))
        selected.append(indices[:count])
    return np.sort(np.concatenate(selected))


def train_known_only(
    model: M3SClassifier,
    train_values: np.ndarray,
    train_labels: np.ndarray,
    validation_values: np.ndarray,
    validation_labels: np.ndarray,
    device: torch.device,
    args: argparse.Namespace,
) -> tuple[np.ndarray, np.ndarray, list[dict[str, object]], dict[str, object]]:
    train_size = len(train_values)
    values = np.concatenate([train_values, validation_values], axis=0)
    model_labels = np.full(len(values), -1, dtype=np.int64)
    validation_indices = np.arange(train_size, len(values), dtype=np.int64)
    model_labels[validation_indices] = validation_labels
    labeled = initial_labeled_indices(train_labels, args.labeled_fraction, args.seed)
    model_labels[labeled] = train_labels[labeled]
    unlabeled = np.setdiff1d(
        np.arange(train_size, dtype=np.int64), labeled, assume_unique=True
    )
    history: list[dict[str, object]] = []
    best_update_validation_loss = float("inf")
    final_training: dict[str, object] = {}
    for iteration in range(args.update_rounds):
        training = train_classifier(
            model,
            values,
            model_labels,
            labeled,
            validation_indices,
            device,
            args.seed + iteration,
            args.epochs,
            args.patience,
            args.batch_size,
            args.learning_rate,
        )
        final_training = training
        if (
            iteration > 0
            and training["best_validation_loss"]
            > best_update_validation_loss + args.update_validation_tolerance
        ):
            history.append(
                {
                    "iteration": iteration + 1,
                    "labeled_before": int(len(labeled)),
                    "pool_before": int(len(unlabeled)),
                    "added_known": 0,
                    "deferred": int(len(unlabeled)),
                    "stop_reason": "known_validation_loss_no_longer_improved",
                    **training,
                }
            )
            break
        best_update_validation_loss = min(
            best_update_validation_loss, float(training["best_validation_loss"])
        )
        if not len(unlabeled):
            break
        probabilities, embeddings = infer(model, values[unlabeled], device)
        _, labeled_embeddings = infer(model, values[labeled], device)
        labeled_standard, unlabeled_standard, _ = standardize_embeddings(
            labeled_embeddings, embeddings
        )
        centroids = class_centroids(
            labeled_standard, model_labels[labeled], len(np.unique(train_labels))
        )
        threshold = alignment_threshold(
            labeled_standard,
            model_labels[labeled],
            centroids,
            args.distance_quantile,
        )
        alignment = align_unlabeled_clusters(
            unlabeled_standard,
            centroids,
            threshold,
            args.dbscan_min_samples,
            args.dbscan_eps_quantile,
        )
        selection = consistency_selection(
            probabilities, alignment, args.top_fraction, args.bottom_fraction
        )
        added = unlabeled[selection.known_indices]
        model_labels[added] = alignment.auxiliary_labels[selection.known_indices]
        pseudo_label_accuracy = (
            float(np.mean(model_labels[added] == train_labels[added]))
            if len(added)
            else None
        )
        labeled = np.sort(np.concatenate([labeled, added]))
        # A strict known-only training split has no eligible unknown pool. Samples
        # flagged as potential unknown remain deferred instead of being exposed.
        deferred_indices = np.union1d(
            selection.unknown_indices, selection.deferred_indices
        )
        deferred = unlabeled[deferred_indices]
        history.append(
            {
                "iteration": iteration + 1,
                "labeled_before": int(len(labeled) - len(added)),
                "pool_before": int(len(unlabeled)),
                "added_known": int(len(added)),
                "potential_unknown_deferred": int(len(selection.unknown_indices)),
                "deferred": int(len(deferred)),
                "pseudo_label_accuracy_audit_only": pseudo_label_accuracy,
                "clusters": int(len(np.unique(alignment.cluster_labels))),
                "dbscan_eps": float(alignment.eps),
                "distance_threshold": float(threshold),
                "confidence_low": float(selection.confidence_low),
                "confidence_high": float(selection.confidence_high),
                **training,
            }
        )
        if not len(added):
            break
        unlabeled = deferred
    return labeled, model_labels[labeled].copy(), history, final_training


def run(args: argparse.Namespace) -> dict[str, object]:
    set_seed(args.seed)
    unknown_classes = [
        value.strip() for value in args.unknown_classes.split(",") if value.strip()
    ]
    if args.dataset == "synthetic":
        bundle = make_synthetic_open_set(seed=args.seed)
    else:
        if not args.csv:
            raise ValueError("--csv is required for tabular data")
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        bundle = prepare_tabular_open_set(
            args.csv,
            config,
            unknown_classes,
            args.benign_class,
            args.max_per_class,
            args.chunksize,
            args.seed,
            args.split_strategy,
        )
    train_values, train_labels, train_unknown = dataset_arrays(bundle.train)
    validation_values, validation_labels, validation_unknown = dataset_arrays(
        bundle.validation
    )
    test_values, test_labels, test_unknown = dataset_arrays(bundle.test)
    if train_unknown.any() or validation_unknown.any():
        raise ValueError("strict-v2 M3S-UPD fitting splits must be known-only")
    device = choose_device(args.device)
    model = M3SClassifier(
        train_values.shape[1],
        len(bundle.class_names),
        embedding_dim=args.embedding_dim,
    ).to(device)
    started = time.perf_counter()
    labeled, labeled_model_labels, update_history, final_training = train_known_only(
        model,
        train_values,
        train_labels,
        validation_values,
        validation_labels,
        device,
        args,
    )
    training_seconds = time.perf_counter() - started
    _, labeled_embeddings = infer(model, train_values[labeled], device)
    validation_probabilities, validation_embeddings = infer(
        model, validation_values, device
    )
    _, validation_risk, validation_history = transductive_predict(
        validation_probabilities,
        validation_embeddings,
        labeled_embeddings,
        labeled_model_labels,
        len(bundle.class_names),
        args.inference_rounds,
        args.dbscan_min_samples,
        args.dbscan_eps_quantile,
        args.distance_quantile,
        args.top_fraction,
        args.bottom_fraction,
    )
    test_probabilities, test_embeddings = infer(model, test_values, device)
    transductive_prediction, test_risk, test_history = transductive_predict(
        test_probabilities,
        test_embeddings,
        labeled_embeddings,
        labeled_model_labels,
        len(bundle.class_names),
        args.inference_rounds,
        args.dbscan_min_samples,
        args.dbscan_eps_quantile,
        args.distance_quantile,
        args.top_fraction,
        args.bottom_fraction,
    )
    threshold = float(np.quantile(validation_risk, args.known_acceptance))
    prediction = test_probabilities.argmax(axis=1)
    report = evaluate_hybrid_open_set(
        test_labels, test_unknown, prediction, test_risk, threshold
    )
    return {
        "model": METHOD,
        "method": METHOD,
        "unknown_classes": unknown_classes,
        "seed": args.seed,
        "known_class_names": bundle.class_names,
        "sample_counts": bundle.sample_counts,
        "split_metadata": bundle.split_metadata,
        "split_sizes": {
            "train": len(bundle.train),
            "validation": len(bundle.validation),
            "test": len(bundle.test),
            "test_unknown": int(test_unknown.sum()),
        },
        "validation_thresholds": {METHOD: threshold},
        "reports": {METHOD: report},
        "training_history": update_history,
        "training_seconds": training_seconds,
        "trainable_parameters": count_trainable_parameters(model),
        "paper_reference": {"url": PAPER_URL, "doi": PAPER_DOI, "version": "v1"},
        "protocol_class": "secondary_transductive",
        "implementation": (
            "M3S-UPD paper-formula adapter using the shared strict-v2 known-only "
            "split; whole validation/test feature batches are clustered without labels "
            "or parameter updates, so results are secondary to inductive baselines"
        ),
        "selection_evidence": {
            "training_splits": "known_only_train_and_known_only_validation",
            "initial_labeled_fraction": args.labeled_fraction,
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
            "test_labels_used_for_final_metrics_only": True,
            "test_features_used_jointly_for_transductive_clustering": True,
            "eligible_for_primary_inductive_table": False,
        },
        "adapter_parameters": {
            "network": "MLP-128-64-32",
            "network_disclosed_by_paper": False,
            "dbscan_min_samples": args.dbscan_min_samples,
            "dbscan_eps_quantile": args.dbscan_eps_quantile,
            "distance_quantile": args.distance_quantile,
            "top_fraction": args.top_fraction,
            "bottom_fraction": args.bottom_fraction,
        },
        "validation_inference_history": validation_history,
        "test_inference_history": test_history,
        "final_training": final_training,
        "arguments": vars(args),
        "_artifacts": {
            "validation_labels": validation_labels,
            "validation_risk": validation_risk,
            "test_labels": test_labels,
            "test_unknown": test_unknown,
            "test_probability": test_probabilities,
            "test_prediction": prediction,
            "test_transductive_prediction": transductive_prediction,
            "test_risk": test_risk,
        },
        "_model": model,
        "_input_dims": bundle.input_dims,
    }


def main() -> None:
    args = parse_arguments()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    result = run(args)
    artifacts = result.pop("_artifacts")
    model = result.pop("_model")
    input_dims = result.pop("_input_dims")
    (output_dir / "metrics.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    np.savez_compressed(output_dir / "scores.npz", **artifacts)
    np.savez_compressed(
        output_dir / "evidence_package.npz",
        validation_risk=artifacts["validation_risk"],
        test_risk=artifacts["test_risk"],
        test_unknown=artifacts["test_unknown"],
    )
    torch.save(
        {
            "model_state": model.state_dict(),
            "arguments": vars(args),
            "class_names": result["known_class_names"],
            "input_dims": input_dims,
        },
        output_dir / "model.pt",
    )
    print("metrics=" + json.dumps(result["reports"], sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
