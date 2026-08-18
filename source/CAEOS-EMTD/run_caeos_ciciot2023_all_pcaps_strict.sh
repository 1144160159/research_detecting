#!/usr/bin/env bash
set -euo pipefail

CODE_ROOT="${CODE_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14}"
DATASET_ROOT="${DATASET_ROOT:-/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC_IOT_Dataset2023/CIC_IOT_Dataset2023_PCAP}"
RUN_ROOT="${CICIOT2023_RUN_ROOT:-/tmp/caeos-ciciot2023-all-pcap-r15}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"

mkdir -p "$RUN_ROOT/label_indices" "$RUN_ROOT/audits" "$RUN_ROOT/logs"
exec 9>"$RUN_ROOT/run.lock"
flock -n 9 || { echo "CICIoT2023 all-PCAP audit is already running" >&2; exit 75; }

"$PYTHON" "$CODE_ROOT/build_caeos_ciciot2023_capture_label_index.py" \
  --dataset-root "$DATASET_ROOT" \
  --output "$RUN_ROOT/label_indices/capture_labels.json"
"$PYTHON" "$CODE_ROOT/build_caeos_ciciot2023_all_pcap_inventory.py" \
  --dataset-root "$DATASET_ROOT" \
  --label-index "$RUN_ROOT/label_indices/capture_labels.json" \
  --output "$RUN_ROOT/inventory.json"
"$PYTHON" "$CODE_ROOT/audit_caeos_ciciot2023_all_pcaps.py" \
  --dataset-root "$DATASET_ROOT" \
  --inventory "$RUN_ROOT/inventory.json" \
  --run-root "$RUN_ROOT"
