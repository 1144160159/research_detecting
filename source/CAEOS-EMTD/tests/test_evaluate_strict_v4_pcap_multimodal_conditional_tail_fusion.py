from __future__ import annotations

import numpy as np

from evaluate_strict_v4_pcap_multimodal_conditional_tail_fusion import (
    class_conditional_percentile,
    conditional_tail_candidates,
    fixed_method_records,
    scenario_records,
)


def test_class_conditional_percentile_uses_matching_prediction_class() -> None:
    reference = np.asarray([0.1, 0.2, 10.0, 20.0])
    prediction = np.asarray([0, 0, 1, 1])
    query = np.asarray([0.15, 15.0])

    result = class_conditional_percentile(
        reference,
        prediction,
        query,
        np.asarray([0, 1]),
        minimum_class_samples=2,
    )

    assert np.allclose(result, [0.5, 0.5])


def test_dual_path_candidate_activates_either_component_pair() -> None:
    validation_belief = np.asarray(
        [[0.9, 0.1], [0.8, 0.2], [0.2, 0.8], [0.1, 0.9]]
    )
    test_belief = np.asarray([[0.9, 0.1], [0.1, 0.9]])
    arrays = {
        "baseline_validation_belief": validation_belief,
        "baseline_test_belief": test_belief,
        "self_validation_risk": np.asarray([0.1, 0.2, 0.1, 0.2]),
        "self_test_risk": np.asarray([0.9, 0.9]),
    }
    for component in ("uncertainty", "conflict", "distance", "energy"):
        arrays[f"self_validation_{component}"] = np.asarray(
            [0.1, 0.2, 0.1, 0.2]
        )
    arrays["self_test_uncertainty"] = np.asarray([0.9, 0.1])
    arrays["self_test_energy"] = np.asarray([0.9, 0.1])
    arrays["self_test_conflict"] = np.asarray([0.1, 0.9])
    arrays["self_test_distance"] = np.asarray([0.1, 0.9])

    candidates = conditional_tail_candidates(arrays)
    dual_test = candidates["CCTF-DualPathMax"][1]

    assert dual_test[0] > 0.5
    assert dual_test[1] > 0.5


def test_scenario_records_report_perfect_separation() -> None:
    validation_belief = np.asarray(
        [[0.9, 0.1], [0.8, 0.2], [0.2, 0.8], [0.1, 0.9]]
    )
    test_belief = np.asarray(
        [[0.9, 0.1], [0.1, 0.9], [0.5, 0.5], [0.5, 0.5]]
    )
    arrays = {
        "baseline_validation_belief": validation_belief,
        "baseline_test_belief": test_belief,
        "baseline_test_label": np.asarray([0, 1, -1, -1]),
        "baseline_test_is_unknown": np.asarray(
            [False, False, True, True]
        ),
        "self_validation_risk": np.asarray([0.1, 0.2, 0.1, 0.2]),
        "self_test_risk": np.asarray([0.1, 0.2, 0.9, 1.0]),
    }
    for component in ("uncertainty", "conflict", "distance", "energy"):
        arrays[f"self_validation_{component}"] = np.asarray(
            [0.1, 0.2, 0.1, 0.2]
        )
        arrays[f"self_test_{component}"] = np.asarray(
            [0.1, 0.2, 0.9, 1.0]
        )

    records = scenario_records(arrays)

    assert records["CAEOS-EMTD"]["unknown_auroc"] == 1.0
    assert records["CCTF-DualPathMax"]["unknown_auroc"] == 1.0
    assert set(records) == {
        "CAEOS-EMTD",
        "CCTF-Mean",
        "CCTF-Max",
        "CCTF-Top2Mean",
        "CCTF-DualPathMax",
        "CCTF-SelfDualMean",
        "CCTF-SelfDualMax",
    }


def test_fixed_method_records_keep_only_incumbent_and_frozen_method() -> None:
    validation_belief = np.asarray(
        [[0.9, 0.1], [0.8, 0.2], [0.2, 0.8], [0.1, 0.9]]
    )
    test_belief = np.asarray(
        [[0.9, 0.1], [0.1, 0.9], [0.5, 0.5], [0.5, 0.5]]
    )
    arrays = {
        "baseline_validation_belief": validation_belief,
        "baseline_test_belief": test_belief,
        "baseline_test_label": np.asarray([0, 1, -1, -1]),
        "baseline_test_is_unknown": np.asarray(
            [False, False, True, True]
        ),
        "self_validation_risk": np.asarray([0.1, 0.2, 0.1, 0.2]),
        "self_test_risk": np.asarray([0.1, 0.2, 0.9, 1.0]),
    }
    for component in ("uncertainty", "conflict", "distance", "energy"):
        arrays[f"self_validation_{component}"] = np.asarray(
            [0.1, 0.2, 0.1, 0.2]
        )
        arrays[f"self_test_{component}"] = np.asarray(
            [0.1, 0.2, 0.9, 1.0]
        )

    records = fixed_method_records(arrays, "CCTF-DualPathMax")

    assert set(records) == {"CAEOS-EMTD", "CCTF-DualPathMax"}
