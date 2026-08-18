import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "a09_local_fallback_quality_composer",
    ROOT / "scripts" / "compose_a09_local_fallback_quality_receipt.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def write(path, raw):
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    return write(path, (json.dumps(value, sort_keys=True) + "\n").encode())


class A09LocalFallbackQualityReceiptTests(unittest.TestCase):
    def inputs(self, root):
        artifact = root / "a09.portable"
        source = root / "a09_fallback.rs"
        binary = root / "capture"
        manifest = root / "evidence.sha256"
        hashes = {
            "artifact": write(artifact, b"artifact"),
            "rust_source": write(source, b"source"),
            "capture_binary": write(binary, b"binary"),
            "evidence_manifest": write(manifest, b"manifest"),
        }
        equivalence = root / "equivalence.json"
        hashes["equivalence"] = write_json(equivalence, {
            "schema_version": 1,
            "scope": "hft_mgbs_a09_local_fallback_equivalence_evidence_v1",
            "candidate_id": "A09",
            "portable_artifact_sha256": hashes["artifact"],
            "source_model_sha256": "1" * 64,
            "numpy_engine_sha256": "2" * 64,
            "campaign_contract_sha256": "3" * 64,
            "holdout_input_sha256": "4" * 64,
            "sample_count": 100,
            "probability_bit_exact_count": 100,
            "decision_exact_count": 100,
            "rust_fallback_source_sha256": hashes["rust_source"],
            "capture_binary_sha256": hashes["capture_binary"],
            "evidence_manifest_sha256": hashes["evidence_manifest"],
            "accepted": True,
            "errors": [],
        })
        benchmark = root / "benchmark.json"
        runs = [
            {
                "run_id": "run-{}".format(index), "flows_per_second": 6000.0,
                "p50_us": 100.0, "p99_us": 9000.0, "max_us": 9500.0,
                "node_visits_per_second": 1000000.0, "cpu_cores": 2.0,
                "rss_bytes": 1000000,
            }
            for index in range(3)
        ]
        benchmark_value = {
            "schema_version": 1,
            "scope": "hft_mgbs_a09_local_fallback_physical_benchmark_v1",
            "candidate_id": "A09",
            "portable_artifact_sha256": hashes["artifact"],
            "capture_binary_sha256": hashes["capture_binary"],
            "rust_fallback_source_sha256": hashes["rust_source"],
            "evidence_manifest_sha256": hashes["evidence_manifest"],
            "runs": runs,
            "restoration_verified": True,
            "accepted": True,
            "errors": [],
        }
        hashes["benchmark"] = write_json(benchmark, benchmark_value)
        return artifact, equivalence, benchmark, source, binary, manifest, hashes, benchmark_value

    def call(self, root, values):
        artifact, equivalence, benchmark, source, binary, manifest, hashes, _ = values
        return MODULE.compose(
            artifact=artifact, equivalence=equivalence, benchmark=benchmark,
            rust_source=source, capture_binary=binary, evidence_manifest=manifest,
            output=root / "receipt.json",
            expected_artifact_sha256=hashes["artifact"],
            expected_equivalence_sha256=hashes["equivalence"],
            expected_benchmark_sha256=hashes["benchmark"],
            expected_rust_source_sha256=hashes["rust_source"],
            expected_capture_binary_sha256=hashes["capture_binary"],
            expected_evidence_manifest_sha256=hashes["evidence_manifest"],
        )

    def test_exact_equivalence_and_three_physical_runs_compose_accepted_nonrelease_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            receipt = self.call(root, self.inputs(root))
            self.assertTrue(receipt["accepted"])
            self.assertEqual(receipt["physical_benchmark_runs"], 3)
            self.assertFalse(receipt["final_pareto_ingestion_allowed"])

    def test_benchmark_over_p99_gate_is_rejected_without_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            values = self.inputs(root)
            benchmark = values[2]
            benchmark_value = values[-1]
            benchmark_value["runs"][0]["p99_us"] = 10001.0
            values[-2]["benchmark"] = write_json(benchmark, benchmark_value)
            with self.assertRaises(ValueError):
                self.call(root, values)
            self.assertFalse((root / "receipt.json").exists())


if __name__ == "__main__":
    unittest.main()
