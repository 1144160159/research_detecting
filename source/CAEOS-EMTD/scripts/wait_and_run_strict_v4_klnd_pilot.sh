#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
PILOT_ROOT="$PROJECT_ROOT/results/strict_v4_klnd_pilot_seed7"
SOURCE_ROOT="$PROJECT_ROOT/runs/strict_v4_full103_mlp_seed7"
OPENDETECT_ROOT="$PROJECT_ROOT/runs/strict_v4_full103_independent_baselines_seed7"
CORRUPTION_ROOT="$PROJECT_ROOT/runs/strict_v4_postselection_corruption_seed7"
CORRUPTION_SUMMARY="$PROJECT_ROOT/results/strict_v4_postselection_corruption_confirmation/summary.json"
PROTOCOL="$PILOT_ROOT/protocol_manifest.json"
GATE="$PILOT_ROOT/expansion_gate.json"
STATE="$PILOT_ROOT/watcher_state.log"
LOCK="$PILOT_ROOT/watcher.lock.d"
EXPECTED_CORRUPTION_RUNS=783

mkdir -p "$PILOT_ROOT"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "k-LND pilot watcher already active" >&2
  exit 0
fi

cleanup() {
  local rc=$?
  if [[ "$rc" -ne 0 ]]; then
    printf '%s watcher failed with exit %d\n' \
      "$(date --iso-8601=seconds)" "$rc" >> "$STATE"
  fi
  rmdir "$LOCK" 2>/dev/null || true
}
trap cleanup EXIT

if [[ -s "$PILOT_ROOT/klnd_complete" && -s "$PILOT_ROOT/analysis.json" ]]; then
  printf '%s pilot and analysis already complete\n' \
    "$(date --iso-8601=seconds)" > "$STATE"
  exit 0
fi
if [[ ! -s "$PROTOCOL" || ! -s "$GATE" ]]; then
  echo "frozen k-LND protocol and expansion gate are required" >&2
  exit 1
fi

printf '%s waiting for 783/783 corruption completion and summary\n' \
  "$(date --iso-8601=seconds)" > "$STATE"
last_report=0
while true; do
  metrics="$(find "$CORRUPTION_ROOT" -type f -name metrics.json 2>/dev/null | wc -l)"
  provenance="$(find "$CORRUPTION_ROOT" -type f -name provenance.json 2>/dev/null | wc -l)"
  failures="$(find "$CORRUPTION_ROOT" -type f -name failure.json 2>/dev/null | wc -l)"
  if [[ "$failures" -ne 0 ]]; then
    echo "corruption branch has $failures failure records" >&2
    exit 1
  fi
  if [[ "$metrics" -eq "$EXPECTED_CORRUPTION_RUNS" \
    && "$provenance" -eq "$EXPECTED_CORRUPTION_RUNS" \
    && -s "$CORRUPTION_SUMMARY" ]]; then
    break
  fi
  now="$(date +%s)"
  if (( now - last_report >= 600 )); then
    summary_ready=false
    [[ -s "$CORRUPTION_SUMMARY" ]] && summary_ready=true
    printf '%s corruption metrics=%s provenance=%s failures=%s summary=%s\n' \
      "$(date --iso-8601=seconds)" "$metrics" "$provenance" "$failures" \
      "$summary_ready" >> "$STATE"
    last_report="$now"
  fi
  sleep 60
done

printf '%s corruption complete; waiting for five idle samples\n' \
  "$(date --iso-8601=seconds)" >> "$STATE"
idle_samples=0
while [[ "$idle_samples" -lt 5 ]]; do
  gpu_processes="$(nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null || true)"
  experiment_processes="$(
    pgrep -af 'train_hybrid_open_set.py|train_neural_open_set.py|run_strict_v4_|execute_strict_v4_|gpu_external' \
      | grep -v -E 'wait_and_run_|pgrep -af|run_strict_v4_klnd_matrix.py' || true
  )"
  if [[ -z "$gpu_processes" && -z "$experiment_processes" ]]; then
    idle_samples=$((idle_samples + 1))
  else
    idle_samples=0
  fi
  [[ "$idle_samples" -ge 5 ]] || sleep 30
done

cd "$PROJECT_ROOT"
printf '%s running frozen 14-scenario k-LND pilot on CPU\n' \
  "$(date --iso-8601=seconds)" >> "$STATE"
nice -n 19 ionice -c 3 "$PYTHON" run_strict_v4_klnd_matrix.py \
  --source-root "$SOURCE_ROOT" \
  --coverage results/strict_v4_full103_seed7/coverage_manifest_v2.json \
  --paper paper/Dahanayaka2023_Robust_Open_Set_Traffic_Fingerprinting.pdf \
  --official-repository /opt/data/private/wangwt/ParkAttackKE/Open-Set-Traffic-Classification-673320b \
  --output-root "$PILOT_ROOT" \
  --mode pilot \
  --workers 1 \
  --device cpu \
  > "$PILOT_ROOT/execution.log" 2>&1

printf '%s summarizing pilot against MLP Energy and OpenDetect\n' \
  "$(date --iso-8601=seconds)" >> "$STATE"
nice -n 19 ionice -c 3 "$PYTHON" summarize_strict_v4_klnd_pilot.py \
  --pilot-root "$PILOT_ROOT" \
  --source-root "$SOURCE_ROOT" \
  --opendetect-root "$OPENDETECT_ROOT" \
  --gate "$GATE" \
  --output-dir "$PILOT_ROOT" \
  > "$PILOT_ROOT/summary.log" 2>&1

printf '%s pilot complete; full102 remains gated and was not launched\n' \
  "$(date --iso-8601=seconds)" >> "$STATE"
