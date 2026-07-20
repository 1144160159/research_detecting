import unittest

import torch

from caeos.losses import compute_training_loss
from caeos.model import (
    ConflictAwareEvidentialNet,
    evidence_to_opinion,
    pairwise_conflict,
)
from caeos.open_set import DiagnosticConformalCalibrator


class CoreAlgorithmTest(unittest.TestCase):
    @staticmethod
    def _diagnostic_output(embedding, labels, uncertainty, conflict):
        num_classes = 2
        belief = torch.full((len(labels), num_classes), 0.05)
        belief[torch.arange(len(labels)), labels] = 0.70
        evidence = torch.full((len(labels), num_classes), 1.0)
        return {
            "fused_embedding": embedding,
            "fused_uncertainty": torch.as_tensor(uncertainty, dtype=torch.float32),
            "global_conflict": torch.as_tensor(conflict, dtype=torch.float32),
            "fused_belief": belief,
            "fused_evidence": evidence,
            "malicious_logit": torch.zeros(len(labels)),
        }

    def test_opinion_mass_is_normalized(self):
        evidence = torch.tensor([[2.0, 1.0, 0.0]])
        _, belief, uncertainty = evidence_to_opinion(evidence)
        total = belief.sum(dim=-1) + uncertainty.squeeze(-1)
        self.assertTrue(torch.allclose(total, torch.ones_like(total), atol=1e-6))

    def test_conflict_is_symmetric_and_zero_on_diagonal(self):
        beliefs = torch.tensor(
            [[[0.8, 0.1], [0.1, 0.8], [0.75, 0.15]]], dtype=torch.float32
        )
        reliability = torch.ones((1, 3))
        raw, effective, global_conflict, _ = pairwise_conflict(beliefs, reliability)
        self.assertTrue(torch.allclose(raw, raw.transpose(1, 2), atol=1e-6))
        self.assertTrue(torch.allclose(torch.diagonal(raw, dim1=1, dim2=2), torch.zeros(1, 3)))
        self.assertGreater(float(global_conflict[0]), 0.0)
        self.assertTrue(torch.allclose(raw, effective))

    def test_unreliable_view_has_smaller_effective_conflict(self):
        beliefs = torch.tensor([[[0.9, 0.0], [0.0, 0.9]]], dtype=torch.float32)
        _, high, _, _ = pairwise_conflict(beliefs, torch.ones((1, 2)))
        _, low, _, _ = pairwise_conflict(beliefs, torch.tensor([[1.0, 0.1]]))
        self.assertLess(float(low[0, 0, 1]), float(high[0, 0, 1]))

    def test_conflict_is_invariant_to_committed_mass_scale(self):
        beliefs = torch.tensor([[[0.4, 0.1], [0.1, 0.4]]], dtype=torch.float32)
        scaled_beliefs = beliefs * torch.tensor([[[0.4], [0.7]]])
        raw, _, _, _ = pairwise_conflict(beliefs, torch.ones((1, 2)))
        scaled_raw, _, _, _ = pairwise_conflict(
            scaled_beliefs, torch.ones((1, 2))
        )
        self.assertTrue(torch.allclose(raw, scaled_raw, atol=1e-6))

    def test_model_forward_and_backward(self):
        model = ConflictAwareEvidentialNet([8, 6, 4], 5, hidden_dim=16, embedding_dim=12)
        views = [torch.randn(10, 8), torch.randn(10, 6), torch.randn(10, 4)]
        output = model(views, torch.ones(10, 3))
        self.assertEqual(tuple(output["fused_belief"].shape), (10, 5))
        self.assertEqual(tuple(output["raw_conflict"].shape), (10, 3, 3))
        loss = -torch.log(output["fused_belief"][:, 0] + 1e-6).mean()
        loss.backward()
        self.assertTrue(any(parameter.grad is not None for parameter in model.parameters()))

    def test_training_loss_uses_reliability_logits(self):
        model = ConflictAwareEvidentialNet([8, 6, 4], 5, hidden_dim=16, embedding_dim=12)
        views = [torch.randn(10, 8), torch.randn(10, 6), torch.randn(10, 4)]
        output = model(views, torch.ones(10, 3))
        targets = torch.arange(10) % 5
        reliability_targets = torch.randint(0, 2, (10, 3), dtype=torch.float32)
        losses = compute_training_loss(
            output,
            targets,
            reliability_targets,
            benign_index=0,
            epoch=0,
            annealing_epochs=2,
        )
        self.assertTrue(torch.isfinite(losses["total"]))
        losses["total"].backward()

    def test_diagnostic_conformal_detects_multivariate_deviation(self):
        generator = torch.Generator().manual_seed(9)
        train_labels = torch.arange(80) // 40
        train_embedding = torch.randn(80, 3, generator=generator) * 0.12
        train_embedding[train_labels == 1] += 3.0
        train_output = self._diagnostic_output(
            train_embedding,
            train_labels,
            torch.full((80,), 0.25),
            torch.full((80,), 0.20),
        )

        validation_labels = torch.arange(40) // 20
        validation_embedding = torch.randn(40, 3, generator=generator) * 0.12
        validation_embedding[validation_labels == 1] += 3.0
        validation_output = self._diagnostic_output(
            validation_embedding,
            validation_labels,
            torch.full((40,), 0.25),
            torch.full((40,), 0.20),
        )

        calibrator = DiagnosticConformalCalibrator(
            2, benign_index=0, known_acceptance=0.95, min_class_samples=5
        )
        calibrator.fit_prototypes(train_embedding, train_labels)
        calibrator.fit_reference(train_output, train_labels)
        calibrator.fit_known_validation(validation_output)

        known_labels = torch.tensor([0, 1])
        known_output = self._diagnostic_output(
            torch.tensor([[0.05, -0.02, 0.03], [3.02, 2.97, 3.01]]),
            known_labels,
            torch.tensor([0.25, 0.25]),
            torch.tensor([0.20, 0.20]),
        )
        unknown_output = self._diagnostic_output(
            torch.tensor([[1.5, -1.5, 1.5], [4.5, 1.5, 4.5]]),
            known_labels,
            torch.tensor([0.90, 0.90]),
            torch.tensor([0.90, 0.90]),
        )
        known_risk, _, _ = calibrator.score(known_output)
        unknown_risk, _, _ = calibrator.score(unknown_output)
        self.assertGreater(float(unknown_risk.mean()), float(known_risk.mean()))
        self.assertEqual(calibrator.state_dict()["type"], "diagnostic_conformal")


if __name__ == "__main__":
    unittest.main()
