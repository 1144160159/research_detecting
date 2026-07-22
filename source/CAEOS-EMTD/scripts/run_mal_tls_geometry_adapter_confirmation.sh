#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-lcb-exploration-20260720}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
CSV="${MAL_TLS_CSV:-/opt/data/private/wangwt/ParkAttackKE/datasets/Mal_TLS2023/data/malicious_TLS.csv}"
RUN_ROOT="$PROJECT_ROOT/runs/mal_tls_geometry_adapter_confirmation"
RESULT_ROOT="$PROJECT_ROOT/results/mal_tls_geometry_adapter_confirmation"
PROTOCOL="$RESULT_ROOT/protocol_manifest.json"

cd "$PROJECT_ROOT"
"$PYTHON" - "$PROTOCOL" "$PROJECT_ROOT" "$CSV" <<'PY'
import hashlib, json, sys
from pathlib import Path
from create_strict_v4_external_confirmation_protocol import canonical_hash

p = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert p["manifest_sha256"] == canonical_hash(p)
assert p["confirmation_metrics_observed_at_freeze"] == 0
for name, expected in p["implementation_sha256"].items():
    assert hashlib.sha256((Path(sys.argv[2]) / name).read_bytes()).hexdigest() == expected
assert hashlib.sha256(Path(sys.argv[3]).read_bytes()).hexdigest() == p["dataset"]["sha256"]
PY

for seed in 197 199 211; do
  for scenario in caphaw cobalt panda qakbot scanners tor; do
    mapfile -t unknowns < <("$PYTHON" -c \
      'import json,sys; p=json.load(open(sys.argv[1])); print("\n".join(p["dataset"]["scenarios"][sys.argv[2]]))' \
      "$PROTOCOL" "$scenario")
    reference="$RUN_ROOT/uniform_mlp/${scenario}_seed${seed}"
    if [[ ! -s "$reference/metrics.json" ]]; then
      "$PYTHON" train.py \
        --dataset tabular --csv "$CSV" --config configs/mal_tls2023.json \
        --unknown-classes "${unknowns[@]}" --benign-class benign \
        --max-per-class 1000 --split-strategy fingerprint_grouped \
        --epochs 15 --batch-size 512 --hidden-dim 128 --embedding-dim 64 \
        --calibrator conformal --encoder-profile uniform_mlp \
        --evidence-temperature-calibration --seed "$seed" --device cuda \
        --output-dir "$reference" >> "$RESULT_ROOT/training.log" 2>&1
    fi
    candidate="$RUN_ROOT/mal_tls_geometry_preserving_adapter/${scenario}_seed${seed}"
    if [[ ! -s "$candidate/metrics.json" ]]; then
      "$PYTHON" train.py \
        --dataset tabular --csv "$CSV" --config configs/mal_tls2023.json \
        --unknown-classes "${unknowns[@]}" --benign-class benign \
        --max-per-class 1000 --split-strategy fingerprint_grouped \
        --epochs 15 --batch-size 512 --hidden-dim 128 --embedding-dim 64 \
        --calibrator conformal \
        --encoder-profile mal_tls_geometry_preserving_adapter \
        --initial-checkpoint "$reference/model.pt" --freeze-base-for-adapter \
        --consistency-weight 1.0 --evidence-temperature-calibration \
        --seed "$seed" --device cuda --output-dir "$candidate" \
        >> "$RESULT_ROOT/training.log" 2>&1
    fi
    "$PYTHON" verify_geometry_preserving_adapter_checkpoints.py \
      --reference "$reference/model.pt" --candidate "$candidate/model.pt" \
      --output "$candidate/base_equivalence.json" \
      > "$candidate/base_equivalence.log" 2>&1
  done
done

[[ "$(find "$RUN_ROOT" -name metrics.json -type f | wc -l)" -eq 36 ]]
"$PYTHON" analyze_mal_tls_geometry_adapter_confirmation.py \
  --protocol "$PROTOCOL" --run-root "$RUN_ROOT" --output-dir "$RESULT_ROOT" \
  > "$RESULT_ROOT/analysis.log" 2>&1
touch "$RESULT_ROOT/confirmation_complete"
