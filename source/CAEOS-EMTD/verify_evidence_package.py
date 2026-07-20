from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


REQUIRED_KEYS = {
    "schema_version",
    "modality_names",
    "known_class_names",
    "selected_risk_name",
    "selected_threshold",
    "test_sample_index",
    "test_known_prediction",
    "test_open_set_prediction",
    "test_rejected",
    "test_selected_risk",
    "test_view_evidence",
    "test_view_probability",
    "test_view_uncertainty",
    "test_view_reliability",
    "test_local_conflict",
    "test_pairwise_conflict",
    "test_global_conflict",
    "test_final_probability",
}

FORBIDDEN_TEST_TRUTH = {"test_labels", "test_unknown", "test_is_unknown"}


def verify(path: Path) -> dict[str, object]:
    with np.load(path, allow_pickle=False) as package:
        keys = set(package.files)
        missing = sorted(REQUIRED_KEYS - keys)
        forbidden = sorted(FORBIDDEN_TEST_TRUTH & keys)
        if missing:
            raise ValueError(f"missing evidence-package keys: {missing}")
        if forbidden:
            raise ValueError(f"test ground truth leaked into evidence package: {forbidden}")

        samples = len(package["test_sample_index"])
        modalities = len(package["modality_names"])
        classes = len(package["known_class_names"])
        expected = {
            "test_view_evidence": (samples, modalities, classes),
            "test_view_probability": (samples, modalities, classes),
            "test_view_uncertainty": (samples, modalities),
            "test_view_reliability": (samples, modalities),
            "test_local_conflict": (samples, modalities),
            "test_pairwise_conflict": (samples, modalities, modalities),
            "test_global_conflict": (samples,),
            "test_final_probability": (samples, classes),
            "test_selected_risk": (samples,),
            "test_rejected": (samples,),
        }
        for name, shape in expected.items():
            if package[name].shape != shape:
                raise ValueError(
                    f"{name} shape {package[name].shape} does not match {shape}"
                )
            if not np.isfinite(package[name]).all():
                raise ValueError(f"{name} contains non-finite values")
        if not np.allclose(package["test_view_probability"].sum(axis=2), 1.0):
            raise ValueError("per-modality probabilities are not normalized")
        if not np.allclose(package["test_final_probability"].sum(axis=1), 1.0):
            raise ValueError("fused probabilities are not normalized")
        rejected = package["test_rejected"].astype(bool)
        open_prediction = package["test_open_set_prediction"]
        if not np.all(open_prediction[rejected] == -1):
            raise ValueError("rejected samples do not use the -1 open-set label")
        threshold = float(package["selected_threshold"])
        if not np.isfinite(threshold):
            raise ValueError("selected threshold is not finite")
        if not np.array_equal(
            rejected, package["test_selected_risk"] > threshold
        ):
            raise ValueError("rejection decisions do not match risk and threshold")
        return {
            "file": str(path),
            "schema_version": str(package["schema_version"]),
            "samples": samples,
            "modalities": modalities,
            "known_classes": classes,
            "keys": len(keys),
            "contains_test_ground_truth": False,
            "selected_risk": str(package["selected_risk_name"]),
            "selected_threshold": threshold,
            "rejected_samples": int(rejected.sum()),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify a CAEOS evidence package")
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    print(json.dumps(verify(Path(args.input)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
