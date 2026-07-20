from __future__ import annotations

import argparse
import copy
import json
import random
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
from sklearn.metrics import f1_score
from torch import Tensor
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler
import torch.nn.functional as F

from caeos.data import make_synthetic_multiclass, prepare_tabular_closed_set
from caeos.losses import compute_training_loss
from caeos.multiclass import (
    build_multiclass_model,
    count_trainable_parameters,
    inject_symmetric_label_noise,
    model_probabilities,
    multiclass_report,
    supervised_contrastive_loss,
)
from caeos.training import corrupt_modalities


EVIDENTIAL_MODELS = {"mc2", "mc3", "mc4"}


class LabelOverrideDataset(Dataset):
    def __init__(self, base: Dataset, labels: Tensor):
        if len(base) != len(labels):
            raise ValueError("label override length does not match dataset")
        self.base = base
        self.labels = labels.to(torch.long)

    def __len__(self) -> int:
        return len(self.base)

    def __getitem__(self, index: int) -> Dict[str, object]:
        item = dict(self.base[index])
        item["label"] = self.labels[index]
        return item


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Closed-set multiclass traffic baselines")
    parser.add_argument(
        "--model",
        choices=("mc0", "mc1", "mc2", "mc3", "mc4", "aegis_backbone"),
        default="mc0",
    )
    parser.add_argument("--dataset", choices=("synthetic", "tabular"), default="synthetic")
    parser.add_argument("--csv", default=None)
    parser.add_argument("--config", default="configs/nf_unsw_nb15.json")
    parser.add_argument("--benign-class", default="Benign")
    parser.add_argument("--max-per-class", type=int, default=5000)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--patience", type=int, default=10)
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
    parser.add_argument("--label-noise", type=float, default=0.0)
    parser.add_argument("--sampling", choices=("weighted", "natural"), default="weighted")
    parser.add_argument("--aegis-root", default="../AEGIS-Net")
    parser.add_argument("--aegis-contrast-weight", type=float, default=0.5)
    parser.add_argument("--temperature", type=float, default=0.07)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--prefetch-factor", type=int, default=2)
    parser.add_argument("--fused-adamw", action="store_true")
    parser.add_argument(
        "--compile-mode",
        choices=("none", "default", "reduce-overhead", "max-autotune"),
        default="none",
    )
    parser.add_argument(
        "--matmul-precision", choices=("highest", "high", "medium"), default="high"
    )
    parser.add_argument("--disable-tf32", action="store_true")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--output-dir", default="runs/multiclass/latest")
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


def weighted_sampler(labels: Tensor) -> WeightedRandomSampler:
    counts = torch.bincount(labels)
    class_weight = 1.0 / counts.to(torch.float64).clamp_min(1.0)
    return WeightedRandomSampler(class_weight[labels], len(labels), replacement=True)


def move_batch(
    batch: Dict[str, object], device: torch.device
) -> Tuple[List[Tensor], Tensor, Tensor]:
    views = [view.to(device, non_blocking=True) for view in batch["views"]]
    quality = batch["quality"].to(device, non_blocking=True)
    labels = batch["label"].to(device, non_blocking=True)
    return views, quality, labels


def classification_loss(
    model_name: str,
    output: Dict[str, Tensor],
    labels: Tensor,
    reliability_target: Tensor,
    benign_index: int,
    epoch: int,
    args: argparse.Namespace,
) -> Tensor:
    if model_name in EVIDENTIAL_MODELS:
        losses = compute_training_loss(
            output,
            labels,
            reliability_target,
            benign_index,
            epoch,
            args.annealing_epochs,
            center_weight=0.0,
            reliability_weight=0.0 if model_name == "mc2" else 0.2,
            malicious_weight=0.0,
        )
        return losses["total"]
    loss = F.cross_entropy(output["logits"], labels)
    if model_name == "mc1":
        view_loss = torch.stack(
            [
                F.cross_entropy(output["view_logits"][:, index], labels)
                for index in range(output["view_logits"].shape[1])
            ]
        ).mean()
        loss = 0.5 * loss + 0.5 * view_loss
    elif model_name == "aegis_backbone":
        loss = loss + args.aegis_contrast_weight * supervised_contrastive_loss(
            output["embedding"], labels, args.temperature
        )
    return loss


