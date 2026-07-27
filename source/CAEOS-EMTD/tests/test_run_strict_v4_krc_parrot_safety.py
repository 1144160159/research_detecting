import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_krc_parrot_safety import validate_protocol


def protocol():
    sources = [
        {
            "scenario": f"scenario{scenario}",
            "training_seed": seed,
        }
        for scenario in range(10)
        for seed in (647, 653, 659)
    ]
    value = {
        "schema_version": "strict_v4_krc_parrot_safety_protocol_v1",
        "execution_admitted": True,
        "selected_algorithm": "krc_csr_caeos_v1",
        "source_model_pair_count": 30,
        "source_model_pairs": sources,
        "capture_count": 320,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def test_validate_protocol_accepts_ustc_10_by_3():
    validate_protocol(protocol())


def test_validate_protocol_rejects_duplicate_pair():
    value = protocol()
    value["source_model_pairs"][-1] = dict(
        value["source_model_pairs"][0]
    )
    value["manifest_sha256"] = canonical_hash(value)
    with pytest.raises(ValueError, match="invalid"):
        validate_protocol(value)


def test_validate_protocol_rejects_unadmitted_execution():
    value = protocol()
    value["execution_admitted"] = False
    value["manifest_sha256"] = canonical_hash(value)
    with pytest.raises(ValueError, match="invalid"):
        validate_protocol(value)
