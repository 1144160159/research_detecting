#!/usr/bin/env bash
set -euo pipefail

ROOT=/opt/data/private/wangwt/ParkAttackKE/datasets/apt_public/optc
CONDA=/opt/data/private/wangwt/anaconda3/bin/conda
FOLDER_URL=https://drive.google.com/drive/folders/1n3kkS3KR31KUegn42yk3-e6JkZvf0Caa
ENUM_PID_FILE="$ROOT/state/gdrive_enumeration.pid"
OUTPUT="$ROOT/raw_original/"

mkdir -p "$OUTPUT" "$ROOT/state" "$ROOT/logs"

if [[ -f "$ENUM_PID_FILE" ]]; then
  enumeration_pid=$(tr -dc '0-9' < "$ENUM_PID_FILE")
  while [[ -n "$enumeration_pid" ]] && kill -0 "$enumeration_pid" 2>/dev/null; do
    sleep 300
  done
fi

while true; do
  if "$CONDA" run --no-capture-output -n py3.9 \
    python -m gdown \
    --folder \
    --remaining-ok \
    --continue \
    --proxy socks5h://127.0.0.1:9998 \
    --output "$OUTPUT" \
    "$FOLDER_URL"; then
    exit 0
  fi
  sleep 3600
done
