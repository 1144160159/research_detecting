from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from create_strict_v4_conflict_topology_copula_confirmation_protocol import (
    create_protocol,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_conflict_topology_copula_confirmation_matrix import (
    verify_pairwise_source,
)
from summarize_strict_v4_conflict_topology_copula_confirmation import (
    METRICS,
    analyze,
)


def sealed(payload: dict) -> dict:
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


def pilot_protocol() -> dict:
    return sealed(
        {
            "schema_version": "strict_v4_conflict_topology_copula_protocol_v1",
            "reserved_confirmation": {"seeds": [233, 239, 241]},
        }
    )


def pilot_analysis(protocol: dict, *, passes: bool = True) -> dict:
    return {
        "schema_version": "strict_v4_conflict_topology_copula_analysis_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "passes": passes,
        "decision": (
            "freeze_for_reserved_seed_confirmation"
            if passes
            else "retain_caeos_pairwise"
        ),
    }


def coverage() -> dict:
    counts = [18, 14, 14, 14, 14, 14, 14]
    registry = {
        f"suite_{index}": {
            "count": count,
            "scenarios": [f"scenario_{position}" for position in range(count)],
        }
        for index, count in enumerate(counts)
    }
    return sealed(
        {
            "schema_version": "strict_v4_coverage_manifest_v2",
            "scenario_registry": registry,
        }
    )


def pairwise_manifest() -> dict:
    return sealed(
        {
            "schema_version": "strict_v4_boundary_pairwise_candidate_v1",
            "candidate": {
                "runtime_uses_unknown_or_test_labels": False,
                "risk_selection": "nested_boundary_pairwise_pseudo_unknown_blend",
                "maximum_alpha": 0.5,
                "minimum_fold_gain": 0.0,
                "hard_pseudo_fraction": 0.5,
                "interpolation": 0.5,
                "max_per_task": 1000,
                "training_objective": "pairwise",
            },
        }
    )


def confirmation_protocol() -> dict:
    registry = {
        f"suite_{suite}": {
            "count": 1 if suite else 2,
            "scenarios": (
                ["scenario_0", "scenario_1"] if suite == 0 else ["scenario_0"]
            ),
        }
        for suite in range(7)
    }
    payload = {
        "schema_version": "strict_v4_conflict_topology_copula_confirmation_protocol_v1",
        "seeds": [233, 239, 241],
        "scenario_registry": registry,
        "scenario_count": 8,
        "expected_ctc_runs": 24,
        "confirmation_inference": {
            "bootstrap_repetitions": 100,
            "bootstrap_seed": 20260721,
            "gate": {"known_macro_f1_absolute_tolerance": 1e-12},
        },
    }
    return sealed(payload)


class ConflictTopologyConfirmationTests(unittest.TestCase):
    def test_positive_pilot_freezes_complete_confirmation_protocol(self) -> None:
        pilot = pilot_protocol()
        value = create_protocol(
            pilot_protocol=pilot,
            pilot_analysis=pilot_analysis(pilot),
            coverage=coverage(),
            pairwise_manifest=pairwise_manifest(),
            input_file_sha256={"coverage": "1" * 64},
            implementation_sha256={"candidate.py": "2" * 64},
            observed_metrics=0,
        )
        self.assertEqual(value["manifest_sha256"], canonical_hash(value))
        self.assertEqual(value["scenario_count"], 102)
        self.assertEqual(value["expected_ctc_runs"], 306)
        self.assertFalse(
            value["claim_boundary"][
                "unknown_or_test_labels_used_for_fit_threshold_or_weight_selection"
            ]
        )

    def test_negative_pilot_cannot_freeze_confirmation(self) -> None:
        pilot = pilot_protocol()
        with self.assertRaisesRegex(ValueError, "did not authorize"):
            create_protocol(
                pilot_protocol=pilot,
                pilot_analysis=pilot_analysis(pilot, passes=False),
                coverage=coverage(),
                pairwise_manifest=pairwise_manifest(),
                input_file_sha256={},
                implementation_sha256={},
                observed_metrics=0,
            )

    def test_pairwise_source_rejects_selection_leakage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            metrics = {
                "seed": 233,
                "risk_policy": "policy",
                "risk_selection": "selection",
                "risk_selection_details": {
                    "unknown_or_test_labels_used_for_selection": True
                },
                "split_metadata": {"split_fingerprint": {"combined": "hash"}},
            }
            (source / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
            for name in ("scores.npz", "evidence_package.npz", "provenance.json"):
                (source / name).touch()
            with self.assertRaisesRegex(ValueError, "leakage guard"):
                verify_pairwise_source(
                    source, seed=233, risk_policy="policy", risk_selection="selection"
                )

    def _write_results(self, root: Path, protocol: dict, delta: float) -> None:
        for suite, registry in protocol["scenario_registry"].items():
            for scenario in registry["scenarios"]:
                for seed in protocol["seeds"]:
                    output = root / suite / f"{scenario}_seed{seed}"
                    output.mkdir(parents=True)
                    reference = {metric: 0.5 for metric in METRICS}
                    candidate = {
                        metric: 0.5 - delta if metric == "unknown_fpr95" else 0.5 + delta
                        for metric in METRICS
                    }
                    payload = {
                        "protocol_manifest_sha256": protocol["manifest_sha256"],
                        "seed": seed,
                        "reports": {"reference": reference, "candidate": candidate},
                        "diagnostics": {
                            "prediction_array_equal": True,
                            "known_macro_f1_absolute_difference": 0.0,
                        },
                    }
                    (output / "metrics.json").write_text(
                        json.dumps(payload), encoding="utf-8"
                    )

    def test_positive_confirmation_passes_all_statistical_gates(self) -> None:
        protocol = confirmation_protocol()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_results(root, protocol, 0.01)
            report = analyze(protocol, root)
        self.assertTrue(report["passes"])
        self.assertEqual(
            report["decision"],
            "ctc_accuracy_confirmed_pending_efficiency_and_external_dataset_gates",
        )

    def test_negative_confirmation_retains_pairwise(self) -> None:
        protocol = confirmation_protocol()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_results(root, protocol, -0.01)
            report = analyze(protocol, root)
        self.assertFalse(report["passes"])
        self.assertEqual(
            report["decision"], "retain_caeos_pairwise_and_reject_ctc_replacement"
        )


if __name__ == "__main__":
    unittest.main()
