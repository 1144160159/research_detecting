#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-lcb-exploration-20260720}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
CSV="${MAL_TLS_CSV:-/opt/data/private/wangwt/ParkAttackKE/datasets/Mal_TLS2023/data/malicious_TLS.csv}"
RUN_ROOT="$PROJECT_ROOT/runs/mal_tls_conservative_residual_pilot_seed193"
RESULT_ROOT="$PROJECT_ROOT/results/mal_tls_conservative_residual_pilot_seed193"
PROTOCOL="$RESULT_ROOT/protocol_manifest.json"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT"
if [[ ! -s "$PROTOCOL" ]]; then
  "$PYTHON" create_mal_tls_conservative_residual_pilot_protocol.py \
    --dataset "$CSV" --project-root "$PROJECT_ROOT" --run-root "$RUN_ROOT" \
    --output "$PROTOCOL" > "$RESULT_ROOT/freeze.log" 2>&1
fi

"$PYTHON" - "$PROTOCOL" "$PROJECT_ROOT" "$CSV" <<'PY'
import hashlib, json, sys
from pathlib import Path
from create_strict_v4_external_confirmation_protocol import canonical_hash

protocol = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert protocol["manifest_sha256"] == canonical_hash(protocol)
assert protocol["metrics_observed_at_freeze"] == 0
for name, expected in protocol["implementation_sha256"].items():
    assert hashlib.sha256((Path(sys.argv[2]) / name).read_bytes()).hexdigest() == expected
assert hashlib.sha256(Path(sys.argv[3]).read_bytes()).hexdigest() == protocol["dataset"]["sha256"]
PY

for profile in uniform_mlp mal_tls_conservative_residual; do
  for scenario in caphaw cobalt panda qakbot scanners tor; do
    mapfile -t unknowns < <("$PYTHON" -c \
      'import json,sys; p=json.load(open(sys.argv[1])); print("\n".join(p["dataset"]["scenarios"][sys.argv[2]]))' \
      "$PROTOCOL" "$scenario")
    output="$RUN_ROOT/$profile/${scenario}_seed193"
    if [[ -s "$output/metrics.json" && -s "$output/data_metadata.json" && -s "$output/evidence_temperature.json" ]]; then
      continue
    fi
    "$PYTHON" train.py \
      --dataset tabular --csv "$CSV" --config configs/mal_tls2023.json \
      --unknown-classes "${unknowns[@]}" --benign-class benign \
      --max-per-class 1000 --split-strategy fingerprint_grouped \
      --epochs 15 --batch-size 512 --hidden-dim 128 --embedding-dim 64 \
      --calibrator conformal --encoder-profile "$profile" \
      --evidence-temperature-calibration \
      --seed 193 --device cuda --output-dir "$output" \
      >> "$RESULT_ROOT/training.log" 2>&1
  done
done

[[ "$(find "$RUN_ROOT" -name metrics.json -type f | wc -l)" -eq 12 ]]
"$PYTHON" analyze_mal_tls_conservative_residual_pilot.py \
  --protocol "$PROTOCOL" --run-root "$RUN_ROOT" --output-dir "$RESULT_ROOT" \
  > "$RESULT_ROOT/analysis.log" 2>&1
touch "$RESULT_ROOT/pilot_complete"
