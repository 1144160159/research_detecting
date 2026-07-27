from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Sequence

import numpy as np

from caeos.hybrid_open_set import (
    bonferroni_union_risk,
    cauchy_combined_risk,
    jensen_shannon_divergence,
    normalized_entropy,
    weighted_risk,
)
from caeos.mdr_runtime import MDRRuntime
from caeos.pairwise_runtime import stable_empirical_tail_scores
from train_hybrid_open_set import missing_aware_cauchy_risk


def pairwise_predict_with_reused_evidence(
    runtime: Any, raw_views: Sequence[np.ndarray]
) -> tuple[Dict[str, np.ndarray], Dict[str, np.ndarray], Dict[str, np.ndarray]]:
    """Reproduce PairwiseRuntime.predict while retaining its first evidence pass."""
    model_views, values, _ = runtime._model_inputs(raw_views)
    global_values = runtime.model._global_values(model_views)
    evidence = runtime.model.predict_with_evidence(model_views)
    probability = np.asarray(
        evidence["final_probability"], dtype=np.float64
    )
    sorted_probability = np.sort(probability, axis=1)
    rf_probability = runtime.model.random_forest.predict_proba(global_values)
    et_probability = runtime.model.extra_trees.predict_proba(global_values)
    components: Dict[str, np.ndarray] = {
        "uncertainty": normalized_entropy(probability),
        "inverse_belief": 1.0 - probability.max(axis=1),
        "inverse_margin": (
            1.0
            - (sorted_probability[:, -1] - sorted_probability[:, -2])
        ),
        "conflict": np.asarray(
            evidence["global_conflict"], dtype=np.float64
        ),
        "tree_disagreement": jensen_shannon_divergence(
            rf_probability, et_probability
        ),
        "distance": runtime.distance_model.score(values),
        "knn_distance": runtime.knn_model.score(values),
    }
    view_names = []
    for index, (view_model, view) in enumerate(
        zip(runtime.view_knn_models, model_views)
    ):
        name = f"knn_view_{index}"
        view_names.append(name)
        components[name] = view_model.score(view)
    prediction = probability.argmax(axis=1)
    components["class_knn_distance"] = runtime.class_knn_model.score(
        values, prediction
    )
    components["lof_density"] = runtime.lof_model.score(values)
    tail = {
        name: stable_empirical_tail_scores(
            runtime.tail_calibrator.reference[name],
            component,
            runtime._tail_cluster_starts[name],
        )
        for name, component in components.items()
    }
    normalized = runtime.normalizer.transform(components)
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
    if runtime.selected_risk == "cauchy_modality_support_union":
        risk = reference_risk
    elif runtime.selected_risk == "pseudo_unknown_learned_blend":
        raw_learned = weighted_risk(normalized, runtime.learned_weights)
        learned_tail = stable_empirical_tail_scores(
            runtime._validation_raw_learned_sorted,
            raw_learned,
            runtime._learned_tail_cluster_starts,
        )
        risk = (
            (1.0 - runtime.selected_alpha) * reference_risk
            + runtime.selected_alpha * learned_tail
        )
    else:
        raise ValueError(
            f"unsupported frozen pairwise risk: {runtime.selected_risk}"
        )
    output = {
        "prediction": np.asarray(prediction, dtype=np.int64),
        "probability": probability,
        "risk": np.asarray(risk, dtype=np.float64),
    }
    retained_evidence = {
        "final_probability": probability,
        "local_conflict": np.asarray(
            evidence["local_conflict"], dtype=np.float64
        ),
    }
    return output, components, retained_evidence


@dataclass
class MDREvidenceReuseRuntime:
    """Exact MDR deployment adapter that eliminates repeated model passes."""

    base_runtime: MDRRuntime

    @property
    def clean_runtime(self):
        return self.base_runtime.clean_runtime

    @property
    def robust_runtime(self):
        return self.base_runtime.robust_runtime

    def predict(
        self, raw_views: Sequence[np.ndarray]
    ) -> Dict[str, np.ndarray]:
        views = [np.asarray(view) for view in raw_views]
        clean, _, clean_evidence = pairwise_predict_with_reused_evidence(
            self.clean_runtime, views
        )
        (
            robust,
            robust_components,
            robust_evidence,
        ) = pairwise_predict_with_reused_evidence(
            self.robust_runtime, views
        )
        missing = self.base_runtime.missing_mask(views)
        view_names = sorted(
            (
                name
                for name in robust_components
                if name.startswith("knn_view_")
            ),
            key=lambda name: int(name.rsplit("_", 1)[1]),
        )
        if len(view_names) != missing.shape[1]:
            raise ValueError("MDR view-risk count differs from missingness mask")
        view_risks = np.stack(
            [
                stable_empirical_tail_scores(
                    self.robust_runtime.tail_calibrator.reference[name],
                    robust_components[name],
                    self.robust_runtime._tail_cluster_starts[name],
                )
                for name in view_names
            ],
            axis=1,
        )
        missing_risk = missing_aware_cauchy_risk(
            view_risks, missing, robust["risk"]
        )
        fused = self.base_runtime.health_calibration.apply(
            clean_evidence,
            robust_evidence,
            clean["risk"],
            robust["risk"],
            missing_risk,
            missing.any(axis=1),
        )
        probability = np.where(
            fused["active"][:, None],
            robust["probability"],
            clean["probability"],
        )
        return {
            **fused,
            "probability": probability,
            "clean_probability": clean["probability"],
            "robust_probability": robust["probability"],
            "clean_risk": clean["risk"],
            "robust_risk": robust["risk"],
            "missing_risk": missing_risk,
            "view_missing": missing,
            "threshold": np.full(
                len(probability),
                self.base_runtime.clean_threshold,
                dtype=np.float64,
            ),
        }

    def corrupt(
        self,
        raw_views: Sequence[np.ndarray],
        *,
        family: str,
        modality: int,
        severity: float,
        seed: int,
    ):
        return self.base_runtime.corrupt(
            raw_views,
            family=family,
            modality=modality,
            severity=severity,
            seed=seed,
        )

    def evidence(self) -> Dict[str, Any]:
        value = dict(self.base_runtime.evidence())
        value["deployment_optimization"] = {
            "schema_version": "mdr_evidence_reuse_v1",
            "effect_semantics_changed": False,
            "clean_model_evidence_passes_per_batch": 1,
            "robust_model_evidence_passes_per_batch": 1,
            "original_clean_model_evidence_passes_per_batch": 2,
            "original_robust_model_evidence_passes_per_batch": 3,
            "unknown_or_test_labels_used": False,
        }
        return value
