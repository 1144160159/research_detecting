import csv
import tempfile
import unittest
from pathlib import Path

from hft_mgbs.unsw import AttackInterval, UnswGroundTruth, canonical_flow_key


class UnswGroundTruthTests(unittest.TestCase):
    def test_bidirectional_key_and_time_overlap_match(self):
        key = canonical_flow_key("10.0.0.1", "10.0.0.2", 1234, 80, 6)
        truth = UnswGroundTruth(
            {key: [AttackInterval(100.0, 102.0, "Exploits")]}
        )
        reverse = ("10.0.0.2", "10.0.0.1", 80, 1234, 6)
        self.assertEqual(len(truth.matching_intervals(reverse, 101.0, 103.0)), 1)
        self.assertEqual(truth.matching_intervals(reverse, 103.0, 104.0), ())

    def test_tolerance_is_explicit(self):
        key = canonical_flow_key("a", "b", 1, 2, 17)
        truth = UnswGroundTruth({key: [AttackInterval(10.0, 10.0, "Generic")]})
        self.assertEqual(truth.matching_intervals(key, 10.5, 11.0), ())
        self.assertEqual(
            len(truth.matching_intervals(key, 10.5, 11.0, tolerance_s=0.5)), 1
        )

    def test_csv_parser_counts_unsupported_and_invalid_rows(self):
        headers = [
            "Start time",
            "Last time",
            "Attack category",
            "Protocol",
            "Source IP",
            "Source Port",
            "Destination IP",
            "Destination Port",
        ]
        rows = [
            ["1", "2", "Exploits", "tcp", "a", "1", "b", "2"],
            ["1", "2", "Other", "icmp", "a", "0", "b", "0"],
            ["bad", "2", "Other", "udp", "a", "1", "b", "2"],
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "gt.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(headers)
                writer.writerows(rows)
            truth = UnswGroundTruth.from_csv(path)
        self.assertEqual(truth.parse_stats["rows_total"], 3)
        self.assertEqual(truth.parse_stats["rows_indexed"], 1)
        self.assertEqual(truth.parse_stats["rows_unsupported_protocol"], 1)
        self.assertEqual(truth.parse_stats["rows_invalid_time"], 1)
        self.assertEqual(truth.event_ids_overlapping(1.5, 1.5), (1,))

    def test_event_scope_uses_time_overlap_and_stable_ids(self):
        key = canonical_flow_key("a", "b", 1, 2, 6)
        truth = UnswGroundTruth(
            {
                key: [
                    AttackInterval(10.0, 12.0, "A", event_id=7),
                    AttackInterval(20.0, 22.0, "B", event_id=8),
                ]
            }
        )

        self.assertEqual(truth.event_ids_overlapping(11.0, 20.0), (7, 8))
        self.assertEqual(truth.event_ids_overlapping(13.0, 19.0), ())


if __name__ == "__main__":
    unittest.main()
