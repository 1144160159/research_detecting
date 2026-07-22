import unittest

import torch

from caeos.model import ConflictAwareEvidentialNet, SpecialistEvidenceAdapter
from caeos.training import train_model
from train import (
    evidence_adapter_kinds_for_profile,
    load_and_freeze_geometry_preserving_adapter,
)


class GeometryPreservingEvidenceAdapterTests(unittest.TestCase):
    def models(self):
        torch.manual_seed(11)
        reference = ConflictAwareEvidentialNet(
            [4, 3, 5, 6], 3, hidden_dim=8, embedding_dim=6, dropout=0.0
        )
        candidate = ConflictAwareEvidentialNet(
            [4, 3, 5, 6],
            3,
            hidden_dim=8,
            embedding_dim=6,
            dropout=0.0,
            evidence_adapter_kinds=["tls_gated", "none", "none", "sequence_tcn"],
        )
        checkpoint = {"model_state": reference.state_dict()}
        load_and_freeze_geometry_preserving_adapter(candidate, checkpoint)
        reference.eval()
        candidate.eval()
        return reference, candidate

    def test_zero_initialized_adapter_is_exact_reference(self) -> None:
        reference, candidate = self.models()
        views = [torch.randn(7, dim) for dim in (4, 3, 5, 6)]
        quality = torch.ones(7, 4)
        with torch.no_grad():
            expected = reference(views, quality)
            actual = candidate(views, quality)
        for key in (
            "fused_evidence",
            "fused_embedding",
            "global_conflict",
            "discount",
            "fused_probability",
        ):
            torch.testing.assert_close(actual[key], expected[key])

    def test_adapter_changes_evidence_but_not_geometry_or_conflict(self) -> None:
        reference, candidate = self.models()
        for adapter in candidate.evidence_adapters:
            if isinstance(adapter, SpecialistEvidenceAdapter):
                torch.nn.init.constant_(adapter.head.bias, 0.5)
        views = [torch.randn(7, dim) for dim in (4, 3, 5, 6)]
        quality = torch.ones(7, 4)
        with torch.no_grad():
            expected = reference(views, quality)
            actual = candidate(views, quality)
        self.assertFalse(torch.equal(actual["fused_evidence"], expected["fused_evidence"]))
        torch.testing.assert_close(actual["fused_embedding"], expected["fused_embedding"])
        torch.testing.assert_close(actual["global_conflict"], expected["global_conflict"])
        torch.testing.assert_close(actual["discount"], expected["discount"])

    def test_only_specialist_adapter_parameters_are_trainable(self) -> None:
        _, candidate = self.models()
        trainable = [name for name, value in candidate.named_parameters() if value.requires_grad]
        self.assertTrue(trainable)
        self.assertTrue(all(name.startswith("evidence_adapters.") for name in trainable))

    def test_profile_uses_uniform_geometry_and_two_specialists(self) -> None:
        names = [
            "tls_handshake",
            "ip_flow_statistics",
            "payload_statistics",
            "packet_sequence",
        ]
        self.assertEqual(
            evidence_adapter_kinds_for_profile(
                "mal_tls_geometry_preserving_adapter", names
            ),
            ["tls_gated", "none", "none", "sequence_tcn"],
        )

    def test_known_only_consistency_training_updates_adapter(self) -> None:
        reference, candidate = self.models()
        labels = torch.tensor([0, 1, 2, 0, 1, 2, 0, 1])
        batch = {
            "views": [torch.randn(8, dim) for dim in (4, 3, 5, 6)],
            "quality": torch.ones(8, 4),
            "label": labels,
            "is_unknown": torch.zeros(8, dtype=torch.bool),
        }
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
            epochs=1,
            learning_rate=1e-3,
            weight_decay=0.0,
            annealing_epochs=1,
            corruption_probability=0.5,
            corruption_noise=0.2,
            use_amp=False,
            teacher_model=reference,
            consistency_weight=1.0,
        )
        self.assertEqual(len(history), 1)
        self.assertIn("consistency_loss", history[0])
        changed = [
            not torch.equal(before[name], value.detach())
            for name, value in candidate.named_parameters()
            if value.requires_grad
        ]
        self.assertTrue(any(changed))


if __name__ == "__main__":
    unittest.main()
