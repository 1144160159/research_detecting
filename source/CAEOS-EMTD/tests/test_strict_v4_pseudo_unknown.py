from __future__ import annotations

import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path

import numpy as np

from analyze_strict_v4_pseudo_unknown_development import (
    CANDIDATE,
    DEVELOPMENT_SCENARIOS,
    REFERENCE,
    analyze,
    validate_pseudo_unknown_protocol,
)
from confirm_strict_v4_pseudo_unknown import decision


def reports(gain: float = 0.05):
    reference = {
        "known_macro_f1": 0.8,
        "unknown_auroc": 0.5,
        "unknown_aupr": 0.5,
        "unknown_fpr95": 0.5,
        "oscr": 0.5,
        "known_acceptance_rate": 0.9,
        "unknown_rejection_rate": 0.5,
    }
    candidate = dict(reference)
    for metric in ("unknown_auroc", "unknown_aupr", "oscr"):
        candidate[metric] += gain
    candidate["unknown_fpr95"] -= gain
    return reference, candidate


def payload(suite: str, scenario: str, gain: float = 0.05):
    reference, candidate = reports(gain)
    if gain < 0:
        reference.update(
            {
                "unknown_auroc": 1.0,
                "unknown_aupr": 1.0,
                "unknown_fpr95": 0.0,
                "oscr": 1.0,
            }
        )
        candidate.update(
            {
                "unknown_auroc": 0.5,
                "unknown_aupr": 0.5,
                "unknown_fpr95": 0.5,
                "oscr": 0.5,
            }
        )
    return {
        "seed": 7,
        "selected_risk": CANDIDATE,
        "selected_report": candidate,
        "reports": {REFERENCE: reference, CANDIDATE: candidate},
        "arguments": {"risk_selection": "nested_pseudo_unknown_blend"},
        "risk_selection_details": {
            "unknown_or_test_labels_used_for_selection": False,
            "learned_feature_names": ["distance"],
            "learned_nonnegative_weights": {"distance": 1.0},
            "pseudo_unknown_learned_blend": {
                "passes": True,
                "selected_alpha": 0.5,
                "unknown_or_test_labels_used": False,
                "pseudo_unknown_source": "known validation attack labels only",
                "folds": [
                    {"task": "a", "training_tasks": ["b", "c"]},
                    {"task": "b", "training_tasks": ["a", "c"]},
                    {"task": "c", "training_tasks": ["a", "b"]},
                ],
            },
        },
        "split_metadata": {
            "split_fingerprint": {"combined": f"{suite}-{scenario}-seed7"}
        },
    }


class StrictV4PseudoUnknownTests(unittest.TestCase):
    def materialize(self, root: Path, negative_suite: str | None = None):
        for suite, scenarios in DEVELOPMENT_SCENARIOS.items():
            for scenario in scenarios:
                directory = root / suite / f"{scenario}_seed7"
                directory.mkdir(parents=True)
                gain = -0.05 if suite == negative_suite else 0.05
                (directory / "metrics.json").write_text(
                    json.dumps(payload(suite, scenario, gain)), encoding="utf-8"
                )
                validation_reference = np.asarray([0.1, 0.2, 0.3, 0.4])
                test_reference = np.asarray(
                    [0.1, 0.2, 0.3, 0.4, 0.35, 0.45]
                    if gain > 0
                    else [0.05, 0.1, 0.15, 0.2, 0.8, 0.9]
                )
                validation_learned = np.asarray([0.05, 0.1, 0.15, 0.2])
                test_learned = np.asarray(
                    [0.05, 0.1, 0.15, 0.2, 0.8, 0.9]
                    if gain > 0
                    else [0.8, 0.9, 0.7, 0.6, 0.05, 0.1]
                )
                alpha = 0.5
                np.savez_compressed(
                    directory / "scores.npz",
                    validation_cauchy_modality_support_union=validation_reference,
                    test_cauchy_modality_support_union=test_reference,
                    validation_pseudo_unknown_learned_blend=(
                        (1 - alpha) * validation_reference
                        + alpha * validation_learned
                    ),
                    test_pseudo_unknown_learned_blend=(
                        (1 - alpha) * test_reference + alpha * test_learned
                    ),
                    test_labels=np.asarray([0, 0, 1, 1, -1, -1]),
                    test_unknown=np.asarray([False, False, False, False, True, True]),
                    test_prediction=np.asarray([0, 0, 1, 1, 0, 1]),
                )
                for name in ("evidence_package.npz", "provenance.json"):
                    (directory / name).write_bytes(b"test")

    def test_protocol_rejects_fold_training_on_itself(self):
        value = payload("suite", "scenario")
        value["risk_selection_details"]["pseudo_unknown_learned_blend"]["folds"][0][
            "training_tasks"
        ].append("a")
        with self.assertRaisesRegex(ValueError, "cross-fitting leakage"):
            validate_pseudo_unknown_protocol(value, "test")

    def test_development_freezes_only_when_both_suites_improve_all_metrics(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.materialize(root)
            report = analyze(root, Path.cwd(), 100, 11)
        self.assertTrue(report["freeze_candidate"])
        self.assertEqual(report["state"], "frozen_unconfirmed")
        self.assertEqual(report["candidate_manifest"]["confirmation"]["seeds"], [73, 79])

    def test_development_rejects_one_negative_suite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.materialize(root, negative_suite="cic_iot2023")
            report = analyze(root, Path.cwd(), 100, 11)
        self.assertFalse(report["freeze_candidate"])
        self.assertEqual(report["state"], "rejected_development")

    def test_confirmation_gate_requires_positive_auroc_bootstrap(self):
        reference, candidate = reports(0.05)
        rows = [
            {
                "suite": suite,
                "scenario": f"s{index}",
                "seed": 73,
                "candidate_selected": CANDIDATE,
                "reference_selected": REFERENCE,
                "candidate_report": candidate,
                "reference_report": reference,
            }
            for index, suite in enumerate(("cic_ton_iot", "cic_iot2023"))
        ]
        from summarize_paired_confirmation import aggregate

        combined = aggregate(rows, 100, 3)
        suites = {
            suite: aggregate([row for row in rows if row["suite"] == suite], 100, 3)
            for suite in ("cic_ton_iot", "cic_iot2023")
        }
        result = decision(combined, suites, Counter({CANDIDATE: 2}), 0.01)
        self.assertTrue(result["passes"])


if __name__ == "__main__":
    unittest.main()
