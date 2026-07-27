from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from create_strict_v4_conflict_topology_copula_protocol import (
    SCENARIOS,
    create_protocol,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_strict_v4_conflict_topology_copula import METRICS, analyze
from run_strict_v4_conflict_topology_copula_matrix import verify_source_record


def inputs():
    return [
        {
            "suite": suite,
            "scenario": scenario,
            "seed": 7,
            "run_root": f"runs/source/{suite}/{scenario}_seed7",
            "selected_risk": "cauchy_modality_support_union",
            "sha256": {
                "metrics.json": "1" * 64,
                "scores.npz": "2" * 64,
                "evidence_package.npz": "3" * 64,
            },
        }
        for suite, scenarios in SCENARIOS.items()
        for scenario in scenarios
    ]


def protocol():
    return create_protocol(
        inputs=inputs(), implementation_sha256={"candidate.py": "4" * 64}, observed_metrics=0
    )


class ConflictTopologyProtocolTests(unittest.TestCase):
    def test_protocol_is_frozen_and_canonical(self) -> None:
        value = protocol()
        self.assertEqual(value["manifest_sha256"], canonical_hash(value))
        self.assertFalse(
            value["known_only_fit"][
                "unknown_or_test_labels_used_for_fit_threshold_or_selection"
            ]
        )
        self.assertEqual(value["reserved_confirmation"]["seeds"], [233, 239, 241])

    def test_protocol_rejects_observed_results(self) -> None:
        with self.assertRaisesRegex(ValueError, "freeze before results"):
            create_protocol(
                inputs=inputs(),
                implementation_sha256={"candidate.py": "4" * 64},
                observed_metrics=1,
            )

    def test_runner_rejects_source_hash_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "runs" / "source" / "suite" / "scenario_seed7"
            source.mkdir(parents=True)
            (source / "metrics.json").write_text("frozen", encoding="utf-8")
            record = {
                "run_root": "runs/source/suite/scenario_seed7",
                "sha256": {"metrics.json": "0" * 64},
            }
            with self.assertRaisesRegex(ValueError, "input SHA mismatch"):
                verify_source_record(root, record)

    def test_positive_summary_opens_confirmation(self) -> None:
        value = protocol()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for record in value["pilot"]["inputs"]:
                output = root / record["suite"] / f'{record["scenario"]}_seed7'
                output.mkdir(parents=True)
                reference = {name: 0.5 for name in METRICS}
                candidate = {
                    name: (0.49 if name == "unknown_fpr95" else 0.51)
                    for name in METRICS
                }
                payload = {
                    "protocol_manifest_sha256": value["manifest_sha256"],
                    "reports": {"reference": reference, "candidate": candidate},
                    "diagnostics": {
                        "prediction_array_equal": True,
                        "known_macro_f1_absolute_difference": 0.0,
                    },
                }
                (output / "metrics.json").write_text(json.dumps(payload), encoding="utf-8")
            result = analyze(value, root)
        self.assertTrue(result["passes"])
        self.assertEqual(result["decision"], "freeze_for_reserved_seed_confirmation")

    def test_suite_regression_closes_gate(self) -> None:
        value = protocol()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for position, record in enumerate(value["pilot"]["inputs"]):
                output = root / record["suite"] / f'{record["scenario"]}_seed7'
                output.mkdir(parents=True)
                reference = {name: 0.5 for name in METRICS}
                delta = -0.03 if record["suite"] == "nf_unsw" else 0.02
                candidate = {
                    name: (
                        reference[name] - delta
                        if name == "unknown_fpr95"
                        else reference[name] + delta
                    )
                    for name in METRICS
                }
                payload = {
                    "protocol_manifest_sha256": value["manifest_sha256"],
                    "reports": {"reference": reference, "candidate": candidate},
                    "diagnostics": {
                        "prediction_array_equal": True,
                        "known_macro_f1_absolute_difference": 0.0,
                    },
                }
                (output / "metrics.json").write_text(json.dumps(payload), encoding="utf-8")
            result = analyze(value, root)
        self.assertFalse(result["passes"])
        self.assertFalse(result["checks"]["minimum_suite_metric_gain"])


if __name__ == "__main__":
    unittest.main()
