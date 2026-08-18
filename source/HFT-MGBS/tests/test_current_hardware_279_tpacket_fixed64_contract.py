import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERIC_RUNNER = ROOT / "scripts" / "run_current_hardware_279_tpacket_diagnostic.sh"
FIXED_RUNNER = ROOT / "scripts" / "run_current_hardware_279_tpacket_fixed64_diagnostic.sh"
GENERIC_CONFIG = ROOT / "configs" / "current_hardware_2_79_tpacket_diagnostic_v1.json"
FIXED_CONFIG = ROOT / "configs" / "current_hardware_2_79_tpacket_fixed64_diagnostic.json"
MODULE = ROOT / "rust" / "hft-capture" / "src" / "fixed_profile_parse.rs"
BIN_SOURCE = ROOT / "rust" / "hft-capture" / "src" / "bin" / "tpacket_v3_full_pipeline.rs"

GENERIC_ID = "TPACKET_QM_RUNTIME_AFFINITY_MULTIFLOW_V2_FULL_PIPELINE_DIAGNOSTIC"
FIXED_ID = "TPACKET_QM_FIXED64_FUSED_PARSE_MULTIFLOW_V2_FULL_PIPELINE_DIAGNOSTIC"
GENERIC_SHA = "499b0b8e9abc14877d85fa0009489ffdf2e7f8d9527986e6cd1993008c2589fe"
FIXED_SHA = "6112b2d6be166e7ce0a571727c98baff62524eee760838b2d683add19be8b7ca"


class Fixed64CandidateContractTest(unittest.TestCase):
    def test_config_is_single_variable(self):
        generic = json.loads(GENERIC_CONFIG.read_text(encoding="utf-8"))
        fixed = json.loads(FIXED_CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(generic["candidate_id"], GENERIC_ID)
        self.assertEqual(fixed["candidate_id"], FIXED_ID)
        for key in ("interfaces", "traffic", "preflight", "runtime_hard_gates", "authorization", "evidence", "qualification"):
            self.assertEqual(generic[key], fixed[key])
        gp, fp = dict(generic["pipeline"]), dict(fixed["pipeline"])
        self.assertEqual(gp.pop("binary_sha256"), GENERIC_SHA)
        self.assertEqual(fp.pop("binary_sha256"), FIXED_SHA)
        self.assertEqual(gp.pop("binary_name"), "tpacket_v3_full_pipeline")
        self.assertEqual(fp.pop("binary_name"), "tpacket_v3_full_pipeline_fixed64")
        self.assertEqual(gp, fp)

    def test_runner_retains_fail_closed_gates_and_broad_competitor_match(self):
        script = FIXED_RUNNER.read_text(encoding="utf-8")
        for token in ("set -Eeuo pipefail", FIXED_ID, FIXED_SHA,
                      "HFT_CURRENT_279_MUTATION_AUTHORIZATION",
                      "HFT_CURRENT_279_RESTORATION_AUTHORIZATION",
                      "HFT_CURRENT_279_IRQBALANCE_STOP_START_AUTHORIZATION",
                      "restoration_ledger.tsv", "sha256sum -c evidence.sha256"):
            self.assertIn(token, script)
        self.assertIn('== tpacket_v3_full_pipeline*', script)

    def test_parser_has_strict_fallback_oracles_and_runtime_observability(self):
        module = MODULE.read_text(encoding="utf-8")
        source = BIN_SOURCE.read_text(encoding="utf-8")
        for token in ("PacketParser::parse", "1..=145", "dst[33] = 146",
                      "fixed_profile_parser_matches_general_parser_field_by_field",
                      "every_profile_invariant_violation_uses_general_fallback",
                      "fast_parse_plus_flow_matches_general_parse_plus_flow_38_features_bitwise",
                      "to_bits()"):
            self.assertIn(token, module)
        for token in ("parse_profile_or_fallback", "fixed_profile_fast_parsed",
                      "fixed_profile_general_fallback",
                      "deterministic_multiflow_v2_fixed64_ipv4_udp_strict_v1"):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
