from __future__ import annotations

import argparse
import copy
import json
import time
from itertools import cycle
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import f1_score
from torch.utils.data import DataLoader, Dataset, Subset, WeightedRandomSampler

from caeos.data import prepare_tabular_open_set
from caeos.hybrid_open_set import evaluate_hybrid_open_set
from caeos.multiclass import count_trainable_parameters
from caeos.sieve import (
    SieveClassifier,
    SieveMahalanobis,
    SieveSelection,
    select_sieve_samples,
    sieve_contrastive_loss,
    swap_adjacent_features,
)
from train_multiclass import choose_device, set_seed


class LabelOverrideDataset(Dataset):
    def __init__(self, base: Dataset, labels: torch.Tensor):
        self.base = base
        self.labels = labels.to(torch.long).cpu()

    def __len__(self) -> int:
        return len(self.base)

    def __getitem__(self, index: int) -> dict[str, object]:
        item = dict(self.base[index])
        item["label"] = self.labels[index]
        return item


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sieve adapted to the shared leakage-controlled open-set split"
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
    parser.add_argument("--max-per-class", type=int, default=300)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--patience", type=int, default=15)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=5e-4)
    parser.add_argument("--momentum", type=float, default=0.9)
    parser.add_argument("--temperature", type=float, default=0.07)
    parser.add_argument("--contrast-weight", type=float, default=1.0)
    parser.add_argument("--neighbors", type=int, default=100)
    parser.add_argument("--xi", type=float, default=1.0)
    parser.add_argument("--zeta", type=float, default=0.93)
    parser.add_argument("--swap-ratio", type=float, default=0.05)
    parser.add_argument("--known-acceptance", type=float, default=0.95)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--no-amp", action="store_true")
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def concatenate_batch(batch: dict[str, object], device: torch.device) -> torch.Tensor:
    return torch.cat(tuple(view.to(device) for view in batch["views"]), dim=1)


@torch.no_grad()
def collect(
    model: SieveClassifier, loader: DataLoader, device: torch.device
) -> dict[str, np.ndarray]:
    model.eval()
    output: dict[str, list[np.ndarray]] = {
        "labels": [],
        "unknown": [],
        "logits": [],
        "embedding": [],
        "detection_embedding": [],
    }
    for batch in loader:
        values = concatenate_batch(batch, device)
        result = model.forward_values(values)
        output["labels"].append(batch["label"].numpy())
        output["unknown"].append(batch["is_unknown"].numpy())
        for name in ("logits", "embedding", "detection_embedding"):
            output[name].append(result[name].cpu().numpy())
    return {name: np.concatenate(parts, axis=0) for name, parts in output.items()}


def selection_from_values(
    values: dict[str, np.ndarray], args: argparse.Namespace, num_classes: int, device
) -> SieveSelection:
    return select_sieve_samples(
        torch.as_tensor(values["embedding"], device=device),
        torch.as_tensor(values["logits"], device=device),
        torch.as_tensor(values["labels"], device=device, dtype=torch.long),
        num_classes,
        args.neighbors,
        args.xi,
        args.zeta,
    )


def selected_loader(
    dataset: Dataset,
    selection: SieveSelection,
    args: argparse.Namespace,
    device: torch.device,
) -> DataLoader:
    indices = selection.selected_indices.detach().cpu()
    if len(indices) < 2:
        indices = torch.arange(len(dataset))
    overridden = LabelOverrideDataset(dataset, selection.modified_labels)
    subset = Subset(overridden, indices.tolist())
    labels = selection.modified_labels.detach().cpu()[indices]
    counts = torch.bincount(labels).to(torch.float64).clamp_min(1.0)
    weights = (1.0 / counts)[labels]
    sampler = WeightedRandomSampler(weights, len(subset), replacement=True)
    return DataLoader(
        subset,
        batch_size=min(args.batch_size, len(subset)),
        sampler=sampler,
        num_workers=args.num_workers,
        pin_memory=device.type == "cuda",
        drop_last=len(subset) > args.batch_size,
    )


