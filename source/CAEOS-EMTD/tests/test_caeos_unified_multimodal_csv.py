import base64
import csv
import hashlib
import json
import struct
import tarfile
import zipfile
from pathlib import Path

import dpkt
import pytest

from caeos_label_alignment import create_label_index
from caeos_unified_dataset import build_source_manifest, canonical_json_hash
from prepare_caeos_unified_multimodal_csv import (
    CICIOT2023_FAMILIES,
    SCHEMA_VERSION,
    TSHARK_FIELDS,
    TSHARK_STATE_PREFERENCES,
    LabelRecord,
    canonical_l4_header,
    capture_tasks,
    materialize_tar_archives,
    merge_parts,
    path_label,
    parse_packet,
    parse_tshark_fields,
    process_capture,
    tshark_command,
    validate_source_manifest,
    verify_csv,
    verify_csv_and_sha256,
    verify_csv_and_sha256_parallel,
)


def test_canonical_tcp_header_preserves_ns_and_masks_flag_byte() -> None:
    header = canonical_l4_header(
        protocol=6,
        source_port=12345,
        destination_port=443,
        header_length=20,
        tcp_sequence=7,
        tcp_acknowledgement=11,
        flags=0x112,
        window=4096,
        udp_length=0,
        icmp_type=0,
        icmp_code=0,
    )

    assert len(header) == 20
    assert header[12] == 0x51
    assert header[13] == 0x12


def ipv6_fragment_then_hop_by_hop_frame() -> bytes:
    tcp = dpkt.tcp.TCP(
        sport=12345,
        dport=443,
        seq=7,
        ack=11,
        flags=dpkt.tcp.TH_ACK,
        win=4096,
        data=b"ipv6-extension-payload",
    )
    hop_by_hop = bytes((dpkt.ip.IP_PROTO_TCP, 0)) + bytes(6)
    fragment = bytes((0, 0)) + struct.pack("!HI", 0, 0x01020304)
    payload = fragment + hop_by_hop + bytes(tcp)
    ipv6 = struct.pack(
        "!IHBB16s16s",
        (6 << 28) | (0x2A << 20),
        len(payload),
        44,
        57,
        bytes.fromhex("20010db8000000000000000000000001"),
        bytes.fromhex("20010db8000000000000000000000002"),
    ) + payload
    return (
        bytes.fromhex("000102030405060708090a0b")
        + struct.pack("!H", dpkt.ethernet.ETH_TYPE_IP6)
        + ipv6
    )


def test_ipv6_fragment_then_hop_by_hop_dpkt_bug_uses_lossless_fallback() -> None:
    parsed = parse_packet(1.25, ipv6_fragment_then_hop_by_hop_frame())

    assert parsed is not None
    key, packet, metadata = parsed
    assert key[2] == dpkt.ip.IP_PROTO_TCP
    assert metadata["ip_version"] == 6
    assert metadata["port_a"] == 12345
    assert metadata["port_b"] == 443
    assert packet.protocol == dpkt.ip.IP_PROTO_TCP
    assert packet.ttl == 57
    assert packet.ip_dscp_ecn == 0x2A
    assert packet.ip_fragment_id == 0x01020304
    assert packet.payload == b"ipv6-extension-payload"


def test_linux_sll_is_not_guessed_as_ethernet_when_address_ends_in_ipv6_type() -> None:
    tcp = dpkt.tcp.TCP(sport=35720, dport=443, data=b"sll-ipv4-payload")
    ip = dpkt.ip.IP(
        src=b"\x0a\x00\x00\x01",
        dst=b"\x0a\x00\x00\x02",
        p=dpkt.ip.IP_PROTO_TCP,
        ttl=61,
        data=tcp,
    )
    ip.len = len(ip)
    sll = dpkt.sll.SLL(
        type=0,
        hrd=1,
        hlen=6,
        hdr=b"\x00\x01\x02\x03\x04\x05\x86\xdd",
        ethtype=dpkt.ethernet.ETH_TYPE_IP,
        data=ip,
    )

    parsed = parse_packet(2.5, bytes(sll))

    assert parsed is not None
    _, packet, metadata = parsed
    assert metadata["ip_version"] == 4
    assert metadata["protocol"] == dpkt.ip.IP_PROTO_TCP
    assert (metadata["port_a"], metadata["port_b"]) == (35720, 443)
    assert packet.ttl == 61
    assert packet.payload == b"sll-ipv4-payload"


