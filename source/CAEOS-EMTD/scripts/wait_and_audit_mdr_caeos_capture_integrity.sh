#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
PROTOCOL="$PROJECT_ROOT/results/strict_v4_mdr_caeos_pilot_protocol_v2/protocol_manifest.json"
DESIGN="$PROJECT_ROOT/results/strict_v4_mdr_caeos_design/design_v2.json"
CAPTURE_ROOT="$PROJECT_ROOT/runs/strict_v4_mdr_caeos_pilot_v2/captures"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_mdr_caeos_capture_integrity_v1"
FINAL_AUDIT="$RESULT_ROOT/final_integrity.json"
COMPLETE_MARKER="$RESULT_ROOT/capture_integrity_complete"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"
STATE_LOG="$RESULT_ROOT/watcher_state.log"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "MDR capture integrity watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

log_state() {
  printf '%s %s\n' "$(date --iso-8601=seconds)" "$*" >> "$STATE_LOG"
}

cd "$PROJECT_ROOT"
log_state "waiting for 42 MDR runtime capture manifests"
while true; do
  count="$(
    find "$CAPTURE_ROOT" -mindepth 4 -maxdepth 4 \
      -name capture_manifest.json -type f 2>/dev/null | wc -l
  )"
  if [[ "$count" -eq 42 ]]; then
    break
  fi
  if [[ "$count" -gt 42 ]]; then
    log_state "unexpected capture count $count"
    exit 1
  fi
  sleep 60
done

if [[ -e "$FINAL_AUDIT" || -e "$COMPLETE_MARKER" ]]; then
  "$PYTHON" - "$FINAL_AUDIT" "$COMPLETE_MARKER" <<'PY'
import json
import sys
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import canonical_hash

audit_path = Path(sys.argv[1])
marker_path = Path(sys.argv[2])
if not audit_path.is_file() or not marker_path.is_file():
    raise SystemExit("partial existing final capture integrity output")
value = json.loads(audit_path.read_text(encoding="utf-8"))
if value.get("manifest_sha256") != canonical_hash(value):
    raise SystemExit("existing capture integrity audit is not canonical")
if value.get("passes") is not True:
    raise SystemExit("existing capture integrity audit did not pass")
if marker_path.read_text(encoding="utf-8").strip() != value["manifest_sha256"]:
    raise SystemExit("capture integrity completion marker mismatch")
PY
  log_state "existing final capture integrity audit validated"
  exit 0
fi

tmp="$RESULT_ROOT/final_integrity.pending.$$"
log_state "auditing complete MDR capture matrix"
PYTHONPATH="$PROJECT_ROOT" "$PYTHON" \
  "$PROJECT_ROOT/audit_mdr_caeos_capture_integrity.py" \
  --protocol "$PROTOCOL" \
  --design "$DESIGN" \
  --capture-root "$CAPTURE_ROOT" \
  --project-root "$PROJECT_ROOT" \
  --output "$tmp"

"$PYTHON" - "$tmp" <<'PY'
import json
import sys
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import canonical_hash

path = Path(sys.argv[1])
value = json.loads(path.read_text(encoding="utf-8"))
if value.get("manifest_sha256") != canonical_hash(value):
    raise SystemExit("capture integrity audit canonical hash mismatch")
if value.get("observed_capture_count") != 42:
    raise SystemExit("capture integrity audit did not cover 42 captures")
if value.get("passes") is not True:
    raise SystemExit("capture integrity audit failed")
PY

mv "$tmp" "$FINAL_AUDIT"
"$PYTHON" - "$FINAL_AUDIT" "$COMPLETE_MARKER" <<'PY'
import json
import sys
from pathlib import Path

value = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
Path(sys.argv[2]).write_text(
    value["manifest_sha256"] + "\n", encoding="utf-8"
)
PY
log_state "complete MDR capture integrity audit passed"
