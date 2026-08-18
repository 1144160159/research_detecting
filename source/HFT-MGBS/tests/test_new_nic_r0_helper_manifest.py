import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


BUILDER = load(
    ROOT / "scripts" / "build_new_nic_r0_helper_manifest.py", "r0_helper_manifest_builder"
)
FINALIZER = load(
    ROOT / "scripts" / "finalize_new_nic_r0_trust_profile.py", "r0_trust_finalizer"
)


class NewNicR0HelperManifestTests(unittest.TestCase):
    def test_builder_emits_exact_manifest_consumed_by_external_approval_finalizer(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "helpers.txt"
            digest = BUILDER.build_manifest(ROOT, output)
            self.assertEqual(digest, hashlib.sha256(output.read_bytes()).hexdigest())
            parsed = FINALIZER._parse_helper_manifest(output.read_bytes())
            self.assertEqual(set(parsed), FINALIZER.APPROVED_HASH_ROLES)
            self.assertEqual(len(parsed), 12)

    def test_execution_plan_schema_freezes_exact_operations_and_safe_topology(self):
        schema = json.loads(
            (ROOT / "configs" / "schemas" / "new_nic_r0_execution_plan_v1.schema.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(
            schema["properties"]["operations"]["required"],
            ["snapshot", "restore", "xdp_run", "dpdk_run", "fallback"],
        )
        topology = schema["properties"]["topology"]["properties"]
        self.assertIs(topology["same_pf_runtime_driver_rebind"]["const"], False)
        self.assertIs(topology["independent_generator"]["const"], True)
        self.assertIs(topology["same_adapter_loopback"]["const"], False)


if __name__ == "__main__":
    unittest.main()
