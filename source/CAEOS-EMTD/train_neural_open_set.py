from __future__ import annotations

import argparse
import copy
import json
import time
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import f1_score
from torch.utils.data import DataLoader

from caeos.data import make_synthetic_open_set, prepare_tabular_open_set
from caeos.cade import CADECalibrator, CADEClassifier
from caeos.closr import CLOSRClassifier, closr_risk, warmup_cosine_learning_rate
from caeos.hybrid_open_set import KnownKnnDistance, evaluate_hybrid_open_set
from caeos.multiclass import (
    ConcatMLPClassifier,
    count_trainable_parameters,
    supervised_contrastive_loss,
)
from caeos.neural_open_set import (
    ARPLClassifier,
    HCRPOSDClassifier,
    CEACalibrator,
    NCICalibrator,
    OpenMaxCalibrator,
    RelativeMahalanobis,
    SharedCovarianceMahalanobis,
    ViMCalibrator,
    arpl_risk,
    energy_risk,
    max_logit_risk,
    msp_risk,
)
from caeos.open_detect import OpenDetectClassifier, open_detect_risk
from caeos.palm import PALMClassifier, PALMSSDMahalanobis
from caeos.ronetc import RoNeTCClassifier, ronetc_risk
from caeos.scale import SCALECalibrator
from caeos.tao_stage1 import PCAResidualScorer, hybrid_scores, mlp_blood_score
from train_multiclass import choose_device, move_batch, set_seed, weighted_sampler


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Same-split neural open-set baselines")
    parser.add_argument("--dataset", choices=("synthetic", "tabular"), default="tabular")
    parser.add_argument("--csv")
    parser.add_argument("--config", default="configs/hikari2021.json")
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
        default="random",
    )
    parser.add_argument("--max-per-class", type=int, default=500)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument(
        "--model",
        choices=(
            "mlp", "supcon", "arpl", "hcrp_osd", "closr", "cade", "opendetect",
            "ronetc", "nci", "energy_cea", "nci_cea",
            "palm",
        ),
        default="mlp",
    )
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--patience", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--embedding-dim", type=int, default=64)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--radius-weight", type=float, default=0.1)
    parser.add_argument("--contrast-weight", type=float, default=0.2)
    parser.add_argument("--contrast-temperature", type=float, default=0.1)
    parser.add_argument("--closr-depth", type=int, default=3)
    parser.add_argument("--closr-margin", type=float, default=1.0)
    parser.add_argument("--closr-alpha", type=float, default=0.5)
    parser.add_argument("--cade-hidden", default="64,32,16")
    parser.add_argument("--cade-contrast-weight", type=float, default=0.1)
    parser.add_argument("--cade-margin", type=float, default=10.0)
    parser.add_argument("--cade-similar-ratio", type=float, default=0.25)
    parser.add_argument("--cade-classifier-hidden", type=int, default=30)
    parser.add_argument("--cade-classifier-dropout", type=float, default=0.2)
    parser.add_argument("--cade-classifier-epochs", type=int, default=30)
    parser.add_argument("--cade-classifier-batch-size", type=int, default=256)
    parser.add_argument("--cade-classifier-lr", type=float, default=1e-3)
    parser.add_argument("--cade-mad-threshold", type=float, default=3.5)
    parser.add_argument("--open-detect-generative-weight", type=float, default=0.005)
    parser.add_argument("--open-detect-reset-epochs", default="50,80")
    parser.add_argument("--ronetc-annealing-epochs", type=int, default=10)
    parser.add_argument("--knn-neighbors", type=int, default=10)
    parser.add_argument("--openmax-tail-size", type=int, default=20)
    parser.add_argument("--openmax-alpha", type=int, default=10)
    parser.add_argument("--nci-alpha", type=float, default=0.0001)
    parser.add_argument("--cea-percentile", type=float, default=99.9)
    parser.add_argument("--cea-addition-coefficient", type=float, default=10.0)
    parser.add_argument("--cea-threshold-caution-coefficient", type=float, default=1.1)
    parser.add_argument("--scale-percentile", type=float, default=85.0)
    parser.add_argument("--scale-temperature", type=float, default=1.0)
    parser.add_argument("--palm-training-views", type=int, default=2)
    parser.add_argument("--palm-prototypes-per-class", type=int, default=6)
    parser.add_argument("--palm-assignment-top-k", type=int, default=5)
    parser.add_argument("--palm-prototype-momentum", type=float, default=0.999)
    parser.add_argument("--palm-temperature", type=float, default=0.1)
    parser.add_argument("--palm-assignment-epsilon", type=float, default=0.05)
    parser.add_argument("--palm-sinkhorn-iterations", type=int, default=3)
    parser.add_argument("--palm-prototype-contrast-weight", type=float, default=1.0)
    parser.add_argument("--palm-learning-rate", type=float, default=0.1)
    parser.add_argument("--palm-momentum", type=float, default=0.9)
    parser.add_argument("--palm-ssd-corrected-centering", action="store_true")
    parser.add_argument("--tao-stage1-adapter", action="store_true")
    parser.add_argument("--tao-blood-estimators", type=int, default=50)
    parser.add_argument("--tao-pca-variance-ratio", type=float, default=0.95)
    parser.add_argument("--tao-alpha", type=float, default=0.6)
    parser.add_argument("--known-acceptance", type=float, default=0.95)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--sampling", choices=("weighted", "natural"), default="weighted")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--no-amp", action="store_true")
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


