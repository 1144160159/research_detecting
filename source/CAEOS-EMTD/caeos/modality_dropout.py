from __future__ import annotations

from typing import Sequence

import numpy as np

from caeos.hybrid import (
    ConflictAwareHybridClassifier,
    _normalize_probability,
    temperature_scale,
)


def build_weighted_modality_dropout_training(
    views: Sequence[np.ndarray],
    labels: np.ndarray,
    copies: int,
    augmentation_weight: float,
    dropout_view_count: int | None = None,
    field_dropout_severities: Sequence[float] = (),
    seed: int = 7,
) -> tuple[list[np.ndarray], np.ndarray, np.ndarray, dict[str, object]]:
    arrays = [np.asarray(view) for view in views]
    labels = np.asarray(labels)
    if not arrays or any(len(view) != len(labels) for view in arrays):
        raise ValueError("modality-dropout training requires aligned non-empty views")
    if copies < 0:
        raise ValueError("modality-dropout copies must be non-negative")
    if augmentation_weight < 0.0:
        raise ValueError("modality-dropout augmentation weight must be non-negative")
    severities = tuple(float(value) for value in field_dropout_severities)
    if any(not 0.0 < value < 1.0 for value in severities):
        raise ValueError("field-dropout severities must be in (0, 1)")
    count = len(arrays) if dropout_view_count is None else int(dropout_view_count)
    if count < 1 or count > len(arrays):
        raise ValueError("dropout_view_count must select available views")
    block_specs = [
        ("modality_missing", missing_index, 1.0, repeat)
        for repeat in range(copies)
        for missing_index in range(count)
    ]
    block_specs.extend(
        ("field_missing", missing_index, severity, severity_index)
        for severity_index, severity in enumerate(severities)
        for missing_index in range(count)
    )
    if not block_specs or augmentation_weight == 0.0:
        return (
            [view.copy() for view in arrays],
            labels.copy(),
            np.ones(len(labels), dtype=np.float64),
            {
                "enabled": False,
                "copies_per_modality": 0,
                "field_dropout_severities": list(severities),
                "dropout_view_count": count,
                "clean_rows": int(len(labels)),
                "augmented_rows": 0,
                "total_augmentation_weight": 0.0,
                "unknown_or_test_labels_used": False,
            },
        )

    parts: list[list[np.ndarray]] = [[view.copy()] for view in arrays]
    label_parts = [labels.copy()]
    weight_parts = [np.ones(len(labels), dtype=np.float64)]
    per_block_weight = float(augmentation_weight) / float(len(block_specs))
    affected_entries: dict[str, int] = {}
    for block_index, (kind, missing_index, severity, repeat) in enumerate(block_specs):
        for view_index, view in enumerate(arrays):
            block = view.copy()
            if view_index == missing_index:
                if kind == "modality_missing":
                    block.fill(0.0)
                    affected = int(block.size)
                else:
                    rng = np.random.default_rng(
                        int(seed)
                        + 1009 * (missing_index + 1)
                        + 9176 * (repeat + 1)
                    )
                    mask = rng.random(block.shape) < severity
                    block[mask] = 0.0
                    affected = int(mask.sum())
                affected_entries[f"block_{block_index}"] = affected
            parts[view_index].append(block)
        label_parts.append(labels.copy())
        weight_parts.append(
            np.full(len(labels), per_block_weight, dtype=np.float64)
        )
    augmented_rows = len(block_specs) * len(labels)
    return (
        [np.concatenate(view_parts, axis=0) for view_parts in parts],
        np.concatenate(label_parts),
        np.concatenate(weight_parts),
        {
            "enabled": True,
            "copies_per_modality": int(copies),
            "field_dropout_severities": list(severities),
            "dropout_view_count": int(count),
            "clean_rows": int(len(labels)),
            "augmented_rows": int(augmented_rows),
            "augmentation_block_count": int(len(block_specs)),
            "affected_entries_by_block": affected_entries,
            "per_augmented_block_weight": per_block_weight,
            "total_augmentation_weight": float(augmentation_weight),
            "clean_effective_weight": float(len(labels)),
            "augmented_effective_weight": float(len(labels) * augmentation_weight),
            "unknown_or_test_labels_used": False,
        },
    )


