from __future__ import annotations

import numpy as np


PAPER_URL = "https://openaccess.thecvf.com/content/ICCV2023/papers/Park_Nearest_Neighbor_Guidance_for_Out-of-Distribution_Detection_ICCV_2023_paper.pdf"
OFFICIAL_CODE_URL = "https://github.com/roomo7time/nnguide"
OFFICIAL_CODE_COMMIT = "c123cac961b17a6c4f11adefd9ad861298be1469"


def _features(values: np.ndarray, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 2 or not array.shape[0] or not array.shape[1]:
        raise ValueError("NNGuide %s must be a non-empty matrix" % name)
    if not np.isfinite(array).all():
        raise ValueError("NNGuide %s must be finite" % name)
    return array


def _logsumexp(logits: np.ndarray) -> np.ndarray:
    maximum = logits.max(axis=1)
    return maximum + np.log(np.exp(logits - maximum[:, None]).sum(axis=1))


def _normalize(features: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(features, axis=1, keepdims=True)
    return features / np.maximum(norms, 1e-12)


class NNGuideCalibrator:
    """Official NNGuide with Energy confidence and an ID training bank."""

    def __init__(
        self,
        bank_ratio: float = 0.01,
        neighbor_count: int = 10,
        bank_seed: int = 0,
    ) -> None:
        self.bank_ratio = float(bank_ratio)
        self.neighbor_count = int(neighbor_count)
        self.bank_seed = int(bank_seed)
        if not 0.0 < self.bank_ratio <= 1.0:
            raise ValueError("NNGuide bank ratio must be in (0, 1]")
        if self.neighbor_count <= 0:
            raise ValueError("NNGuide neighbor count must be positive")
        self.scaled_bank: np.ndarray | None = None
        self.bank_indices: np.ndarray | None = None
        self.training_count: int | None = None
        self.bank_size_from_ratio: int | None = None
        self.minimum_bank_adapter_used: bool | None = None

    @staticmethod
    def _validate_logits(logits: np.ndarray, rows: int) -> np.ndarray:
        array = np.asarray(logits, dtype=np.float64)
        if array.ndim != 2 or array.shape[0] != rows or array.shape[1] < 2:
            raise ValueError("NNGuide logits must match feature rows and have at least two classes")
        if not np.isfinite(array).all():
            raise ValueError("NNGuide logits must be finite")
        return array

    def fit(self, training_features: np.ndarray, training_logits: np.ndarray) -> None:
        features = _features(training_features, "training features")
        logits = self._validate_logits(training_logits, len(features))
        ratio_size = int(len(features) * self.bank_ratio)
        bank_size = max(self.neighbor_count, ratio_size)
        if bank_size > len(features):
            raise ValueError("NNGuide training set is smaller than k")
        indices = np.arange(len(features))
        np.random.RandomState(self.bank_seed).shuffle(indices)
        indices = indices[:bank_size]
        normalized = _normalize(features[indices])
        confidence = _logsumexp(logits[indices])
        self.scaled_bank = normalized * confidence[:, None]
        self.bank_indices = indices.astype(np.int64, copy=False)
        self.training_count = int(len(features))
        self.bank_size_from_ratio = ratio_size
        self.minimum_bank_adapter_used = ratio_size < self.neighbor_count

    def _require_fit(self) -> np.ndarray:
        if self.scaled_bank is None or self.bank_indices is None:
            raise RuntimeError("NNGuide calibrator has not been fitted")
        return self.scaled_bank

    def guidance(self, features: np.ndarray) -> np.ndarray:
        bank = self._require_fit()
        query = _normalize(_features(features, "inference features"))
        similarity = query @ bank.T
        topk = np.partition(
            similarity, similarity.shape[1] - self.neighbor_count, axis=1
        )[:, -self.neighbor_count :]
        return topk.mean(axis=1)

    def evaluate(self, features: np.ndarray, logits: np.ndarray) -> dict[str, np.ndarray]:
        values = _features(features, "inference features")
        raw_logits = self._validate_logits(logits, len(values))
        confidence = _logsumexp(raw_logits)
        guidance = self.guidance(values)
        guided_confidence = confidence * guidance
        return {
            "prediction": raw_logits.argmax(axis=1).astype(np.int64, copy=False),
            "risk": -guided_confidence,
            "base_confidence": confidence,
            "guidance": guidance,
            "guided_confidence": guided_confidence,
        }

    def evidence(self) -> dict[str, object]:
        bank = self._require_fit()
        if (
            self.training_count is None
            or self.bank_size_from_ratio is None
            or self.minimum_bank_adapter_used is None
        ):
            raise RuntimeError("NNGuide fit evidence is incomplete")
        return {
            "method": "NNGuide-Energy",
            "paper": PAPER_URL,
            "official_code": OFFICIAL_CODE_URL,
            "official_code_commit": OFFICIAL_CODE_COMMIT,
            "formula": "S_NNGuide(x)=S_Energy(x)*mean_topk(S_i*cos(z_i,z))",
            "fit_split": "known_training_only",
            "training_embedding_count": self.training_count,
            "bank_ratio": self.bank_ratio,
            "bank_seed": self.bank_seed,
            "bank_size_from_official_ratio": self.bank_size_from_ratio,
            "bank_size_used": int(len(bank)),
            "neighbor_count": self.neighbor_count,
            "base_confidence": "logsumexp_logits_temperature_1",
            "feature_normalization": "l2_per_sample_eps_1e-12",
            "prediction_source": "unmodified_frozen_classifier",
            "risk_orientation": "negative_guided_confidence_larger_is_more_unknown",
            "unknown_or_test_labels_used": False,
            "auxiliary_ood_used": False,
            "adaptation": {
                "minimum_bank_size": "max(k,floor(alpha*N))",
                "minimum_bank_adapter_used": self.minimum_bank_adapter_used,
                "reason": "top-k is undefined when floor(alpha*N) is below k",
            },
        }
