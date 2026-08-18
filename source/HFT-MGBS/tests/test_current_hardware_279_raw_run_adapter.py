from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

import test_current_hardware_279_v2 as fixture_module


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from compose_current_hardware_279_raw_run_v2 import AdapterError, bind_runner_evidence


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CurrentHardware279RawRunAdapterTest(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture_module.CurrentHardware279V2Test(methodName="test_positive_raw_run_recomputes_and_remains_nonproduction")
        self.fixture.setUp()
        self.root = self.fixture.root
        _input, self.request = self.fixture.raw_fixture("normal", 1)
        auto_copies = {
            "runner": "frozen/runner.sh",
            "config": "frozen/config.json",
            "capture_binary": "frozen/tpacket_v3_full_pipeline",
            "pipeline_raw": "pipeline_raw.json",
            "diagnostic_receipt": "diagnostic_receipt.json",
            "pipeline_ready": "pipeline_ready.json",
            "execution_events": "execution_events.tsv",
            "nic_statistics_before": "before_ens8f0_statistics.txt",
            "nic_statistics_after": "pre_restore_ens8f0_statistics.txt",
        }
        for name, relative in auto_copies.items():
            source = self.root / self.request["artifacts"][name]["path"]
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.resolve() != target.resolve():
                shutil.copyfile(source, target)
        shutil.copyfile(
            self.root / self.request["pktgen_devices"][0]["path"],
            self.root / "pktgen_device_0.txt",
        )
        self.source_manifest = self.root / "evidence.sha256"
        self.reseal_source_manifest()

    def tearDown(self):
        self.fixture.tearDown()

    def reseal_source_manifest(self):
        rows = []
        for path in sorted(self.root.rglob("*")):
            if not path.is_file() or path.is_symlink() or path == self.source_manifest:
                continue
            if any(part.startswith("adapter-work") for part in path.relative_to(self.root).parts):
                continue
            rows.append(f"{digest(path)}  {path.relative_to(self.root).as_posix()}\n")
        self.source_manifest.write_bytes("".join(rows).encode("utf-8"))

    def staged(self):
        return {
            name: self.root / self.request["artifacts"][name]["path"]
            for name in (
                "model",
                "runtime_manifest",
                "service_source",
                "engine_source",
                "service_launcher",
                "identity_receipt",
                "window_observations",
                "physical_resources",
                "service_resources",
            )
        }

    def bind(self, work_name="adapter-work"):
        return bind_runner_evidence(
            profile_path=fixture_module.PROFILE,
            evidence_dir=self.root,
            binding_root=self.root,
            work_dir=self.root / work_name,
            campaign_id=self.fixture.campaign,
            candidate_id=self.fixture.candidate,
            backend=self.fixture.backend,
            mode="normal",
            repeat_index=1,
            source_manifest=self.source_manifest,
            staged_artifacts=self.staged(),
            quality_labels=self.root / self.request["quality"]["labels"]["path"],
            quality_predictions=self.root / self.request["quality"]["predictions"]["path"],
            fallback_events=None,
        )

    def test_complete_staged_evidence_generates_small_bound_receipt(self):
        result, input_path, binding_manifest = self.bind()
        self.assertTrue(result["run_qualified"], result["errors"])
        self.assertEqual(result["evidence_gaps"], [])
        self.assertTrue(result["adapter"]["source_manifest_verified"])
        self.assertTrue(result["adapter"]["binding_manifest_verified_by_composer"])
        self.assertTrue(input_path.is_file())
        self.assertTrue(binding_manifest.is_file())
        self.assertFalse(result["production_release_accepted"])
        self.assertFalse(result["final_pareto_ingestion_allowed"])
        # The receipt contains derived metrics/hashes, not raw label records or
        # latency arrays, and therefore remains small.
        serialized = json.dumps(result, allow_nan=False).encode()
        self.assertLess(len(serialized), 100_000)
        self.assertNotIn(b'"records"', serialized)

    def test_missing_supplement_is_explicit_and_never_synthesized(self):
        staged = self.staged()
        staged["service_resources"] = None
        result, _, _ = bind_runner_evidence(
            profile_path=fixture_module.PROFILE,
            evidence_dir=self.root,
            binding_root=self.root,
            work_dir=self.root / "adapter-work-missing",
            campaign_id=self.fixture.campaign,
            candidate_id=self.fixture.candidate,
            backend=self.fixture.backend,
            mode="normal",
            repeat_index=1,
            source_manifest=self.source_manifest,
            staged_artifacts=staged,
            quality_labels=self.root / self.request["quality"]["labels"]["path"],
            quality_predictions=self.root / self.request["quality"]["predictions"]["path"],
            fallback_events=None,
        )
        self.assertFalse(result["run_qualified"])
        self.assertIn("missing:service_resources", result["evidence_gaps"])
        self.assertTrue(any("service" in error for error in result["errors"]))
        self.assertFalse(result["production_release_accepted"])

    def test_runner_manifest_hash_drift_aborts_before_composition(self):
        (self.root / "pipeline_raw.json").write_bytes(b"tampered\n")
        with self.assertRaisesRegex(AdapterError, "hash drift"):
            self.bind("adapter-work-tamper")

    def test_cli_missing_evidence_returns_two_and_writes_gap_receipt(self):
        output = self.root / "adapter-work-cli" / "raw.json"
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "compose_current_hardware_279_raw_run_v2.py"),
                "--profile", str(fixture_module.PROFILE),
                "--evidence-dir", str(self.root),
                "--work-dir", str(self.root / "adapter-work-cli"),
                "--campaign-id", self.fixture.campaign,
                "--candidate-id", self.fixture.candidate,
                "--backend", self.fixture.backend,
                "--mode", "normal",
                "--repeat-index", "1",
                "--output", str(output),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(completed.returncode, 2, completed.stderr)
        receipt = json.loads(output.read_text(encoding="utf-8"))
        self.assertFalse(receipt["run_qualified"])
        self.assertIn("missing:model", receipt["evidence_gaps"])
        self.assertIn("missing:window_observations", receipt["evidence_gaps"])
        self.assertIn("missing:quality_labels", receipt["evidence_gaps"])


if __name__ == "__main__":
    unittest.main()