def write_test_pcap(path: Path) -> None:
    with path.open("wb") as handle:
        writer = dpkt.pcap.Writer(handle)
        for index, payload in enumerate((b"hello", b"world")):
            tcp = dpkt.tcp.TCP(
                sport=12345,
                dport=443,
                seq=index,
                flags=dpkt.tcp.TH_ACK,
                win=4096,
                data=payload,
            )
            ip = dpkt.ip.IP(
                src=b"\x0a\x00\x00\x01",
                dst=b"\x0a\x00\x00\x02",
                p=dpkt.ip.IP_PROTO_TCP,
                ttl=64,
                data=tcp,
            )
            ip.len = len(ip)
            ethernet = dpkt.ethernet.Ethernet(
                src=b"\x00\x01\x02\x03\x04\x05",
                dst=b"\x06\x07\x08\x09\x0a\x0b",
                type=dpkt.ethernet.ETH_TYPE_IP,
                data=ip,
            )
            writer.writepkt(bytes(ethernet), ts=1.0 + index * 0.25)
        writer.close()


def write_fragmented_icmp_pcap(path: Path) -> bytes:
    icmp = dpkt.icmp.ICMP(
        type=dpkt.icmp.ICMP_ECHO,
        code=0,
        data=dpkt.icmp.ICMP.Echo(id=7, seq=9, data=b"fragment-body-" * 140),
    )
    transport = bytes(icmp)
    first_size = 1480
    fragments = (
        (1, 0, transport[:first_size]),
        (0, first_size // 8, transport[first_size:]),
    )
    with path.open("wb") as handle:
        writer = dpkt.pcap.Writer(handle)
        for index, (more_fragments, offset, body) in enumerate(fragments):
            ip = dpkt.ip.IP(
                src=b"\x0a\x00\x00\x01",
                dst=b"\x0a\x00\x00\x02",
                p=dpkt.ip.IP_PROTO_ICMP,
                ttl=64,
                id=1234,
                data=body,
            )
            ip.mf = more_fragments
            ip.offset = offset
            ip.len = len(ip)
            ethernet = dpkt.ethernet.Ethernet(
                src=b"\x00\x01\x02\x03\x04\x05",
                dst=b"\x06\x07\x08\x09\x0a\x0b",
                type=dpkt.ethernet.ETH_TYPE_IP,
                data=ip,
            )
            writer.writepkt(bytes(ethernet), ts=1.0 + index * 0.001)
        writer.close()
    return transport


def dataset(root: Path) -> dict:
    return {
        "id": "ciciot2023",
        "priority": "P0",
        "role": "main_development_and_known_classification",
        "source_root": str(root),
        "source_kind": "pcap_files",
        "include_globs": ["**/*.pcap"],
        "label_policy": "relative_attack_directory",
        "label_binding": "capture_path",
        "preprocess_enabled": True,
    }


def columns() -> list[str]:
    schema_path = Path(__file__).parents[1] / "configs" / "unified_multimodal_v4.schema.json"
    with schema_path.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    return [item["name"] for item in schema["columns"]]


def test_process_capture_writes_reversible_payload(tmp_path: Path) -> None:
    source_root = tmp_path / "pcaps"
    capture = source_root / "BenignTraffic" / "capture.pcap"
    capture.parent.mkdir(parents=True)
    write_test_pcap(capture)
    part = tmp_path / "part.part"
    task = {
        "dataset": dataset(source_root),
        "path": str(capture),
        "member": None,
        "capture_id": "capture-id",
        "source_sha256": "a" * 64,
        "part_path": str(part),
        "schema_sha256": "b" * 64,
        "columns": columns(),
        "idle_seconds": 30.0,
        "maximum_packets": 64,
        "payload_prefix_bytes": 4096,
        "sanitized_l4_prefix_bytes": 2048,
        "maximum_active_flows": 100,
    }
    metadata = process_capture(task)
    assert metadata["counters"]["rows"] == 1
    with part.open("r", encoding="utf-8", newline="") as handle:
        row = next(csv.DictReader(handle, fieldnames=columns()))
    assert row["schema_version"] == SCHEMA_VERSION
    assert row["fine_label"] == "BenignTraffic"
    assert row["family_label"] == "Benign"
    assert int(row["binary_label"]) == 0
    assert row["traffic_class"] == "Benign"
    assert row["attack_category"] == "Benign"
    assert row["attack_subcategory"] == "BenignTraffic"
    assert base64.b64decode(row["payload_b64"]) == b"helloworld"
    sanitized_l4 = base64.b64decode(row["sanitized_l4_b64"])
    assert b"hello" in sanitized_l4 and b"world" in sanitized_l4
    assert row["tcp_sequence_seq"] == "0;1"
    assert row["packet_length_seq"].count(";") == 1
    assert row["packet_iat_us_seq"] == "0;250000"
    assert int(row["packet_iat_us_total"]) == 250000
    assert int(row["forward_packet_iat_us_total"]) == 250000
    assert int(row["reverse_packet_iat_us_total"]) == 0
    assert float(row["packet_iat_us_median"]) == 250000.0
    assert int(row["active_duration_us_total"]) == 250000
    assert int(row["idle_duration_us_total"]) == 0
    assert int(row["tcp_ack_flag_count"]) == 2
    assert int(row["direction_switch_count"]) == 0
    assert float(row["reverse_forward_packet_ratio"]) == 0.0
    assert row["endpoint_a_hash"] != row["endpoint_b_hash"]
    final = tmp_path / "final.csv"
    with final.open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(columns())
        with part.open("r", encoding="utf-8", newline="") as source:
            output.write(source.read())
    verification = verify_csv(final, columns(), expected_rows=1)
    assert verification["full_row_validation"] is True
    assert verification["rows_with_payload"] == 1
    fused_verification, digest = verify_csv_and_sha256(
        final, columns(), expected_rows=1
    )
    assert fused_verification == verification
    assert digest == hashlib.sha256(final.read_bytes()).hexdigest()
    parallel_verification, parallel_digest = verify_csv_and_sha256_parallel(
        final, columns(), expected_rows=1, workers=2, batch_rows=1
    )
    assert parallel_verification["rows"] == verification["rows"]
    assert parallel_verification["rows_with_payload"] == 1
    assert parallel_verification["row_validation_parallelism"] == 2
    assert parallel_digest == digest


def test_process_capture_uses_external_flow_label_index(tmp_path: Path) -> None:
    source_root = tmp_path / "pcaps"
    capture = source_root / "mixed.pcap"
    source_root.mkdir(parents=True)
    write_test_pcap(capture)
    item = dataset(source_root)
    item["label_policy"] = "deferred_ground_truth_join"
    item["label_binding"] = "five_tuple_time_interval_and_ground_truth"
    index = create_label_index(
        tmp_path / "labels.sqlite",
        item["id"],
        [
            {
                "record_id": "labels.csv:2",
                "source_member": "mixed.pcap",
                "src_ip": "10.0.0.1",
                "src_port": 12345,
                "dst_ip": "10.0.0.2",
                "dst_port": 443,
                "protocol": 6,
                "start_ns": 900_000_000,
                "end_ns": 1_300_000_000,
                "fine_label": "Web_Attack_XSS",
                "family_label": "Web_Attack",
                "binary_label": 1,
                "label_source": "labels.csv:2",
            }
        ],
        "registry-sha",
    )
    part = tmp_path / "aligned.part"
    metadata = process_capture(
        {
            "dataset": item,
            "path": str(capture),
            "member": None,
            "capture_id": "capture-id",
            "source_sha256": "a" * 64,
            "part_path": str(part),
            "schema_sha256": "b" * 64,
            "columns": columns(),
            "idle_seconds": 30.0,
            "maximum_packets": 64,
            "payload_prefix_bytes": 4096,
            "sanitized_l4_prefix_bytes": 2048,
            "maximum_active_flows": 100,
            "label_alignment": {
                "path": index["path"],
                "sha256": index["sha256"],
                "tolerance_ns": 0,
            },
        }
    )
    assert metadata["counters"]["label_alignment::aligned_unique_flow"] == 1
    with part.open("r", encoding="utf-8", newline="") as handle:
        row = next(csv.DictReader(handle, fieldnames=columns()))
    assert row["label_status"] == "aligned_unique_flow"
    assert row["label_source"] == "labels.csv:2#labels.csv:2"
    assert row["fine_label"] == "Web_Attack_XSS"
    assert row["family_label"] == "Web_Attack"
    assert row["traffic_class"] == "Malicious"
    assert int(row["binary_label"]) == 1


def test_official_flow_label_overrides_edge_capture_path_label(tmp_path: Path) -> None:
    source_root = tmp_path / "pcaps"
    source_member = "Attack traffic/OS Fingerprinting attack.pcap"
    capture = source_root / source_member
    capture.parent.mkdir(parents=True)
    write_test_pcap(capture)
    item = dataset(source_root)
    item["label_policy"] = "edge_capture_name"
    item["label_binding"] = "capture_path_with_csv_crosscheck"
    index = create_label_index(
        tmp_path / "labels.sqlite",
        item["id"],
        [
            {
                "record_id": "official.csv:2",
                "source_member": source_member,
                "src_ip": "10.0.0.1",
                "src_port": 12345,
                "dst_ip": "10.0.0.2",
                "dst_port": 443,
                "protocol": 6,
                "start_ns": 900_000_000,
                "end_ns": 1_300_000_000,
                "fine_label": "Benign",
                "family_label": "Benign",
                "binary_label": 0,
                "label_source": "official.csv:2",
            }
        ],
        "registry-sha",
    )
    part = tmp_path / "official-precedence.part"
    metadata = process_capture(
        {
            "dataset": item,
            "path": str(capture),
            "member": None,
            "capture_id": "capture-id",
            "source_sha256": "a" * 64,
            "part_path": str(part),
            "schema_sha256": "b" * 64,
            "columns": columns(),
            "idle_seconds": 30.0,
            "maximum_packets": 64,
            "payload_prefix_bytes": 4096,
            "sanitized_l4_prefix_bytes": 2048,
            "maximum_active_flows": 100,
            "label_alignment": {
                "path": index["path"],
                "sha256": index["sha256"],
                "tolerance_ns": 0,
                "external_label_precedence": True,
            },
        }
    )
    assert (
        metadata["counters"][
            "label_alignment::path_external_disagreement_official_retained"
        ]
        == 1
    )
    with part.open("r", encoding="utf-8", newline="") as handle:
        row = next(csv.DictReader(handle, fieldnames=columns()))
    assert row["label_status"] == "aligned_unique_flow"
    assert row["fine_label"] == "Benign"
    assert row["family_label"] == "Benign"
    assert int(row["binary_label"]) == 0


def test_process_capture_splits_conflicting_flow_on_official_boundaries(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "pcaps"
    capture = source_root / "mixed.pcap"
    source_root.mkdir(parents=True)
    write_test_pcap(capture)
    item = dataset(source_root)
    item["label_policy"] = "deferred_ground_truth_join"
    item["label_binding"] = "five_tuple_time_interval_and_ground_truth"
    index = create_label_index(
        tmp_path / "labels.sqlite",
        item["id"],
        [
            {
                "record_id": "labels.csv:2",
                "source_member": "mixed.pcap",
                "src_ip": "10.0.0.1",
                "src_port": 12345,
                "dst_ip": "10.0.0.2",
                "dst_port": 443,
                "protocol": 6,
                "start_ns": 900_000_000,
                "end_ns": 1_100_000_000,
                "fine_label": "MSSQL",
                "family_label": "DDoS",
                "binary_label": 1,
                "label_source": "labels.csv:2",
            },
            {
                "record_id": "labels.csv:3",
                "source_member": "mixed.pcap",
                "src_ip": "10.0.0.1",
                "src_port": 12345,
                "dst_ip": "10.0.0.2",
                "dst_port": 443,
                "protocol": 6,
                "start_ns": 1_100_000_001,
                "end_ns": 1_300_000_000,
                "fine_label": "UDP Flood",
                "family_label": "DDoS",
                "binary_label": 1,
                "label_source": "labels.csv:3",
            },
        ],
        "registry-sha",
    )
    part = tmp_path / "boundary-split.part"
    metadata = process_capture(
        {
            "dataset": item,
            "path": str(capture),
            "member": None,
            "capture_id": "capture-id",
            "source_sha256": "a" * 64,
            "part_path": str(part),
            "schema_sha256": "b" * 64,
            "columns": columns(),
            "idle_seconds": 30.0,
            "maximum_packets": 64,
            "payload_prefix_bytes": 4096,
            "sanitized_l4_prefix_bytes": 2048,
            "maximum_active_flows": 100,
            "label_alignment": {
                "path": index["path"],
                "sha256": index["sha256"],
                "tolerance_ns": 0,
                "official_boundary_split": True,
            },
        }
    )
    assert metadata["counters"]["official_boundary_split_source_flows"] == 1
    assert metadata["counters"]["official_boundary_split_segments"] == 2
    with part.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, fieldnames=columns()))
    assert [row["fine_label"] for row in rows] == ["MSSQL", "UDP Flood"]
    assert [int(row["packet_count_total"]) for row in rows] == [1, 1]
    assert [base64.b64decode(row["payload_b64"]) for row in rows] == [
        b"hello",
        b"world",
    ]


