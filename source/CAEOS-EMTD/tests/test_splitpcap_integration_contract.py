from __future__ import annotations

import struct
from pathlib import Path

import dpkt

from scripts.patch_splitpcap_upstream import patch_source
from scripts.validate_splitpcap_integrity import validate


def write_capture(path: Path, frames: list[bytes] | list[tuple[float, bytes]]) -> None:
    with path.open("wb") as handle:
        writer = dpkt.pcap.Writer(handle)
        for index, item in enumerate(frames, start=1):
            timestamp, frame = item if isinstance(item, tuple) else (float(index), item)
            writer.writepkt(frame, ts=timestamp)
        writer.close()


def test_integrity_validator_is_order_independent(tmp_path: Path) -> None:
    frames = [b"a" * 64, b"b" * 128, b"c" * 2048]
    source = tmp_path / "source.pcap"
    first = tmp_path / "0.pcap"
    second = tmp_path / "1.pcap"
    write_capture(source, frames)
    write_capture(first, [(3.0, frames[2]), (1.0, frames[0])])
    write_capture(second, [(2.0, frames[1])])

    result = validate(source, [first, second])

    assert result["exact_multiset_match"] is True
    assert result["fingerprint"]["packet_count"] == 3


def test_integrity_validator_rejects_changed_packet(tmp_path: Path) -> None:
    source = tmp_path / "source.pcap"
    piece = tmp_path / "0.pcap"
    write_capture(source, [b"a" * 64])
    write_capture(piece, [b"b" * 64])

    try:
        validate(source, [piece])
    except ValueError as error:
        assert "integrity mismatch" in str(error)
    else:
        raise AssertionError("changed packet was accepted")


def test_patcher_removes_fixed_2000_byte_buffer(tmp_path: Path) -> None:
    checkout = tmp_path / "checkout" / "src"
    checkout.mkdir(parents=True)
    source = checkout / "main.cpp"
    source.write_text(
        "pcap_t * wtpcap = pcap_open_dead(DLT_ETH, 65535);\n"
        "int splitpcaps(char *pcapname, char * dst_dir, int piece_num=10)\n"
        "display((unsigned char *)pktdata, pktheader.len);\n"
        "pcap_pkthdr new_pkthdr = pktheader;\n"
        "u_char new_data[2000] = { 0};\n\t\t\tmemcpy(new_data, pktdata, new_pkthdr.len);\n"
        "flow_tuple tuple = gather_flow_tuple(pktdata);\n"
        "pcap_dumper_t * wtpcap_dump = wtpcap_dumps[tuple._hash % piece_num];\n"
        "pcap_dump((u_char*) wtpcap_dump, &new_pkthdr, new_data);\n"
        "pcap_pkthdr pktheader;\n\t\tconst u_char *pktdata = pcap_next(rdpcap, &pktheader);\n"
        "\t\tif (pktdata != NULL)\n\t\t{\n\t\t}\n\t\telse\n\t\t{\n\t\t\tbreak;\n"
        "\t\t}\n\t}\n\t//close pcap handle\n"
        "if (splitpcaps(pcapname, dst_dir,piece_num) <0 )\n"
        "{\n\tprintf(\"Error!!!!%s\\n\", pcapname);\n}\n",
        encoding="utf-8",
    )

    patch_source(source)
    patched = source.read_text(encoding="utf-8")

    assert "new_data[2000]" not in patched
    assert "caeos_flow_hash" in patched
    assert "pcap_open_dead_with_tstamp_precision" in patched
    assert "&new_pkthdr, pktdata" in patched
    assert "display((unsigned char *)pktdata" not in patched
    assert "pcap_next_ex" in patched
    assert "pcap_geterr(rdpcap)" in patched
    assert "pcap_pkthdr new_pkthdr = *pktheader;" in patched
    assert "int split_status = splitpcaps" in patched
    assert "return 2;" in patched
