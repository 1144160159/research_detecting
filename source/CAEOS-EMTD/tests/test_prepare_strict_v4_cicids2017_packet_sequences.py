from __future__ import annotations

import csv
from pathlib import Path

from prepare_strict_v4_cicids2017_packet_sequences import (
    LabelFlow,
    capture_wall_clock_adjustment_us,
    capture_format_from_magic,
    canonical_flow_key,
    interval_match,
    normalize_fine_label,
    parse_timestamp_wall_us,
    select_balanced_flows,
    timestamp_resolution_us,
)
from strict_v4_cicids2017_attack_family import FINE_TO_FAMILY


HEADER = [
    "Flow ID",
    "Source IP",
    "Source Port",
    "Destination IP",
    "Destination Port",
    "Protocol",
    "Timestamp",
    "Flow Duration",
    "Label",
]


def write_labels(path: Path) -> None:
    fine_labels = sorted(FINE_TO_FAMILY)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADER)
        for index, label in enumerate(fine_labels):
            for duplicate in range(3):
                writer.writerow(
                    [
                        f"flow-{index}-{duplicate}",
                        f"10.0.{index}.1",
                        1000 + duplicate,
                        "192.168.0.1",
                        80,
                        6,
                        f"05/07/2017 08:{index:02d}:00",
                        1_000_000,
                        label,
                    ]
                )


def test_balanced_selection_is_deterministic(tmp_path: Path) -> None:
    label_path = tmp_path / "Wednesday-workingHours.pcap_ISCX.csv"
    write_labels(label_path)
    first, first_counts = select_balanced_flows(
        tmp_path, seed=17, maximum_per_family=2
    )
    second, second_counts = select_balanced_flows(
        tmp_path, seed=17, maximum_per_family=2
    )
    assert [flow.flow_id for flow in first] == [flow.flow_id for flow in second]
    assert first_counts == second_counts
    selected_counts = {}
    for flow in first:
        selected_counts[flow.family] = selected_counts.get(flow.family, 0) + 1
    assert set(selected_counts) == set(FINE_TO_FAMILY.values())
    assert set(selected_counts.values()) == {2}


def test_flow_key_is_bidirectional() -> None:
    forward = canonical_flow_key(b"\x0a\x00\x00\x01", 1234, b"\x0a\x00\x00\x02", 80, 6)
    reverse = canonical_flow_key(b"\x0a\x00\x00\x02", 80, b"\x0a\x00\x00\x01", 1234, 6)
    assert forward == reverse


def test_interval_match_obeys_tolerance() -> None:
    flow = LabelFlow(
        flow_id="flow",
        capture_id="capture",
        pcap_name="Wednesday-workingHours.pcap",
        source_ip=b"\x0a\x00\x00\x01",
        source_port=1234,
        destination_ip=b"\x0a\x00\x00\x02",
        destination_port=80,
        protocol=6,
        start_wall_us=10_000_000,
        end_wall_us=11_000_000,
        fine_label="Bot",
        family="Botnet",
        priority=1,
    )
    assert interval_match([flow], [flow.start_wall_us], 9_500_000, 500_000) == flow
    assert interval_match([flow], [flow.start_wall_us], 9_499_999, 500_000) is None


def test_timestamp_parser_uses_wall_clock_epoch() -> None:
    assert parse_timestamp_wall_us("05/07/2017 08:42:00") == 1499244120000000
    assert timestamp_resolution_us("05/07/2017 08:42:00") == 1_000_000
    assert timestamp_resolution_us("05/07/2017 08:42") == 60_000_000


def test_afternoon_capture_restores_omitted_pm_hour() -> None:
    assert (
        capture_wall_clock_adjustment_us(
            "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX",
            "07/07/2017 1:02",
        )
        == 43_200_000_000
    )
    assert (
        capture_wall_clock_adjustment_us(
            "Friday-WorkingHours-Morning.pcap_ISCX",
            "07/07/2017 1:02",
        )
        == 0
    )
    assert (
        capture_wall_clock_adjustment_us(
            "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX",
            "07/07/2017 13:02",
        )
        == 0
    )


def test_web_attack_encoding_variant_is_normalized() -> None:
    assert (
        normalize_fine_label("Web Attack \ufffd Brute Force")
        == "Web Attack - Brute Force"
    )


def test_exact_duplicate_rows_do_not_break_selection(tmp_path: Path) -> None:
    label_path = tmp_path / "Wednesday-workingHours.pcap_ISCX.csv"
    write_labels(label_path)
    with label_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    with label_path.open("a", encoding="utf-8", newline="") as handle:
        csv.writer(handle).writerow(rows[1])
    selected, counters = select_balanced_flows(
        tmp_path, seed=17, maximum_per_family=2
    )
    assert selected
    assert counters["valid_rows"] == len(rows)


def test_capture_magic_distinguishes_pcapng_and_pcap() -> None:
    assert capture_format_from_magic(b"\x0a\x0d\x0d\x0a") == "pcapng"
    assert capture_format_from_magic(b"\xd4\xc3\xb2\xa1") == "pcap"
    assert capture_format_from_magic(b"\x00\x00\x00\x00") == "unknown"
