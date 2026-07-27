import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_mdr_parrot_safety import validate_protocol


def protocol():
    sources = [
        {"scenario": f"scenario{scenario}", "training_seed": seed}
        for scenario in range(10)
        for seed in (137, 139, 149)
    ]
    value = {
        "schema_version": "strict_v4_mdr_parrot_safety_protocol_v1",
        "selected_algorithm": "mdr_caeos_v1",
        "source_model_pair_count": 30,
        "source_model_pairs": sources,
        "capture_count": 320,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def test_validate_protocol_accepts_30_model_pairs():
    validate_protocol(protocol())


def test_validate_protocol_rejects_duplicate_model_pair():
    value = protocol()
    value["source_model_pairs"][-1] = dict(value["source_model_pairs"][0])
    value["manifest_sha256"] = canonical_hash(value)
    with pytest.raises(ValueError, match="invalid"):
        validate_protocol(value)


def test_validate_protocol_rejects_non_mdr_algorithm():
    value = protocol()
    value["selected_algorithm"] = "caeos_pairwise"
    value["manifest_sha256"] = canonical_hash(value)
    with pytest.raises(ValueError, match="invalid"):
        validate_protocol(value)
