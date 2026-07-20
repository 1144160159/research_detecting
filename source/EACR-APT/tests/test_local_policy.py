import tempfile
import unittest
from pathlib import Path

from scripts.check_local_policy import find_violations


class LocalPolicyTests(unittest.TestCase):
    def test_code_only_tree_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "module.py").write_text("x = 1\n", encoding="utf-8")
            self.assertEqual(find_violations(root), [])

    def test_weight_file_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "weights").mkdir()
            (root / "weights" / "model.pt").write_bytes(b"not-a-real-model")
            violations = find_violations(root)
            self.assertEqual(len(violations), 1)


if __name__ == "__main__":
    unittest.main()
