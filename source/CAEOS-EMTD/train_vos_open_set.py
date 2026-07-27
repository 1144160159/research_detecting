from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

import numpy as np
import torch
from sklearn.metrics import f1_score
from torch.utils.data import DataLoader

from caeos.data import make_synthetic_open_set, prepare_tabular_open_set
from caeos.hybrid_open_set import evaluate_hybrid_open_set
from caeos.multiclass import count_trainable_parameters
from caeos.vos import ClassConditionalGaussianQueue, VOSClassifier
from train_multiclass import choose_device, move_batch, set_seed, weighted_sampler


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Strict known-only VOS baseline")
    parser.add_argument("--dataset", choices=("tabular", "synthetic"), default="tabular")
    parser.add_argument("--csv")
    parser.add_argument("--config")
    parser.add_argument("--unknown-classes", required=True)
    parser.add_argument("--benign-class", default="Benign")
    parser.add_argument(
        "--split-strategy",
        choices=("random", "fingerprint_grouped", "capture_grouped"),
        default="fingerprint_grouped",
    )
    parser.add_argument("--max-per-class", type=int, default=5000)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--epochs", type=int, default=35)
    parser.add_argument("--start-epoch", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--hidden-dim", type=int, default=256)
    parser.add_argument("--embedding-dim", type=int, default=128)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--queue-size", type=int, default=128)
    parser.add_argument("--sample-from", type=int, default=1000)
    parser.add_argument("--select", type=int, default=1)
    parser.add_argument("--covariance-ridge", type=float, default=1e-4)
    parser.add_argument("--outlier-loss-weight", type=float, default=0.1)
    parser.add_argument("--known-acceptance", type=float, default=0.95)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--sampling", choices=("natural", "weighted"), default="natural")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--no-amp", action="store_true")
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


@torch.no_grad()
def collect(
    model: VOSClassifier, loader: DataLoader, device: torch.device
) -> dict[str, np.ndarray]:
    model.eval()
    values: dict[str, list[np.ndarray]] = {
        "labels": [],
        "unknown": [],
        "logits": [],
        "embedding": [],
        "weighted_energy": [],
        "head_ood_probability": [],
    }
    for batch in loader:
        views, quality, labels = move_batch(batch, device)
        output = model(views, quality)
        head_probability = torch.softmax(
            model.discriminate_energy(output["weighted_energy"]), dim=1
        )[:, 0]
        values["labels"].append(labels.cpu().numpy())
        values["unknown"].append(batch["is_unknown"].numpy())
        values["head_ood_probability"].append(head_probability.cpu().numpy())
        for name in ("logits", "embedding", "weighted_energy"):
            values[name].append(output[name].cpu().numpy())
    return {name: np.concatenate(parts) for name, parts in values.items()}


