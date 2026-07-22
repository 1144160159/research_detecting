from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

from caeos.hybrid_open_set import (
    bonferroni_union_risk,
    cauchy_combined_risk,
    hybrid_open_set_components,
    weighted_risk,
)
from train_hybrid_open_set import compose_structural_inputs, foss_representation


SUPPORTED_RISKS = {
    "cauchy_modality_support_union",
    "pseudo_unknown_learned_blend",
}
COMPONENT_TIE_TOLERANCE = 1e-12


def snap_to_reference_ties(
    values: np.ndarray,
    reference: np.ndarray,
    tolerance: float = COMPONENT_TIE_TOLERANCE,
) -> np.ndarray:
    """Stabilize empirical ranks at validation-reference ties."""
    values = np.asarray(values, dtype=np.float64)
    reference = np.asarray(reference, dtype=np.float64)
    if reference.ndim != 1 or not len(reference):
        raise ValueError("empirical-tail reference must be non-empty and one-dimensional")
    if tolerance < 0.0:
        raise ValueError("tie tolerance must be nonnegative")

    insertion = np.searchsorted(reference, values, side="left")
    left_index = np.clip(insertion - 1, 0, len(reference) - 1)
    right_index = np.clip(insertion, 0, len(reference) - 1)
    left = reference[left_index]
    right = reference[right_index]
    use_right = np.abs(right - values) < np.abs(values - left)
    nearest = np.where(use_right, right, left)
    return np.where(np.abs(nearest - values) <= tolerance, nearest, values)


def empirical_tail_cluster_starts(
    reference: np.ndarray, tolerance: float = COMPONENT_TIE_TOLERANCE
) -> np.ndarray:
    """Return the first rank of each machine-precision reference cluster."""
    reference = np.asarray(reference, dtype=np.float64)
    if reference.ndim != 1 or not len(reference):
        raise ValueError("empirical-tail reference must be non-empty and one-dimensional")
    if np.any(reference[1:] < reference[:-1]):
        raise ValueError("empirical-tail reference must be sorted")
    if tolerance < 0.0:
        raise ValueError("tie tolerance must be nonnegative")
    return np.concatenate(
        [np.asarray([0], dtype=np.int64), np.flatnonzero(np.diff(reference) > tolerance) + 1]
    )


def stable_empirical_tail_scores(
    reference: np.ndarray,
    values: np.ndarray,
    cluster_starts: np.ndarray,
    tolerance: float = COMPONENT_TIE_TOLERANCE,
) -> np.ndarray:
    """Evaluate an upper empirical tail with one rank per near-tie cluster."""
    reference = np.asarray(reference, dtype=np.float64)
    values = np.asarray(values, dtype=np.float64)
    cluster_starts = np.asarray(cluster_starts, dtype=np.int64)
    insertion = np.searchsorted(reference, values, side="left")
    left_index = np.clip(insertion - 1, 0, len(reference) - 1)
    right_index = np.clip(insertion, 0, len(reference) - 1)
    left_distance = np.abs(values - reference[left_index])
    right_distance = np.abs(reference[right_index] - values)
    nearest_index = np.where(right_distance < left_distance, right_index, left_index)
    cluster_index = np.searchsorted(cluster_starts, nearest_index, side="right") - 1
    stable_insertion = cluster_starts[cluster_index]
    nearest_distance = np.minimum(left_distance, right_distance)
    insertion = np.where(nearest_distance <= tolerance, stable_insertion, insertion)
    upper_count = len(reference) - insertion
    p_value = (upper_count + 1.0) / (len(reference) + 1.0)
    return 1.0 - p_value


