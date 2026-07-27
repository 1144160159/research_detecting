from __future__ import annotations

import pytest

from watch_strict_v4_krc_confirmation_progress import (
    atomic_checkpoint_count,
)


def test_atomic_checkpoint_requires_complete_six_condition_publication():
    assert atomic_checkpoint_count(28, 28, 168) == 28
    assert atomic_checkpoint_count(28, 27, 168) is None
    assert atomic_checkpoint_count(28, 28, 167) is None
    assert atomic_checkpoint_count(26, 26, 156) is None
    assert atomic_checkpoint_count(306, 306, 1836) == 306


def test_atomic_checkpoint_rejects_invalid_counts():
    with pytest.raises(ValueError):
        atomic_checkpoint_count(-1, 0, 0)
    assert atomic_checkpoint_count(307, 307, 1842) is None