def test_process_capture_records_approved_label_exclusion_ratio(tmp_path: Path) -> None:
    source_root = tmp_path / "pcaps"
    capture = source_root / "mixed.pcap"
    source_root.mkdir(parents=True)
    write_test_pcap(capture)
    item = dataset(source_root)
    item["label_policy"] = "deferred_ground_truth_join"
    item["label_binding"] = "five_tuple_time_interval_and_ground_truth"
    index = create_label_index(
        tmp_path / "labels.sqlite",
        item["id"],
        [
            {
                "record_id": "unrelated",
                "source_member": "mixed.pcap",
                "src_ip": "10.0.0.9",
                "src_port": 9,
                "dst_ip": "10.0.0.8",
                "dst_port": 8,
                "protocol": 6,
                "start_ns": 900_000_000,
                "end_ns": 1_300_000_000,
                "fine_label": "Benign",
                "family_label": "Benign",
                "binary_label": 0,
                "label_source": "labels.csv:9",
            }
        ],
        "registry-sha",
    )
    part = tmp_path / "excluded.part"
    metadata = process_capture(
        {
            "dataset": item,
            "path": str(capture),
            "member": None,
            "capture_id": "capture-id",
            "source_sha256": "a" * 64,
            "part_path": str(part),
            "schema_sha256": "b" * 64,
            "columns": columns(),
            "idle_seconds": 30.0,
            "maximum_packets": 64,
            "payload_prefix_bytes": 4096,
            "sanitized_l4_prefix_bytes": 2048,
            "maximum_active_flows": 100,
            "label_alignment": {
                "path": index["path"],
                "sha256": index["sha256"],
                "tolerance_ns": 0,
                "drop_unmatched_reasons": [
                    "five_tuple_absent_from_official_flow_labels"
                ],
            },
        }
    )
    summary = metadata["label_exclusion_summary"]
    assert metadata["counters"].get("rows", 0) == 0
    assert part.read_text(encoding="utf-8") == ""
    assert summary["total_finalized_flows"] == 1
    assert summary["excluded_flows"] == 1
    assert summary["excluded_flow_fraction"] == 1.0
    assert summary["excluded_packets"] == 2
    assert summary["excluded_packet_fraction"] == 1.0
    assert summary["reason_counts"] == {
        "five_tuple_absent_from_official_flow_labels": 1
    }
    assert summary["source_pcaps_modified"] is False


