from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict

import numpy as np
import torch
from torch.utils.data import DataLoader

from caeos.data import prepare_tabular_open_set
from caeos.hybrid_open_set import evaluate_hybrid_open_set
from caeos.medaf_tabular import (
    MEDAFTabularClassifier,
    medaf_probabilities,
    medaf_risk,
    medaf_training_loss,
)
from caeos.metrics import expected_calibration_error
from caeos.multiclass import count_trainable_parameters
from train_multiclass import choose_device, move_batch, set_seed


OFFICIAL_COMMIT = "5d5328333af1f0857b9de20e94063ca8e6353d16"
ADMISSION_AUDIT = (
    "1a0ec766026dcbc86a6d1987c870076a3f31208460a1e56736982ea557aba2f6"
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Strict-v4 MEDAF-Tabular known-only adapter"
    )
    parser.add_argument("--csv", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--unknown-classes", required=True)
    parser.add_argument("--benign-class", default="Benign")
    parser.add_argument(
        "--split-strategy",
        choices=(
            "random",
            "fingerprint_grouped",
            "capture_grouped",
            "temporal_capture_grouped",
        ),
        default="fingerprint_grouped",
    )
    parser.add_argument("--max-per-class", type=int, default=1000)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--epochs", type=int, default=150)
    parser.add_argument("--milestone", type=int, default=130)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--embedding-dim", type=int, default=64)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--learning-rate", type=float, default=0.1)
    parser.add_argument("--momentum", type=float, default=0.9)
    parser.add_argument("--weight-decay", type=float, default=1e-5)
    parser.add_argument("--gate-temperature", type=float, default=100.0)
    parser.add_argument("--logit-temperature", type=float, default=100.0)
    parser.add_argument("--known-acceptance", type=float, default=0.95)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--seed", type=int, default=383)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--no-amp", action="store_true")
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def train_known_only(
    model: MEDAFTabularClassifier,
    train_loader: DataLoader,
    device: torch.device,
    *,
    epochs: int,
    milestone: int,
    learning_rate: float,
    momentum: float,
    weight_decay: float,
    amp: bool,
) -> list[Dict[str, float]]:
    """The training loop intentionally has no validation or test input."""

    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=learning_rate,
        momentum=momentum,
        weight_decay=weight_decay,
    )
    scheduler = torch.optim.lr_scheduler.MultiStepLR(
        optimizer, milestones=[milestone], gamma=0.1
    )
    scaler = torch.cuda.amp.GradScaler(enabled=amp)
    history: list[Dict[str, float]] = []
    for epoch in range(epochs):
        model.train()
        totals = {
            "total": 0.0,
            "expert_cross_entropy": 0.0,
            "gate_cross_entropy": 0.0,
            "attention_diversity": 0.0,
        }
        batches = 0
        for batch in train_loader:
            views, quality, labels = move_batch(batch, device)
            optimizer.zero_grad(set_to_none=True)
            with torch.cuda.amp.autocast(enabled=amp):
                output = model(views, quality, labels)
                losses = medaf_training_loss(output, labels)
            scaler.scale(losses["total"]).backward()
            scaler.step(optimizer)
            scaler.update()
            totals["total"] += float(losses["total"].detach().cpu())
            totals["expert_cross_entropy"] += float(
                losses["expert_cross_entropy"].sum().detach().cpu()
            )
            totals["gate_cross_entropy"] += float(
                losses["gate_cross_entropy"].detach().cpu()
            )
            totals["attention_diversity"] += float(
                losses["attention_diversity"].detach().cpu()
            )
            batches += 1
        record = {
            "epoch": float(epoch + 1),
            "learning_rate": float(optimizer.param_groups[0]["lr"]),
            **{
                name: value / max(1, batches)
                for name, value in totals.items()
            },
        }
        history.append(record)
        print(json.dumps(record, sort_keys=True), flush=True)
        scheduler.step()
    return history


@torch.no_grad()
def collect(
    model: MEDAFTabularClassifier,
    loader: DataLoader,
    device: torch.device,
    logit_temperature: float,
) -> Dict[str, np.ndarray]:
    model.eval()
    output: Dict[str, list[np.ndarray]] = {
        "labels": [],
        "unknown": [],
        "probability": [],
        "risk": [],
        "prediction": [],
        "gate_weights": [],
    }
    for batch in loader:
        views, quality, _ = move_batch(batch, device)
        values = model(views, quality)
        probability = medaf_probabilities(values, logit_temperature)
        output["labels"].append(batch["label"].numpy())
        output["unknown"].append(batch["is_unknown"].numpy())
        output["probability"].append(probability.cpu().numpy())
        output["risk"].append(
            medaf_risk(values, logit_temperature).cpu().numpy()
        )
        output["prediction"].append(
            probability.argmax(dim=-1).cpu().numpy()
        )
        output["gate_weights"].append(
            values["gate_weights"].cpu().numpy()
        )
    return {
        name: np.concatenate(parts, axis=0)
        for name, parts in output.items()
    }


