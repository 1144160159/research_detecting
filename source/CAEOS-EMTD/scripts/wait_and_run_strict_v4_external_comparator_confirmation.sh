#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_external_confirmation"
PROTOCOL_MARKER="$RESULT_ROOT/protocol_complete"
ROUTER_MARKER="$PROJECT_ROOT/results/strict_v4_domain_safe_router_confirmation/confirmation_complete"
DOH_MARKER="$PROJECT_ROOT/results/strict_v4_doh_extension_screen/screen_complete"
OPTIMAL_MARKER="$PROJECT_ROOT/results/strict_v4_optimal_self_algorithm/decision_complete"
OPTIMAL_DECISION="$PROJECT_ROOT/results/strict_v4_optimal_self_algorithm/decision.json"
POSTHOC_OOD_MARKER="$PROJECT_ROOT/runs/strict_v4_posthoc_ood_seed7/posthoc_ood_complete"
POSTHOC_DECISION_MARKER="$PROJECT_ROOT/results/strict_v4_posthoc_ood_seed7/comparator_decision_complete"
TRAINING_PILOT_ROOT="$PROJECT_ROOT/results/strict_v4_external_training_pilot_seed7"
TRAINING_PILOT_MARKER="$TRAINING_PILOT_ROOT/pilot_complete"
COMPLEMENTARY_PILOT_ROOT="$PROJECT_ROOT/results/strict_v4_complementary_training_pilot_seed7"
COMPLEMENTARY_PILOT_MARKER="$COMPLEMENTARY_PILOT_ROOT/pilot_complete"
AEGIS_PILOT_ROOT="$PROJECT_ROOT/results/strict_v4_aegis_training_pilot_seed7"
AEGIS_PILOT_MARKER="$AEGIS_PILOT_ROOT/pilot_complete"
LOCK_DIR="$RESULT_ROOT/launcher.lock.d"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "external comparator confirmation launcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

until [[ -f "$PROTOCOL_MARKER" && -f "$ROUTER_MARKER" && -f "$DOH_MARKER" \
  && -f "$OPTIMAL_MARKER" && -f "$POSTHOC_OOD_MARKER" \
  && -f "$POSTHOC_DECISION_MARKER" && -f "$TRAINING_PILOT_MARKER" \
  && -f "$COMPLEMENTARY_PILOT_MARKER" && -f "$AEGIS_PILOT_MARKER" ]]; do
  sleep 60
done

cd "$PROJECT_ROOT"
if [[ -f "$TRAINING_PILOT_ROOT/full102_expansion_required" \
  && ! -f "$TRAINING_PILOT_ROOT/full102_expansion_complete" ]]; then
  echo "external training pilot requires full102 expansion before comparator confirmation" >&2
  exit 4
fi
if [[ -f "$COMPLEMENTARY_PILOT_ROOT/full102_expansion_required" \
  && ! -f "$COMPLEMENTARY_PILOT_ROOT/full102_expansion_complete" ]]; then
  echo "complementary training pilot requires full102 expansion before comparator confirmation" >&2
  exit 5
fi
if [[ -f "$AEGIS_PILOT_ROOT/full102_expansion_required" \
  && ! -f "$AEGIS_PILOT_ROOT/full102_expansion_complete" ]]; then
  echo "AEGIS training pilot requires full102 expansion before comparator confirmation" >&2
  exit 6
fi
comparator="$(tr -d '[:space:]' < "$POSTHOC_DECISION_MARKER")"
if [[ "$comparator" != "opendetect" ]]; then
  echo "frozen OpenDetect protocol is invalid for selected comparator: $comparator" >&2
  exit 3
fi
selected="$("$PYTHON" -c 'import json,sys; print(json.load(open(sys.argv[1]))["selected_algorithm"])' "$OPTIMAL_DECISION")"
if [[ "$selected" == "caeos_tail_aware_pairwise" ]]; then
  bash scripts/run_strict_v4_tail_external_confirmation.sh \
    > "$RESULT_ROOT/launcher.log" 2>&1
  exit $?
fi
bash scripts/run_strict_v4_external_comparator_confirmation.sh \
  > "$RESULT_ROOT/launcher.log" 2>&1
