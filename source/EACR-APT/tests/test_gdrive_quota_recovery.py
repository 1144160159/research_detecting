import tempfile
import unittest
from pathlib import Path

from scripts.recover_gdrive_quota_hourly import (
    missing_ranges,
    response_is_valid,
    response_reason,
)


class GDriveQuotaRecoveryTests(unittest.TestCase):
    def test_missing_ranges_reuses_exact_existing_chunks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "000000000000-000000000031.chunk").write_bytes(b"x" * 32)
            self.assertEqual(missing_ranges(root, 100, 32), [(32, 63), (64, 95), (96, 99)])

    def test_range_gate_requires_exact_content_range_and_length(self):
        headers = "HTTP/1.1 206 Partial Content\r\nContent-Range: bytes 32-63/100\r\n"
        self.assertTrue(response_is_valid(0, 32, headers, 32, 63, 100))
        self.assertFalse(response_is_valid(0, 31, headers, 32, 63, 100))

    def test_quota_html_is_classified_without_becoming_a_chunk(self):
        reason = response_reason(
            0,
            2009,
            "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n",
            b"<title>Google Drive - Quota exceeded</title> Too many users",
            0,
            1048575,
            10000000,
            "",
        )
        self.assertEqual(reason, "google_drive_quota_exceeded")


if __name__ == "__main__":
    unittest.main()
