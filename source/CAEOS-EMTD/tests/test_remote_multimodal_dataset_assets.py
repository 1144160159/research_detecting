from __future__ import annotations

import gzip
import tempfile
import unittest
import zipfile
from pathlib import Path

from audit_remote_multimodal_dataset_assets import audit_dataset, matching_columns


class RemoteMultimodalAssetAuditTest(unittest.TestCase):
    def test_byte_sequence_and_endpoint_columns_are_separated(self) -> None:
        columns = [
            "Label",
            "Payload Bytes",
            "Packet Length Sequence",
            "Src IP",
            "Dst IP",
        ]
        self.assertEqual(
            matching_columns(columns, ("payload", "byte")),
            ["Payload Bytes"],
        )
        self.assertEqual(
            matching_columns(columns, ("packet_length", "iat")),
            ["Packet Length Sequence"],
        )
        self.assertEqual(
            matching_columns(columns, ("src_ip", "dst_ip")),
            ["Dst IP", "Src IP"],
        )

    def test_byte_count_statistics_are_not_raw_payload(self) -> None:
        columns = [
            "IN_BYTES",
            "Flow Bytes/s",
            "Bwd Bytes/Bulk Avg",
            "tcp.payload",
        ]
        self.assertEqual(
            matching_columns(
                columns,
                (
                    "payload",
                    "raw_data",
                    "packet_bytes",
                    "byte_sequence",
                ),
            ),
            ["tcp.payload"],
        )

    def test_detects_pcap_inside_zip(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            dataset = Path(temporary_directory)
            (dataset / "flows.csv").write_text(
                "src_ip,dst_ip\n1,2\n",
                encoding="utf-8",
            )
            with zipfile.ZipFile(dataset / "PCAPs.zip", "w") as archive:
                archive.writestr(
                    "capture/day1.pcap",
                    b"\xd4\xc3\xb2\xa1payload",
                )

            result = audit_dataset(dataset, 5, 1)

        self.assertTrue(result["capability"]["raw_capture_present"])
        self.assertFalse(result["capability"]["raw_capture_direct_present"])
        self.assertTrue(result["capability"]["raw_capture_archive_present"])
        self.assertFalse(result["capability"]["only_csv_without_raw_capture"])

    def test_rejects_csv_only_zip(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            dataset = Path(temporary_directory)
            (dataset / "flows.csv").write_text(
                "src_ip,dst_ip\n1,2\n",
                encoding="utf-8",
            )
            with zipfile.ZipFile(dataset / "CSVs.zip", "w") as archive:
                archive.writestr("flows.csv", "src_ip,dst_ip\n1,2\n")

            result = audit_dataset(dataset, 5, 1)

        self.assertFalse(result["capability"]["raw_capture_present"])
        self.assertTrue(result["capability"]["only_csv_without_raw_capture"])

    def test_detects_single_gzipped_pcap(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            dataset = Path(temporary_directory)
            with gzip.open(dataset / "capture.pcap.gz", "wb") as handle:
                handle.write(b"\x0a\x0d\x0d\x0arest")

            result = audit_dataset(dataset, 5, 1)

        self.assertTrue(result["capability"]["raw_capture_archive_present"])


if __name__ == "__main__":
    unittest.main()
