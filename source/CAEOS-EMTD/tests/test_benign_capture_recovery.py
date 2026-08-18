from __future__ import annotations

from audit_caeos_benign_capture_dataset import accepted_audit


def base_audit() -> dict:
    return {
        "inventory_sha256": "inventory",
        "source_size_verified": True,
        "temporary_pcap_removed": True,
        "label_conflict_count": 0,
        "capture_label_coverage": 1.0,
        "capture_label": {"traffic_class": "Benign", "binary_label": 0},
        "processed_packets": 100,
        "pcap_packets": 100,
    }


def test_complete_capture_remains_accepted() -> None:
    audit = base_audit()
    audit["complete_pcap_read"] = True
    assert accepted_audit(audit, "inventory")


def test_audited_tail_recovery_is_accepted_only_after_boundary_flows_removed() -> None:
    audit = base_audit()
    audit.update(
        {
            "complete_pcap_read": False,
            "source_quality_action": "retain_complete_flows_before_truncated_tail",
            "truncated_boundary_flows_excluded": True,
            "truncated_boundary_flow_count": 3,
            "recovered_valid_packet_count": 100,
            "capture_read_error": {"exception_type": "PcapTailCorruption"},
        }
    )
    assert accepted_audit(audit, "inventory")
    audit["truncated_boundary_flows_excluded"] = False
    assert not accepted_audit(audit, "inventory")


def test_unpartitioned_corrupt_capture_is_rejected() -> None:
    audit = base_audit()
    audit.update(
        {
            "complete_pcap_read": False,
            "source_quality_action": "retain_complete_flows_before_truncated_tail",
            "truncated_boundary_flows_excluded": True,
            "truncated_boundary_flow_count": 0,
            "recovered_valid_packet_count": 100,
            "capture_read_error": {"exception_type": "PcapTailCorruption"},
        }
    )
    assert not accepted_audit(audit, "inventory")
