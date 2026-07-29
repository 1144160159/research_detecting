from create_strict_v4_core_warning_protocol import create_protocol


def test_core_warning_protocol_freezes_non_posthoc_confirmation() -> None:
    protocol = create_protocol("a" * 64)

    assert protocol["status"] == "frozen_before_fresh_seed_confirmation"
    assert protocol["core_confirmation"]["fresh_seeds"] == [907, 911, 919]
    assert protocol["core_confirmation"]["development_seed_excluded"] == 7
    assert protocol["basic_warning_gate"]["alert_accuracy_min"] == 0.95
    assert protocol["basic_warning_gate"]["benign_fpr_strict_max"] == 0.05
    assert protocol["open_set_gate"]["unknown_label_recall_min"] == 0.95
    assert protocol["claim_boundary"]["single_dataset_pass_is_not_comprehensive_sota"]
    assert "ronetc" in protocol["main_baselines"]
    assert "hierarchical_pairwise" in protocol["self_algorithms"]


def test_core_warning_protocol_forbids_test_metric_dataset_selection() -> None:
    protocol = create_protocol("b" * 64)
    forbidden = protocol["data_optimization"]["forbidden"]

    assert "selecting a dataset because its seed7 result passed" in forbidden
    assert "using unknown or test labels for threshold selection" in forbidden
