import json
import tempfile
import unittest
from pathlib import Path

from create_gpu_dataset_admission_execution_protocol import (
    create_protocol,
    verify_protocol,
)


class GpuDatasetAdmissionExecutionProtocolTests(unittest.TestCase):
    def test_freezes_before_result_and_detects_bound_file_change(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parent = root / "parent.json"
            parent.write_text(
                json.dumps(
                    {
                        "schema_version": "gpu_malicious_dataset_expansion_protocol_v1",
                        "status": "frozen_before_full_scan_and_training",
                    }
                ),
                encoding="utf-8",
            )
            bindings = []
            for name in ("scanner.py", "lsnm.json", "cic.json", "runner.sh"):
                path = root / name
                path.write_text(name, encoding="utf-8")
                bindings.append(path)
            protocol = create_protocol(
                parent_protocol=parent,
                scanner=bindings[0],
                lsnm_config=bindings[1],
                cic_config=bindings[2],
                runner=bindings[3],
                result_path=root / "missing-result.json",
            )
            verify_protocol(protocol)
            bindings[0].write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "bound implementation changed"):
                verify_protocol(protocol)

    def test_refuses_to_freeze_after_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parent = root / "parent.json"
            parent.write_text(
                json.dumps(
                    {
                        "schema_version": "gpu_malicious_dataset_expansion_protocol_v1",
                        "status": "frozen_before_full_scan_and_training",
                    }
                ),
                encoding="utf-8",
            )
            binding = root / "binding"
            binding.write_text("x", encoding="utf-8")
            result = root / "result.json"
            result.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "before results"):
                create_protocol(
                    parent_protocol=parent,
                    scanner=binding,
                    lsnm_config=binding,
                    cic_config=binding,
                    runner=binding,
                    result_path=result,
                )

    def test_waiter_depends_on_postefficiency_chain(self) -> None:
        script = (
            Path(__file__).parents[1]
            / "scripts"
            / "wait_and_run_gpu_dataset_full_admission_audit.sh"
        ).read_text(encoding="utf-8")
        self.assertIn("strict_v4_postefficiency_claim_chain_v2/chain_complete", script)
        self.assertIn("idle_samples", script)
        self.assertIn("run_gpu_dataset_full_admission_audit.sh", script)


if __name__ == "__main__":
    unittest.main()
