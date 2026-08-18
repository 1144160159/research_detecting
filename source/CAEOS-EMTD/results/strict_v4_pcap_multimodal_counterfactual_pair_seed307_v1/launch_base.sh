#!/usr/bin/env bash
set -euo pipefail

RELEASE=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/releases/20260730T141708Z-caeos_delivery_contract_v1-23511-22665
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
PROTOCOL="$RELEASE/protocols/strict_v4_pcap_multimodal_development_v38_pair_base_seed307.json"

export PYTHONPATH="$RELEASE"
exec "$PYTHON" "$RELEASE/run_strict_v4_pcap_multimodal_development.py" \
  --protocol "$PROTOCOL" \
  --python "$PYTHON"
