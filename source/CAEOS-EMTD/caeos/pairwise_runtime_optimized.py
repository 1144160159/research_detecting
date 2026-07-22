from __future__ import annotations

from typing import Sequence

import numpy as np

from caeos.hybrid_open_set import (
    bonferroni_union_risk,
    cauchy_combined_risk,
    hybrid_open_set_components,
    jensen_shannon_divergence,
    weighted_risk,
)
from caeos.hybrid import (
    ConflictAwareHybridClassifier,
    _normalize_probability,
    normalized_entropy,
    temperature_scale,
)
from caeos.pairwise_runtime import PairwiseRuntime, stable_empirical_tail_scores


REFERENCE_COMPONENTS = ("conflict", "tree_disagreement", "distance")
OPTIONAL_COMPONENTS = {"knn_distance", "class_knn_distance", "lof_density"}


def demand_driven_open_set_components(
    model,
    views: Sequence[np.ndarray],
    distance_model,
    distance_values: np.ndarray,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Reuse global forest probabilities for the supported frozen classifier."""
    if type(model) is not ConflictAwareHybridClassifier:
        return hybrid_open_set_components(
            model, views, distance_model, distance_values
        )

    global_values = model._global_values(views)
    rf_probability = model.random_forest.predict_proba(global_values)
    et_probability = model.extra_trees.predict_proba(global_values)
    global_probability = _normalize_probability(
        model.global_rf_weight * rf_probability
        + (1.0 - model.global_rf_weight) * et_probability
    )
    evidence = model._view_evidence(views)
    gate = model.view_weight * np.exp(
        -model.conflict_scale * evidence["global_conflict"]
    )
    probability = _normalize_probability(
        (1.0 - gate[:, None]) * global_probability
        + gate[:, None] * evidence["view_fused_probability"]
    )
    probability = temperature_scale(probability, model.temperature)
    sorted_probability = np.sort(probability, axis=1)
    components = {
        "uncertainty": normalized_entropy(probability),
        "inverse_belief": 1.0 - probability.max(axis=1),
        "inverse_margin": 1.0
        - (sorted_probability[:, -1] - sorted_probability[:, -2]),
        "conflict": np.asarray(evidence["global_conflict"], dtype=np.float64),
        "tree_disagreement": jensen_shannon_divergence(
            rf_probability, et_probability
        ),
        "distance": distance_model.score(distance_values),
    }
    return components, probability


class OptimizedPairwiseRuntime:
    """Demand-driven, numerically equivalent adapter for a frozen runtime."""

    def __init__(self, runtime: PairwiseRuntime):
        if not isinstance(runtime, PairwiseRuntime):
            raise TypeError("runtime must be a PairwiseRuntime")
        self.runtime = runtime

    def _reference_components(
        self, raw_views: Sequence[np.ndarray]
    ) -> tuple[dict[str, np.ndarray], np.ndarray, np.ndarray]:
        model_views, values, _ = self.runtime._model_inputs(raw_views)
        components, probability = demand_driven_open_set_components(
            self.runtime.model,
            model_views,
            self.runtime.distance_model,
            values,
        )
        for index, (view_model, view) in enumerate(
            zip(self.runtime.view_knn_models, model_views)
        ):
            components[f"knn_view_{index}"] = view_model.score(view)
        return components, probability, values

    def _add_learned_components(
        self,
        components: dict[str, np.ndarray],
        probability: np.ndarray,
        values: np.ndarray,
    ) -> None:
        required = set(self.runtime.learned_weights)
        unsupported = required - set(components) - OPTIONAL_COMPONENTS
        if unsupported:
            raise ValueError(
                "optimized runtime cannot produce learned components: "
                + ", ".join(sorted(unsupported))
            )
        if "knn_distance" in required:
            components["knn_distance"] = self.runtime.knn_model.score(values)
        if "class_knn_distance" in required:
            prediction = probability.argmax(axis=1)
            components["class_knn_distance"] = self.runtime.class_knn_model.score(
                values, prediction
            )
        if "lof_density" in required:
            components["lof_density"] = self.runtime.lof_model.score(values)

    def predict(self, raw_views: Sequence[np.ndarray]) -> dict[str, np.ndarray]:
        components, probability, values = self._reference_components(raw_views)
        prediction = probability.argmax(axis=1)
        view_names = sorted(
            (name for name in components if name.startswith("knn_view_")),
            key=lambda name: int(name.rsplit("_", 1)[1]),
        )
        reference_names = (*REFERENCE_COMPONENTS, *view_names)
        tail = {
            name: stable_empirical_tail_scores(
                self.runtime.tail_calibrator.reference[name],
                components[name],
                self.runtime._tail_cluster_starts[name],
            )
            for name in reference_names
        }
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
        if self.runtime.selected_risk == "cauchy_modality_support_union":
            risk = reference_risk
        else:
            self._add_learned_components(components, probability, values)
            learned_components = {
                name: components[name] for name in self.runtime.learned_weights
            }
            normalized = self.runtime.normalizer.transform(learned_components)
            raw_learned = weighted_risk(normalized, self.runtime.learned_weights)
            learned_tail = stable_empirical_tail_scores(
                self.runtime._validation_raw_learned_sorted,
                raw_learned,
                self.runtime._learned_tail_cluster_starts,
            )
            risk = (
                (1.0 - self.runtime.selected_alpha) * reference_risk
                + self.runtime.selected_alpha * learned_tail
            )
        return {
            "prediction": np.asarray(prediction, dtype=np.int64),
            "probability": np.asarray(probability, dtype=np.float64),
            "risk": np.asarray(risk, dtype=np.float64),
        }

    def evidence(self) -> dict[str, object]:
        evidence = dict(self.runtime.evidence())
        evidence.update(
            {
                "optimized_runtime_schema_version": (
                    "strict_v4_pairwise_demand_driven_runtime_v1"
                ),
                "optimization_mode": "selected_risk_demand_driven_components",
                "numerical_equivalence_required": True,
                "numerical_equivalence_absolute_tolerance": 1e-12,
            }
        )
        return evidence