class ModalityDropoutHybridClassifier(ConflictAwareHybridClassifier):
    """Global clean-plus-missing training with clean single-view specialists."""

    def __init__(
        self,
        *args,
        modality_dropout_copies: int = 1,
        modality_dropout_weight: float = 1.0,
        dropout_view_count: int | None = None,
        field_dropout_severities: Sequence[float] = (),
        augmentation_seed: int | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.modality_dropout_copies = int(modality_dropout_copies)
        self.modality_dropout_weight = float(modality_dropout_weight)
        self.dropout_view_count = dropout_view_count
        self.field_dropout_severities = tuple(field_dropout_severities)
        self.augmentation_seed = self.seed if augmentation_seed is None else int(augmentation_seed)
        self.augmentation_metadata: dict[str, object] = {}

    def _validation_corruption_scores(
        self,
        validation_views: Sequence[np.ndarray],
        validation_labels: np.ndarray,
    ) -> dict[str, object]:
        labels = np.asarray(validation_labels)
        scores: dict[str, float] = {}
        count = (
            len(validation_views)
            if self.dropout_view_count is None
            else int(self.dropout_view_count)
        )
        for severity_index, severity in enumerate(self.field_dropout_severities):
            for view_index in range(count):
                corrupted = [np.asarray(view).copy() for view in validation_views]
                rng = np.random.default_rng(
                    self.augmentation_seed
                    + 50021
                    + 1009 * (view_index + 1)
                    + 9176 * (severity_index + 1)
                )
                mask = rng.random(corrupted[view_index].shape) < severity
                corrupted[view_index][mask] = 0.0
                probability = self.predict_proba(corrupted)
                scores[f"field_missing_{severity:.6g}_view{view_index}"] = (
                    self._macro_f1(labels, probability)
                )
        values = tuple(scores.values())
        return {
            "uses_known_validation_labels_only": True,
            "unknown_or_test_labels_used": False,
            "scores": scores,
            "mean_macro_f1": float(np.mean(values)) if values else None,
            "minimum_macro_f1": float(np.min(values)) if values else None,
            "minimax_objective": (
                float(0.5 * np.mean(values) + 0.5 * np.min(values))
                if values
                else None
            ),
        }

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
            probability = rf_weight * rf_validation + (1.0 - rf_weight) * et_validation
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
                candidate = (score, -float(view_weight), -float(conflict_scale))
                incumbent = (best_gated[0], -best_gated[1], -best_gated[2])
                if candidate > incumbent:
                    best_gated = (score, float(view_weight), float(conflict_scale))
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
            candidate = (float(nll), abs(float(temperature) - 1.0))
            incumbent = (best_temperature[0], abs(best_temperature[1] - 1.0))
            if candidate < incumbent:
                best_temperature = (float(nll), float(temperature))
        self.temperature = best_temperature[1]
        self.validation_scores = {
            "random_forest": self._macro_f1(validation_labels, rf_validation),
            "extra_trees": self._macro_f1(validation_labels, et_validation),
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
    ) -> "ModalityDropoutHybridClassifier":
        super().fit(train_views, train_labels, validation_views, validation_labels)
        clean_baseline_score = float(self.validation_scores["selected"])
        augmented_views, augmented_labels, sample_weight, metadata = (
            build_weighted_modality_dropout_training(
                train_views,
                train_labels,
                self.modality_dropout_copies,
                self.modality_dropout_weight,
                self.dropout_view_count,
                self.field_dropout_severities,
                self.augmentation_seed,
            )
        )
        self.augmentation_metadata = metadata
        if metadata["enabled"]:
            augmented_values = self._global_values(augmented_views)
            self.random_forest.fit(
                augmented_values, augmented_labels, sample_weight=sample_weight
            )
            self.extra_trees.fit(
                augmented_values, augmented_labels, sample_weight=sample_weight
            )
            self._reselect_clean_fusion(validation_views, validation_labels)
        else:
            self.validation_scores["training_augmentation"] = metadata
        self.validation_scores["clean_baseline_without_augmentation"] = (
            clean_baseline_score
        )
        self.validation_scores["clean_delta_from_baseline"] = float(
            self.validation_scores["selected"] - clean_baseline_score
        )
        self.validation_scores["field_dropout_validation"] = (
            self._validation_corruption_scores(validation_views, validation_labels)
        )
        return self
