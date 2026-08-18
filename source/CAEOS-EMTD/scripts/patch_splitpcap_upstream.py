from __future__ import annotations

import argparse
from pathlib import Path


SAFE_HASH_IMPLEMENTATION = r'''
static unsigned short caeos_read_be16(const unsigned char *value) {
    return (unsigned short)(((unsigned short)value[0] << 8) | value[1]);
}

static unsigned int caeos_fnv1a(const unsigned char *value, size_t length, unsigned int hash = 2166136261u) {
    for (size_t index = 0; index < length; ++index) {
        hash ^= value[index];
        hash *= 16777619u;
    }
    return hash;
}

static unsigned int caeos_flow_hash(const unsigned char *data, unsigned int caplen, int datalink) {
    if (datalink != DLT_ETH || caplen < 14) {
        return caeos_fnv1a(data, caplen < 64 ? caplen : 64);
    }
    unsigned int offset = 14;
    unsigned short ether_type = caeos_read_be16(data + 12);
    while ((ether_type == 0x8100 || ether_type == 0x88a8) && caplen >= offset + 4) {
        ether_type = caeos_read_be16(data + offset + 2);
        offset += 4;
    }

    unsigned char endpoint_a[18] = {0};
    unsigned char endpoint_b[18] = {0};
    size_t endpoint_length = 0;
    unsigned char protocol = 0;
    unsigned short source_port = 0;
    unsigned short destination_port = 0;

    if (ether_type == 0x0800 && caplen >= offset + 20) {
        unsigned int ihl = (unsigned int)(data[offset] & 0x0f) * 4;
        if (ihl < 20 || caplen < offset + ihl) {
            return caeos_fnv1a(data, caplen < 64 ? caplen : 64);
        }
        protocol = data[offset + 9];
        memcpy(endpoint_a, data + offset + 12, 4);
        memcpy(endpoint_b, data + offset + 16, 4);
        endpoint_length = 6;
        unsigned short fragment = caeos_read_be16(data + offset + 6);
        bool fragmented = (fragment & 0x3fff) != 0;
        unsigned int transport_offset = offset + ihl;
        if (!fragmented && (protocol == 6 || protocol == 17) && caplen >= transport_offset + 4) {
            source_port = caeos_read_be16(data + transport_offset);
            destination_port = caeos_read_be16(data + transport_offset + 2);
        }
        endpoint_a[4] = (unsigned char)(source_port >> 8);
        endpoint_a[5] = (unsigned char)source_port;
        endpoint_b[4] = (unsigned char)(destination_port >> 8);
        endpoint_b[5] = (unsigned char)destination_port;
    } else if (ether_type == 0x86dd && caplen >= offset + 40) {
        protocol = data[offset + 6];
        memcpy(endpoint_a, data + offset + 8, 16);
        memcpy(endpoint_b, data + offset + 24, 16);
        endpoint_length = 18;
        // A conservative zero-port key keeps every IPv6 flow between the same
        // endpoints in one shard, including extension-header traffic.
    } else {
        memcpy(endpoint_a, data + 6, 6);
        memcpy(endpoint_b, data, 6);
        endpoint_length = 6;
    }

    const unsigned char *first = endpoint_a;
    const unsigned char *second = endpoint_b;
    if (memcmp(endpoint_a, endpoint_b, endpoint_length) > 0) {
        first = endpoint_b;
        second = endpoint_a;
    }
    unsigned int hash = caeos_fnv1a(&protocol, 1);
    hash = caeos_fnv1a(first, endpoint_length, hash);
    return caeos_fnv1a(second, endpoint_length, hash);
}

'''


