from __future__ import annotations

import inspect

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

from caeos.medaf_tabular import (
    MEDAFTabularClassifier,
    medaf_probabilities,
    medaf_risk,
    medaf_training_loss,
    official_attention_diversity,
)
from train_medaf_tabular_open_set import train_known_only


class KnownOnlyDataset(Dataset):
    def __init__(self) -> None:
        generator = torch.Generator().manual_seed(389)
        self.views = [
            torch.randn(12, 5, generator=generator),
            torch.randn(12, 4, generator=generator),
            torch.randn(12, 3, generator=generator),
        ]
        self.labels = torch.tensor([0, 1, 2, 3] * 3)

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, index: int):
        return {
            "views": tuple(view[index] for view in self.views),
            "quality": torch.ones(3),
            "label": self.labels[index],
            "is_unknown": torch.tensor(False),
        }


def make_model() -> MEDAFTabularClassifier:
    torch.manual_seed(383)
    return MEDAFTabularClassifier(
        [5, 4, 3],
        4,
        hidden_dim=16,
        embedding_dim=8,
        dropout=0.0,
    )


def test_medaf_tabular_shapes_gate_and_probability() -> None:
    model = make_model()
    views = [torch.randn(7, 5), torch.randn(7, 4), torch.randn(7, 3)]
    labels = torch.tensor([0, 1, 2, 3, 0, 1, 2])
    output = model(views, labels=labels)
    assert output["expert_logits"].shape == (7, 3, 4)
    assert output["gated_logits"].shape == (7, 4)
    assert output["class_activation_maps"].shape == (7, 3, 8)
    torch.testing.assert_close(
        output["gate_weights"].sum(dim=1), torch.ones(7)
    )
    probability = medaf_probabilities(output)
    risk = medaf_risk(output)
    torch.testing.assert_close(probability.sum(dim=1), torch.ones(7))
    torch.testing.assert_close(risk, 1.0 - probability.max(dim=1).values)


def test_medaf_official_loss_weights_and_backward() -> None:
    model = make_model()
    views = [torch.randn(8, 5), torch.randn(8, 4), torch.randn(8, 3)]
    labels = torch.tensor([0, 1, 2, 3, 0, 1, 2, 3])
    output = model(views, labels=labels)
    losses = medaf_training_loss(output, labels)
    expected = (
        0.7 * losses["expert_cross_entropy"].sum()
        + losses["gate_cross_entropy"]
        + 0.01 * losses["attention_diversity"]
    )
    torch.testing.assert_close(losses["total"], expected)
    losses["total"].backward()
    assert model.experts[0].classifier.weight.grad is not None
    assert model.gate_head[-1].weight.grad is not None


def test_gate_loss_does_not_update_expert_branches() -> None:
    model = make_model()
    views = [torch.randn(6, 5), torch.randn(6, 4), torch.randn(6, 3)]
    labels = torch.tensor([0, 1, 2, 3, 0, 1])
    output = model(views)
    F.cross_entropy(output["gated_logits"], labels).backward()
    assert all(
        parameter.grad is None
        for expert in model.experts
        for parameter in expert.parameters()
    )
    assert model.gate_head[-1].weight.grad is not None


def test_official_diversity_is_three_pair_cosine_sum() -> None:
    base = torch.tensor(
        [[0.0, 1.0, 2.0, 4.0], [1.0, 3.0, 5.0, 9.0]]
    )
    maps = base[:, None, :].repeat(1, 3, 1)
    torch.testing.assert_close(
        official_attention_diversity(maps), torch.tensor(3.0)
    )


def test_known_only_training_loop_has_no_validation_or_test_input() -> None:
    parameters = set(inspect.signature(train_known_only).parameters)
    assert "validation_loader" not in parameters
    assert "test_loader" not in parameters
    model = make_model()
    history = train_known_only(
        model,
        DataLoader(KnownOnlyDataset(), batch_size=6, shuffle=False),
        torch.device("cpu"),
        epochs=1,
        milestone=1,
        learning_rate=0.01,
        momentum=0.9,
        weight_decay=1e-5,
        amp=False,
    )
    assert len(history) == 1
    assert history[0]["epoch"] == 1
    assert torch.isfinite(torch.tensor(history[0]["total"]))
