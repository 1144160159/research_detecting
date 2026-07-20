from __future__ import annotations

import argparse
import copy
import json
import random
import time
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

from data.splits import get_splits
from model import OpenDetectNet, train_model, validate_model
from utils import reset_prototype, weight_init


class NpzClassSubset(Dataset):
    def __init__(self, path: str, classes: list[int], train: bool, open_label: bool = False):
        loaded = np.load(path)
        data = np.asarray(loaded["data"]).reshape(-1, 32, 32)
        labels = np.asarray(loaded["target"], dtype=np.int64)
        selected = np.isin(labels, classes)
        self.data = data[selected]
        raw_labels = labels[selected]
        mapping = {label: index for index, label in enumerate(classes)}
        self.labels = np.full(len(raw_labels), 999, dtype=np.int64) if open_label else np.asarray([mapping[int(label)] for label in raw_labels])
        operations = []
        if train:
            operations.extend([transforms.ToPILImage(), transforms.RandomCrop(32, padding=4), transforms.RandomHorizontalFlip()])
        else:
            operations.append(transforms.ToPILImage())
        operations.append(transforms.ToTensor())
        self.transform = transforms.Compose(operations)

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, index: int):
        return self.transform(self.data[index]), int(self.labels[index])


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reproduce official Open-Detect Malicious TLS protocol")
    parser.add_argument("--split", type=int, choices=(0, 1, 2), required=True)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--latent-dim", type=int, default=128)
    parser.add_argument("--lambda-weight", type=float, default=0.005)
    parser.add_argument("--seed", type=int, default=2022)
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True


@torch.no_grad()
def collect(model, loader):
    scores = []
    predictions = []
    labels = []
    model.eval()
    for images, target in loader:
        images = images.cuda(non_blocking=True)
        _, _, kl_div, _ = model(images)
        scores.append(kl_div.min(dim=1).values.cpu().numpy())
        predictions.append(kl_div.argmin(dim=1).cpu().numpy())
        labels.append(target.numpy())
    return np.concatenate(scores), np.concatenate(predictions), np.concatenate(labels)


def main() -> None:
    args = parse_arguments()
    if not torch.cuda.is_available():
        raise RuntimeError("official Open-Detect model requires CUDA")
    set_seed(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    known_classes, unknown_classes, _, _ = get_splits("mal", args.split)
    train_path = "data/dataset/mal_32_1c_train.npz"
    test_path = "data/dataset/mal_32_1c_test.npz"
    train_set = NpzClassSubset(train_path, known_classes, train=True)
    known_test = NpzClassSubset(test_path, known_classes, train=False)
    unknown_test = NpzClassSubset(test_path, unknown_classes, train=False, open_label=True)
    loader_options = {"num_workers": args.num_workers, "pin_memory": True}
    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True, **loader_options)
    known_loader = DataLoader(known_test, batch_size=512, shuffle=False, **loader_options)
    unknown_loader = DataLoader(unknown_test, batch_size=512, shuffle=False, **loader_options)

    model_args = argparse.Namespace(epoch=args.epochs, lamda=args.lambda_weight)
    model = OpenDetectNet("resnet18", 1, args.latent_dim, len(known_classes), 1.0, 1.0).cuda()
    model.apply(weight_init)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate, betas=(0.9, 0.999))
    scheduler = torch.optim.lr_scheduler.MultiStepLR(optimizer, milestones=[50, 80], gamma=0.1)
    best_accuracy = -1.0
    best_state = None
    started = time.perf_counter()
    for epoch in range(args.epochs):
        train_model(model, model_args, train_loader, epoch, optimizer)
        if epoch in (50, 80):
            model.prototypes = reset_prototype(model, train_loader)
        validation_accuracy = float(validate_model(model, model_args, known_loader, epoch))
        scheduler.step()
        if validation_accuracy > best_accuracy:
            best_accuracy = validation_accuracy
            best_state = copy.deepcopy(model.state_dict())
    if best_state is not None:
        model.load_state_dict(best_state)
    training_seconds = time.perf_counter() - started

    known_score, known_prediction, known_labels = collect(model, known_loader)
    unknown_score, _, _ = collect(model, unknown_loader)
    rng = np.random.RandomState(args.seed)
    count = min(len(known_score), len(unknown_score))
    known_index = rng.choice(len(known_score), size=count, replace=False)
    target = np.r_[np.zeros(count, dtype=np.int64), np.ones(len(unknown_score), dtype=np.int64)]
    risk = np.r_[known_score[known_index], unknown_score]
    metrics = {
        "model": "official_open_detect",
        "dataset": "mal",
        "split": args.split,
        "known_classes": known_classes,
        "unknown_classes": unknown_classes,
        "seed": args.seed,
        "known_test_samples": len(known_test),
        "unknown_test_samples": len(unknown_test),
        "known_accuracy": float(accuracy_score(known_labels, known_prediction)),
        "known_macro_f1": float(f1_score(known_labels, known_prediction, average="macro", zero_division=0)),
        "unknown_auroc": float(roc_auc_score(target, risk)),
        "mean_known_risk": float(known_score.mean()),
        "mean_unknown_risk": float(unknown_score.mean()),
        "best_known_validation_accuracy": best_accuracy,
        "training_seconds": training_seconds,
        "protocol_note": "Official train/test NPZ and class splits; known test set is also used for checkpoint selection as in the released code. AUROC is threshold independent.",
        "arguments": vars(args),
    }
    (output_dir / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    torch.save({"model_state": model.state_dict(), "metrics": metrics}, output_dir / "model.pt")
    print("metrics=" + json.dumps(metrics, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
