from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Dict, Sequence

import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from torch import Tensor, nn
import torch.nn.functional as F

from .metrics import expected_calibration_error
from .model import ConflictAwareEvidentialNet, ViewEncoder


class ConcatMLPClassifier(nn.Module):
    def __init__(
        self,
        input_dims: Sequence[int],
        num_classes: int,
        hidden_dim: int = 128,
        embedding_dim: int = 64,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.encoder = ViewEncoder(
            sum(input_dims), hidden_dim, embedding_dim, dropout
        )
        self.classifier = nn.Linear(embedding_dim, num_classes)

    def forward(self, views: Sequence[Tensor], quality: Tensor = None) -> Dict[str, Tensor]:
        embedding = self.encoder(torch.cat(list(views), dim=-1))
        return {"logits": self.classifier(embedding), "embedding": embedding}


class IndependentViewClassifier(nn.Module):
    def __init__(
        self,
        input_dims: Sequence[int],
        num_classes: int,
        hidden_dim: int = 128,
        embedding_dim: int = 64,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.encoders = nn.ModuleList(
            ViewEncoder(dim, hidden_dim, embedding_dim, dropout) for dim in input_dims
        )
        self.heads = nn.ModuleList(
            nn.Linear(embedding_dim, num_classes) for _ in input_dims
        )

    def forward(self, views: Sequence[Tensor], quality: Tensor = None) -> Dict[str, Tensor]:
        embeddings = [encoder(view) for encoder, view in zip(self.encoders, views)]
        view_logits = torch.stack(
            [head(embedding) for head, embedding in zip(self.heads, embeddings)], dim=1
        )
        return {
            "logits": view_logits.mean(dim=1),
            "view_logits": view_logits,
            "embedding": torch.stack(embeddings, dim=1).mean(dim=1),
        }


class AegisBackboneAdapter(nn.Module):
    """Use the open-source AEGIS DeepResNet under the unified data protocol."""

    def __init__(self, aegis_root: str, input_dims: Sequence[int], num_classes: int):
        super().__init__()
        root = Path(aegis_root).resolve()
        network_file = root / "Network.py"
        if not network_file.exists():
            raise FileNotFoundError("AEGIS Network.py not found under %s" % root)
        root_text = str(root)
        if root_text not in sys.path:
            sys.path.insert(0, root_text)
        spec = importlib.util.spec_from_file_location("aegis_open_source_network", network_file)
        if spec is None or spec.loader is None:
            raise ImportError("cannot load AEGIS Network.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.backbone = module.DeepResNet(sum(input_dims), num_classes)

    def forward(self, views: Sequence[Tensor], quality: Tensor = None) -> Dict[str, Tensor]:
        values = torch.cat(list(views), dim=-1).unsqueeze(1)
        logits, embedding = self.backbone(values)
        return {"logits": logits, "embedding": embedding}


def build_multiclass_model(
    name: str,
    input_dims: Sequence[int],
    num_classes: int,
    hidden_dim: int = 128,
    embedding_dim: int = 64,
    dropout: float = 0.1,
    conflict_scale: float = 2.0,
    aegis_root: str = "../AEGIS-Net",
) -> nn.Module:
    if name == "mc0":
        return ConcatMLPClassifier(
            input_dims, num_classes, hidden_dim, embedding_dim, dropout
        )
    if name == "mc1":
        return IndependentViewClassifier(
            input_dims, num_classes, hidden_dim, embedding_dim, dropout
        )
    if name in {"mc2", "mc3", "mc4"}:
        fusion_mode = {"mc2": "sum", "mc3": "reliability", "mc4": "conflict"}[name]
        return ConflictAwareEvidentialNet(
            input_dims,
            num_classes,
            hidden_dim,
            embedding_dim,
            dropout,
            conflict_scale,
            fusion_mode=fusion_mode,
        )
    if name == "aegis_backbone":
        return AegisBackboneAdapter(aegis_root, input_dims, num_classes)
    raise ValueError("unknown multiclass model: %s" % name)


def model_probabilities(name: str, output: Dict[str, Tensor]) -> Tensor:
    if name in {"mc2", "mc3", "mc4"}:
        return output["fused_probability"]
    return torch.softmax(output["logits"], dim=-1)


def supervised_contrastive_loss(
    embeddings: Tensor, labels: Tensor, temperature: float = 0.07
) -> Tensor:
    embeddings = F.normalize(embeddings, dim=-1)
    similarity = embeddings @ embeddings.t() / temperature
    similarity = similarity - similarity.max(dim=1, keepdim=True).values.detach()
    same_class = labels[:, None].eq(labels[None, :])
    diagonal = torch.eye(len(labels), device=labels.device, dtype=torch.bool)
    positive = same_class & ~diagonal
    valid = positive.any(dim=1)
    log_probability = similarity - torch.logsumexp(
        similarity.masked_fill(diagonal, float("-inf")), dim=1, keepdim=True
    )
    positive_mean = (
        log_probability.masked_fill(~positive, 0.0).sum(dim=1)
        / positive.sum(dim=1).clamp_min(1)
    )
    if not valid.any():
        return embeddings.new_tensor(0.0)
    return -positive_mean[valid].mean()


def inject_symmetric_label_noise(
    labels: Tensor, num_classes: int, rate: float, seed: int
) -> Tensor:
    if not 0.0 <= rate < 1.0:
        raise ValueError("label noise rate must be in [0, 1)")
    noisy = labels.clone()
    if rate == 0.0:
        return noisy
    generator = torch.Generator().manual_seed(seed)
    selected = torch.rand(len(labels), generator=generator) < rate
    offsets = torch.randint(
        1, num_classes, (int(selected.sum()),), generator=generator
    )
    noisy[selected] = (noisy[selected] + offsets) % num_classes
    return noisy


def multiclass_report(
    labels: Tensor,
    probabilities: Tensor,
    class_names: Sequence[str],
) -> Dict[str, object]:
    labels_np = labels.detach().cpu().numpy()
    probabilities_np = probabilities.detach().cpu().numpy()
    predictions = probabilities_np.argmax(axis=1)
    clipped = np.clip(probabilities_np, 1e-8, 1.0)
    one_hot = np.eye(len(class_names), dtype=np.float64)[labels_np]
    return {
        "accuracy": float(accuracy_score(labels_np, predictions)),
        "precision_weighted": float(
            precision_score(labels_np, predictions, average="weighted", zero_division=0)
        ),
        "recall_weighted": float(
            recall_score(labels_np, predictions, average="weighted", zero_division=0)
        ),
        "f1_weighted": float(
            f1_score(labels_np, predictions, average="weighted", zero_division=0)
        ),
        "f1_macro": float(
            f1_score(labels_np, predictions, average="macro", zero_division=0)
        ),
        "f1_micro": float(
            f1_score(labels_np, predictions, average="micro", zero_division=0)
        ),
        "balanced_accuracy": float(balanced_accuracy_score(labels_np, predictions)),
        "ece": expected_calibration_error(probabilities_np, labels_np),
        "nll": float(-np.log(clipped[np.arange(len(labels_np)), labels_np]).mean()),
        "brier_score": float(np.square(probabilities_np - one_hot).sum(axis=1).mean()),
        "confusion_matrix": confusion_matrix(
            labels_np, predictions, labels=np.arange(len(class_names))
        ).tolist(),
        "classification_report": classification_report(
            labels_np,
            predictions,
            labels=np.arange(len(class_names)),
            target_names=list(class_names),
            output_dict=True,
            zero_division=0,
        ),
    }


def count_trainable_parameters(model: nn.Module) -> int:
    return int(sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad))
