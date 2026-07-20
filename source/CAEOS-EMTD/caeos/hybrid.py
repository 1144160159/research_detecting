from __future__ import annotations

from typing import Dict, List, Sequence

import numpy as np
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.svm import SVC


def _normalize_probability(probability: np.ndarray) -> np.ndarray:
    probability = np.asarray(probability, dtype=np.float64)
    probability = np.clip(probability, 1e-12, None)
    return probability / probability.sum(axis=-1, keepdims=True)


def normalized_entropy(probability: np.ndarray) -> np.ndarray:
    probability = _normalize_probability(probability)
    num_classes = probability.shape[-1]
    if num_classes <= 1:
        return np.zeros(probability.shape[:-1], dtype=np.float64)
    return -(probability * np.log(probability)).sum(axis=-1) / np.log(num_classes)


def temperature_scale(probability: np.ndarray, temperature: float) -> np.ndarray:
    probability = _normalize_probability(probability)
    return _normalize_probability(
        np.exp(np.log(probability) / max(float(temperature), 1e-6))
    )


def js_divergence(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Normalized Jensen-Shannon divergence for paired class probabilities."""
    left = _normalize_probability(left)
    right = _normalize_probability(right)
    mixture = 0.5 * (left + right)
    return np.clip(
        0.5
        * (
            (left * np.log(left / mixture)).sum(axis=-1)
            + (right * np.log(right / mixture)).sum(axis=-1)
        )
        / np.log(2.0),
        0.0,
        1.0,
    )


def probabilistic_or_conflict(*conflicts: np.ndarray) -> np.ndarray:
    """Combine bounded conflict signals without discarding moderate evidence."""
    if not conflicts:
        raise ValueError("at least one conflict signal is required")
    complement = np.ones_like(np.asarray(conflicts[0], dtype=np.float64))
    for conflict in conflicts:
        complement *= 1.0 - np.clip(conflict, 0.0, 1.0)
    return np.clip(1.0 - complement, 0.0, 1.0)


def pairwise_js_conflict(
    view_probability: np.ndarray, reliability: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Return pairwise JS conflict and its reliability-weighted global value."""
    probability = _normalize_probability(view_probability)
    reliability = np.asarray(reliability, dtype=np.float64)
    if probability.ndim != 3:
        raise ValueError("view_probability must have shape [samples, views, classes]")
    if reliability.shape != probability.shape[:2]:
        raise ValueError("reliability must have shape [samples, views]")

    samples, views, _ = probability.shape
    pairwise = np.zeros((samples, views, views), dtype=np.float64)
    for left in range(views):
        for right in range(left + 1, views):
            left_probability = probability[:, left]
            right_probability = probability[:, right]
            mixture = 0.5 * (left_probability + right_probability)
            divergence = 0.5 * (
                (left_probability * np.log(left_probability / mixture)).sum(axis=1)
                + (right_probability * np.log(right_probability / mixture)).sum(axis=1)
            ) / np.log(2.0)
            pairwise[:, left, right] = divergence
            pairwise[:, right, left] = divergence

    pair_weight = reliability[:, :, None] * reliability[:, None, :]
    upper = np.triu(np.ones((views, views), dtype=np.float64), k=1)[None, :, :]
    global_conflict = (pairwise * pair_weight * upper).sum(axis=(1, 2)) / np.clip(
        (pair_weight * upper).sum(axis=(1, 2)), 1e-12, None
    )
    return pairwise, np.clip(global_conflict, 0.0, 1.0)


class ConflictAwareHybridClassifier:
    """Strong global classifier with independent view evidence and conflict gating."""

    def __init__(
        self,
        estimators: int = 200,
        seed: int = 7,
        jobs: int = -1,
        minimum_view_gain: float = 0.002,
        global_max_features: str | float = "sqrt",
        global_seed_offsets: tuple[int, int] = (0, 0),
        global_view_count: int | None = None,
    ):
        self.estimators = int(estimators)
        self.seed = int(seed)
        self.jobs = int(jobs)
        self.minimum_view_gain = float(minimum_view_gain)
        self.global_max_features = global_max_features
        self.global_seed_offsets = tuple(map(int, global_seed_offsets))
        self.global_view_count = (
            None if global_view_count is None else int(global_view_count)
        )
        common = {
            "n_estimators": self.estimators,
            "class_weight": "balanced_subsample",
            "n_jobs": self.jobs,
            "max_features": self.global_max_features,
        }
        self.random_forest = RandomForestClassifier(
            random_state=self.seed + self.global_seed_offsets[0], **common
        )
        self.extra_trees = ExtraTreesClassifier(
            random_state=self.seed + self.global_seed_offsets[1], **common
        )
        self.view_models: List[ExtraTreesClassifier] = []
        self.global_rf_weight = 0.5
        self.view_weight = 0.0
        self.conflict_scale = 0.0
        self.temperature = 1.0
        self.view_validation_reliability: np.ndarray | None = None
        self.validation_scores: Dict[str, float] = {}

    @staticmethod
    def _concatenate(views: Sequence[np.ndarray]) -> np.ndarray:
        return np.concatenate([np.asarray(view) for view in views], axis=1)

    @staticmethod
    def _macro_f1(labels: np.ndarray, probability: np.ndarray) -> float:
        return float(
            f1_score(
                labels,
                probability.argmax(axis=1),
                average="macro",
                zero_division=0,
            )
        )

    def _global_probability(self, views: Sequence[np.ndarray]) -> np.ndarray:
        values = self._global_values(views)
        return _normalize_probability(
            self.global_rf_weight * self.random_forest.predict_proba(values)
            + (1.0 - self.global_rf_weight) * self.extra_trees.predict_proba(values)
        )

    def _global_values(self, views: Sequence[np.ndarray]) -> np.ndarray:
        count = len(views) if self.global_view_count is None else self.global_view_count
        if count < 1 or count > len(views):
            raise ValueError("global_view_count must select at least one available view")
        return self._concatenate(views[:count])

    def _view_evidence(self, views: Sequence[np.ndarray]) -> Dict[str, np.ndarray]:
        view_probability = np.stack(
            [model.predict_proba(view) for model, view in zip(self.view_models, views)],
            axis=1,
        )
        view_uncertainty = normalized_entropy(view_probability)
        confidence = 1.0 - view_uncertainty
        base_reliability = self.view_validation_reliability[None, :]
        reliability = base_reliability * (0.25 + 0.75 * confidence)
        reliability = np.clip(reliability, 1e-6, 1.0)
        view_evidence = reliability[:, :, None] * confidence[:, :, None] * view_probability
        fused_probability = (
            reliability[:, :, None] * view_probability
        ).sum(axis=1) / reliability.sum(axis=1, keepdims=True)
        pairwise, global_conflict = pairwise_js_conflict(
            view_probability, reliability
        )
        other_reliability = reliability[:, None, :] * (
            1.0 - np.eye(reliability.shape[1], dtype=np.float64)[None, :, :]
        )
        local_conflict = (pairwise * other_reliability).sum(axis=2) / np.clip(
            other_reliability.sum(axis=2), 1e-12, None
        )
        return {
            "view_probability": view_probability,
            "view_evidence": view_evidence,
            "view_uncertainty": view_uncertainty,
            "view_reliability": reliability,
            "view_fused_probability": _normalize_probability(fused_probability),
            "pairwise_conflict": pairwise,
            "global_conflict": global_conflict,
            "local_conflict": local_conflict,
        }

    def fit(
        self,
        train_views: Sequence[np.ndarray],
        train_labels: np.ndarray,
        validation_views: Sequence[np.ndarray],
        validation_labels: np.ndarray,
    ) -> "ConflictAwareHybridClassifier":
        if len(train_views) < 2 or len(train_views) != len(validation_views):
            raise ValueError("matching train/validation views are required")
        train_labels = np.asarray(train_labels)
        validation_labels = np.asarray(validation_labels)
        train_values = self._global_values(train_views)
        validation_values = self._global_values(validation_views)
        self.random_forest.fit(train_values, train_labels)
        self.extra_trees.fit(train_values, train_labels)

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

        self.view_models = []
        view_scores = []
        for index, (train_view, validation_view) in enumerate(
            zip(train_views, validation_views)
        ):
            model = ExtraTreesClassifier(
                n_estimators=self.estimators,
                class_weight="balanced_subsample",
                n_jobs=self.jobs,
                random_state=self.seed + 101 * (index + 1),
            )
            model.fit(train_view, train_labels)
            self.view_models.append(model)
            view_scores.append(
                self._macro_f1(validation_labels, model.predict_proba(validation_view))
            )
        self.view_validation_reliability = np.clip(
            np.asarray(view_scores, dtype=np.float64), 0.05, 1.0
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
        }
        return self

    def predict_with_evidence(
        self, views: Sequence[np.ndarray]
    ) -> Dict[str, np.ndarray]:
        global_probability = self._global_probability(views)
        evidence = self._view_evidence(views)
        gate = self.view_weight * np.exp(
            -self.conflict_scale * evidence["global_conflict"]
        )
        final_probability = _normalize_probability(
            (1.0 - gate[:, None]) * global_probability
            + gate[:, None] * evidence["view_fused_probability"]
        )
        final_probability = temperature_scale(final_probability, self.temperature)
        return {
            **evidence,
            "global_probability": global_probability,
            "gate": gate,
            "final_probability": final_probability,
            "uncertainty": normalized_entropy(final_probability),
        }

    def predict_proba(self, views: Sequence[np.ndarray]) -> np.ndarray:
        return self.predict_with_evidence(views)["final_probability"]


class PairwiseSpecialistHybridClassifier(ConflictAwareHybridClassifier):
    """MC6: MC5 plus validation-selected experts for highly confused class pairs."""

    def __init__(
        self,
        *args,
        max_specialists: int = 4,
        minimum_pair_errors: int = 3,
        minimum_specialist_gain: float = 1e-4,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.max_specialists = int(max_specialists)
        self.minimum_pair_errors = int(minimum_pair_errors)
        self.minimum_specialist_gain = float(minimum_specialist_gain)
        self.specialists: List[Dict[str, object]] = []

    @staticmethod
    def _route_mask(probability: np.ndarray, pair: tuple[int, int], threshold: float):
        top_two = np.argpartition(probability, -2, axis=1)[:, -2:]
        contains_pair = np.isin(top_two, np.asarray(pair)).sum(axis=1) == 2
        pair_mass = probability[:, pair[0]] + probability[:, pair[1]]
        return contains_pair & (pair_mass >= threshold)

    @classmethod
    def _apply_one_specialist(
        cls,
        values: np.ndarray,
        probability: np.ndarray,
        specialist: Dict[str, object],
    ) -> tuple[np.ndarray, np.ndarray]:
        pair = specialist["pair"]
        threshold = float(specialist["threshold"])
        blend = float(specialist["blend"])
        model = specialist["model"]
        mask = cls._route_mask(probability, pair, threshold)
        if not np.any(mask):
            return probability, mask

        updated = probability.copy()
        pair_mass = updated[mask, pair[0]] + updated[mask, pair[1]]
        old_ratio = updated[np.ix_(mask, pair)] / pair_mass[:, None]
        specialist_probability = model.predict_proba(values[mask])
        class_to_column = {
            int(label): index for index, label in enumerate(model.classes_)
        }
        ordered_probability = specialist_probability[
            :, [class_to_column[pair[0]], class_to_column[pair[1]]]
        ]
        ratio = (1.0 - blend) * old_ratio + blend * ordered_probability
        updated[np.ix_(mask, pair)] = pair_mass[:, None] * ratio
        return _normalize_probability(updated), mask

    def fit(
        self,
        train_views: Sequence[np.ndarray],
        train_labels: np.ndarray,
        validation_views: Sequence[np.ndarray],
        validation_labels: np.ndarray,
    ) -> "PairwiseSpecialistHybridClassifier":
        super().fit(train_views, train_labels, validation_views, validation_labels)
        train_labels = np.asarray(train_labels)
        validation_labels = np.asarray(validation_labels)
        train_values = self._concatenate(train_views)
        validation_values = self._concatenate(validation_views)
        probability = super().predict_with_evidence(validation_views)[
            "final_probability"
        ]
        number_of_classes = probability.shape[1]
        matrix = confusion_matrix(
            validation_labels,
            probability.argmax(axis=1),
            labels=np.arange(number_of_classes),
        )
        pair_candidates = []
        for left in range(number_of_classes):
            for right in range(left + 1, number_of_classes):
                errors = int(matrix[left, right] + matrix[right, left])
                if errors >= self.minimum_pair_errors:
                    pair_candidates.append((errors, left, right))
        pair_candidates.sort(reverse=True)

        self.specialists = []
        current_score = self._macro_f1(validation_labels, probability)
        for errors, left, right in pair_candidates[: self.max_specialists]:
            pair = (left, right)
            train_mask = np.isin(train_labels, pair)
            if np.unique(train_labels[train_mask]).size != 2:
                continue
            model = SVC(
                C=10.0,
                gamma="scale",
                kernel="rbf",
                probability=True,
                class_weight="balanced",
                random_state=self.seed + 1009 * (len(self.specialists) + 1),
            )
            model.fit(train_values[train_mask], train_labels[train_mask])
            best = (current_score, 0.0, 1.0, probability, 0)
            for threshold in (0.5, 0.7, 0.85, 0.95):
                for blend in (0.25, 0.5, 0.75, 1.0):
                    candidate_specialist = {
                        "pair": pair,
                        "threshold": threshold,
                        "blend": blend,
                        "model": model,
                    }
                    candidate_probability, active = self._apply_one_specialist(
                        validation_values, probability, candidate_specialist
                    )
                    score = self._macro_f1(
                        validation_labels, candidate_probability
                    )
                    candidate = (score, -blend, threshold)
                    incumbent = (best[0], -best[2], best[1])
                    if candidate > incumbent:
                        best = (
                            score,
                            threshold,
                            blend,
                            candidate_probability,
                            int(active.sum()),
                        )
            if best[0] < current_score + self.minimum_specialist_gain:
                continue
            self.specialists.append(
                {
                    "pair": pair,
                    "threshold": best[1],
                    "blend": best[2],
                    "model": model,
                    "validation_errors": errors,
                    "validation_activations": best[4],
                    "validation_macro_f1": best[0],
                }
            )
            probability = best[3]
            current_score = best[0]
        self.validation_scores["after_pairwise_specialists"] = current_score
        return self

    def specialist_metadata(self) -> List[Dict[str, object]]:
        return [
            {key: value for key, value in specialist.items() if key != "model"}
            for specialist in self.specialists
        ]

    def predict_with_evidence(
        self, views: Sequence[np.ndarray]
    ) -> Dict[str, np.ndarray]:
        evidence = super().predict_with_evidence(views)
        values = self._concatenate(views)
        probability = evidence["final_probability"]
        activation = np.zeros((len(probability), len(self.specialists)), dtype=bool)
        for index, specialist in enumerate(self.specialists):
            probability, active = self._apply_one_specialist(
                values, probability, specialist
            )
            activation[:, index] = active
        evidence["pre_specialist_probability"] = evidence["final_probability"]
        evidence["specialist_activation"] = activation
        evidence["final_probability"] = probability
        evidence["uncertainty"] = normalized_entropy(probability)
        return evidence


class CorruptionRobustHybridClassifier(ConflictAwareHybridClassifier):
    """MC8: conflict-discounted experts with validation-only corruption routing."""

    def __init__(
        self,
        *args,
        minimum_robust_gain: float = 0.0005,
        clean_tolerance: float = 0.002,
        robust_minimum_weight: float = 0.3,
        routing_conflict_mode: str = "global",
        advanced_robust_search: bool = False,
        safety_fallback_mode: str = "none",
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.minimum_robust_gain = float(minimum_robust_gain)
        self.clean_tolerance = float(clean_tolerance)
        self.robust_minimum_weight = float(robust_minimum_weight)
        if not 0.0 <= self.robust_minimum_weight <= 1.0:
            raise ValueError("robust_minimum_weight must be in [0, 1]")
        if routing_conflict_mode not in {
            "global",
            "probabilistic_or",
            "adaptive_missingness",
            "local_max",
            "calibrated_local",
        }:
            raise ValueError(
                "routing_conflict_mode must be global, probabilistic_or, "
                "adaptive_missingness, local_max, or calibrated_local"
            )
        self.routing_conflict_mode = routing_conflict_mode
        self.advanced_robust_search = bool(advanced_robust_search)
        if safety_fallback_mode not in {"none", "validation_minimax"}:
            raise ValueError(
                "safety_fallback_mode must be none or validation_minimax"
            )
        self.safety_fallback_mode = safety_fallback_mode
        self.safety_use_uniform = False
        self.view_missingness_thresholds: np.ndarray | None = None
        self.view_local_conflict_thresholds: np.ndarray | None = None
        self.view_local_conflict_widths: np.ndarray | None = None
        self.robust_discount_scale = 0.0
        self.robust_trim_count = 0
        self.robust_max_view_weight = 0.0
        self.robust_conflict_threshold = 1.0
        self.robust_transition_width = 1.0
        self.robust_validation_scores: Dict[str, float] = {}

    @staticmethod
    def _discounted_view_probability(
        evidence: Dict[str, np.ndarray],
        discount_scale: float,
        trim_count: int = 0,
    ) -> np.ndarray:
        weight = evidence["view_reliability"] * np.exp(
            -float(discount_scale) * evidence["local_conflict"]
        )
        if trim_count > 0 and weight.shape[1] > trim_count:
            order = np.argsort(evidence["local_conflict"], axis=1)
            trimmed = order[:, -int(trim_count) :]
            rows = np.arange(len(weight))[:, None]
            weight[rows, trimmed] = 0.0
        probability = (
            weight[:, :, None] * evidence["view_probability"]
        ).sum(axis=1) / np.clip(weight.sum(axis=1, keepdims=True), 1e-12, None)
        return _normalize_probability(probability)

    def _robust_probability_from_evidence(
        self,
        evidence: Dict[str, np.ndarray],
        discount_scale: float,
        maximum_view_weight: float,
        conflict_threshold: float,
        transition_width: float,
        trim_count: int = 0,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        robust_view = self._discounted_view_probability(
            evidence, discount_scale, trim_count
        )
        global_view_conflict = js_divergence(
            evidence["global_probability"], robust_view
        )
        routing_conflict = self._routing_conflict(
            evidence["global_conflict"],
            global_view_conflict,
            evidence.get("missingness_score"),
            evidence.get("local_conflict"),
        )
        normalized_excess = np.clip(
            (routing_conflict - float(conflict_threshold))
            / max(float(transition_width), 1e-6),
            0.0,
            1.0,
        )
        gate = float(maximum_view_weight) * normalized_excess
        probability = _normalize_probability(
            (1.0 - gate[:, None]) * evidence["global_probability"]
            + gate[:, None] * robust_view
        )
        return probability, robust_view, gate, global_view_conflict

    def _routing_conflict(
        self,
        modal_conflict: np.ndarray,
        global_view_conflict: np.ndarray,
        missingness_score: np.ndarray | None = None,
        local_conflict: np.ndarray | None = None,
    ) -> np.ndarray:
        if self.routing_conflict_mode == "local_max":
            if local_conflict is None:
                return np.asarray(modal_conflict, dtype=np.float64)
            return np.max(np.asarray(local_conflict, dtype=np.float64), axis=1)
        if self.routing_conflict_mode == "calibrated_local":
            if (
                local_conflict is None
                or self.view_local_conflict_thresholds is None
                or self.view_local_conflict_widths is None
            ):
                return np.asarray(modal_conflict, dtype=np.float64)
            excess = (
                np.asarray(local_conflict, dtype=np.float64)
                - self.view_local_conflict_thresholds[None, :]
            ) / self.view_local_conflict_widths[None, :]
            return np.clip(excess, 0.0, 1.0).max(axis=1)
        if self.routing_conflict_mode == "probabilistic_or":
            return probabilistic_or_conflict(
                modal_conflict, global_view_conflict
            )
        if self.routing_conflict_mode == "adaptive_missingness":
            combined = probabilistic_or_conflict(
                modal_conflict, global_view_conflict
            )
            if missingness_score is None:
                return np.asarray(modal_conflict, dtype=np.float64)
            switch = np.clip(
                np.asarray(missingness_score, dtype=np.float64) / 0.25,
                0.0,
                1.0,
            )
            return modal_conflict + switch * (combined - modal_conflict)
        return np.asarray(modal_conflict, dtype=np.float64)

    def _missingness_score(self, views: Sequence[np.ndarray]) -> np.ndarray:
        fractions = np.stack(
            [
                np.mean(np.isclose(view, 0.0, atol=1e-12), axis=1)
                for view in views
            ],
            axis=1,
        )
        if self.view_missingness_thresholds is None:
            return np.zeros(len(fractions), dtype=np.float64)
        excess = (
            fractions - self.view_missingness_thresholds[None, :]
        ) / np.clip(1.0 - self.view_missingness_thresholds[None, :], 1e-6, None)
        return np.clip(excess, 0.0, 1.0).max(axis=1)

    def _validation_corruptions(
        self, validation_views: Sequence[np.ndarray]
    ) -> List[Sequence[np.ndarray]]:
        corruptions: List[Sequence[np.ndarray]] = []
        for view_index, view in enumerate(validation_views):
            rng = np.random.RandomState(self.seed + 7001 + view_index)
            permutation = rng.permutation(len(view))
            permuted = [np.asarray(values).copy() for values in validation_views]
            permuted[view_index] = np.asarray(view)[permutation]
            corruptions.append(permuted)

            for severity in (0.5, 1.0, 2.0, 4.0):
                gaussian = [np.asarray(values).copy() for values in validation_views]
                gaussian[view_index] = np.asarray(view) + rng.normal(
                    0.0, severity, size=np.asarray(view).shape
                )
                corruptions.append(gaussian)
        return corruptions

    def fit(
        self,
        train_views: Sequence[np.ndarray],
        train_labels: np.ndarray,
        validation_views: Sequence[np.ndarray],
        validation_labels: np.ndarray,
    ) -> "CorruptionRobustHybridClassifier":
        train_missingness = np.stack(
            [
                np.mean(np.isclose(view, 0.0, atol=1e-12), axis=1)
                for view in train_views
            ],
            axis=1,
        )
        self.view_missingness_thresholds = np.quantile(
            train_missingness, 0.99, axis=0
        )
        super().fit(train_views, train_labels, validation_views, validation_labels)
        validation_labels = np.asarray(validation_labels)
        clean_evidence = super().predict_with_evidence(validation_views)
        self.view_local_conflict_thresholds = np.quantile(
            clean_evidence["local_conflict"], 0.90, axis=0
        )
        upper_local_conflict = np.quantile(
            clean_evidence["local_conflict"], 0.99, axis=0
        )
        self.view_local_conflict_widths = np.maximum(
            upper_local_conflict - self.view_local_conflict_thresholds, 0.05
        )
        clean_evidence["missingness_score"] = self._missingness_score(
            validation_views
        )
        clean_standard_score = self._macro_f1(
            validation_labels, clean_evidence["final_probability"]
        )
        parent_predict = super().predict_with_evidence
        corruption_evidence = []
        for corrupted in self._validation_corruptions(validation_views):
            evidence = parent_predict(corrupted)
            evidence["missingness_score"] = self._missingness_score(corrupted)
            corruption_evidence.append(evidence)
        standard_corruption_scores = [
            self._macro_f1(validation_labels, evidence["final_probability"])
            for evidence in corruption_evidence
        ]
        baseline_mean = float(np.mean(standard_corruption_scores))
        baseline_minimum = float(np.min(standard_corruption_scores))
        baseline_objective = (
            (1.0 - self.robust_minimum_weight) * baseline_mean
            + self.robust_minimum_weight * baseline_minimum
        )
        clean_uniform_probability = _normalize_probability(
            clean_evidence["view_probability"].mean(axis=1)
        )
        clean_uniform_score = self._macro_f1(
            validation_labels, clean_uniform_probability
        )
        uniform_corruption_scores = [
            self._macro_f1(
                validation_labels,
                _normalize_probability(
                    evidence["view_probability"].mean(axis=1)
                ),
            )
            for evidence in corruption_evidence
        ]
        uniform_mean = float(np.mean(uniform_corruption_scores))
        uniform_minimum = float(np.min(uniform_corruption_scores))
        uniform_objective = (
            (1.0 - self.robust_minimum_weight) * uniform_mean
            + self.robust_minimum_weight * uniform_minimum
        )

        best = None
        discount_scales = (
            (0.0, 1.0, 2.0, 4.0)
            if self.advanced_robust_search
            else (0.0, 1.0, 2.0)
        )
        trim_counts = (0, 1) if self.advanced_robust_search else (0,)
        maximum_view_weights = (
            (0.25, 0.50, 0.75, 1.0)
            if self.advanced_robust_search
            else (0.75, 1.0)
        )
        transition_widths = (
            (0.05, 0.10, 0.20, 0.30)
            if self.advanced_robust_search
            else (0.10, 0.20, 0.30)
        )
        for discount_scale in discount_scales:
          for trim_count in trim_counts:
            clean_robust_view = self._discounted_view_probability(
                clean_evidence, discount_scale, trim_count
            )
            clean_routing_conflict = self._routing_conflict(
                clean_evidence["global_conflict"],
                js_divergence(
                    clean_evidence["global_probability"], clean_robust_view
                ),
                clean_evidence["missingness_score"],
                clean_evidence["local_conflict"],
            )
            threshold_candidates = {
                    0.05,
                    0.10,
                    0.15,
                    float(np.quantile(clean_routing_conflict, 0.90)),
                    float(np.quantile(clean_routing_conflict, 0.95)),
                    float(np.quantile(clean_routing_conflict, 0.99)),
                }
            if self.advanced_robust_search:
                threshold_candidates.add(-1.0)
            for maximum_view_weight in maximum_view_weights:
                for conflict_threshold in sorted(threshold_candidates):
                    for transition_width in transition_widths:
                        clean_probability, _, _, _ = self._robust_probability_from_evidence(
                            clean_evidence,
                            discount_scale,
                            maximum_view_weight,
                            conflict_threshold,
                            transition_width,
                            trim_count,
                        )
                        clean_score = self._macro_f1(
                            validation_labels, clean_probability
                        )
                        if clean_score < clean_standard_score - self.clean_tolerance:
                            continue
                        scores = []
                        for evidence in corruption_evidence:
                            probability, _, _, _ = self._robust_probability_from_evidence(
                                evidence,
                                discount_scale,
                                maximum_view_weight,
                                conflict_threshold,
                                transition_width,
                                trim_count,
                            )
                            scores.append(
                                self._macro_f1(validation_labels, probability)
                            )
                        score_mean = float(np.mean(scores))
                        score_minimum = float(np.min(scores))
                        objective = (
                            (1.0 - self.robust_minimum_weight) * score_mean
                            + self.robust_minimum_weight * score_minimum
                        )
                        candidate = (
                            objective,
                            score_minimum,
                            score_mean,
                            clean_score,
                            -maximum_view_weight,
                            -discount_scale,
                            -transition_width,
                            -trim_count,
                        )
                        if best is None or candidate > best[0]:
                            best = (
                                candidate,
                                float(discount_scale),
                                float(maximum_view_weight),
                                float(conflict_threshold),
                                float(transition_width),
                                int(trim_count),
                            )
        if (
            best is not None
            and best[0][0] >= baseline_objective + self.minimum_robust_gain
        ):
            self.robust_discount_scale = best[1]
            self.robust_max_view_weight = best[2]
            self.robust_conflict_threshold = best[3]
            self.robust_transition_width = best[4]
            self.robust_trim_count = best[5]
            selected_objective = best[0][0]
            selected_minimum = best[0][1]
            selected_mean = best[0][2]
            selected_clean = best[0][3]
        else:
            selected_objective = baseline_objective
            selected_mean = baseline_mean
            selected_minimum = baseline_minimum
            selected_clean = clean_standard_score
        if (
            self.safety_fallback_mode == "validation_minimax"
            and clean_uniform_score >= clean_standard_score - self.clean_tolerance
            and uniform_minimum
            >= selected_minimum + self.minimum_robust_gain
        ):
            self.safety_use_uniform = True
        safety_clean = clean_uniform_score if self.safety_use_uniform else selected_clean
        safety_mean = uniform_mean if self.safety_use_uniform else selected_mean
        safety_minimum = (
            uniform_minimum if self.safety_use_uniform else selected_minimum
        )
        safety_objective = (
            uniform_objective if self.safety_use_uniform else selected_objective
        )
        self.robust_validation_scores = {
            "clean_standard": clean_standard_score,
            "corrupted_standard_mean": baseline_mean,
            "corrupted_standard_minimum": baseline_minimum,
            "corrupted_standard_objective": baseline_objective,
            "clean_selected": selected_clean,
            "corrupted_selected_mean": selected_mean,
            "corrupted_selected_minimum": selected_minimum,
            "corrupted_selected_objective": selected_objective,
            "clean_uniform": clean_uniform_score,
            "corrupted_uniform_mean": uniform_mean,
            "corrupted_uniform_minimum": uniform_minimum,
            "corrupted_uniform_objective": uniform_objective,
            "safety_fallback_mode": self.safety_fallback_mode,
            "safety_use_uniform": self.safety_use_uniform,
            "clean_safety": safety_clean,
            "corrupted_safety_mean": safety_mean,
            "corrupted_safety_minimum": safety_minimum,
            "corrupted_safety_objective": safety_objective,
            "robust_minimum_weight": self.robust_minimum_weight,
            "routing_conflict_mode": self.routing_conflict_mode,
            "trim_count": self.robust_trim_count,
            "advanced_robust_search": self.advanced_robust_search,
        }
        return self

    def predict_with_evidence(
        self, views: Sequence[np.ndarray]
    ) -> Dict[str, np.ndarray]:
        evidence = super().predict_with_evidence(views)
        evidence["missingness_score"] = self._missingness_score(views)
        evidence["standard_final_probability"] = evidence["final_probability"]
        evidence["uniform_view_probability"] = _normalize_probability(
            evidence["view_probability"].mean(axis=1)
        )
        if self.robust_max_view_weight <= 0.0:
            evidence["robust_view_probability"] = evidence[
                "view_fused_probability"
            ]
            evidence["robust_gate"] = np.zeros(len(evidence["global_conflict"]))
            evidence["global_view_conflict"] = js_divergence(
                evidence["global_probability"], evidence["robust_view_probability"]
            )
            if self.safety_use_uniform:
                probability = temperature_scale(
                    evidence["uniform_view_probability"], self.temperature
                )
                evidence["pre_safety_probability"] = evidence[
                    "final_probability"
                ]
                evidence["final_probability"] = probability
                evidence["uncertainty"] = normalized_entropy(probability)
            return evidence
        probability, robust_view, gate, global_view_conflict = (
            self._robust_probability_from_evidence(
            evidence,
            self.robust_discount_scale,
            self.robust_max_view_weight,
            self.robust_conflict_threshold,
            self.robust_transition_width,
            self.robust_trim_count,
            )
        )
        probability = temperature_scale(probability, self.temperature)
        evidence["robust_view_probability"] = robust_view
        evidence["robust_gate"] = gate
        evidence["global_view_conflict"] = global_view_conflict
        evidence["pre_safety_probability"] = probability
        if self.safety_use_uniform:
            probability = temperature_scale(
                evidence["uniform_view_probability"], self.temperature
            )
        evidence["final_probability"] = probability
        evidence["uncertainty"] = normalized_entropy(probability)
        return evidence
