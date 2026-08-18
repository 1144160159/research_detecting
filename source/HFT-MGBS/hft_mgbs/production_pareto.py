"""Fail-closed selection of a sealed production Pareto candidate.

This module is intentionally independent from the exploratory algorithm and
runtime selectors.  Its input unit is one *joint deployment envelope*: frozen
algorithm quality plus data-plane, resource, fallback, restoration and evidence
identity for the exact implementation that would be released.
"""

from __future__ import annotations

import math
import hashlib
import json
import re
from datetime import datetime
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Tuple

from hft_mgbs.capture_runtime_decision import (
    DPDK_BACKEND,
    NATIVE_XDP_BACKEND,
    RuntimeDecisionContractError,
    evaluate_runtime_decision,
)
from hft_mgbs.algorithm_campaign_gate import verify_algorithm_campaign_gate


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

METRIC_NAMES = (
    "grouped_macro_f1",
    "independent_macro_f1",
    "independent_attack_recall",
    "independent_benign_recall",
    "independent_auprc",
    "independent_ece",
    "ground_truth_event_recall",
    "gain_per_cost",
    "throughput_mpps",
    "packet_drop_count",
    "p99_latency_us",
    "p999_latency_us",
    "cpu_utilization",
    "gpu_utilization",
    "memory_utilization",
    "gpu_memory_utilization",
    "budget_overrun_count",
    "key_flow_coverage",
    "fallback_recovery_s",
    "complexity",
)


@dataclass(frozen=True)
class EliminationReason:
    code: str
    actual: Any = None
    limit: Any = None
    relation: Optional[str] = None
    detail: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SelectionPolicy:
    policy_id: str
    min_joint_candidates: int
    max_joint_candidates: int
    max_algorithm_candidates: int
    minimum_measured_repeats: int
    required_evidence: Tuple[str, ...]
    hard_constraints: Mapping[str, Mapping[str, Any]]
    objectives: Mapping[str, str]
    weights: Mapping[str, float]
    rejected_production_backends: Tuple[str, ...]
    equal_capability_backend_priority: Tuple[str, ...]
    algorithm_search_gate: Mapping[str, Any]
    algorithm_campaign_gate: Mapping[str, Any]
    runtime_decision_gate: Mapping[str, Any]
    candidate_evidence_gate: Mapping[str, Any]

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any]) -> "SelectionPolicy":
        if values.get("schema_version") != 1:
            raise ValueError("unsupported production Pareto policy schema")
        policy_id = values.get("policy_id")
        if not isinstance(policy_id, str) or not policy_id:
            raise ValueError("policy_id is required")
        limits = values.get("candidate_limits")
        evidence = values.get("evidence_gate")
        constraints = values.get("hard_constraints")
        objectives = values.get("objectives")
        weights = values.get("champion_weights")
        backend_policy = values.get("backend_policy")
        algorithm_search_gate = values.get("algorithm_search_gate")
        algorithm_campaign_gate = values.get("algorithm_campaign_gate")
        runtime_decision_gate = values.get("runtime_decision_gate")
        candidate_evidence_gate = values.get("candidate_evidence_gate")
        if not all(
            isinstance(item, Mapping)
            for item in (
                limits,
                evidence,
                constraints,
                objectives,
                weights,
                backend_policy,
                algorithm_search_gate,
                algorithm_campaign_gate,
                runtime_decision_gate,
                candidate_evidence_gate,
            )
        ):
            raise ValueError("policy sections must be objects")
        min_joint = _positive_integer(limits.get("minimum_joint_candidates"))
        max_joint = _positive_integer(limits.get("maximum_joint_candidates"))
        max_algorithms = _positive_integer(
            limits.get("maximum_algorithm_candidates")
        )
        repeats = _positive_integer(evidence.get("minimum_measured_repeats"))
        required = evidence.get("required_flags")
        if (
            min_joint is None
            or max_joint is None
            or max_algorithms is None
            or repeats is None
            or min_joint > max_joint
        ):
            raise ValueError("invalid candidate/evidence limits")
        if (
            not isinstance(required, list)
            or not required
            or any(not isinstance(item, str) or not item for item in required)
            or len(required) != len(set(required))
        ):
            raise ValueError("required evidence flags must be unique strings")
        parsed_constraints: Dict[str, Mapping[str, Any]] = {}
        for metric, rule in constraints.items():
            if metric not in METRIC_NAMES or not isinstance(rule, Mapping):
                raise ValueError("invalid hard-constraint metric")
            relation = rule.get("relation")
            limit = _finite_number(rule.get("limit"))
            if relation not in (">=", "<=") or limit is None:
                raise ValueError("invalid hard-constraint rule")
            parsed_constraints[metric] = {
                "relation": relation,
                "limit": limit,
            }
        parsed_objectives: Dict[str, str] = dict(objectives)
        allowed_objectives = set(METRIC_NAMES) | {"resource_pressure"}
        if (
            not parsed_objectives
            or any(name not in allowed_objectives for name in parsed_objectives)
            or any(direction not in ("min", "max") for direction in parsed_objectives.values())
        ):
            raise ValueError("invalid Pareto objective")
        parsed_weights: Dict[str, float] = {}
        if set(weights) != set(parsed_objectives):
            raise ValueError("champion weights must exactly cover objectives")
        for name, value in weights.items():
            number = _finite_number(value)
            if number is None or number < 0:
                raise ValueError("champion weights must be finite and non-negative")
            parsed_weights[name] = number
        if sum(parsed_weights.values()) <= 0:
            raise ValueError("champion weights must have a positive total")
        rejected_backends = backend_policy.get("rejected_production_backends")
        backend_priority = backend_policy.get("equal_capability_priority")
        for name, item in (
            ("rejected_production_backends", rejected_backends),
            ("equal_capability_priority", backend_priority),
        ):
            if (
                not isinstance(item, list)
                or not item
                or any(not isinstance(value, str) or not value for value in item)
                or len(item) != len(set(item))
            ):
                raise ValueError(name + " must contain unique backend names")
        if backend_policy.get("priority_applies_only_to_exact_objective_ties") is not True:
            raise ValueError("backend priority must be limited to exact objective ties")
        search_path = algorithm_search_gate.get("path")
        search_sha256 = algorithm_search_gate.get("sha256")
        expected_actual = _positive_integer(
            algorithm_search_gate.get("expected_actual_candidates")
        )
        expected_maximum = _positive_integer(
            algorithm_search_gate.get("expected_maximum_candidates")
        )
        production_maximum = _positive_integer(
            algorithm_search_gate.get("production_admission_maximum_candidates")
        )
        allowed_algorithms = algorithm_search_gate.get("allowed_algorithm_ids")
        optimality_path = algorithm_search_gate.get("optimality_audit_path")
        optimality_sha256 = algorithm_search_gate.get("optimality_audit_sha256")
        if (
            not isinstance(search_path, str)
            or not search_path
            or Path(search_path).is_absolute()
            or not isinstance(search_sha256, str)
            or SHA256_RE.fullmatch(search_sha256) is None
            or expected_actual is None
            or expected_maximum is None
            or production_maximum is None
            or expected_actual > production_maximum
            or production_maximum != max_algorithms
            or not isinstance(allowed_algorithms, list)
            or not allowed_algorithms
            or any(not isinstance(item, str) or not item for item in allowed_algorithms)
            or len(allowed_algorithms) != len(set(allowed_algorithms))
            or not isinstance(optimality_path, str)
            or not optimality_path
            or Path(optimality_path).is_absolute()
            or not isinstance(optimality_sha256, str)
            or SHA256_RE.fullmatch(optimality_sha256) is None
        ):
            raise ValueError("invalid frozen algorithm-search gate")
        if (
            algorithm_campaign_gate.get("required") is not True
            or not isinstance(algorithm_campaign_gate.get("contract"), Mapping)
            or "receipt" not in algorithm_campaign_gate
        ):
            raise ValueError("invalid frozen algorithm-campaign gate")
        runtime_path = runtime_decision_gate.get("runtime_policy_path")
        runtime_sha256 = runtime_decision_gate.get("runtime_policy_sha256")
        receipt_scope = runtime_decision_gate.get("receipt_scope")
        raw_scope = runtime_decision_gate.get("raw_evidence_scope")
        raw_windows = _positive_integer(
            runtime_decision_gate.get("minimum_raw_windows")
        )
        latency_samples = _positive_integer(
            runtime_decision_gate.get("minimum_latency_samples_per_window")
        )
        primary_backends = runtime_decision_gate.get(
            "production_primary_backends"
        )
        fallback_modes = runtime_decision_gate.get(
            "allowed_dpdk_fallback_modes"
        )
        operational_fields = runtime_decision_gate.get(
            "operational_metric_fields"
        )
        expected_operational_fields = {
            "throughput_mpps",
            "packet_drop_count",
            "p99_latency_us",
            "p999_latency_us",
            "cpu_utilization",
            "gpu_utilization",
            "memory_utilization",
            "gpu_memory_utilization",
            "budget_overrun_count",
            "key_flow_coverage",
            "fallback_recovery_s",
        }
        if (
            runtime_decision_gate.get("required") is not True
            or not isinstance(receipt_scope, str)
            or not receipt_scope
            or not isinstance(raw_scope, str)
            or not raw_scope
            or not isinstance(runtime_path, str)
            or not runtime_path
            or Path(runtime_path).is_absolute()
            or not isinstance(runtime_sha256, str)
            or SHA256_RE.fullmatch(runtime_sha256) is None
            or raw_windows is None
            or latency_samples is None
            or not isinstance(primary_backends, list)
            or not primary_backends
            or any(not isinstance(item, str) or not item for item in primary_backends)
            or len(primary_backends) != len(set(primary_backends))
            or not isinstance(fallback_modes, list)
            or not fallback_modes
            or any(not isinstance(item, str) or not item for item in fallback_modes)
            or len(fallback_modes) != len(set(fallback_modes))
            or runtime_decision_gate.get("canonical_selected_backend")
            != NATIVE_XDP_BACKEND
            or runtime_decision_gate.get("required_primary_action") != "keep_xdp"
            or runtime_decision_gate.get("require_qualified_dpdk_standby") is not True
            or runtime_decision_gate.get("standalone_dpdk_primary_allowed") is not False
            or not isinstance(operational_fields, list)
            or set(operational_fields) != expected_operational_fields
            or len(operational_fields) != len(expected_operational_fields)
        ):
            raise ValueError("invalid frozen runtime-decision gate")
        expected_candidate_evidence_gate = {
            "unified_audit_scope": "hft_mgbs_unified_candidate_evidence_audit",
            "candidate_receipt_scope": "sealed_unified_candidate_evidence_receipt",
            "candidate_evidence_accepted_required": True,
            "full_pipeline_qualified_required": True,
            "pareto_ingestion_allowed_required": True,
            "unified_production_release_must_be_false": True,
            "unified_selection_performed_must_be_false": True,
        }
        if dict(candidate_evidence_gate) != expected_candidate_evidence_gate:
            raise ValueError("invalid unified candidate-evidence gate")
        return cls(
            policy_id=policy_id,
            min_joint_candidates=min_joint,
            max_joint_candidates=max_joint,
            max_algorithm_candidates=max_algorithms,
            minimum_measured_repeats=repeats,
            required_evidence=tuple(required),
            hard_constraints=parsed_constraints,
            objectives=parsed_objectives,
            weights=parsed_weights,
            rejected_production_backends=tuple(rejected_backends),
            equal_capability_backend_priority=tuple(backend_priority),
            algorithm_search_gate={
                "path": search_path,
                "sha256": search_sha256,
                "expected_actual_candidates": expected_actual,
                "expected_maximum_candidates": expected_maximum,
                "production_admission_maximum_candidates": production_maximum,
                "allowed_algorithm_ids": tuple(allowed_algorithms),
                "optimality_audit_path": optimality_path,
                "optimality_audit_sha256": optimality_sha256,
            },
            algorithm_campaign_gate=dict(algorithm_campaign_gate),
            runtime_decision_gate={
                "receipt_scope": receipt_scope,
                "raw_evidence_scope": raw_scope,
                "runtime_policy_path": runtime_path,
                "runtime_policy_sha256": runtime_sha256,
                "minimum_raw_windows": raw_windows,
                "minimum_latency_samples_per_window": latency_samples,
                "production_primary_backends": tuple(primary_backends),
                "canonical_selected_backend": NATIVE_XDP_BACKEND,
                "required_primary_action": "keep_xdp",
                "require_qualified_dpdk_standby": True,
                "allowed_dpdk_fallback_modes": tuple(fallback_modes),
                "standalone_dpdk_primary_allowed": False,
                "operational_metric_fields": tuple(operational_fields),
            },
            candidate_evidence_gate=dict(expected_candidate_evidence_gate),
        )


