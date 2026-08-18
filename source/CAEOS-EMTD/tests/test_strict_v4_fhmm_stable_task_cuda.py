from __future__ import annotations

import sys

import pytest

import train_strict_v4_fhmm_stable_task_cuda as stable


def test_parser_separates_split_and_model_seed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "trainer",
            "--sequence-dataset",
            "dataset.npz",
            "--unknown-family",
            "Botnet",
            "--split-seed",
            "43",
            "--seed",
            "131",
            "--output-dir",
            "output",
            "--required-gpu-uuid",
            "GPU-test",
        ],
    )
    args = stable.parse_arguments()
    assert args.split_seed == 43
    assert args.seed == 131
    assert args.meta_inner_gradient_clip_norm == 1.0
    assert args.gradient_clip_norm == 5.0


def test_fp32_meta_loss_is_finite_on_tiny_model() -> None:
    torch = pytest.importorskip("torch")

    class TinyModel(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.shared = torch.nn.Linear(4, 4)
            self.family = torch.nn.Linear(4, 3)
            self.attack = torch.nn.Linear(4, 1)

        def forward(self, features, statistics):
            hidden = torch.tanh(
                self.shared(torch.cat((features, statistics), dim=1))
            )
            attack = self.attack(hidden).squeeze(1)
            return (
                hidden,
                hidden,
                self.family(hidden),
                attack,
                attack,
            )

    torch.manual_seed(7)
    model = TinyModel()
    batch_features = torch.randn(6, 2)
    batch_statistics = torch.randn(6, 2)
    batch_labels = torch.tensor([0, 1, 2, 0, 1, 2])
    episode_features = torch.randn(4, 2)
    episode_statistics = torch.randn(4, 2)
    episode_targets = torch.tensor([0, 1, 0, 1])
    inner, outer = stable.family_heldout_meta_loss(
        torch=torch,
        model=model,
        batch_features=batch_features,
        batch_statistics=batch_statistics,
        batch_labels=batch_labels,
        benign_index=0,
        heldout_family=2,
        episode_features=episode_features,
        episode_statistics=episode_statistics,
        episode_attack_targets=episode_targets,
        inner_learning_rate=0.02,
        inner_gradient_clip_norm=1.0,
    )
    assert torch.isfinite(inner)
    assert torch.isfinite(outer)
    outer.backward()
    assert all(
        parameter.grad is None or torch.isfinite(parameter.grad).all()
        for parameter in model.parameters()
    )


def test_meta_loss_rejects_nonpositive_clip_norm() -> None:
    torch = pytest.importorskip("torch")
    with pytest.raises(ValueError, match="clip norm"):
        stable.family_heldout_meta_loss(
            torch=torch,
            model=None,
            batch_features=None,
            batch_statistics=None,
            batch_labels=None,
            benign_index=0,
            heldout_family=1,
            episode_features=None,
            episode_statistics=None,
            episode_attack_targets=None,
            inner_learning_rate=0.02,
            inner_gradient_clip_norm=0.0,
        )

