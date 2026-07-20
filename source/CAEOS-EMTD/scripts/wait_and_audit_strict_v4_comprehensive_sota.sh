#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
OUTPUT="$PROJECT_ROOT/results/strict_v4_comprehensive_sota_audit"
EXTERNAL_ROOT="$PROJECT_ROOT/results/strict_v4_external_confirmation"
DOH_ROOT="$PROJECT_ROOT/results/strict_v4_doh_extension_screen"
OPTIMAL_ROOT="$PROJECT_ROOT/results/strict_v4_optimal_self_algorithm"
SIRC_ROOT="$PROJECT_ROOT/results/strict_v4_sirc_msp_fixed_full102_seed7"
DOC_ROOT="$PROJECT_ROOT/results/strict_v4_doc_fixed_pilot_seed7"
MANDATORY_ROOT="$PROJECT_ROOT/results/strict_v4_mandatory_scores_full102_seed7"
MAHALANOBIS_PP_ROOT="$PROJECT_ROOT/results/strict_v4_mahalanobis_pp_full102_seed7"
EXCEL_ROOT="$PROJECT_ROOT/results/strict_v4_excel_full102_seed7"
TRAINING_PILOT_ROOT="$PROJECT_ROOT/results/strict_v4_external_training_pilot_seed7"
COMPLEMENTARY_PILOT_ROOT="$PROJECT_ROOT/results/strict_v4_complementary_training_pilot_seed7"
AEGIS_PILOT_ROOT="$PROJECT_ROOT/results/strict_v4_aegis_training_pilot_seed7"
COMPLEMENTARY_EXPANSION_ROOT="$PROJECT_ROOT/results/strict_v4_complementary_training_full102_seed7"
AEGIS_EXPANSION_ROOT="$PROJECT_ROOT/results/strict_v4_aegis_training_full102_seed7"
FUSION_ROOT="$PROJECT_ROOT/results/strict_v4_fusion_operators_seed7"
ATTENTION_ROOT="$PROJECT_ROOT/results/strict_v4_attention_fusion_seed7"
LOCK_DIR="$OUTPUT/launcher.lock.d"

mkdir -p "$OUTPUT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "comprehensive SOTA audit launcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

until [[ -f "$EXTERNAL_ROOT/confirmation_complete" && -f "$DOH_ROOT/screen_complete" \
  && -f "$OPTIMAL_ROOT/decision_complete" && -f "$SIRC_ROOT/sirc_msp_fixed_complete" \
  && -f "$SIRC_ROOT/summary.json" && -f "$DOC_ROOT/doc_fixed_complete" \
  && -f "$DOC_ROOT/protocol_manifest.json" && -f "$DOC_ROOT/expansion_gate.json" \
  && -f "$DOC_ROOT/analysis.json" && -f "$MANDATORY_ROOT/summary_complete" \
  && -f "$MANDATORY_ROOT/summary.json" \
  && -f "$MAHALANOBIS_PP_ROOT/comparator_decision_complete" \
  && -f "$MAHALANOBIS_PP_ROOT/summary.json" \
  && -f "$EXCEL_ROOT/screen_complete" \
  && -f "$EXCEL_ROOT/summary.json" \
  && -f "$TRAINING_PILOT_ROOT/pilot_complete" \
  && -f "$TRAINING_PILOT_ROOT/protocol_manifest.json" \
  && -f "$TRAINING_PILOT_ROOT/expansion_gate.json" \
  && -f "$TRAINING_PILOT_ROOT/analysis.json" \
  && -f "$COMPLEMENTARY_PILOT_ROOT/pilot_complete" \
  && -f "$COMPLEMENTARY_PILOT_ROOT/protocol_manifest.json" \
  && -f "$COMPLEMENTARY_PILOT_ROOT/expansion_gate.json" \
  && -f "$COMPLEMENTARY_PILOT_ROOT/analysis.json" \
  && -f "$AEGIS_PILOT_ROOT/pilot_complete" \
  && -f "$AEGIS_PILOT_ROOT/protocol_manifest.json" \
  && -f "$AEGIS_PILOT_ROOT/expansion_gate.json" \
  && -f "$AEGIS_PILOT_ROOT/analysis.json" \
  && -f "$FUSION_ROOT/analysis_complete" \
  && -f "$FUSION_ROOT/protocol_manifest.json" \
  && -f "$FUSION_ROOT/analysis.json" \
  && -f "$ATTENTION_ROOT/analysis_complete" \
  && -f "$ATTENTION_ROOT/protocol_manifest.json" \
  && -f "$ATTENTION_ROOT/analysis.json" ]]; do
  sleep 60
