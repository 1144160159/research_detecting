from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from hft_mgbs.features import PacketRecord
from hft_mgbs.unified_feature_reservoir import (
    AUDIT_ONLY_COLUMNS,
    CONTEXT_COLUMNS,
    CSV_SEQUENCE_COLUMNS,
    DERIVED_FEATURE_COLUMNS,
    ENCRYPTED_STRUCTURE_COLUMNS,
    INTEGER_ONLINE_COLUMNS,
    MODEL_CANDIDATE_PERSISTENT_COLUMNS,
    ONLINE_EXTRACTABLE_COLUMNS,
    SAFE_SCALAR_COLUMNS,
    SEQUENCE_COLUMNS,
    TARGET_COLUMNS,
    PacketMetadata,
    UnifiedPcapExportContext,
    UnifiedFeatureReservoir,
    UnifiedFeatureReservoirError,
    default_reservoir_policy,
    materialize_unified_pcap_row,
    validate_reservoir_policy,
)


ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads(
    (ROOT / "configs/unified_feature_reservoir_v1.json").read_text(encoding="utf-8")
)


def packet(
    timestamp: float,
    *,
    reverse: bool = False,
    payload: bytes = b"",
    flags: int = 0,
    dst_port: int = 443,
) -> PacketRecord:
    src, dst = ("10.0.0.2", "10.0.0.1") if reverse else ("10.0.0.1", "10.0.0.2")
    sport, dport = (dst_port, 12345) if reverse else (12345, dst_port)
    return PacketRecord(timestamp, src, dst, sport, dport, 6, 60 + len(payload), payload, flags)


