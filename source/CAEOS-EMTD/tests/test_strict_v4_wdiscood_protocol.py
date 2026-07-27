from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_wdiscood_pilot_protocol import create_protocol, select_scenarios


SUITES = ("a", "b", "c", "d", "e", "f", "g")


def metrics(model: str, report: str, fingerprint: str) -> dict[str, object]:
    return {
        "model": model,
        "reports": {report: {}},
        "split_metadata": {"split_fingerprint": {"combined": fingerprint}},
    }


class StrictV4WDiscOODProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.mlp_root = root / "mlp"
        self.opendetect_root = root / "opendetect"
        self.coverage = {
            "schema_version": "strict_v4_coverage_manifest_v2",
            "manifest_sha256": "coverage-sha",
            "scenario_registry": {
                suite: {"scenarios": [f"scenario_{suite}_{index}" for index in (1, 2, 3)]}
                for suite in SUITES
            },
        }
        self.selected = select_scenarios(self.coverage)
        for suite, scenarios in self.selected.items():
            for scenario in scenarios:
                fingerprint = f"fp-{suite}-{scenario}"
                for run, payload in (
                    (
                        self.mlp_root / suite / f"{scenario}_seed7_mlp",
                        metrics("mlp", "mahalanobis", fingerprint),
                    ),
                    (
                        self.opendetect_root / suite / f"{scenario}_seed7_opendetect",
                        metrics("opendetect", "opendetect", fingerprint),
                    ),
                ):
                    run.mkdir(parents=True)
                    (run / "metrics.json").write_text(json.dumps(payload), encoding="utf-8")
                    (run / "scores.npz").write_bytes(b"scores")
                    (run / "model.pt").write_bytes(b"model")
        self.implementations = {}
        for name in ("calibrator", "evaluator", "protocol_creator", "runner", "summarizer"):
            path = root / f"{name}.py"
            path.write_text(name, encoding="ascii")
            self.implementations[name] = path

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_protocol_freezes_fourteen_sha_bound_sources(self) -> None:
        protocol = create_protocol(
            self.coverage,
            "coverage-file-sha",
            self.mlp_root,
            self.opendetect_root,
            self.implementations,
        )
        self.assertEqual(protocol["expected_scenarios"], 14)
        self.assertEqual(len(protocol["sources"]), 14)
        self.assertEqual(protocol["manifest_sha256"], canonical_hash(protocol))
        self.assertEqual(protocol["method_definition"]["alpha"], 1.0)
        self.assertFalse(protocol["unknown_or_test_labels_used_for_fitting_or_selection"])

    def test_protocol_rejects_split_mismatch(self) -> None:
        scenario = self.selected["a"][0]
        path = self.opendetect_root / "a" / f"{scenario}_seed7_opendetect" / "metrics.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["split_metadata"]["split_fingerprint"]["combined"] = "different"
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "split mismatch"):
            create_protocol(
                self.coverage,
                "coverage-file-sha",
                self.mlp_root,
                self.opendetect_root,
                self.implementations,
            )


if __name__ == "__main__":
    unittest.main()
