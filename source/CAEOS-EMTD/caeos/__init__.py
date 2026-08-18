"""Conflict-aware evidential open-set traffic detection."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .model import ConflictAwareEvidentialNet
    from .open_set import OpenSetCalibrator

__all__ = ["ConflictAwareEvidentialNet", "OpenSetCalibrator"]


def __getattr__(name: str) -> Any:
    if name == "ConflictAwareEvidentialNet":
        from .model import ConflictAwareEvidentialNet

        return ConflictAwareEvidentialNet
    if name == "OpenSetCalibrator":
        from .open_set import OpenSetCalibrator

        return OpenSetCalibrator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
