import math
import unittest

from hft_mgbs.features import MultiGranularityExtractor, PacketRecord


class FeatureTests(unittest.TestCase):
    def test_packet_flow_window_and_deep_features(self):
        extractor = MultiGranularityExtractor(window_seconds=1.0)
        first = PacketRecord(0.1, "a", "b", 1, 2, 6, 100, b"AAAA", 0x02)
        second = PacketRecord(0.3, "a", "b", 1, 2, 6, 200, bytes(range(4)), 0x10)
        extractor.update(first)
        extractor.update(second)

        flow = extractor.flow_features(first.flow_key)
        self.assertEqual(flow["flow_packets"], 2.0)
        self.assertEqual(flow["flow_bytes"], 300.0)
        self.assertAlmostEqual(flow["flow_duration_s"], 0.2)
        self.assertEqual(flow["flow_tcp_flags_or"], 0x12)
        self.assertEqual(extractor.window_features(0.3)["window_packets"], 2.0)

        deep = extractor.deep_payload_features([b"AAAA"])
        self.assertEqual(deep["payload_entropy"], 0.0)
        self.assertEqual(deep["payload_printable_ratio"], 1.0)

    def test_active_flow_bound(self):
        extractor = MultiGranularityExtractor(max_active_flows=2)
        for index in range(3):
            extractor.update(PacketRecord(float(index), str(index), "b", index, 2, 6, 64))
        self.assertEqual(extractor.active_flow_count, 2)

    def test_reverse_packets_share_one_flow_and_preserve_first_packet_direction(self):
        extractor = MultiGranularityExtractor()
        forward_1 = PacketRecord(1.0, "10.0.0.2", "10.0.0.1", 443, 1000, 6, 100, b"aa", 0x02)
        reverse = PacketRecord(1.1, "10.0.0.1", "10.0.0.2", 1000, 443, 6, 200, b"bbb", 0x10)
        forward_2 = PacketRecord(1.3, "10.0.0.2", "10.0.0.1", 443, 1000, 6, 300, b"cccc", 0x01)
        for packet in (forward_1, reverse, forward_2):
            extractor.update(packet)

        flow = extractor.flow_features(reverse.flow_key)
        self.assertEqual(extractor.active_flow_count, 1)
        self.assertEqual(flow["flow_packets"], 3.0)
        self.assertEqual(flow["flow_fwd_packets"], 2.0)
        self.assertEqual(flow["flow_bwd_packets"], 1.0)
        self.assertEqual(flow["flow_fwd_payload_bytes"], 6.0)
        self.assertEqual(flow["flow_bwd_payload_bytes"], 3.0)
        self.assertAlmostEqual(flow["flow_fwd_mean_iat_s"], 0.3)
        self.assertEqual(flow["flow_fwd_tcp_flags_or"], 0x03)
        self.assertEqual(flow["flow_bwd_tcp_flags_or"], 0x10)
        self.assertEqual(flow["flow_fwd_fin_flag_count"], 1.0)
        self.assertEqual(flow["flow_fwd_syn_flag_count"], 1.0)
        self.assertEqual(flow["flow_bwd_ack_flag_count"], 1.0)

    def test_payload_statistics_use_wire_payload_length_not_retained_prefix(self):
        extractor = MultiGranularityExtractor()
        packet = PacketRecord(0.0, "a", "b", 1, 2, 17, 1500, b"prefix", 0, 1200)
        extractor.update(packet)
        self.assertEqual(extractor.flow_features(packet.flow_key)["flow_payload_bytes"], 1200.0)

    def test_timeout_and_tcp_close_roll_flows_without_full_table_scan(self):
        extractor = MultiGranularityExtractor(activity_timeout_s=1.0, max_flow_duration_s=10.0)
        key = ("a", "b", 1, 2, 6)
        extractor.update(PacketRecord(0.0, *key[:2], key[2], key[3], key[4], 64, b"", 0x01))
        extractor.update(PacketRecord(0.1, "b", "a", 2, 1, 6, 64, b"", 0x01))
        extractor.update(PacketRecord(0.2, "a", "b", 1, 2, 6, 64))
        self.assertEqual(extractor.completed_flow_count, 1)
        self.assertEqual(extractor.flow_features(key)["flow_packets"], 1.0)
        extractor.update(PacketRecord(2.0, "a", "b", 1, 2, 6, 64))
        self.assertEqual(extractor.completed_flow_count, 2)
        self.assertEqual(extractor.flow_features(key)["flow_packets"], 1.0)


if __name__ == "__main__":
    unittest.main()
