from __future__ import annotations

import numpy as np


def conformal_upper_tail_probability(
    calibration_topology: np.ndarray,
    topology_risk: np.ndarray,
) -> np.ndarray:
    """Return finite-sample upper-tail conformal p-values for topology risk."""
    calibration = np.asarray(calibration_topology, dtype=np.float64)
    query = np.asarray(topology_risk, dtype=np.float64)
    if calibration.ndim != 1 or query.ndim != 1:
        raise ValueError("calibration and query topology risk must be vectors")
    if calibration.size < 20:
        raise ValueError("at least 20 known calibration scores are required")
    if not np.isfinite(calibration).all() or not np.isfinite(query).all():
        raise ValueError("topology risk values must be finite")
    if np.any((calibration < 0.0) | (calibration > 1.0)) or np.any(
        (query < 0.0) | (query > 1.0)
    ):
        raise ValueError("topology risk must be in [0, 1]")

    ordered = np.sort(calibration)
    first_ge = np.searchsorted(ordered, query, side="left")
    tail_count = calibration.size - first_ge
    return (1.0 + tail_count.astype(np.float64)) / (calibration.size + 1.0)


def budgeted_conformal_uplift(
    incumbent_risk: np.ndarray,
    topology_risk: np.ndarray,
    calibration_topology: np.ndarray,
    tail_probability: float = 0.05,
    alpha: float = 0.25,
) -> tuple[np.ndarray, dict[str, np.ndarray | int | float]]:
    """Apply one-sided topology uplift under a deterministic unlabeled batch budget."""
    incumbent = np.asarray(incumbent_risk, dtype=np.float64)
    topology = np.asarray(topology_risk, dtype=np.float64)
    if incumbent.ndim != 1 or incumbent.shape != topology.shape:
        raise ValueError("incumbent and topology risk must be aligned vectors")
    if not np.isfinite(incumbent).all() or np.any(
        (incumbent < 0.0) | (incumbent > 1.0)
    ):
        raise ValueError("incumbent risk must be finite and in [0, 1]")
    if not 0.0 < float(tail_probability) < 0.5:
        raise ValueError("tail_probability must be in (0, 0.5)")
    if not 0.0 <= float(alpha) <= 1.0:
        raise ValueError("alpha must be in [0, 1]")

    p_values = conformal_upper_tail_probability(calibration_topology, topology)
    strength = np.clip(
        (float(tail_probability) - p_values) / float(tail_probability), 0.0, 1.0
    )
    eligible = np.flatnonzero(strength > 0.0)
    budget = int(np.floor(float(tail_probability) * incumbent.size))
    selected = np.zeros(incumbent.size, dtype=bool)
    if budget > 0 and eligible.size:
        # Primary order is decreasing topology risk; index is a deterministic tie-break.
        order = np.lexsort((eligible, -topology[eligible]))
        selected[eligible[order[: min(budget, eligible.size)]]] = True

    applied_strength = np.where(selected, strength, 0.0)
    candidate = incumbent + float(alpha) * (1.0 - incumbent) * applied_strength
    candidate = np.clip(candidate, incumbent, 1.0)
    evidence: dict[str, np.ndarray | int | float] = {
        "p_values": p_values,
        "strength": applied_strength,
        "selected": selected,
        "budget": budget,
        "selected_count": int(selected.sum()),
        "activation_rate": float(np.mean(selected)) if selected.size else 0.0,
    }
    return candidate, evidence
