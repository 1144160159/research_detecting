#!/usr/bin/env bash
set -euo pipefail

ROOT=/opt/data/private/wangwt/ParkAttackKE/datasets/apt_public/optc
OUTPUT="$ROOT/raw_original"
STATE_DIR="$ROOT/state"
LOG_DIR="$ROOT/logs"
RCLONE_CONFIG=${RCLONE_CONFIG:-/root/.config/rclone/rclone.conf}
RCLONE_REMOTE=${RCLONE_REMOTE:-optc_gdrive:}
RCLONE_BIN=${RCLONE_BIN:-rclone}
SOCKS_PROXY=${SOCKS_PROXY:-socks5://127.0.0.1:9998}
RETRY_SECONDS=${RETRY_SECONDS:-300}

mkdir -p "$OUTPUT" "$STATE_DIR" "$LOG_DIR"
printf '%s\n' "$$" > "$STATE_DIR/original_rclone_queue.pid"
trap 'rm -f "$STATE_DIR/original_rclone_queue.pid"' EXIT

while true; do
  printf '%s starting authenticated OpTC sync\n' "$(date -u +%FT%TZ)"
  if ALL_PROXY="$SOCKS_PROXY" \
     HTTPS_PROXY="$SOCKS_PROXY" \
     HTTP_PROXY="$SOCKS_PROXY" \
     "$RCLONE_BIN" copy "$RCLONE_REMOTE" "$OUTPUT" \
       --config "$RCLONE_CONFIG" \
       --size-only \
       --fast-list \
       --drive-acknowledge-abuse \
       --transfers 4 \
       --checkers 8 \
       --retries 20 \
       --low-level-retries 20 \
       --contimeout 30s \
       --timeout 10m \
       --stats 1m \
       --stats-one-line; then
    date -u +%FT%TZ > "$STATE_DIR/original_rclone_complete"
    exit 0
  fi

  printf '%s sync failed; retrying in %s seconds\n' \
    "$(date -u +%FT%TZ)" "$RETRY_SECONDS"
  sleep "$RETRY_SECONDS"
done