def test_tshark_memory_policy_keeps_all_packets_and_fields(tmp_path: Path) -> None:
    command = tshark_command(
        tmp_path / "capture.pcap",
        None,
        "/usr/bin/tshark",
        session_reset_packets=0,
    )
    assert "-M" not in command
    assert "-c" not in command
    assert "-Y" not in command
    assert "-R" not in command
    for preference in TSHARK_STATE_PREFERENCES:
        assert preference in command
    extracted_fields = [
        command[index + 1]
        for index, value in enumerate(command[:-1])
        if value == "-e"
    ]
    assert extracted_fields == list(TSHARK_FIELDS)


def test_processing_policy_change_rejects_stale_part(tmp_path: Path) -> None:
    source_root = tmp_path / "pcaps"
    capture = source_root / "BenignTraffic" / "capture.pcap"
    capture.parent.mkdir(parents=True)
    write_test_pcap(capture)
    task = {
        "dataset": dataset(source_root),
        "path": str(capture),
        "member": None,
        "capture_id": "capture-id",
        "source_sha256": "a" * 64,
        "part_path": str(tmp_path / "part.part"),
        "schema_sha256": "b" * 64,
        "columns": columns(),
        "idle_seconds": 30.0,
        "maximum_packets": 64,
        "payload_prefix_bytes": 4096,
        "sanitized_l4_prefix_bytes": 2048,
        "maximum_active_flows": 25000,
    }
    metadata = process_capture(task)
    assert metadata["processing_policy_sha256"]
    changed = dict(task)
    changed["maximum_active_flows"] = 12000
    with pytest.raises(ValueError, match="stale resumable part"):
        process_capture(changed)


