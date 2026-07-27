from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

from caeos.hybrid import (
    ConflictAwareHybridClassifier,
    _normalize_probability,
    temperature_scale,
)


DEFAULT_FAMILY_SEVERITIES = {
    "modality_missing": 1.0,
    "field_missing": 0.3,
    "row_missing": 0.3,
    "feature_shuffle": 0.3,
    "gaussian_drift": 0.5,
}


def _stratified_subset(
    labels: np.ndarray, fraction: float, rng: np.random.Generator
) -> np.ndarray:
    selected: List[np.ndarray] = []
    for label in np.unique(labels):
        candidates = np.flatnonzero(labels == label)
        count = min(
            len(candidates),
            max(1, int(round(float(fraction) * len(candidates)))),
        )
        selected.append(
            np.sort(rng.choice(candidates, size=count, replace=False))
        )
    return np.sort(np.concatenate(selected))


def build_weighted_structured_training(
    views: Sequence[np.ndarray],
    labels: np.ndarray,
    *,
    augmentation_weight: float,
    sample_fraction: float,
    family_severities: Dict[str, float],
    seed: int,
) -> Tuple[List[np.ndarray], np.ndarray, np.ndarray, Dict[str, Any]]:
    arrays = [np.asarray(view) for view in views]
    labels = np.asarray(labels)
    if not arrays or any(len(view) != len(labels) for view in arrays):
        raise ValueError("structured augmentation requires aligned non-empty views")
    if not 0.0 <= augmentation_weight <= 1.0:
        raise ValueError("augmentation_weight must be in [0, 1]")
    if not 0.0 < sample_fraction <= 1.0:
        raise ValueError("sample_fraction must be in (0, 1]")
    if set(family_severities) != set(DEFAULT_FAMILY_SEVERITIES):
        raise ValueError("all five frozen corruption families are required")
    severities = {
        name: float(value) for name, value in family_severities.items()
    }
    if severities["modality_missing"] != 1.0:
        raise ValueError("modality_missing severity must be 1")
    for name in ("field_missing", "row_missing", "feature_shuffle"):
        if not 0.0 < severities[name] <= 1.0:
            raise ValueError(f"{name} severity must be in (0, 1]")
    if severities["gaussian_drift"] <= 0.0:
        raise ValueError("gaussian_drift severity must be positive")

    if augmentation_weight == 0.0:
        return (
            [view.copy() for view in arrays],
            labels.copy(),
            np.ones(len(labels), dtype=np.float64),
            {
                "enabled": False,
                "families": list(family_severities),
                "clean_rows": int(len(labels)),
                "augmented_rows": 0,
                "unknown_or_test_labels_used": False,
            },
        )

    parts: List[List[np.ndarray]] = [[view.copy()] for view in arrays]
    label_parts = [labels.copy()]
    block_records: List[Dict[str, Any]] = []
    rng_root = np.random.default_rng(int(seed))
    for family_index, family in enumerate(family_severities):
        severity = severities[family]
        for view_index in range(len(arrays)):
            block_seed = int(
                rng_root.integers(0, np.iinfo(np.int32).max)
                + 1009 * (family_index + 1)
                + 9176 * (view_index + 1)
            )
            rng = np.random.default_rng(block_seed)
            selected = _stratified_subset(labels, sample_fraction, rng)
            block_labels = labels[selected].copy()
            block_views = [view[selected].copy() for view in arrays]
            target = block_views[view_index]
            affected = 0

            if family == "modality_missing":
                target.fill(0.0)
                affected = int(target.size)
            elif family == "field_missing":
                mask = rng.random(target.shape) < severity
                target[mask] = 0.0
                affected = int(mask.sum())
            elif family == "row_missing":
                mask = rng.random(len(target)) < severity
                target[mask] = 0.0
                affected = int(mask.sum() * target.shape[1])
            elif family == "feature_shuffle":
                for label in np.unique(block_labels):
                    positions = np.flatnonzero(block_labels == label)
                    chosen = positions[rng.random(len(positions)) < severity]
                    if len(chosen) > 1:
                        target[chosen] = target[rng.permutation(chosen)]
                        affected += int(len(chosen) * target.shape[1])
            elif family == "gaussian_drift":
                scale = np.std(arrays[view_index], axis=0)
                scale = np.where(
                    np.isfinite(scale) & (scale > 1e-12), scale, 1.0
                )
                target += rng.normal(0.0, severity, size=target.shape) * scale
                affected = int(target.size)
            else:  # pragma: no cover - guarded by the family-set check.
                raise ValueError(f"unsupported augmentation family: {family}")

            if not np.isfinite(target).all():
                raise ValueError("structured augmentation produced non-finite values")
            for index, block in enumerate(block_views):
                parts[index].append(block)
            label_parts.append(block_labels)
            block_records.append(
                {
                    "family": family,
                    "view_index": int(view_index),
                    "severity": severity,
                    "seed": block_seed,
                    "rows": int(len(selected)),
                    "affected_entries": affected,
                }
            )

    augmented_rows = sum(record["rows"] for record in block_records)
    per_augmented_row_weight = (
        float(augmentation_weight) * len(labels) / augmented_rows
    )
    weights = [
        np.ones(len(labels), dtype=np.float64),
        *[
            np.full(record["rows"], per_augmented_row_weight, dtype=np.float64)
            for record in block_records
        ],
    ]
    return (
        [np.concatenate(view_parts, axis=0) for view_parts in parts],
        np.concatenate(label_parts),
        np.concatenate(weights),
        {
            "enabled": True,
            "families": list(family_severities),
            "family_severities": severities,
            "sample_fraction": float(sample_fraction),
            "augmentation_seed": int(seed),
            "augmentation_weight": float(augmentation_weight),
            "clean_rows": int(len(labels)),
            "augmented_rows": int(augmented_rows),
            "augmented_effective_weight": float(
                per_augmented_row_weight * augmented_rows
            ),
            "blocks": block_records,
            "feature_shuffle_is_within_known_class": True,
            "unknown_or_test_labels_used": False,
        },
    )


