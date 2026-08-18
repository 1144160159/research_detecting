from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.compose_dpdk_run_acceptance import compose_acceptance, main


HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
HASH_D = "d" * 64


def data_resource_acceptance():
    return {
        "schema_version": 1,
        "scope": "dpdk_release_gate_acceptance",
        "candidate_id": "R0_DPDK_Q1_B128_RELEASE_V2",
        "qualification_mode": "release_gate_v2",
        "frozen_thresholds_sha256": HASH_A,
        "performance_gate_frozen": True,
        "resource_gate_frozen": True,
        "errors": [],
        "data_resource_qualified": True,
        "runner_qualified": False,
        "r0_capture_only_qualified": False,
        "full_pipeline_qualified": False,
        "final_pareto_ingestion_allowed": False,
    }


def evidence_inventory():
    return {
        "schema_version": 1,
        "required": ["result.json", "restoration_ledger.json"],
        "present": ["result.json", "restoration_ledger.json"],
        "missing": [],
        "empty_required": [],
        "restoration_verified": True,
        "evidence_complete_before_hash": True,
    }


def compose(**overrides):
    arguments = {
        "data_resource_acceptance_sha256": HASH_A,
        "evidence_inventory_sha256": HASH_B,
        "base_hash_evidence_sha256": HASH_C,
        "complete_hash_evidence_sha256": HASH_D,
        "original_exit_status": 0,
        "validator_exit_status": 0,
        "restore_status": 0,
        "restoration_verified": True,
        "evidence_status": 0,
        "base_hash_check_status": 0,
        "complete_hash_check_status": 0,
        "termination_signal": "none",
    }
    arguments.update(overrides)
    return compose_acceptance(
        data_resource_acceptance(),
        evidence_inventory(),
        **arguments,
    )