class UnifiedFeatureReservoirTest(unittest.TestCase):
    def test_policy_and_embedded_default_are_identical(self) -> None:
        validate_reservoir_policy(POLICY)
        self.assertEqual(POLICY, default_reservoir_policy())
        self.assertEqual(len(SAFE_SCALAR_COLUMNS), 85)
        self.assertEqual(len(SEQUENCE_COLUMNS), 17)
        self.assertEqual(len(ENCRYPTED_STRUCTURE_COLUMNS), 8)
        self.assertEqual(len(CONTEXT_COLUMNS), 10)
        self.assertEqual(len(MODEL_CANDIDATE_PERSISTENT_COLUMNS), 116)
        self.assertEqual(len(ONLINE_EXTRACTABLE_COLUMNS), 120)
        self.assertEqual(len(AUDIT_ONLY_COLUMNS), 17)
        self.assertEqual(len(TARGET_COLUMNS), 6)
        self.assertEqual(len(DERIVED_FEATURE_COLUMNS), 7)

    def test_policy_rejects_source_schema_drift(self) -> None:
        value = json.loads(json.dumps(POLICY))
        value["source_contracts"]["caeos_schema_sha256"] = "0" * 64
        with self.assertRaises(UnifiedFeatureReservoirError):
            validate_reservoir_policy(value)

    def test_invalid_packet_metadata_fails_before_state_update(self) -> None:
        reservoir = UnifiedFeatureReservoir(POLICY)
        with self.assertRaisesRegex(UnifiedFeatureReservoirError, "ip_version"):
            reservoir.observe_batch(
                (packet(0.0),),
                (PacketMetadata(ip_version=5),),
            )
        self.assertEqual(reservoir._flows, {})

    def test_all_flow_scalars_sequences_and_context_are_closed(self) -> None:
        reservoir = UnifiedFeatureReservoir(POLICY)
        packets = (
            packet(1.0, payload=b"abc", flags=0x02),
            packet(1.1, reverse=True, payload=b"de", flags=0x12),
            packet(1.2, payload=b"f", flags=0x10),
        )
        metadata = tuple(
            PacketMetadata(
                ip_version=4,
                ip_length=item.wire_length - 14,
                ip_dscp_ecn=index,
                transport_header_length=20,
                packet_ttl=64 - index,
                tcp_window=4096,
                sanitized_l4=b"header" + item.payload,
            )
            for index, item in enumerate(packets)
        )
        key = reservoir.canonical_key(packets[0])
        result = reservoir.observe_batch(packets, metadata, deep_flow_keys=(key,))
        self.assertTrue(result.receipt["feature_reservoir_closed"])
        self.assertEqual(result.receipt["feature_records"], 1)
        record = result.flow_records[0]
        self.assertEqual(set(record.safe_scalars), set(SAFE_SCALAR_COLUMNS))
        self.assertEqual(set(record.packet_sequences), set(SEQUENCE_COLUMNS))
        self.assertEqual(
            set(record.persistent_features), set(ONLINE_EXTRACTABLE_COLUMNS)
        )
        self.assertEqual(record.safe_scalars["packet_count_total"], 3.0)
        self.assertEqual(record.safe_scalars["direction_switch_count"], 2.0)
        self.assertEqual(record.safe_scalars["tcp_syn_flag_count"], 2.0)
        self.assertEqual(record.packet_sequences["direction_seq"], (1, -1, 1))
        self.assertEqual(len(record.payload_features["payload_histogram"]), 256)
        self.assertEqual(sum(record.payload_features["payload_histogram"]), 6)
        self.assertEqual(record.persistent_features["packet_count_stored"], 3)
        self.assertEqual(record.persistent_features["port_a"], 12345)
        self.assertEqual(record.persistent_features["port_b"], 443)
        self.assertEqual(
            record.persistent_features["application_protocol_hint"], "HTTPS_or_encrypted"
        )
        self.assertEqual(
            record.payload_features["sanitized_l4_bytes_total"],
            sum(len(b"header" + item.payload) for item in packets),
        )
        self.assertTrue(record.quality["payload_histogram_complete"])
        self.assertEqual(len(result.window_contexts), 1)
        context = result.window_contexts[0]
        self.assertEqual(set(context) - {"window_id", "window_start_s"}, set(CONTEXT_COLUMNS))
        self.assertFalse(any("10.0.0" in str(value) for value in context.values()))

    def test_deferred_deep_tier_is_explicit_missingness_not_zero_evidence(self) -> None:
        reservoir = UnifiedFeatureReservoir(POLICY)
        result = reservoir.observe_batch((packet(2.0, payload=b"secret"),))
        record = result.flow_records[0]
        self.assertFalse(record.quality["deep_tier_selected"])
        self.assertTrue(record.quality["missingness"]["deep_tier_not_selected"])
        self.assertEqual(record.payload_features["payload_histogram"], tuple())
        self.assertEqual(result.receipt["deep_deferred_flows"], 1)

    def test_tls_and_quic_structure_are_parsed_without_decryption(self) -> None:
        reservoir = UnifiedFeatureReservoir(POLICY)
        tls = b"\x16\x03\x03\x00\x04\x01\x00\x00\x00"
        quic = b"\xc0\x00\x00\x00\x01"
        packets = (packet(3.0, payload=tls), packet(3.1, payload=quic))
        key = reservoir.canonical_key(packets[0])
        result = reservoir.observe_batch(
            packets,
            (PacketMetadata(ip_version=4), PacketMetadata(ip_version=4)),
            deep_flow_keys=(key,),
        )
        encrypted = result.flow_records[0].encrypted_protocol_structure
        self.assertEqual(set(encrypted), set(ENCRYPTED_STRUCTURE_COLUMNS))
        self.assertEqual(encrypted["tls_record_type_seq"], (22,))
        self.assertEqual(encrypted["tls_record_version_seq"], (0x0303,))
        self.assertEqual(encrypted["tls_client_hello_present"], 1)
        self.assertEqual(encrypted["quic_long_header_packet_count"], 1)
        self.assertEqual(encrypted["quic_version_seq"], (1,))

    def test_sixty_four_packet_boundary_creates_exact_continuation_segment(self) -> None:
        reservoir = UnifiedFeatureReservoir(POLICY)
        packets = tuple(packet(4.0 + index * 0.001) for index in range(65))
        result = reservoir.observe_batch(packets)
        self.assertEqual(len(result.flow_records), 2)
        first, second = result.flow_records
        self.assertEqual(first.flow_segment_index, 0)
        self.assertEqual(second.flow_segment_index, 1)
        self.assertEqual(len(first.packet_sequences["packet_length_seq"]), 64)
        self.assertEqual(len(second.packet_sequences["packet_length_seq"]), 1)
        self.assertTrue(first.quality["sequence_complete"])
        self.assertTrue(second.quality["sequence_complete"])
        self.assertFalse(first.quality["missingness"]["packet_sequence_truncated"])
        self.assertEqual(result.receipt["observed_flow_segments"], 2)
        self.assertTrue(result.receipt["feature_reservoir_closed"])

    def test_canonical_and_initiator_relative_directions_are_distinct(self) -> None:
        reservoir = UnifiedFeatureReservoir(POLICY)
        packets = (
            packet(5.0, reverse=True),
            packet(5.1, reverse=False),
        )
        record = reservoir.observe_batch(packets).flow_records[0]
        self.assertEqual(record.packet_sequences["direction_seq"], (-1, 1))
        self.assertEqual(
            record.derived_features["initiator_relative_direction_seq"], (1, -1)
        )

    def test_complete_record_materialises_exact_143_column_row(self) -> None:
        reservoir = UnifiedFeatureReservoir(POLICY)
        item = packet(6.0, payload=b"abc")
        key = reservoir.canonical_key(item)
        record = reservoir.observe_batch(
            (item,),
            (
                PacketMetadata(
                    ip_version=4,
                    ip_length=49,
                    transport_header_length=20,
                    packet_ttl=64,
                    sanitized_l4=b"headerabc",
                    sanitized_l4_total=9,
                ),
            ),
            deep_flow_keys=(key,),
        ).flow_records[0]
        context = UnifiedPcapExportContext(
            schema_version="caeos_unified_multimodal_csv_schema_v4",
            dataset_id="online_capture",
            dataset_role="external_test",
            capture_id="capture-1",
            source_container_sha256="a" * 64,
            source_member="capture.pcap",
            label_status="aligned",
            label_source="operator",
            label_mapping_version="caeos_attack_taxonomy_v1",
            dataset_native_label="Benign",
            traffic_class="Benign",
            attack_category="Benign",
            attack_subcategory="Benign",
            fine_label="Benign",
            family_label="benign",
            binary_label=0,
            sample_disambiguator="0:0",
        )
        row = materialize_unified_pcap_row(record, context)
        self.assertEqual(len(row), 143)
        self.assertEqual(
            set(row),
            set(AUDIT_ONLY_COLUMNS)
            | set(TARGET_COLUMNS)
            | set(ONLINE_EXTRACTABLE_COLUMNS),
        )
        self.assertEqual(row["packet_count_stored"], 1)
        self.assertEqual(
            sum(int(value) for value in row["payload_histogram"].split(";") if value),
            row["payload_bytes_total"],
        )

        schema = json.loads(
            (
                ROOT.parent
                / "CAEOS-EMTD/configs/unified_multimodal_v4.schema.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            set(row),
            {column["name"] for column in schema["columns"]},
        )
        for name in CSV_SEQUENCE_COLUMNS:
            self.assertIsInstance(row[name], str, name)
        for name in INTEGER_ONLINE_COLUMNS:
            self.assertIs(type(row[name]), int, name)

    def test_full_row_export_rejects_deferred_deep_modalities(self) -> None:
        record = UnifiedFeatureReservoir(POLICY).observe_batch((packet(7.0),)).flow_records[0]
        context = UnifiedPcapExportContext(
            "caeos_unified_multimodal_csv_schema_v4", "d", "r", "c", "b" * 64,
            "m", "pending", "none", "caeos_attack_taxonomy_v1", "Pending",
            "", "", "", "", "", -1, "0:0",
        )
        with self.assertRaisesRegex(UnifiedFeatureReservoirError, "complete budgeted"):
            materialize_unified_pcap_row(record, context)

    def test_offline_online_contract_audit_rehashes_both_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "audit.json"
            environment = dict(os.environ)
            environment["PYTHONPATH"] = str(ROOT)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/audit_unified_feature_parity.py"),
                    "--caeos-schema",
                    str((ROOT.parent / "CAEOS-EMTD/configs/unified_multimodal_v4.schema.json").resolve()),
                    "--caeos-feature-views",
                    str((ROOT.parent / "CAEOS-EMTD/configs/unified_multimodal_v5.feature_views.json").resolve()),
                    "--reservoir-policy",
                    str((ROOT / "configs/unified_feature_reservoir_v1.json").resolve()),
                    "--output",
                    str(output.resolve()),
                    "--require-verified",
                ],
                cwd=str(ROOT),
                env=environment,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            audit = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(audit["semantic_contract_verified"])
            self.assertEqual(audit["counts"]["caeos_columns"], 143)
            self.assertEqual(audit["counts"]["online_extractable_columns"], 120)
            self.assertEqual(
                audit["counts"]["model_candidate_persistent_columns"], 116
            )
            self.assertEqual(audit["counts"]["safe_scalars"], 85)
            self.assertFalse(audit["rust_hotpath_parity_qualified"])


if __name__ == "__main__":
    unittest.main()