@dataclass(frozen=True)
class JointCandidate:
    candidate_id: str
    algorithm_id: str
    metrics: Mapping[str, float]
    backend: str
    runtime_evidence: Mapping[str, Any]


@dataclass(frozen=True)
class ProductionCandidateAudit:
    candidate_id: str
    algorithm_id: str
    admitted_to_pareto: bool
    decision_stage: str
    reasons: Tuple[EliminationReason, ...]
    dominated_by: Tuple[str, ...] = ()
    objective_values: Optional[Mapping[str, float]] = None
    champion_score: Optional[float] = None
    backend: Optional[str] = None
    runtime_evidence: Optional[Mapping[str, Any]] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "algorithm_id": self.algorithm_id,
            "admitted_to_pareto": self.admitted_to_pareto,
            "decision_stage": self.decision_stage,
            "reasons": [reason.as_dict() for reason in self.reasons],
            "dominated_by": list(self.dominated_by),
            "objective_values": self.objective_values,
            "champion_score": self.champion_score,
            "backend": self.backend,
            "runtime_evidence": self.runtime_evidence,
        }


@dataclass(frozen=True)
class ProductionParetoSelection:
    policy_id: str
    candidate_count: int
    algorithm_candidate_count: int
    global_errors: Tuple[str, ...]
    audits: Tuple[ProductionCandidateAudit, ...]
    pareto_front_ids: Tuple[str, ...]
    champion_id: Optional[str]
    champion_score: Optional[float]

    def audit_by_id(self, candidate_id: str) -> ProductionCandidateAudit:
        return next(
            audit for audit in self.audits if audit.candidate_id == candidate_id
        )

    def as_dict(self) -> Dict[str, Any]:
        production_release_accepted = self.champion_id is not None
        return {
            "schema_version": 1,
            "scope": "sealed_production_joint_pareto_release",
            "policy_id": self.policy_id,
            "candidate_count": self.candidate_count,
            "algorithm_candidate_count": self.algorithm_candidate_count,
            "global_errors": list(self.global_errors),
            "hard_constraints_applied_before_pareto": True,
            "single_metric_selection_allowed": False,
            "pareto_front_ids": list(self.pareto_front_ids),
            "champion_id": self.champion_id,
            "selected_candidate": self.champion_id,
            "champion_score": self.champion_score,
            "selection_performed": True,
            "selection_qualified": production_release_accepted,
            "production_joint_optimum_proven": production_release_accepted,
            "production_release_accepted": production_release_accepted,
            "accepted": production_release_accepted,
            "final_pareto_eligible": production_release_accepted,
            "final_pareto_ingestion_allowed": production_release_accepted,
            "audits": [audit.as_dict() for audit in self.audits],
        }


def _positive_integer(value: Any) -> Optional[int]:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        return None
    return value


def _finite_number(value: Any) -> Optional[float]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    converted = float(value)
    return converted if math.isfinite(converted) else None


def _same_number(left: Any, right: Any) -> bool:
    left_number = _finite_number(left)
    right_number = _finite_number(right)
    return (
        left_number is not None
        and right_number is not None
        and math.isclose(left_number, right_number, rel_tol=1e-12, abs_tol=1e-12)
    )


