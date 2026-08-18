from __future__ import annotations

import csv

from prepare_caeos_unified_multimodal_csv import TSHARK_TSV_FIELD_LIMIT_BYTES


def test_tshark_tsv_field_limit_accepts_full_raw_packet_fields() -> None:
    assert TSHARK_TSV_FIELD_LIMIT_BYTES == 64 * 1024 * 1024
    assert csv.field_size_limit() >= TSHARK_TSV_FIELD_LIMIT_BYTES