class StructuredRobustHybridClassifier(ConflictAwareHybridClassifier):
    """Clean specialists plus a five-family augmented global classifier."""

    def __init__(
        self,
        *args: Any,
        structured_augmentation_weight: float = 0.25,
        structured_sample_fraction: float = 0.25,
        structured_family_severities: Dict[str, float] = None,
        structured_augmentation_seed: int = 331,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.structured_augmentation_weight = float(
            structured_augmentation_weight
        )
        self.structured_sample_fraction = float(structured_sample_fraction)
        self.structured_family_severities = dict(
            DEFAULT_FAMILY_SEVERITIES
            if structured_family_severities is None
            else structured_family_severities
        )
        self.structured_augmentation_seed = int(
            structured_augmentation_seed
        )
        self.augmentation_metadata: Dict[str, Any] = {}

    def _reselect_clean_fusion(
        self,
        validation_views: Sequence[np.ndarray],
        validation_labels: np.ndarray,
    ) -> None:
        validation_labels = np.asarray(validation_labels)
        validation_values = self._global_values(validation_views)
        rf_validation = self.random_forest.predict_proba(validation_values)
        et_validation = self.extra_trees.predict_proba(validation_values)
        best_global = (-1.0, 0.5)
        for rf_weight in np.linspace(0.0, 1.0, 101):
            probability = (
                rf_weight * rf_validation
                + (1.0 - rf_weight) * et_validation
            )
            score = self._macro_f1(validation_labels, probability)
            candidate = (score, -abs(float(rf_weight) - 0.5))
            incumbent = (best_global[0], -abs(best_global[1] - 0.5))
            if candidate > incumbent:
                best_global = (score, float(rf_weight))
        self.global_rf_weight = best_global[1]
        global_validation = _normalize_probability(
            self.global_rf_weight * rf_validation
            + (1.0 - self.global_rf_weight) * et_validation
        )

        evidence = self._view_evidence(validation_views)
        best_gated = (best_global[0], 0.0, 0.0)
        for view_weight in np.linspace(0.0, 0.5, 26):
            for conflict_scale in (0.0, 1.0, 2.0, 4.0, 8.0):
                gate = view_weight * np.exp(
                    -conflict_scale * evidence["global_conflict"]
                )
                probability = _normalize_probability(
                    (1.0 - gate[:, None]) * global_validation
                    + gate[:, None] * evidence["view_fused_probability"]
                )
                score = self._macro_f1(validation_labels, probability)
                candidate = (
                    score,
                    -float(view_weight),
                    -float(conflict_scale),
                )
                incumbent = (
                    best_gated[0],
                    -best_gated[1],
                    -best_gated[2],
                )
                if candidate > incumbent:
                    best_gated = (
                        score,
                        float(view_weight),
                        float(conflict_scale),
                    )
        if best_gated[0] >= best_global[0] + self.minimum_view_gain:
            self.view_weight = best_gated[1]
            self.conflict_scale = best_gated[2]
            selected_score = best_gated[0]
        else:
            self.view_weight = 0.0
            self.conflict_scale = 0.0
            selected_score = best_global[0]
        selected_gate = self.view_weight * np.exp(
            -self.conflict_scale * evidence["global_conflict"]
        )
        selected_validation = _normalize_probability(
            (1.0 - selected_gate[:, None]) * global_validation
            + selected_gate[:, None] * evidence["view_fused_probability"]
        )
        best_temperature = (float("inf"), 1.0)
        for temperature in np.linspace(0.5, 2.0, 61):
            calibrated = temperature_scale(selected_validation, temperature)
            nll = -np.log(
                calibrated[np.arange(len(validation_labels)), validation_labels]
            ).mean()
            candidate = (
                float(nll),
                abs(float(temperature) - 1.0),
            )
            incumbent = (
                best_temperature[0],
                abs(best_temperature[1] - 1.0),
            )
            if candidate < incumbent:
                best_temperature = (float(nll), float(temperature))
        self.temperature = best_temperature[1]
        self.validation_scores = {
            "random_forest": self._macro_f1(
                validation_labels, rf_validation
            ),
            "extra_trees": self._macro_f1(
                validation_labels, et_validation
            ),
            "global_ensemble": best_global[0],
            "best_gated_candidate": best_gated[0],
            "selected": selected_score,
            "calibrated_nll": best_temperature[0],
            "training_augmentation": self.augmentation_metadata,
        }

    def fit(
        self,
        train_views: Sequence[np.ndarray],
        train_labels: np.ndarray,
        validation_views: Sequence[np.ndarray],
        validation_labels: np.ndarray,
    ) -> "StructuredRobustHybridClassifier":
        ConflictAwareHybridClassifier.fit(
            self,
            train_views,
            train_labels,
            validation_views,
            validation_labels,
        )
        clean_baseline_score = float(self.validation_scores["selected"])
        augmented_views, augmented_labels, weights, metadata = (
            build_weighted_structured_training(
                train_views,
                train_labels,
                augmentation_weight=self.structured_augmentation_weight,
                sample_fraction=self.structured_sample_fraction,
                family_severities=self.structured_family_severities,
                seed=self.structured_augmentation_seed,
            )
        )
        self.augmentation_metadata = metadata
        if metadata["enabled"]:
            augmented_values = self._global_values(augmented_views)
            self.random_forest.fit(
                augmented_values, augmented_labels, sample_weight=weights
            )
            self.extra_trees.fit(
                augmented_values, augmented_labels, sample_weight=weights
            )
            self._reselect_clean_fusion(validation_views, validation_labels)
        self.validation_scores["clean_baseline_without_augmentation"] = (
            clean_baseline_score
        )
        self.validation_scores["clean_delta_from_baseline"] = float(
            self.validation_scores["selected"] - clean_baseline_score
        )
        self.validation_scores["structured_training_augmentation"] = metadata
        return self
