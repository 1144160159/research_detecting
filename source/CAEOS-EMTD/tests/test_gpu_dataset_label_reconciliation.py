from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from audit_krc_downstream_data_readiness_v2 import prepared_dataset
from create_gpu_dataset_label_reconciliation_protocol import (
    create_protocol,
    verify_protocol,
)
from create_gpu_external_preparation_protocol_v2 import (
    create_protocol as create_preparation_protocol,
    verify_protocol as verify_preparation_protocol,
)
from external_dataset_labels import canonical_external_label
from external_dataset_protocol_utils import file_hash
from prepare_gpu_external_datasets_v2 import prepare_dataset
from reconcile_gpu_dataset_admission_labels import reconcile


FAMILIES = [
    "DrDoS_DNS",
    "DrDoS_LDAP",
    "DrDoS_MSSQL",
    "DrDoS_NTP",
    "DrDoS_NetBIOS",
    "DrDoS_SNMP",
    "DrDoS_SSDP",
    "DrDoS_UDP",
    "LDAP",
    "MSSQL",
    "NetBIOS",
    "Portmap",
    "Syn",
    "TFTP",
    "UDP",
    "UDPLag",
]


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


class GpuDatasetLabelReconciliationTests(unittest.TestCase):
    def test_alias_is_member_bound(self) -> None:
        self.assertEqual(
            canonical_external_label(
                "CICDDoS2019", "01-12/UDPLag.csv", " UDP-lag "
            ),
            "UDPLag",
        )
        self.assertEqual(
            canonical_external_label(
                "CICDDoS2019", "01-12/UDPLag.csv", "WebDDoS"
            ),
            "WebDDoS",
        )
        with self.assertRaisesRegex(ValueError, "outside its canonical member"):
            canonical_external_label(
                "CICDDoS2019", "01-12/Syn.csv", "UDP-lag"
            )

    def _fixture(self, root: Path) -> tuple[dict, dict, Path]:
        sources = []
        source_hashes = {}
        for index in range(3):
            path = root / f"source{index}.zip"
            path.write_bytes(f"source-{index}".encode())
            sources.append(
                {
                    "path": str(path),
                    "size_bytes": path.stat().st_size,
                    "member_count": 1,
                    "central_directory_sha256": str(index) * 64,
                }
            )
            source_hashes[str(path)] = file_hash(path)
        expansion = {
            "schema_version": "gpu_malicious_dataset_expansion_protocol_v1",
            "status": "frozen_before_full_scan_and_training",
            "source_identity": sources,
            "datasets": {"CICDDoS2019": {"families": FAMILIES}},
        }
        cic_labels = {family: 3 for family in FAMILIES}
        cic_groups = dict(cic_labels)
        cic_labels["UDPLag"] = 1_873
        cic_groups["UDPLag"] = 1_873
        cic_labels.update(
            {"BENIGN": 10, "UDP-lag": 366_461, "WebDDoS": 439}
        )
        cic_groups.update(
            {"BENIGN": 10, "UDP-lag": 366_461, "WebDDoS": 439}
        )
        checks = {
            "has_rows": True,
            "has_benign": True,
            "all_expected_attack_families_observed": True,
            "no_unexpected_attack_labels": False,
            "no_missing_labels": True,
            "minimum_three_groups_per_label": True,
            "zero_cross_label_groups": True,
            "zero_missing_group_rows": True,
            "required_features_present_in_every_member": True,
        }
        failed = {
            "schema_version": "gpu_malicious_dataset_full_admission_audit_v1",
            "status": "complete",
            "admission_passed": False,
            "source_sha256": source_hashes,
            "datasets": {
                "LSNM2024": {
                    "rows": 20,
                    "admission_passed": True,
                    "checks": {"has_rows": True},
                },
                "CICDDoS2019": {
                    "rows": sum(cic_labels.values()),
                    "label_counts": cic_labels,
                    "groups_by_label": cic_groups,
                    "checks": checks,
                    "admission_passed": False,
                },
            },
        }
        scans = root / "scans"
        write_json(
            scans / "alias.json",
            {
                "member": "01-12/UDPLag.csv",
                "member_crc32": "5d5e840e",
                "member_uncompressed_size": 100,
                "label_counts": {
                    "BENIGN": 3_705,
                    "UDP-lag": 366_461,
                    "WebDDoS": 439,
                },
            },
        )
        write_json(
            scans / "canonical.json",
            {
                "member": "03-11/UDPLag.csv",
                "member_crc32": "09402b54",
                "member_uncompressed_size": 200,
                "label_counts": {"UDPLag": 1_873},
            },
        )
        return expansion, failed, scans

    def test_protocol_and_reconciled_audit_preserve_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            expansion, failed, scans = self._fixture(root)
            expansion_path = root / "expansion.json"
            failed_path = root / "failed.json"
            write_json(expansion_path, expansion)
            write_json(failed_path, failed)
            bound = []
            for name in ("reconciler.py", "preparer.py", "labels.py"):
                path = root / name
                path.write_text(name, encoding="utf-8")
                bound.append(path)
            protocol = create_protocol(
                expansion_path=expansion_path,
                failed_audit_path=failed_path,
                member_scan_root=scans,
                reconciler_path=bound[0],
                preparer_path=bound[1],
                label_module_path=bound[2],
                reconciled_output_root=root / "audit_v2",
                prepared_output_root=root / "prepared_v2",
            )
            verify_protocol(protocol)
            audit = reconcile(protocol, failed)
            self.assertTrue(audit["admission_passed"])
            cic = audit["datasets"]["CICDDoS2019"]
            self.assertNotIn("UDP-lag", cic["label_counts"])
            self.assertEqual(cic["label_counts"]["UDPLag"], 368_334)
            self.assertEqual(cic["label_counts"]["WebDDoS"], 439)
            self.assertEqual(
                sum(cic["label_counts"].values()),
                sum(failed["datasets"]["CICDDoS2019"]["label_counts"].values()),
            )

    def test_preparation_uses_canonical_alias_and_retains_webddos(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive_path = root / "cic.zip"
            rows = [
                "Source IP,Source Port,Destination IP,Destination Port,"
                "Protocol,Timestamp,Feature,Label",
                "1.1.1.1,1,2.2.2.2,2,17,t1,1.0,UDP-lag",
                "1.1.1.2,1,2.2.2.3,2,17,t2,2.0,WebDDoS",
            ]
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("01-12/UDPLag.csv", "\n".join(rows) + "\n")
            config = {
                "modalities": {"flow": ["Feature"]},
                "group_column": "Flow_Group",
                "label_column": "Label",
            }
            outputs, summary = prepare_dataset(
                dataset="CICDDoS2019",
                archive_paths=[archive_path],
                config=config,
                seeds=[223],
                groups_per_label=1,
                rows_per_group=1,
            )
            labels = {row["Label"] for row in outputs[223]}
            self.assertEqual(labels, {"UDPLag", "WebDDoS"})
            self.assertEqual(
                summary["source_label_counts"],
                {"UDPLag": 1, "WebDDoS": 1},
            )

    def test_v2_preparation_protocol_binds_reconciled_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            expansion, failed, scans = self._fixture(project)
            expansion_path = (
                project
                / "results/gpu_malicious_dataset_expansion_protocol_v1"
                / "protocol.json"
            )
            failed_path = project / "failed.json"
            write_json(expansion_path, expansion)
            write_json(failed_path, failed)
            preparer = project / "prepare_gpu_external_datasets_v2.py"
            label_module = project / "external_dataset_labels.py"
            reconciler = project / "reconciler.py"
            runner = project / "scripts/run_v2.sh"
            preparation_creator = (
                project / "create_gpu_external_preparation_protocol_v2.py"
            )
            protocol_utils = project / "external_dataset_protocol_utils.py"
            for path in (
                preparer,
                label_module,
                reconciler,
                runner,
                preparation_creator,
                protocol_utils,
            ):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(path.name, encoding="utf-8")
            for name in ("lsnm2024_external.json", "cicids2017_strict.json"):
                path = project / "configs" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("{}", encoding="utf-8")

            reconciliation = create_protocol(
                expansion_path=expansion_path,
                failed_audit_path=failed_path,
                member_scan_root=scans,
                reconciler_path=reconciler,
                preparer_path=preparer,
                label_module_path=label_module,
                reconciled_output_root=(
                    project
                    / "results/gpu_dataset_reconciled_admission_audit_v2"
                ),
                prepared_output_root=project / "prepared_v2",
            )
            reconciliation_path = (
                project
                / "results/gpu_dataset_label_reconciliation_protocol_v1"
                / "protocol.json"
            )
            write_json(reconciliation_path, reconciliation)
            admission = reconcile(reconciliation, failed)
            admission_root = (
                project / "results/gpu_dataset_reconciled_admission_audit_v2"
            )
            write_json(admission_root / "admission_audit.json", admission)
            (admission_root / "admission_passed").touch()

            protocol = create_preparation_protocol(
                project_root=project,
                data_root=project / "prepared_v2",
                result_root=project / "results/preparation_v2",
                runner=runner,
            )
            verify_preparation_protocol(protocol)
            self.assertEqual(
                protocol["datasets"]["CICDDoS2019"][
                    "expected_attack_family_count"
                ],
                17,
            )
            self.assertEqual(protocol["prepared_manifest_count_at_freeze"], 0)

    def test_readiness_checks_sidecar_labels_and_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            dataset_root = root / "CICDDoS2019"
            dataset_root.mkdir()
            files = {}
            labels = {
                "BENIGN": 1,
                "UDPLag": 1,
                "WebDDoS": 1,
                **{family: 1 for family in FAMILIES if family != "UDPLag"},
            }
            self.assertEqual(len(labels), 18)
            for seed in ("223", "227", "229"):
                csv_path = dataset_root / f"seed{seed}.csv"
                csv_path.write_text("Feature,Flow_Group,Label\n", encoding="utf-8")
                sidecar = {
                    "passed": True,
                    "rows": 18,
                    "label_counts": labels,
                    "csv_sha256": file_hash(csv_path),
                    "provenance": {
                        "reconciled_admission_audit_sha256": "a" * 64,
                        "label_reconciliation_protocol_manifest_sha256": (
                            "b" * 64
                        ),
                    },
                }
                write_json(dataset_root / f"seed{seed}.csv.json", sidecar)
                files[seed] = sidecar
            write_json(
                dataset_root / "manifest.json",
                {
                    "schema_version": (
                        "gpu_external_prepared_dataset_manifest_v1"
                    ),
                    "dataset": "CICDDoS2019",
                    "files": files,
                    "passed": True,
                },
            )
            (dataset_root / "preparation_complete").touch()
            result = prepared_dataset(
                data_root=root,
                dataset="CICDDoS2019",
                expected_label_count=18,
                admission_file_sha256="a" * 64,
                reconciliation_manifest_sha256="b" * 64,
            )
            self.assertTrue(result["passes"])
            self.assertTrue(
                all(
                    row["passes"] for row in result["seed_checks"].values()
                )
            )


if __name__ == "__main__":
    unittest.main()
