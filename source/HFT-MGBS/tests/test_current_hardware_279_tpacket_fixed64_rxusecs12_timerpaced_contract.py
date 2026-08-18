import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_RUNNER = ROOT / "scripts" / "run_current_hardware_279_tpacket_fixed64_rxusecs12_ratep43750_diagnostic.sh"
RUNNER = ROOT / "scripts" / "run_current_hardware_279_tpacket_fixed64_rxusecs12_timerpaced_burst64_ratep5469_diagnostic.sh"
BASE_CONFIG = ROOT / "configs" / "current_hardware_2_79_tpacket_fixed64_rxusecs12_ratep43750_diagnostic.json"
CONFIG = ROOT / "configs" / "current_hardware_2_79_tpacket_fixed64_rxusecs12_timerpaced_burst64_ratep5469_diagnostic.json"

BASE_ID = "TPACKET_QM_FIXED64_FUSED_PARSE_RXUSECS12_RATEP43750_MULTIFLOW_V2_FULL_PIPELINE_DIAGNOSTIC"
CANDIDATE_ID = "TPACKET_QM_FIXED64_FUSED_PARSE_RXUSECS12_TIMERPACED_BURST64_CLONE8_RATEP5469_MULTIFLOW_V2_FULL_PIPELINE_DIAGNOSTIC"
BINARY_SHA = "6112b2d6be166e7ce0a571727c98baff62524eee760838b2d683add19be8b7ca"


