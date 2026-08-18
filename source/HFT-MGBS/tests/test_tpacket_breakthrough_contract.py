import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TpacketBreakthroughContractTests(unittest.TestCase):
    def test_search_is_bounded_and_fail_closed(self):
        value = json.loads((ROOT / "configs" / "tpacket_breakthrough_search_v1.json").read_text())
        self.assertEqual(value["candidate_budget"], 3)
        self.assertEqual(len(value["candidates"]), 3)
        self.assertFalse(value["full_pipeline_qualified"])
        self.assertFalse(value["final_pareto_ingestion_allowed"])
        self.assertEqual(value["hard_gates"]["capture_drop_rate_max"], 0.0)

    def test_runner_has_affinity_and_restoration_gates(self):
        script = (ROOT / "scripts" / "run_tpacket_v3_breakthrough.sh").read_text()
        required = [
            "PACKET_FANOUT_QM",
            "--fanout-mode qm",
            "irq_affinity_before.tsv",
            "irq_affinity_pre_restore.tsv",
            "irq_affinity_restored.tsv",
            "smp_affinity_list",
            "original_rx_ring",
            "rmmod pktgen",
            "trap '' HUP INT TERM",
            "pktgen is already loaded",
            "proc_stat_before.txt",
            "coalesce_restored.txt",
        ]
        for token in required:
            self.assertIn(token, script)


if __name__ == "__main__":
    unittest.main()
