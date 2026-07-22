import json
import tempfile
import unittest
from pathlib import Path

from audit_mal_tls_self_algorithm_selection import candidate_record, rank_eligible
from create_mal_tls_self_algorithm_selection_protocol import create_protocol
from create_strict_v4_external_confirmation_protocol import canonical_hash


def protocol_fixture(schema: str, seed: int):
    payload = {
        "schema_version": schema,
        "training": {"development_seed": seed},
        "metrics_observed_at_freeze": 0,
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


class SelfAlgorithmSelectionTests(unittest.TestCase):
    def test_selection_protocol_is_frozen_before_confirmation_results(self) -> None:
        geometry = protocol_fixture(
            "mal_tls_geometry_preserving_adapter_protocol_v1", 195
        )
        counterfactual = protocol_fixture(
            "mal_tls_counterfactual_conflict_gate_protocol_v1", 201
        )
        protocol = create_protocol(
            geometry,
            counterfactual,
            input_file_sha256={"geometry": "a" * 64},
            implementation_sha256={"audit": "b" * 64},
            observed_confirmation_analyses=0,
        )
        self.assertEqual(
            protocol["schema_version"],
            "mal_tls_self_algorithm_selection_protocol_v2",
        )
        self.assertEqual(protocol["global_incumbent"], "caeos_pairwise")
        self.assertEqual(protocol["confirmation_analyses_observed_at_freeze"], 0)
        self.assertEqual(protocol["manifest_sha256"], canonical_hash(protocol))
        with self.assertRaisesRegex(ValueError, "before confirmation"):
            create_protocol(
                geometry,
                counterfactual,
                input_file_sha256={},
                implementation_sha256={},
                observed_confirmation_analyses=1,
            )

    def test_ranking_requires_eligibility_and_uses_worst_ci_first(self) -> None:
        records = [
            {
                "candidate": "mal_tls_geometry_preserving_adapter",
                "eligible": True,
                "selection_score": {
                    "minimum_bootstrap_95ci_lower_bound": 0.01,
                    "mean_four_metric_oriented_gain": 0.08,
                },
            },
            {
                "candidate": "mal_tls_counterfactual_conflict_gate",
                "eligible": True,
                "selection_score": {
                    "minimum_bootstrap_95ci_lower_bound": 0.02,
                    "mean_four_metric_oriented_gain": 0.03,
                },
            },
        ]
        selected = rank_eligible(
            records,
            [
                "mal_tls_geometry_preserving_adapter",
                "mal_tls_counterfactual_conflict_gate",
            ],
        )
        self.assertEqual(
            selected["candidate"], "mal_tls_counterfactual_conflict_gate"
        )
        records[1]["eligible"] = False
        self.assertEqual(
            rank_eligible(
                records,
                [
                    "mal_tls_geometry_preserving_adapter",
                    "mal_tls_counterfactual_conflict_gate",
                ],
            )["candidate"],
            "mal_tls_geometry_preserving_adapter",
        )

    def test_no_confirmed_candidate_retains_incumbent(self) -> None:
        self.assertIsNone(
            rank_eligible(
                [
                    {
                        "candidate": "mal_tls_geometry_preserving_adapter",
                        "eligible": False,
                        "selection_score": None,
                    }
                ],
                ["mal_tls_geometry_preserving_adapter"],
            )
        )

    def test_candidate_record_requires_confirmation_after_positive_pilot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pilot_path = root / "pilot.json"
            branch = root / "branch"
            confirmation_root = root / "confirmation"
            branch.mkdir()
            confirmation_root.mkdir()
            (branch / "branch_complete").touch()
            pilot_path.write_text(
                json.dumps(
                    {
                        "protocol_manifest_sha256": "p" * 64,
                        "schema_version": (
                            "mal_tls_counterfactual_conflict_gate_analysis_v1"
                        ),
                        "passes": True,
                        "decision": "freeze_for_reserved_seed_confirmation",
                    }
                ),
                encoding="utf-8",
            )
            protocol = {
                "selected_candidate": "mal_tls_counterfactual_conflict_gate"
            }
            protocol["manifest_sha256"] = canonical_hash(protocol)
            protocol_path = confirmation_root / "protocol_manifest.json"
            protocol_path.write_text(json.dumps(protocol), encoding="utf-8")
            analysis_path = confirmation_root / "analysis.json"
            analysis_path.write_text(
                json.dumps(
                    {
                        "schema_version": (
                            "mal_tls_counterfactual_conflict_gate_confirmation_analysis_v1"
                        ),
                        "protocol_manifest_sha256": protocol["manifest_sha256"],
                        "passes": True,
                        "metrics": {
                            name: {"mean": 0.03, "bootstrap_95ci": [0.01, 0.05]}
                            for name in (
                                "unknown_auroc",
                                "unknown_aupr",
                                "unknown_fpr95",
                                "oscr",
                            )
                        },
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "lacks confirmation"):
                candidate_record(
                    candidate="mal_tls_counterfactual_conflict_gate",
                    pilot_analysis_path=pilot_path,
                    branch_root=branch,
                    confirmation_protocol_path=protocol_path,
                    confirmation_analysis_path=analysis_path,
                    expected_confirmation_schema=(
                        "mal_tls_counterfactual_conflict_gate_confirmation_analysis_v1"
                    ),
                    expected_pilot_schema=(
                        "mal_tls_counterfactual_conflict_gate_analysis_v1"
                    ),
                    expected_pilot_manifest_sha256="p" * 64,
                    metrics=["unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr"],
                )
            (confirmation_root / "confirmation_complete").touch()
            record, _ = candidate_record(
                candidate="mal_tls_counterfactual_conflict_gate",
                pilot_analysis_path=pilot_path,
                branch_root=branch,
                confirmation_protocol_path=protocol_path,
                confirmation_analysis_path=analysis_path,
                expected_confirmation_schema=(
                    "mal_tls_counterfactual_conflict_gate_confirmation_analysis_v1"
                ),
                expected_pilot_schema=(
                    "mal_tls_counterfactual_conflict_gate_analysis_v1"
                ),
                expected_pilot_manifest_sha256="p" * 64,
                metrics=["unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr"],
            )
            self.assertTrue(record["eligible"])
            self.assertAlmostEqual(
                record["selection_score"]["minimum_bootstrap_95ci_lower_bound"],
                0.01,
            )


if __name__ == "__main__":
    unittest.main()
