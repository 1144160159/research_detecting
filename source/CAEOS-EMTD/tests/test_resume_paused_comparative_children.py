from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from resume_paused_comparative_children import (
    direct_children,
    process_status,
    validate_run_manifest,
)


def write_status(root: Path, pid: int, ppid: int, state: str = "T") -> None:
    path = root / str(pid)
    path.mkdir(parents=True)
    (path / "status").write_text(
        f"Name:\tpython\nState:\t{state} (state)\nPPid:\t{ppid}\n",
        encoding="utf-8",
    )


class ResumePausedComparativeChildrenTests(unittest.TestCase):
    def test_process_status_and_direct_children(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_status(root, 10, 1)
            write_status(root, 11, 10, "R")
            write_status(root, 12, 10, "T")
            self.assertEqual(process_status(12, root)["state"], "T")
            self.assertEqual(direct_children(10, root), [11, 12])

    def test_missing_process_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertIsNone(process_status(99, Path(directory)))

    def test_parallel_manifest_is_canonical(self) -> None:
        value = {
            "schema_version": "strict_v4_comparative_parallel_run_v1",
            "run_id": "run",
        }
        value["manifest_sha256"] = canonical_hash(value)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            self.assertEqual(validate_run_manifest(path), value)
            value["run_id"] = "tampered"
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "validation failed"):
                validate_run_manifest(path)


if __name__ == "__main__":
    unittest.main()
