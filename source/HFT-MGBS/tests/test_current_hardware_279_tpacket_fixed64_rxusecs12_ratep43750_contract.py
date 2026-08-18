import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_RUNNER = ROOT / "scripts" / "run_current_hardware_279_tpacket_fixed64_rxusecs12_diagnostic.sh"
RUNNER = ROOT / "scripts" / "run_current_hardware_279_tpacket_fixed64_rxusecs12_ratep43750_diagnostic.sh"
BASE_CONFIG = ROOT / "configs" / "current_hardware_2_79_tpacket_fixed64_rxusecs12_diagnostic.json"
CONFIG = ROOT / "configs" / "current_hardware_2_79_tpacket_fixed64_rxusecs12_ratep43750_diagnostic.json"

BASE_ID = "TPACKET_QM_FIXED64_FUSED_PARSE_RXUSECS12_MULTIFLOW_V2_FULL_PIPELINE_DIAGNOSTIC"
CANDIDATE_ID = "TPACKET_QM_FIXED64_FUSED_PARSE_RXUSECS12_RATEP43750_MULTIFLOW_V2_FULL_PIPELINE_DIAGNOSTIC"
BINARY_SHA = "6112b2d6be166e7ce0a571727c98baff62524eee760838b2d683add19be8b7ca"


class Fixed64RxUsecs12Ratep43750ContractTest(unittest.TestCase):
    def test_config_changes_only_rate_limit_identity_and_observation_gates(self):
        base = json.loads(BASE_CONFIG.read_text(encoding="utf-8"))
        candidate = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(base.pop("candidate_id"), BASE_ID)
        self.assertEqual(candidate.pop("candidate_id"), CANDIDATE_ID)
        rate_contract = {
            "ratep_per_burst_call": 43750,
            "expected_delay_ns": 22857,
            "expected_effective_pps_per_queue_min": 345000,
            "expected_effective_pps_per_queue_max": 355000,
            "expected_effective_pps_aggregate_min": 2800000,
        }
        for key, expected in rate_contract.items():
            self.assertEqual(candidate["traffic"].pop(key), expected)
        self.assertEqual(candidate.pop("runtime_hard_gates"), {
            **base["runtime_hard_gates"],
            "minimum_full_epoch_mpps": 2.79,
            "packet_socket_drops_max": 0,
            "packet_socket_freeze_queue_count_max": 0,
            "feature_queue_drops_max": 0,
            "key_feature_queue_drops_max": 0,
            "parse_rejected_max": 0,
            "require_capture_lossless": True,
            "require_internal_delivery_lossless": True,
            "require_all_workers_error_free": True,
        })
        base.pop("runtime_hard_gates")
        self.assertEqual(base, candidate)
        self.assertEqual(json.loads(CONFIG.read_text())["pipeline"]["binary_sha256"], BINARY_SHA)

    def test_ratep_uses_burst_call_semantics_not_per_packet_value(self):
        runner = RUNNER.read_text(encoding="utf-8")
        self.assertIn('pgset "${control}" ratep 43750', runner)
        self.assertNotIn("ratep 350000", runner)
        self.assertIn(r'"ratep_delay": r"\bdelay:\s*22857\b"', runner)
        self.assertIn('"burst": r"^\\s*burst:\\s*8\\s*$"', runner)
        self.assertIn('"clone_skb": r"\\bclone_skb:\\s*64\\b"', runner)

    def test_post_run_gates_rate_and_every_available_loss_counter(self):
        runner = RUNNER.read_text(encoding="utf-8")
        for token in (
            "pktgen_rate_gate.json", "345000 <= rate <= 355000",
            '"queues_outside_range": queue_failures',
            'not queue_failures and sum(rates) >= 2800000',
            "capacity_capture_gate.json",
            'minimum >= 2.79',
            '"packet_socket_drops"', '"packet_socket_freeze_queue_count"',
            '"feature_queue_drops"', '"key_feature_queue_drops"',
            '"parse_rejected"', '"capture_lossless"',
            '"internal_delivery_lossless"', '"all_workers_error_free"',
            "nic_rx_discards_gate.json", BINARY_SHA,
        ):
            self.assertIn(token, runner)
        self.assertLess(runner.index('"queues_outside_range": queue_failures'),
                        runner.index('raise SystemExit("pktgen rate gate failed;'))

    def test_derivative_has_only_whitelisted_hunks(self):
        base = BASE_RUNNER.read_text(encoding="utf-8")
        candidate = RUNNER.read_text(encoding="utf-8")
        normalized = candidate.replace(
            "current_hardware_2_79_tpacket_fixed64_rxusecs12_ratep43750_diagnostic.json",
            "current_hardware_2_79_tpacket_fixed64_rxusecs12_diagnostic.json",
        ).replace(CANDIDATE_ID, BASE_ID)

        removable_lines = (
            '    ("traffic", "ratep_per_burst_call"):',
            '    ("traffic", "expected_delay_ns"):',
            '    ("traffic", "expected_effective_pps_per_queue_min"):',
            '    ("traffic", "expected_effective_pps_per_queue_max"):',
            '    ("traffic", "expected_effective_pps_aggregate_min"):',
            '    ("runtime_hard_gates", "minimum_full_epoch_mpps"):',
            '    ("runtime_hard_gates", "packet_socket_drops_max"):',
            '    ("runtime_hard_gates", "packet_socket_freeze_queue_count_max"):',
            '    ("runtime_hard_gates", "feature_queue_drops_max"):',
            '    ("runtime_hard_gates", "key_feature_queue_drops_max"):',
            '    ("runtime_hard_gates", "parse_rejected_max"):',
            '    ("runtime_hard_gates", "require_capture_lossless"):',
            '    ("runtime_hard_gates", "require_internal_delivery_lossless"):',
            '    ("runtime_hard_gates", "require_all_workers_error_free"):',
            '        "ratep_delay":',
        )
        normalized = "\n".join(
            line for line in normalized.splitlines()
            if not line.startswith(removable_lines)
        ) + "\n"
        normalized = normalized.replace(
            "  # Linux 5.10 pktgen ratep controls burst calls, not individual packets:\n"
            "  # delay=floor(1e9/43750)=22857 ns and burst=8 targets about 350 kpps/queue.\n"
            "  pgset \"${control}\" ratep 43750\n", ""
        )
        normalized = re.sub(
            r'\npython3 - "\$\{evidence_dir\}" <<\'PY\'\nimport json, pathlib, re, sys\n'
            r'.*?\nPY\n(?=cp -- /proc/net/pktgen/pgctrl)',
            "\n", normalized, flags=re.DOTALL,
        )
        normalized = normalized.replace(
            'done\n\ncp -- /proc/net/pktgen/pgctrl',
            'done\ncp -- /proc/net/pktgen/pgctrl',
        )
        normalized = re.sub(
            r'minimum = v\.get\("min_full_epoch_mpps"\)\n.*?\n'
            r'    raise SystemExit\("capacity capture gate failed"\)\n',
            "", normalized, flags=re.DOTALL,
        )
        self.assertEqual(base, normalized)


if __name__ == "__main__":
    unittest.main()
