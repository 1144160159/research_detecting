#!/usr/bin/env bash
set -euo pipefail

PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
CODE=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
DATA_ROOT='/opt/data/private/wangwt/ParkAttackKE/datasets/cic/EdgeIIoT/Edge-IIoTset dataset'
PCAP="$DATA_ROOT/Attack traffic/Port Scanning attack.pcap"
PACKET_CSV="$DATA_ROOT/Attack traffic/Port_Scanning_attack.csv"
SOURCE_MEMBER='Attack traffic/Port Scanning attack.pcap'
RUN_ROOT=/tmp/caeos-edge-iiotset-prefix-r14
INDEX="$RUN_ROOT/label_indices/edge_iiotset_port_scanning.sqlite"
INDEX_AUDIT="$RUN_ROOT/audits/edge_iiotset_port_scanning_label_index_r14.json"
INDEX_VALIDATION="$RUN_ROOT/audits/edge_iiotset_port_scanning_label_index_validation_r14.json"
COVERAGE_AUDIT="$RUN_ROOT/audits/edge_iiotset_port_scanning_complete_pcap_r14.json"

mkdir -p "$RUN_ROOT/label_indices" "$RUN_ROOT/audits"
rm -f "$INDEX" "$INDEX_AUDIT" "$INDEX_VALIDATION" "$COVERAGE_AUDIT"

cd "$CODE"
"$PYTHON" build_caeos_edge_iiotset_label_index.py \
  --pcap "$PCAP" \
  --packet-csv "$PACKET_CSV" \
  --source-member "$SOURCE_MEMBER" \
  --label-index "$INDEX" \
  --audit-output "$INDEX_AUDIT" \
  --idle-seconds 30 \
  > "$RUN_ROOT/build.stdout.json"

INDEX_SHA=$("$PYTHON" -c 'import json,sys; print(json.load(open(sys.argv[1]))["label_index"]["sha256"])' "$INDEX_AUDIT")
"$PYTHON" validate_caeos_label_index.py \
  --path "$INDEX" \
  --dataset-id edge_iiotset \
  --output "$INDEX_VALIDATION" \
  --group-counts \
  > "$RUN_ROOT/validate.stdout.json"

"$PYTHON" audit_caeos_label_alignment_coverage.py \
  --dataset-id edge_iiotset \
  --pcap "$PCAP" \
  --source-member "$SOURCE_MEMBER" \
  --label-index "$INDEX" \
  --label-index-sha256 "$INDEX_SHA" \
  --output "$COVERAGE_AUDIT" \
  --maximum-packets 1000000 \
  --idle-seconds 30 \
  --tolerance-ns 0 \
  --conflict-policy reject \
  --time-nonoverlap-policy reject \
  --drop-unmatched-reason protocol_outside_official_tcp_udp_flow_labels \
  --drop-unmatched-reason five_tuple_absent_from_official_flow_labels \
  > "$RUN_ROOT/coverage.stdout.json"

"$PYTHON" - "$INDEX_AUDIT" "$INDEX_VALIDATION" "$COVERAGE_AUDIT" <<'PY'
import json
import sys

index_audit, validation, coverage = [json.load(open(path)) for path in sys.argv[1:]]
flows = coverage["counters"].get("flows", 0)
excluded = coverage["label_exclusion_summary"]["excluded_flows"]
retained = flows - excluded
print(json.dumps({
    "index_sha256": index_audit["label_index"]["sha256"],
    "index_record_count": index_audit["label_index"]["record_count"],
    "pairing_counters": index_audit["counters"],
    "pairing_passed": index_audit["pairing_passed"],
    "validation": validation,
    "complete_pcap_read": coverage["complete_pcap_read"],
    "coverage_fraction": coverage["coverage_fraction"],
    "matched_flows": coverage["matched_flows"],
    "policy_excluded_flows": excluded,
    "effective_retained_flow_coverage": (
        coverage["matched_flows"] / retained if retained else 0.0
    ),
    "label_exclusion_summary": coverage["label_exclusion_summary"],
    "coverage_counters": coverage["counters"],
    "formal_gate_passed": coverage["formal_gate_passed"],
    "formal_gate_reason": coverage["formal_gate_reason"],
}, ensure_ascii=False, sort_keys=True))
PY
