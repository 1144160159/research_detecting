from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.preflight_dpdk_cpu_idle import (
    parse_cpu_list,
    parse_proc_stat,
    sibling_cpus,
    utilization,
)


class DpdkCpuPreflightTest(unittest.TestCase):
    def test_cpu_ranges_are_normalized_and_invalid_ranges_rejected(self):
        self.assertEqual(parse_cpu_list("3,1-2,2"), [1, 2, 3])
        with self.assertRaises(ValueError):
            parse_cpu_list("3-1")

    def test_proc_stat_and_utilization_include_iowait_as_idle(self):
        before = parse_proc_stat("cpu4 10 0 10 70 10 0 0 0 0 0\n")
        after = parse_proc_stat("cpu4 20 0 20 140 20 0 0 0 0 0\n")
        self.assertEqual(before[4], (100, 80))
        self.assertAlmostEqual(utilization(before[4], after[4]), 0.2)

    def test_missing_or_non_monotonic_counters_fail_closed(self):
        self.assertIsNone(utilization(None, (10, 5)))
        self.assertIsNone(utilization((10, 5), (9, 4)))

    def test_smt_siblings_are_read_from_sysfs_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = (
                root
                / "devices"
                / "system"
                / "cpu"
                / "cpu4"
                / "topology"
                / "thread_siblings_list"
            )
            path.parent.mkdir(parents=True)
            path.write_text("4,60\n", encoding="utf-8")
            self.assertEqual(sibling_cpus(4, root), [4, 60])


if __name__ == "__main__":
    unittest.main()
