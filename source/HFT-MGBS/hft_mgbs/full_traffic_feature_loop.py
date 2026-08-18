"""Backend-neutral full-traffic recognition and feature-extraction closure.

The high-speed Rust data plane remains responsible for live packet capture.
This module freezes the backend-independent method semantics used by the
reference implementation and by raw-runtime evidence audits:

* every successfully parsed packet receives a base recognition record;
* every observed flow emits one feature result, even when optional work is
  reduced to the base tier;
* flow/deep upgrades are selected by the measured-cost budget scheduler;
* a capture-backend transition never resets flow state or budget feedback;
* packet, recognition, flow and budget conservation are explicit receipts.

The current BCM57810 TPACKET_V3 backend is a service-continuity fallback.  It
can keep this method running, but its receipt must never claim the production
SLA of a future native AF_XDP or DPDK data plane.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Tuple

from .features import FlowKey, PacketRecord
from .pipeline import AdaptiveExtractionPipeline, PipelineResult
from .unified_feature_reservoir import (
    PacketMetadata,
    UnifiedFeatureReservoir,
    UnifiedFlowFeatureRecord,
    default_reservoir_policy,
)


POLICY_SCOPE = "hft_mgbs_full_traffic_feature_loop_policy_v1"
RECEIPT_SCOPE = "hft_mgbs_full_traffic_feature_loop_receipt_v1"
AUDIT_SCOPE = "hft_mgbs_high_speed_feature_loop_audit_v1"
FAILOVER_RECEIPT_SCOPE = "hft_mgbs_capture_runtime_failover_execution_receipt_v2"

NATIVE_XDP_BACKEND = "native_af_xdp_zerocopy"
DPDK_BACKEND = "dpdk"
CURRENT_HARDWARE_BACKEND = "current_tpacket_v3_bcm57810"
BACKENDS = (NATIVE_XDP_BACKEND, DPDK_BACKEND, CURRENT_HARDWARE_BACKEND)
PRODUCTION_BACKENDS = (NATIVE_XDP_BACKEND, DPDK_BACKEND)

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class FullTrafficFeatureLoopError(ValueError):
    """Raised when a batch, transition or receipt violates the frozen loop."""


@dataclass(frozen=True)
class CapturedPacketBatch:
    """One normalized batch delivered by any supported capture backend.

    ``packets`` contains the successfully parsed packets.  Rejected frames and
    capture drops remain in the denominator through their explicit counters.
    The sequence is local to one backend generation and starts at one.
    """

    backend: str
    generation: int
    batch_sequence: int
    packets: Tuple[PacketRecord, ...]
    parse_rejected: int = 0
    capture_dropped: int = 0
    source_id: str = "unspecified"
    packet_metadata: Tuple[PacketMetadata, ...] = ()


@dataclass(frozen=True)
class TrafficRecognition:
    packet_index: int
    flow_key: FlowKey
    protocol_class: str
    service_class: str
    payload_class: str
    canonical_direction: str
    is_key_flow: bool
    base_features: Mapping[str, float]


@dataclass(frozen=True)
class FullTrafficBatchResult:
    recognitions: Tuple[TrafficRecognition, ...]
    flow_results: Tuple[PipelineResult, ...]
    unified_flow_records: Tuple[UnifiedFlowFeatureRecord, ...]
    window_contexts: Tuple[Mapping[str, Any], ...]
    receipt: Mapping[str, Any]


_PROTOCOL_CLASSES = {
    1: "icmp",
    6: "tcp",
    17: "udp",
    47: "gre",
    50: "esp",
    51: "ah",
    58: "icmpv6",
    132: "sctp",
}

_SERVICE_CLASSES = {
    21: "ftp",
    22: "ssh",
    23: "telnet",
    25: "smtp",
    53: "dns",
    80: "http",
    110: "pop3",
    123: "ntp",
    143: "imap",
    443: "https",
    445: "smb",
    993: "imaps",
    995: "pop3s",
    3389: "rdp",
}


def _integer(value: Any, path: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise FullTrafficFeatureLoopError("{} must be an integer >= {}".format(path, minimum))
    return value


def _number(value: Any, path: str, minimum: float = 0.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise FullTrafficFeatureLoopError("{} must be numeric".format(path))
    result = float(value)
    if not math.isfinite(result) or result < minimum:
        raise FullTrafficFeatureLoopError("{} must be finite and >= {}".format(path, minimum))
    return result


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate_feature_loop_policy(policy: Mapping[str, Any]) -> None:
    expected = {
        "schema_version",
        "scope",
        "policy_id",
        "backend_priority",
        "production_backends",
        "current_hardware_fallback",
        "unified_feature_reservoir",
        "recognition",
        "extraction",
        "budget",
        "qualification_boundaries",
    }
    if set(policy) != expected:
        raise FullTrafficFeatureLoopError("feature-loop policy envelope is not exact")
    if policy.get("schema_version") != 1 or policy.get("scope") != POLICY_SCOPE:
        raise FullTrafficFeatureLoopError("feature-loop policy identity is invalid")
    if list(policy.get("backend_priority", ())) != list(BACKENDS):
        raise FullTrafficFeatureLoopError("backend priority is not frozen")
    if list(policy.get("production_backends", ())) != list(PRODUCTION_BACKENDS):
        raise FullTrafficFeatureLoopError("production backend set is not frozen")
    fallback = policy.get("current_hardware_fallback")
    if not isinstance(fallback, Mapping) or set(fallback) != {
        "backend",
        "role",
        "production_sla_eligible",
    }:
        raise FullTrafficFeatureLoopError("current-hardware fallback contract is invalid")
    if (
        fallback.get("backend") != CURRENT_HARDWARE_BACKEND
        or fallback.get("role") != "degraded_service_continuity_fallback"
        or fallback.get("production_sla_eligible") is not False
    ):
        raise FullTrafficFeatureLoopError("current hardware must remain a degraded fallback")

    reservoir = policy.get("unified_feature_reservoir")
    if reservoir != {
        "policy_id": "HFT_MGBS_UNIFIED_FEATURE_RESERVOIR_V1",
        "canonical_policy_sha256": "1da8b39dae34e0bd13b7ccc99712635f4d8fd859286335dc206b284b35d87a72",
        "required": True,
    }:
        raise FullTrafficFeatureLoopError("unified feature reservoir binding drifted")

    recognition = policy.get("recognition")
    if not isinstance(recognition, Mapping) or set(recognition) != {
        "all_parsed_packets_receive_base_features",
        "parse_rejects_remain_in_denominator",
        "protocol_classes",
        "common_service_ports",
    }:
        raise FullTrafficFeatureLoopError("recognition contract is invalid")
    if recognition.get("all_parsed_packets_receive_base_features") is not True:
        raise FullTrafficFeatureLoopError("base recognition must cover every parsed packet")
    if recognition.get("parse_rejects_remain_in_denominator") is not True:
        raise FullTrafficFeatureLoopError("parse rejects must remain in the denominator")
    if list(recognition.get("protocol_classes", ())) != sorted(
        set(_PROTOCOL_CLASSES.values()).union(("other",))
    ):
        raise FullTrafficFeatureLoopError("protocol-class set drifted")
    ports = recognition.get("common_service_ports")
    if list(ports or ()) != sorted(_SERVICE_CLASSES):
        raise FullTrafficFeatureLoopError("key-flow service-port set drifted")

    extraction = policy.get("extraction")
    if not isinstance(extraction, Mapping) or set(extraction) != {
        "tiers",
        "one_result_per_observed_flow",
        "deep_tier_optional",
        "max_deep_payload_bytes_per_flow",
    }:
        raise FullTrafficFeatureLoopError("extraction contract is invalid")
    if list(extraction.get("tiers", ())) != ["packet", "window", "flow", "deep"]:
        raise FullTrafficFeatureLoopError("feature tiers drifted")
    if extraction.get("one_result_per_observed_flow") is not True:
        raise FullTrafficFeatureLoopError("every observed flow must emit one result")
    if extraction.get("deep_tier_optional") is not True:
        raise FullTrafficFeatureLoopError("deep work must remain optional")
    _integer(
        extraction.get("max_deep_payload_bytes_per_flow"),
        "extraction.max_deep_payload_bytes_per_flow",
        1,
    )

    budget = policy.get("budget")
    if not isinstance(budget, Mapping) or set(budget) != {
        "configured_budget_us",
        "execution_budget_safety_ratio",
        "budget_overrun_count_max",
        "minimum_key_flow_coverage",
    }:
        raise FullTrafficFeatureLoopError("budget contract is invalid")
    _number(budget.get("configured_budget_us"), "budget.configured_budget_us", 0.001)
    safety = _number(
        budget.get("execution_budget_safety_ratio"),
        "budget.execution_budget_safety_ratio",
        0.001,
    )
    if safety > 1.0:
        raise FullTrafficFeatureLoopError("budget safety ratio cannot exceed one")
    _integer(budget.get("budget_overrun_count_max"), "budget.budget_overrun_count_max")
    coverage = _number(
        budget.get("minimum_key_flow_coverage"), "budget.minimum_key_flow_coverage"
    )
    if coverage > 1.0:
        raise FullTrafficFeatureLoopError("key-flow coverage cannot exceed one")

    boundaries = policy.get("qualification_boundaries")
    if not isinstance(boundaries, Mapping) or boundaries != {
        "method_receipt_is_production_qualification": False,
        "hardware_experiment_still_required": True,
        "current_hardware_can_claim_production_sla": False,
    }:
        raise FullTrafficFeatureLoopError("qualification boundaries are invalid")


class AllTrafficRecognizer:
    """Deterministic L3/L4/service recognition for every parsed packet."""

    def __init__(self, service_ports: Iterable[int] = _SERVICE_CLASSES) -> None:
        self.service_ports = frozenset(int(port) for port in service_ports)
        if self.service_ports != frozenset(_SERVICE_CLASSES):
            raise FullTrafficFeatureLoopError("service-port identity must match the live Rust path")

    @staticmethod
    def _service(packet: PacketRecord) -> str:
        if packet.dst_port in _SERVICE_CLASSES:
            return _SERVICE_CLASSES[packet.dst_port]
        if packet.src_port in _SERVICE_CLASSES:
            return _SERVICE_CLASSES[packet.src_port]
        return "unclassified"

    def recognize(
        self, packet: PacketRecord, packet_index: int, pipeline: AdaptiveExtractionPipeline
    ) -> TrafficRecognition:
        if not isinstance(packet, PacketRecord):
            raise FullTrafficFeatureLoopError("captured packets must be PacketRecord instances")
        _number(packet.timestamp, "packet.timestamp")
        _integer(packet.src_port, "packet.src_port")
        _integer(packet.dst_port, "packet.dst_port")
        _integer(packet.protocol, "packet.protocol")
        _integer(packet.wire_length, "packet.wire_length")
        _integer(packet.actual_payload_length, "packet.payload_length")
        if packet.src_port > 65535 or packet.dst_port > 65535:
            raise FullTrafficFeatureLoopError("packet port is outside the unsigned-16 range")
        if packet.protocol > 255:
            raise FullTrafficFeatureLoopError("packet protocol is outside the unsigned-8 range")
        key = pipeline.extractor.canonical_key(packet)
        service = self._service(packet)
        return TrafficRecognition(
            packet_index=packet_index,
            flow_key=key,
            protocol_class=_PROTOCOL_CLASSES.get(packet.protocol, "other"),
            service_class=service,
            payload_class="payload" if packet.actual_payload_length > 0 else "no_payload",
            canonical_direction=("forward" if packet.flow_key == key else "reverse"),
            is_key_flow=service != "unclassified",
            base_features=pipeline.extractor.packet_features(packet),
        )


class FullTrafficFeatureSystem:
    """Stateful closed loop shared by production and fallback capture paths."""

    def __init__(
        self,
        *,
        policy: Mapping[str, Any],
        active_backend: str,
        pipeline: Optional[AdaptiveExtractionPipeline] = None,
        recognizer: Optional[AllTrafficRecognizer] = None,
        feature_reservoir: Optional[UnifiedFeatureReservoir] = None,
    ) -> None:
        validate_feature_loop_policy(policy)
        if active_backend not in BACKENDS:
            raise FullTrafficFeatureLoopError("unsupported initial capture backend")
        extraction = policy["extraction"]
        budget = policy["budget"]
        self.policy = dict(policy)
        self.policy_sha256 = _canonical_sha256(policy)
        self.pipeline = pipeline or AdaptiveExtractionPipeline(
            execution_budget_safety_ratio=float(budget["execution_budget_safety_ratio"]),
            max_deep_payload_bytes_per_flow=int(
                extraction["max_deep_payload_bytes_per_flow"]
            ),
        )
        self.recognizer = recognizer or AllTrafficRecognizer()
        self.feature_reservoir = feature_reservoir or UnifiedFeatureReservoir(
            default_reservoir_policy()
        )
        reservoir_binding = policy["unified_feature_reservoir"]
        if (
            self.feature_reservoir.policy.get("policy_id")
            != reservoir_binding["policy_id"]
            or self.feature_reservoir.policy_sha256
            != reservoir_binding["canonical_policy_sha256"]
        ):
            raise FullTrafficFeatureLoopError(
                "runtime feature reservoir does not match the loop policy"
            )
        self.active_backend = active_backend
        self.generation = 1
        self._last_batch_sequence = 0
        self._transitions = []
        self._totals = Counter()

    def apply_failover_receipt(self, receipt: Mapping[str, Any]) -> bool:
        """Apply an already executed, independently sealed transition.

        The control-plane executor performs the mutation and rollback.  This
        method only advances the data-plane generation after the receipt proves
        that the selected backend owns capture.  Extractor and scheduler state
        are deliberately retained across the handoff.
        """

        if receipt.get("scope") != FAILOVER_RECEIPT_SCOPE:
            raise FullTrafficFeatureLoopError("failover execution receipt scope is invalid")
        if receipt.get("error") is not None or receipt.get("recovery_required") is not False:
            raise FullTrafficFeatureLoopError("failed failover receipt cannot advance the loop")
        outcome = receipt.get("outcome")
        if outcome == "decision_requires_no_automatic_mutation":
            return False
        selected = receipt.get("selected_backend")
        if selected not in BACKENDS or outcome != "switched_to_" + str(selected):
            raise FullTrafficFeatureLoopError("failover outcome and backend disagree")
        if receipt.get("current_backend") != self.active_backend:
            raise FullTrafficFeatureLoopError("failover receipt starts from a stale backend")
        if receipt.get("mutations_performed") is not True:
            raise FullTrafficFeatureLoopError("switch receipt does not prove a mutation")
        after = receipt.get("after_snapshot")
        if not isinstance(after, Mapping) or after.get("active_backend") != selected:
            raise FullTrafficFeatureLoopError("post-switch ownership was not proved")
        digest = receipt.get("receipt_sha256")
        if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
            raise FullTrafficFeatureLoopError("failover receipt is not sealed")
        previous = self.active_backend
        self.active_backend = str(selected)
        self.generation += 1
        self._last_batch_sequence = 0
        self._transitions.append(
            {
                "from": previous,
                "to": self.active_backend,
                "generation": self.generation,
                "receipt_sha256": digest,
            }
        )
        return True

    def process_batch(
        self,
        batch: CapturedPacketBatch,
        *,
        allow_deep: bool = True,
        budget_us: Optional[float] = None,
    ) -> FullTrafficBatchResult:
        if batch.backend != self.active_backend or batch.generation != self.generation:
            raise FullTrafficFeatureLoopError("batch belongs to a stale capture generation")
        sequence = _integer(batch.batch_sequence, "batch.batch_sequence", 1)
        if sequence != self._last_batch_sequence + 1:
            raise FullTrafficFeatureLoopError("batch sequence is not consecutive")
        rejected = _integer(batch.parse_rejected, "batch.parse_rejected")
        dropped = _integer(batch.capture_dropped, "batch.capture_dropped")
        packets = tuple(batch.packets)
        configured_budget = (
            float(self.policy["budget"]["configured_budget_us"])
            if budget_us is None
            else _number(budget_us, "budget_us", 0.001)
        )
        recognitions = tuple(
            self.recognizer.recognize(packet, index, self.pipeline)
            for index, packet in enumerate(packets)
        )
        key_flows = {item.flow_key for item in recognitions if item.is_key_flow}
        unique_flows = {item.flow_key for item in recognitions}
        flow_results = tuple(
            self.pipeline.process_batch(
                packets,
                budget_us=configured_budget,
                allow_deep=allow_deep,
                key_flows=key_flows,
            )
        )
        plan = self.pipeline.last_schedule_plan
        if plan is None:
            raise FullTrafficFeatureLoopError("pipeline omitted its schedule receipt")
        deep_flow_keys = {
            result.flow_key for result in flow_results if result.tier == "deep"
        }
        reservoir_result = self.feature_reservoir.observe_batch(
            packets,
            batch.packet_metadata,
            deep_flow_keys=deep_flow_keys,
        )

        parsed = len(packets)
        received = parsed + rejected
        tier_counts = Counter(result.tier for result in flow_results)
        parse_conservation = received == parsed + rejected
        recognition_conservation = parsed == len(recognitions)
        packet_feature_conservation = parsed == sum(
            bool(item.base_features) for item in recognitions
        )
        flow_feature_conservation = len(unique_flows) == len(flow_results) and {
            result.flow_key for result in flow_results
        } == unique_flows
        reservoir_flow_conservation = (
            {record.flow_key for record in reservoir_result.flow_records}
            == unique_flows
            and reservoir_result.receipt.get("feature_reservoir_closed") is True
        )
        budget_closed = (
            plan.budget_overrun_count
            <= int(self.policy["budget"]["budget_overrun_count_max"])
        )
        key_closed = plan.key_flow_coverage + 1e-12 >= float(
            self.policy["budget"]["minimum_key_flow_coverage"]
        )
        lossless = dropped == 0
        recognition_complete = (
            lossless
            and rejected == 0
            and parse_conservation
            and recognition_conservation
            and packet_feature_conservation
        )
        loop_closed = (
            recognition_complete
            and flow_feature_conservation
            and reservoir_flow_conservation
            and budget_closed
            and key_closed
        )
        degraded = self.active_backend == CURRENT_HARDWARE_BACKEND
        receipt: Dict[str, Any] = {
            "schema_version": 1,
            "scope": RECEIPT_SCOPE,
            "policy_id": self.policy["policy_id"],
            "policy_sha256": self.policy_sha256,
            "source_id": batch.source_id,
            "backend": self.active_backend,
            "backend_generation": self.generation,
            "batch_sequence": sequence,
            "degraded_mode": degraded,
            "capture": {
                "packets_received": received,
                "packets_parsed": parsed,
                "parse_rejected": rejected,
                "capture_dropped": dropped,
                "lossless": lossless,
            },
            "recognition": {
                "recognized_packets": len(recognitions),
                "base_featured_packets": sum(bool(item.base_features) for item in recognitions),
                "protocol_counts": dict(sorted(Counter(item.protocol_class for item in recognitions).items())),
                "service_counts": dict(sorted(Counter(item.service_class for item in recognitions).items())),
                "key_flow_count": len(key_flows),
            },
            "extraction": {
                "observed_flows": len(unique_flows),
                "feature_results": len(flow_results),
                "tier_counts": {name: tier_counts.get(name, 0) for name in ("base", "flow", "deep")},
                "unified_feature_records": len(reservoir_result.flow_records),
                "unified_flow_segments": reservoir_result.receipt[
                    "observed_flow_segments"
                ],
                "persistent_schema_column_count": reservoir_result.receipt[
                    "persistent_schema_column_count"
                ],
                "online_extractable_column_count": reservoir_result.receipt[
                    "online_extractable_column_count"
                ],
                "model_candidate_persistent_column_count": reservoir_result.receipt[
                    "model_candidate_persistent_column_count"
                ],
                "safe_scalar_count": reservoir_result.receipt["safe_scalar_count"],
                "sequence_column_count": reservoir_result.receipt["sequence_column_count"],
                "encrypted_structure_count": reservoir_result.receipt[
                    "encrypted_structure_count"
                ],
                "context_feature_count": reservoir_result.receipt[
                    "context_feature_count"
                ],
                "window_context_count": len(reservoir_result.window_contexts),
                "deep_selected_flows": reservoir_result.receipt[
                    "deep_selected_flows"
                ],
                "deep_deferred_flows": reservoir_result.receipt[
                    "deep_deferred_flows"
                ],
                "feature_reservoir_receipt_sha256": reservoir_result.receipt[
                    "receipt_sha256"
                ],
            },
            "budget": {
                "configured_budget_us": configured_budget,
                "effective_budget_us": plan.effective_budget_us,
                "estimated_used_us": plan.estimated_used_us,
                "actual_used_us": plan.actual_used_us,
                "budget_overrun_count": plan.budget_overrun_count,
                "key_flow_total": plan.key_flow_total,
                "key_flow_covered": plan.key_flow_covered,
                "key_flow_coverage": plan.key_flow_coverage,
                "fallback_active": plan.fallback_active,
                "scheduler_estimates": self.pipeline.scheduler.estimates,
            },
            "conservation": {
                "parse": parse_conservation,
                "recognition": recognition_conservation,
                "packet_base_features": packet_feature_conservation,
                "flow_results": flow_feature_conservation,
                "unified_feature_reservoir": reservoir_flow_conservation,
                "budget": budget_closed,
                "key_flows": key_closed,
            },
            "all_traffic_recognition_complete": recognition_complete,
            "feature_extraction_loop_closed": loop_closed,
            "method_contract_verified": loop_closed,
            "production_sla_qualified": False,
            "hardware_experiment_required": True,
            "final_pareto_ingestion_allowed": False,
        }
        receipt["receipt_sha256"] = _canonical_sha256(receipt)
        self._last_batch_sequence = sequence
        self._totals.update(
            packets_received=received,
            packets_parsed=parsed,
            parse_rejected=rejected,
            capture_dropped=dropped,
            recognized_packets=len(recognitions),
            observed_flows=len(unique_flows),
            feature_results=len(flow_results),
            unified_feature_records=len(reservoir_result.flow_records),
            closed_batches=int(loop_closed),
            batches=1,
        )
        return FullTrafficBatchResult(
            recognitions,
            flow_results,
            reservoir_result.flow_records,
            reservoir_result.window_contexts,
            receipt,
        )

    def summary(self) -> Mapping[str, Any]:
        return {
            "schema_version": 1,
            "scope": "hft_mgbs_full_traffic_feature_loop_session_summary_v1",
            "active_backend": self.active_backend,
            "backend_generation": self.generation,
            "degraded_mode": self.active_backend == CURRENT_HARDWARE_BACKEND,
            "transitions": tuple(self._transitions),
            "totals": dict(self._totals),
            "flow_state_preserved_across_switches": True,
            "unified_feature_reservoir_preserved_across_switches": True,
            "scheduler_feedback_preserved_across_switches": True,
            "production_sla_qualified": False,
        }


def audit_high_speed_metrics(
    metrics: Mapping[str, Any], *, backend: str, policy: Mapping[str, Any]
) -> Dict[str, Any]:
    """Recompute the method closure from a Rust high-speed raw report.

    This deliberately proves the feature method only.  It does not promote a
    diagnostic or fallback run to a production performance qualification.
    """

    validate_feature_loop_policy(policy)
    if backend not in BACKENDS:
        raise FullTrafficFeatureLoopError("unsupported high-speed metrics backend")
    errors = []

    def counter(name: str) -> int:
        try:
            return _integer(metrics.get(name), "metrics." + name)
        except FullTrafficFeatureLoopError as error:
            errors.append(str(error))
            return 0

    received = counter("packets_received")
    parsed = counter("packets_parsed")
    rejected = counter("parse_rejected")
    dropped = counter("capture_packets_dropped")
    flows = counter("flows_emitted")
    deep_selected = counter("deep_flows_selected")
    deep_deferred = counter("deep_flows_deferred")
    overruns = counter("budget_overrun_count")
    parse_conservation = received == parsed + rejected
    flow_conservation = flows == deep_selected + deep_deferred
    if not parse_conservation:
        errors.append("metrics.parse_conservation")
    if not flow_conservation:
        errors.append("metrics.feature_tier_conservation")
    if dropped:
        errors.append("metrics.capture_packets_dropped")
    if rejected:
        errors.append("metrics.parse_rejected")
    if overruns > int(policy["budget"]["budget_overrun_count_max"]):
        errors.append("metrics.budget_overrun_count")

    key = metrics.get("key_flow_conservation")
    key_conservation = isinstance(key, Mapping) and (
        key.get("eligible_equals_enqueue_outcomes") is True
        and key.get("enqueued_equals_completion_outcomes") is True
        and key.get("eligible_conservation_abs_delta") == 0
        and key.get("completion_conservation_abs_delta") == 0
    )
    if not key_conservation:
        errors.append("metrics.key_flow_conservation")
    key_total = counter("key_flows_total")
    coverage = metrics.get("key_flow_coverage")
    if key_total:
        if not isinstance(coverage, (int, float)) or isinstance(coverage, bool) or (
            float(coverage) + 1e-12 < float(policy["budget"]["minimum_key_flow_coverage"])
        ):
            errors.append("metrics.key_flow_coverage")

    method_closed = not errors
    result = {
        "schema_version": 1,
        "scope": AUDIT_SCOPE,
        "policy_id": policy["policy_id"],
        "policy_sha256": _canonical_sha256(policy),
        "backend": backend,
        "degraded_mode": backend == CURRENT_HARDWARE_BACKEND,
        "counters": {
            "packets_received": received,
            "packets_parsed": parsed,
            "parse_rejected": rejected,
            "capture_packets_dropped": dropped,
            "flows_emitted": flows,
            "deep_flows_selected": deep_selected,
            "deep_flows_deferred": deep_deferred,
            "budget_overrun_count": overruns,
            "key_flows_total": key_total,
        },
        "conservation": {
            "parse": parse_conservation,
            "feature_tiers": flow_conservation,
            "key_flows": key_conservation,
        },
        "all_traffic_recognition_complete": dropped == 0 and rejected == 0 and parse_conservation,
        "feature_extraction_loop_closed": method_closed,
        "method_contract_verified": method_closed,
        "errors": errors,
        "production_sla_qualified": False,
        "hardware_experiment_required": True,
        "final_pareto_ingestion_allowed": False,
    }
    result["audit_sha256"] = _canonical_sha256(result)
    return result
