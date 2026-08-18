from __future__ import annotations

import unittest

import numpy as np

from prepare_strict_v4_cic_iot2023_pcap_multimodal import (
    GRAPH_NODE_FEATURES,
    PACKET_COUNT,
    PAD_TOKEN,
    PAYLOAD_TOKENS,
    PacketRecord,
    canonical_flow_key,
    packet_features,
)


class PcapMultimodalPreparationTest(unittest.TestCase):
    def test_flow_key_is_bidirectionally_stable(self) -> None:
        forward = canonical_flow_key(b"a", b"b", 10, 20, 6)
        reverse = canonical_flow_key(b"b", b"a", 20, 10, 6)
        self.assertEqual(forward[:3], reverse[:3])
        self.assertEqual(forward[3], -reverse[3])

    def test_packet_features_have_frozen_shapes_and_no_address_input(self) -> None:
        records = [
            PacketRecord(1.0, 100, 1.0, 6, 2, b"hello"),
            PacketRecord(1.1, 80, -1.0, 6, 16, b"world"),
        ]
        payload, sequence, graph, quality = packet_features(records)
        self.assertEqual(payload.shape, (PAYLOAD_TOKENS,))
        self.assertEqual(sequence.shape, (PACKET_COUNT * 6,))
        self.assertEqual(
            graph.shape,
            (
                PACKET_COUNT * GRAPH_NODE_FEATURES
                + PACKET_COUNT * PACKET_COUNT,
            ),
        )
        self.assertEqual(quality.shape, (3,))
        np.testing.assert_array_equal(
            payload[:10],
            np.frombuffer(b"helloworld", dtype=np.uint8),
        )
        self.assertTrue(np.all(payload[10:] == PAD_TOKEN))
        adjacency = graph[PACKET_COUNT * GRAPH_NODE_FEATURES :].reshape(
            PACKET_COUNT, PACKET_COUNT
        )
        self.assertEqual(float(adjacency[0, 1]), 1.0)
        self.assertGreater(float(quality[0]), 0.0)


try:
    import torch

    from caeos.model import (
        BytePayloadCNNEncoder,
        PacketInteractionGraphEncoder,
    )
except ImportError:  # pragma: no cover - lightweight local runtime
    torch = None


@unittest.skipIf(torch is None, "torch is unavailable")
class PcapMultimodalEncoderTest(unittest.TestCase):
    def test_byte_and_graph_encoders_return_finite_embeddings(self) -> None:
        byte_encoder = BytePayloadCNNEncoder(64, 64, 32, 0.0)
        byte_tokens = torch.full((3, 64), 256, dtype=torch.long)
        byte_tokens[0, :8] = torch.arange(8)
        byte_output = byte_encoder(byte_tokens)
        self.assertEqual(tuple(byte_output.shape), (3, 32))
        self.assertTrue(torch.isfinite(byte_output).all())

        graph_dim = PACKET_COUNT * GRAPH_NODE_FEATURES + PACKET_COUNT**2
        graph_encoder = PacketInteractionGraphEncoder(
            graph_dim, 64, 32, 0.0
        )
        graph = torch.zeros((3, graph_dim))
        graph[:, 4] = 1.0
        graph[:, PACKET_COUNT * GRAPH_NODE_FEATURES] = 1.0
        graph_output = graph_encoder(graph)
        self.assertEqual(tuple(graph_output.shape), (3, 32))
        self.assertTrue(torch.isfinite(graph_output).all())


if __name__ == "__main__":
    unittest.main()
