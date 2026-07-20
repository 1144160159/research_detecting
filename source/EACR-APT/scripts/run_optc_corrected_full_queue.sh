#!/usr/bin/env bash
set -euo pipefail

ROOT=/opt/data/private/wangwt/ParkAttackKE/datasets/apt_public/optc_corrected
CODE=/opt/data/private/wangwt/ParkAttackKE/APT-Chain-Reconstruction/source/EACR-APT
CONDA=/opt/data/private/wangwt/anaconda3/bin/conda
ACTIVE_PID_FILE="$ROOT/state/evaluation_20260923_25_download.pid"

if [[ -f "$ACTIVE_PID_FILE" ]]; then
  active_pid=$(tr -dc '0-9' < "$ACTIVE_PID_FILE")
  while [[ -n "$active_pid" ]] && kill -0 "$active_pid" 2>/dev/null; do
    sleep 300
  done
fi

cd "$CODE"
exec "$CONDA" run --no-capture-output -n py3.9 \
  python -u scripts/collect_dataverse_parallel.py \
  --base-url https://entrepot.recherche.data.gouv.fr \
  --persistent-id doi:10.57745/UXCWOC \
  --root "$ROOT" \
  --connections 4 \
  --jobs 3
