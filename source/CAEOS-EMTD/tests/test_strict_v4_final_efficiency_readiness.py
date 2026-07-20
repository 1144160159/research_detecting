import json
import tempfile
import unittest
from pathlib import Path

from audit_strict_v4_final_efficiency_readiness import audit_method, build_readiness


def protocol() -> dict:
    return {
        "schema_version": "strict_v4_final_efficiency_protocol_v1",
        "manifest_sha256": "a" * 64,
        "inference_benchmark": {"saved_artifacts_only_no_refit": True},
    }


def write_run(root: Path, name: str, model: str, artifact: bool) -> None:
    run = root / name
    run.mkdir(parents=True)
    (run / "metrics.json").write_text(
        json.dumps({"model": model}), encoding="utf-8"
    )
    if artifact:
        (run / "model.pt").write_bytes(b"checkpoint")


class StrictV4FinalEfficiencyReadinessTests(unittest.TestCase):
    def test_missing_candidate_models_blocks_saved_artifact_protocol(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_run(root / "candidate", "one", "caeos", False)
            write_run(root / "external", "one", "opendetect", True)
            report = build_readiness(
                protocol(),
                audit_method("candidate", root / "candidate", 1),
                audit_method("external", root / "external", 1, "opendetect"),
            )
            self.assertFalse(report["v1_protocol_executable"])
            self.assertEqual(
                report["methods"]["candidate"]["runs_with_loadable_model"], 0
            )
            self.assertEqual(
                report["methods"]["comparator"]["runs_with_loadable_model"], 1
            )
            self.assertFalse(report["direct_efficiency_claim_allowed"])

    def test_complete_saved_models_make_execution_ready_but_not_claim_ready(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_run(root / "candidate", "one", "caeos", True)
            write_run(root / "external", "one", "opendetect", True)
            report = build_readiness(
                protocol(),
                audit_method("candidate", root / "candidate", 1),
                audit_method("external", root / "external", 1, "opendetect"),
            )
            self.assertTrue(report["v1_protocol_executable"])
            self.assertFalse(report["direct_efficiency_claim_allowed"])

    def test_model_filter_excludes_unrelated_runs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_run(root, "open", "opendetect", True)
            write_run(root, "other", "palm", True)
            audited = audit_method("external", root, 1, "opendetect")
            self.assertEqual(audited["observed_runs"], 1)
            self.assertTrue(audited["saved_artifact_coverage_complete"])


if __name__ == "__main__":
    unittest.main()
