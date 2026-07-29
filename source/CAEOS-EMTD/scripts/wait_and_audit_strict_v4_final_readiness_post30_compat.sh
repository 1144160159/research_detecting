#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
PROTOCOL_ROOT="$PROJECT_ROOT/results/strict_v4_final_readiness_post30_compat_v1"
PROTOCOL="$PROTOCOL_ROOT/protocol_manifest.json"
FINAL_ROOT="$PROJECT_ROOT/results/strict_v4_final_paper_readiness"
CHAIN_ROOT="$PROJECT_ROOT/results/strict_v4_postefficiency_claim_chain_v2"
ACCURACY="$PROJECT_ROOT/results/strict_v4_comprehensive_sota_audit_v12/audit.json"
COMPAT="$PROJECT_ROOT/results/strict_v4_comprehensive_sota_audit_v12/supersession_compatibility_v1.json"
EFFICIENCY="$PROJECT_ROOT/results/strict_v4_final_efficiency_v5/summary.json"
OPTIMIZED="$PROJECT_ROOT/results/strict_v4_optimized_efficiency_v6/summary.json"
TENSORIZED="$PROJECT_ROOT/results/strict_v4_tensorized_full_efficiency"
CORRUPTION="$PROJECT_ROOT/results/strict_v4_postselection_corruption_confirmation/summary.json"
COMPARATIVE="$PROJECT_ROOT/results/strict_v4_comparative_corruption/summary.json"
LOCK="$PROTOCOL_ROOT/watcher.lock.d"
STATE="$PROTOCOL_ROOT/state.log"

mkdir -p "$PROTOCOL_ROOT"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "post-30 compatibility readiness watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT

printf '%s waiting for final readiness inputs\n' \
  "$(date --iso-8601=seconds)" > "$STATE"
until [[ -s "$PROTOCOL" \
  && -s "$EFFICIENCY" \
  && -s "$OPTIMIZED" \
  && -f "$TENSORIZED/branch_complete" \
  && -s "$CORRUPTION" \
  && -s "$COMPARATIVE" ]]; do
  sleep 60
done

cd "$PROJECT_ROOT"
"$PYTHON" audit_strict_v4_final_paper_readiness_post30_compat.py \
  --protocol "$PROTOCOL" \
  --accuracy-audit "$ACCURACY" \
  --post30-compatibility "$COMPAT" \
  --efficiency-summary "$EFFICIENCY" \
  --optimized-efficiency-summary "$OPTIMIZED" \
  --tensorized-full-root "$TENSORIZED" \
  --corruption-summary "$CORRUPTION" \
  --comparative-corruption-summary "$COMPARATIVE" \
  --output-dir "$FINAL_ROOT" \
  > "$PROTOCOL_ROOT/audit.log" 2>&1
"$PYTHON" - "$FINAL_ROOT/audit.json" <<'PY'
import json
import sys
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import canonical_hash

path = Path(sys.argv[1])
value = json.loads(path.read_text(encoding="utf-8"))
assert value["schema_version"] == "strict_v4_final_paper_readiness_audit_v4"
assert value["manifest_sha256"] == canonical_hash(value)
assert value["gates"]["post30_baseline_coverage_complete"] is True
PY
touch "$CHAIN_ROOT/chain_complete"
printf '%s compatibility readiness complete\n' \
  "$(date --iso-8601=seconds)" >> "$STATE"
