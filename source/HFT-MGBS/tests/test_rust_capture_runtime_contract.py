import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RustCaptureRuntimeContractTests(unittest.TestCase):
    def test_native_xdp_forces_zerocopy_and_generic_forces_copy(self):
        source = (ROOT / "rust/hft-capture/src/xdp_capture.rs").read_text(
            encoding="utf-8"
        )
        self.assertIn("xdp_sys::{XDP_COPY, XDP_ZEROCOPY}", source)
        self.assertIn("Self::Native => XDP_ZEROCOPY", source)
        self.assertIn("Self::Skb => XDP_COPY", source)
        self.assertIn("assert_ne!(HftXdpMode::Native.bind_flags(), 0)", source)
        self.assertIn(
            "assert_ne!(HftXdpMode::Native.bind_flags(), XDP_COPY)", source
        )

    def test_rust_decision_engine_is_pure_and_uses_shared_golden(self):
        source = (
            ROOT / "rust/hft-capture/src/capture_runtime_decision.rs"
        ).read_text(encoding="utf-8")
        self.assertIn("pub fn evaluate_runtime_decision(", source)
        self.assertIn("decision_is_non_mutating: true", source)
        self.assertIn("capture_runtime_current_golden_v1.json", source)
        self.assertIn("same_adapter_all_pf_rebind", source)
        self.assertIn("runtime_safety_failure_is_not_a_capture_backend_fallback_signal", source)
        self.assertIn("key_flow_failure_is_not_a_capture_backend_fallback_signal", source)
        for forbidden in (
            "std::process::Command",
            'Command::new("ip")',
            'Command::new("ethtool")',
            'Command::new("dpdk-devbind")',
            'File::create("/sys/',
        ):
            self.assertNotIn(forbidden, source)

    def test_rust_cli_has_same_exit_code_contract_and_no_pf_mutation(self):
        source = (
            ROOT / "rust/hft-capture/src/bin/capture_runtime_decision.rs"
        ).read_text(encoding="utf-8")
        self.assertIn("decision_exit_code", source)
        self.assertIn("std::process::exit(2)", source)
        self.assertNotIn("std::process::Command", source)
        self.assertNotIn("/sys/bus/pci", source)
        self.assertNotIn("dpdk-devbind", source)

    def test_existing_dependencies_are_reused(self):
        cargo = (ROOT / "rust/hft-capture/Cargo.toml").read_text(encoding="utf-8")
        self.assertIn('serde = { version = "1.0", features = ["derive"] }', cargo)
        self.assertIn('serde_json = "1.0"', cargo)
        self.assertNotIn("chrono =", cargo)
        self.assertNotIn("time =", cargo)


if __name__ == "__main__":
    unittest.main()
