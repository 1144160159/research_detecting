#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_full103_seed7"
BASELINE_RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_full103_baselines_seed7"
MAIN_MARKER="$RESULT_ROOT/full103_complete"
BASELINE_MARKER="$BASELINE_RESULT_ROOT/full103_baselines_complete"
ROUTER_MANIFEST="$PROJECT_ROOT/results/strict_v4_domain_safe_router_development/candidate_manifest.json"
ROUTER_PROTOCOL="$PROJECT_ROOT/results/strict_v4_domain_safe_router_confirmation/protocol_manifest.json"
EXTERNAL_PROTOCOL_ROOT="$PROJECT_ROOT/results/strict_v4_external_confirmation"

mkdir -p "$RESULT_ROOT"
LOCK_DIR="$RESULT_ROOT/summary_launcher.lock.d"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "summary launcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

cd "$PROJECT_ROOT"
until [[ -f "$MAIN_MARKER" ]]; do
  sleep 60
done

"$PYTHON" summarize_strict_v4_full103.py \
  --manifest "$RESULT_ROOT/coverage_manifest_v2.json" \
  --raw-fusion "$RESULT_ROOT/raw_fusion.json" \
  --router-manifest "$ROUTER_MANIFEST" \
  --gate-root runs/strict_v4_full103_pairwise_caeos_seed7 \
  --mlp-root runs/strict_v4_full103_mlp_seed7 \
  --output-dir "$RESULT_ROOT" \
  > "$RESULT_ROOT/summary_without_independent_baselines.log" 2>&1
touch "$RESULT_ROOT/summary_without_independent_baselines_complete"

until [[ -f "$BASELINE_MARKER" ]]; do
  sleep 60
done

"$PYTHON" summarize_strict_v4_full103.py \
  --manifest "$RESULT_ROOT/coverage_manifest_v2.json" \
  --raw-fusion "$RESULT_ROOT/raw_fusion.json" \
  --router-manifest "$ROUTER_MANIFEST" \
  --gate-root runs/strict_v4_full103_pairwise_caeos_seed7 \
  --mlp-root runs/strict_v4_full103_mlp_seed7 \
  --baseline-root runs/strict_v4_full103_independent_baselines_seed7 \
  --baseline-manifest "$BASELINE_RESULT_ROOT/baseline_manifest_v2.json" \
  --output-dir "$RESULT_ROOT" \
  > "$RESULT_ROOT/summary_with_independent_baselines.log" 2>&1
mkdir -p "$EXTERNAL_PROTOCOL_ROOT"
"$PYTHON" create_strict_v4_external_confirmation_protocol.py \
  --full-summary "$RESULT_ROOT/summary.json" \
  --coverage-manifest "$RESULT_ROOT/coverage_manifest_v2.json" \
  --router-protocol "$ROUTER_PROTOCOL" \
  --output "$EXTERNAL_PROTOCOL_ROOT/protocol_manifest.json" \
  > "$EXTERNAL_PROTOCOL_ROOT/protocol_creation.log" 2>&1
touch "$EXTERNAL_PROTOCOL_ROOT/protocol_complete"
touch "$RESULT_ROOT/final_seed7_summary_complete"
