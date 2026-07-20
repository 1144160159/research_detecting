from __future__ import annotations

from typing import Any

import numpy as np
import torch


PAPER_URL = "https://arxiv.org/abs/2503.08023"
OFFICIAL_CODE_URL = "https://github.com/sudarshanregmi/AdaSCALE"
OFFICIAL_CODE_COMMIT = "ed5f639e10520a04f6a83f30a32c060d6f012ea8"
DEFAULT_P_MIN = 60.0
DEFAULT_P_MAX = 85.0
DEFAULT_K1_PERCENT = 1.0
DEFAULT_K2_PERCENT = 5.0
DEFAULT_LAMBDA = 10.0
DEFAULT_PERTURB_FRACTION = 0.05
DEFAULT_EPSILON = 0.5
DEFAULT_TEMPERATURE = 1.0


def _finite_scalar(name: str, value: float) -> float:
    result = float(value)
    if not np.isfinite(result):
        raise ValueError("%s must be finite" % name)
    return result


def validate_parameters(
    p_min: float,
    p_max: float,
    k1_percent: float,
    k2_percent: float,
    lmbda: float,
    perturb_fraction: float,
    epsilon: float,
    temperature: float,
) -> None:
    p_min = _finite_scalar("p_min", p_min)
    p_max = _finite_scalar("p_max", p_max)
    if not 0.0 < p_min < p_max < 100.0:
        raise ValueError("AdaSCALE percentiles must satisfy 0 < p_min < p_max < 100")
    for name, value in (("k1_percent", k1_percent), ("k2_percent", k2_percent)):
        value = _finite_scalar(name, value)
        if not 0.0 < value <= 100.0:
            raise ValueError("%s must be in (0, 100]" % name)
    if _finite_scalar("lambda", lmbda) < 0.0:
        raise ValueError("AdaSCALE lambda must be non-negative")
    perturb_fraction = _finite_scalar("perturb_fraction", perturb_fraction)
    if not 0.0 < perturb_fraction <= 1.0:
        raise ValueError("AdaSCALE perturb_fraction must be in (0, 1]")
    if _finite_scalar("epsilon", epsilon) < 0.0:
        raise ValueError("AdaSCALE epsilon must be non-negative")
    if _finite_scalar("temperature", temperature) <= 0.0:
        raise ValueError("AdaSCALE temperature must be positive")


def percent_to_count(feature_count: int, percent: float) -> int:
    if feature_count <= 0:
        raise ValueError("feature_count must be positive")
    value = _finite_scalar("percent", percent)
    if not 0.0 < value <= 100.0:
        raise ValueError("percent must be in (0, 100]")
    # The official implementation floors the count. The lower bound is the
    # preregistered tabular adaptation for low-dimensional hidden layers.
    return min(feature_count, max(1, int(feature_count * value / 100.0)))


def _matrix(name: str, values: np.ndarray) -> np.ndarray:
    result = np.asarray(values, dtype=np.float64)
    if result.ndim != 2 or result.shape[0] == 0 or result.shape[1] == 0:
        raise ValueError("%s must be a non-empty matrix" % name)
    if not np.isfinite(result).all():
        raise ValueError("%s must be finite" % name)
    return result


def q_prime_statistic(
    feature: np.ndarray,
    feature_perturbed: np.ndarray,
    *,
    k1_percent: float = DEFAULT_K1_PERCENT,
    k2_percent: float = DEFAULT_K2_PERCENT,
    lmbda: float = DEFAULT_LAMBDA,
) -> tuple[np.ndarray, int, int]:
    """Compute paper Algorithm 1's Q' = lambda * Q + C_o.

    k1 selects activation shifts and k2 selects perturbed activations. This
    follows the paper and official inference function. The official repository's
    ECDF setup function reverses these two counts despite its erratum notice.
    """

    original = _matrix("feature", feature)
    perturbed = _matrix("feature_perturbed", feature_perturbed)
    if original.shape != perturbed.shape:
        raise ValueError("original and perturbed features must have equal shape")
    lmbda = _finite_scalar("lambda", lmbda)
    if lmbda < 0.0:
        raise ValueError("AdaSCALE lambda must be non-negative")
    k1 = percent_to_count(original.shape[1], k1_percent)
    k2 = percent_to_count(original.shape[1], k2_percent)

    ranking_feature = np.maximum(original, 0.0)
    shift = np.abs(perturbed - original)
    k1_indices = np.argpartition(
        ranking_feature, original.shape[1] - k1, axis=1
    )[:, -k1:]
    k2_indices = np.argpartition(
        ranking_feature, original.shape[1] - k2, axis=1
    )[:, -k2:]
    q = np.take_along_axis(shift, k1_indices, axis=1).sum(axis=1)
    correction = np.take_along_axis(
        np.maximum(perturbed, 0.0), k2_indices, axis=1
    ).sum(axis=1)
    return lmbda * q + correction, k1, k2


