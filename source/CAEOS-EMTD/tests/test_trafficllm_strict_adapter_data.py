from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from audit_trafficllm_strict_adapter_data import (
    EXPECTED_CLASSES,
    FULL_DIRECTORY,
    OFFICIAL_AGGREGATE_FILES,
    SPLIT_DIRECTORY,
    audit,
    file_hash,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash


class TrafficLLMStrictAdapterDataTests(unittest.TestCase):
    def create_inputs(
        self, root: Path
    ) -> tuple[Path, Path, Path]:
        official = root / "official"
        official.mkdir()
        preprocessor = official / "preprocessor.py"
        preprocessor.write_text(
            "\n".join(
                [
                    "def preprocess_string(s):",
                    "    return s.replace(' ', '')",
                    *(f"# {name}" for name in OFFICIAL_AGGREGATE_FILES),
                ]
            ),
            encoding="utf-8",
        )
        prior_path = root / "prior.json"
        prior_path.write_text(
            json.dumps(
                {
                    "source_audit": {
                        "TrafficLLM": {
                            "head": "a" * 40,
                            "source_tree_sha256": "b" * 64,
                            "key_source_sha256": {
                                "preprocessor.py": file_hash(preprocessor)
                            },
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        dataset = root / "dataset"
        full = dataset / FULL_DIRECTORY
        split = dataset / SPLIT_DIRECTORY
        for name in EXPECTED_CLASSES:
            (full / name).mkdir(parents=True)
            (split / "train" / name).mkdir(parents=True)
            (split / "test" / name).mkdir(parents=True)
        np.save(
            split / "train" / sorted(EXPECTED_CLASSES)[0] / "flow.npy",
            np.arange(1600, dtype=np.uint8).reshape(1, 1600),
        )
        return official, prior_path, dataset

    def test_rejects_crossplatform_array_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = audit(*self.create_inputs(Path(temporary)))
        self.assertTrue(
            result["candidate_dataset"]["expected_twelve_classes_exact"]
        )
        self.assertEqual(
            result["candidate_dataset"]["sample_shape"], [1, 1600]
        )
        self.assertEqual(
            result["candidate_dataset"]["sample_dtype"], "uint8"
        )
        self.assertFalse(
            result["strict_adapter_gates"][
                "official_aggregate_layout_present"
            ]
        )
        self.assertFalse(
            result["strict_adapter_gates"][
                "sample_type_matches_official_preprocessor"
            ]
        )
        self.assertFalse(
            result["admission_decision"][
                "strict_v4_protocol_adapter_execution_admitted"
            ]
        )
        self.assertEqual(
            result["manifest_sha256"], canonical_hash(result)
        )

    def test_detects_preprocessor_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            official, prior, dataset = self.create_inputs(root)
            (official / "preprocessor.py").write_text(
                "changed = True\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "differs"):
                audit(official, prior, dataset)


if __name__ == "__main__":
    unittest.main()
