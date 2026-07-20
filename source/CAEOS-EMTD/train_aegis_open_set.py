from __future__ import annotations

import argparse
import copy
import json
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import f1_score
from torch.utils.data import DataLoader, Dataset

from caeos.aegis import (
    AEGISClassifier,
    AEGISKNN,
    produce_pseudo_labels,
    supervised_contrastive_loss,
)
from caeos.data import prepare_tabular_open_set
from caeos.hybrid_open_set import evaluate_hybrid_open_set
from caeos.multiclass import count_trainable_parameters
from train_multiclass import choose_device, set_seed


class IndexedDataset(Dataset):
    def __init__(self, base: Dataset) -> None:
        self.base = base

    def __len__(self) -> int:
        return len(self.base)

    def __getitem__(self, index: int) -> dict[str, object]:
        item = dict(self.base[index])
        item["sample_index"] = index
        return item


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AEGIS-Net strict-v4 clean-label adapter")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--unknown-classes", required=True)
    parser.add_argument("--benign-class", default="Benign")
    parser.add_argument(
        "--split-strategy",
        choices=("random", "fingerprint_grouped", "capture_grouped"),
        default="fingerprint_grouped",
    )
    parser.add_argument("--max-per-class", type=int, default=1000)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--correction-start-epoch", type=int, default=20)
    parser.add_argument("--patience", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--momentum", type=float, default=0.9)
    parser.add_argument("--pseudo-weight", type=float, default=0.1)
    parser.add_argument("--contrast-weight", type=float, default=0.5)
    parser.add_argument("--temperature", type=float, default=0.07)
    parser.add_argument("--prototypes-per-class", type=int, default=14)
    parser.add_argument("--prototype-max-samples", type=int, default=1280)
    parser.add_argument("--neighbors", type=int, default=50)
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
    model: AEGISClassifier, loader: DataLoader, device: torch.device
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
        result = model.forward_values(concatenate_batch(batch, device))
        output["labels"].append(batch["label"].numpy())
        output["unknown"].append(batch["is_unknown"].numpy())
        for name in ("logits", "embedding", "detection_embedding"):
            output[name].append(result[name].cpu().numpy())
    return {name: np.concatenate(parts, axis=0) for name, parts in output.items()}


def main() -> None:
    args = parse_arguments()
    set_seed(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
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
    train_dataset = IndexedDataset(bundle.train)
    train_loader = DataLoader(train_dataset, shuffle=False, **options)
    shuffled_loader = DataLoader(train_dataset, shuffle=True, **options)
    validation_loader = DataLoader(bundle.validation, shuffle=False, **options)
    test_loader = DataLoader(bundle.test, shuffle=False, **options)

    model = AEGISClassifier(bundle.input_dims, len(bundle.class_names)).to(device)
    optimizer = torch.optim.SGD(
        model.parameters(), lr=args.learning_rate, momentum=args.momentum
    )
    amp = device.type == "cuda" and not args.no_amp
    scaler = torch.cuda.amp.GradScaler(enabled=amp)
    original_labels = bundle.train.labels.numpy().astype(np.int64)
    pseudo_labels = original_labels.copy()
    best_score = -1.0
    best_state = None
    stale = 0
    history = []
    started = time.perf_counter()
    for epoch in range(args.epochs):
        if epoch >= args.correction_start_epoch:
            train_values = collect(model, train_loader, device)
            pseudo_labels = produce_pseudo_labels(
                train_values["embedding"],
                original_labels,
                len(bundle.class_names),
                args.prototypes_per_class,
                args.prototype_max_samples,
                args.seed + epoch,
            )
        model.train()
        loss_total = 0.0
        batches = 0
        for batch in shuffled_loader:
            values = concatenate_batch(batch, device)
            labels = batch["label"].to(device)
            indices = batch["sample_index"].numpy()
            corrected = torch.as_tensor(pseudo_labels[indices], device=device)
            optimizer.zero_grad(set_to_none=True)
            with torch.cuda.amp.autocast(enabled=amp):
                result = model.forward_values(values)
                classification = F.cross_entropy(result["logits"], labels)
                contrastive = supervised_contrastive_loss(
                    result["embedding"], labels, args.temperature
                )
                if epoch >= args.correction_start_epoch:
                    pseudo = F.cross_entropy(result["logits"], corrected)
                    loss = (
                        (1.0 - args.pseudo_weight) * classification
                        + args.pseudo_weight * pseudo
                        + args.contrast_weight * contrastive
                    )
                else:
                    pseudo = classification.detach() * 0.0
                    loss = classification + args.contrast_weight * contrastive
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            scaler.step(optimizer)
            scaler.update()
            loss_total += float(loss.detach().cpu())
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
            "loss": loss_total / max(1, batches),
            "validation_macro_f1": validation_f1,
            "pseudo_label_change_rate": float((pseudo_labels != original_labels).mean()),
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

    train_values = collect(model, train_loader, device)
    validation = collect(model, validation_loader, device)
    test = collect(model, test_loader, device)
    detector = AEGISKNN(args.neighbors).fit(train_values["detection_embedding"])
    validation_risk = detector.score(validation["detection_embedding"])
    test_risk = detector.score(test["detection_embedding"])
    threshold = float(np.quantile(validation_risk, args.known_acceptance))
    prediction = test["logits"].argmax(axis=1)
    unknown = test["unknown"].astype(bool)
    report = evaluate_hybrid_open_set(
        test["labels"], unknown, prediction, test_risk, threshold
    )
    result = {
        "model": "aegis_clean_adapter",
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
        "validation_thresholds": {"aegis_clean_adapter": threshold},
        "reports": {"aegis_clean_adapter": report},
        "auxiliary_reports": {},
        "training_history": history,
        "training_seconds": training_seconds,
        "trainable_parameters": count_trainable_parameters(model),
        "implementation": (
            "AEGIS-Net DeepResNet, supervised contrastive objective, density-prototype "
            "label correction, and k=50 normalized-feature neighbor detector adapted "
            "to the shared clean-label strict-v4 split"
        ),
        "source_reference": {
            "official_repository": "https://github.com/GoatWu/AEGIS-Net",
            "adapter_repairs": [
                "preserve the Conv1d channel dimension removed by the released predict method",
                "select checkpoints on known validation instead of training true-label accuracy",
                "calibrate rejection on known validation instead of cross-dataset OOD labels",
            ],
            "task_boundary": (
                "clean-label strict-v4 adapter does not claim the original noisy-label protocol"
            ),
        },
        "selection_evidence": {
            "protocol": "strict_known_only",
            "checkpoint_selection": {
                "split": "known_only_validation",
                "criterion": "macro_f1",
            },
            "postprocessors": {
                "aegis_knn": {
                    "fit_split": "known_only_train",
                    "neighbors": detector.fitted_neighbors,
                }
            },
            "deployment_thresholds": {
                "aegis_clean_adapter": {
                    "split": "known_only_validation",
                    "known_acceptance_quantile": args.known_acceptance,
                    "value": threshold,
                }
            },
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
            "test_labels_used_for_final_metrics_only": True,
        },
        "arguments": vars(args),
    }
    (output_dir / "metrics.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    np.savez_compressed(
        output_dir / "scores.npz",
        validation_labels=validation["labels"],
        validation_aegis=validation_risk,
        test_labels=test["labels"],
        test_unknown=unknown,
        test_aegis=test_risk,
        prediction_aegis=prediction,
    )
    torch.save(
        {
            "state_dict": model.state_dict(),
            "class_names": bundle.class_names,
            "input_dims": bundle.input_dims,
        },
        output_dir / "model.pt",
    )
    print("metrics=" + json.dumps({"aegis_clean_adapter": report}, sort_keys=True))


if __name__ == "__main__":
    main()
