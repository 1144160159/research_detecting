#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
ROOT="$PROJECT_ROOT/results/strict_v4_vgrf_selected_system_confirmation_v1"
DESIGN="$ROOT/design_protocol.json"
PREPARATION="$ROOT/preparation_protocol.json"
SELECTION_ROOT="$PROJECT_ROOT/results/strict_v4_vgrf_confirmation_seed311_313"
SELECTION="$SELECTION_ROOT/final_selection.json"
CONFIRMATION="$SELECTION_ROOT/summary.json"
SUMMARY="$ROOT/summary.json"
LOCK="$ROOT/watcher.lock.d"
STATE="$ROOT/state.log"

mkdir -p "$ROOT"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "VGRF selected-system watcher already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT

printf '%s waiting for final VGRF-or-Pairwise selection\n' \
  "$(date --iso-8601=seconds)" > "$STATE"
until [[ -s "$DESIGN" \
  && -s "$PREPARATION" \
  && -f "$SELECTION_ROOT/branch_complete" \
  && -s "$SELECTION" ]]; do
  sleep 60
done

selected="$("$PYTHON" - "$SELECTION" <<'PY'
import json
import sys

print(json.load(open(sys.argv[1], encoding="utf-8"))["selected_algorithm"])
PY
)"
cd "$PROJECT_ROOT"
if [[ "$selected" == "caeos_pairwise" ]]; then
  "$PYTHON" - "$DESIGN" "$PREPARATION" "$SELECTION" \
    "$ROOT/not_required.json" <<'PY'
import json
import sys
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)

design_path, preparation_path, selection_path, output = map(
    Path, sys.argv[1:]
)
design = json.loads(design_path.read_text(encoding="utf-8"))
preparation = json.loads(
    preparation_path.read_text(encoding="utf-8")
)
selection = json.loads(selection_path.read_text(encoding="utf-8"))
value = {
    "schema_version": "strict_v4_vgrf_selected_system_not_required_v1",
    "status": "complete",
    "reason": "final_self_algorithm_is_pairwise",
    "selected_algorithm": selection["selected_algorithm"],
    "design_manifest_sha256": design["manifest_sha256"],
    "preparation_protocol_manifest_sha256": preparation["manifest_sha256"],
    "final_selection_manifest_sha256": selection["manifest_sha256"],
    "input_file_sha256": {
        "design": file_hash(design_path),
        "preparation": file_hash(preparation_path),
        "final_selection": file_hash(selection_path),
    },
}
value["manifest_sha256"] = canonical_hash(value)
output.write_text(
    json.dumps(value, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY
  touch "$ROOT/branch_complete"
  printf '%s Pairwise selected; VGRF system branch not required\n' \
    "$(date --iso-8601=seconds)" >> "$STATE"
  exit 0
fi
if [[ "$selected" != "caeos_validation_gated_class_conditional_reliability_fusion" ]]; then
  echo "unsupported selected algorithm: $selected" >&2
  exit 1
fi
until [[ -s "$CONFIRMATION" ]]; do sleep 60; done
"$PYTHON" - "$DESIGN" "$PREPARATION" "$SELECTION" "$CONFIRMATION" \
  "$ROOT/execution_required.json" <<'PY'
import json
import sys
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)

design_path, preparation_path, selection_path, confirmation_path, output = (
    map(Path, sys.argv[1:])
)
items = {
    "design": json.loads(design_path.read_text(encoding="utf-8")),
    "preparation": json.loads(
        preparation_path.read_text(encoding="utf-8")
    ),
    "final_selection": json.loads(
        selection_path.read_text(encoding="utf-8")
    ),
    "vgrf_confirmation": json.loads(
        confirmation_path.read_text(encoding="utf-8")
    ),
}
value = {
    "schema_version": "strict_v4_vgrf_selected_system_execution_required_v1",
    "status": "required_before_integrated_sota_v2",
    "expected_equivalence_blocks": 204,
    "expected_comparative_corruption_pairs": 1530,
    "input_manifest_sha256": {
        name: item["manifest_sha256"]
        for name, item in items.items()
    },
    "input_file_sha256": {
        "design": file_hash(design_path),
        "preparation": file_hash(preparation_path),
        "final_selection": file_hash(selection_path),
        "vgrf_confirmation": file_hash(confirmation_path),
    },
}
value["manifest_sha256"] = canonical_hash(value)
output.write_text(
    json.dumps(value, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY
printf '%s VGRF selected; waiting for system execution summary\n' \
  "$(date --iso-8601=seconds)" >> "$STATE"
until [[ -s "$SUMMARY" ]]; do sleep 60; done
"$PYTHON" validate_strict_v4_vgrf_selected_system_summary.py \
  --design "$DESIGN" \
  --preparation "$PREPARATION" \
  --final-selection "$SELECTION" \
  --confirmation-summary "$CONFIRMATION" \
  --system-summary "$SUMMARY" \
  --output "$ROOT/validation.json" \
  > "$ROOT/validation.log" 2>&1
touch "$ROOT/branch_complete"
printf '%s VGRF selected-system branch validated\n' \
  "$(date --iso-8601=seconds)" >> "$STATE"
