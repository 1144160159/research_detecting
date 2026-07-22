#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
EXPLORATION_ROOT="${EXPLORATION_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-lcb-exploration-20260720}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"

EFFICIENCY_ROOT="$PROJECT_ROOT/results/strict_v4_final_efficiency_v5"
EFFICIENCY_SUMMARY="$EFFICIENCY_ROOT/summary.json"
EFFICIENCY_COMPLETE="$EFFICIENCY_ROOT/recovery_complete"
GROOD_ROOT="$EXPLORATION_ROOT/results/strict_v4_grood_pilot_seed7"
GROOD_ANALYSIS="$GROOD_ROOT/analysis.json"
GROOD_COMPLETE="$GROOD_ROOT/pilot_complete"
GSC_ROOT="$PROJECT_ROOT/results/strict_v4_gsc_pilot_seed7"
GSC_ANALYSIS="$GSC_ROOT/analysis.json"
GSC_COMPLETE="$GSC_ROOT/pilot_complete"
PRO_ROOT="$PROJECT_ROOT/results/strict_v4_pro_msp_fixed_pilot_seed7"
PRO_ANALYSIS="$PRO_ROOT/analysis.json"
PRO_COMPLETE="$PRO_ROOT/branch_complete"
ACTSUB_ROOT="$PROJECT_ROOT/results/strict_v4_actsub_scale_fixed_pilot_seed7"
ACTSUB_ANALYSIS="$ACTSUB_ROOT/analysis.json"
ACTSUB_COMPLETE="$ACTSUB_ROOT/branch_complete"
CADREF_ROOT="$PROJECT_ROOT/results/strict_v4_cadref_family_pilot_seed7"
CADREF_ANALYSIS="$CADREF_ROOT/analysis.json"
CADREF_COMPLETE="$CADREF_ROOT/branch_complete"
FISHER_RAO_ROOT="$PROJECT_ROOT/results/strict_v4_fisher_rao_family_pilot_seed7"
FISHER_RAO_ANALYSIS="$FISHER_RAO_ROOT/analysis.json"
FISHER_RAO_COMPLETE="$FISHER_RAO_ROOT/branch_complete"
UNIFIED_SELF_ROOT="$PROJECT_ROOT/results/strict_v4_unified_self_algorithm_selection"
UNIFIED_SELF_DECISION="$UNIFIED_SELF_ROOT/accuracy_decision.json"
UNIFIED_SELF_COMPLETE="$UNIFIED_SELF_ROOT/accuracy_decision_complete"
ACCURACY_ROOT="$PROJECT_ROOT/results/strict_v4_comprehensive_sota_audit"
ACCURACY_AUDIT="$ACCURACY_ROOT/audit.json"
ACCURACY_COMPLETE="$ACCURACY_ROOT/audit_complete"

CHAIN_ROOT="$PROJECT_ROOT/results/strict_v4_postefficiency_claim_chain_v2"
LOCK_DIR="$CHAIN_ROOT/watcher.lock.d"
STATE_LOG="$CHAIN_ROOT/state.log"
IDLE_LOG="$CHAIN_ROOT/gpu_idle_observations.log"

CORRUPTION_PROTOCOL="$PROJECT_ROOT/results/strict_v4_postselection_corruption_seed7/protocol_manifest.json"
CORRUPTION_PROTOCOL_SHA="83415875d1f26c8f1c948dac65f498110a5f3a6080e2aba4fd4407aa05eea4f4"
CORRUPTION_RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_postselection_corruption_seed7"
CORRUPTION_RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_postselection_corruption_confirmation"

COMPARATIVE_PROTOCOL_ROOT="$PROJECT_ROOT/results/strict_v4_comparative_corruption_protocol"
COMPARATIVE_PROTOCOL="$COMPARATIVE_PROTOCOL_ROOT/protocol_manifest.json"
COMPARATIVE_RUN_ROOT="$PROJECT_ROOT/runs/strict_v4_comparative_corruption"
COMPARATIVE_RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_comparative_corruption"
FINAL_ROOT="$PROJECT_ROOT/results/strict_v4_final_paper_readiness"

mkdir -p "$CHAIN_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "post-efficiency claim-chain watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

log_state() {
  printf '%s %s\n' "$(date --iso-8601=seconds)" "$*" | tee -a "$STATE_LOG"
}

