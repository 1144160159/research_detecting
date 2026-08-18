import sys

from run_nested_gate_matrix import parse_arguments


def test_matrix_parser_exposes_frozen_pug_selection(monkeypatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_nested_gate_matrix.py",
            "--risk-selection",
            "nested_pug_continuous_outer_min_p",
        ],
    )

    args = parse_arguments()

    assert args.risk_selection == "nested_pug_continuous_outer_min_p"
