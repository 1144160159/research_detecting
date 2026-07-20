#!/usr/bin/env bash
set -euo pipefail

CONDA=/opt/data/private/wangwt/anaconda3/bin/conda
PYTHON_SCRIPT=/opt/data/private/wangwt/ParkAttackKE/APT-Chain-Reconstruction/source/EACR-APT/scripts/download_optc_manifest_missing.py
STATE_DIR=/opt/data/private/wangwt/ParkAttackKE/datasets/apt_public/optc/state
WAIT_PID=${1:-}

mkdir -p "$STATE_DIR"
printf '%s\n' "$$" > "$STATE_DIR/original_manifest_queue.pid"
trap 'rm -f "$STATE_DIR/original_manifest_queue.pid"' EXIT

if [[ -n "$WAIT_PID" ]]; then
  while kill -0 "$WAIT_PID" 2>/dev/null; do
    sleep 30
  done
fi

while true; do
  if "$CONDA" run --no-capture-output -n py3.9 \
    python "$PYTHON_SCRIPT"; then
    exit 0
  fi
  sleep 300
done