class FinalParetoSelector:
    """Apply evidence and operational gates before multi-objective selection."""

    def __init__(
        self,
        policy: SelectionPolicy,
        artifact_root: Optional[Path] = None,
        policy_artifact_root: Optional[Path] = None,
        algorithm_receipt_root: Optional[Path] = None,
    ) -> None:
        self.policy = policy
        self.artifact_root = (
            None if artifact_root is None else artifact_root.resolve()
        )
        self.policy_artifact_root = (
            None
            if policy_artifact_root is None
            else policy_artifact_root.resolve()
        )
        self.algorithm_receipt_root = (
            None
            if algorithm_receipt_root is None
            else algorithm_receipt_root.resolve()
        )
        runtime_errors, runtime_policy = self._audit_runtime_policy()
        self.runtime_policy = runtime_policy
        campaign_errors, algorithm_campaign = self._audit_algorithm_campaign()
        self.algorithm_campaign = algorithm_campaign
        self.policy_errors = (
            self._audit_algorithm_search()
            + self._audit_algorithm_optimality(
                require_legacy_acceptance=algorithm_campaign.get("qualified") is not True
            )
            + campaign_errors
            + runtime_errors
        )

    def _audit_algorithm_campaign(self) -> Tuple[Tuple[str, ...], Mapping[str, Any]]:
        if self.policy_artifact_root is None:
            return (
                ("algorithm_campaign.policy_artifact_root_missing",),
                {"qualified": False, "winner": None},
            )
        result = verify_algorithm_campaign_gate(
            self.policy_artifact_root.parent,
            self.policy.algorithm_campaign_gate,
            reference_base=self.policy_artifact_root,
            remote_artifact_root=self.algorithm_receipt_root,
        )
        errors = list(result["errors"])
        allowed = tuple(self.policy.algorithm_search_gate["allowed_algorithm_ids"])
        if result["qualified"] is True and result.get("winner") not in allowed:
            errors.append("algorithm_campaign.winner")
        return tuple(dict.fromkeys(errors)), result

    def _audit_runtime_policy(
        self,
    ) -> Tuple[Tuple[str, ...], Optional[Mapping[str, Any]]]:
        gate = self.policy.runtime_decision_gate
        if self.policy_artifact_root is None:
            return ("runtime_decision.policy_artifact_root_missing",), None
        path = (
            self.policy_artifact_root / str(gate["runtime_policy_path"])
        ).resolve()
        try:
            path.relative_to(self.policy_artifact_root)
        except ValueError:
            return ("runtime_decision.policy_path_escape",), None
        if not path.is_file() or path.is_symlink():
            return ("runtime_decision.policy_file",), None
        payload_bytes = path.read_bytes()
        errors = []
        if hashlib.sha256(payload_bytes).hexdigest() != gate["runtime_policy_sha256"]:
            errors.append("runtime_decision.policy_sha256")
        try:
            payload = json.loads(
                payload_bytes.decode("utf-8"),
                parse_constant=lambda value: (_ for _ in ()).throw(
                    ValueError("non-finite JSON constant: " + value)
                ),
            )
        except (UnicodeDecodeError, ValueError, json.JSONDecodeError):
            return tuple(errors + ["runtime_decision.policy_json"]), None
        if not isinstance(payload, Mapping):
            return tuple(errors + ["runtime_decision.policy_schema"]), None
        return tuple(errors), payload

    def _audit_algorithm_search(self) -> Tuple[str, ...]:
        gate = self.policy.algorithm_search_gate
        if self.policy_artifact_root is None:
            return ("algorithm_search.policy_artifact_root_missing",)
        path = (self.policy_artifact_root / str(gate["path"])).resolve()
        try:
            path.relative_to(self.policy_artifact_root)
        except ValueError:
            return ("algorithm_search.path_escape",)
        if not path.is_file() or path.is_symlink():
            return ("algorithm_search.file",)
        payload_bytes = path.read_bytes()
        errors = []
        actual_sha256 = hashlib.sha256(payload_bytes).hexdigest()
        if actual_sha256 != gate["sha256"]:
            errors.append("algorithm_search.sha256")
        try:
            payload = json.loads(
                payload_bytes.decode("utf-8"),
                parse_constant=lambda value: (_ for _ in ()).throw(
                    ValueError("non-finite JSON constant: " + value)
                ),
            )
        except (UnicodeDecodeError, ValueError, json.JSONDecodeError):
            return tuple(errors + ["algorithm_search.json"])
        budget = payload.get("exploration_budget", {})
        candidates = payload.get("candidates")
        if budget.get("actual_candidates") != gate["expected_actual_candidates"]:
            errors.append("algorithm_search.actual_candidates")
        if budget.get("maximum_candidates") != gate["expected_maximum_candidates"]:
            errors.append("algorithm_search.maximum_candidates")
        if not isinstance(candidates, list) or len(candidates) != gate["expected_actual_candidates"]:
            errors.append("algorithm_search.candidate_count")
        elif len({item.get("id") for item in candidates if isinstance(item, Mapping)}) != len(candidates):
            errors.append("algorithm_search.duplicate_candidate_id")
        else:
            search_ids = {
                item.get("id") for item in candidates if isinstance(item, Mapping)
            }
            if not set(gate["allowed_algorithm_ids"]).issubset(search_ids):
                errors.append("algorithm_search.allowed_algorithm_ids")
            practical_front = payload.get("practical_front")
            if (
                not isinstance(practical_front, list)
                or not set(gate["allowed_algorithm_ids"]).issubset(
                    set(practical_front)
                )
            ):
                errors.append("algorithm_search.practical_front")
        if (
            gate["expected_actual_candidates"]
            > gate["production_admission_maximum_candidates"]
        ):
            errors.append("algorithm_search.production_admission_cap")
        return tuple(errors)

    def _audit_algorithm_optimality(
        self, *, require_legacy_acceptance: bool = True
    ) -> Tuple[str, ...]:
        gate = self.policy.algorithm_search_gate
        if self.policy_artifact_root is None:
            return ("algorithm_optimality.policy_artifact_root_missing",)
        project_root = self.policy_artifact_root.parent.resolve()
        path = (
            self.policy_artifact_root / str(gate["optimality_audit_path"])
        ).resolve()
        try:
            path.relative_to(project_root)
        except ValueError:
            return ("algorithm_optimality.path_escape",)
        if not path.is_file() or path.is_symlink():
            return ("algorithm_optimality.file",)
        payload_bytes = path.read_bytes()
        errors = []
        if hashlib.sha256(payload_bytes).hexdigest() != gate[
            "optimality_audit_sha256"
        ]:
            errors.append("algorithm_optimality.sha256")
        try:
            audit = json.loads(
                payload_bytes.decode("utf-8"),
                parse_constant=lambda value: (_ for _ in ()).throw(
                    ValueError("non-finite JSON constant: " + value)
                ),
            )
        except (UnicodeDecodeError, ValueError, json.JSONDecodeError):
            return tuple(errors + ["algorithm_optimality.json"])
        if not isinstance(audit, Mapping):
            return tuple(errors + ["algorithm_optimality.schema"])
        expected_scalar = {
            "schema_version": 1,
            "scope": "bounded_offline_algorithm_optimality_audit",
        }
        if require_legacy_acceptance:
            expected_scalar.update({
            "accepted": True,
            "algorithm_only_practical_optimum_proven": True,
            "errors": [],
            "actual_candidate_count": gate["expected_actual_candidates"],
            "confirmatory_metric_comparison_complete": True,
            "confirmatory_evidence_hash_complete": True,
            "evidence_hash_complete_candidate_count": gate[
                "expected_actual_candidates"
            ],
            "paired_metric_complete_candidate_count": gate[
                "expected_actual_candidates"
            ],
            })
        for name, expected in expected_scalar.items():
            if audit.get(name) != expected:
                errors.append("algorithm_optimality." + name)
        # This gate proves only bounded algorithm-side optimality.  Joint
        # production optimality and final ingestion are deliberately decided
        # later from runtime/data-plane evidence and therefore are not required
        # (and may correctly remain false) in the algorithm audit.
        if require_legacy_acceptance:
            allowed = list(gate["allowed_algorithm_ids"])
            if len(allowed) != 1:
                errors.append("algorithm_optimality.single_winner_policy")
            else:
                winner = allowed[0]
                if audit.get("confirmatory_practical_winner") != winner:
                    errors.append("algorithm_optimality.selected_winner")
                if audit.get("confirmatory_practical_front") != [winner]:
                    errors.append("algorithm_optimality.confirmatory_practical_front")
                if audit.get("practical_front_recomputed_from_available_metrics") != [
                    winner
                ]:
                    errors.append("algorithm_optimality.recomputed_practical_front")
        search_path = (
            self.policy_artifact_root / str(gate["path"])
        ).resolve()
        try:
            search = json.loads(search_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, json.JSONDecodeError):
            search = None
        if not isinstance(search, Mapping) or audit.get("search_id") != search.get(
            "search_id"
        ):
            errors.append("algorithm_optimality.search_id")
        return tuple(dict.fromkeys(errors))

    def _read_receipt(
        self,
        record: Mapping[str, Any],
        candidate_id: str,
        algorithm_id: str,
        backend: str,
    ) -> Tuple[Optional[Mapping[str, Any]], Tuple[EliminationReason, ...]]:
        reference = record.get("candidate_evidence_receipt")
        if not isinstance(reference, Mapping):
            return None, (EliminationReason("candidate_evidence_receipt"),)
        raw_path = reference.get("path")
        expected_sha256 = reference.get("sha256")
        reasons = []
        if not isinstance(raw_path, str) or not raw_path:
            return None, (EliminationReason("candidate_evidence_receipt.path"),)
        path = Path(raw_path)
        if path.is_absolute():
            resolved = path.resolve()
        elif self.artifact_root is not None:
            resolved = (self.artifact_root / path).resolve()
        else:
            return None, (
                EliminationReason("candidate_evidence_receipt.path_not_absolute"),
            )
        if self.artifact_root is not None:
            try:
                resolved.relative_to(self.artifact_root)
            except ValueError:
                return None, (
                    EliminationReason("candidate_evidence_receipt.path_escape"),
                )
        if not resolved.is_file() or resolved.is_symlink():
            return None, (EliminationReason("candidate_evidence_receipt.file"),)
        payload_bytes = resolved.read_bytes()
        if len(payload_bytes) > 1024 * 1024:
            return None, (EliminationReason("candidate_evidence_receipt.size"),)
        actual_sha256 = hashlib.sha256(payload_bytes).hexdigest()
        if (
            not isinstance(expected_sha256, str)
            or SHA256_RE.fullmatch(expected_sha256) is None
            or actual_sha256 != expected_sha256
        ):
            reasons.append(
                EliminationReason(
                    "candidate_evidence_receipt.sha256",
                    actual=actual_sha256,
                    limit=expected_sha256,
                    relation="==",
                )
            )
        try:
            receipt = json.loads(
                payload_bytes.decode("utf-8"),
                parse_constant=lambda value: (_ for _ in ()).throw(
                    ValueError("non-finite JSON constant: " + value)
                ),
            )
        except (UnicodeDecodeError, ValueError, json.JSONDecodeError):
            reasons.append(EliminationReason("candidate_evidence_receipt.json"))
            return None, tuple(reasons)
        if not isinstance(receipt, Mapping):
            reasons.append(EliminationReason("candidate_evidence_receipt.schema"))
            return None, tuple(reasons)
        expected_fields = {
            "schema_version": 1,
            "scope": self.policy.candidate_evidence_gate[
                "candidate_receipt_scope"
            ],
            "candidate_id": candidate_id,
            "algorithm_id": algorithm_id,
            "backend": backend,
            "candidate_evidence_accepted": True,
            "production_release_accepted": False,
            "selection_performed": False,
            "final_pareto_ingestion_allowed": True,
            "fallback_qualified": True,
            "restoration_verified": True,
            "algorithm_search_sha256": self.policy.algorithm_search_gate[
                "sha256"
            ],
        }
        for name, expected in expected_fields.items():
            if receipt.get(name) != expected:
                reasons.append(
                    EliminationReason(
                        "candidate_evidence_receipt." + name,
                        actual=receipt.get(name),
                        limit=expected,
                        relation="==",
                    )
                )
        for name in ("code_sha256", "input_sha256", "evidence_manifest_sha256"):
            if receipt.get(name) != record.get(name):
                reasons.append(
                    EliminationReason(
                        "candidate_evidence_receipt." + name,
                        actual=receipt.get(name),
                        limit=record.get(name),
                        relation="==",
                    )
                )
        runtime_reference = record.get("runtime_decision_receipt")
        runtime_expected = (
            runtime_reference.get("sha256")
            if isinstance(runtime_reference, Mapping)
            else None
        )
        if receipt.get("runtime_decision_receipt_sha256") != runtime_expected:
            reasons.append(
                EliminationReason(
                    "candidate_evidence_receipt.runtime_decision_receipt_sha256",
                    actual=receipt.get("runtime_decision_receipt_sha256"),
                    limit=runtime_expected,
                    relation="==",
                )
            )
        receipt_evidence = receipt.get("evidence")
        if receipt_evidence != record.get("evidence"):
            reasons.append(EliminationReason("candidate_evidence_receipt.evidence"))
        if receipt.get("metrics") != record.get("metrics"):
            reasons.append(EliminationReason("candidate_evidence_receipt.metrics"))
        if receipt.get("manifest_status") != record.get("manifest_status"):
            reasons.append(EliminationReason("candidate_evidence_receipt.manifest_status"))
        if receipt.get("measured_repeats") != record.get("measured_repeats"):
            reasons.append(EliminationReason("candidate_evidence_receipt.measured_repeats"))
        run_ids = receipt.get("measured_run_ids")
        record_repeats = record.get("measured_repeats")
        if (
            not isinstance(run_ids, list)
            or any(not isinstance(run_id, str) or not run_id for run_id in run_ids)
            or len(run_ids) != len(set(run_ids))
            or len(run_ids) < self.policy.minimum_measured_repeats
            or len(run_ids) != record_repeats
        ):
            reasons.append(
                EliminationReason(
                    "candidate_evidence_receipt.independent_run_ids",
                    actual=run_ids,
                    limit=self.policy.minimum_measured_repeats,
                    relation=">= unique",
                )
            )
        return receipt, tuple(reasons)

    def _read_bound_json(
        self,
        reference: Any,
        code: str,
        *,
        maximum_size: int,
    ) -> Tuple[Optional[Mapping[str, Any]], Tuple[EliminationReason, ...], Optional[str]]:
        if not isinstance(reference, Mapping):
            return None, (EliminationReason(code),), None
        raw_path = reference.get("path")
        expected_sha256 = reference.get("sha256")
        if not isinstance(raw_path, str) or not raw_path:
            return None, (EliminationReason(code + ".path"),), None
        path = Path(raw_path)
        if path.is_absolute():
            resolved = path.resolve()
        elif self.artifact_root is not None:
            resolved = (self.artifact_root / path).resolve()
        else:
            return None, (EliminationReason(code + ".path_not_absolute"),), None
        if self.artifact_root is not None:
            try:
                resolved.relative_to(self.artifact_root)
            except ValueError:
                return None, (EliminationReason(code + ".path_escape"),), None
        if not resolved.is_file() or resolved.is_symlink():
            return None, (EliminationReason(code + ".file"),), None
        payload_bytes = resolved.read_bytes()
        if len(payload_bytes) > maximum_size:
            return None, (EliminationReason(code + ".size"),), None
        actual_sha256 = hashlib.sha256(payload_bytes).hexdigest()
        reasons = []
        if (
            not isinstance(expected_sha256, str)
            or SHA256_RE.fullmatch(expected_sha256) is None
            or actual_sha256 != expected_sha256
        ):
            reasons.append(
                EliminationReason(
                    code + ".sha256",
                    actual=actual_sha256,
                    limit=expected_sha256,
                    relation="==",
                )
            )
        try:
            payload = json.loads(
                payload_bytes.decode("utf-8"),
                parse_constant=lambda value: (_ for _ in ()).throw(
                    ValueError("non-finite JSON constant: " + value)
                ),
            )
        except (UnicodeDecodeError, ValueError, json.JSONDecodeError):
            return None, tuple(reasons + [EliminationReason(code + ".json")]), actual_sha256
        if not isinstance(payload, Mapping):
            return None, tuple(reasons + [EliminationReason(code + ".schema")]), actual_sha256
        return payload, tuple(reasons), actual_sha256

    @staticmethod
    def _nearest_rank(values: Sequence[float], quantile: float) -> float:
        ordered = sorted(values)
        return ordered[max(0, math.ceil(quantile * len(ordered)) - 1)]

    def _recompute_runtime_metrics(
        self,
        raw: Mapping[str, Any],
        observation: Mapping[str, Any],
        candidate_id: str,
        backend: str,
        observation_sha256: str,
        measured_repeats: Any,
    ) -> Tuple[Optional[Mapping[str, float]], Tuple[EliminationReason, ...]]:
        gate = self.policy.runtime_decision_gate
        reasons = []
        if raw.get("schema_version") != 1:
            reasons.append(EliminationReason("runtime_raw.schema_version"))
        if raw.get("scope") != gate["raw_evidence_scope"]:
            reasons.append(EliminationReason("runtime_raw.scope"))
        if raw.get("candidate_id") != candidate_id:
            reasons.append(EliminationReason("runtime_raw.candidate_id"))
        if raw.get("backend") != backend:
            reasons.append(EliminationReason("runtime_raw.backend"))
        if raw.get("observation_sha256") != observation_sha256:
            reasons.append(EliminationReason("runtime_raw.observation_sha256"))
        windows = raw.get("windows")
        observed_windows = observation.get("online_windows")
        if not isinstance(windows, list):
            return None, tuple(reasons + [EliminationReason("runtime_raw.windows")])
        if not isinstance(observed_windows, list):
            return None, tuple(reasons + [EliminationReason("runtime_raw.observation_windows")])
        if (
            len(windows) < gate["minimum_raw_windows"]
            or len(windows) != len(observed_windows)
            or len(windows) != measured_repeats
        ):
            return None, tuple(
                reasons
                + [
                    EliminationReason(
                        "runtime_raw.window_count",
                        actual=len(windows),
                        limit={
                            "minimum": gate["minimum_raw_windows"],
                            "observation_windows": len(observed_windows),
                            "measured_repeats": measured_repeats,
                        },
                        relation="== and >=",
                    )
                ]
            )

        run_ids = []
        throughputs = []
        drops = 0
        p99_values = []
        p999_values = []
        resources = {
            "cpu_utilization": [],
            "gpu_utilization": [],
            "memory_utilization": [],
            "gpu_memory_utilization": [],
        }
        resource_fields = {
            "cpu_utilization": "host_cpu_samples_fraction",
            "gpu_utilization": "gpu_samples_fraction",
            "memory_utilization": "memory_samples_fraction",
            "gpu_memory_utilization": "gpu_memory_samples_fraction",
        }
        overruns = 0
        coverages = []
        recoveries = []
        capabilities = observation.get("capabilities")
        dpdk_capability = (
            capabilities.get("dpdk") if isinstance(capabilities, Mapping) else None
        )
        topology = (
            dpdk_capability.get("topology")
            if isinstance(dpdk_capability, Mapping)
            else None
        )
        expected_fallback_mode = {
            "dedicated_standby_adapter": "dedicated_standby_adapter",
            "same_pf_rebind": "maintenance",
            "same_adapter_all_pf_rebind": "maintenance",
        }.get(topology)
        if expected_fallback_mode is None:
            reasons.append(
                EliminationReason(
                    "runtime_raw.dpdk_fallback_topology",
                    actual=topology,
                    limit=[
                        "dedicated_standby_adapter",
                        "same_pf_rebind",
                        "same_adapter_all_pf_rebind",
                    ],
                    relation="in",
                )
            )
        for index, (window, observed) in enumerate(zip(windows, observed_windows)):
            prefix = f"runtime_raw.windows[{index}]"
            if not isinstance(window, Mapping) or not isinstance(observed, Mapping):
                reasons.append(EliminationReason(prefix))
                continue
            run_id = window.get("run_id")
            if not isinstance(run_id, str) or not run_id:
                reasons.append(EliminationReason(prefix + ".run_id"))
            else:
                run_ids.append(run_id)
            for name in ("start_utc", "end_utc", "capture_backend"):
                if window.get(name) != observed.get(name):
                    reasons.append(EliminationReason(prefix + "." + name))
            try:
                start = datetime.fromisoformat(
                    str(window.get("start_utc")).replace("Z", "+00:00")
                )
                end = datetime.fromisoformat(
                    str(window.get("end_utc")).replace("Z", "+00:00")
                )
                duration_s = (end - start).total_seconds()
            except (TypeError, ValueError):
                duration_s = 0.0
            if duration_s <= 0:
                reasons.append(EliminationReason(prefix + ".duration"))
            received = window.get("packets_received")
            dropped = window.get("packets_dropped")
            offered = window.get("packets_offered")
            if (
                isinstance(received, bool)
                or not isinstance(received, int)
                or received <= 0
                or isinstance(dropped, bool)
                or not isinstance(dropped, int)
                or dropped < 0
                or isinstance(offered, bool)
                or not isinstance(offered, int)
                or offered != received + dropped
            ):
                reasons.append(EliminationReason(prefix + ".packet_counters"))
            else:
                if received != observed.get("packets_received") or dropped != observed.get("packets_dropped"):
                    reasons.append(EliminationReason(prefix + ".observation_packet_counters"))
                if duration_s > 0:
                    throughputs.append(received / duration_s / 1_000_000.0)
                drops += dropped
            latency = window.get("latency_samples_us")
            if (
                not isinstance(latency, list)
                or len(latency) < gate["minimum_latency_samples_per_window"]
            ):
                reasons.append(EliminationReason(prefix + ".latency_samples_us"))
            else:
                parsed_latency = [_finite_number(value) for value in latency]
                if any(value is None or value < 0 for value in parsed_latency):
                    reasons.append(EliminationReason(prefix + ".latency_samples_us"))
                else:
                    finite_latency = [float(value) for value in parsed_latency if value is not None]
                    p99 = self._nearest_rank(finite_latency, 0.99)
                    p999 = self._nearest_rank(finite_latency, 0.999)
                    p99_values.append(p99)
                    p999_values.append(p999)
                    if not _same_number(p99, observed.get("kernel_to_feature_p99_us")):
                        reasons.append(EliminationReason(prefix + ".observation_p99"))
                    if not _same_number(p999, observed.get("kernel_to_feature_p999_us")):
                        reasons.append(EliminationReason(prefix + ".observation_p999"))
            for metric, field in resource_fields.items():
                samples = window.get(field)
                if not isinstance(samples, list) or not samples:
                    reasons.append(EliminationReason(prefix + "." + field))
                    continue
                parsed = [_finite_number(value) for value in samples]
                if any(value is None or not 0 <= value <= 1 for value in parsed):
                    reasons.append(EliminationReason(prefix + "." + field))
                    continue
                maximum = max(float(value) for value in parsed if value is not None)
                resources[metric].append(maximum)
                observed_field = {
                    "cpu_utilization": "host_cpu_fraction",
                    "memory_utilization": "memory_fraction",
                }.get(metric)
                if observed_field and not _same_number(maximum, observed.get(observed_field)):
                    reasons.append(EliminationReason(prefix + ".observation_" + observed_field))
            budget = window.get("budget_overrun_count")
            if isinstance(budget, bool) or not isinstance(budget, int) or budget < 0:
                reasons.append(EliminationReason(prefix + ".budget_overrun_count"))
            else:
                overruns += budget
                if budget != observed.get("budget_overrun_count"):
                    reasons.append(EliminationReason(prefix + ".observation_budget_overrun_count"))
            total = window.get("key_flow_total")
            covered = window.get("key_flow_covered")
            if (
                isinstance(total, bool)
                or not isinstance(total, int)
                or total <= 0
                or isinstance(covered, bool)
                or not isinstance(covered, int)
                or covered < 0
                or covered > total
            ):
                reasons.append(EliminationReason(prefix + ".key_flow_counters"))
            else:
                coverage = covered / total
                coverages.append(coverage)
                if total != observed.get("key_flow_total") or covered != observed.get("key_flow_covered"):
                    reasons.append(EliminationReason(prefix + ".observation_key_flow_counters"))
                if not _same_number(coverage, observed.get("key_flow_coverage")):
                    reasons.append(EliminationReason(prefix + ".observation_key_flow_coverage"))
            start_ns = window.get("fallback_started_monotonic_ns")
            ready_ns = window.get("fallback_ready_monotonic_ns")
            if (
                isinstance(start_ns, bool)
                or not isinstance(start_ns, int)
                or start_ns < 0
                or isinstance(ready_ns, bool)
                or not isinstance(ready_ns, int)
                or ready_ns <= start_ns
            ):
                reasons.append(EliminationReason(prefix + ".fallback_timestamps"))
            else:
                recovery_s = (ready_ns - start_ns) / 1_000_000_000.0
                recoveries.append(recovery_s)
                if not _same_number(recovery_s * 1000.0, observed.get("fallback_recovery_ms")):
                    reasons.append(EliminationReason(prefix + ".observation_fallback_recovery_ms"))
            if window.get("fallback_target_backend") != DPDK_BACKEND:
                reasons.append(EliminationReason(prefix + ".fallback_target_backend"))
            if window.get("fallback_mode") not in gate["allowed_dpdk_fallback_modes"]:
                reasons.append(EliminationReason(prefix + ".fallback_mode"))
            if (
                expected_fallback_mode is not None
                and window.get("fallback_mode") != expected_fallback_mode
            ):
                reasons.append(
                    EliminationReason(prefix + ".fallback_mode_topology_mismatch")
                )
            if window.get("restoration_verified") is not True:
                reasons.append(EliminationReason(prefix + ".restoration_verified"))
        if len(run_ids) != len(windows) or len(run_ids) != len(set(run_ids)):
            reasons.append(EliminationReason("runtime_raw.independent_run_ids"))
        if reasons:
            return None, tuple(_deduplicate_reasons(reasons))
        metrics = {
            "throughput_mpps": min(throughputs),
            "packet_drop_count": float(drops),
            "p99_latency_us": max(p99_values),
            "p999_latency_us": max(p999_values),
            "cpu_utilization": max(resources["cpu_utilization"]),
            "gpu_utilization": max(resources["gpu_utilization"]),
            "memory_utilization": max(resources["memory_utilization"]),
            "gpu_memory_utilization": max(resources["gpu_memory_utilization"]),
            "budget_overrun_count": float(overruns),
            "key_flow_coverage": min(coverages),
            "fallback_recovery_s": max(recoveries),
        }
        return metrics, ()

    def _read_runtime_decision_receipt(
        self,
        record: Mapping[str, Any],
        candidate_id: str,
        backend: str,
        metrics: Mapping[str, Any],
    ) -> Tuple[Optional[Mapping[str, float]], Tuple[EliminationReason, ...]]:
        gate = self.policy.runtime_decision_gate
        receipt, reasons, _ = self._read_bound_json(
            record.get("runtime_decision_receipt"),
            "runtime_decision_receipt",
            maximum_size=4 * 1024 * 1024,
        )
        if receipt is None:
            return None, reasons
        collected = list(reasons)
        if receipt.get("schema_version") != 1:
            collected.append(EliminationReason("runtime_decision_receipt.schema_version"))
        if receipt.get("receipt_scope") != gate["receipt_scope"]:
            collected.append(EliminationReason("runtime_decision_receipt.scope"))
        if receipt.get("runtime_policy_sha256") != gate["runtime_policy_sha256"]:
            collected.append(EliminationReason("runtime_decision_receipt.runtime_policy_sha256"))
        if receipt.get("release_qualification") is not False:
            collected.append(EliminationReason("runtime_decision_receipt.release_boundary"))
        if receipt.get("pareto_metrics_must_be_recomputed_from_raw") is not True:
            collected.append(EliminationReason("runtime_decision_receipt.raw_recomputation"))
        observation, observation_reasons, observation_sha256 = self._read_bound_json(
            receipt.get("observation_artifact"),
            "runtime_decision_receipt.observation",
            maximum_size=8 * 1024 * 1024,
        )
        collected.extend(observation_reasons)
        raw, raw_reasons, _ = self._read_bound_json(
            receipt.get("raw_runtime_evidence"),
            "runtime_decision_receipt.raw",
            maximum_size=64 * 1024 * 1024,
        )
        collected.extend(raw_reasons)
        if isinstance(receipt.get("observation_artifact"), Mapping):
            if receipt.get("observation_sha256") != receipt[
                "observation_artifact"
            ].get("sha256"):
                collected.append(EliminationReason("runtime_decision_receipt.observation_sha256"))
        if isinstance(receipt.get("raw_runtime_evidence"), Mapping):
            if receipt.get("raw_runtime_evidence_sha256") != receipt[
                "raw_runtime_evidence"
            ].get("sha256"):
                collected.append(EliminationReason("runtime_decision_receipt.raw_sha256"))
        if self.runtime_policy is None or observation is None:
            return None, tuple(_deduplicate_reasons(collected))
        canonical_observation_sha256 = hashlib.sha256(
            json.dumps(
                observation,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        if receipt.get("observation_canonical_sha256") != canonical_observation_sha256:
            collected.append(
                EliminationReason("runtime_decision_receipt.observation_canonical_sha256")
            )
        canonical_policy_sha256 = hashlib.sha256(
            json.dumps(
                self.runtime_policy,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        if receipt.get("runtime_policy_canonical_sha256") != canonical_policy_sha256:
            collected.append(
                EliminationReason("runtime_decision_receipt.policy_canonical_sha256")
            )
        decision_at = receipt.get("decision_at_utc")
        try:
            decision_time = datetime.fromisoformat(
                str(decision_at).replace("Z", "+00:00")
            )
            if decision_time.tzinfo is None:
                raise ValueError("timezone missing")
            replay = evaluate_runtime_decision(
                self.runtime_policy, observation, now=decision_time
            )
        except (ValueError, RuntimeDecisionContractError):
            collected.append(EliminationReason("runtime_decision_receipt.replay"))
            replay = None
        if replay is not None:
            for name, expected in replay.items():
                if receipt.get(name) != expected:
                    collected.append(
                        EliminationReason("runtime_decision_receipt.decision." + name)
                    )
        if backend not in gate["production_primary_backends"]:
            collected.append(
                EliminationReason(
                    "runtime_decision.dpdk_primary_forbidden"
                    if backend == "dpdk"
                    else "runtime_decision.primary_backend",
                    actual=backend,
                    limit=list(gate["production_primary_backends"]),
                    relation="in",
                )
            )
        expected_decision = {
            "action": gate["required_primary_action"],
            "current_backend": gate["canonical_selected_backend"],
            "selected_backend": gate["canonical_selected_backend"],
            "transition_permitted": False,
            "production_backend_available": True,
        }
        for name, expected in expected_decision.items():
            if receipt.get(name) != expected:
                collected.append(
                    EliminationReason(
                        "runtime_decision." + name,
                        actual=receipt.get(name),
                        limit=expected,
                        relation="==",
                    )
                )
        xdp = receipt.get("xdp_capability")
        online = receipt.get("online_gates")
        dpdk = receipt.get("dpdk_capability")
        if not isinstance(xdp, Mapping) or any(
            xdp.get(name) is not True
            for name in ("eligible", "native_verified", "zerocopy_verified")
        ):
            collected.append(EliminationReason("runtime_decision.xdp_fully_qualified"))
        if not isinstance(online, Mapping) or any(
            online.get(name) is not True
            for name in (
                "capture_gate_qualified",
                "key_flow_gate_qualified",
                "runtime_safety_gate_qualified",
            )
        ):
            collected.append(EliminationReason("runtime_decision.online_gates"))
        if not isinstance(dpdk, Mapping) or dpdk.get("eligible") is not True:
            collected.append(EliminationReason("runtime_decision.dpdk_standby_qualified"))
        if raw is None or observation_sha256 is None:
            return None, tuple(_deduplicate_reasons(collected))
        derived, derived_reasons = self._recompute_runtime_metrics(
            raw,
            observation,
            candidate_id,
            backend,
            observation_sha256,
            record.get("measured_repeats"),
        )
        collected.extend(derived_reasons)
        if derived is not None:
            for name in gate["operational_metric_fields"]:
                if not _same_number(derived.get(name), metrics.get(name)):
                    collected.append(
                        EliminationReason(
                            "runtime_raw.metrics." + name,
                            actual=derived.get(name),
                            limit=metrics.get(name),
                            relation="==",
                        )
                    )
        if collected:
            return derived, tuple(_deduplicate_reasons(collected))
        return derived, ()

    def _read_unified_audit(
        self,
        record: Mapping[str, Any],
        candidate_id: str,
        metrics: Mapping[str, Any],
    ) -> Tuple[Optional[Mapping[str, Any]], Tuple[EliminationReason, ...]]:
        reference = record.get("unified_candidate_evidence_audit")
        if not isinstance(reference, Mapping):
            return None, (EliminationReason("unified_candidate_evidence_audit"),)
        raw_path = reference.get("path")
        expected_sha256 = reference.get("sha256")
        if not isinstance(raw_path, str) or not raw_path:
            return None, (EliminationReason("unified_candidate_evidence_audit.path"),)
        path = Path(raw_path)
        if path.is_absolute():
            resolved = path.resolve()
        elif self.artifact_root is not None:
            resolved = (self.artifact_root / path).resolve()
        else:
            return None, (
                EliminationReason("unified_candidate_evidence_audit.path_not_absolute"),
            )
        if self.artifact_root is not None:
            try:
                resolved.relative_to(self.artifact_root)
            except ValueError:
                return None, (
                    EliminationReason("unified_candidate_evidence_audit.path_escape"),
                )
        if not resolved.is_file() or resolved.is_symlink():
            return None, (EliminationReason("unified_candidate_evidence_audit.file"),)
        payload_bytes = resolved.read_bytes()
        if len(payload_bytes) > 4 * 1024 * 1024:
            return None, (EliminationReason("unified_candidate_evidence_audit.size"),)
        actual_sha256 = hashlib.sha256(payload_bytes).hexdigest()
        reasons = []
        if (
            not isinstance(expected_sha256, str)
            or SHA256_RE.fullmatch(expected_sha256) is None
            or actual_sha256 != expected_sha256
        ):
            reasons.append(
                EliminationReason(
                    "unified_candidate_evidence_audit.sha256",
                    actual=actual_sha256,
                    limit=expected_sha256,
                    relation="==",
                )
            )
        try:
            audit = json.loads(
                payload_bytes.decode("utf-8"),
                parse_constant=lambda value: (_ for _ in ()).throw(
                    ValueError("non-finite JSON constant: " + value)
                ),
            )
        except (UnicodeDecodeError, ValueError, json.JSONDecodeError):
            return None, tuple(reasons + [EliminationReason("unified_candidate_evidence_audit.json")])
        if not isinstance(audit, Mapping):
            return None, tuple(reasons + [EliminationReason("unified_candidate_evidence_audit.schema")])
        expected = {
            "schema_version": 1,
            "scope": self.policy.candidate_evidence_gate["unified_audit_scope"],
            "candidate_id": candidate_id,
            "algorithm_id": record.get("algorithm_id"),
            "candidate_evidence_accepted": True,
            "accepted": False,
            "production_release_accepted": False,
            "selection_performed": False,
            "selected_candidate": None,
            "final_pareto_ingestion_allowed": True,
            "full_pipeline_qualified": True,
            "errors": [],
        }
        for name, value in expected.items():
            if audit.get(name) != value:
                reasons.append(
                    EliminationReason(
                        "unified_candidate_evidence_audit." + name,
                        actual=audit.get(name),
                        limit=value,
                        relation="==",
                    )
                )
        if audit.get("derived_production_pareto_metrics") != metrics:
            reasons.append(
                EliminationReason("unified_candidate_evidence_audit.metrics")
            )
        return audit, tuple(reasons)

    def _parse_candidate(
        self, record: Mapping[str, Any]
    ) -> Tuple[Optional[JointCandidate], Tuple[EliminationReason, ...], str, str]:
        reasons = []
        candidate_id = record.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id:
            candidate_id = "<invalid-candidate-id>"
            reasons.append(EliminationReason("candidate_id"))
        algorithm_id = record.get("algorithm_id", candidate_id)
        if not isinstance(algorithm_id, str) or not algorithm_id:
            algorithm_id = "<invalid-algorithm-id>"
            reasons.append(EliminationReason("algorithm_id"))
        backend = record.get("backend")
        if not isinstance(backend, str) or not backend:
            backend = "<invalid-backend>"
            reasons.append(EliminationReason("backend"))
        elif backend in self.policy.rejected_production_backends:
            reasons.append(
                EliminationReason(
                    "backend.production_capability",
                    actual=backend,
                    detail="backend is diagnostic-only in the frozen environment",
                )
            )
        if algorithm_id not in self.policy.algorithm_search_gate[
            "allowed_algorithm_ids"
        ]:
            reasons.append(
                EliminationReason(
                    "algorithm_id.production_admission",
                    actual=algorithm_id,
                    limit=list(
                        self.policy.algorithm_search_gate[
                            "allowed_algorithm_ids"
                        ]
                    ),
                    relation="in",
                )
            )

        metrics_raw = record.get("metrics")
        parsed_metrics: Dict[str, float] = {}
        if not isinstance(metrics_raw, Mapping):
            reasons.append(EliminationReason("metrics"))
        else:
            for name in METRIC_NAMES:
                value = _finite_number(metrics_raw.get(name))
                if value is None:
                    reasons.append(EliminationReason("metrics." + name))
                else:
                    parsed_metrics[name] = value
            if metrics_raw.get("name") != candidate_id:
                reasons.append(EliminationReason("metrics.name"))
            for name in ("packet_drop_count", "budget_overrun_count"):
                raw = metrics_raw.get(name)
                if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
                    reasons.append(EliminationReason("metrics." + name))
            for name in (
                "grouped_macro_f1",
                "independent_macro_f1",
                "independent_attack_recall",
                "independent_benign_recall",
                "independent_auprc",
                "independent_ece",
                "ground_truth_event_recall",
                "cpu_utilization",
                "gpu_utilization",
                "memory_utilization",
                "gpu_memory_utilization",
                "key_flow_coverage",
            ):
                value = parsed_metrics.get(name)
                if value is not None and not 0 <= value <= 1:
                    reasons.append(EliminationReason("metrics." + name))
            for name, value in parsed_metrics.items():
                if value < 0:
                    reasons.append(EliminationReason("metrics." + name))
            if (
                parsed_metrics.get("p999_latency_us") is not None
                and parsed_metrics.get("p99_latency_us") is not None
                and parsed_metrics["p999_latency_us"]
                < parsed_metrics["p99_latency_us"]
            ):
                reasons.append(EliminationReason("metrics.p999_below_p99"))

        evidence = record.get("evidence")
        if not isinstance(evidence, Mapping):
            reasons.append(EliminationReason("evidence"))
        else:
            for flag in self.policy.required_evidence:
                if evidence.get(flag) is not True:
                    reasons.append(EliminationReason("evidence." + flag))
            unknown = sorted(set(evidence) - set(self.policy.required_evidence))
            if unknown:
                reasons.append(
                    EliminationReason(
                        "evidence.unknown_flags", detail=",".join(unknown)
                    )
                )
        if record.get("manifest_status") != "complete":
            reasons.append(EliminationReason("manifest_status"))
        repeats = record.get("measured_repeats")
        if (
            isinstance(repeats, bool)
            or not isinstance(repeats, int)
            or repeats < self.policy.minimum_measured_repeats
        ):
            reasons.append(
                EliminationReason(
                    "measured_repeats",
                    actual=repeats,
                    limit=self.policy.minimum_measured_repeats,
                    relation=">=",
                )
            )
        for name in ("code_sha256", "input_sha256", "evidence_manifest_sha256"):
            value = record.get(name)
            if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
                reasons.append(EliminationReason(name, actual=value))
        for name in (
            "fallback_qualified",
            "restoration_verified",
            "final_pareto_ingestion_allowed",
        ):
            if record.get(name) is not True:
                reasons.append(EliminationReason(name, actual=record.get(name)))
        _receipt, receipt_reasons = self._read_receipt(
            record, candidate_id, algorithm_id, backend
        )
        reasons.extend(receipt_reasons)
        _runtime_metrics, runtime_reasons = self._read_runtime_decision_receipt(
            record,
            candidate_id,
            backend,
            metrics_raw if isinstance(metrics_raw, Mapping) else {},
        )
        reasons.extend(runtime_reasons)
        _audit, unified_reasons = self._read_unified_audit(
            record, candidate_id, metrics_raw if isinstance(metrics_raw, Mapping) else {}
        )
        reasons.extend(unified_reasons)
        if _receipt is not None and isinstance(record.get("unified_candidate_evidence_audit"), Mapping):
            if _receipt.get("unified_candidate_evidence_audit_sha256") != record[
                "unified_candidate_evidence_audit"
            ].get("sha256"):
                reasons.append(
                    EliminationReason(
                        "candidate_evidence_receipt.unified_candidate_evidence_audit_sha256"
                    )
                )
        if reasons:
            return None, tuple(_deduplicate_reasons(reasons)), candidate_id, algorithm_id
        runtime_reference = record["runtime_decision_receipt"]
        return (
            JointCandidate(
                candidate_id,
                algorithm_id,
                parsed_metrics,
                backend,
                {
                    "runtime_decision_receipt_sha256": runtime_reference["sha256"],
                    "runtime_policy_sha256": self.policy.runtime_decision_gate[
                        "runtime_policy_sha256"
                    ],
                    "receipt_rehashed": True,
                    "decision_replayed": True,
                    "metrics_recomputed_from_raw": True,
                    "derived_operational_metrics": dict(_runtime_metrics or {}),
                    "primary_backend": NATIVE_XDP_BACKEND,
                    "dpdk_role": "standby_or_maintenance_fallback_only",
                },
            ),
            (),
            candidate_id,
            algorithm_id,
        )

    def _hard_gate_reasons(
        self, candidate: JointCandidate
    ) -> Tuple[EliminationReason, ...]:
        reasons = []
        for metric, rule in self.policy.hard_constraints.items():
            actual = candidate.metrics[metric]
            limit = float(rule["limit"])
            relation = str(rule["relation"])
            failed = actual < limit if relation == ">=" else actual > limit
            if failed:
                reasons.append(
                    EliminationReason(metric, actual, limit, relation)
                )
        return tuple(reasons)

    def resource_pressure(self, candidate: JointCandidate) -> float:
        ratios = []
        for metric in (
            "cpu_utilization",
            "gpu_utilization",
            "memory_utilization",
            "gpu_memory_utilization",
        ):
            rule = self.policy.hard_constraints[metric]
            ratios.append(candidate.metrics[metric] / float(rule["limit"]))
        return max(ratios)

    def objective_value(self, candidate: JointCandidate, name: str) -> float:
        if name == "resource_pressure":
            return self.resource_pressure(candidate)
        return candidate.metrics[name]

    def dominates(self, left: JointCandidate, right: JointCandidate) -> bool:
        no_worse = True
        strictly_better = False
        for name, direction in self.policy.objectives.items():
            left_value = self.objective_value(left, name)
            right_value = self.objective_value(right, name)
            if direction == "max":
                no_worse = no_worse and left_value >= right_value
                strictly_better = strictly_better or left_value > right_value
            else:
                no_worse = no_worse and left_value <= right_value
                strictly_better = strictly_better or left_value < right_value
        return no_worse and strictly_better

    def _champion_scores(
        self, front: Sequence[JointCandidate]
    ) -> Mapping[str, float]:
        total_weight = sum(self.policy.weights.values())
        scores = {candidate.candidate_id: 0.0 for candidate in front}
        for name, direction in self.policy.objectives.items():
            values = [self.objective_value(candidate, name) for candidate in front]
            low, high = min(values), max(values)
            for candidate in front:
                value = self.objective_value(candidate, name)
                normalized = 1.0 if high == low else (value - low) / (high - low)
                benefit = normalized if direction == "max" else 1.0 - normalized
                scores[candidate.candidate_id] += (
                    self.policy.weights[name] * benefit / total_weight
                )
        return scores

    def _backend_rank(self, backend: str) -> int:
        try:
            return self.policy.equal_capability_backend_priority.index(backend)
        except ValueError:
            return len(self.policy.equal_capability_backend_priority)

    def select(
        self, records: Iterable[Mapping[str, Any]]
    ) -> ProductionParetoSelection:
        materialized = list(records)
        global_errors = list(self.policy_errors)
        if len(materialized) < self.policy.min_joint_candidates:
            global_errors.append(
                "candidate_count_below_min:{}<{}".format(
                    len(materialized), self.policy.min_joint_candidates
                )
            )
        if len(materialized) > self.policy.max_joint_candidates:
            global_errors.append(
                "candidate_count_exceeds_max:{}>{}".format(
                    len(materialized), self.policy.max_joint_candidates
                )
            )
        raw_ids = [repr(record.get("candidate_id")) for record in materialized]
        duplicate_ids = len(raw_ids) != len(set(raw_ids))
        if duplicate_ids:
            global_errors.append("duplicate_candidate_id")
        raw_algorithm_ids = [
            record.get("algorithm_id", record.get("candidate_id"))
            for record in materialized
        ]
        algorithm_count = len({repr(value) for value in raw_algorithm_ids})
        if algorithm_count > self.policy.max_algorithm_candidates:
            global_errors.append(
                "algorithm_candidate_count_exceeds_max:{}>{}".format(
                    algorithm_count, self.policy.max_algorithm_candidates
                )
            )
        # Duplicate IDs cannot be represented by the per-ID audit map. Other
        # global policy failures are retained while candidate-specific evidence
        # and hard-gate reasons are still computed below.
        if duplicate_ids:
            audits = tuple(
                ProductionCandidateAudit(
                    str(record.get("candidate_id", "<invalid-candidate-id>")),
                    str(
                        record.get(
                            "algorithm_id",
                            record.get("candidate_id", "<invalid-algorithm-id>"),
                        )
                    ),
                    False,
                    "global_policy",
                    tuple(EliminationReason(code) for code in global_errors),
                )
                for record in materialized
            )
            return ProductionParetoSelection(
                self.policy.policy_id,
                len(materialized),
                algorithm_count,
                tuple(global_errors),
                audits,
                (),
                None,
                None,
            )

        audits_by_id: Dict[str, ProductionCandidateAudit] = {}
        admitted = []
        for record in materialized:
            candidate, reasons, candidate_id, algorithm_id = self._parse_candidate(
                record
            )
            if candidate is None:
                audits_by_id[candidate_id] = ProductionCandidateAudit(
                    candidate_id,
                    algorithm_id,
                    False,
                    "evidence",
                    reasons,
                    backend=str(record.get("backend", "<invalid-backend>")),
                )
                continue
            hard_reasons = self._hard_gate_reasons(candidate)
            if hard_reasons:
                audits_by_id[candidate_id] = ProductionCandidateAudit(
                    candidate_id,
                    algorithm_id,
                    False,
                    "hard_constraint",
                    hard_reasons,
                    backend=candidate.backend,
                    runtime_evidence=candidate.runtime_evidence,
                )
                continue
            admitted.append(candidate)

        front = []
        for candidate in admitted:
            dominators = tuple(
                sorted(
                    other.candidate_id
                    for other in admitted
                    if other is not candidate and self.dominates(other, candidate)
                )
            )
            objective_values = {
                name: self.objective_value(candidate, name)
                for name in self.policy.objectives
            }
            if dominators:
                audits_by_id[candidate.candidate_id] = ProductionCandidateAudit(
                    candidate.candidate_id,
                    candidate.algorithm_id,
                    False,
                    "dominated",
                    (
                        EliminationReason(
                            "pareto_dominated",
                            detail="dominated_by=" + ",".join(dominators),
                        ),
                    ),
                    dominators,
                    objective_values,
                    backend=candidate.backend,
                    runtime_evidence=candidate.runtime_evidence,
                )
            else:
                front.append(candidate)

        if global_errors:
            for candidate in admitted:
                audits_by_id[candidate.candidate_id] = ProductionCandidateAudit(
                    candidate.candidate_id,
                    candidate.algorithm_id,
                    False,
                    "global_policy",
                    tuple(EliminationReason(code) for code in global_errors),
                    backend=candidate.backend,
                    runtime_evidence=candidate.runtime_evidence,
                )
            audits = tuple(
                audits_by_id[
                    str(record.get("candidate_id", "<invalid-candidate-id>"))
                ]
                for record in materialized
            )
            return ProductionParetoSelection(
                self.policy.policy_id,
                len(materialized),
                algorithm_count,
                tuple(global_errors),
                audits,
                (),
                None,
                None,
            )

        front.sort(key=lambda candidate: candidate.candidate_id)
        champion_id = None
        champion_score = None
        if front:
            scores = self._champion_scores(front)
            champion = sorted(
                front,
                key=lambda candidate: (
                    -scores[candidate.candidate_id],
                    self._backend_rank(candidate.backend),
                    candidate.candidate_id,
                ),
            )[0]
            champion_id = champion.candidate_id
            champion_score = scores[champion_id]
            for candidate in front:
                score = scores[candidate.candidate_id]
                is_champion = candidate.candidate_id == champion_id
                reasons = ()
                stage = "pareto_champion" if is_champion else "pareto_tradeoff"
                if not is_champion:
                    reasons = (
                        EliminationReason(
                            "lower_multiobjective_utility",
                            actual=score,
                            limit=champion_score,
                            relation="<=",
                            detail=(
                                "tie_break=backend_priority_only_for_exact_score_tie_then_"
                                "candidate_id_ascending"
                            ),
                        ),
                    )
                audits_by_id[candidate.candidate_id] = ProductionCandidateAudit(
                    candidate.candidate_id,
                    candidate.algorithm_id,
                    True,
                    stage,
                    reasons,
                    (),
                    {
                        name: self.objective_value(candidate, name)
                        for name in self.policy.objectives
                    },
                    score,
                    candidate.backend,
                    candidate.runtime_evidence,
                )

        audits = tuple(
            audits_by_id[str(record.get("candidate_id", "<invalid-candidate-id>"))]
            for record in materialized
        )
        return ProductionParetoSelection(
            self.policy.policy_id,
            len(materialized),
            algorithm_count,
            (),
            audits,
            tuple(candidate.candidate_id for candidate in front),
            champion_id,
            champion_score,
        )


def _deduplicate_reasons(
    reasons: Sequence[EliminationReason],
) -> Sequence[EliminationReason]:
    seen = set()
    result = []
    for reason in reasons:
        key = (reason.code, repr(reason.actual), repr(reason.limit), reason.relation, reason.detail)
        if key not in seen:
            seen.add(key)
            result.append(reason)
    return result
