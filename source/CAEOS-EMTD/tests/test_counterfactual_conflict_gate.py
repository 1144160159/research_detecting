import unittest

import torch

from caeos.model import ConflictAwareEvidentialNet
from caeos.training import (
    evaluate_counterfactual_gate,
    label_mismatched_sources,
    train_model,
)
from train import load_and_freeze_counterfactual_conflict_gate


class CounterfactualConflictGateTests(unittest.TestCase):
    def models(self):
        torch.manual_seed(17)
        reference = ConflictAwareEvidentialNet(
            [4, 3, 5, 6], 3, hidden_dim=8, embedding_dim=6, dropout=0.0
        )
        candidate = ConflictAwareEvidentialNet(
            [4, 3, 5, 6],
            3,
            hidden_dim=8,
            embedding_dim=6,
            dropout=0.0,
            counterfactual_conflict_gate=True,
        )
        load_and_freeze_counterfactual_conflict_gate(
            candidate, {"model_state": reference.state_dict()}
        )
        reference.eval()
        candidate.eval()
        return reference, candidate

    @staticmethod
    def batch():
        labels = torch.tensor([0, 1, 2, 0, 1, 2, 0, 1])
        return {
            "views": [torch.randn(8, dim) for dim in (4, 3, 5, 6)],
            "quality": torch.ones(8, 4),
            "label": labels,
            "is_unknown": torch.zeros(8, dtype=torch.bool),
        }

    def test_mismatched_sources_are_known_label_different(self) -> None:
        labels = torch.tensor([0, 0, 0, 1, 2])
        sources, valid = label_mismatched_sources(labels)
        self.assertTrue(bool(valid.all()))
        self.assertTrue(bool((labels[sources] != labels).all()))

    def test_zero_initialized_gate_is_exact_reference(self) -> None:
        reference, candidate = self.models()
        batch = self.batch()
        with torch.no_grad():
            expected = reference(batch["views"], batch["quality"])
            actual = candidate(batch["views"], batch["quality"])
        for key in (
            "fused_evidence",
            "fused_probability",
            "fused_embedding",
            "global_conflict",
        ):
            torch.testing.assert_close(actual[key], expected[key])
        torch.testing.assert_close(
            actual["counterfactual_gate_log_attenuation"], torch.zeros(8)
        )

    def test_only_gate_parameters_are_trainable(self) -> None:
        _, candidate = self.models()
        trainable = [name for name, value in candidate.named_parameters() if value.requires_grad]
        self.assertTrue(trainable)
        self.assertTrue(
            all(name.startswith("counterfactual_conflict_gate.") for name in trainable)
        )

    def test_known_only_counterfactual_training_updates_gate(self) -> None:
        reference, candidate = self.models()
        batch = self.batch()
        before = {
            name: value.detach().clone()
            for name, value in candidate.named_parameters()
            if value.requires_grad
        }
        history = train_model(
            candidate,
            [batch],
            [batch],
            torch.device("cpu"),
            benign_index=0,
            epochs=2,
            learning_rate=1e-2,
            weight_decay=0.0,
            annealing_epochs=1,
            corruption_probability=0.2,
            corruption_noise=0.2,
            use_amp=False,
            teacher_model=reference,
            consistency_weight=1.0,
            counterfactual_weight=1.0,
            counterfactual_margin=0.05,
            counterfactual_modality_indices=(0, 3),
            prefer_last_epoch_on_known_f1_tie=True,
        )
        self.assertGreater(history[0]["counterfactual_loss"], 0.0)
        self.assertTrue(
            any(
                not torch.equal(before[name], value.detach())
                for name, value in candidate.named_parameters()
                if value.requires_grad
            )
        )
        diagnostic = evaluate_counterfactual_gate(
            candidate, [batch], torch.device("cpu"), (0, 3), 0.05
        )
        self.assertEqual(diagnostic["valid_samples"], 8)
        self.assertFalse(diagnostic["unknown_or_test_labels_used"])


if __name__ == "__main__":
    unittest.main()
