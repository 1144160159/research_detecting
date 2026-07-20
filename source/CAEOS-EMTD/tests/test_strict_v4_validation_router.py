from analyze_strict_v4_validation_router import (
    CONFIRMATION,
    REFERENCE,
    analyze,
    build_manifest,
    select_endpoint,
)


def _run(suite: str, scenario: str, seed: int, feature: float, gain: float):
    base = {
        "unknown_auroc": 0.5,
        "unknown_aupr": 0.5,
        "unknown_fpr95": 0.5,
        "oscr": 0.5,
    }
    candidate = {
        "unknown_auroc": 0.5 + gain,
        "unknown_aupr": 0.5 + gain,
        "unknown_fpr95": 0.5 - gain,
        "oscr": 0.5 + gain,
    }
    return {
        "suite": suite,
        "scenario": scenario,
        "seed": seed,
        "features": {
            "rank_correlation": feature,
            "mean_absolute_rank_difference": feature,
            "top5_jaccard": feature,
            "current_class_q95_std": feature,
            "cauchy_class_q95_std": feature,
            "class_q95_std_delta": feature,
            "current_class_rejection_std": feature,
            "cauchy_class_rejection_std": feature,
            "class_rejection_std_delta": feature,
            "known_class_count": 5.0,
        },
        "reports": {REFERENCE: base, "cauchy_all": candidate},
    }


def test_validation_router_freezes_only_after_nested_scenario_gains():
    runs = []
    for suite in ("cic_ton_iot", "cic_iot2023"):
        for index in range(6):
            runs.append(_run(suite, f"s{index}", 7, 0.2 + index * 0.1, 0.02))
    report = analyze(
        runs,
        {
            "run_count": len(runs),
            "scenario_count": 12,
            "runtime_features_use_known_validation_only": True,
            "source_metrics_combined_sha256": "synthetic",
        },
    )
    assert report["freeze_candidate"] is True
    assert all(value > 0 for value in report["nested_loso"]["combined"].values())
    rule = report["full_development"]["selected_rule"]
    assert select_endpoint(rule, runs[0]) in {REFERENCE, "cauchy_all"}
    manifest = build_manifest(report, {"synthetic": {}})
    assert manifest["status"] == "frozen_unconfirmed"
    assert manifest["confirmation"]["expected_run_count"] == 30
    assert manifest["confirmation"]["seeds"] == [47, 53]
    assert len(CONFIRMATION["scenarios"]["cic_ton_iot"]) == 9