def test_process_capture_preserves_ipv4_fragment_payload(tmp_path: Path) -> None:
    source_root = tmp_path / "pcaps"
    capture = source_root / "DDoS-ICMP_Fragmentation" / "capture.pcap"
    capture.parent.mkdir(parents=True)
    transport = write_fragmented_icmp_pcap(capture)
    part = tmp_path / "fragment.part"
    metadata = process_capture(
        {
            "dataset": dataset(source_root),
            "path": str(capture),
            "member": None,
            "capture_id": "fragment-capture-id",
            "source_sha256": "c" * 64,
            "part_path": str(part),
            "schema_sha256": "d" * 64,
            "columns": columns(),
            "idle_seconds": 30.0,
            "maximum_packets": 64,
            "payload_prefix_bytes": 4096,
            "sanitized_l4_prefix_bytes": 2048,
            "maximum_active_flows": 100,
        }
    )
    assert metadata["counters"]["rows"] == 1
    with part.open("r", encoding="utf-8", newline="") as handle:
        row = next(csv.DictReader(handle, fieldnames=columns()))
    expected_payload = transport[4:]
    assert base64.b64decode(row["payload_b64"]) == expected_payload
    assert row["packet_payload_length_seq"] == (
        f"{1480 - 4};{len(transport) - 1480}"
    )
    assert row["transport_header_length_seq"] == "4;0"
    assert row["ip_fragment_offset_seq"] == "0;1480"
    assert row["ip_fragment_id_seq"] == "1234;1234"
    assert int(row["fragmented_packet_count"]) == 2
    assert int(row["noninitial_fragment_count"]) == 1
    assert int(row["port_a"]) == 0 and int(row["port_b"]) == 0
    assert int(row["payload_bytes_total"]) == len(expected_payload)
    histogram = [int(value) for value in row["payload_histogram"].split(";")]
    assert sum(histogram) == len(expected_payload)


