from __future__ import annotations

import pytest

from run_strict_v4_csr_caeos_pilot import validate_protocol


def test_protocol_validation_fails_closed() -> None:
    with pytest.raises(ValueError):
        validate_protocol(
            {
                "schema_version": "strict_v4_csr_caeos_pilot_protocol_v1",
                "execution_admitted": False,
            }
        )
