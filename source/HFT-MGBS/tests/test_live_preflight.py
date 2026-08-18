from __future__ import annotations

import unittest

from hft_mgbs.live_preflight import audit_host_preflight


def frozen_thresholds():
    return {
        "frozen": True,
        "target_load_mpps": 1.0,
        "target_load_gbps": None,
        "max_parse_reject_rate": 0.01,
        "max_end_to_end_p99_us": 1000.0,
        "max_end_to_end_p999_us": 2000.0,
        "min_run_duration_s": 3600.0,
    }


class LivePreflightTest(unittest.TestCase):
    def test_physical_interface_capabilities_and_thresholds_pass(self):
        result = audit_host_preflight(
            "/sys/devices/pci0000:00/0000:01:00.0/net/ens1f0",
            (1 << 12) | (1 << 13),
            frozen_thresholds(),
            carrier=1,
            operstate="up",
            speed_mbps=10000,
            driver="bnx2x",
            capture_driver="af-packet-ts",
            timestamp_capabilities=(
                "software-receive",
                "software-system-clock",
            ),
        )

        self.assertTrue(result["accepted"])

    def test_virtual_interface_missing_capability_and_template_fail(self):
        thresholds = frozen_thresholds()
        thresholds["frozen"] = False
        thresholds["target_load_mpps"] = None
        thresholds["max_end_to_end_p99_us"] = None

        result = audit_host_preflight(
            "/sys/devices/virtual/net/eth0",
            1 << 13,
            thresholds,
            carrier=0,
            operstate="down",
            speed_mbps=None,
            driver=None,
        )

        self.assertFalse(result["accepted"])
        self.assertIn("interface.not_physical", result["errors"])
        self.assertIn("capability.cap_net_admin", result["errors"])
        self.assertIn("thresholds.not_frozen", result["errors"])
        self.assertIn("thresholds.target_load", result["errors"])
        self.assertIn(
            "thresholds.max_end_to_end_p99_us", result["errors"]
        )
        self.assertIn("link.no_carrier", result["errors"])
        self.assertFalse(result["link_ready"])

    def test_physical_interface_without_carrier_fails_closed(self):
        result = audit_host_preflight(
            "/sys/devices/pci0000:00/0000:01:00.0/net/ens1f0",
            (1 << 12) | (1 << 13),
            frozen_thresholds(),
            carrier=0,
            operstate="down",
            speed_mbps=-1,
            driver="bnx2x",
        )

        self.assertFalse(result["accepted"])
        self.assertIn("link.no_carrier", result["errors"])
        self.assertIn("link.operstate", result["errors"])
        self.assertIn("link.speed", result["errors"])

    def test_timestamped_driver_requires_kernel_timestamp_support(self):
        result = audit_host_preflight(
            "/sys/devices/pci0000:00/0000:01:00.0/net/ens1f0",
            (1 << 12) | (1 << 13),
            frozen_thresholds(),
            carrier=1,
            operstate="up",
            speed_mbps=10000,
            driver="bnx2x",
            capture_driver="af-packet-ts",
            timestamp_capabilities=("software-transmit",),
        )

        self.assertFalse(result["accepted"])
        self.assertIn(
            "timestamp.so_timestampns_unsupported", result["errors"]
        )

    def test_final_10gbe_gate_rejects_management_or_slow_interface(self):
        result = audit_host_preflight(
            "/sys/devices/pci0000:00/0000:01:00.0/net/ens9f0",
            (1 << 12) | (1 << 13),
            frozen_thresholds(),
            carrier=1,
            operstate="up",
            speed_mbps=1000,
            driver="tg3",
            capture_driver="af-packet-ts",
            timestamp_capabilities=(
                "software-receive",
                "software-system-clock",
            ),
            minimum_speed_mbps=10000,
            require_unmanaged=True,
            network_master="br0",
            has_ip_address=False,
            carries_default_route=True,
        )

        self.assertFalse(result["accepted"])
        self.assertIn("link.speed_below_minimum", result["errors"])
        self.assertIn("interface.network_master", result["errors"])
        self.assertIn("interface.default_route", result["errors"])

    def test_final_10gbe_gate_rejects_configured_ip_address(self):
        result = audit_host_preflight(
            "/sys/devices/pci0000:00/0000:01:00.0/net/ens1f0",
            (1 << 12) | (1 << 13),
            frozen_thresholds(),
            carrier=1,
            operstate="up",
            speed_mbps=10000,
            driver="ixgbe",
            minimum_speed_mbps=10000,
            require_unmanaged=True,
            network_master=None,
            has_ip_address=True,
            carries_default_route=False,
        )

        self.assertFalse(result["accepted"])
        self.assertIn(
            "interface.ip_address_configured",
            result["errors"],
        )

    def test_virtual_interface_can_only_pass_explicit_diagnostic_mode(self):
        result = audit_host_preflight(
            "/sys/devices/virtual/net/hftdiagc",
            (1 << 12) | (1 << 13),
            frozen_thresholds(),
            carrier=1,
            operstate="up",
            speed_mbps=10000,
            driver="virtual",
            capture_driver="af-packet-ts",
            timestamp_capabilities=(
                "software-receive",
                "software-system-clock",
            ),
            allow_virtual_diagnostic=True,
        )

        self.assertTrue(result["accepted"])
        self.assertFalse(result["physical_nic_visible"])
        self.assertTrue(result["virtual_interface_visible"])
        self.assertTrue(result["virtual_diagnostic_allowed"])


if __name__ == "__main__":
    unittest.main()