def empirical_cdf(sorted_reference: np.ndarray, values: np.ndarray) -> np.ndarray:
    reference = np.asarray(sorted_reference, dtype=np.float64)
    query = np.asarray(values, dtype=np.float64)
    if reference.ndim != 1 or reference.size == 0:
        raise ValueError("ECDF reference must be a non-empty vector")
    if query.ndim != 1:
        raise ValueError("ECDF queries must be a vector")
    if not (np.isfinite(reference).all() and np.isfinite(query).all()):
        raise ValueError("ECDF values must be finite")
    if np.any(reference[:-1] > reference[1:]):
        raise ValueError("ECDF reference must be sorted")
    return np.searchsorted(reference, query, side="right") / float(len(reference))


def adaptive_percentiles(
    sorted_reference: np.ndarray,
    q_prime: np.ndarray,
    p_min: float = DEFAULT_P_MIN,
    p_max: float = DEFAULT_P_MAX,
) -> np.ndarray:
    p_min = _finite_scalar("p_min", p_min)
    p_max = _finite_scalar("p_max", p_max)
    if not 0.0 < p_min < p_max < 100.0:
        raise ValueError("AdaSCALE percentiles must satisfy 0 < p_min < p_max < 100")
    return p_min + (1.0 - empirical_cdf(sorted_reference, q_prime)) * (
        p_max - p_min
    )


