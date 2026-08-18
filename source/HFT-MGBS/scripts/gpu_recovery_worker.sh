#!/usr/bin/env bash
set -euo pipefail

action="${1:-start}"
PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/HFT-MGBS}"
CODE_ROOT="${CODE_ROOT:-${PROJECT_ROOT}/source/HFT-MGBS}"
CONDA="${CONDA:-/opt/data/private/wangwt/anaconda3/bin/conda}"
CONDA_ENV="${CONDA_ENV:-py3.9}"
MODEL="${MODEL:-${PROJECT_ROOT}/models/a09/rc1/a09_bundle.joblib}"
RUN_ROOT="${PROJECT_ROOT}/runs/split_recovery_probe"
PID_FILE="${RUN_ROOT}/worker.pid"
LOG_FILE="${RUN_ROOT}/worker.log"
mkdir -p "${RUN_ROOT}"

stop_worker() {
  if [[ ! -s "${PID_FILE}" ]]; then
    return
  fi
  pid="$(cat "${PID_FILE}")"
  if [[ ! "${pid}" =~ ^[0-9]+$ ]] || ! kill -0 "${pid}" 2>/dev/null; then
    rm -f "${PID_FILE}"
    return
  fi
  cmdline="$(tr '\0' ' ' < "/proc/${pid}/cmdline")"
  if [[ "${cmdline}" != *"hft_mgbs.gpu_service"* ]] || [[ "${cmdline}" != *"50054"* ]]; then
    echo "refusing to stop an unverified recovery worker: ${pid}" >&2
    exit 9
  fi
  pgid="$(ps -o pgid= -p "${pid}" | tr -d ' ')"
  if [[ "${pgid}" == "${pid}" ]]; then
    kill -- "-${pgid}" 2>/dev/null || true
  else
    kill "${pid}" 2>/dev/null || true
  fi
  rm -f "${PID_FILE}"
}

case "${action}" in
  stop)
    stop_worker
    exit 0
    ;;
  restart)
    stop_worker
    ;;
  start)
    if [[ -s "${PID_FILE}" ]] && kill -0 "$(cat "${PID_FILE}")" 2>/dev/null; then
      echo "already_running pid=$(cat "${PID_FILE}")"
      exit 0
    fi
    ;;
  *)
    echo "usage: $0 {start|restart|stop}" >&2
    exit 2
    ;;
esac

cd "${CODE_ROOT}"
nohup setsid "${CONDA}" run --no-capture-output -n "${CONDA_ENV}" \
  env PYTHONPATH=. OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  python -m hft_mgbs.gpu_service \
  --bind 127.0.0.1:50054 \
  --connect 10.0.5.8:50053 \
  --model "${MODEL}" \
  --model-n-jobs 1 \
  --warmup-batch-size 512 \
  > "${LOG_FILE}" 2>&1 &
pid="$!"
echo "${pid}" > "${PID_FILE}"

for _ in $(seq 1 30); do
  if ! kill -0 "${pid}" 2>/dev/null; then
    tail -n 50 "${LOG_FILE}" >&2
    exit 3
  fi
  if grep -q '"status": "ready"' "${LOG_FILE}"; then
    echo "started pid=${pid} log=${LOG_FILE}"
    exit 0
  fi
  sleep 1
done
echo "recovery worker did not become ready" >&2
exit 4