def train_epoch(
    model: SieveClassifier,
    supervised_loader: DataLoader,
    all_loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    scaler: torch.cuda.amp.GradScaler,
    device: torch.device,
    args: argparse.Namespace,
) -> dict[str, float]:
    model.train()
    supervised_batches = cycle(supervised_loader)
    ce_total = 0.0
    contrast_total = 0.0
    batches = 0
    amp = device.type == "cuda" and not args.no_amp
    for all_batch in all_loader:
        labeled_batch = next(supervised_batches)
        all_values = concatenate_batch(all_batch, device)
        labeled_values = concatenate_batch(labeled_batch, device)
        labels = labeled_batch["label"].to(device)

        labeled_first = swap_adjacent_features(labeled_values, args.swap_ratio)
        labeled_second = swap_adjacent_features(labeled_values, args.swap_ratio)
        target = F.one_hot(labels, model.classifier.out_features).to(torch.float32)
        inputs = torch.cat([labeled_first, labeled_second], dim=0)
        targets = torch.cat([target, target], dim=0)
        mix = max(np.random.beta(4, 4), 0.5)
        order = torch.randperm(len(inputs), device=device)
        mixed_inputs = mix * inputs + (1.0 - mix) * inputs[order]
        mixed_targets = mix * targets + (1.0 - mix) * targets[order]

        contrast_first = all_values
        contrast_second = swap_adjacent_features(all_values, args.swap_ratio)
        optimizer.zero_grad(set_to_none=True)
        with torch.cuda.amp.autocast(enabled=amp):
            joined = torch.cat(
                [mixed_inputs, contrast_first, contrast_second], dim=0
            )
            embedding, _ = model.encode_values(joined)
            mixed_embedding, first_embedding, second_embedding = torch.split(
                embedding,
                [len(mixed_inputs), len(contrast_first), len(contrast_second)],
                dim=0,
            )
            logits = model.classifier(mixed_embedding)
            cross_entropy = -torch.mean(
                torch.sum(F.log_softmax(logits, dim=1) * mixed_targets, dim=1)
            )
            projected = model.projection(
                torch.cat([first_embedding, second_embedding], dim=0)
            )
            first_projected, second_projected = torch.chunk(projected, 2, dim=0)
            contrastive = sieve_contrastive_loss(
                first_projected, second_projected, args.temperature
            )
            loss = cross_entropy + args.contrast_weight * contrastive
        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
        scaler.step(optimizer)
        scaler.update()
        ce_total += float(cross_entropy.detach().cpu())
        contrast_total += float(contrastive.detach().cpu())
        batches += 1
    return {
        "cross_entropy": ce_total / max(1, batches),
        "contrastive": contrast_total / max(1, batches),
    }


