from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class LiveRunnerContractTest(unittest.TestCase):
    def test_runner_uses_local_rust_injector_and_fail_closed_preflight(self):
        script = (ROOT / "scripts" / "run_live_acceptance.sh").read_text(
            encoding="utf-8"
        )

        self.assertIn("preflight_live_host.py", script)
        self.assertIn('target/release/pcap_injector', script)
        self.assertIn("compose_live_evidence.py", script)
        self.assertIn("--max-duration-s", script)
        self.assertIn("capture and replay interfaces must be distinct", script)
        self.assertNotIn("tcpreplay", script)
        self.assertIn('status=preflight_failed', script)
        self.assertIn('status=${execution_status}', script)
        self.assertIn("virtual_link_live_diagnostic", script)
        self.assertIn("physical_link_live_diagnostic", script)
        self.assertIn("physical_nic_live_replay", script)
        self.assertIn("--minimum-speed-mbps", script)
        self.assertIn("--require-unmanaged", script)
        self.assertIn('if [[ "${composition_status}" != "0" ]]', script)

    def test_physical_link_diagnostic_is_bounded_and_non_production(self):
        script = (
            ROOT / "scripts" / "run_physical_link_diagnostic.sh"
        ).read_text(encoding="utf-8")
        thresholds = (
            ROOT / "configs" / "live_thresholds_physical_diagnostic.json"
        ).read_text(encoding="utf-8")

        self.assertIn("physical_link_live_diagnostic", script)
        self.assertIn("ens8f0", script)
        self.assertIn("ens8f1", script)
        self.assertIn("generic-receive-offload", script)
        self.assertIn("restore_capture_offloads", script)
        self.assertIn("temporary_gro_lro_off_restore_on_exit", script)
        self.assertIn("build_hft_xdp_ebpf.sh", (
            ROOT / "scripts" / "run_live_acceptance.sh"
        ).read_text(encoding="utf-8"))
        self.assertIn("--xdp-ebpf-object", (
            ROOT / "scripts" / "run_live_acceptance.sh"
        ).read_text(encoding="utf-8"))
        self.assertIn('"diagnostic_only": true', thresholds)
        self.assertIn(
            '"final_pareto_ingestion_allowed": false', thresholds
        )

    def test_virtual_diagnostic_is_isolated_and_non_production(self):
        script = (
            ROOT / "scripts" / "run_virtual_live_diagnostic.sh"
        ).read_text(encoding="utf-8")
        thresholds = (
            ROOT / "configs" / "live_thresholds_veth_diagnostic.json"
        ).read_text(encoding="utf-8")

        self.assertIn("ip link add", script)
        self.assertIn("type veth peer name", script)
        self.assertIn("virtual_link_live_diagnostic", script)
        self.assertNotIn("ens8f0", script)
        self.assertNotIn("ens8f1", script)
        self.assertIn('"diagnostic_only": true', thresholds)
        self.assertIn(
            '"final_pareto_ingestion_allowed": false', thresholds
        )

    def test_temporary_management_shadow_is_passive_and_bounded(self):
        script = (
            ROOT / "scripts" / "run_temporary_shadow_capture.sh"
        ).read_text(encoding="utf-8")
        profile = (
            ROOT / "configs" / "temporary_interface_ens9f0_shadow.json"
        ).read_text(encoding="utf-8")

        self.assertIn('ACK_MANAGEMENT_INTERFACE="${ACK_MANAGEMENT_INTERFACE:-0}"', script)
        self.assertIn("MAX_DURATION_S >= 1 && MAX_DURATION_S <= 60", script)
        self.assertIn("--max-duration-s", script)
        self.assertIn("shadow_b128_f1000", script)
        self.assertIn("shadow_b64_f500", script)
        self.assertIn("shadow_b32_f250", script)
        self.assertIn("final_pareto_ingestion_allowed=false", script)
        self.assertNotIn("pcap_injector", script)
        self.assertNotIn("--pcap", script)
        self.assertIn('"mode": "passive-capture-only"', profile)
        self.assertIn('"traffic_generation_allowed": false', profile)
        self.assertIn('"final_pareto_ingestion_allowed": false', profile)

        matrix = (
            ROOT / "scripts" / "run_temporary_shadow_matrix.sh"
        ).read_text(encoding="utf-8")
        self.assertIn("candidate_count=3", matrix)
        self.assertIn("repeat_count=${REPEATS}", matrix)
        self.assertIn("total_run_count=9", matrix)
        self.assertIn("traffic_generation_allowed=false", matrix)

    def test_runtime_candidate_runner_keeps_algorithm_frozen(self):
        script = (
            ROOT / "scripts" / "gpu_runtime_candidate.sh"
        ).read_text(encoding="utf-8")

        self.assertIn("runtime_only_frozen_A09", script)
        self.assertIn("--model-n-jobs 1", script)
        self.assertIn("--prediction-execution", script)
        self.assertIn("taskset -c", script)
        self.assertIn("refusing to stop an unverified runtime candidate", script)

    def test_production_gpu_runner_uses_selected_runtime(self):
        script = (
            ROOT / "scripts" / "start_gpu_service.sh"
        ).read_text(encoding="utf-8")

        self.assertIn('PREDICTION_EXECUTION="${PREDICTION_EXECUTION:-thread}"', script)
        self.assertIn('CPU_SET="${CPU_SET:-all}"', script)
        self.assertIn("--prediction-execution", script)
        self.assertIn("taskset -c", script)
        self.assertIn('RUNTIME_CANDIDATE="thread_all"', script)
        self.assertIn('"scope": "selected_runtime_" + runtime_candidate', script)
        self.assertIn("runtime_manifest.json", script)

    def test_rust_capture_has_graceful_duration_bound(self):
        path = ROOT / "rust" / "hft-capture" / "src" / "main.rs"
        if not path.exists():
            self.skipTest("Rust source is intentionally absent on Python node")
        source = path.read_text(encoding="utf-8")

        self.assertIn("max_duration_s: Option<u64>", source)
        self.assertIn("--max-duration-s must be positive", source)
        self.assertIn("started.elapsed() >= Duration::from_secs(limit)", source)

    def test_timestamp_capture_filters_local_outgoing_frames(self):
        path = (
            ROOT
            / "rust"
            / "hft-capture"
            / "src"
            / "kernel_af_packet.rs"
        )
        if not path.exists():
            self.skipTest("Rust source is intentionally absent on Python node")
        source = path.read_text(encoding="utf-8")

        self.assertIn("PACKET_IGNORE_OUTGOING", source)
        self.assertIn("libc::SOL_PACKET", source)
        self.assertIn("msg_name", source)
        self.assertIn("sll_pkttype", source)
        self.assertIn("is_ingress_packet_type", source)


if __name__ == "__main__":
    unittest.main()
