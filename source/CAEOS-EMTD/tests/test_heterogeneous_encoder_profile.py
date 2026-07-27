from __future__ import annotations

import unittest

from train import encoder_kinds_for_profile


class HeterogeneousEncoderProfileTests(unittest.TestCase):
    def test_mal_tls_profile_maps_each_native_modality(self) -> None:
        names = [
            "tls_handshake",
            "ip_flow_statistics",
            "payload_statistics",
            "packet_sequence",
        ]
        self.assertEqual(
            encoder_kinds_for_profile("mal_tls_heterogeneous", names),
            ["tls_gated", "mlp", "mlp", "sequence_tcn"],
        )

    def test_mal_tls_profile_rejects_feature_group_proxy(self) -> None:
        with self.assertRaises(ValueError):
            encoder_kinds_for_profile(
                "mal_tls_heterogeneous", ["flow", "protocol", "relation"]
            )


if __name__ == "__main__":
    unittest.main()
