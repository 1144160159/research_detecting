from analyze_strict_v4_self_algorithm_operational_gaps import metric_gaps


def test_operational_gaps_separate_alert_and_unknown_rejection() -> None:
    gaps = metric_gaps(
        {
            "alert_accuracy": 0.96,
            "benign_fpr": 0.056,
            "known_attack_type_accuracy": 0.97,
            "unknown_attack_alert_recall": 0.84,
            "unknown_attack_recall": 0.72,
        }
    )
    assert gaps["alert_accuracy_deficit_to_95"] == 0.0
    assert abs(gaps["benign_fpr_excess_over_5"] - 0.006) < 1e-12
    assert gaps["known_attack_type_accuracy_deficit_to_95"] == 0.0
    assert abs(gaps["unknown_attack_recall_deficit_to_95"] - 0.23) < 1e-12
    assert abs(gaps["unknown_missed_before_alert_fraction"] - 0.16) < 1e-12
    assert (
        abs(
            gaps["unknown_alerted_but_not_labeled_unknown_fraction"] - 0.12
        )
        < 1e-12
    )
