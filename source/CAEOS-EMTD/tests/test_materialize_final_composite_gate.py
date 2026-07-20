from __future__ import annotations

from materialize_final_composite_gate import CURRENT_SUITE_RISK, POLICY, rewrite_metrics


def report(auroc: float) -> dict[str, float]:
    return {
        "known_macro_f1": 0.9,
        "unknown_auroc": auroc,
        "unknown_aupr": 0.7,
        "unknown_fpr95": 0.4,
        "oscr": 0.75,
    }


def source_metrics() -> dict[str, object]:
    return {
        "seed": 7,
        "selected_risk": "nested_hierarchical_joint_gate",
        "selected_report": report(0.8),
        "reports": {"disagreement_augmented": report(0.9)},
        "validation_thresholds": {"disagreement_augmented": 0.95},
        "risk_selection": "nested_hierarchical_joint_gate",
        "risk_policy": "source",
        "parameter_fingerprint": "a" * 64,
        "arguments": {
            "risk_selection": "nested_hierarchical_joint_gate",
            "risk_policy": "source",
        },
    }


def test_composite_materializer_applies_confirmed_nf_risk() -> None:
    result, fingerprint = rewrite_metrics(
        source_metrics(),
        "nf_cse",
        "disagreement_augmented",
        "b" * 64,
        "c" * 64,
    )
    assert result["selected_risk"] == "disagreement_augmented"
    assert result["selected_report"]["unknown_auroc"] == 0.9
    assert result["risk_policy"] == POLICY
    assert result["arguments"]["risk_selection"] == "disagreement_augmented"
    assert len(fingerprint) == 64
    assert result["final_composite_risk_selection"][
        "unknown_or_test_labels_used_for_runtime_selection"
    ] is False


def test_composite_materializer_preserves_confirmed_reference_report() -> None:
    result, _ = rewrite_metrics(
        source_metrics(),
        "ustc_tfc2016",
        CURRENT_SUITE_RISK,
        "b" * 64,
        "c" * 64,
    )
    assert result["selected_risk"] == "nested_hierarchical_joint_gate"
    assert result["final_composite_risk_selection"]["suite_policy"] == CURRENT_SUITE_RISK
    assert result["selected_report"]["unknown_auroc"] == 0.8
