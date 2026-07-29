#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
DATA_ROOT="${DATA_ROOT:-/opt/data/private/wangwt/ParkAttackKE/datasets/caeos_external_open_set_v1}"
AUDIT_ROOT="$PROJECT_ROOT/results/gpu_dataset_full_admission_audit_v1"
RESULT_ROOT="$PROJECT_ROOT/results/gpu_external_dataset_preparation_v1"
PROTOCOL="$PROJECT_ROOT/results/gpu_external_dataset_preparation_protocol_v1/protocol.json"
EXPANSION="$PROJECT_ROOT/results/gpu_malicious_dataset_expansion_protocol_v1/protocol.json"
LOCK_DIR="$RESULT_ROOT/run.lock.d"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT" "$DATA_ROOT"
test -s "$AUDIT_ROOT/admission_audit.json"
test -f "$AUDIT_ROOT/admission_passed"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "GPU external dataset preparation is already active" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

"$PYTHON" - "$PROTOCOL" <<'PY'
import json, sys
from create_gpu_external_preparation_protocol import verify_protocol
verify_protocol(json.load(open(sys.argv[1], encoding="utf-8")))
PY

if [[ ! -f "$DATA_ROOT/LSNM2024/preparation_complete" ]]; then
  ionice -c3 nice -n 15 "$PYTHON" prepare_gpu_external_datasets.py \
    --dataset LSNM2024 \
    --admission-audit "$AUDIT_ROOT/admission_audit.json" \
    --expansion-protocol "$EXPANSION" \
    --config configs/lsnm2024_external.json \
    --output-root "$DATA_ROOT" \
    --seeds 223 227 229 --groups-per-label 500 --rows-per-group 8 \
    > "$RESULT_ROOT/lsnm2024.log" 2>&1
fi

if [[ ! -f "$DATA_ROOT/CICDDoS2019/preparation_complete" ]]; then
  ionice -c3 nice -n 15 "$PYTHON" prepare_gpu_external_datasets.py \
    --dataset CICDDoS2019 \
    --admission-audit "$AUDIT_ROOT/admission_audit.json" \
    --expansion-protocol "$EXPANSION" \
    --config configs/cicids2017_strict.json \
    --output-root "$DATA_ROOT" \
    --seeds 223 227 229 --groups-per-label 4000 --rows-per-group 1 \
    > "$RESULT_ROOT/cicddos2019.log" 2>&1
fi

"$PYTHON" - "$DATA_ROOT" "$RESULT_ROOT" <<'PY'
import hashlib, json, sys
from pathlib import Path

data_root, result_root = map(Path, sys.argv[1:])
datasets = {}
for name in ("LSNM2024", "CICDDoS2019"):
    path = data_root / name / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert manifest["passed"] is True
    datasets[name] = {
        "manifest": str(path),
        "manifest_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "seed_rows": {
            seed: entry["rows"] for seed, entry in manifest["files"].items()
        },
    }
combined = {
    "schema_version": "gpu_external_dataset_preparation_summary_v1",
    "status": "complete",
    "datasets": datasets,
    "ready_for_frozen_external_experiments": True,
}
(result_root / "summary.json").write_text(
    json.dumps(combined, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
PY
touch "$RESULT_ROOT/preparation_complete"
