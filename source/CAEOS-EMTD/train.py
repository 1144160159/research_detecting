from __future__ import annotations

import argparse
import json
import os
import random
from pathlib import Path
from typing import Dict

import numpy as np
import torch
from torch.utils.data import DataLoader, WeightedRandomSampler

from caeos.data import make_synthetic_open_set, prepare_tabular_open_set
from caeos.metrics import evaluate_open_set
from caeos.model import ConflictAwareEvidentialNet
from caeos.open_set import DiagnosticConformalCalibrator, OpenSetCalibrator
from caeos.training import collect_outputs, train_model


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Conflict-aware evidential open-set traffic detection"
    )
    parser.add_argument("--dataset", choices=("synthetic", "tabular"), default="synthetic")
    parser.add_argument("--csv", default=None)
    parser.add_argument("--config", default="configs/nf_unsw_nb15.json")
    parser.add_argument("--unknown-classes", nargs="+", default=["Backdoor"])
    parser.add_argument("--benign-class", default="Benign")
    parser.add_argument("--max-per-class", type=int, default=5000)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--embedding-dim", type=int, default=64)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--conflict-scale", type=float, default=2.0)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--annealing-epochs", type=int, default=8)
    parser.add_argument("--corruption-probability", type=float, default=0.20)
    parser.add_argument("--corruption-noise", type=float, default=1.0)
    parser.add_argument("--known-acceptance", type=float, default=0.95)
    parser.add_argument(
        "--calibrator", choices=("weighted", "conformal"), default="weighted"
    )
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--output-dir", default="runs/latest")
    parser.add_argument("--no-amp", action="store_true")
    return parser.parse_args()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def choose_device(name: str) -> torch.device:
    if name == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(name)


def make_weighted_sampler(labels: torch.Tensor) -> WeightedRandomSampler:
    counts = torch.bincount(labels)
    class_weight = 1.0 / counts.to(torch.float64).clamp_min(1.0)
    sample_weight = class_weight[labels]
    return WeightedRandomSampler(sample_weight, len(labels), replacement=True)


def json_dump(path: Path, value: Dict[str, object]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)


def main() -> None:
    args = parse_arguments()
    set_seed(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.dataset == "synthetic":
        bundle = make_synthetic_open_set(seed=args.seed)
    else:
        if not args.csv:
            raise ValueError("--csv is required for tabular data")
        with open(args.config, "r", encoding="utf-8") as handle:
            data_config = json.load(handle)
        bundle = prepare_tabular_open_set(
            args.csv,
            data_config,
            args.unknown_classes,
            args.benign_class,
            args.max_per_class,
            args.chunksize,
            args.seed,
        )

    print("class_names=" + json.dumps(bundle.class_names, ensure_ascii=False))
    print("sample_counts=" + json.dumps(bundle.sample_counts, ensure_ascii=False))
    print("split_sizes=train:%d validation:%d test:%d" % (
        len(bundle.train), len(bundle.validation), len(bundle.test)
    ))

    train_loader = DataLoader(
        bundle.train,
        batch_size=args.batch_size,
        sampler=make_weighted_sampler(bundle.train.labels),
        num_workers=args.num_workers,
        pin_memory=torch.cuda.is_available(),
    )
    train_calibration_loader = DataLoader(
        bundle.train,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=torch.cuda.is_available(),
    )
    validation_loader = DataLoader(
        bundle.validation,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=torch.cuda.is_available(),
    )
    test_loader = DataLoader(
        bundle.test,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=torch.cuda.is_available(),
    )

    device = choose_device(args.device)
    print("device=%s torch=%s" % (device, torch.__version__))
    model = ConflictAwareEvidentialNet(
        bundle.input_dims,
        len(bundle.class_names),
        args.hidden_dim,
        args.embedding_dim,
        args.dropout,
        args.conflict_scale,
    ).to(device)

    history = train_model(
        model,
        train_loader,
        validation_loader,
        device,
        bundle.benign_index,
        args.epochs,
        args.learning_rate,
        args.weight_decay,
        args.annealing_epochs,
        args.corruption_probability,
        args.corruption_noise,
        not args.no_amp,
    )

    train_output, train_labels, _ = collect_outputs(
        model, train_calibration_loader, device
    )
    validation_output, _, _ = collect_outputs(model, validation_loader, device)
    if args.calibrator == "conformal":
        calibrator = DiagnosticConformalCalibrator(
            len(bundle.class_names),
            bundle.benign_index,
            known_acceptance=args.known_acceptance,
        )
    else:
        calibrator = OpenSetCalibrator(
            len(bundle.class_names),
            bundle.benign_index,
            known_acceptance=args.known_acceptance,
        )
    calibrator.fit_prototypes(train_output["fused_embedding"], train_labels)
    if args.calibrator == "conformal":
        calibrator.fit_reference(train_output, train_labels)
    calibrator.fit_known_validation(validation_output)

    test_output, test_labels, test_unknown = collect_outputs(model, test_loader, device)
    report = evaluate_open_set(test_output, test_labels, test_unknown, calibrator)
    report["calibrator"] = args.calibrator
    print("metrics=" + json.dumps(report, ensure_ascii=False, sort_keys=True))

    checkpoint = {
        "model_state": model.state_dict(),
        "input_dims": bundle.input_dims,
        "class_names": bundle.class_names,
        "modality_names": bundle.modality_names,
        "benign_index": bundle.benign_index,
        "arguments": vars(args),
    }
    torch.save(checkpoint, str(output_dir / "model.pt"))
    json_dump(output_dir / "calibrator.json", calibrator.state_dict())
    json_dump(output_dir / "metrics.json", report)
    json_dump(output_dir / "history.json", {"epochs": history})
    json_dump(
        output_dir / "data_metadata.json",
        {
            "class_names": bundle.class_names,
            "modality_names": bundle.modality_names,
            "input_dims": bundle.input_dims,
            "sample_counts": bundle.sample_counts,
            "preprocessing": bundle.preprocessing,
        },
    )


if __name__ == "__main__":
    main()
