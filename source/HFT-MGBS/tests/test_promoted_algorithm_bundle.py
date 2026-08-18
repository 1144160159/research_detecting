import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "export_a09_bundle", ROOT / "scripts" / "export_a09_bundle.py"
)
EXPORTER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = EXPORTER
SPEC.loader.exec_module(EXPORTER)


class PromotedAlgorithmBundleTest(unittest.TestCase):
    def test_candidate_policy_accepts_only_matching_a09_a10_floors(self):
        EXPORTER.validate_candidate_policy("A09", 0.8)
        EXPORTER.validate_candidate_policy("A10", 0.9)
        for candidate, floor in (("A09", 0.9), ("A10", 0.8), ("A08", 0.8)):
            with self.subTest(candidate=candidate, floor=floor):
                with self.assertRaises(ValueError):
                    EXPORTER.validate_candidate_policy(candidate, floor)

    def test_binding_exporter_qualifies_separate_normal_and_fallback_artifacts(self):
        source = (ROOT / "scripts" / "export_promoted_algorithm_bundle.py").read_text(
            "utf-8"
        )
        for token in (
            "_promotion_artifacts",
            "formal_receipt_sha256",
            "promoted_algorithm_search_sha256",
            'for mode in ("normal", "fallback")',
            'command.append("--disable-deep")',
            "binary_prediction_metrics",
            "_constraint_violations",
            "formal_sample_identity_bound",
            "normal_and_fallback_bundles_qualified",
            '"campaign_prediction_exact_replay": False',
            "deployment_artifact_qualification_complete",
            "production_joint_optimum_proven\": False",
            "final_pareto_ingestion_allowed\": False",
        ):
            with self.subTest(token=token):
                self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
