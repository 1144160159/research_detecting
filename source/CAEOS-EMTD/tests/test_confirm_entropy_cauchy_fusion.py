from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from confirm_entropy_cauchy_fusion import build_confirmation, validate_manifest


def report(delta: float) -> dict[str, float]:
    return {
        "known_macro_f1": 0.9,
        "unknown_auroc": 0.7 + delta,
        "unknown_aupr": 0.6 + delta,
        "unknown_fpr95": 0.5 - delta,
        "oscr": 0.65 + delta,
        "known_acceptance_rate": 0.95,
        "unknown_rejection_rate": 0.5,
    }


class ConfirmEntropyCauchyFusionTest(unittest.TestCase):
    def write_manifest(self, path: Path) -> dict[str, object]:
        analyzer = path.parents[0] / "analyze_entropy_cauchy_fusion.py"
        source = Path(__file__).parents[1] / "analyze_entropy_cauchy_fusion.py"
        analyzer.write_bytes(source.read_bytes())
        core = {
            "schema_version": "entropy_cauchy_fusion_manifest_v1",
            "status": "frozen_unconfirmed",
            "selected_candidate": "rank_union",
            "candidate_family": ["entropy", "cauchy_all", "rank_union"],
            "endpoint_calibration": "known_validation_empirical_cdf_only",
            "fusion_definitions": {"rank_union": "test"},
            "selection_rule": {"primary": "auroc"},
            "development_seeds": [7, 11],
            "confirmation_seeds": [67, 71],
            "source_artifacts_combined_sha256": "a" * 64,
            "analysis_implementation_sha256": hashlib.sha256(
                source.read_bytes()
            ).hexdigest(),
            "development_candidate_screening_uses_test_unknown_labels": True,
            "runtime_fusion_uses_unknown_or_test_labels": False,
        }
        digest = hashlib.sha256(
            json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        manifest = {**core, "manifest_sha256": digest}
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return manifest

    def test_tampered_manifest_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            path = directory / "manifest.json"
            manifest = self.write_manifest(path)
            manifest["selected_candidate"] = "rank_mean"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                validate_manifest(path)

    def test_positive_scenario_block_confirmation_passes(self) -> None:
        rows = []
        for scenario in tuple(f"scenario_{index}" for index in range(14)):
            for seed in (67, 71):
                rows.append(
                    {
                        "suite": "edge",
                        "scenario": scenario,
                        "seed": seed,
                        "candidate_selected": "rank_union",
                        "reference_selected": "entropy",
                        "candidate_report": report(0.1),
                        "reference_report": report(0.0),
                        "split_fingerprint": f"{scenario}-{seed}",
                    }
                )
        result = build_confirmation(rows, 500, 19)
        self.assertEqual("confirmed", result["confirmation_status"])


if __name__ == "__main__":
    unittest.main()
