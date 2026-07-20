import json
from pathlib import Path
import tempfile
import unittest

from create_strict_v4_dcc_pilot_protocol import create_protocol, select_scenarios
from create_strict_v4_external_confirmation_protocol import canonical_hash


SUITES = ("a", "b", "c", "d", "e", "f", "g")


def metrics(model: str, report: str, fingerprint: str) -> dict[str, object]:
    return {
        "model": model,
        "reports": {report: {}},
        "split_metadata": {"split_fingerprint": {"combined": fingerprint}},
    }


class StrictV4DccProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.mlp_root = root / "mlp"
        self.opendetect_root = root / "opendetect"
        self.pp_root = root / "mahalanobis_pp"
        self.coverage = {
            "schema_version": "strict_v4_coverage_manifest_v2",
            "manifest_sha256": "coverage-sha",
            "scenario_registry": {
                suite: {"scenarios": [f"scenario_{suite}_{index}" for index in range(1, 4)]}
                for suite in SUITES
            },
        }
        self.selected = select_scenarios(self.coverage)
        for suite, scenarios in self.selected.items():
            for scenario in scenarios:
                fingerprint = f"fp-{suite}-{scenario}"
                runs = (
                    (
                        self.mlp_root / suite / f"{scenario}_seed7_mlp",
                        metrics("mlp", "mahalanobis", fingerprint),
                        ("metrics.json", "scores.npz", "model.pt"),
                    ),
                    (
                        self.opendetect_root / suite / f"{scenario}_seed7_opendetect",
                        metrics("opendetect", "opendetect", fingerprint),
                        ("metrics.json", "scores.npz", "model.pt"),
                    ),
                    (
                        self.pp_root / suite / f"{scenario}_seed7_mahalanobis_pp",
                        metrics("mlp_posthoc_mahalanobis_pp", "mahalanobis_pp", fingerprint),
                        ("metrics.json", "scores.npz", "provenance.json"),
                    ),
                )
                for run, payload, names in runs:
                    run.mkdir(parents=True)
                    for name in names:
                        if name == "metrics.json":
                            (run / name).write_text(json.dumps(payload), encoding="utf-8")
                        else:
                            (run / name).write_bytes(name.encode("ascii"))
        self.implementations = {}
        for name in ("calibrator", "evaluator", "protocol_creator", "runner", "summarizer"):
            path = root / f"{name}.py"
            path.write_text(name, encoding="ascii")
            self.implementations[name] = path

    def tearDown(self) -> None:
        self.temp.cleanup()

    def build(self) -> dict[str, object]:
        return create_protocol(
            self.coverage,
            "coverage-file-sha",
            self.mlp_root,
            self.opendetect_root,
            self.pp_root,
            self.implementations,
        )

    def test_protocol_freezes_fourteen_sources_and_parameters(self) -> None:
        protocol = self.build()
        self.assertEqual(protocol["expected_scenarios"], 14)
        self.assertEqual(len(protocol["sources"]), 14)
        self.assertEqual(protocol["manifest_sha256"], canonical_hash(protocol))
        self.assertFalse(protocol["unknown_or_test_labels_used_for_fitting_or_selection"])
        self.assertEqual(protocol["method_definition"]["requested_residual_dimension"], 50)
        self.assertTrue(protocol["method_definition"]["parameters_frozen_without_ood_validation"])
        self.assertEqual(
            protocol["expansion_gate"]["mean_unknown_metric_rank_among_four_maximum"],
            2.0,
        )

    def test_selection_is_deterministic(self) -> None:
        self.assertEqual(self.selected, select_scenarios(self.coverage))

    def test_protocol_rejects_split_mismatch(self) -> None:
        scenario = self.selected["a"][0]
        path = self.pp_root / "a" / f"{scenario}_seed7_mahalanobis_pp" / "metrics.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["split_metadata"]["split_fingerprint"]["combined"] = "different"
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "split mismatch"):
            self.build()


if __name__ == "__main__":
    unittest.main()