def train(
    model: VOSClassifier,
    train_loader: DataLoader,
    validation_loader: DataLoader,
    class_count: int,
    device: torch.device,
    args: argparse.Namespace,
) -> tuple[list[dict[str, object]], ClassConditionalGaussianQueue]:
    queues = ClassConditionalGaussianQueue(class_count, args.queue_size)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay
    )
    amp = device.type == "cuda" and not args.no_amp
    scaler = torch.cuda.amp.GradScaler(enabled=amp)
    history: list[dict[str, object]] = []
    for epoch in range(args.epochs):
        model.train()
        totals = {"loss": 0.0, "classification": 0.0, "outlier": 0.0}
        batches = 0
        synthesis_batches = 0
        generated_count = 0
        for batch in train_loader:
            views, quality, labels = move_batch(batch, device)
            optimizer.zero_grad(set_to_none=True)
            with torch.cuda.amp.autocast(enabled=amp):
                output = model(views, quality)
                classification = torch.nn.functional.cross_entropy(
                    output["logits"], labels
                )
            queues.update(output["embedding"], labels)
            outlier_loss = torch.zeros((), device=device)
            if epoch + 1 >= args.start_epoch and queues.ready():
                synthetic = queues.synthesize(
                    sample_from=args.sample_from,
                    select=args.select,
                    ridge=args.covariance_ridge,
                ).detach()
                with torch.cuda.amp.autocast(enabled=amp):
                    synthetic_logits = model.classify_embedding(synthetic)
                    energies = torch.cat(
                        [output["weighted_energy"], model.energy(synthetic_logits)]
                    )
                    targets = torch.cat(
                        [
                            torch.ones(len(output["logits"]), device=device),
                            torch.zeros(len(synthetic_logits), device=device),
                        ]
                    ).long()
                    outlier_loss = torch.nn.functional.cross_entropy(
                        model.discriminate_energy(energies), targets
                    )
                synthesis_batches += 1
                generated_count += int(len(synthetic))
            loss = classification + args.outlier_loss_weight * outlier_loss
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            scaler.step(optimizer)
            scaler.update()
            totals["loss"] += float(loss.detach().cpu())
            totals["classification"] += float(classification.detach().cpu())
            totals["outlier"] += float(outlier_loss.detach().cpu())
            batches += 1

        validation = collect(model, validation_loader, device)
        validation_f1 = float(
            f1_score(
                validation["labels"],
                validation["logits"].argmax(axis=1),
                average="macro",
                zero_division=0,
            )
        )
        record = {
            "epoch": epoch + 1,
            "train_loss": totals["loss"] / max(1, batches),
            "classification_loss": totals["classification"] / max(1, batches),
            "outlier_loss": totals["outlier"] / max(1, synthesis_batches),
            "validation_macro_f1_diagnostic_only": validation_f1,
            "synthesis_batches": synthesis_batches,
            "generated_outliers": generated_count,
            "queue_counts": queues.counts(),
        }
        history.append(record)
        print(
            "vos_epoch=%d loss=%.6f validation_macro_f1=%.6f synthesis_batches=%d"
            % (epoch + 1, record["train_loss"], validation_f1, synthesis_batches),
            flush=True,
        )
    return history, queues


def open_set_report(
    labels: np.ndarray,
    unknown: np.ndarray,
    prediction: np.ndarray,
    validation_risk: np.ndarray,
    test_risk: np.ndarray,
    acceptance: float,
) -> tuple[float, dict[str, float]]:
    threshold = float(np.quantile(validation_risk, acceptance))
    return threshold, evaluate_hybrid_open_set(
        labels, unknown, prediction, test_risk, threshold
    )


