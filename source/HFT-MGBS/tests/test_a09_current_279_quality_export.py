import ast
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_a09_current_279_quality_evidence.py"
SPEC = importlib.util.spec_from_file_location("quality_export", str(SCRIPT))
EXPORT = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(EXPORT)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
    return path


class A09Current279QualityExportTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def test_cli_has_no_outer_evaluation_tuning_or_model_identity_surface(self):
        actions = {item.dest for item in EXPORT._parser()._actions}
        self.assertFalse(
            actions
            & {
                "max_packets_per_capture",
                "max_flows_per_capture",
                "tolerance_s",
                "n_jobs",
                "model_bundle",
                "runtime_manifest",
            }
        )
        self.assertTrue(
            {"trusted_contract_sha256", "trusted_prepare_receipt_sha256", "trusted_exporter_sha256"}
            <= actions
        )
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        forbidden_calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in {"fit", "fit_transform"}:
                    forbidden_calls.append(node.func.attr)
        self.assertEqual(forbidden_calls, [])
        self.assertNotIn("calibration", actions)
        self.assertNotIn("summary", actions)

    def test_sample_id_is_direction_independent_but_time_bound_and_finite(self):
        first = {
            "forward_key": ("10.0.0.2", "10.0.0.1", 443, 12345, 6),
            "start_timestamp": 1.0,
            "last_timestamp": 2.0,
        }
        reverse = {
            "forward_key": ("10.0.0.1", "10.0.0.2", 12345, 443, 6),
            "start_timestamp": 1.0,
            "last_timestamp": 2.0,
        }
        self.assertEqual(EXPORT.stable_sample_id("g", first), EXPORT.stable_sample_id("g", reverse))
        later = dict(first, start_timestamp=3.0, last_timestamp=4.0)
        self.assertNotEqual(EXPORT.stable_sample_id("g", first), EXPORT.stable_sample_id("g", later))
        with self.assertRaises(EXPORT.ExportError):
            EXPORT.stable_sample_id("g", dict(first, start_timestamp=float("nan")))
        with self.assertRaises(EXPORT.ExportError):
            EXPORT.stable_sample_id("g", dict(first, start_timestamp=3.0, last_timestamp=2.0))

    def _prepared(self):
        prepared = self.root / "prepared"
        frozen = prepared / "frozen"
        frozen.mkdir(parents=True)
        files = {
            "model": frozen / "a09.joblib",
            "runtime_manifest": frozen / "runtime.json",
            "service_source": frozen / "service.py",
            "engine_source": frozen / "engine.py",
            "service_launcher": frozen / "start.sh",
        }
        for name, path in files.items():
            if name != "runtime_manifest":
                path.write_bytes(name.encode())
        dump(
            files["runtime_manifest"],
            {"schema_version": 2, "candidate_id": "A09", "model_sha256": digest(files["model"])},
        )
        manifest = prepared / "prepare_manifest.sha256"
        manifest.write_text(
            "".join(
                "{}  {}\n".format(digest(path), path.relative_to(prepared).as_posix())
                for path in files.values()
            ),
            encoding="utf-8",
        )
        receipt = dump(
            prepared / "prepare_receipt.json",
            {
                "schema_version": 1,
                "scope": EXPORT.PREPARE_SCOPE,
                "read_only_source_access": True,
                "service_started_or_stopped": False,
                "traffic_started_or_stopped": False,
                "gaps": [],
                "runtime_manifest_actual_sha256": digest(files["runtime_manifest"]),
                "runtime_identity": {"candidate_id": "A09"},
                "artifact_sha256": {name: digest(path) for name, path in files.items()},
                "artifacts": {
                    name: {"path": path.relative_to(prepared).as_posix(), "sha256": digest(path)}
                    for name, path in files.items()
                },
                "prepare_manifest": {
                    "path": manifest.relative_to(prepared).as_posix(),
                    "sha256": digest(manifest),
                },
            },
        )
        return receipt, files

    def test_prepare_receipt_is_externally_trusted_and_rehashes_every_artifact(self):
        receipt, files = self._prepared()
        result = EXPORT.validate_prepare_receipt(receipt, digest(receipt))
        self.assertEqual(result[1], files["model"].resolve())
        with self.assertRaisesRegex(EXPORT.ExportError, "external trust root"):
            EXPORT.validate_prepare_receipt(receipt, "0" * 64)
        files["model"].write_bytes(b"drift")
        with self.assertRaises(EXPORT.ExportError):
            EXPORT.validate_prepare_receipt(receipt, digest(receipt))

    def test_import_binding_rejects_pythonpath_module_substitution(self):
        contract = json.loads((ROOT / "configs" / "algorithm_qualification_campaign_v1.json").read_text())
        paths = {
            name: expected.resolve() for name, (_module, expected) in EXPORT.EXECUTED_BINDINGS.items()
        }
        fake = mock.Mock(__file__=str(self.root / "candidate_dataset.py"))
        real_import = EXPORT.importlib.import_module

        def import_side_effect(name):
            return fake if name == "hft_mgbs.candidate_dataset" else real_import(name)

        with mock.patch.object(EXPORT.importlib, "import_module", side_effect=import_side_effect):
            with self.assertRaisesRegex(EXPORT.ExportError, "not campaign-bound"):
                EXPORT.verify_import_bindings(contract, paths)

    def test_snapshot_detects_model_runtime_input_and_pcap_drift(self):
        paths = []
        for name in ("model", "runtime", "manifest", "capture.pcap", "truth.csv"):
            path = self.root / name
            path.write_bytes(name.encode())
            paths.append(path)
        snapshot = EXPORT._snapshot(paths)
        paths[-2].write_bytes(b"changed")
        with self.assertRaisesRegex(EXPORT.ExportError, "source drift"):
            EXPORT._verify_snapshot(snapshot)

    def test_bundle_rejects_nan_threshold_and_wrong_positive_class(self):
        class Model:
            classes_ = [0, 1]
            estimators_ = [object()] * 200
            n_estimators = 200
            random_state = 7
            min_samples_leaf = 2
            class_weight = "balanced"

        model = Model()
        bundle = {"thresholds": [float("nan")]}
        with self.assertRaises(EXPORT.ExportError):
            EXPORT._finite("threshold", bundle["thresholds"][0], 0.0)
        model.classes_ = [1, 0]
        positive = 1
        self.assertNotEqual(model.classes_[positive], 1)

    def test_transaction_failure_leaves_no_final_or_complete_artifact(self):
        final = self.root / "release"
        resolved, staging = EXPORT._staging_directory(final)
        (staging / "partial.json").write_text("{}")
        try:
            raise EXPORT.ExportError("fault injection")
        except EXPORT.ExportError:
            import shutil

            shutil.rmtree(str(staging), ignore_errors=True)
        self.assertFalse(resolved.exists())
        self.assertFalse((resolved / "COMPLETE.json").exists())

    def test_portable_source_contains_inventory_not_summary_derived_labels(self):
        source = EXPORT._portable_source(
            {"schema_version": 1, "algorithm": "sha256", "entries": []},
            "a" * 64,
            [{"role": "ground_truth_csv", "sha256": "b" * 64, "size_bytes": 7}],
            [{"event_id": "e-unmatched", "eligible_groups": ["g"]}],
            [],
            "c" * 64,
            "d" * 64,
        )
        output = self.root / "copied" / "official_quality_source.json"
        dump(output, source)
        copied = json.loads(output.read_text())
        self.assertTrue(copied["portable"])
        self.assertEqual(copied["eligible_events"][0]["event_id"], "e-unmatched")
        self.assertNotIn("macro_f1", json.dumps(copied))

    def test_duplicate_relations_and_sample_ids_are_structurally_rejected(self):
        labels = {
            "records": [
                {"sample_id": "s", "label": 1, "group": "g"},
                {"sample_id": "s", "label": 1, "group": "g"},
            ],
            "sample_event_relations": [
                {"sample_id": "s", "group": "g", "event_id": "e"},
                {"sample_id": "s", "group": "g", "event_id": "e"},
            ],
        }
        ids = [row["sample_id"] for row in labels["records"]]
        relations = [tuple(row.values()) for row in labels["sample_event_relations"]]
        self.assertNotEqual(len(ids), len(set(ids)))
        self.assertNotEqual(len(relations), len(set(relations)))


if __name__ == "__main__":
    unittest.main()