@torch.no_grad()
def collect_predictions(
    model: torch.nn.Module,
    model_name: str,
    loader: DataLoader,
    device: torch.device,
) -> Tuple[Tensor, Tensor]:
    model.eval()
    labels_all = []
    probabilities_all = []
    for batch in loader:
        views, quality, labels = move_batch(batch, device)
        output = model(views, quality)
        labels_all.append(labels.cpu())
        probabilities_all.append(model_probabilities(model_name, output).cpu())
    return torch.cat(labels_all), torch.cat(probabilities_all)


def validation_macro_f1(
    model: torch.nn.Module,
    model_name: str,
    loader: DataLoader,
    device: torch.device,
) -> float:
    labels, probabilities = collect_predictions(model, model_name, loader, device)
    return float(
        f1_score(
            labels.numpy(), probabilities.argmax(dim=1).numpy(), average="macro", zero_division=0
        )
    )


def train_model(
    model: torch.nn.Module,
    model_name: str,
    train_loader: DataLoader,
    validation_loader: DataLoader,
    device: torch.device,
    benign_index: int,
    args: argparse.Namespace,
) -> List[Dict[str, float]]:
    optimizer_options = {
        "lr": args.learning_rate,
        "weight_decay": args.weight_decay,
    }
    if args.fused_adamw and device.type == "cuda":
        optimizer_options["fused"] = True
    try:
        optimizer = torch.optim.AdamW(model.parameters(), **optimizer_options)
    except (TypeError, RuntimeError):
        optimizer_options.pop("fused", None)
        optimizer = torch.optim.AdamW(model.parameters(), **optimizer_options)
    use_amp = not args.no_amp and device.type == "cuda"
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)
    best_score = -1.0
    best_state = None
    stale_epochs = 0
    history = []

    for epoch in range(args.epochs):
        model.train()
        total_loss = 0.0
        batches = 0
        for batch in train_loader:
            views, quality, labels = move_batch(batch, device)
            if model_name in {"mc3", "mc4"}:
                views, quality, reliability_target = corrupt_modalities(
                    views,
                    quality,
                    args.corruption_probability,
                    args.corruption_noise,
                )
            else:
                reliability_target = torch.ones(
                    (len(labels), len(views)), device=device, dtype=views[0].dtype
                )
            optimizer.zero_grad(set_to_none=True)
            with torch.cuda.amp.autocast(enabled=use_amp):
                output = model(views, quality)
                loss = classification_loss(
                    model_name,
                    output,
                    labels,
                    reliability_target,
                    benign_index,
                    epoch,
                    args,
                )
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.0)
            scaler.step(optimizer)
            scaler.update()
            total_loss += float(loss.detach().cpu())
            batches += 1

        score = validation_macro_f1(
            model, model_name, validation_loader, device
        )
        record = {
            "epoch": float(epoch + 1),
            "train_loss": total_loss / max(1, batches),
            "validation_macro_f1": score,
        }
        history.append(record)
        print(
            "epoch=%d train_loss=%.5f validation_macro_f1=%.5f"
            % (epoch + 1, record["train_loss"], score),
            flush=True,
        )
        if score > best_score + 1e-6:
            best_score = score
            best_state = copy.deepcopy(model.state_dict())
            stale_epochs = 0
        else:
            stale_epochs += 1
            if stale_epochs >= args.patience:
                print("early_stop_epoch=%d" % (epoch + 1), flush=True)
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    return history


def json_dump(path: Path, value: object) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)