@torch.no_grad()
def collect(model, loader, device) -> dict[str, np.ndarray]:
    model.eval()
    output = {"labels": [], "unknown": [], "logits": [], "embedding": []}
    for batch in loader:
        views, quality, labels = move_batch(batch, device)
        result = model(views, quality)
        output["labels"].append(labels.cpu().numpy())
        output["unknown"].append(batch["is_unknown"].numpy())
        output["logits"].append(result["logits"].cpu().numpy())
        output["embedding"].append(result["embedding"].cpu().numpy())
        for name in ("joint_uncertainty", "view_uncertainty", "sequential_conflict"):
            if name in result:
                output.setdefault(name, []).append(result[name].cpu().numpy())
    return {name: np.concatenate(parts, axis=0) for name, parts in output.items()}


def validation_f1(model, loader, device) -> float:
    values = collect(model, loader, device)
    return float(f1_score(values["labels"], values["logits"].argmax(axis=1), average="macro", zero_division=0))


def collect_mlp_blood(model, loader, device, estimators: int, seed: int) -> np.ndarray:
    scores = []
    for batch_index, batch in enumerate(loader):
        views, _, _ = move_batch(batch, device)
        scores.append(
            mlp_blood_score(
                model,
                views,
                estimators=estimators,
                seed=seed + batch_index,
            )
        )
    return np.concatenate(scores)


def train_cade(model, train_loader, validation_loader, device, args) -> list[dict[str, object]]:
    """Train CADE's autoencoder and target classifier as independent stages."""
    amp = device.type == "cuda" and not args.no_amp
    history: list[dict[str, object]] = []
    optimizer = torch.optim.Adam(
        model.autoencoder_parameters(), lr=args.learning_rate
    )
    scaler = torch.cuda.amp.GradScaler(enabled=amp)
    for epoch in range(args.epochs):
        model.train()
        total = 0.0
        batches = 0
        for batch in train_loader:
            views, quality, labels = move_batch(batch, device)
            optimizer.zero_grad(set_to_none=True)
            with torch.cuda.amp.autocast(enabled=amp):
                output = model(views, quality)
                loss = model.autoencoder_loss(output, labels)
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(
                list(model.autoencoder_parameters()), 5.0
            )
            scaler.step(optimizer)
            scaler.update()
            total += float(loss.detach().cpu())
            batches += 1
        record = {
            "phase": "contrastive_autoencoder",
            "epoch": epoch + 1,
            "train_loss": total / max(1, batches),
            "validation_macro_f1": None,
        }
        history.append(record)
        print(
            "cade_ae_epoch=%d loss=%.6f"
            % (epoch + 1, record["train_loss"]),
            flush=True,
        )

    classifier_sampler = (
        weighted_sampler(train_loader.dataset.labels)
        if args.sampling == "weighted"
        else None
    )
    classifier_loader = DataLoader(
        train_loader.dataset,
        batch_size=args.cade_classifier_batch_size,
        sampler=classifier_sampler,
        shuffle=classifier_sampler is None,
        num_workers=train_loader.num_workers,
        pin_memory=train_loader.pin_memory,
    )
    classifier_optimizer = torch.optim.Adam(
        model.classifier.parameters(), lr=args.cade_classifier_lr
    )
    classifier_scaler = torch.cuda.amp.GradScaler(enabled=amp)
    best_score = -1.0
    best_state = None
    for epoch in range(args.cade_classifier_epochs):
        model.train()
        total = 0.0
        batches = 0
        for batch in classifier_loader:
            views, quality, labels = move_batch(batch, device)
            classifier_optimizer.zero_grad(set_to_none=True)
            with torch.cuda.amp.autocast(enabled=amp):
                output = model(views, quality)
                loss = torch.nn.functional.cross_entropy(output["logits"], labels)
            classifier_scaler.scale(loss).backward()
            classifier_scaler.unscale_(classifier_optimizer)
            torch.nn.utils.clip_grad_norm_(model.classifier.parameters(), 5.0)
            classifier_scaler.step(classifier_optimizer)
            classifier_scaler.update()
            total += float(loss.detach().cpu())
            batches += 1
        score = validation_f1(model, validation_loader, device)
        record = {
            "phase": "target_classifier",
            "epoch": epoch + 1,
            "train_loss": total / max(1, batches),
            "validation_macro_f1": score,
        }
        history.append(record)
        print(
            "cade_classifier_epoch=%d loss=%.6f validation_macro_f1=%.6f"
            % (epoch + 1, record["train_loss"], score),
            flush=True,
        )
        if score > best_score + 1e-6:
            best_score = score
            best_state = copy.deepcopy(model.classifier.state_dict())
    if best_state is not None:
        model.classifier.load_state_dict(best_state)
    return history


