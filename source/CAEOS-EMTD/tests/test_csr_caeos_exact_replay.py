import numpy as np

from caeos.csr_exact_replay_runtime import CSRExactReplayRuntime


class FakeBaseRuntime:
    clean_threshold = 0.5

    def predict(self, raw_views):
        clean_probability = np.asarray(
            [[0.8, 0.2], [0.3, 0.7]], dtype=np.float64
        )
        probability = clean_probability.copy()
        probability[0, 0] = np.nextafter(probability[0, 0], 1.0)
        return {
            "prediction": probability.argmax(axis=1),
            "probability": probability,
            "clean_probability": clean_probability,
            "risk": np.asarray([0.4, 0.9]),
            "clean_risk": np.asarray([0.2, 0.9]),
            "active": np.asarray([True, False]),
            "any_missing": np.asarray([False, False]),
        }

    def corrupt(self, raw_views, **kwargs):
        return [np.asarray(view).copy() for view in raw_views]

    def evidence(self):
        return {
            "schema_version": "strict_v4_csr_caeos_runtime_v1",
            "algorithm": "csr_caeos_v1",
            "contains_test_ground_truth": False,
            "modality_count": 1,
        }


def test_exact_replay_changes_only_prediction_probability_source():
    runtime = CSRExactReplayRuntime(FakeBaseRuntime())
    source = runtime.base_runtime.predict([np.zeros((2, 1))])
    result = runtime.predict([np.zeros((2, 1))])
    assert not np.array_equal(
        source["probability"], source["clean_probability"]
    )
    assert np.array_equal(
        result["probability"], result["clean_probability"]
    )
    assert np.array_equal(
        result["prediction"], result["clean_probability"].argmax(axis=1)
    )
    assert np.array_equal(result["risk"], source["risk"])
    assert np.array_equal(result["active"], source["active"])
    assert runtime.clean_threshold == source.get("threshold", 0.5)


def test_exact_replay_evidence_is_effect_blind():
    evidence = CSRExactReplayRuntime(FakeBaseRuntime()).evidence()
    assert evidence["runtime_revision"] == "exact_clean_probability_replay_v2"
    assert evidence["technical_repair"]["changes_risk"] is False
    assert evidence["technical_repair"]["changes_active_mask"] is False
    assert evidence["technical_repair"]["reads_effect_metrics"] is False
    assert evidence["technical_repair"]["reads_test_labels"] is False
