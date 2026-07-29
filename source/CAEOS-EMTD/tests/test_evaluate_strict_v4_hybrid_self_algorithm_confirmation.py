from evaluate_strict_v4_hybrid_self_algorithm_development import gates


def test_all_seed_contract_cannot_be_replaced_by_overall_mean() -> None:
    passing = {
        "alert_accuracy": 0.96,
        "alert_precision": 0.97,
        "alert_recall": 0.96,
        "alert_f1": 0.96,
        "benign_fpr": 0.04,
        "known_attack_type_accuracy": 0.96,
        "unknown_attack_alert_recall": 0.97,
        "unknown_attack_recall": 0.96,
        "unknown_label_precision": 0.8,
    }
    failing = dict(passing)
    failing["benign_fpr"] = 0.051
    by_seed = [gates(passing), gates(passing), gates(failing)]
    assert not all(value["full_known_unknown_95_5_gate"] for value in by_seed)