def test_inventory_discovers_direct_and_archive_captures(tmp_path: Path) -> None:
    root = tmp_path / "sources"
    direct = root / "Direct" / "direct.pcap"
    direct.parent.mkdir(parents=True)
    write_test_pcap(direct)
    archive_path = root / "captures.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.write(direct, "Archived/member.pcap")
    catalog = {
        "schema_version": "caeos_unified_multimodal_catalog_v1",
        "datasets": [
            {
                **dataset(root),
                "include_globs": ["**/*.pcap", "*.zip"],
            }
        ],
    }
    manifest = build_source_manifest(catalog, io_threads=2)
    assert manifest["dataset_count"] == 1
    assert manifest["capture_count"] == 2
    assert manifest["full_source_hashes_computed"] is True
    assert all("sha256" in item for item in manifest["datasets"][0]["source_files"])
    validate_source_manifest(catalog, manifest)
    changed_catalog = json.loads(json.dumps(catalog))
    changed_catalog["datasets"][0]["label_binding"] = "different_binding"
    try:
        validate_source_manifest(changed_catalog, manifest)
    except ValueError as error:
        assert "catalog hash mismatch" in str(error)
    else:
        raise AssertionError("changed catalog must not reuse the source manifest")


def test_tshark_fields_preserve_noninitial_fragment_payload() -> None:
    fields = {name: "" for name in TSHARK_FIELDS}
    body = bytes(range(256)) + bytes(range(72))
    fields.update(
        {
            "frame.time_epoch": "1.125000000",
            "frame.len": "362",
            "frame.protocols": "eth:ethertype:ip:data",
            "ip.version": "4",
            "ip.src": "10.0.0.1",
            "ip.dst": "10.0.0.2",
            "ip.len": "348",
            "ip.dsfield": "0x00",
            "ip.flags.mf": "0",
            "ip.frag_offset": "1480",
            "ip.id": "0x0072",
            "ip.ttl": "64",
            "ip.proto": "1",
            "data.data": body.hex(),
        }
    )
    parsed = parse_tshark_fields([fields[name] for name in TSHARK_FIELDS])
    assert parsed is not None
    key, packet, metadata = parsed
    assert packet.timestamp_ns == 1_125_000_000
    assert packet.fragment_offset == 1480
    assert packet.ip_fragment_id == 0x72
    assert packet.transport_header_length == 0
    assert packet.payload == body
    assert packet.sanitized_l4_header == b""
    assert metadata["port_a"] == 0 and metadata["port_b"] == 0
    assert key[-1] == 1


