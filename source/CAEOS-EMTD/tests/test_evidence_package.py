import tempfile
import unittest
from pathlib import Path

import numpy as np

from verify_evidence_package import verify


class EvidencePackageTest(unittest.TestCase):
    def test_verifier_accepts_consistent_deployment_package(self):
        samples, modalities, classes = 4, 2, 3
        probability = np.full((samples, modalities, classes), 1.0 / classes)
        fused = np.full((samples, classes), 1.0 / classes)
        risk = np.asarray([0.1, 0.8, 0.2, 0.9])
        rejected = risk > 0.5
        prediction = np.asarray([0, 1, 2, 0])
        open_prediction = prediction.copy()
        open_prediction[rejected] = -1
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence_package.npz"
            np.savez_compressed(
                path,
                schema_version=np.asarray("1.0"),
                modality_names=np.asarray(["a", "b"]),
                known_class_names=np.asarray(["x", "y", "z"]),
                selected_risk_name=np.asarray("support_union"),
                selected_threshold=np.asarray(0.5),
                test_sample_index=np.arange(samples),
                test_known_prediction=prediction,
                test_open_set_prediction=open_prediction,
                test_rejected=rejected,
                test_selected_risk=risk,
                test_view_evidence=probability,
                test_view_probability=probability,
                test_view_uncertainty=np.zeros((samples, modalities)),
                test_view_reliability=np.ones((samples, modalities)),
                test_local_conflict=np.zeros((samples, modalities)),
                test_pairwise_conflict=np.zeros((samples, modalities, modalities)),
                test_global_conflict=np.zeros(samples),
                test_final_probability=fused,
            )
            report = verify(path)

        self.assertEqual(report["samples"], samples)
        self.assertFalse(report["contains_test_ground_truth"])
        self.assertEqual(report["rejected_samples"], 2)


if __name__ == "__main__":
    unittest.main()
