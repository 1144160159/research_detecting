#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RESULT_ROOT="$PROJECT_ROOT/results/parrot2025_full_no_decryption_features_v1"
PROTOCOL="$RESULT_ROOT/protocol.json"
DOWNSTREAM_DECISION="$PROJECT_ROOT/results/strict_v4_krc_integrated_comprehensive_sota_v2/downstream_decision.json"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"
STATE_LOG="$RESULT_ROOT/state.log"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "PARROT full feature watcher is already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

printf '%s waiting for KRC downstream decision\n' "$(date --iso-8601=seconds)" > "$STATE_LOG"
until [[ -s "$DOWNSTREAM_DECISION" && -s "$PROTOCOL" ]]; do
  sleep 300
done
if ! "$PYTHON" - "$DOWNSTREAM_DECISION" <<'PY'
import json
import sys
value = json.load(open(sys.argv[1], "r", encoding="utf-8"))
raise SystemExit(0 if value.get("downstream_execution_required") is True else 1)
PY
then
  printf '%s KRC negative; PARROT model-safety branch not required\n' "$(date --iso-8601=seconds)" >> "$STATE_LOG"
  exit 0
fi

idle_samples=0
while [[ "$idle_samples" -lt 5 ]]; do
  gpu_processes="$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null || true)"
  experiment_processes="$(pgrep -af 'train_|run_strict|execute_strict|corruption|tensorized' | grep -v -E 'wait_and_|pgrep -af' || true)"
  if [[ -z "$gpu_processes" && -z "$experiment_processes" ]]; then
    idle_samples=$((idle_samples + 1))
  else
    idle_samples=0
  fi
  [[ "$idle_samples" -ge 5 ]] || sleep 30
done

cd "$PROJECT_ROOT"
printf '%s running PARROT full no-decryption feature extraction\n' "$(date --iso-8601=seconds)" >> "$STATE_LOG"
nice -n 19 ionice -c 3 "$PYTHON" run_parrot2025_full_no_decryption_feature_extraction.py \
  --protocol "$PROTOCOL" \
  --project-root "$PROJECT_ROOT" \
  --output-root "$RESULT_ROOT" \
  > "$RESULT_ROOT/execution.log" 2>&1
printf '%s PARROT full feature extraction complete\n' "$(date --iso-8601=seconds)" >> "$STATE_LOG"