def test_tar_archive_is_materialized_once_and_preserves_source_identity(
    tmp_path: Path,
) -> None:
    root = tmp_path / "sources"
    capture = root / "BenignTraffic" / "capture.pcap"
    capture.parent.mkdir(parents=True)
    write_test_pcap(capture)
    archive_path = root / "captures.tar.gz"
    member = "Archived/BenignTraffic/capture.pcap"
    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(capture, arcname=member)
    catalog = {
        "schema_version": "caeos_unified_multimodal_catalog_v1",
        "feature_reservoir": {
            "flow_idle_timeout_seconds": 30.0,
            "maximum_packets": 64,
            "payload_prefix_bytes": 4096,
        },
        "datasets": [
            {
                **dataset(root),
                "include_globs": ["*.tar.gz"],
            }
        ],
    }
    source_manifest = build_source_manifest(catalog, io_threads=2)
    source_dataset = source_manifest["datasets"][0]
    staged = materialize_tar_archives(
        catalog["datasets"][0], source_dataset, tmp_path / "output", io_threads=2
    )
    assert len(staged) == 1
    staged_path = Path(next(iter(staged.values())))
    assert staged_path.is_file()
    tasks = capture_tasks(
        catalog["datasets"][0],
        source_dataset,
        tmp_path / "output",
        {
            "columns": [{"name": name} for name in columns()],
        },
        catalog["feature_reservoir"],
        maximum_active_flows=100,
        staged_members=staged,
    )
    assert len(tasks) == 1
    assert tasks[0]["path"] == str(staged_path)
    assert tasks[0]["member"] is None
    assert tasks[0]["source_member_override"] == member
    metadata = process_capture(tasks[0])
    assert metadata["source_path"] == str(archive_path)
    assert metadata["source_member"] == member
    assert metadata["counters"]["rows"] == 1


