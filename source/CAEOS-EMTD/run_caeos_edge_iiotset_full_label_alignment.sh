#!/usr/bin/env bash
set -euo pipefail

PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
CODE=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
DATA_ROOT='/opt/data/private/wangwt/ParkAttackKE/datasets/cic/EdgeIIoT/Edge-IIoTset dataset'
RUN_ROOT=${EDGE_IIOTSET_RUN_ROOT:-/tmp/caeos-edge-iiotset-all-pcap-r15}

mkdir -p "$RUN_ROOT/logs"
cd "$CODE"
exec "$PYTHON" audit_caeos_edge_iiotset_all_pcaps.py \
  --data-root "$DATA_ROOT" \
  --run-root "$RUN_ROOT" \
  --idle-seconds 30 \
  --maximum-packets 9223372036854775807 \
  --maximum-unmatched-samples 100 \
  --resume \
  --verify-source-sha-on-resume \
  >> "$RUN_ROOT/logs/runner.stdout.log" \
  2>> "$RUN_ROOT/logs/runner.stderr.log"
