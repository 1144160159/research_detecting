import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_RUNNER = ROOT / "scripts" / "run_current_hardware_279_tpacket_fixed64_diagnostic.sh"
RUNNER = ROOT / "scripts" / "run_current_hardware_279_tpacket_fixed64_rxusecs12_diagnostic.sh"
BASE_CONFIG = ROOT / "configs" / "current_hardware_2_79_tpacket_fixed64_diagnostic.json"
CONFIG = ROOT / "configs" / "current_hardware_2_79_tpacket_fixed64_rxusecs12_diagnostic.json"

BASE_ID = "TPACKET_QM_FIXED64_FUSED_PARSE_MULTIFLOW_V2_FULL_PIPELINE_DIAGNOSTIC"
CANDIDATE_ID = "TPACKET_QM_FIXED64_FUSED_PARSE_RXUSECS12_MULTIFLOW_V2_FULL_PIPELINE_DIAGNOSTIC"
BINARY_SHA = "6112b2d6be166e7ce0a571727c98baff62524eee760838b2d683add19be8b7ca"


class Fixed64RxUsecs12ContractTest(unittest.TestCase):
    def test_config_changes_only_candidate_id_and_rx_usecs(self):
        base = json.loads(BASE_CONFIG.read_text(encoding="utf-8"))
        candidate = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(base.pop("candidate_id"), BASE_ID)
        self.assertEqual(candidate.pop("candidate_id"), CANDIDATE_ID)
        self.assertEqual(base["traffic"].pop("rx_usecs"), 24)
        self.assertEqual(candidate["traffic"].pop("rx_usecs"), 12)
        self.assertEqual(base, candidate)
        self.assertEqual(candidate["pipeline"]["binary_sha256"], BINARY_SHA)

    def test_runner_is_exact_single_variable_derivative(self):
        base = BASE_RUNNER.read_text(encoding="utf-8")
        candidate = RUNNER.read_text(encoding="utf-8")
        self.assertTrue(candidate.startswith("#!/usr/bin/env bash\n"))
        self.assertEqual(len(base.splitlines()), len(candidate.splitlines()))
        normalized = candidate.replace(
            "current_hardware_2_79_tpacket_fixed64_rxusecs12_diagnostic.json",
            "current_hardware_2_79_tpacket_fixed64_diagnostic.json",
        ).replace(CANDIDATE_ID, BASE_ID).replace(
            '("traffic", "rx_usecs"): 12', '("traffic", "rx_usecs"): 24'
        ).replace('rx-usecs 12', 'rx-usecs 24')
        self.assertEqual(base, normalized)
        self.assertIn("set -Eeuo pipefail", candidate)
        self.assertIn("sha256sum -c evidence.sha256", candidate)
        self.assertIn(BINARY_SHA, candidate)
        for token in ("cleanup() {", "compare_unchanged() {", "restoration_ledger.tsv",
                      "evidence.sha256.check.tmp", "nic_rx_discards_gate.json",
                      "fixed64 fast/fallback conservation failed", "exit 0"):
            self.assertIn(token, candidate)

    def test_config_and_runner_agree(self):
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
        runner = RUNNER.read_text(encoding="utf-8")
        self.assertEqual(cfg["traffic"]["rx_usecs"], 12)
        self.assertEqual(cfg["pipeline"]["binary_sha256"], BINARY_SHA)
        for token in (CANDIDATE_ID, '("traffic", "rx_usecs"): 12',
                      'ethtool -C "${capture_nic}" rx-usecs 12'):
            self.assertIn(token, runner)


if __name__ == "__main__":
    unittest.main()
