#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
ROOT="$PROJECT_ROOT/results/strict_v4_mdr_integrated_comprehensive_sota_v1"
PROTOCOL="$ROOT/protocol_manifest.json"
POST_DESIGN="$PROJECT_ROOT/results/strict_v4_mdr_postselection_evidence_v1/design_protocol.json"
OPENDETECT_DESIGN="$PROJECT_ROOT/results/strict_v4_mdr_opendetect_efficiency_v1/design_protocol.json"
MDR="$PROJECT_ROOT/results/strict_v4_mdr_caeos_confirmation"
SELECTION="$MDR/final_selection.json"
EXTERNAL="$PROJECT_ROOT/results/strict_v4_mdr_external_malicious_v1"
SYSTEM="$PROJECT_ROOT/results/strict_v4_mdr_selected_system_v1"
OPENDETECT="$PROJECT_ROOT/results/strict_v4_mdr_opendetect_efficiency_v1"
PARROT="$PROJECT_ROOT/results/strict_v4_mdr_parrot_safety_v1"
LOCK="$ROOT/watcher.lock.d"
STATE="$ROOT/watcher_state.log"

mkdir -p "$ROOT"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "MDR integrated SOTA watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT

log_state() {
  printf '%s %s\n' "$(date --iso-8601=seconds)" "$*" | tee -a "$STATE"
}

cd "$PROJECT_ROOT"
: > "$STATE"
if [[ ! -s "$PROTOCOL" ]]; then
  log_state "missing pre-result integrated protocol; refusing post-result freeze"
  exit 1
fi
log_state "waiting for canonical MDR selection"
until [[ -f "$MDR/branch_complete" && -s "$SELECTION" ]]; do
  sleep 60
done

selected="$("$PYTHON" - "$SELECTION" <<'PY'
import json, sys
from create_strict_v4_external_confirmation_protocol import canonical_hash
value = json.load(open(sys.argv[1], encoding="utf-8"))
if value.get("schema_version") != "strict_v4_final_self_algorithm_selection_v2":
    raise SystemExit("wrong final selection schema")
if value.get("manifest_sha256") != canonical_hash(value):
    raise SystemExit("final selection canonical SHA mismatch")
print(value.get("selected_algorithm", ""))
PY
)"

if [[ "$selected" != "mdr_caeos_v1" ]]; then
  "$PYTHON" - "$PROTOCOL" "$SELECTION" "$ROOT/not_required.json" <<'PY'
import hashlib, json, sys
from pathlib import Path
from create_strict_v4_external_confirmation_protocol import canonical_hash
protocol_path, selection_path, output = map(Path, sys.argv[1:])
protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
selection = json.loads(selection_path.read_text(encoding="utf-8"))
value = {
    "schema_version": "strict_v4_mdr_integrated_sota_not_required_v1",
    "status": "not_required",
    "reason": "final_reserved_confirmation_did_not_select_mdr",
    "selected_algorithm": selection.get("selected_algorithm"),
    "integrated_protocol_manifest_sha256": protocol["manifest_sha256"],
    "selection_manifest_sha256": selection["manifest_sha256"],
    "input_file_sha256": {
        "protocol": hashlib.sha256(protocol_path.read_bytes()).hexdigest(),
        "selection": hashlib.sha256(selection_path.read_bytes()).hexdigest(),
    },
    "accuracy_robustness_external_sota_with_deployability_supported": False,
    "multidimensional_comprehensive_sota_supported": False,
}
value["manifest_sha256"] = canonical_hash(value)
output.write_text(
    json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
PY
  touch "$ROOT/audit_complete" "$ROOT/branch_complete"
  log_state "MDR not selected; canonical not-required record written"
  exit 0
fi

log_state "MDR selected; waiting for all five evidence branches"
until [[ -f "$EXTERNAL/branch_complete" \
  && -f "$SYSTEM/branch_complete" \
  && -f "$OPENDETECT/branch_complete" \
  && -f "$PARROT/branch_complete" \
  && -s "$MDR/protocol_manifest.json" \
  && -s "$MDR/summary.json" \
  && -s "$MDR/audit.json" \
  && -s "$EXTERNAL/protocol_manifest.json" \
  && -s "$EXTERNAL/summary.json" \
  && -s "$EXTERNAL/audit.json" \
  && -s "$SYSTEM/protocol_manifest.json" \
  && -s "$SYSTEM/summary.json" \
  && -s "$SYSTEM/audit.json" \
  && -s "$OPENDETECT/protocol_manifest.json" \
  && -s "$OPENDETECT/summary.json" \
  && -s "$OPENDETECT/audit.json" \
  && -s "$PARROT/protocol_manifest.json" \
  && -s "$PARROT/summary.json" \
  && -s "$PARROT/audit.json" ]]; do
  sleep 300
done

log_state "auditing frozen MDR evidence without gate substitution"
"$PYTHON" audit_strict_v4_mdr_integrated_comprehensive_sota.py \
  --project-root "$PROJECT_ROOT" \
  --integrated-protocol "$PROTOCOL" \
  --postselection-design "$POST_DESIGN" \
  --opendetect-efficiency-design "$OPENDETECT_DESIGN" \
  --selection "$SELECTION" \
  --confirmation-protocol "$MDR/protocol_manifest.json" \
  --confirmation-summary "$MDR/summary.json" \
  --confirmation-audit "$MDR/audit.json" \
  --external-protocol "$EXTERNAL/protocol_manifest.json" \
  --external-summary "$EXTERNAL/summary.json" \
  --external-audit "$EXTERNAL/audit.json" \
  --system-protocol "$SYSTEM/protocol_manifest.json" \
  --system-summary "$SYSTEM/summary.json" \
  --system-audit "$SYSTEM/audit.json" \
  --opendetect-protocol "$OPENDETECT/protocol_manifest.json" \
  --opendetect-summary "$OPENDETECT/summary.json" \
  --opendetect-audit "$OPENDETECT/audit.json" \
  --parrot-protocol "$PARROT/protocol_manifest.json" \
  --parrot-summary "$PARROT/summary.json" \
  --parrot-audit "$PARROT/audit.json" \
  --output "$ROOT/audit.json" \
  > "$ROOT/audit.log" 2>&1

"$PYTHON" - "$ROOT/audit.json" <<'PY'
import json, sys
value = json.load(open(sys.argv[1], encoding="utf-8"))
if value.get("passes") is not True:
    raise SystemExit("MDR integrated audit integrity failed")
PY
touch "$ROOT/audit_complete" "$ROOT/branch_complete"
log_state "MDR integrated evidence audit complete"