def adascale_factors(
    feature: np.ndarray, percentiles: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    original = _matrix("feature", feature)
    p = np.asarray(percentiles, dtype=np.float64)
    if p.shape != (len(original),) or not np.isfinite(p).all():
        raise ValueError("percentiles must be one finite value per feature row")
    if np.any(p <= 0.0) or np.any(p >= 100.0):
        raise ValueError("percentiles must be in (0, 100)")

    rectified = np.maximum(original, 0.0)
    feature_count = rectified.shape[1]
    retained_counts = feature_count - np.round(
        feature_count * p / 100.0
    ).astype(np.int64)
    retained_counts = np.clip(retained_counts, 1, feature_count)
    descending = np.sort(rectified, axis=1)[:, ::-1]
    cumulative = np.cumsum(descending, axis=1)
    retained_mass = cumulative[np.arange(len(original)), retained_counts - 1]
    total_mass = rectified.sum(axis=1)
    ratio = np.zeros(len(original), dtype=np.float64)
    positive = total_mass > 0.0
    if np.any(positive & (retained_mass <= 0.0)):
        raise FloatingPointError("AdaSCALE retained activation mass is not positive")
    ratio[positive] = total_mass[positive] / retained_mass[positive]
    if np.any(ratio > np.log(np.finfo(np.float64).max)):
        raise OverflowError("AdaSCALE exponent exceeds float64 range")
    factors = np.ones(len(original), dtype=np.float64)
    factors[positive] = np.exp(ratio[positive])
    return factors, retained_counts


def _logsumexp(logits: np.ndarray, temperature: float) -> np.ndarray:
    normalized = logits / temperature
    maximum = normalized.max(axis=1)
    return temperature * (
        maximum + np.log(np.exp(normalized - maximum[:, None]).sum(axis=1))
    )


class AdaSCALECalibrator:
    def __init__(
        self,
        p_min: float = DEFAULT_P_MIN,
        p_max: float = DEFAULT_P_MAX,
        k1_percent: float = DEFAULT_K1_PERCENT,
        k2_percent: float = DEFAULT_K2_PERCENT,
        lmbda: float = DEFAULT_LAMBDA,
        perturb_fraction: float = DEFAULT_PERTURB_FRACTION,
        epsilon: float = DEFAULT_EPSILON,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> None:
        validate_parameters(
            p_min, p_max, k1_percent, k2_percent, lmbda,
            perturb_fraction, epsilon, temperature,
        )
        self.p_min = float(p_min)
        self.p_max = float(p_max)
        self.k1_percent = float(k1_percent)
        self.k2_percent = float(k2_percent)
        self.lmbda = float(lmbda)
        self.perturb_fraction = float(perturb_fraction)
        self.epsilon = float(epsilon)
        self.temperature = float(temperature)
        self.sorted_reference: np.ndarray | None = None
        self.classifier_weight: np.ndarray | None = None
        self.classifier_bias: np.ndarray | None = None
        self.k1_count: int | None = None
        self.k2_count: int | None = None

    def fit(
        self,
        validation_feature: np.ndarray,
        validation_feature_perturbed: np.ndarray,
        classifier_weight: np.ndarray,
        classifier_bias: np.ndarray | None,
    ) -> None:
        q_prime, k1, k2 = q_prime_statistic(
            validation_feature,
            validation_feature_perturbed,
            k1_percent=self.k1_percent,
            k2_percent=self.k2_percent,
            lmbda=self.lmbda,
        )
        weight = np.asarray(classifier_weight, dtype=np.float64)
        if weight.ndim != 2 or weight.shape[1] != validation_feature.shape[1]:
            raise ValueError("classifier weight must have shape [classes, features]")
        if classifier_bias is None:
            bias = np.zeros(weight.shape[0], dtype=np.float64)
        else:
            bias = np.asarray(classifier_bias, dtype=np.float64)
        if bias.shape != (weight.shape[0],):
            raise ValueError("classifier bias must have shape [classes]")
        if not (np.isfinite(weight).all() and np.isfinite(bias).all()):
            raise ValueError("classifier parameters must be finite")
        self.sorted_reference = np.sort(q_prime)
        self.classifier_weight = weight.copy()
        self.classifier_bias = bias.copy()
        self.k1_count = k1
        self.k2_count = k2

    def _require_fit(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        if (
            self.sorted_reference is None
            or self.classifier_weight is None
            or self.classifier_bias is None
        ):
            raise RuntimeError("AdaSCALE calibrator has not been fitted")
        return self.sorted_reference, self.classifier_weight, self.classifier_bias

    def evaluate(
        self, feature: np.ndarray, feature_perturbed: np.ndarray
    ) -> dict[str, np.ndarray]:
        reference, weight, bias = self._require_fit()
        q_prime, k1, k2 = q_prime_statistic(
            feature,
            feature_perturbed,
            k1_percent=self.k1_percent,
            k2_percent=self.k2_percent,
            lmbda=self.lmbda,
        )
        if k1 != self.k1_count or k2 != self.k2_count:
            raise ValueError("inference feature dimension differs from calibration")
        percentiles = adaptive_percentiles(reference, q_prime, self.p_min, self.p_max)
        factors, retained_counts = adascale_factors(feature, percentiles)
        # Official AdaSCALE-A estimates the factor from ReLU(feature), then
        # applies it to the original feature supplied to the linear classifier.
        logits = np.asarray(feature, dtype=np.float64) * factors[:, None]
        logits = logits @ weight.T + bias
        return {
            "q_prime": q_prime,
            "percentile": percentiles,
            "factor": factors,
            "retained_count": retained_counts,
            "logits": logits,
            "prediction": logits.argmax(axis=1),
            "risk": -_logsumexp(logits, self.temperature),
        }

    def evidence(self) -> dict[str, object]:
        reference, weight, bias = self._require_fit()
        return {
            "method": "AdaSCALE-A",
            "paper": PAPER_URL,
            "official_code": OFFICIAL_CODE_URL,
            "official_code_commit": OFFICIAL_CODE_COMMIT,
            "protocol_class": "paper_formula_frozen_low_dimensional_tabular_adapter",
            "parameters": {
                "p_min": self.p_min,
                "p_max": self.p_max,
                "k1_percent": self.k1_percent,
                "k2_percent": self.k2_percent,
                "lambda": self.lmbda,
                "perturb_fraction": self.perturb_fraction,
                "epsilon": self.epsilon,
                "temperature": self.temperature,
            },
            "parameter_source": (
                "official README fixed defaults; p_max=85 from official default "
                "configuration and paper sensitivity setting; no OOD sweep"
            ),
            "fit_split": "known_only_validation_ecdf",
            "validation_embedding_count": int(len(reference)),
            "feature_dimension": int(weight.shape[1]),
            "class_count": int(weight.shape[0]),
            "classifier_bias_present": bool(np.any(bias != 0.0)),
            "selected_k1_count": self.k1_count,
            "selected_k2_count": self.k2_count,
            "adaptation": {
                "gelu_policy": "relu_for_ranking_and_scale_ratio_then_scale_raw_embedding",
                "minimum_top_k_for_low_dimensional_features": 1,
                "input_coordinates": "already_standardized_tabular_features",
                "multiview_perturbation": "global_lowest_absolute_gradient_over_concatenated_views",
                "zero_activation_mass_policy": "identity_scale",
                "risk_orientation": "negative_energy_larger_is_more_unknown",
            },
            "formula_resolution": (
                "paper Algorithm 1 and official inference use k1 for Q shift and "
                "k2 for C_o; official ECDF setup source reverses them"
            ),
            "unknown_or_test_labels_used": False,
        }


def adascale_feature_batch(
    model: torch.nn.Module,
    views: list[torch.Tensor],
    quality: torch.Tensor,
    perturb_fraction: float = DEFAULT_PERTURB_FRACTION,
    epsilon: float = DEFAULT_EPSILON,
) -> tuple[np.ndarray, np.ndarray]:
    if not 0.0 < float(perturb_fraction) <= 1.0:
        raise ValueError("perturb_fraction must be in (0, 1]")
    if not np.isfinite(epsilon) or epsilon < 0.0:
        raise ValueError("epsilon must be finite and non-negative")
    model.eval()
    inputs = [value.detach().clone().requires_grad_(True) for value in views]
    result = model(inputs, quality)
    logits = result["logits"]
    feature = result["embedding"]
    prediction = logits.detach().argmax(dim=1)
    selected = logits.gather(1, prediction[:, None]).sum()
    gradients = torch.autograd.grad(selected, inputs, only_inputs=True)

    flat_gradient = torch.cat([gradient.detach().abs() for gradient in gradients], dim=1)
    total_features = flat_gradient.shape[1]
    perturb_count = min(
        total_features,
        max(1, int(total_features * float(perturb_fraction))),
    )
    indices = torch.topk(
        flat_gradient, perturb_count, dim=1, largest=False
    ).indices
    flat_mask = torch.zeros_like(flat_gradient)
    flat_mask.scatter_(1, indices, 1.0)
    masks = torch.split(flat_mask, [value.shape[1] for value in inputs], dim=1)
    perturbed = [
        value.detach() + float(epsilon) * gradient.detach().sign() * mask
        for value, gradient, mask in zip(inputs, gradients, masks)
    ]
    with torch.no_grad():
        feature_perturbed = model(perturbed, quality)["embedding"]
    return feature.detach().cpu().numpy(), feature_perturbed.cpu().numpy()


def collect_adascale_features(
    model: torch.nn.Module,
    loader: Any,
    device: torch.device,
    perturb_fraction: float = DEFAULT_PERTURB_FRACTION,
    epsilon: float = DEFAULT_EPSILON,
) -> dict[str, np.ndarray]:
    output: dict[str, list[np.ndarray]] = {
        "labels": [],
        "unknown": [],
        "feature": [],
        "feature_perturbed": [],
    }
    for batch in loader:
        views = [value.to(device, non_blocking=True) for value in batch["views"]]
        quality = batch["quality"].to(device, non_blocking=True)
        feature, feature_perturbed = adascale_feature_batch(
            model,
            views,
            quality,
            perturb_fraction=perturb_fraction,
            epsilon=epsilon,
        )
        output["labels"].append(batch["label"].numpy())
        output["unknown"].append(batch["is_unknown"].numpy())
        output["feature"].append(feature)
        output["feature_perturbed"].append(feature_perturbed)
    return {name: np.concatenate(parts, axis=0) for name, parts in output.items()}
