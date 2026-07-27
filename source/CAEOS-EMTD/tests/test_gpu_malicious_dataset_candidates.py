import csv
import tempfile
import unittest
import zipfile
from pathlib import Path

from audit_gpu_malicious_dataset_candidates import sample_csv_rows, sample_zip_members
from create_gpu_dataset_expansion_protocol import (
    build_protocol,
    central_directory_identity,
)


class GpuMaliciousDatasetCandidateAuditTests(unittest.TestCase):
    def test_sample_detects_label_columns_without_full_scan(self) -> None:
        sample = sample_csv_rows(
            ["feature,Attack_type,Label\n", "1,DDoS,1\n", "2,Benign,0\n"],
            limit=1,
        )
        self.assertEqual(sample["sampled_rows"], 1)
        self.assertEqual(sample["candidate_label_columns"], ["Attack_type", "Label"])
        self.assertEqual(sample["candidate_label_samples"]["Attack_type"], ["DDoS"])

    def test_zip_sampler_reads_each_csv_member(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dataset.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("Malicious/DDoS/a.csv", "x,label\n1,DDoS\n")
                archive.writestr("Benign/b.csv", "x,label\n2,Benign\n")
                archive.writestr("README.txt", "ignored")
            records = sample_zip_members(path)
            self.assertEqual(len(records), 2)
            self.assertEqual(
                {Path(record["member"]).name for record in records},
                {"a.csv", "b.csv"},
            )

    def test_protocol_freezes_archives_and_self_algorithm_track(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archives = []
            for name in ("lsnm.zip", "ddos1.zip", "ddos2.zip"):
                path = root / name
                with zipfile.ZipFile(path, "w") as archive:
                    archive.writestr("data.csv", "x,label\n1,attack\n")
                archives.append(str(path))
            audit = {
                "status": "complete_sampled_read_only_audit",
                "candidates": {
                    "LSNM2024": {
                        "admission_status": "priority_1_prepare_grouped_open_set",
                        "source_files": archives[:1],
                        "malicious_families_from_paths": [f"a{i}" for i in range(15)],
                    },
                    "CICDDoS2019": {
                        "admission_status": "priority_2_ddos_family_external_suite",
                        "source_files": archives[1:],
                        "attack_families_from_paths": [f"d{i}" for i in range(16)],
                    },
                },
            }
            protocol = build_protocol(audit)
            self.assertEqual(len(protocol["source_identity"]), 3)
            self.assertFalse(protocol["claim_boundary"]["formal_selection_evidence"])
            self.assertEqual(protocol["algorithm_evaluation"]["incumbent"], "CAEOS-Pairwise")
            self.assertIn(
                "mal_tls_counterfactual_conflict_gate",
                protocol["algorithm_evaluation"]["challengers"],
            )
            identity = central_directory_identity(Path(archives[0]))
            self.assertEqual(identity["member_count"], 1)
            self.assertEqual(len(identity["central_directory_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
