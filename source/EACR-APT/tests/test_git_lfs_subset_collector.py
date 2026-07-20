import tempfile
import unittest
from pathlib import Path

from scripts.collect_git_lfs_subset import (
    parse_lfs_pointer,
    select_inventory,
    write_sha256,
)


class GitLfsSubsetCollectorTests(unittest.TestCase):
    def test_parses_strict_lfs_pointer(self):
        oid = "a" * 64
        pointer = (
            "version https://git-lfs.github.com/spec/v1\n"
            f"oid sha256:{oid}\n"
            "size 12345\n"
        ).encode("ascii")
        self.assertEqual(
            parse_lfs_pointer(pointer), {"oid_sha256": oid, "size": 12345}
        )
        self.assertIsNone(parse_lfs_pointer(b"ordinary repository metadata\n"))

    def test_selects_only_explicit_apt_scopes(self):
        rows = [
            {"path": "datasets/apt_simulations/a/sysmon.log", "size": 10},
            {"path": "datasets/malware/fin7/b/security.log", "size": 20},
            {"path": "datasets/malware/unrelated/c.log", "size": 30},
        ]
        selected = select_inventory(
            rows,
            ["datasets/apt_simulations/**", "datasets/malware/fin7/**"],
        )
        self.assertEqual([row["size"] for row in selected], [10, 20])

    def test_rejects_traversal_in_selection_glob(self):
        with self.assertRaisesRegex(ValueError, "Unsafe repository path"):
            select_inventory([], ["../payload/**"])

    def test_writes_sidecar_sha256(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.jsonl"
            path.write_bytes(b"one\n")
            write_sha256(path)
            sidecar = path.with_name(path.name + ".sha256").read_text(encoding="utf-8")
            self.assertRegex(sidecar, r"^[0-9a-f]{64}  manifest\.jsonl\n$")


if __name__ == "__main__":
    unittest.main()