def train_open_detect(model, train_loader, validation_loader, device, args) -> list[dict[str, object]]:
    """Train the official Open-Detect objective under the shared tabular input."""
    amp = device.type == "cuda" and not args.no_amp
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate, betas=(0.9, 0.999))
    scheduler = torch.optim.lr_scheduler.MultiStepLR(
        optimizer, milestones=[50, 80], gamma=0.1
    )
    scaler = torch.cuda.amp.GradScaler(enabled=amp)
    reset_epochs = {
        int(value.strip())
        for value in args.open_detect_reset_epochs.split(",")
        if value.strip()
    }
    best_score = -1.0
    best_state = None
    history: list[dict[str, object]] = []
    for epoch in range(args.epochs):
        model.train()
        total = 0.0
        batches = 0
        for batch in train_loader:
            views, quality, labels = move_batch(batch, device)
            optimizer.zero_grad(set_to_none=True)
            with torch.cuda.amp.autocast(enabled=amp):
                output = model(views, quality)
                loss = model.loss(output, labels)
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            scaler.step(optimizer)
            scaler.update()
            total += float(loss.detach().cpu())
            batches += 1

        reset = epoch + 1 in reset_epochs
        if reset:
            fit_values = collect(model, train_loader, device)
            model.reset_prototypes(fit_values["embedding"], fit_values["labels"])
        score = validation_f1(model, validation_loader, device)
        record = {
            "epoch": epoch + 1,
            "train_loss": total / max(1, batches),
            "validation_macro_f1": score,
            "prototype_reset": reset,
        }
        history.append(record)
        print(
            "opendetect_epoch=%d loss=%.6f validation_macro_f1=%.6f prototype_reset=%s"
            % (epoch + 1, record["train_loss"], score, reset),
            flush=True,
        )
        if score > best_score + 1e-6:
            best_score = score
            best_state = copy.deepcopy(model.state_dict())
        scheduler.step()
    if best_state is not None:
        model.load_state_dict(best_state)
    return history


def train_palm(model, train_loader, validation_loader, device, args) -> list[dict[str, object]]:
    """Train PALM with its official optimizer family and known-only selection."""

    amp = device.type == "cuda" and not args.no_amp
    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=args.palm_learning_rate,
        momentum=args.palm_momentum,
        nesterov=args.palm_momentum > 0.0,
        weight_decay=args.weight_decay,
    )
    scaler = torch.cuda.amp.GradScaler(enabled=amp)
    total_steps = max(1, args.epochs * len(train_loader))
    warmup_steps = min(total_steps, 10 * len(train_loader))
    best_loss = float("inf")
    best_state = None
    history: list[dict[str, object]] = []
    global_step = 0
    for epoch in range(args.epochs):
        model.train()
        total = 0.0
        batches = 0
        for batch in train_loader:
            if global_step < warmup_steps:
                learning_rate = args.palm_learning_rate * (
                    (global_step + 1) / max(1, warmup_steps)
                )
            else:
                progress = (global_step - warmup_steps) / max(
                    1, total_steps - warmup_steps
                )
                cosine = 0.5 * (1.0 + np.cos(np.pi * progress))
                learning_rate = args.palm_learning_rate * (
                    0.001 + 0.999 * cosine
                )
            for group in optimizer.param_groups:
                group["lr"] = float(learning_rate)

            views, quality, labels = move_batch(batch, device)
            optimizer.zero_grad(set_to_none=True)
            with torch.cuda.amp.autocast(enabled=amp):
                output = model(views, quality)
                loss = model.loss(output, labels)
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            scaler.step(optimizer)
            scaler.update()
            total += float(loss.detach().cpu())
            batches += 1
            global_step += 1

        epoch_loss = total / max(1, batches)
        validation_score = validation_f1(model, validation_loader, device)
        record = {
            "epoch": epoch + 1,
            "train_loss": epoch_loss,
            "validation_macro_f1": validation_score,
            "checkpoint_selection_value": epoch_loss,
            "prototype_updates": int(model.objective.update_count.detach().cpu()),
        }
        history.append(record)
        print(
            "palm_epoch=%d loss=%.6f validation_macro_f1=%.6f"
            % (epoch + 1, epoch_loss, validation_score),
            flush=True,
        )
        # The validation score is diagnostic only. This mirrors the official
        # repository's minimum training-loss checkpoint without OOD exposure.
        if epoch_loss < best_loss:
            best_loss = epoch_loss
            best_state = copy.deepcopy(model.state_dict())
    if best_state is not None:
        model.load_state_dict(best_state)
    return history


