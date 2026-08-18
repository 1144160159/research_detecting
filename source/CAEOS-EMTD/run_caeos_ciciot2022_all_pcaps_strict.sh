#!/usr/bin/env bash
set -euo pipefail

CODE_ROOT="${CODE_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14}"
DATASET_ROOT="${DATASET_ROOT:-/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC_IOT_Dataset2022}"
RUN_ROOT="${CICIOT2022_RUN_ROOT:-/tmp/caeos-ciciot2022-all-pcap-r15}"
TEMP_ROOT="${TEMP_ROOT:-$RUN_ROOT/pcap_current}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"

mkdir -p "$RUN_ROOT/label_indices" "$RUN_ROOT/audits" "$RUN_ROOT/logs" "$TEMP_ROOT"
exec 9>"$RUN_ROOT/run.lock"
flock -n 9 || { echo "CICIoT2022 all-PCAP audit is already running" >&2; exit 75; }

"$PYTHON" "$CODE_ROOT/build_caeos_ciciot2022_capture_label_index.py" \
  --dataset-root "$DATASET_ROOT" \
  --output "$RUN_ROOT/label_indices/capture_labels.json"
"$PYTHON" "$CODE_ROOT/build_caeos_ciciot2022_all_pcap_inventory.py" \
  --dataset-root "$DATASET_ROOT" \
  --label-index "$RUN_ROOT/label_indices/capture_labels.json" \
  --output "$RUN_ROOT/inventory.json"
"$PYTHON" "$CODE_ROOT/audit_caeos_ciciot2022_all_pcaps.py" \
  --dataset-root "$DATASET_ROOT" \
  --inventory "$RUN_ROOT/inventory.json" \
  --run-root "$RUN_ROOT" \
  --temp-root "$TEMP_ROOT"
