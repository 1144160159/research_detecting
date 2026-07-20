from __future__ import annotations

import numpy as np


PAPER_URL = "https://openreview.net/forum?id=dm8e7gsH0d"
OFFICIAL_CODE_URL = "https://github.com/Qinyu-Allen-Zhao/OptFSOOD"
OFFICIAL_CODE_COMMIT = "c09a85e1f15de5a1f45c89419be6a5fff03f88c5"


class OptFSCalibrator:
    """Official fixed-weight OptFS with vanilla confidence.

    OptFS learns a piecewise-constant shaping function from ID training
    features and the frozen classifier only. Predictions remain those of the
    unshaped classifier; negative shaped confidence is returned as OOD risk.
    """

    def __init__(
        self,
        quantile_epsilon: float = 1e-3,
        bin_count: int = 100,
        theta_norm: float = 1000.0,
    ) -> None:
        self.quantile_epsilon = float(quantile_epsilon)
        self.bin_count = int(bin_count)
        self.theta_norm = float(theta_norm)
        if not 0.0 < self.quantile_epsilon < 0.5:
            raise ValueError("OptFS quantile epsilon must be in (0, 0.5)")
        if self.bin_count <= 0:
            raise ValueError("OptFS bin count must be positive")
        if not np.isfinite(self.theta_norm) or self.theta_norm <= 0.0:
            raise ValueError("OptFS theta norm must be finite and positive")
        self.left_boundary: np.ndarray | None = None
        self.width: float | None = None
        self.theta: np.ndarray | None = None
        self.classifier_weight: np.ndarray | None = None
        self.classifier_bias: np.ndarray | None = None
        self.training_count: int | None = None

    @staticmethod
    def _features(values: np.ndarray) -> np.ndarray:
        array = np.asarray(values, dtype=np.float64)
        if array.ndim != 2 or not array.shape[0] or not array.shape[1]:
            raise ValueError("OptFS features must be a non-empty matrix")
        if not np.isfinite(array).all():
            raise ValueError("OptFS features must be finite")
        return array

    @staticmethod
    def _classifier(
        weight: np.ndarray, bias: np.ndarray | None, feature_count: int
    ) -> tuple[np.ndarray, np.ndarray]:
        w = np.asarray(weight, dtype=np.float64)
        if w.ndim != 2 or w.shape[0] < 2 or w.shape[1] != feature_count:
            raise ValueError("OptFS classifier weight must have shape [classes, features]")
        b = np.zeros(w.shape[0], dtype=np.float64) if bias is None else np.asarray(bias, dtype=np.float64)
        if b.shape != (w.shape[0],):
            raise ValueError("OptFS classifier bias must have shape [classes]")
        if not np.isfinite(w).all() or not np.isfinite(b).all():
            raise ValueError("OptFS classifier parameters must be finite")
        return w.copy(), b.copy()

    def fit(
        self,
        training_features: np.ndarray,
        training_logits: np.ndarray,
        classifier_weight: np.ndarray,
        classifier_bias: np.ndarray | None = None,
    ) -> None:
        feature = self._features(training_features)
        logits = np.asarray(training_logits, dtype=np.float64)
        weight, bias = self._classifier(classifier_weight, classifier_bias, feature.shape[1])
        if logits.shape != (len(feature), weight.shape[0]) or not np.isfinite(logits).all():
            raise ValueError("OptFS training logits must match features and classes")
        prediction = logits.argmax(axis=1)
        left = float(np.quantile(feature, self.quantile_epsilon))
        right = float(np.quantile(feature, 1.0 - self.quantile_epsilon))
        width = (right - left) / self.bin_count
        if not np.isfinite(width) or width <= 0.0:
            raise ValueError("OptFS training feature quantile range is degenerate")

        # Equivalent to the official np.arange(left, right, width), while
        # deterministically preserving the intended 100-bin configuration.
        boundaries = left + width * np.arange(self.bin_count, dtype=np.float64)
        contribution = weight[prediction] * feature
        lc_fv = np.empty(self.bin_count, dtype=np.float64)
        for index, boundary in enumerate(boundaries):
            mask = (feature >= boundary) & (feature < boundary + width)
            lc_fv[index] = np.mean(np.sum(mask * contribution, axis=1))
        norm = float(np.linalg.norm(lc_fv, ord=2))
        if not np.isfinite(norm) or norm <= 0.0:
            raise ValueError("OptFS logit-contribution vector has zero norm")

        self.left_boundary = boundaries
        self.width = width
        self.theta = lc_fv / norm * self.theta_norm
        self.classifier_weight = weight
        self.classifier_bias = bias
        self.training_count = int(len(feature))

    def _require_fit(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
        if (
            self.classifier_weight is None
            or self.classifier_bias is None
            or self.left_boundary is None
            or self.width is None
            or self.theta is None
        ):
            raise RuntimeError("OptFS calibrator has not been fitted")
        return self.classifier_weight, self.classifier_bias, self.left_boundary, self.width

    def transform(self, features: np.ndarray) -> np.ndarray:
        weight, _, boundaries, width = self._require_fit()
        values = self._features(features)
        if values.shape[1] != weight.shape[1]:
            raise ValueError("OptFS inference feature dimension differs from classifier")
        shaped = np.zeros_like(values)
        assert self.theta is not None
        for index, boundary in enumerate(boundaries):
            mask = (values >= boundary) & (values < boundary + width)
            shaped += mask * values * self.theta[index]
        return shaped

    def evaluate(self, features: np.ndarray, logits: np.ndarray) -> dict[str, np.ndarray]:
        weight, _, _, _ = self._require_fit()
        values = self._features(features)
        raw_logits = np.asarray(logits, dtype=np.float64)
        if raw_logits.shape != (len(values), weight.shape[0]):
            raise ValueError("OptFS inference logits must match features and classes")
        prediction = raw_logits.argmax(axis=1)
        shaped = self.transform(values)
        confidence = np.sum(weight[prediction] * shaped, axis=1)
        return {
            "prediction": prediction.astype(np.int64, copy=False),
            "risk": -confidence,
            "confidence": confidence,
            "shaped_feature": shaped,
        }

    def evidence(self) -> dict[str, object]:
        weight, bias, boundaries, width = self._require_fit()
        if self.theta is None or self.training_count is None:
            raise RuntimeError("OptFS fit evidence is incomplete")
        return {
            "method": "OptFS Ours (V)",
            "paper": PAPER_URL,
            "official_code": OFFICIAL_CODE_URL,
            "official_code_commit": OFFICIAL_CODE_COMMIT,
            "formula": "theta=1000*I(z)/||I(z)||_2; vanilla confidence=sum(w_pred*h_shaped)",
            "fit_split": "known_training_only",
            "training_embedding_count": self.training_count,
            "quantile_epsilon": self.quantile_epsilon,
            "bin_count": self.bin_count,
            "theta_target_norm": self.theta_norm,
            "theta_observed_norm": float(np.linalg.norm(self.theta, ord=2)),
            "search_range": [float(boundaries[0]), float(boundaries[-1] + width)],
            "class_count": int(weight.shape[0]),
            "feature_dimension": int(weight.shape[1]),
            "classifier_bias_present": bool(np.any(bias != 0.0)),
            "score_variant": "official_default_vanilla",
            "prediction_source": "unshaped_frozen_classifier",
            "risk_orientation": "negative_vanilla_confidence_larger_is_more_unknown",
            "unknown_or_test_labels_used": False,
            "auxiliary_ood_used": False,
            "adaptation": {
                "signed_gelu_features": "native_global_value_bins_no_rectification",
                "boundary_construction": "exactly_100_equal_width_bins_with_official_quantiles",
                "official_10000_sample_diagnostic": "omitted_non_algorithmic_print_only_check",
            },
        }
