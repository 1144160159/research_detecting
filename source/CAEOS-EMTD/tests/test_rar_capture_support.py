from __future__ import annotations

from caeos_unified_dataset import parse_unrar_verbose_list


def test_parse_unrar_verbose_list_keeps_suffixless_capture_members() -> None:
    output = """
        Name: pcap/capDESKTOP-1-10.0.0.1
        Type: File
        Size: 263181292
 Packed size: 234279148
       CRC32: FD648ABB

        Name: pcap/capDESKTOP-1-10.0.0.2
        Type: File
        Size: 287024196
 Packed size: 255071910
       CRC32: E069FD06
"""
    members = parse_unrar_verbose_list(output)

    assert [item["name"] for item in members] == [
        "pcap/capDESKTOP-1-10.0.0.1",
        "pcap/capDESKTOP-1-10.0.0.2",
    ]
    assert [item["size_bytes"] for item in members] == [263181292, 287024196]
    assert members[0]["crc32"] == "fd648abb"
    assert members[0]["capture_detection"] == "dataset_contract_all_rar_files"