def patch_source(path: Path) -> None:
    raw = path.read_bytes()
    try:
        source = raw.decode("utf-8")
    except UnicodeDecodeError:
        source = raw.decode("gb18030")
    source = source.replace("\r\n", "\n")
    if "#include <errno.h>" not in source:
        source = source.replace("#include <time.h>", "#include <time.h>\n#include <errno.h>", 1)
    marker = "int splitpcaps(char *pcapname, char * dst_dir, int piece_num=10)"
    if "caeos_flow_hash" not in source:
        if marker not in source:
            raise ValueError("splitpcap function marker not found")
        source = source.replace(marker, SAFE_HASH_IMPLEMENTATION + marker, 1)

    source = source.replace(
        "pcap_t * wtpcap = pcap_open_dead(DLT_ETH, 65535);",
        "pcap_t * wtpcap = pcap_open_dead_with_tstamp_precision(\n"
        "            pcap_datalink(rdpcap), pcap_snapshot(rdpcap),\n"
        "            pcap_get_tstamp_precision(rdpcap));",
    )
    source = source.replace(
        'char mkdir_cmd[256] = { 0 };\n\tsprintf(mkdir_cmd, "mkdir %s", dst_dir);\n\tsystem(mkdir_cmd);',
        'if (mkdir(dst_dir, 0755) != 0 && errno != EEXIST) {\n'
        '        printf("Error when create dst directory:%s\\n", dst_dir);\n'
        '        pcap_close(rdpcap);\n'
        '        return -2;\n'
        '    }',
    )
    source = source.replace("display((unsigned char *)pktdata, pktheader.len);", "// Per-packet dumping is disabled for bounded logs.")
    source = source.replace(
        "u_char new_data[2000] = { 0};\n\t\t\tmemcpy(new_data, pktdata, new_pkthdr.len);",
        "// Packet bytes are written directly; caplen may exceed 2000 bytes and may be less than wire len.",
    )
    source = source.replace(
        "flow_tuple tuple = gather_flow_tuple(pktdata);",
        "unsigned int shard_hash = caeos_flow_hash(pktdata, pktheader->caplen, pcap_datalink(rdpcap));",
    )
    source = source.replace(
        "pcap_pkthdr pktheader;\n\t\tconst u_char *pktdata = pcap_next(rdpcap, &pktheader);\n\t\tif (pktdata != NULL)",
        "pcap_pkthdr *pktheader = NULL;\n"
        "        const u_char *pktdata = NULL;\n"
        "        int read_status = pcap_next_ex(rdpcap, &pktheader, &pktdata);\n"
        "        if (read_status == 1)",
    )
    source = source.replace(
        "pcap_pkthdr new_pkthdr = pktheader;",
        "pcap_pkthdr new_pkthdr = *pktheader;",
    )
    source = source.replace(
        "\t\t}\n\t\telse\n\t\t{\n\t\t\tbreak;\n\t\t}\n\t}",
        "        }\n"
        "        else if (read_status == -2)\n"
        "        {\n"
        "            break;\n"
        "        }\n"
        "        else\n"
        "        {\n"
        "            fprintf(stderr, \"pcap read failed after %d packets: %s\\n\", nb_transfer, pcap_geterr(rdpcap));\n"
        "            return -3;\n"
        "        }\n"
        "    }",
    )
    source = source.replace(
        "pcap_dumper_t * wtpcap_dump = wtpcap_dumps[tuple._hash % piece_num];",
        "pcap_dumper_t * wtpcap_dump = wtpcap_dumps[shard_hash % piece_num];",
    )
    source = source.replace(
        "pcap_dump((u_char*) wtpcap_dump, &new_pkthdr, new_data);",
        "pcap_dump((u_char*) wtpcap_dump, &new_pkthdr, pktdata);",
    )
    source = source.replace(
        "if (splitpcaps(pcapname, dst_dir,piece_num) <0 )",
        "int split_status = splitpcaps(pcapname, dst_dir, piece_num);\n"
        "    if (split_status < 0)",
    )
    source = source.replace(
        'printf("Error!!!!%s\\n", pcapname);',
        'fprintf(stderr, "splitpcap failed with status %d: %s\\n", split_status, pcapname);\n'
        "        return 2;",
    )
    required = (
        "caeos_flow_hash",
        "pcap_open_dead_with_tstamp_precision",
        "pcap_dump((u_char*) wtpcap_dump, &new_pkthdr, pktdata);",
        "Per-packet dumping is disabled",
        "pcap_next_ex",
        "pcap_geterr(rdpcap)",
        "int split_status = splitpcaps",
        "return 2;",
    )
    if any(value not in source for value in required):
        raise ValueError("splitpcap safety patch did not apply completely")
    if "new_data[2000]" in source:
        raise ValueError("unsafe fixed packet buffer remains")
    if "system(mkdir_cmd)" in source:
        raise ValueError("unsafe shell directory creation remains")
    if "pcap_next(rdpcap" in source:
        raise ValueError("pcap_next still conflates read errors with EOF")
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(source)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("checkout", type=Path)
    args = parser.parse_args()
    patch_source(args.checkout / "src" / "main.cpp")


if __name__ == "__main__":
    main()