done

for root in "$COMPLEMENTARY_PILOT_ROOT" "$AEGIS_PILOT_ROOT"; do
  while [[ -f "$root/full102_expansion_required" \
    && ! -f "$root/full102_expansion_complete" ]]; do
    sleep 60
  done
done

EXPANSION_ARGS=()
if [[ -f "$COMPLEMENTARY_PILOT_ROOT/full102_expansion_required" ]]; then
  EXPANSION_ARGS+=(
    --complementary-expansion-protocol "$COMPLEMENTARY_EXPANSION_ROOT/protocol_manifest.json"
    --complementary-expansion-analysis "$COMPLEMENTARY_EXPANSION_ROOT/analysis.json"
  )
fi
if [[ -f "$AEGIS_PILOT_ROOT/full102_expansion_required" ]]; then
  EXPANSION_ARGS+=(
    --aegis-expansion-protocol "$AEGIS_EXPANSION_ROOT/protocol_manifest.json"
    --aegis-expansion-analysis "$AEGIS_EXPANSION_ROOT/analysis.json"
  )
fi

cd "$PROJECT_ROOT"
"$PYTHON" audit_strict_v4_comprehensive_sota.py \
  --full-summary results/strict_v4_full103_seed7/summary.json \
  --posthoc-summary results/strict_v4_posthoc_ood_seed7/summary.json \
  --extended-summary "$SIRC_ROOT/summary.json" \
  --mandatory-summary "$MANDATORY_ROOT/summary.json" \
  --mahalanobis-pp-summary "$MAHALANOBIS_PP_ROOT/summary.json" \
  --excel-summary "$EXCEL_ROOT/summary.json" \
  --doc-protocol "$DOC_ROOT/protocol_manifest.json" \
  --doc-gate "$DOC_ROOT/expansion_gate.json" \
  --doc-analysis "$DOC_ROOT/analysis.json" \
  --training-pilot-protocol "$TRAINING_PILOT_ROOT/protocol_manifest.json" \
  --training-pilot-gate "$TRAINING_PILOT_ROOT/expansion_gate.json" \
  --training-pilot-analysis "$TRAINING_PILOT_ROOT/analysis.json" \
  --complementary-pilot-protocol "$COMPLEMENTARY_PILOT_ROOT/protocol_manifest.json" \
  --complementary-pilot-gate "$COMPLEMENTARY_PILOT_ROOT/expansion_gate.json" \
  --complementary-pilot-analysis "$COMPLEMENTARY_PILOT_ROOT/analysis.json" \
  --aegis-pilot-protocol "$AEGIS_PILOT_ROOT/protocol_manifest.json" \
  --aegis-pilot-gate "$AEGIS_PILOT_ROOT/expansion_gate.json" \
  --aegis-pilot-analysis "$AEGIS_PILOT_ROOT/analysis.json" \
  --fusion-protocol "$FUSION_ROOT/protocol_manifest.json" \
  --fusion-analysis "$FUSION_ROOT/analysis.json" \
  --attention-protocol "$ATTENTION_ROOT/protocol_manifest.json" \
  --attention-analysis "$ATTENTION_ROOT/analysis.json" \
  --final-decision "$OPTIMAL_ROOT/decision.json" \
  --router-confirmation results/strict_v4_domain_safe_router_confirmation/confirmation.json \
  --external-confirmation "$EXTERNAL_ROOT/confirmation.json" \
  --doh-summary "$DOH_ROOT/summary.json" \
  --tournament-protocol "$OPTIMAL_ROOT/tournament_protocol.json" \
  "${EXPANSION_ARGS[@]}" \
  --output-dir "$OUTPUT" \
  > "$OUTPUT/audit.log" 2>&1
touch "$OUTPUT/audit_complete"