validate_manifest() {
  local path="$1"
  local schema="$2"
  local expected_sha="${3:-}"
  "$PYTHON" - "$path" "$schema" "$expected_sha" <<'PY'
import json
import sys
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import canonical_hash

path = Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
if payload.get("schema_version") != sys.argv[2]:
    raise SystemExit(f"unexpected schema in {path}")
if payload.get("manifest_sha256") != canonical_hash(payload):
    raise SystemExit(f"canonical hash mismatch in {path}")
if sys.argv[3] and payload.get("manifest_sha256") != sys.argv[3]:
    raise SystemExit(f"frozen manifest hash mismatch in {path}")
PY
}

cd "$PROJECT_ROOT"
: > "$STATE_LOG"
log_state "waiting for efficiency-v5, unified self selection, GROOD, GSC, PRO, ActSub, CADRef, Fisher-Rao, and comprehensive-accuracy prerequisites"
until [[ -s "$EFFICIENCY_SUMMARY" && -f "$EFFICIENCY_COMPLETE" \
  && -s "$UNIFIED_SELF_DECISION" && -f "$UNIFIED_SELF_COMPLETE" \
  && -s "$GROOD_ANALYSIS" && -f "$GROOD_COMPLETE" \
  && -s "$GSC_ANALYSIS" && -f "$GSC_COMPLETE" \
  && -s "$PRO_ANALYSIS" && -f "$PRO_COMPLETE" \
  && -s "$ACTSUB_ANALYSIS" && -f "$ACTSUB_COMPLETE" \
  && -s "$CADREF_ANALYSIS" && -f "$CADREF_COMPLETE" \
  && -s "$FISHER_RAO_ANALYSIS" && -f "$FISHER_RAO_COMPLETE" \
  && -s "$ACCURACY_AUDIT" && -f "$ACCURACY_COMPLETE" ]]; do
  sleep 60
done
log_state "all result prerequisites are complete"

validate_manifest \
  "$CORRUPTION_PROTOCOL" \
  strict_v4_postselection_corruption_protocol_v1 \
  "$CORRUPTION_PROTOCOL_SHA"

BLOCKER_PATTERN='execute_strict_v4_final_efficiency|run_strict_v4_conflict_topology_copula|run_strict_v4_wdiscood|run_doh_temporal|run_strict_v4_vos|run_mal_tls_geometry|run_strict_v4_grood|run_strict_v4_gsc|run_strict_v4_pro|run_strict_v4_actsub|run_strict_v4_cadref|run_strict_v4_fisher_rao|run_strict_v4_postselection_corruption|run_strict_v4_comparative_corruption'
: > "$IDLE_LOG"
idle_samples=0
while [[ "$idle_samples" -lt 5 ]]; do
  gpu_processes="$(nvidia-smi --query-compute-apps=pid,process_name \
    --format=csv,noheader 2>/dev/null || true)"
  experiment_processes="$(pgrep -af "$BLOCKER_PATTERN" 2>/dev/null || true)"
  printf '%s sample=%d gpu=%q experiments=%q\n' \
    "$(date --iso-8601=seconds)" "$idle_samples" \
    "$gpu_processes" "$experiment_processes" >> "$IDLE_LOG"
  if [[ -n "$gpu_processes" || -n "$experiment_processes" ]]; then
    idle_samples=0
  else
    idle_samples=$((idle_samples + 1))
  fi
  [[ "$idle_samples" -ge 5 ]] || sleep 30
done
log_state "five consecutive idle samples passed"

mkdir -p "$CORRUPTION_RESULT_ROOT"
if [[ ! -s "$CORRUPTION_RESULT_ROOT/summary.json" \
  || ! -f "$CORRUPTION_RESULT_ROOT/summary_complete" ]]; then
  log_state "running resumable candidate post-selection corruption matrix"
  "$PYTHON" run_strict_v4_postselection_corruption.py \
    --protocol "$CORRUPTION_PROTOCOL" \
    --coverage results/strict_v4_full103_seed7/coverage_manifest_v2.json \
    --pairwise-candidate results/strict_v4_boundary_pairwise_development/candidate_manifest.json \
    --clean-root runs/strict_v4_full103_pairwise_caeos_seed7 \
    --cache-root caches/strict_v4_domain_safe_router_confirmation \
    --output-root "$CORRUPTION_RUN_ROOT" \
    > "$CORRUPTION_RESULT_ROOT/execution.log" 2>&1
  "$PYTHON" summarize_strict_v4_postselection_corruption.py \
    --protocol "$CORRUPTION_PROTOCOL" \
    --coverage results/strict_v4_full103_seed7/coverage_manifest_v2.json \
    --run-root "$CORRUPTION_RUN_ROOT" \
    --output-dir "$CORRUPTION_RESULT_ROOT" \
    > "$CORRUPTION_RESULT_ROOT/summary.log" 2>&1
