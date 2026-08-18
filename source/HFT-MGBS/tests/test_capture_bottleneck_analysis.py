from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.analyze_capture_bottleneck import (
    analyze_capture_bottleneck,
    load_artifact,
    main,
)


ROOT = Path(__file__).resolve().parents[1]
HASH_A = "a" * 64
HASH_B = "b" * 64


def contract() -> dict:
    return json.loads(
        (ROOT / "configs" / "capture_bottleneck_decision_v1.json").read_text(
            encoding="utf-8"
        )
    )


def dpdk_result(tx: float = 2.57, rx: float = 2.569) -> dict:
    return {
        "schema_version": 5,
        "scope": "r0_dpdk_bnx2x_capture_only",
        "backend": "dpdk_bnx2x_single_queue",
        "candidate_id": "R0_DPDK_BNX2X_Q1_12.0_B256_RELEASE_V2",
        "frozen_thresholds_sha256": HASH_A,
        "target_mpps": 12.0,
        "queue_count": 1,
        "offered_packets": 38_547_638,
        "received_packets": 38_547_638,
        "offered_received_gap": 0,
        "observed_tx_mpps_min_1s": tx,
        "observed_rx_mpps_min_1s": rx,
        "capture_stats_delta": {"imissed": 0, "ierrors": 0, "rx_nombuf": 0},
        "replay_stats_delta": {"oerrors": 0},
        "end_to_end_latency_us": {
            "samples": 12_000,
            "p99": 522.37,
            "p999": 529.25,
        },
        "hard_gate_errors": ["tx_target_load", "rx_target_load", "end_to_end_p99"],
        "data_plane_qualified": False,
        "resource_gate_evaluated": False,
        "r0_capture_only_qualified": False,
        "full_pipeline_qualified": False,
        "final_pareto_ingestion_allowed": False,
    }


def dpdk_acceptance() -> dict:
    return {
        "schema_version": 1,
        "scope": "dpdk_release_gate_runner_acceptance",
        "receipt_semantics": "derived_from_preacceptance_sealed_evidence_v1",
        "standalone_receipt_trusted": False,
        "evidence_seal_excludes": ["acceptance.json", "acceptance.stdout.json"],
        "candidate_id": "R0_DPDK_BNX2X_Q1_12.0_B256_RELEASE_V2",
        "frozen_thresholds_sha256": HASH_A,
        "input_sha256": {"result": HASH_B, "evidence": "c" * 64},
        "status": {
            "original_exit_status": 10,
            "validator_exit_status": 10,
            "restore_status": 0,
            "evidence_status": 0,
            "base_hash_check_status": 0,
            "complete_hash_check_status": 0,
        },
        "termination_signal": "none",
        "data_resource_qualified": False,
        "restoration_verified": True,
        "evidence_complete_before_hash": True,
        "hash_checks_verified": True,
        "errors": ["tx_target_load", "rx_target_load", "end_to_end_p99"],
        "runner_qualified": False,
        "r0_capture_only_qualified": False,
        "full_pipeline_qualified": False,
        "final_pareto_ingestion_allowed": False,
    }


def tpacket(offered_mpps: float = 2.794217, capture_mpps: float = 2.790743) -> dict:
    per_device = [349277, 349277, 349277, 349277, 349277, 349277, 349277, 349278]
    assert sum(per_device) == 2_794_217
    return {
        "schema_version": 1,
        "scope": "tpacket_v3_breakthrough_r0_acceptance",
        "candidate_id": "B2_FIXED8_CLONE64_BURST8_QM8_IRQ",
        "pktgen_devices": 8,
        "offered_packets": 41_691_559,
        "offered_mpps_sum": offered_mpps,
        "per_device_pps": per_device,
        "synthetic_test_packets": 41_691_559,
        "offered_received_gap": 0,
        "rx_discards_delta": 0,
        "packet_socket_drops": 0,
        "packet_socket_freeze_queue_count": 0,
        "loss_accounting_exact": True,
        "synthetic_rx_min_full_epoch_mpps": capture_mpps,
        "p99_us": 93.0,
        "p999_us": 126.0,
        "host_cpu_fraction": 0.30,
        "capture_memory_fraction": 0.01,
        "generator_12mpps_gate_qualified": False,
        "capture_rate_12mpps_gate_qualified": False,
        "loss_gate_qualified": True,
        "latency_gate_qualified": True,
        "resource_gate_qualified": True,
        "irq_assignment_verified": True,
        "irq_affinity_stable": True,
        "irq_restoration_verified": True,
        "ring_restoration_verified": True,
        "coalesce_restoration_verified": True,
        "links_restored": True,
        "pktgen_module_unloaded": True,
        "runner_exit_status": 0,
        "restoration_verified": True,
        "r0_capture_only_qualified": False,
        "full_pipeline_qualified": False,
        "final_pareto_ingestion_allowed": False,
    }


def write_artifact(root: Path, name: str, value: dict, kind: str):
    path = root / name
    path.write_text(json.dumps(value, allow_nan=False) + "\n", encoding="utf-8")
    return load_artifact(path, kind)


