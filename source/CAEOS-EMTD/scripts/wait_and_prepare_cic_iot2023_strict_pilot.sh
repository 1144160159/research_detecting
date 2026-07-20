#!/usr/bin/env bash
set -euo pipefail

ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-external-fusion-confirm-20260717}"
MODERN="${MODERN_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v2-20260716/runs/strict_v2_modern_baselines_5seed}"
SOURCE="${CIC_IOT_SOURCE:-/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC_IOT_Dataset2023/CIC_IOT_Dataset2023_PCAP/CSV/CSV}"
PY="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
OUT_DIR="$ROOT/caches/strict_v4/cic_iot2023/stratified"
OUTPUT="$OUT_DIR/seed7_max1000.csv"
SIDECAR="${OUTPUT}.json"
MARKER="$OUT_DIR/preparation_complete"
LOG="$OUT_DIR/preparation.log"
LOCK="$OUT_DIR/.prepare.lock"

mkdir -p "$OUT_DIR"
if ! mkdir "$LOCK" 2>/dev/null; then
  printf '%s another CICIoT2023 cache preparer is active\n' "$(date -Is)" >>"$LOG"
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT

verify_sha() {
  local expected="$1"
  local path="$2"
  local actual
  actual="$(sha256sum "$path" | awk '{print $1}')"
  if [[ "$actual" != "$expected" ]]; then
    printf '%s hash mismatch path=%s expected=%s actual=%s\n' \
      "$(date -Is)" "$path" "$expected" "$actual" >>"$LOG"
    exit 1
  fi
}

verify_sha 1c57f250e9a24c0cad04c36c99ab0f0c75af19d9be56235b2e724dc38dfa77fd \
  "$ROOT/prepare_cic_iot2023_strict.py"
verify_sha 2c7e8dbd4f1d6c399c913b884b0ae7f4743fc7521e011df4b9ae27e8c3441cdb \
  "$ROOT/configs/cic_iot2023_strict.json"

while true; do
  count="$(find "$MODERN" -name metrics.json 2>/dev/null | wc -l)"
  state="missing"
  if [[ -s "$MODERN/manifest.json" ]]; then
    state="$($PY -c 'import json,sys; print(json.load(open(sys.argv[1])).get("state", "missing"))' "$MODERN/manifest.json")"
  fi
  printf '%s waiting modern=%s/380 state=%s\n' \
    "$(date -Is)" "$count" "$state" >>"$LOG"
  if [[ "$count" == "380" && "$state" == "complete" ]]; then
    break
  fi
  sleep 60
done

if [[ -s "$OUTPUT" && -s "$SIDECAR" && -f "$MARKER" ]]; then
  printf '%s CICIoT2023 pilot cache already complete\n' "$(date -Is)" >>"$LOG"
  exit 0
fi
if [[ -e "$OUTPUT" || -e "$SIDECAR" || -e "$MARKER" ]]; then
  printf '%s refusing ambiguous partial CICIoT2023 cache artifacts\n' \
    "$(date -Is)" >>"$LOG"
  exit 1
fi

printf '%s starting low-priority CICIoT2023 strict pilot cache\n' \
  "$(date -Is)" >>"$LOG"
ionice -c3 nice -n 19 "$PY" "$ROOT/prepare_cic_iot2023_strict.py" \
  --input-dir "$SOURCE" \
  --output "$OUTPUT" \
  --seed 7 \
  --max-per-class 1000 \
  --group-rows 1000 \
  --expected-source-files 309 \
  >>"$LOG" 2>&1

"$PY" - "$SIDECAR" "$OUTPUT" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

sidecar = json.load(open(sys.argv[1], encoding="utf-8"))
output = Path(sys.argv[2])
digest = hashlib.sha256(output.read_bytes()).hexdigest()
assert sidecar["schema_version"] == "cic_iot2023_strict_cache_v1"
assert sidecar["source_selection"]["merged_csv_excluded"] is True
assert sidecar["source_selection"]["source_file_count"] == 309
assert len(sidecar["source_files"]) == 309
assert len(sidecar["rows_seen_per_class"]) == 34
assert len(sidecar["rows_sampled_per_class"]) == 34
assert min(sidecar["rows_sampled_per_class"].values()) > 0
assert len(sidecar["feature_columns"]) == 39
assert sidecar["output_rows"] == sum(sidecar["rows_sampled_per_class"].values())
assert sidecar["output_sha256"] == digest
PY

touch "$MARKER"
printf '%s CICIoT2023 strict pilot cache complete\n' "$(date -Is)" >>"$LOG"