class DpdkAcceptanceComposerTest(unittest.TestCase):
    def test_all_independent_gates_are_required_for_runner_qualification(self):
        acceptance = compose()
        self.assertEqual(acceptance["errors"], [])
        self.assertTrue(acceptance["runner_qualified"])
        self.assertTrue(acceptance["r0_capture_only_qualified"])
        self.assertTrue(acceptance["data_resource_qualified"])
        self.assertTrue(acceptance["restoration_verified"])
        self.assertTrue(acceptance["evidence_complete_before_hash"])
        self.assertTrue(acceptance["hash_checks_verified"])
        self.assertFalse(acceptance["standalone_receipt_trusted"])
        self.assertEqual(
            acceptance["receipt_semantics"],
            "derived_from_preacceptance_sealed_evidence_v1",
        )
        self.assertEqual(
            acceptance["evidence_seal_excludes"],
            ["acceptance.json", "acceptance.stdout.json"],
        )
        self.assertFalse(acceptance["full_pipeline_qualified"])
        self.assertFalse(acceptance["final_pareto_ingestion_allowed"])

    def test_every_nonzero_status_and_signal_fail_closed(self):
        acceptance = compose(
            original_exit_status=1,
            validator_exit_status=10,
            restore_status=15,
            evidence_status=16,
            base_hash_check_status=1,
            complete_hash_check_status=1,
            termination_signal="TERM",
        )
        for error in (
            "original_exit_status_nonzero",
            "validator_exit_status_nonzero",
            "restore_status_nonzero",
            "evidence_status_nonzero",
            "base_hash_check_status_nonzero",
            "complete_hash_check_status_nonzero",
            "termination_signal_present",
        ):
            self.assertIn(error, acceptance["errors"])
        self.assertFalse(acceptance["runner_qualified"])
        self.assertFalse(acceptance["r0_capture_only_qualified"])

    def test_malformed_types_and_missing_hashes_fail_closed(self):
        acceptance = compose(
            original_exit_status=True,
            restoration_verified="true",
            data_resource_acceptance_sha256=None,
            base_hash_evidence_sha256="not-a-hash",
        )
        self.assertIn("original_exit_status_type", acceptance["errors"])
        self.assertIn("restoration_verified_type", acceptance["errors"])
        self.assertIn(
            "data_resource_acceptance_sha256", acceptance["errors"]
        )
        self.assertIn(
            "evidence_sha256_base_check_sha256", acceptance["errors"]
        )
        self.assertFalse(acceptance["runner_qualified"])

    def test_inconsistent_data_and_inventory_fail_closed(self):
        data = data_resource_acceptance()
        data["errors"] = ["latency_gate"]
        inventory = evidence_inventory()
        inventory["missing"] = ["result.json"]
        acceptance = compose_acceptance(
            data,
            inventory,
            data_resource_acceptance_sha256=HASH_A,
            evidence_inventory_sha256=HASH_B,
            base_hash_evidence_sha256=HASH_C,
            complete_hash_evidence_sha256=HASH_D,
            original_exit_status=0,
            validator_exit_status=0,
            restore_status=0,
            restoration_verified=True,
            evidence_status=0,
            base_hash_check_status=0,
            complete_hash_check_status=0,
            termination_signal="none",
        )
        self.assertIn(
            "data_resource_acceptance_errors", acceptance["errors"]
        )
        self.assertIn("evidence_inventory_incomplete", acceptance["errors"])
        self.assertFalse(acceptance["data_resource_qualified"])
        self.assertFalse(acceptance["evidence_complete_before_hash"])
        self.assertFalse(acceptance["runner_qualified"])

    def test_cli_binds_file_hashes_and_accepts_raw_complete_hash(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            data_path = root / "data.json"
            inventory_path = root / "inventory.json"
            base_path = root / "base_check.txt"
            output_path = root / "acceptance.json"
            data_path.write_text(
                json.dumps(data_resource_acceptance()) + "\n",
                encoding="utf-8",
            )
            inventory_path.write_text(
                json.dumps(evidence_inventory()) + "\n",
                encoding="utf-8",
            )
            base_path.write_text("all base hashes OK\n", encoding="utf-8")

            exit_status = main(
                [
                    "--data-resource-acceptance",
                    str(data_path),
                    "--evidence-inventory",
                    str(inventory_path),
                    "--original-exit-status",
                    "0",
                    "--validator-exit-status",
                    "0",
                    "--restore-status",
                    "0",
                    "--restoration-verified",
                    "true",
                    "--evidence-status",
                    "0",
                    "--base-hash-check-status",
                    "0",
                    "--complete-hash-check-status",
                    "0",
                    "--termination-signal",
                    "none",
                    "--base-hash-evidence",
                    str(base_path),
                    "--complete-hash-evidence",
                    HASH_D.upper(),
                    "--output",
                    str(output_path),
                ]
            )
            acceptance = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(exit_status, 0)
            self.assertTrue(acceptance["runner_qualified"])
            self.assertEqual(
                acceptance["input_sha256"]["data_resource_acceptance"],
                hashlib.sha256(data_path.read_bytes()).hexdigest(),
            )
            self.assertEqual(
                acceptance["input_sha256"]["evidence_inventory"],
                hashlib.sha256(inventory_path.read_bytes()).hexdigest(),
            )
            self.assertEqual(
                acceptance["input_sha256"]["evidence_sha256_base_check"],
                hashlib.sha256(base_path.read_bytes()).hexdigest(),
            )
            self.assertEqual(
                acceptance["input_sha256"][
                    "evidence_sha256_complete_check"
                ],
                HASH_D,
            )
            self.assertEqual(
                acceptance["hash_evidence_source"],
                {
                    "evidence_sha256_base_check": "file",
                    "evidence_sha256_complete_check": "provided_sha256",
                },
            )

    def test_cli_writes_fail_closed_output_for_bad_inputs(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            bad_data = root / "bad.json"
            output_path = root / "acceptance.json"
            bad_data.write_text("{", encoding="utf-8")
            exit_status = main(
                [
                    "--data-resource-acceptance",
                    str(bad_data),
                    "--evidence-inventory",
                    str(root / "missing.json"),
                    "--original-exit-status",
                    "bad",
                    "--validator-exit-status",
                    "0",
                    "--restore-status",
                    "0",
                    "--restoration-verified",
                    "yes",
                    "--evidence-status",
                    "0",
                    "--base-hash-check-status",
                    "0",
                    "--complete-hash-check-status",
                    "0",
                    "--termination-signal",
                    "none",
                    "--base-hash-evidence",
                    str(root / "missing-base.txt"),
                    "--complete-hash-evidence",
                    "bad-sha",
                    "--output",
                    str(output_path),
                ]
            )
            acceptance = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(exit_status, 10)
            for error in (
                "data_resource_acceptance_json_invalid",
                "evidence_inventory_missing",
                "original_exit_status_type",
                "restoration_verified_type",
                "evidence_sha256_base_check_missing",
                "evidence_sha256_complete_check_missing",
            ):
                self.assertIn(error, acceptance["errors"])
            self.assertFalse(acceptance["runner_qualified"])
            self.assertFalse(acceptance["hash_checks_verified"])
            self.assertFalse(acceptance["final_pareto_ingestion_allowed"])


if __name__ == "__main__":
    unittest.main()
