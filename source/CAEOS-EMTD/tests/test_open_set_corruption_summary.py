import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from summarize_open_set_corruption_pilot import (
    REPORTS,
    aggregate,
    canonical_manifest_hash,
    load_and_audit,
    validate_manifest,
)


def manifest() -> dict:
    payload = {
        "schema_version": "strict_v2_open_set_corruption_pilot_v1",
        "scenarios": ["fingerprinting"],
        "seeds": [7],
        "reports": list(REPORTS),
        "conditions": [
            {
                "id": "clean",
                "family": "clean",
                "train_label_noise": 0.0,
                "test_corruption_kind": "none",
                "test_corruption_modality": 0,
                "test_corruption_severity": 0.0,
                "test_corruption_seed": 20260717,
            },
            {
                "id": "missing_m1",
                "family": "modality_missing",
                "train_label_noise": 0.0,
                "test_corruption_kind": "modality_missing",
                "test_corruption_modality": 1,
                "test_corruption_severity": 1.0,
                "test_corruption_seed": 20260717,
            },
        ],
        "expected_run_count": 2,
    }
    payload["manifest_sha256"] = canonical_manifest_hash(payload)
    return payload


def write_run(root: Path, condition: dict, fingerprint: str = "a" * 64) -> None:
    run = root / condition["id"] / "edge_iiot" / "fingerprinting_seed7"
    run.mkdir(parents=True)
    test_modality = condition["test_corruption_modality"]
    if condition["test_corruption_kind"] == "none":
        test_modality = None
    report = {
        "known_macro_f1": 0.8,
        "unknown_auroc": 0.9,
        "unknown_aupr": 0.85,
        "unknown_fpr95": 0.2,
        "oscr": 0.75,
        "known_acceptance_rate": 0.9,
        "unknown_rejection_rate": 0.8,
    }
    metrics = {
        "corruption_protocol": {
            "train_label_noise_fraction": condition["train_label_noise"],
            "test_corruption": {
                "kind": condition["test_corruption_kind"],
                "modality": test_modality,
                "severity": condition["test_corruption_severity"],
                "seed": condition["test_corruption_seed"],
            },
            "train_only_label_corruption": True,
            "validation_is_clean": True,
            "test_only_feature_corruption": True,
            "unknown_or_test_labels_used_to_generate_corruption": False,
        },
        "split_metadata": {"split_fingerprint": {"combined": fingerprint}},
        "validation_thresholds": {"cauchy_modality_support_union": 0.5},
        "reports": {name: report for name in REPORTS},
    }
    (run / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
    command = [
        "python",
        "train_hybrid_open_set.py",
        "--test-corruption-kind",
        condition["test_corruption_kind"],
        "--test-corruption-modality",
        str(condition["test_corruption_modality"]),
        "--test-corruption-severity",
        str(condition["test_corruption_severity"]),
        "--test-corruption-seed",
        str(condition["test_corruption_seed"]),
        "--train-label-noise",
        str(condition["train_label_noise"]),
    ]
    provenance = {
        "task": {"scenario": "fingerprinting", "seed": 7},
        "command": command,
        "code": {"sha256": "b" * 64},
    }
    (run / "provenance.json").write_text(json.dumps(provenance), encoding="utf-8")
    np.savez(run / "scores.npz", values=np.ones(1))
    np.savez(run / "evidence_package.npz", values=np.ones(1))


class OpenSetCorruptionSummaryTests(unittest.TestCase):
    def test_complete_matrix_audits_and_aggregates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            payload = manifest()
            path = root / "manifest.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            frozen = validate_manifest(path)
            for condition in frozen["conditions"]:
                write_run(root / "runs", condition)
            rows = load_and_audit(root / "runs", frozen)
            summary = aggregate(rows, frozen)
            self.assertEqual(summary["completed_runs"], 2)
            self.assertTrue(summary["split_fingerprints_identical_across_conditions"])

    def test_manifest_tampering_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "manifest.json"
            payload = manifest()
            payload["seeds"] = [11]
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "manifest SHA mismatch"):
                validate_manifest(path)

    def test_changed_split_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            payload = manifest()
            write_run(root, payload["conditions"][0])
            write_run(root, payload["conditions"][1], fingerprint="c" * 64)
            with self.assertRaisesRegex(ValueError, "split fingerprint changed"):
                load_and_audit(root, payload)

    def test_test_corruption_threshold_change_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            payload = manifest()
            for condition in payload["conditions"]:
                write_run(root, condition)
            path = root / "missing_m1" / "edge_iiot" / "fingerprinting_seed7" / "metrics.json"
            metrics = json.loads(path.read_text(encoding="utf-8"))
            metrics["validation_thresholds"]["cauchy_modality_support_union"] = 0.6
            path.write_text(json.dumps(metrics), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "clean-validation threshold"):
                load_and_audit(root, payload)


if __name__ == "__main__":
    unittest.main()