class CaptureBottleneckAnalysisTests(unittest.TestCase):
    def analyze(self, *, dpdk=True, tpacket_value=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            contract_artifact = write_artifact(root, "contract.json", contract(), "decision_contract")
            pairs = []
            if dpdk:
                pairs.append(
                    (
                        write_artifact(root, "result.json", dpdk_result(), "dpdk_result"),
                        write_artifact(
                            root, "dpdk_acceptance.json", dpdk_acceptance(), "dpdk_acceptance"
                        ),
                    )
                )
            tpacket_artifacts = []
            if tpacket_value is not None:
                tpacket_artifacts.append(
                    write_artifact(root, "tpacket.json", tpacket_value, "tpacket_acceptance")
                )
            return analyze_capture_bottleneck(contract_artifact, pairs, tpacket_artifacts)

    def test_loss_free_subtarget_tpacket_is_generator_limited_but_target_unproven(self):
        result = self.analyze(dpdk=False, tpacket_value=tpacket())
        self.assertTrue(result["analysis_valid"])
        self.assertTrue(result["findings"]["generator_limited"])
        self.assertTrue(result["findings"]["target_unproven"])
        self.assertFalse(result["capture_target_qualified"])
        self.assertFalse(result["extrapolation_performed"])
        self.assertFalse(result["full_pipeline_qualified"])
        self.assertFalse(result["final_pareto_ingestion_allowed"])

    def test_12m_requested_single_queue_plateau_is_attributed_to_path(self):
        result = self.analyze(dpdk=True, tpacket_value=None)
        self.assertTrue(result["analysis_valid"])
        self.assertTrue(result["findings"]["single_queue_path_limited"])
        self.assertFalse(result["findings"]["generator_limited"])
        self.assertTrue(result["findings"]["target_unproven"])

    def test_offered_target_with_exact_drops_is_capture_limited(self):
        receipt = tpacket(offered_mpps=12.0, capture_mpps=11.8)
        receipt["per_device_pps"] = [1_500_000] * 8
        receipt["offered_packets"] = 180_000_000
        receipt["synthetic_test_packets"] = 179_999_000
        receipt["offered_received_gap"] = 1_000
        receipt["rx_discards_delta"] = 1_000
        receipt["loss_accounting_exact"] = True
        receipt["loss_gate_qualified"] = False
        receipt["generator_12mpps_gate_qualified"] = True
        receipt["capture_rate_12mpps_gate_qualified"] = False
        result = self.analyze(dpdk=False, tpacket_value=receipt)
        self.assertTrue(result["analysis_valid"])
        self.assertTrue(result["findings"]["capture_limited"])
        self.assertFalse(result["findings"]["generator_limited"])

    def test_nonfinite_json_and_counter_mismatch_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            contract_artifact = write_artifact(root, "contract.json", contract(), "decision_contract")
            invalid_path = root / "invalid.json"
            invalid_path.write_text('{"offered_mpps_sum": NaN}', encoding="utf-8")
            invalid = load_artifact(invalid_path, "tpacket_acceptance")
            result = analyze_capture_bottleneck(contract_artifact, [], [invalid])
            self.assertFalse(result["analysis_valid"])
            self.assertTrue(result["findings"]["target_unproven"])
            self.assertIn("no_eligible_observation", result["errors"])

        inconsistent = tpacket()
        inconsistent["offered_received_gap"] = 1
        result = self.analyze(dpdk=False, tpacket_value=inconsistent)
        self.assertFalse(result["analysis_valid"])
        self.assertTrue(result["findings"]["target_unproven"])

    def test_unrestored_receipt_cannot_attribute_or_qualify(self):
        receipt = tpacket()
        receipt["restoration_verified"] = False
        result = self.analyze(dpdk=False, tpacket_value=receipt)
        self.assertFalse(result["analysis_valid"])
        self.assertFalse(result["findings"]["generator_limited"])
        self.assertTrue(result["findings"]["target_unproven"])

    def test_expected_hash_is_optional_but_mismatch_fails_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "receipt.json"
            path.write_text(json.dumps(tpacket()) + "\n", encoding="utf-8")
            artifact = load_artifact(path, "tpacket_acceptance", "0" * 64)
            self.assertFalse(artifact["binding_qualified"])
            self.assertIn("sha256_mismatch", artifact["errors"])

    def test_cli_binds_paths_and_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            contract_path = root / "contract.json"
            receipt_path = root / "receipt.json"
            output_path = root / "analysis.json"
            contract_path.write_text(json.dumps(contract()) + "\n", encoding="utf-8")
            receipt_path.write_text(json.dumps(tpacket()) + "\n", encoding="utf-8")
            digest = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
            status = main(
                [
                    "--contract",
                    str(contract_path),
                    "--tpacket-acceptance",
                    str(receipt_path),
                    "--expected-sha256",
                    f"{receipt_path}={digest.upper()}",
                    "--output",
                    str(output_path),
                ]
            )
            result = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(status, 0)
            self.assertTrue(result["analysis_valid"])
            self.assertTrue(result["evidence_binding_qualified"])

    def test_config_contract_has_bounded_fail_closed_prohibitions(self):
        value = contract()
        self.assertEqual(value["target_mpps"], 12.0)
        self.assertIn(
            "never extrapolate a zero-loss sub-target observation to 12 Mpps",
            value["prohibitions"],
        )
        self.assertFalse(value["full_pipeline_qualified"])
        self.assertFalse(value["final_pareto_ingestion_allowed"])


if __name__ == "__main__":
    unittest.main()
