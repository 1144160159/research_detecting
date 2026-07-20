from collections import Counter

from confirm_strict_v4_validation_router import decision


def _metric(gain: float, lower: float = 0.001):
    return {
        "oriented_mean_improvement": gain,
        "bootstrap_95_ci": {"lower": lower, "upper": gain + 0.01},
    }


def test_router_decision_requires_suite_gains_and_both_endpoints():
    combined = {
        "metrics": {
            "unknown_auroc": _metric(0.02),
            "unknown_aupr": _metric(0.01),
            "unknown_fpr95": _metric(0.03),
            "oscr": _metric(0.01),
        }
    }
    suite_report = {
        "metrics": {
            "unknown_auroc": _metric(0.01),
            "unknown_aupr": _metric(0.01),
            "unknown_fpr95": _metric(0.01),
            "oscr": _metric(0.01),
        }
    }
    suites = {"cic_ton_iot": suite_report, "cic_iot2023": suite_report}
    passed = decision(combined, suites, Counter({"cauchy_all": 10, "cauchy_modality_support_union": 20}), 0.01)
    assert passed["passes"] is True
    failed = decision(combined, suites, Counter({"cauchy_all": 30}), 0.01)
    assert failed["passes"] is False