class Fixed64RxUsecs12TimerPacedContractTest(unittest.TestCase):
    def test_config_changes_only_approved_timer_pacing_contract(self):
        base = json.loads(BASE_CONFIG.read_text(encoding="utf-8"))
        candidate = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(base.pop("candidate_id"), BASE_ID)
        self.assertEqual(candidate.pop("candidate_id"), CANDIDATE_ID)

        approved_keys = (
            "clone_skb", "burst", "ratep_per_burst_call", "expected_delay_ns",
            "expected_effective_pps_per_queue_min",
            "expected_effective_pps_per_queue_max",
            "expected_effective_pps_aggregate_min",
        )
        baseline_contract = {key: base["traffic"].pop(key) for key in approved_keys}
        candidate_contract = {key: candidate["traffic"].pop(key) for key in approved_keys}
        self.assertEqual(baseline_contract, {
            "clone_skb": 64,
            "burst": 8,
            "ratep_per_burst_call": 43750,
            "expected_delay_ns": 22857,
            "expected_effective_pps_per_queue_min": 345000,
            "expected_effective_pps_per_queue_max": 355000,
            "expected_effective_pps_aggregate_min": 2800000,
        })
        self.assertEqual(candidate_contract, {
            "clone_skb": 8,
            "burst": 64,
            "ratep_per_burst_call": 5469,
            "expected_delay_ns": 182848,
            "expected_effective_pps_per_queue_min": 345000,
            "expected_effective_pps_per_queue_max": 355000,
            "expected_effective_pps_aggregate_min": 2790000,
        })
        self.assertEqual(base, candidate)
        self.assertEqual(json.loads(CONFIG.read_text())["pipeline"]["binary_sha256"], BINARY_SHA)

    def test_linux_510_timer_pacing_and_header_group_contract(self):
        runner = RUNNER.read_text(encoding="utf-8")
        for token in (
            'pgset "${control}" clone_skb 8',
            'pgset "${control}" burst 64',
            'pgset "${control}" ratep 5469',
            'delay=floor(1e9/5469)=182848 ns',
            'clone_skb=8 preserves the prior 512-packet header group (8 * 64)',
            '"clone_skb": r"\\bclone_skb:\\s*8\\b"',
            '"burst": r"^\\s*burst:\\s*64\\s*$"',
            '"ratep_delay": r"\\bdelay:\\s*182848\\b"',
        ):
            self.assertIn(token, runner)
        self.assertNotIn('pgset "${control}" ratep 5600', runner)
        self.assertNotIn('pgset "${control}" ratep 43750', runner)
        self.assertEqual(5469 * 64 * 8, 2_800_128)
        self.assertGreater(182848, 100000)

    def test_one_shot_post_run_gates_are_fail_closed(self):
        runner = RUNNER.read_text(encoding="utf-8")
        for token in (
            "pktgen_rate_gate.json",
            "345000 <= rate <= 355000",
            'not queue_failures and sum(rates) >= 2790000',
            '"full_epoch_packet_counts": full_epoch_counts',
            '"full_epoch_below_279_mpps": full_epoch_below_threshold',
            "and not full_epoch_below_threshold",
            "minimum >= 2.79",
            'v.get("full_epoch_windows", 0) >= 15',
            '"packet_socket_drops"',
            '"packet_socket_freeze_queue_count"',
            '"feature_queue_drops"',
            '"key_feature_queue_drops"',
            '"parse_rejected"',
            '"capture_lossless"',
            '"internal_delivery_lossless"',
            '"all_workers_error_free"',
            "nic_rx_discards_gate.json",
            "evidence.sha256.check",
            "restoration_verified",
            BINARY_SHA,
        ):
            self.assertIn(token, runner)
        self.assertEqual(runner.count("echo start >/proc/net/pktgen/pgctrl"), 1)
        self.assertNotIn("retry", runner.lower())

    def test_runner_is_mechanical_derivative_with_only_approved_hunks(self):
        expected = BASE_RUNNER.read_text(encoding="utf-8")

        def swap(old, new, count=1):
            nonlocal expected
            self.assertEqual(expected.count(old), count, msg=f"baseline drift for: {old[:80]!r}")
            expected = expected.replace(old, new)

        swap(
            "current_hardware_2_79_tpacket_fixed64_rxusecs12_ratep43750_diagnostic.json",
            "current_hardware_2_79_tpacket_fixed64_rxusecs12_timerpaced_burst64_ratep5469_diagnostic.json",
        )
        swap(BASE_ID, CANDIDATE_ID, 2)
        swap('    ("traffic", "clone_skb"): 64,', '    ("traffic", "clone_skb"): 8,')
        swap('    ("traffic", "burst"): 8,', '    ("traffic", "burst"): 64,')
        swap('    ("traffic", "ratep_per_burst_call"): 43750,', '    ("traffic", "ratep_per_burst_call"): 5469,')
        swap('    ("traffic", "expected_delay_ns"): 22857,', '    ("traffic", "expected_delay_ns"): 182848,')
        swap('    ("traffic", "expected_effective_pps_aggregate_min"): 2800000,',
             '    ("traffic", "expected_effective_pps_aggregate_min"): 2790000,')
        swap('  pgset "${control}" clone_skb 64', '  pgset "${control}" clone_skb 8')
        swap('  pgset "${control}" burst 8', '  pgset "${control}" burst 64')
        swap(
            "  # Linux 5.10 pktgen ratep controls burst calls, not individual packets:\n"
            "  # delay=floor(1e9/43750)=22857 ns and burst=8 targets about 350 kpps/queue.\n"
            '  pgset "${control}" ratep 43750',
            "  # Linux 5.10 pktgen ratep controls burst calls, not individual packets.\n"
            "  # delay=floor(1e9/5469)=182848 ns and burst=64 targets 350016 pps/queue.\n"
            "  # clone_skb=8 preserves the prior 512-packet header group (8 * 64).\n"
            '  pgset "${control}" ratep 5469',
        )
        swap(
            '        "clone_skb": r"\\bclone_skb:\\s*64\\b",\n'
            '        "ratep_delay": r"\\bdelay:\\s*22857\\b",',
            '        "clone_skb": r"\\bclone_skb:\\s*8\\b",\n'
            '        "burst": r"^\\s*burst:\\s*64\\s*$",\n'
            '        "ratep_delay": r"\\bdelay:\\s*182848\\b",',
        )
        swap(
            '        "delay": r"\\bdelay:\\s*22857\\b",\n'
            '        "clone_skb": r"\\bclone_skb:\\s*64\\b",\n'
            '        "burst": r"^\\s*burst:\\s*8\\s*$",',
            '        "delay": r"\\bdelay:\\s*182848\\b",\n'
            '        "clone_skb": r"\\bclone_skb:\\s*8\\b",\n'
            '        "burst": r"^\\s*burst:\\s*64\\s*$",',
        )
        swap('    "ratep_per_burst_call": 43750,', '    "ratep_per_burst_call": 5469,')
        swap('    "expected_delay_ns": 22857,', '    "expected_delay_ns": 182848,')
        swap('    "aggregate_minimum_pps": 2800000,', '    "aggregate_minimum_pps": 2790000,')
        swap('    "passed": not queue_failures and sum(rates) >= 2800000,',
             '    "passed": not queue_failures and sum(rates) >= 2790000,')
        swap(
            'minimum = v.get("min_full_epoch_mpps")\ncapacity_gate = {',
            'minimum = v.get("min_full_epoch_mpps")\n'
            'epoch_counts = v.get("epoch_second_counts")\n'
            'if not isinstance(epoch_counts, dict) or len(epoch_counts) < 3:\n'
            '    raise SystemExit("per-second receive evidence is missing")\n'
            'ordered_epoch_counts = [epoch_counts[key] for key in sorted(epoch_counts, key=int)]\n'
            'if any(not isinstance(count, int) or isinstance(count, bool) or count < 0\n'
            '       for count in ordered_epoch_counts):\n'
            '    raise SystemExit("per-second receive evidence has an invalid count")\n'
            'full_epoch_counts = ordered_epoch_counts[1:-1]\n'
            'if len(full_epoch_counts) != v.get("full_epoch_windows"):\n'
            '    raise SystemExit("full-window count does not match per-second receive evidence")\n'
            'full_epoch_below_threshold = [\n'
            '    count for count in full_epoch_counts if count < 2790000\n'
            ']\n'
            'capacity_gate = {',
        )
        swap(
            '    "full_epoch_windows": v.get("full_epoch_windows"),',
            '    "full_epoch_windows": v.get("full_epoch_windows"),\n'
            '    "full_epoch_packet_counts": full_epoch_counts,\n'
            '    "full_epoch_below_279_mpps": full_epoch_below_threshold,',
        )
        swap(
            '    and minimum >= 2.79 and v.get("full_epoch_windows", 0) >= 15',
            '    and minimum >= 2.79 and v.get("full_epoch_windows", 0) >= 15\n'
            '    and not full_epoch_below_threshold',
        )
        self.assertEqual(expected, RUNNER.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
