from analyze_strict_v4_validation_router import REFERENCE
from analyze_strict_v4_validation_router_v2 import analyze, build_manifest


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
    feature_names = (
        "rank_correlation",
        "mean_absolute_rank_difference",
        "top5_jaccard",
        "current_class_q95_std",
        "cauchy_class_q95_std",
        "class_q95_std_delta",
        "current_class_rejection_std",
        "cauchy_class_rejection_std",
        "class_rejection_std_delta",
    )
    return {
        "suite": suite,
        "scenario": scenario,
        "seed": seed,
        "features": {**{name: feature for name in feature_names}, "known_class_count": 5.0},
        "reports": {REFERENCE: base, "cauchy_all": candidate},
    }


def test_suite_router_freezes_separate_rules_and_new_boundary():
    runs = []
    for suite in ("cic_ton_iot", "cic_iot2023"):
        for index in range(6):
            runs.append(_run(suite, f"s{index}", 7, 0.2 + index * 0.1, 0.02))
    report = analyze(
        runs,
        {
            "run_count": len(runs),
            "scenario_count": 12,
            "source_metrics_combined_sha256": "synthetic",
        },
    )
    assert report["freeze_candidate"] is True
    manifest = build_manifest(report)
    assert manifest["status"] == "frozen_unconfirmed"
    assert set(manifest["candidate"]["selected_rules"]) == {
        "cic_ton_iot",
        "cic_iot2023",
    }
    assert manifest["confirmation"]["expected_run_count"] == 30
    assert manifest["confirmation"]["seeds"] == [59, 61]
