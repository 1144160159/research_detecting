#!/usr/bin/env bash
set -euo pipefail

action="${1:-}"
candidate="${2:-}"
prediction_execution="${3:-thread}"
cpu_set="${4:-all}"
bind="${5:-127.0.0.1:50055}"
connect="${6:-10.0.5.8:50056}"
PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/HFT-MGBS}"
CODE_ROOT="${CODE_ROOT:-${PROJECT_ROOT}/source/HFT-MGBS}"
CONDA="${CONDA:-/opt/data/private/wangwt/anaconda3/bin/conda}"
CONDA_ENV="${CONDA_ENV:-py3.9}"
MODEL="${MODEL:-${PROJECT_ROOT}/models/a09/rc1/a09_bundle.joblib}"

if [[ ! "${candidate}" =~ ^[a-z0-9_-]+$ ]]; then
  echo "candidate must match [a-z0-9_-]+" >&2
  exit 2
fi
if [[ "${prediction_execution}" != "thread" \
   && "${prediction_execution}" != "inline" ]]; then
  echo "prediction execution must be thread or inline" >&2
  exit 2
fi

run_root="${PROJECT_ROOT}/runs/runtime_online/${candidate}"
pid_file="${run_root}/service.pid"
log_file="${run_root}/service.log"
manifest="${run_root}/runtime_candidate.json"
mkdir -p "${run_root}"

stop_candidate() {
  if [[ ! -s "${pid_file}" ]]; then
    return
  fi
  local pid
  pid="$(cat "${pid_file}")"
  if [[ ! "${pid}" =~ ^[0-9]+$ ]] || ! kill -0 "${pid}" 2>/dev/null; then
    rm -f "${pid_file}"
    return
  fi
  local cmdline
  cmdline="$(tr '\0' ' ' < "/proc/${pid}/cmdline")"
  if [[ "${cmdline}" != *"hft_mgbs.gpu_service"* ]] \
    || [[ "${cmdline}" != *"${bind}"* ]]; then
    echo "refusing to stop an unverified runtime candidate: ${pid}" >&2
    exit 9
  fi
  local pgid
  pgid="$(ps -o pgid= -p "${pid}" | tr -d ' ')"
  if [[ "${pgid}" == "${pid}" ]]; then
    kill -- "-${pgid}" 2>/dev/null || true
  else
    kill "${pid}" 2>/dev/null || true
  fi
  for _ in $(seq 1 50); do
    if [[ "${pgid}" == "${pid}" ]]; then
      if ! kill -0 -- "-${pgid}" 2>/dev/null; then
        rm -f "${pid_file}"
        return
      fi
    elif ! kill -0 "${pid}" 2>/dev/null; then
      rm -f "${pid_file}"
      return
    fi
    sleep 0.1
  done
  echo "runtime candidate process group did not stop: ${pgid}" >&2
  exit 10
}

case "${action}" in
  stop)
    stop_candidate
    exit 0
    ;;
  start)
    if [[ -s "${pid_file}" ]] \
      && kill -0 "$(cat "${pid_file}")" 2>/dev/null; then
      echo "candidate already running" >&2
      exit 3
    fi
    ;;
  *)
    echo "usage: $0 {start|stop} CANDIDATE [thread|inline] [CPU_SET|all] [BIND] [CONNECT]" >&2
    exit 2
    ;;
esac

launcher=()
if [[ "${cpu_set}" != "all" ]]; then
  launcher+=(taskset -c "${cpu_set}")
fi
launcher+=(
  "${CONDA}" run --no-capture-output -n "${CONDA_ENV}"
  env PYTHONPATH=.
  OMP_NUM_THREADS=1
  OPENBLAS_NUM_THREADS=1
  MKL_NUM_THREADS=1
  NUMEXPR_NUM_THREADS=1
  python -m hft_mgbs.gpu_service
  --bind "${bind}"
  --connect "${connect}"
  --model "${MODEL}"
  --model-n-jobs 1
  --warmup-batch-size 512
  --prediction-execution "${prediction_execution}"
)

cd "${CODE_ROOT}"
nohup setsid "${launcher[@]}" > "${log_file}" 2>&1 &
pid="$!"
echo "${pid}" > "${pid_file}"

python3 - "${manifest}" "${candidate}" "${prediction_execution}" \
  "${cpu_set}" "${bind}" "${connect}" "${pid}" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

path, candidate, mode, cpu_set, bind, connect, pid = sys.argv[1:]
Path(path).write_text(
    json.dumps(
        {
            "schema_version": 1,
            "scope": "runtime_only_frozen_A09",
            "candidate": candidate,
            "prediction_execution": mode,
            "cpu_set": cpu_set,
            "bind": bind,
            "connect": connect,
            "pid": int(pid),
            "started_at": datetime.now(timezone.utc).isoformat(),
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
PY

for _ in $(seq 1 60); do
  if ! kill -0 "${pid}" 2>/dev/null; then
    tail -n 50 "${log_file}" >&2
    exit 4
  fi
  if grep -q '"status": "ready"' "${log_file}"; then
    echo "started candidate=${candidate} pid=${pid} log=${log_file}"
    exit 0
  fi
  sleep 0.5
done
echo "runtime candidate did not become ready" >&2
tail -n 50 "${log_file}" >&2
exit 5
