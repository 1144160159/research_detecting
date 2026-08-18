import json
from pathlib import Path

from audit_caeos_ciciot2023_all_pcaps import aggregate, run
from build_caeos_ciciot2023_all_pcap_inventory import build_inventory


def fixture_index(root: Path, captures: list[tuple[str, bytes]]) -> Path:
    rows = []
    for relative, payload in captures:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        rows.append({"capture": relative, "pcap_bytes": len(payload), "is_malicious": True, "attack_family": "DoS", "attack_fine": "DoS-TCP_Flood"})
    index = root / "labels.json"
    index.write_text(json.dumps({"schema": "caeos.ciciot2023.capture_label_index.v1", "captures": rows}))
    return index


def test_inventory_requires_exact_disk_set(tmp_path: Path):
    index = fixture_index(tmp_path, [("PCAP/DoS-TCP_Flood/a.pcap", b"a")])
    report = build_inventory(tmp_path, index)
    assert report["summary"]["expected_source_count"] == 1
    assert report["summary"]["filesystem_set_equals_label_index"] is True


def test_aggregate_formal_gate_requires_full_scope():
    inventory = {"summary": {"expected_source_count": 2, "inventory_ready": True}, "entries": [{"source_id": "a"}, {"source_id": "b"}]}
    audit = {"complete_pcap_read": True, "source_size_verified": True, "label_conflict_count": 0, "time_nonoverlap_count": 0, "protocol_policy_version": "official_capture_tcp_udp_icmp_v2", "excluded_packet_count_by_reason": {}, "matched_flow_count": 0, "retained_supported_ip_flow_count": 0, "capture_label_coverage": 1.0}
    assert aggregate(inventory, [{**audit, "source_id": "a"}], 1)["formal_dataset_gate_passed"] is False
    assert aggregate(inventory, [{**audit, "source_id": "a"}, {**audit, "source_id": "b"}], 2)["formal_dataset_gate_passed"] is True


def test_run_is_resumable_and_scoped_smoke(tmp_path: Path, monkeypatch):
    index = fixture_index(tmp_path, [("PCAP/DoS-TCP_Flood/a.pcap", b"a"), ("PCAP/DoS-TCP_Flood/b.pcap", b"b")])
    inventory = build_inventory(tmp_path, index)
    inventory_path = tmp_path / "inventory.json"
    inventory_path.write_text(json.dumps(inventory))
    monkeypatch.setattr("audit_caeos_ciciot2023_all_pcaps.inspect_pcap", lambda *_: {"processed_packets": 1, "complete_pcap_read": True, "protocol_policy_version": "official_capture_tcp_udp_icmp_v2", "retained_supported_ip_flow_count": 1, "retained_tcp_udp_flow_count": 1, "retained_icmp_flow_count": 0, "excluded_packet_count_by_reason": {}})
    first = run(tmp_path, inventory_path, tmp_path / "run", "a\\.pcap$")
    assert first["accepted_source_count"] == 1
    assert first["formal_dataset_gate_passed"] is False
    second = run(tmp_path, inventory_path, tmp_path / "run", "a\\.pcap$")
    assert second["audit_file_count"] == 1
