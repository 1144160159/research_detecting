"""Attack-chain scoring and a deterministic beam-search baseline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping, Sequence, Tuple


@dataclass(frozen=True)
class ChainEvidence:
    anomaly: float
    temporal: float
    cross_source: float
    stage_compatibility: float
    diversity_coverage: float
    noise: float
    redundancy: float


@dataclass(frozen=True)
class ChainScoreWeights:
    anomaly: float = 1.0
    temporal: float = 1.0
    cross_source: float = 1.0
    stage_compatibility: float = 1.0
    diversity_coverage: float = 1.0
    noise: float = 1.0
    redundancy: float = 1.0


def score_chain(evidence: ChainEvidence, weights: ChainScoreWeights) -> float:
    """Implements alpha*A+beta*T+gamma*X+delta*K+eta*D-lambda*N-mu*R."""

    return (
        weights.anomaly * evidence.anomaly
        + weights.temporal * evidence.temporal
        + weights.cross_source * evidence.cross_source
        + weights.stage_compatibility * evidence.stage_compatibility
        + weights.diversity_coverage * evidence.diversity_coverage
        - weights.noise * evidence.noise
        - weights.redundancy * evidence.redundancy
    )


def beam_search_paths(
    adjacency: Mapping[str, Sequence[Tuple[str, float]]],
    seed: str,
    max_hops: int = 6,
    beam_width: int = 10,
) -> List[Tuple[Tuple[str, ...], float]]:
    """Return acyclic top paths under additive edge scores.

    This is a transparent lower-bound baseline, not the final ATT&CK decoder.
    """

    if max_hops < 0 or beam_width <= 0:
        raise ValueError("max_hops must be non-negative and beam_width positive")
    beam = [((seed,), 0.0)]
    completed = list(beam)
    for _ in range(max_hops):
        expanded = []
        for path, path_score in beam:
            for neighbor, edge_score in adjacency.get(path[-1], ()):  # type: ignore[arg-type]
                if neighbor in path:
                    continue
                expanded.append((path + (neighbor,), path_score + float(edge_score)))
        if not expanded:
            break
        expanded.sort(key=lambda item: (-item[1], item[0]))
        beam = expanded[:beam_width]
        completed.extend(beam)

    best_by_path = {path: score for path, score in completed}
    return sorted(best_by_path.items(), key=lambda item: (-item[1], item[0]))[:beam_width]
