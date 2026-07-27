from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import struct

from hft_mgbs.candidate_dataset import extract_candidate_flow_records

from test_pcap import ipv4_tcp_frame, pcap_bytes


class CandidateDatasetTest(unittest.TestCase):
    def test_observer_sees_all_flows_before_sampling(self):
        frame_a = bytearray(ipv4_tcp_frame(b"a"))
        frame_b = bytearray(ipv4_tcp_frame(b"b"))
        frame_a[34:36] = struct.pack("!H", 1000)
        frame_b[34:36] = struct.pack("!H", 1001)
        observed = []
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "flows.pcap"
            path.write_bytes(pcap_bytes([bytes(frame_a), bytes(frame_b)]))
            selected, summary = extract_candidate_flow_records(
                str(path),
                "test",
                batch_size=2,
                budget_us=0.0,
                key_flow_ratio=0.0,
                max_packets=2,
                max_flows=1,
                execution_budget_safety_ratio=0.5,
                flow_record_observer=observed.append,
            )

        self.assertEqual(len(selected), 1)
        self.assertEqual(len(observed), 2)
        self.assertEqual(summary["flow_records"], 2)
        self.assertEqual(summary["parsed_packets"], 2)
        self.assertEqual(summary["execution_budget_safety_ratio"], 0.5)
        self.assertEqual(summary["packet_start_timestamp"], 1.0)
        self.assertEqual(summary["packet_last_timestamp"], 1.001)


if __name__ == "__main__":
    unittest.main()