def main() -> None:
    args = parse_arguments()
    set_seed(args.seed)
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
    device = choose_device(args.device)
    options = {
        "batch_size": args.batch_size,
        "num_workers": args.num_workers,
        "pin_memory": device.type == "cuda",
    }
    fit_loader = DataLoader(bundle.train, shuffle=False, **options)
    validation_loader = DataLoader(bundle.validation, shuffle=False, **options)
    test_loader = DataLoader(bundle.test, shuffle=False, **options)
    all_loader = DataLoader(
        bundle.train,
        shuffle=True,
        drop_last=len(bundle.train) > args.batch_size,
        **options,
    )

    model = SieveClassifier(bundle.input_dims, len(bundle.class_names)).to(device)
    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=args.learning_rate,
        momentum=args.momentum,
        weight_decay=args.weight_decay,
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=args.epochs, eta_min=args.learning_rate / 50.0
    )
    amp = device.type == "cuda" and not args.no_amp
    scaler = torch.cuda.amp.GradScaler(enabled=amp)
    best_score = -1.0
    best_state = None
    stale = 0
    history = []
    started = time.perf_counter()
    for epoch in range(args.epochs):
        train_values = collect(model, fit_loader, device)
        selection = selection_from_values(
            train_values, args, len(bundle.class_names), device
        )
        supervised_loader = selected_loader(bundle.train, selection, args, device)
        losses = train_epoch(
            model,
            supervised_loader,
            all_loader,
            optimizer,
            scaler,
            device,
            args,
        )
        scheduler.step()
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
            **losses,
            "validation_macro_f1": validation_f1,
            "selected": int(selection.selected_indices.numel()),
            "clean": int(selection.clean_indices.numel()),
            "expanded": int(selection.expanded_indices.numel()),
            "mean_confidence": selection.mean_confidence,
        }
        history.append(record)
        print(json.dumps(record, sort_keys=True), flush=True)
        if validation_f1 > best_score + 1e-6:
            best_score = validation_f1
            best_state = copy.deepcopy(model.state_dict())
            stale = 0
        else:
            stale += 1
            if stale >= args.patience:
                break
    training_seconds = time.perf_counter() - started
    if best_state is not None:
        model.load_state_dict(best_state)

    train_values = collect(model, fit_loader, device)
    selection = selection_from_values(
        train_values, args, len(bundle.class_names), device
    )
    selected = selection.selected_indices.detach().cpu().numpy()
    modified_labels = selection.modified_labels.detach().cpu().numpy()[selected]
    selected_counts = {
        bundle.class_names[index]: int((modified_labels == index).sum())
        for index in range(len(bundle.class_names))
    }
    detector = SieveMahalanobis()
    detector.fit(train_values["detection_embedding"][selected], modified_labels)
    validation = collect(model, validation_loader, device)
    test = collect(model, test_loader, device)
    validation_risk = detector.score(validation["detection_embedding"])
    test_risk = detector.score(test["detection_embedding"])
    training_risk = detector.score(train_values["detection_embedding"][selected])
    threshold = float(np.quantile(validation_risk, args.known_acceptance))
    training_threshold = float(np.quantile(training_risk, args.known_acceptance))
    prediction = test["logits"].argmax(axis=1)
    unknown = test["unknown"].astype(bool)
    report = evaluate_hybrid_open_set(
        test["labels"], unknown, prediction, test_risk, threshold
    )
    training_threshold_report = evaluate_hybrid_open_set(
        test["labels"], unknown, prediction, test_risk, training_threshold
    )

    result = {
        "model": "sieve",
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
        "validation_thresholds": {"sieve": threshold},
        "reports": {"sieve": report},
        "auxiliary_reports": {
            "sieve_training_95pct_threshold": training_threshold_report
        },
        "final_selection": {
            "selected": int(len(selected)),
            "clean": int(selection.clean_indices.numel()),
            "expanded": int(selection.expanded_indices.numel()),
            "class_counts": selected_counts,
        },
        "training_history": history,
        "training_seconds": training_seconds,
        "trainable_parameters": count_trainable_parameters(model),
        "implementation": (
            "Official Sieve DeepResNet, neighbor-consistency screening, "
            "confidence expansion, mixup, batch contrastive objective, and "
            "class-conditional Mahalanobis detector adapted to the shared "
            "CAEOS split; preprocessing and checkpoint selection use training "
            "statistics and known validation only"
        ),
        "protocol": "clean-label complete unknown-class holdout; not Sieve's mixed-noise original protocol",
        "source_reference": {
            "paper_doi": "10.1109/TDSC.2026.3697849",
            "official_repository": "https://github.com/niebikong/Sieve",
            "official_repository_head_verified_2026_07_15": "d071e7abe362c23364ca6206197e0d9224df491f",
            "adapter_repairs": [
                "replace author-machine absolute paths with command-line paths",
                "select checkpoints on known validation instead of the test set",
                "fit preprocessing on training data only",
                "provide the two contrastive views expected by the training loop",
            ],
        },
        "arguments": vars(args),
    }
    with (output_dir / "metrics.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    np.savez_compressed(
        output_dir / "scores.npz",
        validation_labels=validation["labels"],
        validation_sieve=validation_risk,
        test_labels=test["labels"],
        test_unknown=unknown,
        test_sieve=test_risk,
        prediction_sieve=prediction,
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
    print("metrics=" + json.dumps({"sieve": report}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
