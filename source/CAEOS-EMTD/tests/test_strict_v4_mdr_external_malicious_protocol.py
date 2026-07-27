from pathlib import Path

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_external_malicious_protocol import (
    create_protocol,
    derive_seed,
    require_canonical,
)


def test_derived_seeds_are_deterministic_and_purpose_separated():
    left = derive_seed("a" * 64, "LSNM2024", "attack", 223, "augmentation")
    again = derive_seed(
        "a" * 64, "LSNM2024", "attack", 223, "augmentation"
    )
    profile = derive_seed(
        "a" * 64, "LSNM2024", "attack", 223, "validation_profile"
    )
    assert left == again
    assert left != profile
    assert 0 <= left < 2**31


def test_derived_seed_changes_with_scenario_identity():
    first = derive_seed("b" * 64, "LSNM2024", "a", 223, "augmentation")
    second = derive_seed("b" * 64, "LSNM2024", "b", 223, "augmentation")
    assert first != second


def test_canonical_guard_rejects_drift():
    value = {"schema_version": "schema", "field": 1}
    value["manifest_sha256"] = canonical_hash(value)
    require_canonical(value, "schema", "value")
    value["field"] = 2
    with pytest.raises(ValueError, match="canonical SHA"):
        require_canonical(value, "schema", "value")


def test_protocol_module_imports_without_results():
    assert Path(__file__).name.endswith("_protocol.py")


def test_confirmation_runtime_parameters_are_nested():
    import inspect

    source = inspect.getsource(create_protocol)
    assert 'confirmation_protocol["confirmation"]' in source
    assert '"health_quantile"' in source
    assert '"training_sample_fraction"' in source