def train(model, train_loader, validation_loader, device, args) -> list[dict[str, object]]:
    if args.model == "cade":
        return train_cade(model, train_loader, validation_loader, device, args)
    if args.model == "opendetect":
        return train_open_detect(model, train_loader, validation_loader, device, args)
    if args.model == "palm":
        return train_palm(model, train_loader, validation_loader, device, args)
    initial_lr = 1e-6 if args.model == "closr" else args.learning_rate
    optimizer = torch.optim.AdamW(model.parameters(), lr=initial_lr, weight_decay=args.weight_decay)
    amp = device.type == "cuda" and not args.no_amp
    scaler = torch.cuda.amp.GradScaler(enabled=amp)
    best_score = -1.0
    best_state = None
    stale = 0
    history = []
    global_step = 0
    total_steps = max(1, args.epochs * len(train_loader))
    for epoch in range(args.epochs):
        model.train()
        total = 0.0
        batches = 0
        for batch in train_loader:
            views, quality, labels = move_batch(batch, device)
            if args.model == "closr":
                learning_rate = warmup_cosine_learning_rate(
                    global_step, total_steps, args.learning_rate
                )
                for group in optimizer.param_groups:
                    group["lr"] = learning_rate
            optimizer.zero_grad(set_to_none=True)
            with torch.cuda.amp.autocast(enabled=amp):
                output = model(views, quality)
                if args.model in {"arpl", "hcrp_osd", "closr"}:
                    loss = model.loss(output, labels)
                elif args.model == "ronetc":
                    loss = model.loss(output, labels, epoch)
                else:
                    loss = torch.nn.functional.cross_entropy(output["logits"], labels)
                    if args.model == "supcon":
                        loss = loss + args.contrast_weight * supervised_contrastive_loss(
                            output["embedding"], labels, args.contrast_temperature
                        )
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            scaler.step(optimizer)
            scaler.update()
            total += float(loss.detach().cpu())
            batches += 1
            global_step += 1
        score = None if args.model == "closr" else validation_f1(model, validation_loader, device)
        record = {"epoch": epoch + 1, "train_loss": total / max(1, batches), "validation_macro_f1": score}
        history.append(record)
        if score is None:
            print("epoch=%d loss=%.6f" % (epoch + 1, record["train_loss"]), flush=True)
            continue
        print("epoch=%d loss=%.6f validation_macro_f1=%.6f" % (epoch + 1, record["train_loss"], score), flush=True)
        if score > best_score + 1e-6:
            best_score = score
            best_state = copy.deepcopy(model.state_dict())
            stale = 0
        else:
            stale += 1
            if stale >= args.patience:
                break
    if best_state is not None:
        model.load_state_dict(best_state)
    return history


def report_for(labels, unknown, prediction, validation_risk, test_risk, acceptance):
    threshold = float(np.quantile(validation_risk, acceptance))
    return threshold, evaluate_hybrid_open_set(labels, unknown, prediction, test_risk, threshold)


