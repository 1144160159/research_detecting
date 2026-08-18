"""Verify remote replay and split-recovery artifacts against the release config."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.audit_release_candidate import audit


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def same_number(left, right, tolerance=1e-12) -> bool:
    return (
        isinstance(left, (int, float))
        and isinstance(right, (int, float))
        and abs(float(left) - float(right)) <= tolerance
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("algorithm_search", type=Path)
    parser.add_argument("release_candidate", type=Path)
    parser.add_argument("physical_confirmation", type=Path)
    parser.add_argument("recovery_confirmation", type=Path)
    parser.add_argument("--runtime-selection", type=Path)
    parser.add_argument("--virtual-diagnostic", type=Path)
    parser.add_argument("--resource-confirmation", type=Path)
    parser.add_argument("--temporary-shadow", type=Path)
    parser.add_argument("--interface-readiness", type=Path)
    parser.add_argument("--timestamp-probe", type=Path)
    parser.add_argument("--live-preflight-index", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    search = json.loads(args.algorithm_search.read_text(encoding="utf-8"))
    release = json.loads(args.release_candidate.read_text(encoding="utf-8"))
    physical = json.loads(
        args.physical_confirmation.read_text(encoding="utf-8")
    )
    recovery = json.loads(
        args.recovery_confirmation.read_text(encoding="utf-8")
    )
    result = audit(search, release)
    errors = list(result["errors"])
    evidence = release.get("evidence") or {}

    checks = (
        (
            "physical",
            args.physical_confirmation,
            evidence.get("physical_replay_confirmation"),
            evidence.get("physical_replay_confirmation_sha256"),
        ),
        (
            "recovery",
            args.recovery_confirmation,
            evidence.get("split_recovery_confirmation"),
            evidence.get("split_recovery_confirmation_sha256"),
        ),
    )
    hashes = {}
    for name, path, expected_path, expected_hash in checks:
        actual_hash = sha256(path)
        hashes[name] = actual_hash
        if str(path) != expected_path:
            errors.append("remote.{}.path".format(name))
        if actual_hash != expected_hash:
            errors.append("remote.{}.sha256".format(name))

    runtime_selection_hash = None
    if args.runtime_selection is not None:
        runtime_selection_hash = sha256(args.runtime_selection)
        if str(args.runtime_selection) != evidence.get("runtime_search"):
            errors.append("remote.runtime_selection.path")
        if runtime_selection_hash != evidence.get(
            "runtime_robust_selection_sha256"
        ):
            errors.append("remote.runtime_selection.sha256")
        runtime_selection = json.loads(
            args.runtime_selection.read_text(encoding="utf-8")
        )
        configured_runtime_selection = (
            release.get("observed_runtime_robust_selection") or {}
        )
        initial_runtime_candidate = runtime_selection.get(
            "selected_candidate"
        )
        final_runtime_candidate = configured_runtime_selection.get(
            "selected_candidate"
        )
        runtime_selection_map = {
            "accepted": runtime_selection.get("accepted"),
            "candidate_count": runtime_selection.get("candidate_count"),
            "passing_candidate_count": runtime_selection.get(
                "passing_candidate_count"
            ),
            "pareto_front": runtime_selection.get("pareto_front"),
            "initial_selected_candidate": initial_runtime_candidate,
            "final_pareto_ingestion_allowed": runtime_selection.get(
                "final_pareto_ingestion_allowed"
            ),
        }
        selected_runtime_rows = [
            item
            for item in runtime_selection.get("candidates") or []
            if item.get("candidate_id")
            == final_runtime_candidate
        ]
        if final_runtime_candidate not in (
            runtime_selection.get("pareto_front") or []
        ):
            errors.append("remote.runtime_selection.final_not_pareto")
        if (
            final_runtime_candidate != initial_runtime_candidate
            and not configured_runtime_selection.get(
                "selection_update_reason"
            )
        ):
            errors.append("remote.runtime_selection.update_reason")
        if len(selected_runtime_rows) != 1:
            errors.append("remote.runtime_selection.selected_row")
        else:
            selected_runtime = selected_runtime_rows[0]
            runtime_selection_map.update(
                {
                    "campaign_count_per_candidate": (
                        selected_runtime.get("campaign_count")
                    ),
                    "repeats_per_candidate": selected_runtime.get(
                        "total_run_count"
                    ),
                    "eligible_cpu_count": (
                        selected_runtime.get("metrics") or {}
                    ).get("eligible_cpu_count"),
                }
            )
            for name in (
                "inference_batch_p99_us_max",
                "internal_feature_p99_us_max",
                "end_to_end_p99_us_max",
                "end_to_end_p999_us_max",
            ):
                runtime_selection_map[name] = (
                    selected_runtime.get("metrics") or {}
                ).get(name)
        for name, value in runtime_selection_map.items():
            expected = configured_runtime_selection.get(name)
            if isinstance(value, (int, float)) or isinstance(
                expected, (int, float)
            ):
                matched = same_number(expected, value)
            else:
                matched = expected == value
            if not matched:
                errors.append(
                    "remote.runtime_selection.observed.{}".format(name)
                )

    temporary_shadow_hash = None
    if args.temporary_shadow is not None:
        temporary_shadow_hash = sha256(args.temporary_shadow)
        if str(args.temporary_shadow) != evidence.get(
            "temporary_passive_shadow"
        ):
            errors.append("remote.temporary_shadow.path")
        if temporary_shadow_hash != evidence.get(
            "temporary_passive_shadow_summary_sha256"
        ):
            errors.append("remote.temporary_shadow.sha256")
        temporary_shadow = json.loads(
            args.temporary_shadow.read_text(encoding="utf-8")
        )
        configured_shadow = (
            release.get("observed_temporary_passive_shadow") or {}
        )
        runtime = release.get("runtime") or {}
        selected_shadow_rows = [
            item
            for item in temporary_shadow.get("candidates") or []
            if item.get("candidate_id")
            == temporary_shadow.get("selected_candidate")
        ]
        if len(selected_shadow_rows) != 1:
            errors.append("remote.temporary_shadow.selected_row")
        else:
            selected_shadow = selected_shadow_rows[0]
            shadow_map = {
                "diagnostic_only": temporary_shadow.get(
                    "diagnostic_only"
                ),
                "run_count": selected_shadow.get("run_count"),
                "confirmation_duration_s": selected_shadow.get(
                    "duration_s_min"
                ),
                "capture_interface": temporary_shadow.get(
                    "capture_interface"
                ),
                "runtime_candidate": runtime.get("runtime_candidate"),
                "batch_size": selected_shadow.get("batch_size"),
                "feature_flush_us": selected_shadow.get(
                    "feature_flush_us"
                ),
                "packets_received_min": selected_shadow.get(
                    "packets_received_min"
                ),
                "parse_reject_rate_max": selected_shadow.get(
                    "parse_reject_rate_max"
                ),
                "capture_drop_rate_max": selected_shadow.get(
                    "capture_drop_rate_max"
                ),
                "key_flow_coverage_min": selected_shadow.get(
                    "key_flow_coverage_min"
                ),
                "gpu_flows_scored_min": selected_shadow.get(
                    "gpu_flows_scored_min"
                ),
                "gpu_batches_failed_max": selected_shadow.get(
                    "gpu_batches_failed_max"
                ),
                "gpu_queue_full_max": selected_shadow.get(
                    "gpu_queue_full_max"
                ),
                "fallback_flows_max": selected_shadow.get(
                    "fallback_flows_max"
                ),
                "budget_overrun_count_max": selected_shadow.get(
                    "budget_overrun_count_max"
                ),
                "packet_processing_p99_us_max": selected_shadow.get(
                    "packet_processing_p99_us_max"
                ),
                "internal_feature_enqueue_p99_us_max": (
                    selected_shadow.get(
                        "internal_feature_enqueue_p99_us_max"
                    )
                ),
                "gpu_batch_round_trip_p99_us_max": selected_shadow.get(
                    "gpu_batch_round_trip_p99_us_max"
                ),
                "final_pareto_ingestion_allowed": (
                    temporary_shadow.get(
                        "final_pareto_ingestion_allowed"
                    )
                ),
                "production_10gbe_claim_allowed": temporary_shadow.get(
                    "production_10gbe_claim_allowed"
                ),
            }
            if selected_shadow.get("duration_s_min") != selected_shadow.get(
                "duration_s_max"
            ):
                errors.append(
                    "remote.temporary_shadow.duration_consistency"
                )
            for name, value in shadow_map.items():
                expected = configured_shadow.get(name)
                if isinstance(value, (int, float)) or isinstance(
                    expected, (int, float)
                ):
                    matched = same_number(expected, value)
                else:
                    matched = expected == value
                if not matched:
                    errors.append(
                        "remote.temporary_shadow.observed.{}".format(name)
                    )

    interface_readiness_hash = None
    if args.interface_readiness is not None:
        interface_readiness_hash = sha256(args.interface_readiness)
        if str(args.interface_readiness) != evidence.get(
            "final_10gbe_interface_readiness"
        ):
            errors.append("remote.interface_readiness.path")
        if interface_readiness_hash != evidence.get(
            "final_10gbe_interface_readiness_sha256"
        ):
            errors.append("remote.interface_readiness.sha256")
        readiness = json.loads(
            args.interface_readiness.read_text(encoding="utf-8")
        )
        configured_readiness = (
            release.get("observed_final_10gbe_interface_readiness") or {}
        )
        readiness_map = {
            "minimum_speed_mbps": readiness.get("minimum_speed_mbps"),
            "require_unmanaged": readiness.get("require_unmanaged"),
            "excluded_interfaces": readiness.get("excluded_interfaces"),
            "hardware_eligible_interfaces": readiness.get(
                "hardware_eligible_interfaces"
            ),
            "hardware_pair_count": readiness.get("hardware_pair_count"),
            "full_preflight_eligible_interfaces": readiness.get(
                "full_preflight_eligible_interfaces"
            ),
            "full_preflight_pair_count": readiness.get(
                "full_preflight_pair_count"
            ),
            "final_live_run_allowed": readiness.get(
                "final_live_run_allowed"
            ),
        }
        for name, value in readiness_map.items():
            if configured_readiness.get(name) != value:
                errors.append(
                    "remote.interface_readiness.observed.{}".format(name)
                )
        observed_interface_blockers = {
            item.get("interface"): item.get("hardware_errors")
            for item in readiness.get("interfaces") or []
        }
        if configured_readiness.get(
            "interface_blockers"
        ) != observed_interface_blockers:
            errors.append(
                "remote.interface_readiness.interface_blockers"
            )
        observed_threshold_blockers = {
            error
            for item in readiness.get("interfaces") or []
            for error in item.get("errors") or []
            if str(error).startswith("thresholds.")
        }
        if set(
            configured_readiness.get("threshold_blockers") or []
        ) != observed_threshold_blockers:
            errors.append(
                "remote.interface_readiness.threshold_blockers"
            )

    virtual_diagnostic_hash = None
    if args.virtual_diagnostic is not None:
        virtual_diagnostic_hash = sha256(args.virtual_diagnostic)
        if str(args.virtual_diagnostic) != evidence.get(
            "virtual_link_diagnostic"
        ):
            errors.append("remote.virtual_diagnostic.path")
        if virtual_diagnostic_hash != evidence.get(
            "virtual_link_diagnostic_sha256"
        ):
            errors.append("remote.virtual_diagnostic.sha256")
        virtual_diagnostic = json.loads(
            args.virtual_diagnostic.read_text(encoding="utf-8")
        )
        configured_virtual = (
            release.get("observed_virtual_link_diagnostic") or {}
        )
        virtual_worst = (
            virtual_diagnostic.get("observed_worst_case") or {}
        )
        virtual_map = {
            "accepted": virtual_diagnostic.get("accepted"),
            "run_count": virtual_diagnostic.get("run_count"),
            "capture_binary_sha256": (
                virtual_diagnostic.get("identity") or {}
            ).get("code_sha256"),
            "final_pareto_ingestion_allowed": virtual_diagnostic.get(
                "final_pareto_ingestion_allowed"
            ),
        }
        for name in (
            "offered_packets_min",
            "pipeline_drop_rate_max",
            "parse_reject_rate_max",
            "key_flow_coverage_min",
            "inference_batch_p99_us_max",
            "internal_feature_p99_us_max",
            "end_to_end_p99_us_max",
            "end_to_end_p999_us_max",
            "budget_overrun_count_max",
        ):
            virtual_map[name] = virtual_worst.get(name)
        for name, value in virtual_map.items():
            expected = configured_virtual.get(name)
            if isinstance(value, (int, float)) or isinstance(
                expected, (int, float)
            ):
                matched = same_number(expected, value)
            else:
                matched = expected == value
            if not matched:
                errors.append(
                    "remote.virtual_diagnostic.observed.{}".format(name)
                )

    resource_confirmation_hash = None
    if args.resource_confirmation is not None:
        resource_confirmation_hash = sha256(args.resource_confirmation)
        if str(args.resource_confirmation) != evidence.get(
            "inference_node_resource_confirmation"
        ):
            errors.append("remote.resource_confirmation.path")
        if resource_confirmation_hash != evidence.get(
            "inference_node_resource_confirmation_sha256"
        ):
            errors.append("remote.resource_confirmation.sha256")
        resource_confirmation = json.loads(
            args.resource_confirmation.read_text(encoding="utf-8")
        )
        configured_resource = (
            release.get("observed_split_inference_resource_confirmation")
            or {}
        )
        resource_worst = (
            resource_confirmation.get("observed_worst_case") or {}
        )
        resource_map = {
            "accepted": resource_confirmation.get("accepted"),
            "run_count": resource_confirmation.get("run_count"),
            "final_pareto_ingestion_allowed": resource_confirmation.get(
                "final_pareto_ingestion_allowed"
            ),
        }
        for name in (
            "process_sample_count_min",
            "gpu_sample_count_min",
            "cpu_cores_used_max",
            "host_cpu_fraction_max",
            "rss_bytes_max",
            "host_memory_fraction_max",
            "threads_max",
            "process_tree_pid_count_max",
            "service_gpu_process_present",
            "service_gpu_utilization_fraction_max",
            "service_gpu_memory_fraction_max",
            "service_gpu_memory_mib_max",
        ):
            resource_map[name] = resource_worst.get(name)
        resource_map[
            "system_gpu_utilization_fraction_background_max"
        ] = resource_worst.get(
            "system_gpu_utilization_fraction_max"
        )
        resource_map[
            "system_gpu_memory_fraction_background_max"
        ] = resource_worst.get("system_gpu_memory_fraction_max")
        for name, value in resource_map.items():
            expected = configured_resource.get(name)
            if isinstance(value, (int, float)) or isinstance(
                expected, (int, float)
            ):
                matched = same_number(expected, value)
            else:
                matched = expected == value
            if not matched:
                errors.append(
                    "remote.resource_confirmation.observed.{}".format(
                        name
                    )
                )
        resource_identity = resource_confirmation.get("identity") or {}
        if resource_identity.get("candidate_id") != release.get(
            "candidate_id"
        ):
            errors.append("remote.resource_confirmation.candidate_id")
        if resource_identity.get("runtime_candidate") != (
            release.get("runtime") or {}
        ).get("runtime_candidate"):
            errors.append("remote.resource_confirmation.runtime_candidate")
        if resource_identity.get("algorithm_device") != "cpu":
            errors.append("remote.resource_confirmation.algorithm_device")
        if resource_identity.get("gpu_required") is not False:
            errors.append("remote.resource_confirmation.gpu_required")

        resource_run_records = evidence.get(
            "inference_node_resource_runs"
        ) or []
        if len(resource_run_records) < 3:
            errors.append("remote.resource_confirmation.run_records")
        for index, record in enumerate(resource_run_records):
            path = Path(str(record.get("path", "")))
            if not path.is_file():
                errors.append(
                    "remote.resource_confirmation.run{}.missing".format(
                        index
                    )
                )
                continue
            if sha256(path) != record.get("sha256"):
                errors.append(
                    "remote.resource_confirmation.run{}.sha256".format(
                        index
                    )
                )

    configured_binary_hash = evidence.get(
        "physical_replay_binary_sha256"
    )
    replay_binary_hashes = []
    for index, run_dir in enumerate(
        evidence.get("physical_replay_runs") or []
    ):
        binary_path = Path(run_dir) / "hft-capture.bin"
        if not binary_path.is_file():
            errors.append("remote.physical_binary.{}.missing".format(index))
            continue
        binary_hash = sha256(binary_path)
        replay_binary_hashes.append(binary_hash)
        if binary_hash != configured_binary_hash:
            errors.append("remote.physical_binary.{}.sha256".format(index))
    if len(replay_binary_hashes) < 3:
        errors.append("remote.physical_binary.run_count")

    timestamp_hash = None
    if args.timestamp_probe is not None:
        timestamp_hash = sha256(args.timestamp_probe)
        if str(args.timestamp_probe) != evidence.get(
            "timestamp_driver_probe"
        ):
            errors.append("remote.timestamp_probe.path")
        if timestamp_hash != evidence.get("timestamp_driver_probe_sha256"):
            errors.append("remote.timestamp_probe.sha256")
        timestamp = json.loads(
            args.timestamp_probe.read_text(encoding="utf-8")
        )
        configured_timestamp = (
            release.get("observed_timestamp_driver_probe") or {}
        )
        timestamp_latency = (
            timestamp.get("kernel_receive_to_feature_enqueue_latency") or {}
        )
        timestamp_map = {
            "capture_driver": timestamp.get("capture_driver"),
            "timestamp_provenance": timestamp.get("timestamp_provenance"),
            "packets_received": timestamp.get("packets_received"),
            "packets_parsed": timestamp.get("packets_parsed"),
            "parse_reject_rate": timestamp.get("parse_reject_rate"),
            "kernel_receive_to_feature_enqueue_samples": (
                timestamp_latency.get("samples")
            ),
            "kernel_receive_to_feature_enqueue_p99_us": (
                timestamp_latency.get("p99_us")
            ),
            "kernel_receive_to_feature_enqueue_p999_us": (
                timestamp_latency.get("p999_us")
            ),
            "kernel_timestamp_anomalies": timestamp.get(
                "kernel_timestamp_anomalies"
            ),
            "realtime_clock_step_count": timestamp.get(
                "realtime_clock_step_count"
            ),
        }
        for name, value in timestamp_map.items():
            expected = configured_timestamp.get(name)
            if isinstance(value, (int, float)) or isinstance(
                expected, (int, float)
            ):
                matched = same_number(expected, value)
            else:
                matched = expected == value
            if not matched:
                errors.append("remote.timestamp_probe.observed.{}".format(name))
        timestamp_binary_record = (
            args.timestamp_probe.parent / "binary.sha256"
        )
        if not timestamp_binary_record.is_file():
            errors.append("remote.timestamp_probe.binary_record")
        else:
            recorded_binary_hash = (
                timestamp_binary_record.read_text(encoding="utf-8")
                .split()[0]
            )
            if recorded_binary_hash != evidence.get(
                "timestamp_driver_probe_binary_sha256"
            ):
                errors.append("remote.timestamp_probe.binary_sha256")

    live_preflight_index_hash = None
    if args.live_preflight_index is not None:
        live_preflight_index_hash = sha256(args.live_preflight_index)
        if str(args.live_preflight_index.parent) != evidence.get(
            "latest_live_preflight_bundle"
        ):
            errors.append("remote.live_preflight.path")
        if live_preflight_index_hash != evidence.get(
            "latest_live_preflight_bundle_index_sha256"
        ):
            errors.append("remote.live_preflight.sha256")
        counter_map_path = (
            args.live_preflight_index.parent / "frozen_counter_map.json"
        )
        if not counter_map_path.is_file():
            errors.append("remote.live_preflight.counter_map")
        elif sha256(counter_map_path) != evidence.get(
            "live_counter_map_sha256"
        ):
            errors.append("remote.live_preflight.counter_map_sha256")

    if physical.get("passed_offline_confirmation") is not True:
        errors.append("remote.physical.not_passed")
    if recovery.get("passed") is not True:
        errors.append("remote.recovery.not_passed")

    configured_physical = (
        release.get("observed_physical_offline_confirmation") or {}
    )
    observed_physical = physical.get("observed_worst_case") or {}
    physical_map = {
        "run_count": physical.get("run_count"),
        "packets_per_run": (
            (physical.get("runs") or [{}])[0].get("packets_received")
        ),
        "flows_per_run": (
            (physical.get("runs") or [{}])[0].get("flows_emitted")
        ),
        "capture_drop_rate_max": observed_physical.get(
            "capture_drop_rate_max"
        ),
        "parse_reject_rate_max": observed_physical.get(
            "parse_reject_rate_max"
        ),
        "key_flow_coverage_min": observed_physical.get(
            "key_flow_coverage_min"
        ),
        "gpu_batch_p99_us_max": observed_physical.get(
            "gpu_batch_p99_us_max"
        ),
        "feature_enqueue_p99_us_max": observed_physical.get(
            "feature_enqueue_p99_us_max"
        ),
        "feature_enqueue_p999_us_max": observed_physical.get(
            "feature_enqueue_p999_us_max"
        ),
        "packet_processing_p99_us_max": observed_physical.get(
            "packet_p99_us_max"
        ),
        "gpu_queue_full_max": observed_physical.get("gpu_queue_full_max"),
        "gpu_batches_failed_max": observed_physical.get(
            "gpu_batches_failed_max"
        ),
        "fallback_flows_max": observed_physical.get("fallback_flows_max"),
        "budget_overrun_count_max": observed_physical.get(
            "budget_overrun_count_max"
        ),
        "physical_process_cpu_percent_of_one_core_max": (
            observed_physical.get("physical_cpu_percent_max")
        ),
        "physical_rss_kb_max": observed_physical.get(
            "physical_rss_kb_max"
        ),
    }
    for name, value in physical_map.items():
        if not same_number(configured_physical.get(name), value):
            errors.append("remote.physical.observed.{}".format(name))

    configured_recovery = (
        release.get("observed_split_recovery_confirmation") or {}
    )
    recovery_worst = recovery.get("observed_worst_case") or {}
    recovery_map = {
        "run_count": recovery.get("run_count"),
        "baseline_round_trip_ms_max": recovery_worst.get(
            "baseline_round_trip_ms_max"
        ),
        "reconnect_ms_max": recovery_worst.get("reconnect_ms_max"),
        "recovered_round_trip_ms_max": recovery_worst.get(
            "recovered_round_trip_ms_max"
        ),
        "recovery_to_success_s_max": (
            recovery_worst.get("recovery_to_success_ms_max", float("inf"))
            / 1000.0
        ),
    }
    for name, value in recovery_map.items():
        if not same_number(configured_recovery.get(name), value):
            errors.append("remote.recovery.observed.{}".format(name))

    payload = {
        "schema_version": 1,
        "scope": "remote_release_artifact_audit",
        "release_id": release.get("release_id"),
        "candidate_id": release.get("candidate_id"),
        "algorithm_candidate_count": result["algorithm_candidate_count"],
        "physical_confirmation_sha256": hashes["physical"],
        "split_recovery_confirmation_sha256": hashes["recovery"],
        "runtime_robust_selection_sha256": runtime_selection_hash,
        "virtual_link_diagnostic_sha256": virtual_diagnostic_hash,
        "inference_node_resource_confirmation_sha256": (
            resource_confirmation_hash
        ),
        "temporary_passive_shadow_summary_sha256": (
            temporary_shadow_hash
        ),
        "final_10gbe_interface_readiness_sha256": (
            interface_readiness_hash
        ),
        "physical_replay_binary_sha256": (
            replay_binary_hashes[0] if replay_binary_hashes else None
        ),
        "timestamp_driver_probe_sha256": timestamp_hash,
        "latest_live_preflight_bundle_index_sha256": (
            live_preflight_index_hash
        ),
        "accepted": not errors,
        "errors": errors,
        "final_pareto_eligible": False,
        "physical_live_gate_pending": True,
    }
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0 if payload["accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
