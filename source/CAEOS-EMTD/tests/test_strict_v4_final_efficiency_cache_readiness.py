from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

from audit_strict_v4_final_efficiency_cache_readiness import build_audit


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


class FinalEfficiencyCacheReadinessTests(unittest.TestCase):
    def test_seed7_ready_seed191_missing_blocks_timing_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = {}
            overrides = {}
            for index in range(7):
                suite = f"suite_{index}"
                path = root / suite / "seed7.csv"
                path.parent.mkdir(parents=True)
                path.write_bytes(f"cache-{index}".encode())
                sidecar = Path(str(path) + ".json")
                sidecar.write_bytes(f"sidecar-{index}".encode())
                artifacts[suite] = {
                    "path": f"/remote/{suite}/seed7.csv",
                    "sha256": sha(path.read_bytes()),
                    "sidecar_sha256": sha(sidecar.read_bytes()),
                }
                overrides[suite] = path
            coverage = {
                "schema_version": "strict_v4_coverage_manifest_v2",
                "manifest_sha256": "a" * 64,
                "cache_artifacts": artifacts,
            }
            audit = build_audit(
                coverage, search_roots=[root], path_overrides=overrides
            )
            self.assertTrue(audit["seed7_frozen_replay"]["all_sha_verified"])
            self.assertEqual(
                audit["seed191_training_sentinels"]["ready_suites"], 0
            )
            self.assertFalse(audit["gates"]["formal_timing_allowed"])
            self.assertFalse(
                audit["gates"]["protocol_freeze_blocked_by_cache_precompute"]
            )

    def test_seed191_is_detected_by_suite_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = {}
            overrides = {}
            for index in range(7):
                suite = f"suite_{index}"
                path = root / suite / "seed7.csv"
                path.parent.mkdir(parents=True)
                path.write_bytes(b"cache")
                sidecar = Path(str(path) + ".json")
                sidecar.write_bytes(b"sidecar")
                fresh = root / suite / "seed191_max1000.csv"
                fresh.write_bytes(b"fresh")
                Path(str(fresh) + ".json").write_bytes(b"fresh-sidecar")
                artifacts[suite] = {
                    "path": str(path),
                    "sha256": sha(path.read_bytes()),
                    "sidecar_sha256": sha(sidecar.read_bytes()),
                }
                overrides[suite] = path
            coverage = {
                "schema_version": "strict_v4_coverage_manifest_v2",
                "manifest_sha256": "b" * 64,
                "cache_artifacts": artifacts,
            }
            audit = build_audit(
                coverage, search_roots=[root], path_overrides=overrides
            )
            self.assertEqual(
                audit["seed191_training_sentinels"]["ready_suites"], 7
            )
            self.assertTrue(audit["gates"]["formal_timing_allowed"])

    def test_seed191_without_sidecar_is_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = {}
            overrides = {}
            for index in range(7):
                suite = f"suite_{index}"
                path = root / suite / "seed7.csv"
                path.parent.mkdir(parents=True)
                path.write_bytes(b"cache")
                sidecar = Path(str(path) + ".json")
                sidecar.write_bytes(b"sidecar")
                (root / suite / "seed191_max1000.csv").write_bytes(b"incomplete")
                artifacts[suite] = {
                    "path": str(path),
                    "sha256": sha(path.read_bytes()),
                    "sidecar_sha256": sha(sidecar.read_bytes()),
                }
                overrides[suite] = path
            coverage = {
                "schema_version": "strict_v4_coverage_manifest_v2",
                "manifest_sha256": "c" * 64,
                "cache_artifacts": artifacts,
            }
            audit = build_audit(
                coverage, search_roots=[root], path_overrides=overrides
            )
            self.assertEqual(
                audit["seed191_training_sentinels"]["ready_suites"], 0
            )
            self.assertFalse(audit["gates"]["formal_timing_allowed"])


if __name__ == "__main__":
    unittest.main()
