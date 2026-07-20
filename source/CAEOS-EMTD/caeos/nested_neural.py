from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np
import torch
from sklearn.metrics import roc_auc_score
from torch.utils.data import Dataset


class RemappedSubset(Dataset):
    """Subset a known dataset and remap sparse class indices for training."""

    def __init__(
        self,
        dataset: Dataset,
        indices: Sequence[int],
        label_map: Mapping[int, int],
        pseudo_unknown_class: int | None = None,
    ) -> None:
        self.dataset = dataset
        self.indices = np.asarray(indices, dtype=np.int64)
        self.label_map = {int(key): int(value) for key, value in label_map.items()}
        self.pseudo_unknown_class = pseudo_unknown_class
        original = np.asarray(dataset.labels)[self.indices]
        self.labels = torch.as_tensor(
            [self.label_map.get(int(value), -1) for value in original],
            dtype=torch.long,
        )

    def __len__(self) -> int:
        return int(len(self.indices))

    def __getitem__(self, index: int):
        item = dict(self.dataset[int(self.indices[index])])
        original_label = int(item["label"])
        item["label"] = torch.tensor(
            self.label_map.get(original_label, -1), dtype=torch.long
        )
        item["is_unknown"] = torch.tensor(
            self.pseudo_unknown_class is not None
            and original_label == self.pseudo_unknown_class,
            dtype=torch.bool,
        )
        return item


@dataclass(frozen=True)
class CandidateAggregate:
    mean_auroc: float
    minimum_auroc: float
    robust_objective: float


def aggregate_scores(scores: Sequence[float]) -> CandidateAggregate:
    values = np.asarray(scores, dtype=np.float64)
    if values.size == 0:
        raise ValueError("at least one score is required")
    mean_score = float(values.mean())
    minimum_score = float(values.min())
    return CandidateAggregate(
        mean_auroc=mean_score,
        minimum_auroc=minimum_score,
        robust_objective=0.5 * mean_score + 0.5 * minimum_score,
    )


def pseudo_unknown_auroc(
    labels: np.ndarray, risk: np.ndarray, held_out_class: int
) -> float:
    target = np.asarray(labels, dtype=np.int64) == int(held_out_class)
    if target.all() or not target.any():
        raise ValueError("pseudo-unknown evaluation requires both known and held-out samples")
    return float(roc_auc_score(target.astype(np.int64), np.asarray(risk)))


def select_candidate(
    aggregates: Mapping[str, CandidateAggregate],
    neural_candidates: Sequence[str] = ("neural_mahalanobis", "neural_knn"),
    minimum_neural_gain: float = 0.0,
) -> tuple[str, str]:
    if not aggregates:
        raise ValueError("candidate aggregates cannot be empty")

    def rank(name: str):
        value = aggregates[name]
        return (value.robust_objective, value.minimum_auroc, value.mean_auroc)

    hybrid_names = [name for name in aggregates if name not in neural_candidates]
    neural_names = [name for name in neural_candidates if name in aggregates]
    if not hybrid_names:
        return max(aggregates, key=rank), "no_hybrid_candidate"
    hybrid = max(hybrid_names, key=rank)
    if not neural_names:
        return hybrid, "no_neural_candidate"
    neural = max(neural_names, key=rank)
    gain = (
        aggregates[neural].robust_objective
        - aggregates[hybrid].robust_objective
    )
    if gain > float(minimum_neural_gain):
        return neural, "neural_gain=%.6f" % gain
    return hybrid, "neural_gain=%.6f_below_margin" % gain
