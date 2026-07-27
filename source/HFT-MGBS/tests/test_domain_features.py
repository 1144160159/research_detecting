from __future__ import annotations

import unittest

from hft_mgbs.domain_features import transform_feature_row


class DomainFeatureTest(unittest.TestCase):
    def row(self):
        return {
            "packet_protocol": 6.0,
            "packet_src_port": 55000.0,
            "packet_dst_port": 443.0,
            "window_packets": 10000.0,
            "flow_packets": 10.0,
            "flow_bytes": 1000.0,
            "flow_payload_bytes": 600.0,
            "flow_fwd_packets": 7.0,
            "flow_bwd_packets": 3.0,
            "flow_fwd_bytes": 700.0,
            "flow_bwd_bytes": 300.0,
            "flow_fwd_payload_bytes": 500.0,
            "flow_bwd_payload_bytes": 100.0,
            "flow_fwd_mean_iat_s": 0.1,
            "flow_bwd_mean_iat_s": 0.2,
            "flow_fwd_iat_std_s": 0.01,
            "flow_bwd_iat_std_s": 0.03,
            "payload_entropy": 7.5,
        }

    def test_invariant_projection_removes_capture_window_artifact(self):
        projected = transform_feature_row(self.row(), "invariant_v1")

        self.assertNotIn("window_packets", projected)
        self.assertEqual(projected["service_port_443"], 1.0)
        self.assertAlmostEqual(
            projected["packet_direction_imbalance"], 0.4
        )

    def test_no_ports_profile_drops_service_identity(self):
        projected = transform_feature_row(
            self.row(), "invariant_no_ports_v1"
        )

        self.assertFalse(
            any(name.startswith("service_port_") for name in projected)
        )


if __name__ == "__main__":
    unittest.main()
