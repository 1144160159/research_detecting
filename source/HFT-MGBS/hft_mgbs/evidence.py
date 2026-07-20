"""Evidence gate preventing partial benchmarks from entering final Pareto selection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Tuple

from .optimization import CandidateMetrics


REQUIRED_EVIDENCE = (
    "throughput_live_replay",
    "nic_packet_drop",
    "end_to_end_p99",
    "end_to_end_p999",
    "cpu_resource",
    "gpu_resource",
    "memory_resource",
    "budget_overrun",
    "key_flow_coverage",
    "fallback_recovery",
    "quality_protocol",
)


@dataclass(frozen=True)
class CandidateEvidenceEnvelope:
    metrics: CandidateMetrics
    evidence: Mapping[str, bool]
    manifest_status: str
    measured_repeats: int
    code_sha256: str
    input_sha256: str

    @classmethod
    def from_mapping(cls, values: Mapping[str, object]) -> "CandidateEvidenceEnvelope":
        return cls(
            metrics=CandidateMetrics.from_mapping(values["metrics"]),
            evidence=dict(values["evidence"]),
            manifest_status=str(values["manifest_status"]),
            measured_repeats=int(values["measured_repeats"]),
            code_sha256=str(values["code_sha256"]),
            input_sha256=str(values["input_sha256"]),
        )


@dataclass(frozen=True)
class EvidenceAudit:
    accepted: bool
    errors: Tuple[str, ...]

    def as_dict(self) -> Dict[str, object]:
        return {"accepted": self.accepted, "errors": list(self.errors)}


def audit_candidate_evidence(envelope: CandidateEvidenceEnvelope) -> EvidenceAudit:
    errors = []
    missing = [name for name in REQUIRED_EVIDENCE if not envelope.evidence.get(name, False)]
    if missing:
        errors.append("missing_verified_evidence:" + ",".join(missing))
    unknown = sorted(set(envelope.evidence) - set(REQUIRED_EVIDENCE))
    if unknown:
        errors.append("unknown_evidence_flags:" + ",".join(unknown))
    if envelope.manifest_status != "complete":
        errors.append("manifest_not_complete")
    if envelope.measured_repeats < 3:
        errors.append("measured_repeats_below_3")
    if len(envelope.code_sha256) != 64:
        errors.append("invalid_code_sha256")
    if len(envelope.input_sha256) != 64:
        errors.append("invalid_input_sha256")
    return EvidenceAudit(not errors, tuple(errors))
