import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.summarize_interface_readiness import summarize


def record(interface, *, accepted=True, errors=None):
    return {
        "interface": interface,
        "accepted": accepted,
        "errors": errors or [],
        "physical_nic_visible": True,
        "carrier": 1,
        "operstate": "up",
        "speed_mbps": 10000,
        "driver": "ixgbe",
        "network_master": None,
        "has_ip_address": False,
        "carries_default_route": False,
    }


class InterfaceReadinessTest(unittest.TestCase):
    def _write(self, root, payload):
        path = root / f"{payload['interface']}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_two_clean_interfaces_form_one_final_pair(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = [
                self._write(root, record("ens1f0")),
                self._write(root, record("ens1f1")),
            ]

            result = summarize(paths, set())

        self.assertEqual(result["hardware_pair_count"], 1)
        self.assertEqual(result["full_preflight_pair_count"], 1)
        self.assertTrue(result["final_live_run_allowed"])

    def test_threshold_and_hardware_blockers_are_distinguished(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            threshold_only = record(
                "ens1f0",
                accepted=False,
                errors=["thresholds.not_frozen"],
            )
            no_carrier = record(
                "ens1f1",
                accepted=False,
                errors=["link.no_carrier", "thresholds.not_frozen"],
            )
            paths = [
                self._write(root, threshold_only),
                self._write(root, no_carrier),
            ]

            result = summarize(paths, set())

        self.assertEqual(result["hardware_eligible_interfaces"], ["ens1f0"])
        self.assertEqual(result["hardware_pair_count"], 0)
        self.assertEqual(result["full_preflight_pair_count"], 0)
        self.assertFalse(result["final_live_run_allowed"])

    def test_explicitly_excluded_interface_never_forms_pair(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = [
                self._write(root, record("ens8f0")),
                self._write(root, record("ens9f0")),
            ]

            result = summarize(paths, {"ens8f0"})

        self.assertEqual(result["hardware_eligible_interfaces"], ["ens9f0"])
        self.assertFalse(result["final_live_run_allowed"])


if __name__ == "__main__":
    unittest.main()
