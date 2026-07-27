from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from caeos.data import TabularViewPreprocessor


UNKNOWN_CLASS_NAME = "__unknown__"


def feature_schema_hash(
    modality_names: Sequence[str],
    modalities: Mapping[str, Sequence[str]],
) -> str:
    payload = {
        "modality_names": [str(name) for name in modality_names],
        "modalities": {
            str(name): [str(column) for column in modalities[name]]
            for name in modality_names
        },
    }
    return hashlib.sha256(
        json.dumps(
            payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")
        ).encode("ascii")
    ).hexdigest()


def _processor_from_state(
    state: Mapping[str, Sequence[float]], expected_width: int
) -> TabularViewPreprocessor:
    processor = TabularViewPreprocessor()
    arrays = {}
    for name in ("median", "mean", "std"):
        values = np.asarray(state[name], dtype=np.float32)
        if values.shape != (expected_width,):
            raise ValueError(
                f"processor {name} has shape {values.shape}, expected "
                f"({expected_width},)"
            )
        if not np.isfinite(values).all():
            raise ValueError(f"processor {name} contains non-finite values")
        arrays[name] = values
    if np.any(arrays["std"] <= 0.0):
        raise ValueError("processor std must be positive")
    processor.median = arrays["median"]
    processor.mean = arrays["mean"]
    processor.std = arrays["std"]
    return processor


@dataclass
class PairwiseDeploymentBundle:
    """Raw-feature deployment state for one frozen pairwise scenario."""

    runtime: Any
    modality_names: tuple[str, ...]
    modalities: dict[str, tuple[str, ...]]
    processor_states: dict[str, dict[str, list[float]]]
    class_names: tuple[str, ...]
    benign_index: int
    selected_threshold: float
    risk_policy_name: str
    source_config_sha256: str

    def __post_init__(self) -> None:
        self.modality_names = tuple(str(name) for name in self.modality_names)
        self.modalities = {
            str(name): tuple(str(column) for column in columns)
            for name, columns in self.modalities.items()
        }
        self.class_names = tuple(str(name) for name in self.class_names)
        if not self.modality_names:
            raise ValueError("deployment bundle requires at least one modality")
        if set(self.modality_names) != set(self.modalities):
            raise ValueError("modality names and modality definitions differ")
        if set(self.modality_names) != set(self.processor_states):
            raise ValueError("modality names and processor states differ")
        feature_columns = self.feature_columns
        if len(feature_columns) != len(set(feature_columns)):
            raise ValueError("feature columns must be unique across modalities")
        if not self.class_names or len(self.class_names) != len(set(self.class_names)):
            raise ValueError("class names must be non-empty and unique")
        if not 0 <= int(self.benign_index) < len(self.class_names):
            raise ValueError("benign index is outside class names")
        self.benign_index = int(self.benign_index)
        self.selected_threshold = float(self.selected_threshold)
        if not np.isfinite(self.selected_threshold):
            raise ValueError("selected threshold must be finite")
        if not self.risk_policy_name:
            raise ValueError("risk policy name is required")
        if len(self.source_config_sha256) != 64:
            raise ValueError("source config SHA-256 is invalid")
        self._processors = {
            name: _processor_from_state(
                self.processor_states[name], len(self.modalities[name])
            )
            for name in self.modality_names
        }
        self.feature_schema_sha256 = feature_schema_hash(
            self.modality_names, self.modalities
        )

    @property
    def feature_columns(self) -> tuple[str, ...]:
        return tuple(
            column
            for name in self.modality_names
            for column in self.modalities[name]
        )

    def transform_frame(
        self, frame: pd.DataFrame
    ) -> tuple[list[np.ndarray], np.ndarray]:
        if not isinstance(frame, pd.DataFrame):
            raise TypeError("deployment input must be a pandas DataFrame")
        missing = [column for column in self.feature_columns if column not in frame]
        if missing:
            raise ValueError(f"deployment input is missing columns: {missing}")
        views = []
        quality_columns = []
        for name in self.modality_names:
            columns = list(self.modalities[name])
            numeric = frame.loc[:, columns].apply(pd.to_numeric, errors="coerce")
            values, quality = self._processors[name].transform(
                numeric.to_numpy(dtype=np.float32)
            )
            views.append(values)
            quality_columns.append(quality)
        quality = np.stack(quality_columns, axis=1)
        return views, quality

    def predict_views(
        self, views: Sequence[np.ndarray], quality: np.ndarray | None = None
    ) -> dict[str, np.ndarray]:
        output = self.runtime.predict(views)
        prediction = np.asarray(output["prediction"], dtype=np.int64)
        probability = np.asarray(output["probability"], dtype=np.float64)
        risk = np.asarray(output["risk"], dtype=np.float64)
        if prediction.ndim != 1 or risk.shape != prediction.shape:
            raise ValueError("runtime prediction and risk shapes are invalid")
        if probability.shape != (len(prediction), len(self.class_names)):
            raise ValueError("runtime probability shape does not match class names")
        if np.any((prediction < 0) | (prediction >= len(self.class_names))):
            raise ValueError("runtime prediction is outside class names")
        if not np.isfinite(probability).all() or not np.isfinite(risk).all():
            raise ValueError("runtime output contains non-finite values")
        rejected = risk > self.selected_threshold
        open_set_index = np.where(rejected, -1, prediction).astype(np.int64)
        open_set_name = np.asarray(
            [
                UNKNOWN_CLASS_NAME if reject else self.class_names[index]
                for index, reject in zip(prediction, rejected)
            ],
            dtype=object,
        )
        result = {
            "closed_set_index": prediction,
            "open_set_index": open_set_index,
            "open_set_name": open_set_name,
            "probability": probability,
            "risk": risk,
            "rejected": rejected,
        }
        if quality is not None:
            quality_array = np.asarray(quality, dtype=np.float32)
            if quality_array.shape != (len(prediction), len(self.modality_names)):
                raise ValueError("quality shape does not match rows and modalities")
            result["modality_quality"] = quality_array
        return result

    def predict_frame(self, frame: pd.DataFrame) -> dict[str, np.ndarray]:
        views, quality = self.transform_frame(frame)
        return self.predict_views(views, quality)

    def evidence(self) -> dict[str, object]:
        runtime_evidence = (
            self.runtime.evidence() if hasattr(self.runtime, "evidence") else None
        )
        return {
            "schema_version": "strict_v4_pairwise_deployment_bundle_v2",
            "feature_schema_sha256": self.feature_schema_sha256,
            "feature_count": len(self.feature_columns),
            "modality_names": list(self.modality_names),
            "class_count": len(self.class_names),
            "benign_class": self.class_names[self.benign_index],
            "selected_threshold": self.selected_threshold,
            "risk_policy_name": self.risk_policy_name,
            "source_config_sha256": self.source_config_sha256,
            "unknown_or_test_labels_used_for_preprocessing_selection_or_threshold": False,
            "contains_raw_input_rows": False,
            "contains_fitted_nonparametric_reference_vectors": True,
            "contains_fitted_class_conditional_state": True,
            "contains_validation_labels": False,
            "contains_test_labels": False,
            "storage_policy": "gpu_private_do_not_publish",
            "runtime_evidence": runtime_evidence,
        }