def test_mixed_capture_labels_remain_deferred(tmp_path: Path) -> None:
    item = dataset(tmp_path)
    item["label_policy"] = "deferred_ground_truth_join"
    label = path_label(item, "normal_attack_pcaps/normal_XSS/mixed.pcap")
    assert label.status == "deferred_label_join"
    assert label.binary_label == -1


def test_attack_labels_have_binary_category_and_subcategory(tmp_path: Path) -> None:
    item = dataset(tmp_path)
    item["label_policy"] = "edge_capture_name"
    item["label_binding"] = "capture_path_with_csv_crosscheck"
    label = path_label(item, "Attack traffic/OS Fingerprinting attack.pcap")
    assert label.traffic_class == "Malicious"
    assert label.binary_label == 1
    assert label.attack_category == "Reconnaissance"
    assert label.attack_subcategory == "OS_Fingerprinting_attack"


def test_ciciot2023_explicit_family_controls_attack_category() -> None:
    expected = {
        "Benign": "Benign",
        "DDoS": "DDoS",
        "DoS": "DoS",
        "Recon": "Reconnaissance",
        "BruteForce": "Brute_Force",
        "Spoofing": "Spoofing_MITM",
        "Mirai": "Botnet_Malware",
        "Web": "Web_Attack",
    }
    for fine_label, family_label in CICIOT2023_FAMILIES.items():
        binary_label = 0 if family_label == "Benign" else 1
        label = LabelRecord(
            "capture_path", fine_label, family_label, binary_label
        )
        assert label.attack_category == expected[family_label]

    assert (
        LabelRecord("capture_path", "Backdoor_Malware", "Web", 1).attack_category
        == "Web_Attack"
    )
    assert (
        LabelRecord("capture_path", "BrowserHijacking", "Web", 1).attack_category
        == "Web_Attack"
    )


def test_pending_labels_never_create_final_dataset_csv(tmp_path: Path) -> None:
    source_root = tmp_path / "pcaps"
    capture = source_root / "mixed.pcap"
    source_root.mkdir(parents=True)
    write_test_pcap(capture)
    item = dataset(source_root)
    item["label_policy"] = "deferred_ground_truth_join"
    item["label_binding"] = "five_tuple_time_interval_and_ground_truth"
    schema_path = Path(__file__).parents[1] / "configs" / "unified_multimodal_v4.schema.json"
    with schema_path.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    part = tmp_path / "capture.part"
    metadata = process_capture(
        {
            "dataset": item,
            "path": str(capture),
            "member": None,
            "capture_id": "capture-id",
            "source_sha256": "a" * 64,
            "part_path": str(part),
            "schema_sha256": canonical_json_hash(schema),
            "columns": columns(),
            "idle_seconds": 30.0,
            "maximum_packets": 64,
            "payload_prefix_bytes": 4096,
            "sanitized_l4_prefix_bytes": 2048,
            "maximum_active_flows": 100,
        }
    )
    result = merge_parts(
        item,
        [metadata],
        tmp_path / "output",
        columns(),
        canonical_json_hash(schema),
        "b" * 64,
        parser_processes=1,
    )
    assert result["features_materialized"] is True
    assert result["csv_materialized"] is False
    assert result["formal_label_ready"] is False
    assert not (tmp_path / "output" / "ciciot2023.csv").exists()
    assert Path(result["staged_feature_path"]).suffix == ".part"
