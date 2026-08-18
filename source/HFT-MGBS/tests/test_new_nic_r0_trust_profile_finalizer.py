import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from hft_mgbs.new_nic_r0_unified import _validate_profile
from scripts.finalize_new_nic_r0_trust_profile import (
    CORE_PATHS,
    HELPER_ROLES,
    finalize_trust_profile,
)


ROOT = Path(__file__).resolve().parents[1]
PENDING = ROOT / "configs" / "new_nic_r0_unified_trust_profile_v1.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


class NewNicR0TrustProfileFinalizerTests(unittest.TestCase):
    def build_fixture(self, base: Path):
        helper_root = base / "helpers"
        approval_root = base / "external-approval"
        output_root = base / "output"
        helper_root.mkdir()
        approval_root.mkdir()
        output_root.mkdir()

        role_paths = {
            role: (ROOT / relative).resolve()
            for role, relative in CORE_PATHS.items()
        }
        for role in HELPER_ROLES:
            path = helper_root / role
            path.write_text("#!/bin/sh\n# {}\nexit 0\n".format(role), encoding="utf-8")
            if os.name != "nt":
                path.chmod(0o500)
            role_paths[role] = path.resolve()
        approved_hashes = {
            role: digest(path) for role, path in sorted(role_paths.items())
        }

        manifest = approval_root / "helper-manifest.txt"
        manifest.write_text(
            "".join(
                "{} {} {}\n".format(role, role_paths[role], approved_hashes[role])
                for role in sorted(role_paths)
            ),
            encoding="utf-8",
        )
        manifest_sha = digest(manifest)
        receipt = approval_root / "helper-manifest.sha256"
        receipt.write_text(manifest_sha + "\n", encoding="utf-8")
        approval = approval_root / "change-record.json"
        write_json(
            approval,
            {
                "schema_version": 1,
                "scope": "new_nic_r0_trust_profile_external_approval",
                "change_id": "CHG-20260814-001",
                "approver": "independent-release-operator",
                "approved": True,
                "contract_id": "hft-new-nic-r0-xdp-primary-dpdk-fallback-v1",
                "pending_profile_sha256": digest(PENDING),
                "helper_manifest_sha256": manifest_sha,
                "approved_role_sha256": approved_hashes,
            },
        )
        output = output_root / "approved-profile.json"
        arguments = {
            "repo_root": ROOT,
            "pending_profile_path": PENDING,
            "helper_root": helper_root,
            "helper_manifest_path": manifest,
            "trusted_helper_manifest_sha256": manifest_sha,
            "approval_record_path": approval,
            "trusted_approval_record_sha256": digest(approval),
            "trust_receipt_path": receipt,
            "output_path": output,
        }
        return arguments, role_paths, output

    def test_pending_instance_cannot_be_used_as_approved_profile(self):
        pending = json.loads(PENDING.read_text(encoding="utf-8"))

        self.assertEqual(pending["status"], "hardware_helpers_pending")
        self.assertEqual(pending["pending_roles"], list(HELPER_ROLES))
        self.assertTrue(
            all(
                pending["approved_role_sha256"][role] is None
                for role in HELPER_ROLES
            )
        )
        with self.assertRaises(ValueError):
            _validate_profile(pending)

    def test_independently_pinned_artifacts_finalize_exact_approved_instance(self):
        with tempfile.TemporaryDirectory() as temporary:
            arguments, _, output = self.build_fixture(Path(temporary))

            result = finalize_trust_profile(**arguments)

            self.assertTrue(output.is_file())
            self.assertEqual(
                result["status"],
                "approved_for_new_nic_r0_unified_recompute",
            )
            self.assertNotIn("pending_roles", result)
            self.assertFalse(result["production_qualified"])
            self.assertFalse(result["final_pareto_ingestion_allowed"])
            _validate_profile(result)
            self.assertEqual(result, json.loads(output.read_text(encoding="utf-8")))

    def test_helper_drift_after_approval_is_rejected_without_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            arguments, role_paths, output = self.build_fixture(Path(temporary))
            role_paths["xdp_runner"].write_text("#!/bin/sh\nexit 9\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                finalize_trust_profile(**arguments)

            self.assertFalse(output.exists())

    def test_unpinned_approval_record_is_rejected_without_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            arguments, _, output = self.build_fixture(Path(temporary))
            arguments["trusted_approval_record_sha256"] = "0" * 64

            with self.assertRaises(ValueError):
                finalize_trust_profile(**arguments)

            self.assertFalse(output.exists())

    def test_symlinked_helper_is_rejected_without_output(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlink is unavailable")
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            arguments, role_paths, output = self.build_fixture(base)
            helper = role_paths["xdp_runner"]
            real_helper = base / "real-xdp-runner"
            helper.replace(real_helper)
            try:
                os.symlink(real_helper, helper)
            except OSError as exc:
                self.skipTest("symlink creation is unavailable: {}".format(exc))

            with self.assertRaises(ValueError):
                finalize_trust_profile(**arguments)

            self.assertFalse(output.exists())

    def test_existing_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            arguments, _, output = self.build_fixture(Path(temporary))
            output.write_text("keep\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                finalize_trust_profile(**arguments)

            self.assertEqual(output.read_text(encoding="utf-8"), "keep\n")


if __name__ == "__main__":
    unittest.main()
