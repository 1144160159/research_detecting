import unittest

import torch
from torch import nn

from caeos.evidence_temperature import (
    apply_evidence_temperature,
    fit_known_evidence_temperature,
)
from caeos.model import ConservativeResidualEncoder, build_view_encoder
from train import encoder_kinds_for_profile


class ConservativeResidualEncoderTests(unittest.TestCase):
    def test_zero_initialized_specialist_starts_as_backbone(self) -> None:
        torch.manual_seed(3)
        base = nn.Linear(4, 3)
        specialist = nn.Linear(4, 3)
        encoder = ConservativeResidualEncoder(base, specialist, 3)
        values = torch.randn(5, 4)
        torch.testing.assert_close(encoder(values), base(values))

    def test_residual_is_bounded_per_embedding_coordinate(self) -> None:
        base = nn.Linear(4, 3)
        specialist = nn.Linear(4, 3)
        encoder = ConservativeResidualEncoder(base, specialist, 3)
        nn.init.ones_(encoder.residual_projection.weight)
        values = torch.randn(7, 4)
        delta = encoder(values) - base(values)
        self.assertLessEqual(float(delta.abs().max()), 0.25 + 1e-7)

    def test_profile_assigns_only_tls_and_sequence_specialists(self) -> None:
        names = [
            "tls_handshake",
            "ip_flow_statistics",
            "payload_statistics",
            "packet_sequence",
        ]
        self.assertEqual(
            encoder_kinds_for_profile("mal_tls_conservative_residual", names),
            ["tls_residual_025", "mlp", "mlp", "sequence_residual_025"],
        )
        self.assertIsInstance(
            build_view_encoder("tls_residual_025", 4, 8, 6, 0.0),
            ConservativeResidualEncoder,
        )

    def test_temperature_fit_uses_known_labels_and_preserves_argmax(self) -> None:
        output = {"fused_evidence": torch.tensor([[8.0, 1.0], [1.0, 8.0]])}
        labels = torch.tensor([0, 1])
        temperature, nll = fit_known_evidence_temperature(
            output, labels, grid=(0.5, 1.0, 2.0)
        )
        self.assertEqual(temperature, 0.5)
        self.assertGreaterEqual(nll, 0.0)
        calibrated = apply_evidence_temperature(output, temperature)
        torch.testing.assert_close(
            calibrated["fused_probability"].argmax(1), labels
        )


if __name__ == "__main__":
    unittest.main()
