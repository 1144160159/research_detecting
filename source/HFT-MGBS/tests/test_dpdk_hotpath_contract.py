from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUST = (ROOT / "rust" / "hft-dpdk" / "src" / "main.rs").read_text(
    encoding="utf-8"
)
SHIM_C = (ROOT / "rust" / "hft-dpdk" / "csrc" / "hft_dpdk_shim.c").read_text(
    encoding="utf-8"
)
SHIM_H = (ROOT / "rust" / "hft-dpdk" / "csrc" / "hft_dpdk_shim.h").read_text(
    encoding="utf-8"
)
EXECUTION = json.loads(
    (ROOT / "configs" / "dpdk_hotpath_10mpps_execution_v1.json").read_text(
        encoding="utf-8"
    )
)


class DpdkHotpathContractTest(unittest.TestCase):
    def test_result_splits_tx_and_rx_hotpath_counters(self):
        for field in (
            "alloc_fail",
            "tx_calls",
            "tx_zero",
            "tx_partial",
            "tx_full",
            "tx_successful_bursts",
            "rx_polls",
            "rx_nonzero",
            "rx_zero",
        ):
            self.assertIn(f"{field}: u64", RUST)
        self.assertIn("rx_hotpath_counters: Vec<HotpathCounters>", RUST)
        self.assertIn("tx_hotpath_counters: Vec<HotpathCounters>", RUST)
        self.assertIn(
            "stalls: hotpath.alloc_fail.saturating_add(hotpath.tx_zero)", RUST
        )

    def test_adjusted_descriptors_and_mempool_counts_are_reported(self):
        for field in (
            "descriptor_configuration",
            "mempool_configured_capacity",
            "mempool_before",
            "mempool_after",
        ):
            self.assertIn(field, RUST)
        self.assertIn("actual_rx_desc", SHIM_H)
        self.assertIn("actual_tx_desc", SHIM_H)
        self.assertIn("rte_eth_dev_adjust_nb_rx_tx_desc", SHIM_C)
        self.assertIn("*actual_rx_desc = rx_desc", SHIM_C)
        self.assertIn("*actual_tx_desc = tx_desc", SHIM_C)
        self.assertIn("rte_mempool_avail_count", SHIM_C)
        self.assertIn("rte_mempool_in_use_count", SHIM_C)

    def test_64_byte_prepare_has_masked_fast_path_and_generic_fallback(self):
        self.assertIn("frame_size == 64 && template_count != 0", SHIM_C)
        self.assertIn("(sequence + i) & template_mask", SHIM_C)
        self.assertIn("(size_t)template_index << 6", SHIM_C)
        self.assertIn(
            "(uint16_t)((sequence + i) % template_count)", SHIM_C
        )
        self.assertIn("memcpy(data + timestamp_offset, &timestamp_cycles", SHIM_C)
        self.assertIn("timestamp_offset: u16", RUST)

    def test_zero_poll_housekeeping_is_bounded_without_removing_watchdog(self):
        self.assertIn("ZERO_POLL_HOUSEKEEPING_INTERVAL: u64 = 64", RUST)
        self.assertIn("zero_poll_requires_housekeeping(consecutive_zero_polls)", RUST)
        self.assertIn("WorkerWatchdog::spawn", RUST)
        self.assertIn("WORKER_WATCHDOG_EXIT_CODE", RUST)

    def test_execution_contract_is_staged_and_fail_closed(self):
        self.assertTrue(EXECUTION["frozen"])
        self.assertTrue(EXECUTION["diagnostic_only"])
        self.assertFalse(EXECUTION["final_pareto_ingestion_allowed"])
        stages = EXECUTION["stages"]
        self.assertEqual(
            [stage["target_mpps"] for stage in stages], [None, 1.0, 5.0, 10.0]
        )
        self.assertEqual(stages[-1]["required_repeats"], 3)
        self.assertEqual(EXECUTION["hard_gates"]["packet_gap"], 0)
        self.assertTrue(
            EXECUTION["hard_gates"]["complete_evidence_manifest_required"]
        )


if __name__ == "__main__":
    unittest.main()
