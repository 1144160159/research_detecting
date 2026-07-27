from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from create_strict_v4_ustc_deployment_package_design import (
    PAIRWISE,
    VGRF,
)
from create_strict_v4_ustc_deployment_package_protocol import (
    create_protocol,
)
from summarize_strict_v4_ustc_deployment_packages import summarize


ROOT = Path(__file__).resolve().parent.parent


def write_canonical(path: Path, payload: dict) -> None:
    payload["manifest_sha256"] = canonical_hash(payload)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


class USTCDeploymentPackageTests(unittest.TestCase):
    def make_design(self, root: Path) -> tuple[Path, Path]:
        result_root = root / "results"
        design_path = root / "design.json"
        design = {
            "schema_version": "strict_v4_ustc_deployment_package_design_v1",
            "selection_source": {
                "schema_version": (
                    "strict_v4_final_self_algorithm_selection_v1"
                ),
                "allowed_algorithms": [PAIRWISE, VGRF],
            },
            "implementation_sha256": {},
            "output_policy": {
                "result_root": str(result_root),
                "run_root": str(root / "runs"),
            },
            "vgrf_policy": {"known_only_parameters": {"x": 1}},
            "package_matrix": {"inputs": [], "package_count": 20},
            "pairwise_policy": {},
            "parrot_feature_contract": {"feature_count": 56},
            "execution_policy": {},
            "claim_boundary": {},
        }
        write_canonical(design_path, design)
        return design_path, result_root

    def make_selection(self, root: Path, algorithm: str) -> Path:
        selection_path = root / "selection.json"
        selection = {
            "schema_version": "strict_v4_final_self_algorithm_selection_v1",
            "selected_algorithm": algorithm,
            "vgrf_confirmation_passes": algorithm == VGRF,
        }
        write_canonical(selection_path, selection)
        return selection_path

    def test_pairwise_protocol_freezes_without_vgrf_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            design_path, _ = self.make_design(root)
            selection_path = self.make_selection(root, PAIRWISE)
            protocol = create_protocol(
                design_path,
                selection_path,
                root,
                root / "missing_protocol.json",
                root / "missing_summary.json",
            )
        self.assertEqual(
            protocol["selection"]["selected_algorithm"], PAIRWISE
        )
        self.assertIsNone(protocol["vgrf_binding"])
        self.assertFalse(protocol["external_execution_admitted"])

    def test_vgrf_protocol_requires_full102_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            design_path, _ = self.make_design(root)
            selection_path = self.make_selection(root, VGRF)
            with self.assertRaises(FileNotFoundError):
                create_protocol(
                    design_path,
                    selection_path,
                    root,
                    root / "missing_protocol.json",
                    root / "missing_summary.json",
                )

    def make_summary_protocol(self, root: Path) -> dict:
        packages = []
        for scenario in (
            "cridex",
            "geodo",
            "htbot",
            "miuref",
            "neris",
            "nsis_ay",
            "shifu",
            "tinba",
            "virut",
            "zeus",
        ):
            for seed in (311, 313):
                packages.append(
                    {
                        "package_id": f"{scenario}_seed{seed}",
                        "scenario": scenario,
                        "training_seed": seed,
                    }
                )
        protocol = {
            "selection": {"selected_algorithm": PAIRWISE},
            "package_matrix": {"inputs": packages},
            "output_policy": {"result_root": str(root / "results")},
            "parrot_feature_contract": {"feature_count": 56},
        }
        protocol["manifest_sha256"] = canonical_hash(protocol)
        return protocol

    def materialize_records(
        self, root: Path, protocol: dict, omit_audit: bool = False
    ) -> None:
        audit_path = root / "audit.json"
        audit_path.write_text('{"passes": true}\n', encoding="utf-8")
        audit_entry = {
            "path": str(audit_path),
            "sha256": file_hash(audit_path),
        }
        for package in protocol["package_matrix"]["inputs"]:
            package_root = (
                Path(protocol["output_policy"]["result_root"])
                / "packages"
                / package["package_id"]
            )
            package_root.mkdir(parents=True, exist_ok=True)
            artifact = package_root / "bundle.joblib"
            artifact.write_bytes(package["package_id"].encode("ascii"))
            audits = {
                "pairwise": audit_entry,
                "selected": audit_entry,
                "parrot_feature_contract": audit_entry,
            }
            if omit_audit and package["package_id"] == "cridex_seed311":
                audits.pop("parrot_feature_contract")
            record = {
                "schema_version": (
                    "strict_v4_ustc_deployment_package_record_v1"
                ),
                "protocol_manifest_sha256": protocol["manifest_sha256"],
                "package_id": package["package_id"],
                "scenario": package["scenario"],
                "training_seed": package["training_seed"],
                "selected_algorithm": PAIRWISE,
                "selected_artifact": str(artifact),
                "selected_artifact_sha256": file_hash(artifact),
                "selected_artifact_bytes": artifact.stat().st_size,
                "audits": audits,
                "formal_model_metrics_admitted": 0,
                "external_execution_admitted": False,
                "storage_policy": "gpu_private_do_not_publish",
            }
            (package_root / "package_record.json").write_text(
                json.dumps(record) + "\n", encoding="utf-8"
            )

    def test_summary_requires_and_counts_all_twenty_packages(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            protocol = self.make_summary_protocol(root)
            self.materialize_records(root, protocol)
            result = summarize(protocol, root)
        self.assertEqual(result["package_count"], 20)
        self.assertEqual(result["scenario_count"], 10)
        self.assertEqual(result["seed_counts"], {"311": 10, "313": 10})
        self.assertTrue(result["external_execution_admitted"])

    def test_summary_fails_when_required_audit_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            protocol = self.make_summary_protocol(root)
            self.materialize_records(root, protocol, omit_audit=True)
            with self.assertRaisesRegex(ValueError, "required package audits"):
                summarize(protocol, root)

    def test_watcher_is_selection_and_idle_gated(self) -> None:
        watcher = (
            ROOT
            / "scripts"
            / "wait_and_run_strict_v4_ustc_deployment_packages.sh"
        ).read_text(encoding="utf-8")
        self.assertIn("final_selection.json", watcher)
        self.assertIn("five consecutive idle samples passed", watcher)
        self.assertIn(
            "create_strict_v4_ustc_deployment_package_protocol.py", watcher
        )


if __name__ == "__main__":
    unittest.main()
