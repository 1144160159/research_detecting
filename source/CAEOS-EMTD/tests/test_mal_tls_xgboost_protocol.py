from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path
import unittest

from create_mal_tls_xgboost_protocol import create_protocol, freeze_or_validate_protocol
from summarize_mal_tls_xgboost_multiseed import analyze


SEEDS = (7, 11, 19, 23, 29)
METRICS = (
    "accuracy",
    "f1_macro",
    "f1_weighted",
    "balanced_accuracy",
    "ece",
    "nll",
    "training_seconds",
    "inference_samples_per_second",
)


class MalTlsXgboostProtocolTests(unittest.TestCase):
    def fixture(self, root: Path) -> tuple[dict, Path]:
        csv_path = root / "malicious_TLS.csv"
        config_path = root / "mal_tls2023.json"
        implementation = root / "train_classical.py"
        generator = root / "create_mal_tls_xgboost_protocol.py"
        runner = root / "scripts" / "run_mal_tls_xgboost_multiseed.sh"
        summarizer = root / "summarize_mal_tls_xgboost_multiseed.py"
        runner.parent.mkdir(parents=True)
        csv_path.write_text("label,value\nBenign,0\n", encoding="ascii")
        config_path.write_text('{"label_column":"label"}\n', encoding="ascii")
        implementation.write_text("print('fixture')\n", encoding="ascii")
        generator.write_text("print('protocol')\n", encoding="ascii")
        runner.write_text("#!/bin/sh\n", encoding="ascii")
        summarizer.write_text("print('summary')\n", encoding="ascii")
        protocol = create_protocol(root, csv_path, config_path, "2.1.4", 0)
        return protocol, implementation

    def write_runs(self, root: Path, protocol: dict) -> tuple[Path, Path]:
        run_root = root / "runs"
        mc7_root = root / "mc7"
        for index, seed in enumerate(protocol["seeds"]):
            value = 0.8 + index * 0.01
            row = {metric: value for metric in METRICS}
            row.update(
                {
                    "model": "xgboost",
                    "seed": seed,
                    "selection_evidence": {
                        "unknown_or_test_labels_used_for_fitting_or_selection": False
                    },
                }
            )
            reference = {metric: value - 0.02 for metric in METRICS}
            reference["seed"] = seed
            xgb_path = run_root / ("seed%d" % seed)
            mc7_path = mc7_root / ("mc5_seed%d" % seed)
            xgb_path.mkdir(parents=True)
            mc7_path.mkdir(parents=True)
            (xgb_path / "metrics.json").write_text(json.dumps(row), encoding="utf-8")
            (mc7_path / "metrics.json").write_text(
                json.dumps(reference), encoding="utf-8"
            )
        return run_root, mc7_root

    def test_protocol_is_zero_result_frozen_and_bound(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            protocol, _ = self.fixture(Path(directory))
        self.assertEqual(protocol["status"], "frozen_before_results")
        self.assertEqual(protocol["expected_runs"], 5)
        self.assertEqual(protocol["benign_class"], "benign")
        self.assertEqual(
            sorted(protocol["implementation_sha256"]),
            ["protocol_generator", "runner", "summarizer", "trainer"],
        )
        self.assertEqual(protocol["metrics_identity_field"], "seed")
        self.assertFalse(protocol["test_labels_used_for_fitting_or_selection"])

    def test_protocol_rejects_nonzero_results_and_implementation_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol, implementation = self.fixture(root)
            path = root / "protocol.json"
            with self.assertRaisesRegex(ValueError, "zero results"):
                freeze_or_validate_protocol(path, protocol, 1)
            freeze_or_validate_protocol(path, protocol, 0)
            implementation.write_text("print('changed')\n", encoding="ascii")
            changed = create_protocol(
                root, root / "malicious_TLS.csv", root / "mal_tls2023.json", "2.1.4", 0
            )
            with self.assertRaisesRegex(ValueError, "differs from current evidence"):
                freeze_or_validate_protocol(path, changed, 5)

    def test_summary_has_five_paired_runs_and_no_leak(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol, _ = self.fixture(root)
            run_root, mc7_root = self.write_runs(root, protocol)
            result = analyze(protocol, run_root, mc7_root)
        self.assertEqual(result["run_count"], 5)
        self.assertEqual(result["failure_count"], 0)
        self.assertAlmostEqual(
            result["paired_xgboost_minus_mc7_stable"]["f1_macro"]["mean"], 0.02
        )

    def test_summary_rejects_selection_leak_or_nonfinite_metric(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol, _ = self.fixture(root)
            run_root, mc7_root = self.write_runs(root, protocol)
            path = run_root / "seed7" / "metrics.json"
            row = json.loads(path.read_text(encoding="utf-8"))
            row["selection_evidence"][
                "unknown_or_test_labels_used_for_fitting_or_selection"
            ] = True
            path.write_text(json.dumps(row), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "selection evidence"):
                analyze(protocol, run_root, mc7_root)
            row["selection_evidence"][
                "unknown_or_test_labels_used_for_fitting_or_selection"
            ] = False
            row["f1_macro"] = float("nan")
            path.write_text(json.dumps(row), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "finite"):
                analyze(protocol, run_root, mc7_root)

    def test_summary_rejects_protocol_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol, _ = self.fixture(root)
            run_root, mc7_root = self.write_runs(root, protocol)
            tampered = copy.deepcopy(protocol)
            tampered["max_depth"] = 9
            with self.assertRaisesRegex(ValueError, "SHA mismatch"):
                analyze(tampered, run_root, mc7_root)


if __name__ == "__main__":
    unittest.main()