def main() -> None:
    args = parse_arguments()
    if args.tao_stage1_adapter and args.model != "mlp":
        raise ValueError("TAO Stage-1 adapter is only defined for --model mlp")
    set_seed(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    unknown_classes = [value.strip() for value in args.unknown_classes.split(",") if value.strip()]
    if args.dataset == "synthetic":
        bundle = make_synthetic_open_set(seed=args.seed)
    else:
        if not args.csv:
            raise ValueError("--csv is required for tabular data")
        with open(args.config, "r", encoding="utf-8") as handle:
            config = json.load(handle)
        bundle = prepare_tabular_open_set(args.csv, config, unknown_classes, args.benign_class, args.max_per_class, args.chunksize, args.seed, args.split_strategy)

    device = choose_device(args.device)
    runtime_execution = {
        "requested_device": args.device,
        "resolved_device": str(device),
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_device_name": (
            torch.cuda.get_device_name(device) if device.type == "cuda" else None
        ),
        "cuda_device_index": (
            int(device.index) if device.type == "cuda" and device.index is not None else 0
        )
        if device.type == "cuda"
        else None,
        "torch_version": torch.__version__,
        "torch_cuda_version": torch.version.cuda,
    }
    loader_options = {"batch_size": args.batch_size, "num_workers": args.num_workers, "pin_memory": device.type == "cuda"}
    sampler = weighted_sampler(bundle.train.labels) if args.sampling == "weighted" else None
    train_loader = DataLoader(bundle.train, sampler=sampler, shuffle=sampler is None, **loader_options)
    validation_loader = DataLoader(bundle.validation, shuffle=False, **loader_options)
    test_loader = DataLoader(bundle.test, shuffle=False, **loader_options)
    fit_loader = DataLoader(bundle.train, shuffle=False, **loader_options)

    if args.model == "hcrp_osd":
        model = HCRPOSDClassifier(
            bundle.input_dims,
            len(bundle.class_names),
            args.hidden_dim,
            args.embedding_dim,
            args.dropout,
            args.temperature,
            args.radius_weight,
        )
    elif args.model == "arpl":
        model = ARPLClassifier(bundle.input_dims, len(bundle.class_names), args.hidden_dim, args.embedding_dim, args.dropout, args.temperature, args.radius_weight)
    elif args.model == "closr":
        model = CLOSRClassifier(
            bundle.input_dims,
            len(bundle.class_names),
            args.hidden_dim,
            args.embedding_dim,
            args.closr_depth,
            args.dropout,
            args.closr_margin,
            True,
            args.closr_alpha,
        )
    elif args.model == "cade":
        hidden_dims = tuple(
            int(value.strip())
            for value in args.cade_hidden.split(",")
            if value.strip()
        )
        model = CADEClassifier(
            bundle.input_dims,
            len(bundle.class_names),
            hidden_dims,
            args.cade_classifier_hidden,
            args.cade_classifier_dropout,
            args.cade_contrast_weight,
            args.cade_margin,
            args.cade_similar_ratio,
        )
    elif args.model == "opendetect":
        model = OpenDetectClassifier(
            bundle.input_dims,
            len(bundle.class_names),
            args.hidden_dim,
            args.embedding_dim,
            args.dropout,
            args.temperature,
            args.open_detect_generative_weight,
        )
    elif args.model == "ronetc":
        model = RoNeTCClassifier(
            bundle.input_dims,
            len(bundle.class_names),
            args.hidden_dim,
            args.embedding_dim,
            args.dropout,
            args.ronetc_annealing_epochs,
        )
    elif args.model == "palm":
        model = PALMClassifier(
            bundle.input_dims,
            len(bundle.class_names),
            args.hidden_dim,
            args.embedding_dim,
            args.dropout,
            args.palm_training_views,
            args.palm_prototypes_per_class,
            args.palm_assignment_top_k,
            args.palm_prototype_momentum,
            args.palm_temperature,
            args.palm_assignment_epsilon,
            args.palm_sinkhorn_iterations,
            args.palm_prototype_contrast_weight,
        )
    else:
        model = ConcatMLPClassifier(bundle.input_dims, len(bundle.class_names), args.hidden_dim, args.embedding_dim, args.dropout)
    model = model.to(device)
    started = time.perf_counter()
    history = train(model, train_loader, validation_loader, device, args)
    training_seconds = time.perf_counter() - started
    train_values = collect(model, fit_loader, device)
    if args.model == "closr":
        model.fit_centroids(train_values["embedding"], train_values["labels"])
        train_values = collect(model, fit_loader, device)
    validation = collect(model, validation_loader, device)
    test = collect(model, test_loader, device)
    labels = test["labels"]
    unknown = test["unknown"].astype(bool)
    reports: dict[str, dict[str, float]] = {}
    auxiliary_reports: dict[str, dict[str, float]] = {}
    thresholds: dict[str, float] = {}
    validation_scores: dict[str, np.ndarray] = {}
    test_scores: dict[str, np.ndarray] = {}
    test_predictions: dict[str, np.ndarray] = {}
    postprocessor_evidence: dict[str, dict[str, object]] = {}

    if args.model == "ronetc":
        name = "ronetc"
        validation_risk = ronetc_risk(validation["joint_uncertainty"])
        test_risk = ronetc_risk(test["joint_uncertainty"])
        prediction = test["logits"].argmax(axis=1)
        validation_scores[name] = validation_risk
        test_scores[name] = test_risk
        test_predictions[name] = prediction
        thresholds[name], reports[name] = report_for(
            labels,
            unknown,
            prediction,
            validation_risk,
            test_risk,
            args.known_acceptance,
        )
    elif args.model == "opendetect":
        name = "opendetect"
        validation_risk = open_detect_risk(validation["logits"])
        test_risk = open_detect_risk(test["logits"])
        prediction = test["logits"].argmax(axis=1)
        validation_scores[name] = validation_risk
        test_scores[name] = test_risk
        test_predictions[name] = prediction
        thresholds[name], reports[name] = report_for(
            labels,
            unknown,
            prediction,
            validation_risk,
            test_risk,
            args.known_acceptance,
        )
    elif args.model == "cade":
        name = "cade"
        calibrator = CADECalibrator()
        calibrator.fit(train_values["embedding"], train_values["labels"])
        validation_risk = calibrator.score(validation["embedding"])
        test_risk = calibrator.score(test["embedding"])
        prediction = test["logits"].argmax(axis=1)
        validation_scores[name] = validation_risk
        test_scores[name] = test_risk
        test_predictions[name] = prediction
        thresholds[name], reports[name] = report_for(
            labels,
            unknown,
            prediction,
            validation_risk,
            test_risk,
            args.known_acceptance,
        )
        auxiliary_reports["cade_official_mad35"] = evaluate_hybrid_open_set(
            labels,
            unknown,
            prediction,
            test_risk,
            args.cade_mad_threshold,
        )
    elif args.model == "closr":
        name = "closr"
        validation_risk = closr_risk(validation["logits"])
        test_risk = closr_risk(test["logits"])
        prediction = test["logits"].argmax(axis=1)
        validation_scores[name] = validation_risk
        test_scores[name] = test_risk
        test_predictions[name] = prediction
        thresholds[name], reports[name] = report_for(
            labels,
            unknown,
            prediction,
            validation_risk,
            test_risk,
            args.known_acceptance,
        )
    elif args.model in {"arpl", "hcrp_osd"}:
        name = "hcrp_osd_adapter" if args.model == "hcrp_osd" else "arpl"
        validation_risk = arpl_risk(validation["logits"])
        test_risk = arpl_risk(test["logits"])
        validation_scores[name] = validation_risk
        test_scores[name] = test_risk
        test_predictions[name] = test["logits"].argmax(axis=1)
        thresholds[name], reports[name] = report_for(labels, unknown, test["logits"].argmax(axis=1), validation_risk, test_risk, args.known_acceptance)
    elif args.model == "palm":
        name = "palm_ssd_plus"
        calibrator = PALMSSDMahalanobis(
            official_centering=not args.palm_ssd_corrected_centering
        )
        calibrator.fit(train_values["embedding"])
        validation_risk = calibrator.score(validation["embedding"])
        test_risk = calibrator.score(test["embedding"])
        prediction = test["logits"].argmax(axis=1)
        validation_scores[name] = validation_risk
        test_scores[name] = test_risk
        test_predictions[name] = prediction
        thresholds[name], reports[name] = report_for(
            labels,
            unknown,
            prediction,
            validation_risk,
            test_risk,
            args.known_acceptance,
        )
        postprocessor_evidence["palm_representation"] = model.evidence()
        postprocessor_evidence["palm_ssd_plus"] = calibrator.evidence()
    elif args.model in {"nci", "energy_cea", "nci_cea"}:
        name = args.model
        prediction = test["logits"].argmax(axis=1)
        if args.model in {"nci", "nci_cea"}:
            nci = NCICalibrator(args.nci_alpha)
            nci.fit(
                train_values["embedding"],
                model.classifier.weight.detach().cpu().numpy(),
            )
            validation_base_risk = nci.score(
                validation["embedding"], validation["logits"]
            )
            test_base_risk = nci.score(test["embedding"], test["logits"])
            postprocessor_evidence["nci"] = nci.evidence()
        else:
            validation_base_risk = energy_risk(
                validation["logits"], args.temperature
            )
            test_base_risk = energy_risk(test["logits"], args.temperature)

        if args.model in {"energy_cea", "nci_cea"}:
            cea = CEACalibrator(
                percentile=args.cea_percentile,
                addition_coefficient=args.cea_addition_coefficient,
                threshold_caution_coefficient=(
                    args.cea_threshold_caution_coefficient
                ),
            )
            cea.fit(validation["embedding"], validation_base_risk)
            validation_risk = cea.score(
                validation["embedding"], validation_base_risk
            )
            test_risk = cea.score(test["embedding"], test_base_risk)
            postprocessor_evidence["cea"] = cea.evidence()
            postprocessor_evidence["cea"]["base_score"] = (
                "energy" if args.model == "energy_cea" else "nci"
            )
        else:
            validation_risk = validation_base_risk
            test_risk = test_base_risk

        validation_scores[name] = validation_risk
        test_scores[name] = test_risk
        test_predictions[name] = prediction
        thresholds[name], reports[name] = report_for(
            labels,
            unknown,
            prediction,
            validation_risk,
            test_risk,
            args.known_acceptance,
        )
    else:
        prediction = test["logits"].argmax(axis=1)
        classifier_weight = model.classifier.weight.detach().cpu().numpy()
        classifier_bias = model.classifier.bias.detach().cpu().numpy()
        risks = {
            "msp": (msp_risk(validation["logits"]), msp_risk(test["logits"])),
            "energy": (energy_risk(validation["logits"], args.temperature), energy_risk(test["logits"], args.temperature)),
            "max_logit": (max_logit_risk(validation["logits"]), max_logit_risk(test["logits"])),
        }
        mahalanobis = SharedCovarianceMahalanobis()
        mahalanobis.fit(train_values["embedding"], train_values["labels"])
        risks["mahalanobis"] = (mahalanobis.score(validation["embedding"]), mahalanobis.score(test["embedding"]))
        relative_mahalanobis = RelativeMahalanobis()
        relative_mahalanobis.fit(train_values["embedding"], train_values["labels"])
        risks["relative_mahalanobis"] = (
            relative_mahalanobis.score(validation["embedding"]),
            relative_mahalanobis.score(test["embedding"]),
        )
        knn = KnownKnnDistance(args.knn_neighbors)
        knn.fit(train_values["embedding"])
        risks["knn"] = (knn.score(validation["embedding"]), knn.score(test["embedding"]))
        vim = ViMCalibrator()
        vim.fit(
            train_values["embedding"],
            train_values["logits"],
            model.classifier.weight.detach().cpu().numpy(),
            model.classifier.bias.detach().cpu().numpy(),
        )
        risks["vim"] = (
            vim.score(validation["embedding"], validation["logits"]),
            vim.score(test["embedding"], test["logits"]),
        )
        nci = NCICalibrator(args.nci_alpha)
        nci.fit(train_values["embedding"], classifier_weight)
        validation_nci = nci.score(
            validation["embedding"], validation["logits"]
        )
        test_nci = nci.score(test["embedding"], test["logits"])
        risks["nci"] = (validation_nci, test_nci)
        postprocessor_evidence["nci"] = nci.evidence()

        energy_cea = CEACalibrator(
            percentile=args.cea_percentile,
            addition_coefficient=args.cea_addition_coefficient,
            threshold_caution_coefficient=(
                args.cea_threshold_caution_coefficient
            ),
        )
        validation_energy = risks["energy"][0]
        test_energy = risks["energy"][1]
        energy_cea.fit(validation["embedding"], validation_energy)
        risks["energy_cea"] = (
            energy_cea.score(validation["embedding"], validation_energy),
            energy_cea.score(test["embedding"], test_energy),
        )
        postprocessor_evidence["energy_cea"] = energy_cea.evidence()
        postprocessor_evidence["energy_cea"]["base_score"] = "energy"

        nci_cea = CEACalibrator(
            percentile=args.cea_percentile,
            addition_coefficient=args.cea_addition_coefficient,
            threshold_caution_coefficient=(
                args.cea_threshold_caution_coefficient
            ),
        )
        nci_cea.fit(validation["embedding"], validation_nci)
        risks["nci_cea"] = (
            nci_cea.score(validation["embedding"], validation_nci),
            nci_cea.score(test["embedding"], test_nci),
        )
        postprocessor_evidence["nci_cea"] = nci_cea.evidence()
        postprocessor_evidence["nci_cea"]["base_score"] = "nci"
        if args.tao_stage1_adapter:
            pca = PCAResidualScorer(args.tao_pca_variance_ratio)
            pca.fit(train_values["embedding"])
            validation_pca = pca.score(validation["embedding"])
            test_pca = pca.score(test["embedding"])
            validation_blood = collect_mlp_blood(
                model,
                validation_loader,
                device,
                args.tao_blood_estimators,
                args.seed + 1000,
            )
            test_blood = collect_mlp_blood(
                model,
                test_loader,
                device,
                args.tao_blood_estimators,
                args.seed + 2000,
            )
            risks["tao_stage1_adapter"] = hybrid_scores(
                validation_pca,
                validation_blood,
                test_pca,
                test_blood,
                alpha=args.tao_alpha,
            )
            postprocessor_evidence["tao_stage1_adapter"] = {
                "upstream_repository": "https://github.com/WaIdo/TAO-NET",
                "upstream_commit": "a1574f38741772ac79628131f9fbef8a7c78374a",
                "protocol_class": "paper_code_adapter",
                "backbone": "shared_two_layer_mlp_not_upstream_roberta",
                "blood": "Hutchinson inter-layer Jacobian smoothness",
                "pca_fit_split": "known_only_train_embeddings",
                "normalization_split": "known_only_validation",
                "threshold_split": "known_only_validation",
                "alpha": args.tao_alpha,
                "pca_variance_ratio": args.tao_pca_variance_ratio,
                "blood_estimators": args.tao_blood_estimators,
                "upstream_default_test_youden_replaced": True,
                "unknown_or_test_labels_used_for_fitting_or_selection": False,
            }
        for name, (validation_risk, test_risk) in risks.items():
            validation_scores[name] = validation_risk
            test_scores[name] = test_risk
            test_predictions[name] = prediction
            thresholds[name], reports[name] = report_for(labels, unknown, prediction, validation_risk, test_risk, args.known_acceptance)
        scale = SCALECalibrator(
            percentile=args.scale_percentile,
            temperature=args.scale_temperature,
            rectify_negative=True,
        )
        scale.fit(
            validation["embedding"],
            validation["labels"],
            classifier_weight,
            classifier_bias,
        )
        validation_risk = scale.score(validation["embedding"])
        test_risk = scale.score(test["embedding"])
        scale_prediction = scale.predict(test["embedding"])
        validation_scores["scale"] = validation_risk
        test_scores["scale"] = test_risk
        test_predictions["scale"] = scale_prediction
        thresholds["scale"], reports["scale"] = report_for(
            labels,
            unknown,
            scale_prediction,
            validation_risk,
            test_risk,
            args.known_acceptance,
        )
        postprocessor_evidence["scale"] = scale.evidence()
        openmax = OpenMaxCalibrator(args.openmax_tail_size, args.openmax_alpha)
        openmax.fit(train_values["logits"], train_values["labels"])
        validation_risk, _ = openmax.predict(validation["logits"])
        test_risk, openmax_prediction = openmax.predict(test["logits"])
        validation_scores["openmax"] = validation_risk
        test_scores["openmax"] = test_risk
        test_predictions["openmax"] = openmax_prediction
        thresholds["openmax"], reports["openmax"] = report_for(labels, unknown, openmax_prediction, validation_risk, test_risk, args.known_acceptance)

    result = {
        "model": args.model,
        "method": next(iter(reports)) if len(reports) == 1 else "mlp_score_suite",
        "unknown_classes": unknown_classes,
        "seed": args.seed,
        "known_class_names": bundle.class_names,
        "sample_counts": bundle.sample_counts,
        "split_metadata": bundle.split_metadata,
        "split_sizes": {"train": len(bundle.train), "validation": len(bundle.validation), "test": len(bundle.test), "test_unknown": int(unknown.sum())},
        "validation_thresholds": thresholds,
        "reports": reports,
        "auxiliary_reports": auxiliary_reports,
        "training_history": history,
        "training_seconds": training_seconds,
        "trainable_parameters": count_trainable_parameters(model),
        "runtime_execution": runtime_execution,
        "implementation": {
            "closr": "official CLOSR method adapted to the shared CAEOS split and feature protocol",
            "cade": "official CADE method adapted to PyTorch and the shared CAEOS split and feature protocol",
            "opendetect": "official Open-Detect Gaussian-prototype VAE objective adapted to the shared CAEOS split and tabular side-channel features",
            "ronetc": "RoNeTC Dirichlet opinion, joint evidential loss, and Dempster-Shafer fusion adapted to shared tabular side-channel views; threshold calibrated on known validation only",
            "nci": "official NCI centered feature-to-predicted-class-weight alignment plus L1 feature norm; official default alpha fixed a priori and threshold calibrated on known validation only",
            "energy_cea": "official CEA extreme-activation correction applied to Energy risk; CEA threshold and scale fitted on known validation only",
            "nci_cea": "official CEA extreme-activation correction applied to NCI risk; NCI mean fitted on known train and CEA parameters fitted on known validation only",
            "palm": "official PALM mixture-prototype objective and SSD+ detector adapted from image crops to shared tabular side-channel views; all fitting and checkpoint selection are known-only",
            "hcrp_osd": "paper-structure HCRP-OSD adapter using parallel 2D CNN and 1D residual branches with the shared ARPL objective; not author-code reproduction; threshold calibrated on known validation only",
        }.get(args.model, "CAEOS same-split neural baseline"),
        "selection_evidence": {
            "protocol": "strict_known_only",
            "checkpoint_selection": (
                {
                    "split": "none",
                    "criterion": "fixed_paper_training_budget",
                }
                if args.model == "closr"
                else {
                    "split": (
                        "known_only_train"
                        if args.model == "palm"
                        else "known_only_validation"
                    ),
                    "criterion": (
                        "minimum_epoch_mean_palm_loss"
                        if args.model == "palm"
                        else "macro_f1"
                    ),
                }
            ),
            "postprocessors": postprocessor_evidence,
            "deployment_thresholds": {
                name: {
                    "split": "known_only_validation",
                    "known_acceptance_quantile": args.known_acceptance,
                    "value": value,
                }
                for name, value in thresholds.items()
            },
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
            "test_labels_used_for_final_metrics_only": True,
        },
        "arguments": vars(args),
    }
    with (output_dir / "metrics.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    score_archive = {
        "validation_labels": validation["labels"],
        "test_labels": labels,
        "test_unknown": unknown,
    }
    for name in validation_scores:
        score_archive[f"validation_{name}"] = validation_scores[name]
        score_archive[f"test_{name}"] = test_scores[name]
        score_archive[f"prediction_{name}"] = test_predictions[name]
    np.savez_compressed(output_dir / "scores.npz", **score_archive)
    torch.save({"model_state": model.state_dict(), "arguments": vars(args), "class_names": bundle.class_names, "input_dims": bundle.input_dims}, output_dir / "model.pt")
    print("metrics=" + json.dumps(reports, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
