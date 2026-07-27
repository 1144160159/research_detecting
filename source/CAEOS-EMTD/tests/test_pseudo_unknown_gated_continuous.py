from __future__ import annotations

import copy

from caeos.pseudo_unknown_gated_continuous import (
    PUG_GATE_V1,
    PUG_RISK_NAME,
    evaluate_pseudo_unknown_gate,
    select_pug_route,
)


def folds() -> list[dict]:
    rows = []
    for index in range(6):
        reference = {
            "known_macro_f1": 0.8,
            "unknown_auroc": 0.70,
            "unknown_aupr": 0.60,
            "unknown_fpr95": 0.60,
            "oscr": 0.55,
        }
        candidate = {
            "known_macro_f1": 0.8,
            "unknown_auroc": 0.71,
            "unknown_aupr": 0.61,
            "unknown_fpr95": 0.55,
            "oscr": 0.56,
        }
        rows.append(
            {
                "fold": f"attack_{index}",
                "reference": reference,
                "candidate": candidate,
            }
        )
    return rows


def test_gate_selects_continuous_route_only_when_every_check_passes() -> None:
    result = evaluate_pseudo_unknown_gate(folds(), PUG_GATE_V1)

    assert result["passes"] is True
    assert result["selected_route"] == "continuous_outer_min_p"
    assert result["selection_uses_unknown_or_test_labels"] is False
    assert result["checks"]["worst_fold_aupr_protection"] is True


def test_gate_rejects_hidden_worst_fold_aupr_loss() -> None:
    rows = folds()
    rows[0]["candidate"]["unknown_aupr"] = 0.585
    for row in rows[1:]:
        row["candidate"]["unknown_aupr"] = 0.62

    result = evaluate_pseudo_unknown_gate(rows, PUG_GATE_V1)

    assert result["aggregates"]["unknown_aupr"]["mean_oriented_delta"] > 0
    assert result["checks"]["worst_fold_aupr_protection"] is False
    assert result["passes"] is False
    assert result["selected_route"] == "exact_pairwise_passthrough"


def test_gate_rejects_known_f1_change() -> None:
    rows = copy.deepcopy(folds())
    rows[1]["candidate"]["known_macro_f1"] += 1e-6

    result = evaluate_pseudo_unknown_gate(rows, PUG_GATE_V1)

    assert result["checks"]["known_macro_f1_invariant"] is False
    assert result["passes"] is False


def test_route_preserves_pairwise_learned_endpoint() -> None:
    route = select_pug_route(
        "pseudo_unknown_learned_blend",
        {
            "passes": True,
            "selection_uses_unknown_or_test_labels": False,
        },
    )

    assert route["pug_base_route_eligible"] is False
    assert route["selected_risk"] == "pseudo_unknown_learned_blend"


def test_route_falls_back_when_pug_gate_fails() -> None:
    route = select_pug_route(
        "cauchy_modality_support_union",
        {
            "passes": False,
            "selection_uses_unknown_or_test_labels": False,
        },
    )

    assert route["pug_base_route_eligible"] is True
    assert route["pug_selected"] is False
    assert route["selected_risk"] == "cauchy_modality_support_union"


def test_route_selects_pug_only_after_pairwise_fallback_and_gate_pass() -> None:
    route = select_pug_route(
        "cauchy_modality_support_union",
        {
            "passes": True,
            "selection_uses_unknown_or_test_labels": False,
        },
    )

    assert route["pug_selected"] is True
    assert route["selected_risk"] == PUG_RISK_NAME