fi
validate_manifest \
  "$CORRUPTION_RESULT_ROOT/summary.json" \
  strict_v4_postselection_corruption_summary_v1
log_state "candidate corruption summary validated"

mkdir -p "$COMPARATIVE_PROTOCOL_ROOT" "$COMPARATIVE_RESULT_ROOT"
if [[ ! -s "$COMPARATIVE_PROTOCOL" ]]; then
  observed=0
  if [[ -d "$COMPARATIVE_RUN_ROOT" ]]; then
    observed="$(find "$COMPARATIVE_RUN_ROOT" -name paired_corruption.json \
      -type f | wc -l)"
  fi
  if [[ "$observed" -ne 0 ]]; then
    log_state "refusing to freeze comparative protocol after paired results exist"
    exit 1
  fi
  log_state "freezing comparative corruption protocol before paired results"
  "$PYTHON" create_strict_v4_comparative_corruption_protocol.py \
    --coverage results/strict_v4_full103_seed7/coverage_manifest_v2.json \
    --decision results/strict_v4_optimal_self_algorithm/decision.json \
    --external-confirmation results/strict_v4_external_confirmation/confirmation.json \
    --candidate-corruption-protocol "$CORRUPTION_PROTOCOL" \
    --candidate-corruption-summary "$CORRUPTION_RESULT_ROOT/summary.json" \
    --candidate-root runs/strict_v4_domain_safe_router_confirmation_caeos \
    --comparator-root runs/strict_v4_external_comparator_confirmation \
    --candidate-trainer train_hybrid_open_set.py \
    --candidate-runtime caeos/pairwise_runtime.py \
    --candidate-capture capture_pairwise_runtime.py \
    --comparator-runtime caeos/open_detect_runtime.py \
    --comparator-capture capture_opendetect_runtime.py \
    --evaluator evaluate_strict_v4_comparative_corruption.py \
    --runner run_strict_v4_comparative_corruption.py \
    --summarizer summarize_strict_v4_comparative_corruption.py \
    --run-root "$COMPARATIVE_RUN_ROOT" \
    --output-dir "$COMPARATIVE_PROTOCOL_ROOT" \
    > "$COMPARATIVE_PROTOCOL_ROOT/freeze.log" 2>&1
fi
validate_manifest \
  "$COMPARATIVE_PROTOCOL" \
  strict_v4_comparative_corruption_protocol_v1

if [[ ! -s "$COMPARATIVE_RESULT_ROOT/summary.json" \
  || ! -f "$COMPARATIVE_RESULT_ROOT/summary_complete" ]]; then
  log_state "running resumable Pairwise-vs-OpenDetect comparative corruption matrix"
  "$PYTHON" run_strict_v4_comparative_corruption.py \
    --protocol "$COMPARATIVE_PROTOCOL" \
    --output-root "$COMPARATIVE_RUN_ROOT" \
    --project-root "$PROJECT_ROOT" \
    > "$COMPARATIVE_RESULT_ROOT/execution.log" 2>&1
  "$PYTHON" summarize_strict_v4_comparative_corruption.py \
    --protocol "$COMPARATIVE_PROTOCOL" \
    --run-root "$COMPARATIVE_RUN_ROOT" \
    --output-dir "$COMPARATIVE_RESULT_ROOT" \
    > "$COMPARATIVE_RESULT_ROOT/summary.log" 2>&1
fi
validate_manifest \
  "$COMPARATIVE_RESULT_ROOT/summary.json" \
  strict_v4_comparative_corruption_summary_v1
log_state "comparative corruption summary validated"

mkdir -p "$FINAL_ROOT"
log_state "auditing final paper readiness against efficiency v5"
"$PYTHON" audit_strict_v4_final_paper_readiness.py \
  --accuracy-audit "$ACCURACY_AUDIT" \
  --efficiency-summary "$EFFICIENCY_SUMMARY" \
  --corruption-summary "$CORRUPTION_RESULT_ROOT/summary.json" \
  --comparative-corruption-summary "$COMPARATIVE_RESULT_ROOT/summary.json" \
  --output-dir "$FINAL_ROOT" \
  > "$FINAL_ROOT/audit.log" 2>&1
validate_manifest \
  "$FINAL_ROOT/audit.json" \
  strict_v4_final_paper_readiness_audit_v1
touch "$CHAIN_ROOT/chain_complete"
log_state "post-efficiency claim chain complete"
