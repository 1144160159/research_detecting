import unittest

import torch

from caeos.open_detect_runtime import OpenDetectRuntime


class OpenDetectRuntimeTests(unittest.TestCase):
    def test_rejects_non_opendetect_checkpoint(self) -> None:
        with self.assertRaisesRegex(ValueError, "not an OpenDetect"):
            OpenDetectRuntime.from_checkpoint({"arguments": {"model": "mlp"}})

    def test_synchronize_cpu_is_noop(self) -> None:
        runtime = OpenDetectRuntime(model=torch.nn.Linear(1, 1), device_name="cpu")
        runtime.synchronize()
        self.assertEqual(runtime.device_name, "cpu")


if __name__ == "__main__":
    unittest.main()
