#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
PYTHON="${PYTHON:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
XGBOOST_ROOT="${XGBOOST_ROOT:-/opt/data/private/wangwt/python_packages/xgboost-2.1.4}"
CSV=/opt/data/private/wangwt/ParkAttackKE/datasets/Mal_TLS2023/data/malicious_TLS.csv
CONFIG="$PROJECT_ROOT/configs/mal_tls2023.json"
RUN_ROOT="$PROJECT_ROOT/runs/mal_tls_xgboost_multiseed"
RESULT_ROOT="$PROJECT_ROOT/results/mal_tls_xgboost_multiseed"
MC7_ROOT=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/runs/mal_tls_mc7_stable_multiseed
export PYTHONPATH="$XGBOOST_ROOT${PYTHONPATH:+:$PYTHONPATH}"

mkdir -p "$RESULT_ROOT"
LOCK_DIR="$RESULT_ROOT/launcher.lock.d"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "XGBoost multiseed launcher is already active: $LOCK_DIR" >&2
  exit 1
fi
cleanup() {
  rmdir "$LOCK_DIR" 2>/dev/null || true
}
trap cleanup EXIT INT TERM
cd "$PROJECT_ROOT"
VERSION="$($PYTHON -c 'import xgboost; print(xgboost.__version__)')"
"$PYTHON" create_mal_tls_xgboost_protocol.py \
  --project-root "$PROJECT_ROOT" --csv "$CSV" --config "$CONFIG" \
  --xgboost-version "$VERSION" --run-root "$RUN_ROOT" \
  --output "$RESULT_ROOT/protocol_manifest.json" \
  > "$RESULT_ROOT/protocol.log" 2>&1

for seed in 7 11 19 23 29; do
  output="$RUN_ROOT/seed$seed"
  if [[ -f "$output/metrics.json" ]]; then
    continue
  fi
  mkdir -p "$output"
  rm -f "$output/failure.json"
  if ! nice -n 15 "$PYTHON" train_classical.py \
    --model xgboost --dataset tabular --csv "$CSV" --config "$CONFIG" \
    --benign-class benign --max-per-class 500 --estimators 1000 \
    --max-depth 8 --learning-rate 0.05 --subsample 0.9 --colsample-bytree 0.9 \
    --early-stopping-rounds 30 --jobs 4 --seed "$seed" --output-dir "$output" \
    > "$output/run.log" 2>&1; then
    printf '{"seed":%s}\n' "$seed" > "$output/failure.json"
    exit 1
  fi
  if [[ ! -s "$output/metrics.json" ]]; then
    printf '{"seed":%s,"reason":"missing_metrics"}\n' "$seed" > "$output/failure.json"
    exit 1
  fi
done

"$PYTHON" summarize_mal_tls_xgboost_multiseed.py \
  --protocol "$RESULT_ROOT/protocol_manifest.json" \
  --run-root "$RUN_ROOT" --mc7-root "$MC7_ROOT" --output-dir "$RESULT_ROOT" \
  > "$RESULT_ROOT/summary.log" 2>&1
