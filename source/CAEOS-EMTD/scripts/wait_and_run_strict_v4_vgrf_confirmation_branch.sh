#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
PILOT_ROOT="$PROJECT_ROOT/results/strict_v4_validation_gated_reliability_fusion_seed307"
RESULT_ROOT="$PROJECT_ROOT/results/strict_v4_vgrf_confirmation_seed311_313"
LOCK_DIR="$RESULT_ROOT/watcher.lock.d"

mkdir -p "$RESULT_ROOT"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then exit 0; fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT
while [[ ! -f "$PILOT_ROOT/pilot_complete" ]]; do sleep 300; done
passes="$($PYTHON - "$PILOT_ROOT/analysis.json" <<'PY'
import json, sys
value = json.load(open(sys.argv[1], encoding='utf-8'))
print('true' if value.get('passes') is True and value.get('decision') == 'freeze_seed311_313_full102_confirmation' else 'false')
PY
)"
if [[ "$passes" != "true" ]]; then
  "$PYTHON" - "$PILOT_ROOT/analysis.json" "$RESULT_ROOT/not_required.json" "$RESULT_ROOT/final_selection.json" <<'PY'
import hashlib, json, sys
from pathlib import Path
source, output, selection_path = map(Path, sys.argv[1:])
payload = {'status': 'not_required', 'reason': 'seed307_pilot_gate_failed', 'pilot_analysis_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
output.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
selection = {
    'schema_version': 'strict_v4_final_self_algorithm_selection_v1',
    'status': 'complete_after_negative_seed307_pilot',
    'selected_algorithm': 'caeos_pairwise',
    'vgrf_confirmation_passes': False,
    'pilot_analysis_file_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'selection_rule': 'negative VGRF pilot makes full102 not required and retains Pairwise',
}
unsigned = json.dumps(selection, sort_keys=True, separators=(',', ':')).encode()
selection['manifest_sha256'] = hashlib.sha256(unsigned).hexdigest()
selection_path.write_text(json.dumps(selection, indent=2, sort_keys=True) + '\n', encoding='utf-8')
PY
  touch "$RESULT_ROOT/branch_complete"
  exit 0
fi
cd "$PROJECT_ROOT"
bash scripts/run_strict_v4_vgrf_confirmation_branch.sh > "$RESULT_ROOT/watcher_execution.log" 2>&1
