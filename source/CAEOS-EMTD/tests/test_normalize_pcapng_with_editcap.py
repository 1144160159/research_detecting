import importlib.util
import struct
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "normalize_pcapng_with_editcap.py"
SPEC = importlib.util.spec_from_file_location("normalize_pcapng", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def block(block_type: int, body: bytes) -> bytes:
    padding = b"\x00" * ((-len(body)) % 4)
    length = 12 + len(body) + len(padding)
    return struct.pack("<II", block_type, length) + body + padding + struct.pack("<I", length)


def test_multi_interface_pcapng_and_pcap_have_same_ordered_fingerprint(tmp_path):
    first = b"\x00\x01\x02\x03"
    second = b"\x10\x11\x12"
    pcapng = tmp_path / "source.pcapng"
    shb = block(MODULE.PCAPNG_SHB, struct.pack("<IHHq", 0x1A2B3C4D, 1, 0, -1))
    idb_a = block(MODULE.PCAPNG_IDB, struct.pack("<HHI", 1, 0, 65535))
    idb_b = block(MODULE.PCAPNG_IDB, struct.pack("<HHI", 1, 0, 262144))
    epb_a = block(
        MODULE.PCAPNG_EPB,
        struct.pack("<IIIII", 0, 0, 1_000_001, len(first), 8) + first,
    )
    epb_b = block(
        MODULE.PCAPNG_EPB,
        struct.pack("<IIIII", 1, 0, 2_000_002, len(second), 7) + second,
    )
    pcapng.write_bytes(shb + idb_a + idb_b + epb_a + epb_b)

    pcap = tmp_path / "normalized.pcap"
    global_header = b"\xd4\xc3\xb2\xa1" + struct.pack("<HHIIII", 2, 4, 0, 0, 262144, 1)
    record_a = struct.pack("<IIII", 1, 1, len(first), 8) + first
    record_b = struct.pack("<IIII", 2, 2, len(second), 7) + second
    pcap.write_bytes(global_header + record_a + record_b)

    source = MODULE.capture_fingerprint(pcapng)
    normalized = MODULE.capture_fingerprint(pcap)

    assert source["interface_count"] == 2
    assert source["snaplens"] == [65535, 262144]
    assert source["linktypes"] == normalized["linktypes"] == [1]
    assert MODULE.packet_fields(source) == MODULE.packet_fields(normalized)
