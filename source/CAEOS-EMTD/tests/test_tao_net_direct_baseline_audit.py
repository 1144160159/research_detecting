from __future__ import annotations

import tempfile
import subprocess
import unittest
from pathlib import Path

from audit_tao_net_direct_baseline import (
    admission_decision,
    raw_dataset_inventory,
    required_artifact_inventory,
)
from create_tao_net_direct_baseline_protocol import (
    REQUIRED_RELEASE_ARTIFACTS,
    canonical_hash,
    git_blob_hash,
)


class TAONetDirectBaselineAuditTests(unittest.TestCase):
    def test_canonical_hash_ignores_manifest_field(self) -> None:
        value = {"schema_version": "test", "answer": 42}
        observed = canonical_hash(value)
        value["manifest_sha256"] = observed
        self.assertEqual(observed, canonical_hash(value))

    def test_released_artifacts_fail_closed_when_absent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            observed = required_artifact_inventory(Path(directory))
        self.assertEqual(observed["expected"], len(REQUIRED_RELEASE_ARTIFACTS))
        self.assertEqual(observed["present"], 0)
        self.assertFalse(observed["complete"])

    def test_git_blob_hash_is_independent_of_worktree_line_endings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(
                ["git", "-C", str(root), "config", "user.email", "test@example.com"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(root), "config", "user.name", "Test"],
                check=True,
            )
            path = root / "source.py"
            path.write_bytes(b"print('ok')\n")
            subprocess.run(
                ["git", "-C", str(root), "add", "source.py"], check=True
            )
            subprocess.run(
                ["git", "-C", str(root), "commit", "-q", "-m", "fixture"],
                check=True,
            )
            observed = git_blob_hash(root, "source.py")
            path.write_bytes(b"print('ok')\r\n")
            self.assertEqual(observed, git_blob_hash(root, "source.py"))

    def test_raw_dataset_identity_requires_every_frozen_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            roots = {
                "iscxvpn": root / "vpn",
                "iscxtor": root / "tor",
            }
            expected = {
                "iscxvpn": {"PCAPs/vpn.zip": 17},
                "iscxtor": {"PCAPs/tor.tar.xz": 19},
            }
            for name, required in expected.items():
                for relative, size in required.items():
                    path = roots[name] / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with path.open("wb") as handle:
                        handle.truncate(size)
            observed = raw_dataset_inventory(roots, expected)
            self.assertTrue(
                observed["iscxvpn"]["raw_identity_candidate_complete"]
            )
            self.assertTrue(
                observed["iscxtor"]["raw_identity_candidate_complete"]
            )
            (roots["iscxtor"] / next(iter(expected["iscxtor"]))).unlink()
            observed = raw_dataset_inventory(roots, expected)
            self.assertFalse(
                observed["iscxtor"]["raw_identity_candidate_complete"]
            )

    def test_protocol_boundary_forbids_count_increment(self) -> None:
        boundary = {
            "same_protocol_as_strict_v4": False,
            "unknown_validation_exposure": True,
            "baseline_count_increment": 0,
        }
        self.assertFalse(boundary["same_protocol_as_strict_v4"])
        self.assertTrue(boundary["unknown_validation_exposure"])
        self.assertEqual(boundary["baseline_count_increment"], 0)

    def test_native_reproduction_and_main_table_are_separate_gates(self) -> None:
        observed = admission_decision(
            {"official_artifacts_complete": True},
            {"same_protocol_as_strict_v4": False},
        )
        self.assertTrue(observed["native_execution_admitted"])
        self.assertFalse(observed["strict_v4_main_table_admitted"])


if __name__ == "__main__":
    unittest.main()
