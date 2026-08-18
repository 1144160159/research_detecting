import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERIC_RUNNER = ROOT / "scripts" / "run_current_hardware_279_tpacket_diagnostic.sh"
NATIVE_RUNNER = ROOT / "scripts" / "run_current_hardware_279_tpacket_native_cpu_diagnostic.sh"
GENERIC_CONFIG = ROOT / "configs" / "current_hardware_2_79_tpacket_diagnostic_v1.json"
NATIVE_CONFIG = ROOT / "configs" / "current_hardware_2_79_tpacket_native_cpu_diagnostic.json"

GENERIC_ID = "TPACKET_QM_RUNTIME_AFFINITY_MULTIFLOW_V2_FULL_PIPELINE_DIAGNOSTIC"
NATIVE_ID = "TPACKET_QM_NATIVE_CPU_MULTIFLOW_V2_FULL_PIPELINE_DIAGNOSTIC"
GENERIC_BINARY_SHA = "499b0b8e9abc14877d85fa0009489ffdf2e7f8d9527986e6cd1993008c2589fe"
NATIVE_BINARY_SHA = "8ddab139045b9e9a9b1a9fbfa89836869aedef67c8fb95ffbfb2d7ff2cff0623"
GENERIC_RUNNER_SHA = "826ceb8fb91158a391ed2c076ad6c9d9dbdcf59d6d5fb5b470c2efb6fde85c59"
GENERIC_CONFIG_SHA = "7e7df0e71d94236e9188b39a446a983cff0205e98e13e1ed20610d8527d6cdd6"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class NativeCpuVariantContractTest(unittest.TestCase):
    def test_generic_chain_is_byte_identical(self):
        self.assertEqual(sha256(GENERIC_RUNNER), GENERIC_RUNNER_SHA)
        self.assertEqual(sha256(GENERIC_CONFIG), GENERIC_CONFIG_SHA)

    def test_native_config_changes_only_identity_and_binary_artifact(self):
        generic = json.loads(GENERIC_CONFIG.read_text(encoding="utf-8"))
        native = json.loads(NATIVE_CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(generic["candidate_id"], GENERIC_ID)
        self.assertEqual(native["candidate_id"], NATIVE_ID)
        self.assertEqual(generic["traffic"], native["traffic"])
        self.assertEqual(generic["interfaces"], native["interfaces"])
        for key in ("preflight", "runtime_hard_gates", "authorization", "evidence", "qualification"):
            self.assertEqual(generic[key], native[key])
        generic_pipeline = dict(generic["pipeline"])
        native_pipeline = dict(native["pipeline"])
        self.assertEqual(generic_pipeline.pop("binary_name"), "tpacket_v3_full_pipeline")
        self.assertEqual(native_pipeline.pop("binary_name"), "tpacket_v3_full_pipeline_native_cpu")
        self.assertEqual(generic_pipeline.pop("binary_sha256"), GENERIC_BINARY_SHA)
        self.assertEqual(native_pipeline.pop("binary_sha256"), NATIVE_BINARY_SHA)
        self.assertEqual(generic_pipeline, native_pipeline)

    def test_runner_is_auditable_exact_derivative(self):
        expected = GENERIC_RUNNER.read_text(encoding="utf-8")
        expected = expected.replace(
            "/home/wangwt/phase_2/code/HFT-MGBS/configs/current_hardware_2_79_tpacket_diagnostic_v1.json",
            "/home/wangwt/phase_2/code/HFT-MGBS/configs/current_hardware_2_79_tpacket_native_cpu_diagnostic.json",
        )
        expected = expected.replace(
            "/home/wangwt/phase_2/code/HFT-MGBS/rust/hft-capture/target/release/tpacket_v3_full_pipeline",
            "/home/wangwt/phase_2/code/HFT-MGBS/rust/hft-capture/target/release/tpacket_v3_full_pipeline_native_cpu",
        )
        expected = expected.replace(GENERIC_ID, NATIVE_ID)
        expected = expected.replace(GENERIC_BINARY_SHA, NATIVE_BINARY_SHA)
        expected = expected.replace(
            '[[ "$(basename -- "${exe}")" == tpacket_v3_full_pipeline ]] || continue',
            '[[ "$(basename -- "${exe}")" == tpacket_v3_full_pipeline* ]] || continue',
        )
        self.assertEqual(NATIVE_RUNNER.read_text(encoding="utf-8"), expected)

    def test_fail_closed_contract_is_retained(self):
        script = NATIVE_RUNNER.read_text(encoding="utf-8")
        for token in (
            "set -Eeuo pipefail",
            "HFT_CURRENT_279_MUTATION_AUTHORIZATION",
            "HFT_CURRENT_279_RESTORATION_AUTHORIZATION",
            "HFT_CURRENT_279_IRQBALANCE_STOP_START_AUTHORIZATION",
            "HFT_CURRENT_279_RUNNER_SHA256",
            "HFT_CURRENT_279_CONFIG_SHA256",
            "HFT_CURRENT_279_BINARY_SHA256",
            "restoration_ledger.tsv",
        ):
            self.assertIn(token, script)
        self.assertIn('== tpacket_v3_full_pipeline*', script)


if __name__ == "__main__":
    unittest.main()
