#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-external-fusion-confirm-20260717}"
STRONG="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/runs/strict_v2_strong_baselines_5seed"
MODERN="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v2-20260716/runs/strict_v2_modern_baselines_5seed"
LEGACY="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v2-20260716/runs/strict_v2_legacy_baselines_5seed"
LOG="$PROJECT_ROOT/results/external_fusion_confirmation/waiter.log"

mkdir -p "$(dirname "$LOG")"
while true; do
  strong_count="$(find "$STRONG" -name metrics.json | wc -l)"
  modern_count="$(find "$MODERN" -name metrics.json | wc -l)"
  legacy_count="$(find "$LEGACY" -name metrics.json | wc -l)"
  failures="$(find "$STRONG" "$MODERN" "$LEGACY" -name failure.json | wc -l)"
  printf '%s strong=%s/380 modern=%s/380 legacy=%s/950 failures=%s\n' \
    "$(date -Is)" "$strong_count" "$modern_count" "$legacy_count" "$failures" \
    >> "$LOG"
  [[ "$failures" -eq 0 ]] || exit 1
  if [[ "$strong_count" -eq 380 && "$modern_count" -eq 380 && "$legacy_count" -eq 950 ]]; then
    break
  fi
  sleep 300
done

printf '%s primary matrices complete; finalizing strict-v2 SOTA comparison\n' \
  "$(date -Is)" >> "$LOG"
bash "$PROJECT_ROOT/scripts/finalize_strict_v2_sota.sh" >> "$LOG" 2>&1
printf '%s strict-v2 finalization complete; starting external fusion confirmation\n' \
  "$(date -Is)" >> "$LOG"
exec bash "$PROJECT_ROOT/scripts/run_edge_external_fusion_confirmation.sh" \
  >> "$LOG" 2>&1
