from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np
import pandas as pd

from caeos.pairwise_deployment import (
    _processor_from_state,
    feature_schema_hash,
)


@dataclass
class MDRDeploymentBundle:
    """Raw-feature deployment state for one frozen MDR scenario."""

    runtime: Any
    modality_names: tuple[str, ...]
    modalities: dict[str, tuple[str, ...]]
    processor_states: dict[str, dict[str, list[float]]]
    class_names: tuple[str, ...]
    benign_index: int
    source_config_sha256: str
    source_split_fingerprint: str

    def __post_init__(self) -> None:
        self.modality_names = tuple(str(name) for name in self.modality_names)
        self.modalities = {
            str(name): tuple(str(column) for column in columns)
            for name, columns in self.modalities.items()
        }
        self.class_names = tuple(str(name) for name in self.class_names)
        if not self.modality_names:
            raise ValueError("MDR deployment requires at least one modality")
        if set(self.modality_names) != set(self.modalities):
            raise ValueError("MDR modality names and definitions differ")
        if set(self.modality_names) != set(self.processor_states):
            raise ValueError("MDR modality names and processors differ")
        if len(self.feature_columns) != len(set(self.feature_columns)):
            raise ValueError("MDR deployment feature columns are not unique")
        if not self.class_names or len(self.class_names) != len(
            set(self.class_names)
        ):
            raise ValueError("MDR deployment class names are invalid")
        self.benign_index = int(self.benign_index)
        if not 0 <= self.benign_index < len(self.class_names):
            raise ValueError("MDR deployment benign index is invalid")
        for value in (
            self.source_config_sha256,
            self.source_split_fingerprint,
        ):
            if len(value) != 64:
                raise ValueError("MDR deployment source SHA-256 is invalid")
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

    @property
    def selected_threshold(self) -> float:
        return float(self.runtime.clean_threshold)

    def transform_frame(
        self, frame: pd.DataFrame
    ) -> tuple[list[np.ndarray], np.ndarray]:
        if not isinstance(frame, pd.DataFrame):
            raise TypeError("MDR deployment input must be a pandas DataFrame")
        missing = [
            column for column in self.feature_columns if column not in frame
        ]
        if missing:
            raise ValueError(f"MDR deployment input missing columns: {missing}")
        views = []
        quality_columns = []
        for name in self.modality_names:
            columns = list(self.modalities[name])
            numeric = frame.loc[:, columns].apply(
                pd.to_numeric, errors="coerce"
            )
            values, quality = self._processors[name].transform(
                numeric.to_numpy(dtype=np.float32)
            )
            views.append(values)
            quality_columns.append(quality)
        return views, np.stack(quality_columns, axis=1)

    def predict_views(
        self, views: Sequence[np.ndarray]
    ) -> dict[str, np.ndarray]:
        output = self.runtime.predict(views)
        prediction = np.asarray(output["prediction"], dtype=np.int64)
        probability = np.asarray(output["probability"], dtype=np.float64)
        risk = np.asarray(output["risk"], dtype=np.float64)
        if prediction.ndim != 1 or risk.shape != prediction.shape:
            raise ValueError("MDR deployment prediction shapes are invalid")
        if probability.shape != (len(prediction), len(self.class_names)):
            raise ValueError("MDR probability shape differs from class names")
        if (
            not np.isfinite(probability).all()
            or not np.isfinite(risk).all()
            or np.any((prediction < 0) | (prediction >= len(self.class_names)))
        ):
            raise ValueError("MDR deployment output is invalid")
        return {
            **output,
            "prediction": prediction,
            "probability": probability,
            "risk": risk,
            "rejected": risk > self.selected_threshold,
        }

    def predict_frame(self, frame: pd.DataFrame) -> dict[str, np.ndarray]:
        views, quality = self.transform_frame(frame)
        return {**self.predict_views(views), "input_quality": quality}

    def evidence(self) -> dict[str, Any]:
        runtime = self.runtime.evidence()
        return {
            "schema_version": "strict_v4_mdr_deployment_bundle_v1",
            "algorithm": "mdr_caeos_v1",
            "modality_names": list(self.modality_names),
            "modalities": {
                name: list(self.modalities[name])
                for name in self.modality_names
            },
            "feature_columns": list(self.feature_columns),
            "feature_count": len(self.feature_columns),
            "feature_schema_sha256": self.feature_schema_sha256,
            "class_names": list(self.class_names),
            "benign_index": self.benign_index,
            "selected_threshold": self.selected_threshold,
            "augmentation_weight": float(runtime["augmentation_weight"]),
            "source_config_sha256": self.source_config_sha256,
            "source_split_fingerprint": self.source_split_fingerprint,
            "runtime_schema_version": runtime["schema_version"],
            "input_contract": "raw_ordered_tabular_features_without_payload_decryption",
            "unknown_or_test_labels_used_for_fit_selection_or_threshold": False,
            "contains_test_ground_truth": False,
            "storage_policy": "gpu_private_do_not_publish",
        }
