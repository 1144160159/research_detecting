from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SyncContractTest(unittest.TestCase):
    def test_gpu_sync_preserves_split_source_and_shell_execution(self):
        script = (ROOT / "sync_to_gpu.cmd").read_text(encoding="utf-8")

        self.assertIn("--exclude=target", script)
        self.assertIn("configs deploy rust scripts tests", script)
        self.assertIn("chmod 755 scripts/*.sh", script)
        self.assertIn("-o ClearAllForwardings=yes", script)
        self.assertIn('set "REMOTE_PORT=25696"', script)
        self.assertIn("-o ConnectTimeout=120", script)

    def test_split_sync_validates_both_nodes_without_artifact_transfer(self):
        script = (ROOT / "sync_split_deployment.cmd").read_text(
            encoding="utf-8"
        )

        self.assertIn("root@10.0.5.8", script)
        self.assertIn("root@10.0.5.103", script)
        self.assertIn('set "GPU_PORT=25696"', script)
        self.assertEqual(script.count("ConnectTimeout=120"), 6)
        self.assertNotIn("ConnectTimeout=15", script)
        self.assertIn("configs deploy docs hft_mgbs rust scripts tests", script)
        self.assertIn("--exclude=target", script)
        self.assertIn("chmod 755 %PHYSICAL_DIR%/scripts/*.sh", script)
        self.assertIn("chmod 755 %GPU_DIR%/scripts/*.sh", script)
        self.assertIn("cargo test --all-targets", script)
        self.assertIn("python -m pytest -q", script)
        self.assertNotIn("datasets", script)
        self.assertNotIn("models", script)
        self.assertNotIn("results", script)


if __name__ == "__main__":
    unittest.main()
