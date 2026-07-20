from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
from torch.utils.data import DataLoader

from caeos.data import prepare_tabular_open_set
from caeos.closr import CLOSRClassifier, closr_risk
from caeos.hybrid_open_set import KnownKnnDistance
from caeos.multiclass import ConcatMLPClassifier
from caeos.open_detect import OpenDetectClassifier, open_detect_risk
from caeos.nested_neural import (
    CandidateAggregate,
    RemappedSubset,
    aggregate_scores,
    pseudo_unknown_auroc,
    select_candidate,
)
from caeos.neural_open_set import SharedCovarianceMahalanobis
from train_multiclass import choose_device, set_seed, weighted_sampler
from train_neural_open_set import collect, train


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validation-only nested gate over hybrid and neural open-set risks"
    )
    parser.add_argument("--csv", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--unknown-classes", required=True)
    parser.add_argument("--benign-class", default="Benign")
    parser.add_argument(
        "--split-strategy",
        choices=("random", "fingerprint_grouped", "capture_grouped"),
        default="fingerprint_grouped",
    )
    parser.add_argument("--max-per-class", type=int, default=2000)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--epochs", type=int, default=35)
    parser.add_argument("--patience", type=int, default=7)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--embedding-dim", type=int, default=64)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--knn-neighbors", type=int, default=10)
    parser.add_argument(
        "--candidate-model", choices=("mlp", "closr", "opendetect"), default="mlp"
    )
    parser.add_argument("--closr-depth", type=int, default=3)
    parser.add_argument("--closr-margin", type=float, default=1.0)
    parser.add_argument("--closr-alpha", type=float, default=0.5)
    parser.add_argument("--open-detect-temperature", type=float, default=1.0)
    parser.add_argument("--open-detect-generative-weight", type=float, default=0.005)
    parser.add_argument("--open-detect-reset-epochs", default="50,80")
    parser.add_argument("--minimum-neural-gain", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--no-amp", action="store_true")
    parser.add_argument("--gate-metrics", required=True)
    parser.add_argument("--neural-metrics", required=True)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def inner_training_arguments(args: argparse.Namespace, seed: int) -> SimpleNamespace:
    return SimpleNamespace(
        model=args.candidate_model,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        no_amp=args.no_amp,
        epochs=args.epochs,
        patience=args.patience,
        contrast_weight=0.0,
        contrast_temperature=0.1,
        closr_margin=args.closr_margin,
        closr_alpha=args.closr_alpha,
        open_detect_reset_epochs=args.open_detect_reset_epochs,
        seed=seed,
    )


def fit_inner_candidate(bundle, held_out: int, device, args):
    train_labels = bundle.train.labels.numpy()
    validation_labels = bundle.validation.labels.numpy()
    train_indices = np.flatnonzero(train_labels != held_out)
    validation_known_indices = np.flatnonzero(validation_labels != held_out)
    validation_all_indices = np.arange(len(validation_labels))
    remaining = sorted(set(train_labels[train_indices].tolist()))
    label_map = {old: new for new, old in enumerate(remaining)}

    train_set = RemappedSubset(bundle.train, train_indices, label_map)
    validation_known = RemappedSubset(
        bundle.validation, validation_known_indices, label_map
    )
    validation_all = RemappedSubset(
        bundle.validation,
        validation_all_indices,
        label_map,
        pseudo_unknown_class=held_out,
    )
    loader_options = {
        "batch_size": args.batch_size,
        "num_workers": args.num_workers,
        "pin_memory": device.type == "cuda",
    }
    natural_sampling = args.candidate_model == "opendetect"
    train_loader = DataLoader(
        train_set,
        sampler=None if natural_sampling else weighted_sampler(train_set.labels),
        shuffle=natural_sampling,
        **loader_options,
    )
    validation_loader = DataLoader(
        validation_known, shuffle=False, **loader_options
    )
    fit_loader = DataLoader(train_set, shuffle=False, **loader_options)
    pseudo_loader = DataLoader(validation_all, shuffle=False, **loader_options)

    inner_seed = args.seed + 5000 + held_out
    set_seed(inner_seed)
    if args.candidate_model == "closr":
        model = CLOSRClassifier(
            bundle.input_dims,
            len(remaining),
            args.hidden_dim,
            args.embedding_dim,
            args.closr_depth,
            args.dropout,
            args.closr_margin,
            True,
            args.closr_alpha,
        ).to(device)
    elif args.candidate_model == "opendetect":
        model = OpenDetectClassifier(
            bundle.input_dims,
            len(remaining),
            args.hidden_dim,
            args.embedding_dim,
            args.dropout,
            args.open_detect_temperature,
            args.open_detect_generative_weight,
        ).to(device)
    else:
        model = ConcatMLPClassifier(
            bundle.input_dims,
            len(remaining),
            args.hidden_dim,
            args.embedding_dim,
            args.dropout,
        ).to(device)
    history = train(
        model,
        train_loader,
        validation_loader,
        device,
        inner_training_arguments(args, inner_seed),
    )
    training = collect(model, fit_loader, device)
    if args.candidate_model == "closr":
        model.fit_centroids(training["embedding"], training["labels"])
        validation = collect(model, pseudo_loader, device)
        candidate_risk = closr_risk(validation["logits"])
        candidate_scores = {
            "closr": pseudo_unknown_auroc(
                validation_labels, candidate_risk, held_out
            )
        }
    elif args.candidate_model == "opendetect":
        validation = collect(model, pseudo_loader, device)
        candidate_risk = open_detect_risk(validation["logits"])
        candidate_scores = {
            "opendetect": pseudo_unknown_auroc(
                validation_labels, candidate_risk, held_out
            )
        }
    else:
        validation = collect(model, pseudo_loader, device)

        mahalanobis = SharedCovarianceMahalanobis()
        mahalanobis.fit(training["embedding"], training["labels"])
        mahalanobis_risk = mahalanobis.score(validation["embedding"])
        knn = KnownKnnDistance(args.knn_neighbors)
        knn.fit(training["embedding"])
        knn_risk = knn.score(validation["embedding"])
        candidate_scores = {
            "neural_mahalanobis": pseudo_unknown_auroc(
                validation_labels, mahalanobis_risk, held_out
            ),
            "neural_knn": pseudo_unknown_auroc(
                validation_labels, knn_risk, held_out
            ),
        }
    finite_validation_scores = [
        value["validation_macro_f1"]
        for value in history
        if value["validation_macro_f1"] is not None
    ]
    return {
        "class_index": held_out,
        "class_name": bundle.class_names[held_out],
        "known_validation_samples": int((validation_labels != held_out).sum()),
        "pseudo_unknown_samples": int((validation_labels == held_out).sum()),
        **candidate_scores,
        "epochs_trained": len(history),
        "best_validation_macro_f1": (
            max(finite_validation_scores) if finite_validation_scores else None
        ),
    }


def as_aggregate(value: dict[str, float]) -> CandidateAggregate:
    return CandidateAggregate(
        mean_auroc=float(value["mean_auroc"]),
        minimum_auroc=float(value["minimum_auroc"]),
        robust_objective=float(value["robust_objective"]),
    )


def resolve_gate_candidate(gate_metrics: dict) -> tuple[str, CandidateAggregate, dict]:
    details = gate_metrics["risk_selection_details"]
    selected = details.get("selected_risk") or gate_metrics.get("selected_risk")
    if selected is None:
        candidates = details["candidate_aggregates"]
        selected = max(
            candidates,
            key=lambda name: (
                candidates[name]["robust_objective"],
                candidates[name]["minimum_auroc"],
                candidates[name]["mean_auroc"],
            ),
        )
    aggregate = as_aggregate(details["candidate_aggregates"][selected])
    report = details.get("selected_report") or gate_metrics["reports"][selected]
    return selected, aggregate, report


def main() -> None:
    args = parse_arguments()
    started = time.perf_counter()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(args.config, "r", encoding="utf-8") as handle:
        config = json.load(handle)
    unknown_classes = [
        value.strip() for value in args.unknown_classes.split(",") if value.strip()
    ]
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
    with open(args.gate_metrics, "r", encoding="utf-8") as handle:
        gate_metrics = json.load(handle)
    with open(args.neural_metrics, "r", encoding="utf-8") as handle:
        neural_metrics = json.load(handle)
    if gate_metrics["known_class_names"] != bundle.class_names:
        raise ValueError("gate metrics and reconstructed bundle use different classes")
    if neural_metrics["known_class_names"] != bundle.class_names:
        raise ValueError("neural metrics and reconstructed bundle use different classes")

    device = choose_device(args.device)
    held_out_reports = []
    for held_out in range(1, len(bundle.class_names)):
        report = fit_inner_candidate(bundle, held_out, device, args)
        held_out_reports.append(report)
        candidate_fields = {
            name: value
            for name, value in report.items()
            if name in {"neural_mahalanobis", "neural_knn", "closr", "opendetect"}
        }
        print(
            "held_out=%s candidates=%s"
            % (report["class_name"], json.dumps(candidate_fields, sort_keys=True)),
            flush=True,
        )

    existing = gate_metrics["risk_selection_details"]["candidate_aggregates"]
    gate_selected_name, gate_aggregate, gate_selected_report = resolve_gate_candidate(
        gate_metrics
    )
    if args.candidate_model in {"closr", "opendetect"}:
        candidate_name = args.candidate_model
        aggregates = {
            "caeos_gate": gate_aggregate,
            candidate_name: aggregate_scores(
                [report[candidate_name] for report in held_out_reports]
            ),
        }
        neural_candidates = (candidate_name,)
    else:
        aggregates = {
            "support_union": as_aggregate(existing["support_union"]),
            "cauchy_evidence": as_aggregate(existing["cauchy_evidence"]),
            "neural_mahalanobis": aggregate_scores(
                [report["neural_mahalanobis"] for report in held_out_reports]
            ),
            "neural_knn": aggregate_scores(
                [report["neural_knn"] for report in held_out_reports]
            ),
        }
        neural_candidates = ("neural_mahalanobis", "neural_knn")
    selected, reason = select_candidate(
        aggregates,
        neural_candidates=neural_candidates,
        minimum_neural_gain=args.minimum_neural_gain,
    )
    if selected == "caeos_gate":
        selected_report = gate_selected_report
    elif selected in {"support_union", "cauchy_evidence"}:
        selected_report = gate_metrics["reports"][selected]
    else:
        neural_name = (
            selected
            if selected in {"closr", "opendetect"}
            else selected.removeprefix("neural_")
        )
        selected_report = neural_metrics["reports"][neural_name]

    if args.candidate_model in {"closr", "opendetect"}:
        candidate_name = args.candidate_model
        candidate_outer_auroc = {
            "caeos_gate": gate_selected_report["unknown_auroc"],
            candidate_name: neural_metrics["reports"][candidate_name]["unknown_auroc"],
        }
    else:
        candidate_outer_auroc = {
            "support_union": gate_metrics["reports"]["support_union"]["unknown_auroc"],
            "cauchy_evidence": gate_metrics["reports"]["cauchy_evidence"]["unknown_auroc"],
            "neural_mahalanobis": neural_metrics["reports"]["mahalanobis"]["unknown_auroc"],
            "neural_knn": neural_metrics["reports"]["knn"]["unknown_auroc"],
        }
    result = {
        "unknown_classes": unknown_classes,
        "seed": args.seed,
        "known_class_names": bundle.class_names,
        "selection_rule": "0.5 * inner mean AUROC + 0.5 * inner minimum AUROC",
        "minimum_neural_gain": args.minimum_neural_gain,
        "gate_selected_risk": gate_selected_name,
        "candidate_model": args.candidate_model,
        "candidate_aggregates": {
            name: value.__dict__ for name, value in aggregates.items()
        },
        "held_out_reports": held_out_reports,
        "selected_risk": selected,
        "selection_reason": reason,
        "selected_report": selected_report,
        "candidate_outer_auroc": candidate_outer_auroc,
        "outer_oracle_auroc": max(candidate_outer_auroc.values()),
        "outer_regret": max(candidate_outer_auroc.values())
        - selected_report["unknown_auroc"],
        "elapsed_seconds": time.perf_counter() - started,
        "arguments": vars(args),
    }
    with (output_dir / "metrics.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    print("metrics=" + json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
