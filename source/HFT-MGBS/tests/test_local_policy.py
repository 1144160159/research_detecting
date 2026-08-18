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

    def test_rust_target_build_artifacts_are_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "rust" / "hft-capture" / "target" / "release"
            target.mkdir(parents=True)
            (target / "hft-capture").write_bytes(b"x" * (11 * 1024 * 1024))

            violations = find_violations(root)

        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
