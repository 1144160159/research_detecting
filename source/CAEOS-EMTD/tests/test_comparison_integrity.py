from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from summarize_neural_comparison import REPORT_METRICS, aggregate, load_runs


def metric_report(auroc: float = 0.8) -> dict[str, float]:
    report = {metric: 0.5 for metric in REPORT_METRICS}
    report["unknown_auroc"] = auroc
    return report


def arguments() -> dict[str, object]:
    return {
        "csv": "cache.csv",
        "config": "configs/edge_iiot.json",
        "split_strategy": "fingerprint_grouped",
        "max_per_class": 1000,
        "benign_class": "Normal",
    }


def gate_metrics() -> dict[str, object]:
    return {
        "unknown_classes": "Fingerprinting",
        "seed": 7,
        "sample_counts": {"Normal": 1000, "Fingerprinting": 1000},
        "split_metadata": {"strategy": "fingerprint_grouped", "version": 1},
        "arguments": {**arguments(), "risk_selection": "density_gate_v2"},
        "risk_selection": "density_gate_v2",
        "selected_risk": "density_reliability_blend",
        "selected_report": metric_report(0.9),
    }


def neural_metrics() -> dict[str, object]:
    return {
        "unknown_classes": "Fingerprinting",
        "seed": 7,
        "sample_counts": {"Normal": 1000, "Fingerprinting": 1000},
        "split_metadata": {"strategy": "fingerprint_grouped", "version": 1},
        "arguments": arguments(),
        "reports": {"closr": metric_report(0.8)},
    }


class ComparisonIntegrityTest(unittest.TestCase):
    def write_pair(
        self,
        root: Path,
        gate: dict[str, object],
        neural: dict[str, object],
    ) -> tuple[Path, Path]:
        gate_root = root / "gate"
        neural_root = root / "neural"
        gate_run = gate_root / "edge_iiot" / "fingerprinting_seed7"
        neural_run = neural_root / "fingerprinting_seed7_closr"
        gate_run.mkdir(parents=True)
        neural_run.mkdir(parents=True)
        (gate_run / "metrics.json").write_text(
            json.dumps(gate), encoding="utf-8"
        )
        (neural_run / "metrics.json").write_text(
            json.dumps(neural), encoding="utf-8"
        )
        return gate_root, neural_root

    def test_load_runs_uses_recorded_gate_method(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            gate_root, neural_root = self.write_pair(
                Path(directory), gate_metrics(), neural_metrics()
            )
            runs = load_runs(gate_root, "edge_iiot", neural_root)

        self.assertEqual(runs[0]["gate_method"], "density_gate_v2")
        self.assertEqual(aggregate(runs)["gate_method"], "density_gate_v2")

    def test_every_protocol_identity_field_must_match(self) -> None:
        mutations = {
            "unknown_classes": lambda value: value.__setitem__(
                "unknown_classes", "XSS"
            ),
            "sample_counts": lambda value: value["sample_counts"].__setitem__(
                "Normal", 999
            ),
            "split_metadata": lambda value: value["split_metadata"].__setitem__(
                "version", 2
            ),
            "arguments.csv": lambda value: value["arguments"].__setitem__(
                "csv", "other.csv"
            ),
            "arguments.config": lambda value: value["arguments"].__setitem__(
                "config", "configs/other.json"
            ),
            "arguments.split_strategy": lambda value: value["arguments"].__setitem__(
                "split_strategy", "random"
            ),
            "arguments.max_per_class": lambda value: value["arguments"].__setitem__(
                "max_per_class", 999
            ),
            "arguments.benign_class": lambda value: value["arguments"].__setitem__(
                "benign_class", "Benign"
            ),
        }
        for field, mutate in mutations.items():
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                neural = copy.deepcopy(neural_metrics())
                mutate(neural)
                gate_root, neural_root = self.write_pair(
                    Path(directory), gate_metrics(), neural
                )
                with self.assertRaisesRegex(ValueError, "protocol identity mismatch"):
                    load_runs(gate_root, "edge_iiot", neural_root)

    def test_missing_gate_result_is_not_silently_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            neural_root = Path(directory) / "neural"
            run = neural_root / "fingerprinting_seed7_closr"
            run.mkdir(parents=True)
            (run / "metrics.json").write_text(
                json.dumps(neural_metrics()), encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "missing gate result"):
                load_runs(Path(directory) / "gate", "edge_iiot", neural_root)

    def test_empty_method_root_is_not_silently_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            neural_root = Path(directory) / "neural"
            neural_root.mkdir()
            with self.assertRaisesRegex(ValueError, "no neural metrics"):
                load_runs(Path(directory) / "gate", "edge_iiot", neural_root)

    def test_aggregate_rejects_missing_methods_instead_of_intersection(self) -> None:
        base = {
            "suite": "edge_iiot",
            "gate_method": "density_gate_v2",
            "gate": 0.9,
            "gate_report": metric_report(0.9),
            "oracle_neural": 0.8,
        }
        runs = [
            {
                **base,
                "scenario": "fingerprinting",
                "seed": 7,
                "neural": {"closr": 0.8, "sieve": 0.7},
                "neural_reports": {
                    "closr": metric_report(0.8),
                    "sieve": metric_report(0.7),
                },
            },
            {
                **base,
                "scenario": "xss",
                "seed": 7,
                "neural": {"closr": 0.8},
                "neural_reports": {"closr": metric_report(0.8)},
            },
        ]
        with self.assertRaisesRegex(ValueError, "method set mismatch"):
            aggregate(runs)


if __name__ == "__main__":
    unittest.main()