def main() -> None:
    args = parse_arguments()
    set_seed(args.seed)
    torch.set_float32_matmul_precision(args.matmul_precision)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if args.dataset == "synthetic":
        bundle = make_synthetic_multiclass(seed=args.seed)
    else:
        if not args.csv:
            raise ValueError("--csv is required for tabular data")
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

    clean_labels = bundle.train.labels.clone()
    noisy_labels = inject_symmetric_label_noise(
        clean_labels, len(bundle.class_names), args.label_noise, args.seed + 1000
    )
    train_dataset = LabelOverrideDataset(bundle.train, noisy_labels)
    sampler = weighted_sampler(noisy_labels) if args.sampling == "weighted" else None
    device = choose_device(args.device)
    loader_options = {
        "batch_size": args.batch_size,
        "num_workers": args.num_workers,
        "pin_memory": device.type == "cuda",
    }
    if args.num_workers > 0:
        loader_options["persistent_workers"] = True
        loader_options["prefetch_factor"] = args.prefetch_factor
    train_loader = DataLoader(
        train_dataset,
        sampler=sampler,
        shuffle=sampler is None,
        **loader_options,
    )
    validation_loader = DataLoader(bundle.validation, shuffle=False, **loader_options)
    test_loader = DataLoader(bundle.test, shuffle=False, **loader_options)

    model = build_multiclass_model(
        args.model,
        bundle.input_dims,
        len(bundle.class_names),
        args.hidden_dim,
        args.embedding_dim,
        args.dropout,
        args.conflict_scale,
        args.aegis_root,
    ).to(device)
    raw_model = model
    if device.type == "cuda":
        allow_tf32 = not args.disable_tf32
        torch.backends.cuda.matmul.allow_tf32 = allow_tf32
        torch.backends.cudnn.allow_tf32 = allow_tf32
        torch.cuda.reset_peak_memory_stats(device)
    if args.compile_mode != "none":
        if not hasattr(torch, "compile"):
            raise RuntimeError("torch.compile requires PyTorch 2.0 or newer")
        compile_options = {} if args.compile_mode == "default" else {"mode": args.compile_mode}
        model = torch.compile(model, **compile_options)
    print("model=%s device=%s torch=%s" % (args.model, device, torch.__version__))
    print("class_names=" + json.dumps(bundle.class_names, ensure_ascii=False))
    print("sample_counts=" + json.dumps(bundle.sample_counts, ensure_ascii=False))
    print(
        "split_sizes=train:%d validation:%d test:%d"
        % (len(bundle.train), len(bundle.validation), len(bundle.test))
    )

    if device.type == "cuda":
        torch.cuda.synchronize(device)
    training_start = time.perf_counter()
    history = train_model(
        model,
        args.model,
        train_loader,
        validation_loader,
        device,
        bundle.benign_index,
        args,
    )
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    training_seconds = time.perf_counter() - training_start
    inference_start = time.perf_counter()
    test_labels, test_probabilities = collect_predictions(
        model, args.model, test_loader, device
    )
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    inference_seconds = time.perf_counter() - inference_start
    report = multiclass_report(test_labels, test_probabilities, bundle.class_names)
    report["model"] = args.model
    report["trainable_parameters"] = count_trainable_parameters(raw_model)
    report["label_noise_requested"] = args.label_noise
    report["label_noise_realized"] = float((clean_labels != noisy_labels).float().mean())
    report["training_seconds"] = training_seconds
    report["inference_seconds"] = inference_seconds
    report["inference_samples_per_second"] = len(test_labels) / max(inference_seconds, 1e-9)
    report["peak_gpu_memory_mb"] = (
        float(torch.cuda.max_memory_allocated(device) / (1024 ** 2))
        if device.type == "cuda"
        else 0.0
    )
    report["compile_mode"] = args.compile_mode
    report["tf32_enabled"] = device.type == "cuda" and not args.disable_tf32
    print("metrics=" + json.dumps(report, ensure_ascii=False, sort_keys=True))

    torch.save(
        {
            "model_state": raw_model.state_dict(),
            "model": args.model,
            "input_dims": bundle.input_dims,
            "class_names": bundle.class_names,
            "arguments": vars(args),
        },
        str(output_dir / "model.pt"),
    )
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
            "split_sizes": {
                "train": len(bundle.train),
                "validation": len(bundle.validation),
                "test": len(bundle.test),
            },
        },
    )


if __name__ == "__main__":
    main()
