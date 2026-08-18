#!/usr/bin/env bash
set -euo pipefail

RELEASE=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/releases/20260730T141708Z-caeos_delivery_contract_v1-23511-22665
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
PROTOCOL="$RELEASE/protocols/strict_v4_pcap_multimodal_development_v39_pair_counterfactual_seed307.json"
LOG=/tmp/caeos-v39-cf307-launch.log

exec >>"$LOG" 2>&1
echo "START_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cd "$RELEASE"
export PYTHONPATH="$RELEASE"
set +e
"$PYTHON" "$RELEASE/run_strict_v4_pcap_multimodal_development.py" \
  --protocol "$PROTOCOL" \
  --python "$PYTHON"
status=$?
set -e
echo "EXIT_CODE=$status"
echo "END_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit "$status"