def main() -> None:
    args = parse_arguments()
    if args.start_epoch < 1 or args.start_epoch > args.epochs:
        raise ValueError("VOS start epoch must be inside the training budget")
    if args.select > args.sample_from:
        raise ValueError("VOS select cannot exceed sample-from")
    set_seed(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    unknown_classes = [
        value.strip() for value in args.unknown_classes.split(",") if value.strip()
    ]
    if args.dataset == "synthetic":
        bundle = make_synthetic_open_set(seed=args.seed)
    else:
        if not args.csv or not args.config:
            raise ValueError("VOS tabular training requires --csv and --config")
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
    device = choose_device(args.device)
    options = {
        "batch_size": args.batch_size,
        "num_workers": args.num_workers,
        "pin_memory": device.type == "cuda",
    }
    sampler = (
        weighted_sampler(bundle.train.labels) if args.sampling == "weighted" else None
    )
    train_loader = DataLoader(
        bundle.train, sampler=sampler, shuffle=sampler is None, **options
    )
    fit_loader = DataLoader(bundle.train, shuffle=False, **options)
    validation_loader = DataLoader(bundle.validation, shuffle=False, **options)
    test_loader = DataLoader(bundle.test, shuffle=False, **options)
    model = VOSClassifier(
        bundle.input_dims,
        len(bundle.class_names),
        args.hidden_dim,
        args.embedding_dim,
        args.dropout,
    ).to(device)
    started = time.perf_counter()
    history, queues = train(
        model,
        train_loader,
        validation_loader,
        len(bundle.class_names),
        device,
        args,
    )
    training_seconds = time.perf_counter() - started
    train_values = collect(model, fit_loader, device)
    validation = collect(model, validation_loader, device)
    test = collect(model, test_loader, device)
    prediction = test["logits"].argmax(axis=1)
    unknown = test["unknown"].astype(bool)

    validation_energy = -np.logaddexp.reduce(validation["logits"], axis=1)
    test_energy = -np.logaddexp.reduce(test["logits"], axis=1)
    energy_threshold, energy_report = open_set_report(
        test["labels"],
        unknown,
        prediction,
        validation_energy,
        test_energy,
        args.known_acceptance,
    )
    head_threshold, head_report = open_set_report(
        test["labels"],
        unknown,
        prediction,
        validation["head_ood_probability"],
        test["head_ood_probability"],
        args.known_acceptance,
    )
    result = {
        "schema_version": "strict_v4_vos_metrics_v1",
        "model": "vos",
        "method": "vos_energy",
        "unknown_classes": unknown_classes,
        "seed": args.seed,
        "known_class_names": bundle.class_names,
        "sample_counts": bundle.sample_counts,
        "split_metadata": bundle.split_metadata,
        "split_sizes": {
            "train": len(bundle.train),
            "validation": len(bundle.validation),
            "test": len(bundle.test),
            "test_unknown": int(unknown.sum()),
        },
        "validation_thresholds": {
            "vos_energy": energy_threshold,
            "vos_energy_head": head_threshold,
        },
        "reports": {"vos_energy": energy_report},
        "auxiliary_reports": {"vos_energy_head": head_report},
        "training_history": history,
        "training_seconds": training_seconds,
        "trainable_parameters": count_trainable_parameters(model),
        "implementation": (
            "VOS per-class feature queues, class means, tied covariance, low-likelihood "
            "Gaussian virtual outliers, weighted-energy binary regularization, and plain "
            "energy evaluation adapted to shared tabular side-channel views"
        ),
        "vos_evidence": {
            "paper": "https://openreview.net/forum?id=TW7d65uYu5M",
            "official_code": "https://github.com/deeplearning-wisc/vos",
            "official_classification_trainer": (
                "https://github.com/deeplearning-wisc/vos/blob/main/"
                "classification/CIFAR/train_virtual.py"
            ),
            "fit_split": "known_only_train",
            "checkpoint_selection": "fixed_prefrozen_training_budget",
            "primary_score": "negative_plain_logsumexp_energy",
            "queue_counts_at_completion": queues.counts(),
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
        },
        "selection_evidence": {
            "protocol": "strict_known_only",
            "checkpoint_selection": {
                "split": "none",
                "criterion": "fixed_prefrozen_training_budget",
            },
            "deployment_thresholds": {
                "vos_energy": {
                    "split": "known_only_validation",
                    "known_acceptance_quantile": args.known_acceptance,
                    "value": energy_threshold,
                }
            },
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
            "test_labels_used_for_final_metrics_only": True,
        },
        "arguments": vars(args),
    }
    (output_dir / "metrics.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    np.savez_compressed(
        output_dir / "scores.npz",
        validation_labels=validation["labels"],
        validation_vos_energy=validation_energy,
        test_labels=test["labels"],
        test_unknown=unknown,
        test_vos_energy=test_energy,
        prediction_vos_energy=prediction,
        validation_vos_energy_head=validation["head_ood_probability"],
        test_vos_energy_head=test["head_ood_probability"],
    )
    torch.save(
        {
            "model_state": model.state_dict(),
            "arguments": vars(args),
            "class_names": bundle.class_names,
            "input_dims": bundle.input_dims,
        },
        output_dir / "model.pt",
    )
    print(json.dumps({"vos_energy": energy_report}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