def main() -> None:
    args = parse_arguments()
    if args.epochs != 150 or args.milestone != 130:
        raise ValueError(
            "formal MEDAF-Tabular adapter fixes epochs=150 and milestone=130"
        )
    set_seed(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    unknown_classes = [
        value.strip()
        for value in args.unknown_classes.split(",")
        if value.strip()
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
    loader_options = {
        "batch_size": args.batch_size,
        "num_workers": args.num_workers,
        "pin_memory": device.type == "cuda",
    }
    generator = torch.Generator().manual_seed(args.seed)
    train_loader = DataLoader(
        bundle.train,
        shuffle=True,
        generator=generator,
        **loader_options,
    )
    validation_loader = DataLoader(
        bundle.validation, shuffle=False, **loader_options
    )
    test_loader = DataLoader(bundle.test, shuffle=False, **loader_options)
    model = MEDAFTabularClassifier(
        bundle.input_dims,
        len(bundle.class_names),
        hidden_dim=args.hidden_dim,
        embedding_dim=args.embedding_dim,
        dropout=args.dropout,
        gate_temperature=args.gate_temperature,
    ).to(device)
    started = time.perf_counter()
    history = train_known_only(
        model,
        train_loader,
        device,
        epochs=args.epochs,
        milestone=args.milestone,
        learning_rate=args.learning_rate,
        momentum=args.momentum,
        weight_decay=args.weight_decay,
        amp=device.type == "cuda" and not args.no_amp,
    )
    training_seconds = time.perf_counter() - started
    validation = collect(
        model, validation_loader, device, args.logit_temperature
    )
    test = collect(model, test_loader, device, args.logit_temperature)
    threshold = float(
        np.quantile(validation["risk"], args.known_acceptance)
    )
    unknown = test["unknown"].astype(bool)
    report = evaluate_hybrid_open_set(
        test["labels"],
        unknown,
        test["prediction"],
        test["risk"],
        threshold,
    )
    known = ~unknown
    report["ece"] = expected_calibration_error(
        test["probability"][known], test["labels"][known]
    )
    result = {
        "schema_version": "strict_v4_medaf_tabular_adapter_result_v1",
        "model": "medaf_tabular_adapter",
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
            "medaf_tabular_adapter": threshold
        },
        "reports": {"medaf_tabular_adapter": report},
        "training_history": history,
        "training_seconds": training_seconds,
        "trainable_parameters": count_trainable_parameters(model),
        "source_reference": {
            "paper": (
                "Exploring Diverse Representations for Open Set Recognition"
            ),
            "venue": "AAAI 2024",
            "official_commit": OFFICIAL_COMMIT,
            "admission_audit_manifest_sha256": ADMISSION_AUDIT,
            "adapter_name": "MEDAF-Tabular adapter",
            "not_native_medaf_reproduction": True,
            "preserved_mechanisms": [
                "three expert branches",
                "class-conditional activation diversity",
                "independent adaptive gate",
                "detached expert logits for gate training",
                "gated MSP with temperatures fixed at 100",
                "official 0.7/1.0/0.01 loss weights",
            ],
        },
        "selection_evidence": {
            "training_split": "known_only_train",
            "checkpoint_selection": "fixed_final_epoch_150",
            "deployment_threshold": {
                "split": "known_only_validation",
                "known_acceptance_quantile": args.known_acceptance,
                "value": threshold,
            },
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
            "test_labels_used_for_final_metrics_only": True,
        },
        "arguments": vars(args),
    }
    (output_dir / "metrics.json").write_bytes(
        (json.dumps(result, indent=2, sort_keys=True) + "\n").encode(
            "utf-8"
        )
    )
    np.savez_compressed(
        output_dir / "scores.npz",
        validation_labels=validation["labels"],
        validation_medaf_tabular=validation["risk"],
        test_labels=test["labels"],
        test_unknown=unknown,
        test_medaf_tabular=test["risk"],
        prediction_medaf_tabular=test["prediction"],
        test_probability_medaf_tabular=test["probability"],
        validation_gate_weights=validation["gate_weights"],
        test_gate_weights=test["gate_weights"],
    )
    torch.save(
        {
            "state_dict": model.state_dict(),
            "class_names": bundle.class_names,
            "input_dims": bundle.input_dims,
            "source_commit": OFFICIAL_COMMIT,
        },
        output_dir / "model.pt",
    )
    print(json.dumps(result["reports"], sort_keys=True))


if __name__ == "__main__":
    main()
