import tempfile
import unittest
from pathlib import Path

from scripts.check_local_policy import find_violations


class LocalPolicyTests(unittest.TestCase):
    def test_forbidden_capture_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "datasets").mkdir()
            (root / "datasets" / "sample.pcap").write_bytes(b"pcap")
            violations = find_violations(root)
        self.assertEqual(violations[0]["reason"], "forbidden_directory")


if __name__ == "__main__":
    unittest.main()
