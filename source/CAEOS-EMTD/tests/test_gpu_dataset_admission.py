import tempfile
import unittest
import zipfile
from pathlib import Path

from audit_gpu_dataset_admission import (
    LsnmSessionizer,
    aggregate_dataset,
    normalized_header,
    scan_archive,
)


LSNM_HEADER = [
    "Time",
    "Source",
    "Destination",
    "Protocol",
    "TCP Source Port",
    "TCP Destination Port",
]


class GpuDatasetAdmissionTests(unittest.TestCase):
    def test_normalizes_bom_whitespace(self) -> None:
        self.assertEqual(normalized_header("\ufeff  Source   IP "), "Source IP")

    def test_lsnm_sessionizer_is_bidirectional_and_gap_aware(self) -> None:
        columns = {name: index for index, name in enumerate(LSNM_HEADER)}
        sessionizer = LsnmSessionizer("Malicious/DDoS/a.csv", gap_seconds=10)
        first = sessionizer.group(
            ["1", "10.0.0.1", "10.0.0.2", "6", "123", "443"], columns
        )
        reverse = sessionizer.group(
            ["2", "10.0.0.2", "10.0.0.1", "6", "443", "123"], columns
        )
        later = sessionizer.group(
            ["20", "10.0.0.1", "10.0.0.2", "6", "123", "443"], columns
        )
        self.assertEqual(first, reverse)
        self.assertNotEqual(first, later)

    def test_archive_scan_is_exact_and_resumable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive_path = root / "lsnm.zip"
            header = LSNM_HEADER + ["label"]
            rows = [
                ["1", "a", "b", "6", "1", "2", "normal"],
                ["2", "b", "a", "6", "2", "1", "normal"],
                ["30", "a", "b", "6", "1", "2", "normal"],
            ]
            buffer = []
            buffer.append(",".join(header))
            buffer.extend(",".join(row) for row in rows)
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr(
                    "Dataset-Ready (Use This)/Benign/normal_data.csv",
                    "\n".join(buffer) + "\n",
                )
            work = root / "work"
            first = scan_archive(
                dataset="LSNM2024", archive_path=archive_path, work_dir=work
            )
            second = scan_archive(
                dataset="LSNM2024", archive_path=archive_path, work_dir=work
            )
            self.assertEqual(first, second)
            self.assertEqual(first[0]["rows"], 3)
            self.assertEqual(first[0]["group_summary"]["groups"], 1)
            self.assertEqual(first[0]["group_summary"]["cross_label_groups"], 0)

    def test_aggregate_fails_missing_groups_and_features(self) -> None:
        report = aggregate_dataset(
            "LSNM2024",
            [
                {
                    "member": "Benign/a.csv",
                    "header": ["Length"],
                    "rows": 2,
                    "malformed_rows": 0,
                    "missing_group_rows": 1,
                    "label_counts": {"normal": 2},
                    "group_summary": {
                        "groups_by_first_label": {"normal": 1},
                        "cross_label_groups": 0,
                    },
                }
            ],
            ["attack"],
            ["Length", "IP TTL"],
        )
        self.assertFalse(report["admission_passed"])
        self.assertFalse(report["checks"]["zero_missing_group_rows"])
        self.assertFalse(report["checks"]["required_features_present_in_every_member"])


if __name__ == "__main__":
    unittest.main()
