import unittest

from hft_mgbs.features import PacketRecord
from hft_mgbs.representations import multi_level_vector, packet_length_sequence


class RepresentationTests(unittest.TestCase):
    def test_bidirectional_sign_and_padding(self):
        packets = [
            PacketRecord(1.0, "a", "b", 1, 2, 6, 100),
            PacketRecord(1.001, "b", "a", 2, 1, 6, 200),
        ]
        result = packet_length_sequence(packets, max_packets=4)
        self.assertEqual(result["signed_lengths"], [100.0, -200.0, 0.0, 0.0])
        self.assertEqual(result["mask"], [1.0, 1.0, 0.0, 0.0])
        self.assertAlmostEqual(result["iat_us"][1], 1000.0)

    def test_multi_level_summary(self):
        packets = [PacketRecord(0.0, "a", "b", 1, 2, 17, 64, b"abc")]
        result = multi_level_vector(packets, max_packets=2)
        self.assertEqual(result["flow_summary"][:2], [1.0, 64.0])
        self.assertEqual(result["flow_summary"][4], 3.0)


if __name__ == "__main__":
    unittest.main()
