from __future__ import annotations

import numpy as np
import pytest

from caeos.pseudo_unknown_gated_continuous import PUG_RISK_NAME
from caeos.selected_system_runtime import (
    SelectedSystemRuntime,
    infer_runtime_algorithm,
    validate_prediction_output,
)


class Runtime:
    def __init__(self, schema: str, algorithm: str | None = None) -> None:
        self.schema = schema
        self.algorithm = algorithm

    def evidence(self):
        result = {
            "schema_version": self.schema,
            "contains_test_ground_truth": False,
        }
        if self.schema == "strict_v4_pairwise_runtime_v2":
            result["selected_risk"] = (
                PUG_RISK_NAME
                if self.algorithm == "caeos_pug"
                else "cauchy_modality_support_union"
            )
            result["contains_training_or_test_labels"] = False
        else:
            result["algorithm"] = self.algorithm
        return result

    def predict(self, _views):
        return {
            "prediction": np.asarray([0, 1]),
            "probability": np.asarray([[0.8, 0.2], [0.1, 0.9]]),
            "risk": np.asarray([0.2, 0.7]),
        }


@pytest.mark.parametrize(
    ("schema", "algorithm"),
    [
        ("strict_v4_pairwise_runtime_v2", "caeos_pairwise"),
        ("strict_v4_pairwise_runtime_v2", "caeos_pug"),
        ("strict_v4_krc_csr_runtime_v1", "krc_csr_caeos_v1"),
        ("strict_v4_rrc_csr_runtime_v1", "rrc_csr_caeos_v1"),
    ],
)
def test_adapter_accepts_all_frozen_self_algorithms(
    schema: str, algorithm: str
) -> None:
    runtime = Runtime(schema, algorithm)
    adapter = SelectedSystemRuntime(runtime, algorithm, 0.95)

    output = adapter.predict([])

    assert infer_runtime_algorithm(runtime) == algorithm
    assert output["risk"].tolist() == [0.2, 0.7]
    assert adapter.evidence()["threshold_source"] == "known_validation_only"


def test_adapter_rejects_algorithm_runtime_mismatch() -> None:
    with pytest.raises(ValueError, match="disagrees"):
        SelectedSystemRuntime(
            Runtime("strict_v4_pairwise_runtime_v2", "caeos_pug"),
            "caeos_pairwise",
            0.95,
        )


def test_prediction_contract_rejects_probability_drift() -> None:
    with pytest.raises(ValueError, match="sum to one"):
        validate_prediction_output(
            {
                "prediction": np.asarray([0]),
                "probability": np.asarray([[0.8, 0.8]]),
                "risk": np.asarray([0.2]),
            }
        )


def test_prediction_contract_rejects_argmax_drift() -> None:
    with pytest.raises(ValueError, match="argmax"):
        validate_prediction_output(
            {
                "prediction": np.asarray([1]),
                "probability": np.asarray([[0.8, 0.2]]),
                "risk": np.asarray([0.2]),
            }
        )
