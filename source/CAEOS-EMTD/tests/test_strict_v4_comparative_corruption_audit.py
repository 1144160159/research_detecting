from audit_strict_v4_comparative_corruption_summary import (
    independent_holm,
)


def test_independent_holm_matches_closed_form_example():
    adjusted = independent_holm({"a": 0.001, "b": 0.01, "c": 0.04})
    assert adjusted == {"a": 0.003, "b": 0.02, "c": 0.04}
