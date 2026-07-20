from confirm_cross_suite_fixed_risk import confirmation_decision


def inference(delta: float, lower: float = 0.01) -> dict[str, object]:
    metrics = {}
    for metric in (
        "known_macro_f1",
        "unknown_auroc",
        "unknown_aupr",
        "unknown_fpr95",
        "oscr",
    ):
        metrics[metric] = {
            "oriented_mean_improvement": delta,
            "bootstrap_95_ci": {"lower": lower, "upper": 0.1},
        }
    return {"metrics": metrics}


def test_confirmation_decision_requires_all_frozen_gates() -> None:
    combined = inference(0.02)
    suites = {"nf_cse": inference(0.01), "ustc_tfc2016": inference(0.01)}
    assert confirmation_decision(combined, suites, 0.01)["passes"] is True

    suites["ustc_tfc2016"]["metrics"]["unknown_fpr95"][
        "oriented_mean_improvement"
    ] = 0.0
    assert confirmation_decision(combined, suites, 0.01)["passes"] is False


def test_confirmation_decision_rejects_primary_ci_and_safety_regression() -> None:
    combined = inference(0.02, lower=0.0)
    suites = {"nf_cse": inference(0.01), "ustc_tfc2016": inference(0.01)}
    assert confirmation_decision(combined, suites, 0.01)["passes"] is False

    combined = inference(0.02)
    combined["metrics"]["known_macro_f1"]["oriented_mean_improvement"] = -0.011
    assert confirmation_decision(combined, suites, 0.01)["passes"] is False
