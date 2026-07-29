from create_strict_v4_xgboost_seed7_development_protocol import SCENARIOS
from summarize_strict_v4_xgboost_seed7_development import basic_gate


def test_seed7_development_universe_is_cicids2017_leave_one_attack_out() -> None:
    assert len(SCENARIOS) == 14
    assert len(set(SCENARIOS)) == 14
    assert {"bot", "heartbleed", "web_sql_injection"} <= set(SCENARIOS)


def test_basic_gate_requires_all_operational_targets() -> None:
    passing = {
        "alert_accuracy": 0.95,
        "alert_precision": 0.95,
        "alert_recall": 0.95,
        "benign_fpr": 0.049,
        "known_attack_type_accuracy": 0.95,
    }
    assert basic_gate(passing)
    for key in (
        "alert_accuracy",
        "alert_precision",
        "alert_recall",
        "known_attack_type_accuracy",
    ):
        failing = dict(passing)
        failing[key] = 0.949
        assert not basic_gate(failing)
    failing_fpr = dict(passing)
    failing_fpr["benign_fpr"] = 0.05
    assert not basic_gate(failing_fpr)
