from __future__ import annotations

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


class DpdkStockTcpRssProfileTest(unittest.TestCase):
    def test_udp_remains_the_explicit_default(self):
        self.assertIn("enum TrafficProfile", RUST)
        self.assertIn("UdpCompat", RUST)
        self.assertIn(
            "default_value_t = TrafficProfile::UdpCompat",
            RUST,
        )
        self.assertIn(
            'Self::UdpCompat => "udp_compat"',
            RUST,
        )

    def test_tcp_profile_is_diagnostic_only_and_multiqueue(self):
        self.assertIn("TcpRssDiagnostic", RUST)
        self.assertIn(
            '"TCP RSS diagnostic profile requires at least two symmetric queues"',
            RUST,
        )
        self.assertIn(
            '"dpdk_bnx2x_stock_tcp_rss_diagnostic"',
            RUST,
        )
        self.assertIn("traffic_profile: &'static str", RUST)
        self.assertIn("synthetic_flow_count: usize", RUST)
        self.assertIn("port_configuration: &'static str", RUST)

    def test_stock_profile_requests_no_ethdev_rss_but_keeps_symmetric_queues(self):
        self.assertIn(
            "HFT_DPDK_TRAFFIC_PROFILE_STOCK_TCP_RSS_DIAGNOSTIC = 1",
            SHIM_H,
        )
        tcp_branch = SHIM_C.index(
            "HFT_DPDK_TRAFFIC_PROFILE_STOCK_TCP_RSS_DIAGNOSTIC) {"
        )
        configure = SHIM_C.index("rte_eth_dev_configure", tcp_branch)
        branch = SHIM_C[tcp_branch:configure]
        self.assertIn("config.rxmode.mq_mode = RTE_ETH_MQ_RX_NONE", branch)
        self.assertIn("config.rx_adv_conf.rss_conf.rss_hf = 0", branch)
        self.assertIn(
            "rte_eth_dev_configure(port_id, queue_count, queue_count, &config)",
            SHIM_C,
        )

    def test_tcp_timestamp_uses_padding_and_dynamic_checked_offset(self):
        self.assertIn("TCP_RSS_DIAGNOSTIC_TIMESTAMP_OFFSET: u16 = 54", RUST)
        self.assertIn("TrafficProfile::TcpRssDiagnostic =>", RUST)
        self.assertIn("40", RUST)
        self.assertIn("ipv4_transport_checksum", RUST)
        self.assertIn("frame[transport + 12] = 5 << 4", RUST)
        self.assertIn("frame[transport + 13] = 0x02", RUST)
        self.assertIn(
            "(uint32_t)timestamp_offset + sizeof(timestamp_cycles) > frame_size",
            SHIM_C,
        )
        self.assertIn("memcpy(data + timestamp_offset, &timestamp_cycles", SHIM_C)
        self.assertNotIn("memcpy(data + 42, &timestamp_cycles", SHIM_C)

    def test_template_cardinality_and_protocol_are_bound_into_report(self):
        self.assertIn("const TEMPLATE_COUNT: usize = 256", RUST)
        self.assertIn("synthetic_flow_count: TEMPLATE_COUNT", RUST)
        self.assertIn("ip_protocol: args.traffic_profile.ip_protocol()", RUST)
        self.assertIn(
            "timestamp_offset_bytes: args.traffic_profile.timestamp_offset()",
            RUST,
        )


if __name__ == "__main__":
    unittest.main()
