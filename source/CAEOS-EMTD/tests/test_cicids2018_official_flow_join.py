from __future__ import annotations

import csv
from pathlib import Path

from audit_caeos_cicids2018_official_flow_join import (
    field_indices,
    normalized_number,
    normalized_timestamp,
    row_signature,
)


OFFICIAL_HEADER = [
    "Dst Port", "Protocol", "Timestamp", "Flow Duration", "Tot Fwd Pkts",
    "Tot Bwd Pkts", "TotLen Fwd Pkts", "TotLen Bwd Pkts", "Fwd Pkt Len Max",
    "Fwd Pkt Len Min", "Bwd Pkt Len Max", "Bwd Pkt Len Min", "FIN Flag Cnt",
    "SYN Flag Cnt", "RST Flag Cnt", "PSH Flag Cnt", "ACK Flag Cnt",
    "URG Flag Cnt", "Init Fwd Win Byts", "Init Bwd Win Byts",
    "Fwd Act Data Pkts", "Fwd Seg Size Min", "Label",
]

GENERATED_HEADER = [
    "Dst Port", "Protocol", "Timestamp", "Flow Duration", "Total Fwd Packet",
    "Total Bwd packets", "Total Length of Fwd Packet", "Total Length of Bwd Packet",
    "Fwd Packet Length Max", "Fwd Packet Length Min", "Bwd Packet Length Max",
    "Bwd Packet Length Min", "FIN Flag Count", "SYN Flag Count", "RST Flag Count",
    "PSH Flag Count", "ACK Flag Count", "URG Flag Count", "FWD Init Win Bytes",
    "Bwd Init Win Bytes", "Fwd Act Data Pkts", "Fwd Seg Size Min", "Label",
]


def test_official_and_regenerated_aliases_produce_same_signature() -> None:
    official = [
        "443", "6", "15/02/2018 14:23:34", "100", "2", "3", "40", "50",
        "30", "10", "40", "10", "0", "1", "0", "1", "3", "0", "8192",
        "1024", "1", "20", "Benign",
    ]
    generated = official.copy()
    generated[2] = "15/02/2018 02:23:34 PM"
    generated[6] = "40.0"

    assert row_signature(official, field_indices(OFFICIAL_HEADER, True)) == row_signature(
        generated, field_indices(GENERATED_HEADER, False)
    )


def test_numeric_and_timestamp_normalization() -> None:
    assert normalized_number("40.000") == "40"
    assert normalized_number("0.1250") == "0.125"
    assert normalized_timestamp("15/02/2018 02:23:34 PM") == normalized_timestamp(
        "15/02/2018 14:23:34"
    )
