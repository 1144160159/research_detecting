import io
import json
import tarfile
from pathlib import Path

from audit_caeos_ciciot2022_all_pcaps import aggregate, run
from build_caeos_ciciot2022_all_pcap_inventory import build_inventory


def add_member(archive: tarfile.TarFile, name: str, payload: bytes):
    info = tarfile.TarInfo(name)
    info.size = len(payload)
    archive.addfile(info, io.BytesIO(payload))


def fixture_dataset(root: Path) -> Path:
    active = root / "5-Active" / "active.pcap"
    active.parent.mkdir()
    active.write_bytes(b"active")
    benign_rules = []
    for number, experiment in enumerate(("Power", "Idle", "Interactions", "Scenarios"), 1):
        name = f"{number}-{experiment}.tar.gz"
        with tarfile.open(root / name, "w:gz") as archive:
            add_member(archive, f"{number}-{experiment}/capture.pcap", experiment.encode())
        benign_rules.append({"archive": name, "experiment": experiment})
    attack_name = "6-Attacks/1-Flood/Camera/TCP/attack.pcap"
    with tarfile.open(root / "6-Attacks.tar.gz", "w:gz") as archive:
        add_member(archive, attack_name, b"attack")
    index = root / "labels.json"
    index.write_text(json.dumps({
        "schema": "caeos.ciciot2022.capture_label_index.v1",
        "active_captures": [{"capture": "5-Active/active.pcap", "pcap_bytes": 6}],
        "attack_members": [{"archive": "6-Attacks.tar.gz", "member": attack_name, "pcap_bytes": 6, "attack_family": "Flood", "attack_fine": "Flood-TCP"}],
        "benign_archive_rules": benign_rules,
    }))
    return index


def test_inventory_expands_all_four_benign_archives(tmp_path: Path):
    inventory = build_inventory(tmp_path, fixture_dataset(tmp_path))
    assert inventory["summary"]["expected_source_count"] == 6
    assert inventory["summary"]["all_four_benign_archives_expanded"] is True
    assert all(value == 1 for value in inventory["summary"]["benign_archive_member_count_by_archive"].values())


def test_formal_gate_requires_every_inventory_member():
    inventory = {"summary": {"expected_source_count": 2, "inventory_ready": True}, "entries": [{"source_id": "a"}, {"source_id": "b"}]}
    audit = {"complete_pcap_read": True, "source_size_verified": True, "temporary_pcap_removed": True, "label_conflict_count": 0, "time_nonoverlap_count": 0, "protocol_policy_version": "official_capture_tcp_udp_icmp_v2", "excluded_packet_count_by_reason": {}, "matched_flow_count": 0, "retained_supported_ip_flow_count": 0, "capture_label_coverage": 1.0}
    assert aggregate(inventory, [{**audit, "source_id": "a"}], 1)["formal_dataset_gate_passed"] is False
    assert aggregate(inventory, [{**audit, "source_id": "a"}, {**audit, "source_id": "b"}], 2)["formal_dataset_gate_passed"] is True


def test_archive_smoke_removes_each_temporary_member(tmp_path: Path, monkeypatch):
    inventory = build_inventory(tmp_path, fixture_dataset(tmp_path))
    inventory_path = tmp_path / "inventory.json"
    inventory_path.write_text(json.dumps(inventory))
    monkeypatch.setattr("audit_caeos_ciciot2022_all_pcaps.inspect_pcap", lambda *_: {"processed_packets": 1, "complete_pcap_read": True, "protocol_policy_version": "official_capture_tcp_udp_icmp_v2", "retained_supported_ip_flow_count": 1, "retained_tcp_udp_flow_count": 1, "retained_icmp_flow_count": 0, "excluded_packet_count_by_reason": {}})
    temp_root = tmp_path / "temp"
    summary = run(tmp_path, inventory_path, tmp_path / "run", temp_root, "6-Attacks")
    assert summary["accepted_source_count"] == 1
    assert summary["formal_dataset_gate_passed"] is False
    assert list(temp_root.iterdir()) == []