@dataclass
class PairwiseRuntime:
    """Serializable inference state for the frozen pairwise CAEOS branch."""

    model: Any
    foss_model: Any
    distance_model: Any
    knn_model: Any
    view_knn_models: list[Any]
    class_knn_model: Any
    lof_model: Any
    normalizer: Any
    tail_calibrator: Any
    selected_risk: str
    learned_weights: dict[str, float]
    validation_raw_learned: np.ndarray
    selected_alpha: float
    foss_structural_view: bool
    foss_structural_view_mode: str
    foss_structural_view_scope: str

    def __post_init__(self) -> None:
        if self.selected_risk not in SUPPORTED_RISKS:
            raise ValueError(f"unsupported frozen pairwise risk: {self.selected_risk}")
        if not 0.0 <= float(self.selected_alpha) <= 1.0:
            raise ValueError("selected_alpha must be in [0, 1]")
        self.validation_raw_learned = np.asarray(
            self.validation_raw_learned, dtype=np.float64
        )
        if self.validation_raw_learned.ndim != 1:
            raise ValueError("validation_raw_learned must be one-dimensional")
        if self.selected_risk == "pseudo_unknown_learned_blend":
            if not self.validation_raw_learned.size:
                raise ValueError("learned blend requires validation calibration scores")
            if not np.isfinite(self.validation_raw_learned).all():
                raise ValueError("validation calibration scores must be finite")
            self._validation_raw_learned_sorted = np.sort(
                self.validation_raw_learned
            )
            self._learned_tail_cluster_starts = empirical_tail_cluster_starts(
                self._validation_raw_learned_sorted
            )
        if self.tail_calibrator is not None:
            self._tail_cluster_starts = {
                name: empirical_tail_cluster_starts(reference)
                for name, reference in self.tail_calibrator.reference.items()
            }

    def _model_inputs(
        self, raw_views: Sequence[np.ndarray]
    ) -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
        views = [np.asarray(view) for view in raw_views]
        if not views or len({len(view) for view in views}) != 1:
            raise ValueError("pairwise runtime requires aligned modality views")
        raw_values = np.concatenate(views, axis=1)
        structural = None
        if self.foss_structural_view:
            structural = foss_representation(
                self.foss_model, raw_values, self.foss_structural_view_mode
            )
        model_views, values, _ = compose_structural_inputs(
            views, structural, self.foss_structural_view_scope
        )
        return model_views, values, raw_values

    def component_values(
        self, raw_views: Sequence[np.ndarray]
    ) -> tuple[dict[str, np.ndarray], np.ndarray]:
        model_views, values, _ = self._model_inputs(raw_views)
        components, probability = hybrid_open_set_components(
            self.model, model_views, self.distance_model, values
        )
        components["knn_distance"] = self.knn_model.score(values)
        view_names = []
        for index, (view_model, view) in enumerate(
            zip(self.view_knn_models, model_views)
        ):
            name = f"knn_view_{index}"
            view_names.append(name)
            components[name] = view_model.score(view)
        prediction = probability.argmax(axis=1)
        components["class_knn_distance"] = self.class_knn_model.score(
            values, prediction
        )
        components["lof_density"] = self.lof_model.score(values)
        return components, probability

    def predict(self, raw_views: Sequence[np.ndarray]) -> dict[str, np.ndarray]:
        components, probability = self.component_values(raw_views)
        prediction = probability.argmax(axis=1)
        view_names = sorted(
            (name for name in components if name.startswith("knn_view_")),
            key=lambda name: int(name.rsplit("_", 1)[1]),
        )

        tail = {
            name: stable_empirical_tail_scores(
                self.tail_calibrator.reference[name],
                values,
                self._tail_cluster_starts[name],
            )
            for name, values in components.items()
        }
        normalized = self.normalizer.transform(components)
        cauchy_evidence = cauchy_combined_risk(
            tail, ("conflict", "tree_disagreement")
        )
        modality_support = bonferroni_union_risk(
            tail, ("distance", *view_names)
        )
        reference_risk = bonferroni_union_risk(
            {
                "cauchy_evidence": cauchy_evidence,
                "modality_support": modality_support,
            },
            ("cauchy_evidence", "modality_support"),
        )
        if self.selected_risk == "cauchy_modality_support_union":
            risk = reference_risk
        else:
            raw_learned = weighted_risk(normalized, self.learned_weights)
            learned_tail = stable_empirical_tail_scores(
                self._validation_raw_learned_sorted,
                raw_learned,
                self._learned_tail_cluster_starts,
            )
            risk = (
                (1.0 - self.selected_alpha) * reference_risk
                + self.selected_alpha * learned_tail
            )
        return {
            "prediction": np.asarray(prediction, dtype=np.int64),
            "probability": np.asarray(probability, dtype=np.float64),
            "risk": np.asarray(risk, dtype=np.float64),
        }

    def evidence(self) -> dict[str, object]:
        return {
            "schema_version": "strict_v4_pairwise_runtime_v2",
            "selected_risk": self.selected_risk,
            "selected_alpha": float(self.selected_alpha),
            "learned_feature_names": sorted(self.learned_weights),
            "validation_calibration_count": int(self.validation_raw_learned.size),
            "empirical_tail_tie_tolerance": COMPONENT_TIE_TOLERANCE,
            "empirical_tail_tie_policy": "adjacent_reference_cluster_first_rank",
            "learned_tail_tie_policy": "adjacent_reference_cluster_first_rank",
            "contains_training_or_test_labels": False,
            "contains_test_ground_truth": False,
        }
