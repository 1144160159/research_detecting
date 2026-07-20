import json
import tempfile
import unittest
from pathlib import Path

from audit_strict_v4_efficiency_evidence import audit_source, build_audit


def write_metrics(root: Path, run: str, payload: dict) -> None:
    path = root / "suite" / run / "metrics.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def complete_payload(model: str) -> dict:
    return {
        "model": model,
        "training_seconds": 2.0,
        "inference_seconds": 0.5,
        "inference_samples_per_second": 200.0,
        "peak_gpu_memory_mb": 100.0,
        "trainable_parameters": 1000,
        "hardware": {"gpu_name": "test-gpu"},
    }


class StrictV4EfficiencyEvidenceAuditTests(unittest.TestCase):
    def test_complete_same_semantics_evidence_allows_comparison(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("candidate", "external"):
                write_metrics(root / name, "run", complete_payload(name))
            sources = [
                audit_source(name, root / name, 1)
                for name in ("candidate", "external")
            ]
            report = build_audit(sources)
            self.assertTrue(report["direct_efficiency_comparison_allowed"])

    def test_elapsed_and_training_time_are_not_treated_as_comparable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = complete_payload("candidate")
            candidate.pop("training_seconds")
            candidate["elapsed_seconds"] = 3.0
            write_metrics(root / "candidate", "run", candidate)
            write_metrics(root / "external", "run", complete_payload("external"))
            report = build_audit(
                [
                    audit_source("candidate", root / "candidate", 1),
                    audit_source("external", root / "external", 1),
                ]
            )
            self.assertFalse(
                report["comparison_gates"]["training_time_same_semantics"]
            )
            self.assertFalse(report["direct_efficiency_comparison_allowed"])

    def test_model_filter_excludes_other_models(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_metrics(root, "opendetect", complete_payload("opendetect"))
            write_metrics(root, "other", complete_payload("other"))
            source = audit_source("opendetect", root, 1, "opendetect")
            self.assertEqual(source["discovered_metrics_files"], 2)
            self.assertEqual(source["observed_runs"], 1)
            self.assertTrue(source["coverage_complete"])


if __name__ == "__main__":
    unittest.main()
