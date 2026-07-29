#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
ROOT="$PROJECT_ROOT/results/strict_v4_integrated_comprehensive_sota_v2"
DESIGN="$ROOT/design_protocol.json"
BASE="$PROJECT_ROOT/results/strict_v4_final_paper_readiness"
COMPAT="$PROJECT_ROOT/results/strict_v4_comprehensive_sota_audit_v12/supersession_compatibility_v1.json"
SELECTION_ROOT="$PROJECT_ROOT/results/strict_v4_vgrf_confirmation_seed311_313"
SELECTION="$SELECTION_ROOT/final_selection.json"
RECONFIRM="$PROJECT_ROOT/results/strict_v4_selected_external_reconfirmation_seed311_313"
EXTERNAL="$PROJECT_ROOT/results/gpu_external_dataset_evaluation_v1"
VGRF_SYSTEM="$PROJECT_ROOT/results/strict_v4_vgrf_selected_system_confirmation_v1"
LOCK="$ROOT/watcher.lock.d"
STATE="$ROOT/state.log"

mkdir -p "$ROOT"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "integrated comprehensive SOTA v2 watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT

printf '%s waiting for algorithm-consistent integrated evidence\n' \
  "$(date --iso-8601=seconds)" > "$STATE"
until [[ -s "$DESIGN" \
  && -f "$BASE/audit_complete" \
  && -s "$BASE/audit.json" \
  && -f "$SELECTION_ROOT/branch_complete" \
  && -s "$SELECTION" \
  && -f "$RECONFIRM/branch_complete" \
  && -f "$EXTERNAL/evaluation_complete" \
  && -s "$EXTERNAL/summary.json" ]]; do
  sleep 60
done

selected="$("$PYTHON" - "$SELECTION" <<'PY'
import json
import sys

print(json.load(open(sys.argv[1], encoding="utf-8"))["selected_algorithm"])
PY
)"
system_args=()
if [[ "$selected" == "caeos_validation_gated_class_conditional_reliability_fusion" ]]; then
  until [[ -f "$VGRF_SYSTEM/branch_complete" \
    && -s "$VGRF_SYSTEM/summary.json" ]]; do
    sleep 60
  done
  system_args=(--selected-system-summary "$VGRF_SYSTEM/summary.json")
elif [[ "$selected" != "caeos_pairwise" ]]; then
  echo "unsupported final selected algorithm: $selected" >&2
  exit 1
fi

cd "$PROJECT_ROOT"
"$PYTHON" audit_strict_v4_integrated_comprehensive_sota_v2.py \
  --design "$DESIGN" \
  --base-readiness "$BASE/audit.json" \
  --post30-compatibility "$COMPAT" \
  --final-selection "$SELECTION" \
  --reconfirmation-root "$RECONFIRM" \
  --external-summary "$EXTERNAL/summary.json" \
  "${system_args[@]}" \
  --output "$ROOT/audit.json" \
  > "$ROOT/audit.log" 2>&1
printf '%s integrated v2 audit complete\n' \
  "$(date --iso-8601=seconds)" >> "$STATE"
