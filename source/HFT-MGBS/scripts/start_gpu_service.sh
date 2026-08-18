#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/HFT-MGBS}"
CODE_ROOT="${CODE_ROOT:-${PROJECT_ROOT}/source/HFT-MGBS}"
CONDA_ENV="${CONDA_ENV:-py3.9}"
PYTHON_BIN="${PYTHON_BIN:-/opt/data/private/wangwt/anaconda3/envs/${CONDA_ENV}/bin/python}"
MODEL_DIR="${MODEL_DIR:-${PROJECT_ROOT}/models/a09/rc1}"
MODEL="${MODEL:-${MODEL_DIR}/a09_bundle.joblib}"
MODEL_REQUESTED="${MODEL}"
MODEL_N_JOBS="${MODEL_N_JOBS:-1}"
WARMUP_BATCH_SIZE="${WARMUP_BATCH_SIZE:-512}"
MODEL_THREAD_LIMIT="${MODEL_THREAD_LIMIT:-1}"
PREDICTION_EXECUTION="${PREDICTION_EXECUTION:-thread}"
INFERENCE_ENGINE="${INFERENCE_ENGINE:-sklearn}"
CPU_SET="${CPU_SET:-all}"
BIND="${BIND:-0.0.0.0:50051}"
CONNECT="${CONNECT:-10.0.5.8:50052}"
RUN_ROOT="${PROJECT_ROOT}/runs/split_deployment"
PID_FILE="${RUN_ROOT}/gpu_service.pid"
LOG_FILE="${RUN_ROOT}/gpu_service.log"
RUNTIME_MANIFEST="${RUN_ROOT}/runtime_manifest.json"
RESTART="${RESTART:-0}"

if [[ ! -f "${MODEL}" ]]; then
  echo "A09 model bundle does not exist: ${MODEL}" >&2
  exit 2
fi
if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "frozen Python interpreter is not executable: ${PYTHON_BIN}" >&2
  exit 2
fi
PYTHON_BIN="$(readlink -f "${PYTHON_BIN}")"
CODE_ROOT_REAL="$(readlink -f "${CODE_ROOT}")"
MODEL="$(readlink -f "${MODEL}")"
SCRIPT_REAL="$(readlink -f "$0")"
if [[ ! -f "${MODEL}" || ! -f "${SCRIPT_REAL}" ]]; then
  echo "model or launcher could not be resolved to a regular file" >&2
  exit 2
fi
if [[ "${PREDICTION_EXECUTION}" != "thread" \
   && "${PREDICTION_EXECUTION}" != "inline" ]]; then
  echo "PREDICTION_EXECUTION must be thread or inline" >&2
  exit 2
fi
if [[ "${INFERENCE_ENGINE}" != "sklearn" \
   && "${INFERENCE_ENGINE}" != "numpy_exact" ]]; then
  echo "INFERENCE_ENGINE must be sklearn or numpy_exact" >&2
  exit 2
fi
if [[ ! -f "${CODE_ROOT_REAL}/hft_mgbs/gpu_service.py" ]] \
  || [[ "${INFERENCE_ENGINE}" == "numpy_exact" \
     && ! -f "${CODE_ROOT_REAL}/hft_mgbs/a09_numpy_inference.py" ]]; then
  echo "selected inference engine source is missing" >&2
  exit 2
fi
if [[ "${CPU_SET}" != "all" ]] \
  && ! taskset -c "${CPU_SET}" true >/dev/null 2>&1; then
  echo "CPU_SET is invalid or unavailable: ${CPU_SET}" >&2
  exit 2
fi
case "${PREDICTION_EXECUTION}:${CPU_SET}" in
  thread:all) RUNTIME_CANDIDATE="thread_all" ;;
  inline:all) RUNTIME_CANDIDATE="inline_all" ;;
  thread:0-3) RUNTIME_CANDIDATE="thread_cpu0_3" ;;
  inline:0-3) RUNTIME_CANDIDATE="inline_cpu0_3" ;;
  inline:6) RUNTIME_CANDIDATE="inline_cpu6" ;;
  *)
    echo "runtime is outside the frozen candidate set" >&2
    exit 2
    ;;
esac
mkdir -p "${RUN_ROOT}"

bind_port="${BIND##*:}"
if [[ ! "${bind_port}" =~ ^[1-9][0-9]*$ ]] \
  || (( bind_port > 65535 )); then
  echo "BIND must end in a valid TCP port" >&2
  exit 2
fi

has_exact_pair() {
  local expected_name="$1"
  local expected_value="$2"
  shift 2
  local -a values=("$@")
  local index
  for ((index = 0; index + 1 < ${#values[@]}; index++)); do
    if [[ "${values[index]}" == "${expected_name}" \
       && "${values[index + 1]}" == "${expected_value}" ]]; then
      return 0
    fi
  done
  return 1
}

is_expected_service_pid() {
  local candidate_pid="$1"
  [[ "${candidate_pid}" =~ ^[1-9][0-9]*$ ]] || return 1
  [[ -r "/proc/${candidate_pid}/cmdline" ]] || return 1
  [[ "$(readlink -f "/proc/${candidate_pid}/exe")" == "${PYTHON_BIN}" ]] || return 1
  [[ "$(readlink -f "/proc/${candidate_pid}/cwd")" == "${CODE_ROOT_REAL}" ]] || return 1
  local -a argv=()
  mapfile -d '' -t argv < "/proc/${candidate_pid}/cmdline"
  has_exact_pair -m hft_mgbs.gpu_service "${argv[@]}" || return 1
  has_exact_pair --bind "${BIND}" "${argv[@]}" || return 1
  has_exact_pair --connect "${CONNECT}" "${argv[@]}" || return 1
  has_exact_pair --model "${MODEL}" "${argv[@]}" || return 1
  has_exact_pair --inference-engine "${INFERENCE_ENGINE}" "${argv[@]}" \
    || return 1
}

process_start_ticks() {
  local candidate_pid="$1"
  [[ -r "/proc/${candidate_pid}/stat" ]] || return 0
  awk '{print $22}' "/proc/${candidate_pid}/stat" 2>/dev/null || true
}

same_process() {
  local candidate_pid="$1"
  local expected_start_ticks="$2"
  [[ -n "${expected_start_ticks}" ]] \
    && [[ "$(process_start_ticks "${candidate_pid}")" == "${expected_start_ticks}" ]]
}

is_legacy_conda_wrapper_pid() {
  local candidate_pid="$1"
  [[ "${candidate_pid}" =~ ^[1-9][0-9]*$ ]] || return 1
  [[ -r "/proc/${candidate_pid}/cmdline" ]] || return 1
  [[ "$(readlink -f "/proc/${candidate_pid}/cwd")" == "${CODE_ROOT_REAL}" ]] \
    || return 1
  local -a argv=()
  mapfile -d '' -t argv < "/proc/${candidate_pid}/cmdline"
  local value saw_conda=0 saw_run=0
  for value in "${argv[@]}"; do
    [[ "${value##*/}" == "conda" ]] && saw_conda=1
    [[ "${value}" == "run" ]] && saw_run=1
  done
  (( saw_conda == 1 && saw_run == 1 )) || return 1
  has_exact_pair -m hft_mgbs.gpu_service "${argv[@]}" || return 1
  has_exact_pair --bind "${BIND}" "${argv[@]}" || return 1
  has_exact_pair --connect "${CONNECT}" "${argv[@]}" || return 1
  has_exact_pair --model "${MODEL_REQUESTED}" "${argv[@]}" \
    || has_exact_pair --model "${MODEL}" "${argv[@]}" \
    || return 1
}

listener_pid() {
  ss -H -ltnp "sport = :${bind_port}" 2>/dev/null \
    | sed -n 's/.*pid=\([0-9][0-9]*\).*/\1/p' \
    | sort -u
}

old_pid=""
if [[ -s "${PID_FILE}" ]]; then
  old_pid="$(<"${PID_FILE}")"
fi
active_listener_pid="$(listener_pid)"
old_pid_owns_listener=false
old_pid_start_ticks=""
old_pid_legacy_verified=false
if [[ "${old_pid}" =~ ^[1-9][0-9]*$ ]]; then
  old_pid_start_ticks="$(process_start_ticks "${old_pid}")"
fi
if [[ "${old_pid}" =~ ^[1-9][0-9]*$ \
   && "${active_listener_pid}" =~ ^[1-9][0-9]*$ ]]; then
  ancestor="${active_listener_pid}"
  while [[ "${ancestor}" =~ ^[1-9][0-9]*$ && "${ancestor}" != "1" ]]; do
    if [[ "${ancestor}" == "${old_pid}" ]]; then
      old_pid_owns_listener=true
      break
    fi
    ancestor="$(awk '/^PPid:/ {print $2}' "/proc/${ancestor}/status" 2>/dev/null || true)"
  done
  if [[ "${old_pid_owns_listener}" == "true" ]] \
    && is_legacy_conda_wrapper_pid "${old_pid}"; then
    old_pid_legacy_verified=true
  fi
fi

stop_verified_service() {
  local candidate_pid="$1"
  local start_ticks="$2"
  if ! same_process "${candidate_pid}" "${start_ticks}" \
    || ! is_expected_service_pid "${candidate_pid}"; then
    echo "service identity changed before TERM; refusing signal" >&2
    return 1
  fi
  kill -TERM "${candidate_pid}"
  for _ in $(seq 1 50); do
    if ! same_process "${candidate_pid}" "${start_ticks}"; then
      return 0
    fi
    sleep 0.1
  done
  if ! is_expected_service_pid "${candidate_pid}"; then
    echo "service identity changed before KILL; refusing signal" >&2
    return 1
  fi
  kill -KILL "${candidate_pid}"
  for _ in $(seq 1 20); do
    if ! same_process "${candidate_pid}" "${start_ticks}"; then
      return 0
    fi
    sleep 0.1
  done
  echo "verified service did not terminate" >&2
  return 1
}

stop_verified_legacy_wrapper() {
  local candidate_pid="$1"
  local start_ticks="$2"
  if ! same_process "${candidate_pid}" "${start_ticks}" \
    || ! is_legacy_conda_wrapper_pid "${candidate_pid}"; then
    echo "legacy conda wrapper identity changed; refusing signal" >&2
    return 1
  fi
  kill -TERM "${candidate_pid}"
  for _ in $(seq 1 50); do
    if ! same_process "${candidate_pid}" "${start_ticks}"; then
      return 0
    fi
    sleep 0.1
  done
  if ! is_legacy_conda_wrapper_pid "${candidate_pid}"; then
    echo "legacy conda wrapper identity changed before KILL" >&2
    return 1
  fi
  kill -KILL "${candidate_pid}"
  for _ in $(seq 1 20); do
    if ! same_process "${candidate_pid}" "${start_ticks}"; then
      return 0
    fi
    sleep 0.1
  done
  echo "legacy conda wrapper did not terminate" >&2
  return 1
}

if [[ -n "${active_listener_pid}" ]]; then
  active_listener_start_ticks="$(process_start_ticks "${active_listener_pid}")"
  active_listener_current_verified=false
  active_listener_legacy_verified=false
  if is_expected_service_pid "${active_listener_pid}"; then
    active_listener_current_verified=true
  elif [[ "${old_pid_owns_listener}" == "true" \
       && "${old_pid_legacy_verified}" == "true" ]]; then
    # One-time migration: the listener is the exact child proven from the
    # frozen legacy conda wrapper. Validate its service argv independently.
    local_listener_argv=()
    mapfile -d '' -t local_listener_argv \
      < "/proc/${active_listener_pid}/cmdline"
    if [[ "$(readlink -f "/proc/${active_listener_pid}/cwd")" == "${CODE_ROOT_REAL}" ]] \
      && has_exact_pair -m hft_mgbs.gpu_service "${local_listener_argv[@]}" \
      && has_exact_pair --bind "${BIND}" "${local_listener_argv[@]}" \
      && has_exact_pair --connect "${CONNECT}" "${local_listener_argv[@]}" \
      && { has_exact_pair --model "${MODEL_REQUESTED}" "${local_listener_argv[@]}" \
        || has_exact_pair --model "${MODEL}" "${local_listener_argv[@]}"; }; then
      active_listener_legacy_verified=true
    fi
  fi
  if [[ "${active_listener_current_verified}" != "true" \
     && "${active_listener_legacy_verified}" != "true" ]]; then
    echo "port ${bind_port} belongs to an unverified process; refusing mutation" >&2
    exit 3
  fi
  if [[ "${RESTART}" != "1" ]]; then
    if [[ "${active_listener_current_verified}" != "true" ]]; then
      echo "verified legacy service requires RESTART=1 migration" >&2
      exit 3
    fi
    if [[ "${old_pid}" != "${active_listener_pid}" ]]; then
      echo "live listener is verified but PID file is not current" >&2
      exit 3
    fi
    echo "already_running pid=${active_listener_pid}"
    exit 0
  fi
  if [[ "${active_listener_current_verified}" == "true" ]]; then
    stop_verified_service \
      "${active_listener_pid}" "${active_listener_start_ticks}"
  else
    if ! same_process "${old_pid}" "${old_pid_start_ticks}" \
      || ! is_legacy_conda_wrapper_pid "${old_pid}"; then
      echo "legacy wrapper identity changed before migration TERM" >&2
      exit 3
    fi
    kill -TERM "${old_pid}"
    for _ in $(seq 1 50); do
      if ! same_process "${active_listener_pid}" "${active_listener_start_ticks}"; then
        break
      fi
      sleep 0.1
    done
    if same_process "${active_listener_pid}" "${active_listener_start_ticks}"; then
      echo "legacy service listener did not stop with its verified wrapper" >&2
      exit 3
    fi
    for _ in $(seq 1 50); do
      if ! same_process "${old_pid}" "${old_pid_start_ticks}"; then
        break
      fi
      sleep 0.1
    done
    if same_process "${old_pid}" "${old_pid_start_ticks}"; then
      if ! is_legacy_conda_wrapper_pid "${old_pid}"; then
        echo "legacy wrapper identity changed after child stop" >&2
        exit 3
      fi
      kill -KILL "${old_pid}"
    fi
  fi
fi
if [[ -n "${old_pid}" && "${old_pid}" != "${active_listener_pid}" \
   && "${active_listener_legacy_verified:-false}" != "true" ]] \
  && same_process "${old_pid}" "${old_pid_start_ticks}"; then
  if [[ "${old_pid_owns_listener}" != "true" \
     || "${old_pid_legacy_verified}" != "true" ]]; then
    echo "stale PID file names a live unrelated process; refusing mutation" >&2
    exit 3
  fi
  stop_verified_legacy_wrapper "${old_pid}" "${old_pid_start_ticks}"
fi
rm -f "${PID_FILE}"
if [[ -n "$(listener_pid)" ]]; then
  echo "GPU listener did not stop cleanly" >&2
  exit 3
fi

# Only update the convenience link after every ownership/refusal gate passed.
mkdir -p "${PROJECT_ROOT}/models/a09"
ln -sfn "${MODEL_DIR}" "${PROJECT_ROOT}/models/a09/current"

cd "${CODE_ROOT}"
launcher=()
if [[ "${CPU_SET}" != "all" ]]; then
  launcher+=(taskset -c "${CPU_SET}")
fi
launcher+=(
  env PYTHONPATH=.
  OMP_NUM_THREADS="${MODEL_THREAD_LIMIT}"
  OPENBLAS_NUM_THREADS="${MODEL_THREAD_LIMIT}"
  MKL_NUM_THREADS="${MODEL_THREAD_LIMIT}"
  NUMEXPR_NUM_THREADS="${MODEL_THREAD_LIMIT}"
  "${PYTHON_BIN}" -m hft_mgbs.gpu_service
  --bind "${BIND}"
  --connect "${CONNECT}"
  --model "${MODEL}"
  --model-n-jobs "${MODEL_N_JOBS}"
  --warmup-batch-size "${WARMUP_BATCH_SIZE}"
  --prediction-execution "${PREDICTION_EXECUTION}"
  --inference-engine "${INFERENCE_ENGINE}"
)
nohup setsid "${launcher[@]}" > "${LOG_FILE}" 2>&1 &
pid="$!"
pid_start_ticks=""
for _ in $(seq 1 10); do
  pid_start_ticks="$(process_start_ticks "${pid}")"
  [[ -n "${pid_start_ticks}" ]] && break
  sleep 0.01
done
startup_complete=0
manifest_tmp="${RUNTIME_MANIFEST}.tmp.${pid}"
pid_tmp="${PID_FILE}.tmp.${pid}"
cleanup_startup() {
  local status=$?
  trap - EXIT HUP INT TERM
  rm -f "${manifest_tmp}" "${pid_tmp}"
  if (( startup_complete == 0 )) \
    && same_process "${pid}" "${pid_start_ticks}"; then
    kill -TERM "${pid}" 2>/dev/null || true
    for _ in $(seq 1 20); do
      same_process "${pid}" "${pid_start_ticks}" || break
      sleep 0.1
    done
    if same_process "${pid}" "${pid_start_ticks}"; then
      kill -KILL "${pid}" 2>/dev/null || true
    fi
  fi
  return "${status}"
}
trap cleanup_startup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

for _ in $(seq 1 30); do
  if ! kill -0 "${pid}" 2>/dev/null; then
    echo "service exited during startup" >&2
    tail -n 50 "${LOG_FILE}" >&2
    exit 3
  fi
  if grep -q '"status": "ready"' "${LOG_FILE}"; then
    observed_listener_pid="$(listener_pid)"
    if [[ "${observed_listener_pid}" != "${pid}" ]] \
      || ! same_process "${pid}" "${pid_start_ticks}" \
      || ! is_expected_service_pid "${pid}"; then
      echo "ready marker is not owned by the frozen service process" >&2
      exit 3
    fi
    actual_cpu_set="$(
      awk '/^Cpus_allowed_list:/ {print $2}' "/proc/${pid}/status"
    )"
    [[ -n "${actual_cpu_set}" ]] || {
      echo "could not resolve service CPU affinity" >&2
      exit 3
    }
    process_group_id="$(ps -o pgid= -p "${pid}" | tr -d ' ')"
    model_sha256="$(sha256sum "${MODEL}" | awk '{print $1}')"
    service_source_sha256="$(sha256sum "${CODE_ROOT}/hft_mgbs/gpu_service.py" | awk '{print $1}')"
    numpy_engine_source_sha256=""
    if [[ "${INFERENCE_ENGINE}" == "numpy_exact" ]]; then
      numpy_engine_source_sha256="$(sha256sum "${CODE_ROOT}/hft_mgbs/a09_numpy_inference.py" | awk '{print $1}')"
    fi
    launcher_sha256="$(sha256sum "${SCRIPT_REAL}" | awk '{print $1}')"
    command_sha256="$(sha256sum "/proc/${pid}/cmdline" | awk '{print $1}')"
    "${PYTHON_BIN}" - "${manifest_tmp}" "${pid}" "${pid_start_ticks}" \
      "${process_group_id}" \
      "${PYTHON_BIN}" "${CODE_ROOT_REAL}" "${command_sha256}" \
      "${model_sha256}" "${service_source_sha256}" \
      "${numpy_engine_source_sha256}" "${launcher_sha256}" \
      "${PREDICTION_EXECUTION}" "${INFERENCE_ENGINE}" \
      "${CPU_SET}" "${actual_cpu_set}" \
      "${MODEL_N_JOBS}" "${MODEL_THREAD_LIMIT}" \
      "${BIND}" "${CONNECT}" "${MODEL}" "${RUNTIME_CANDIDATE}" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

(
    path,
    pid,
    process_start_ticks,
    process_group_id,
    python_executable,
    working_directory,
    command_sha256,
    model_sha256,
    service_source_sha256,
    numpy_engine_source_sha256,
    launcher_sha256,
    prediction_execution,
    inference_engine,
    cpu_set_request,
    cpu_set,
    model_n_jobs,
    model_thread_limit,
    bind,
    connect,
    model,
    runtime_candidate,
) = sys.argv[1:]
Path(path).write_text(
    json.dumps(
        {
            "schema_version": 2,
            "scope": "selected_runtime_" + runtime_candidate,
            "candidate_id": "A09",
            "runtime_candidate": runtime_candidate,
            "pid": int(pid),
            "process_start_ticks": int(process_start_ticks),
            "process_group_id": int(process_group_id),
            "python_executable": python_executable,
            "working_directory": working_directory,
            "command_sha256": command_sha256,
            "model_sha256": model_sha256,
            "service_source_sha256": service_source_sha256,
            "numpy_engine_source_sha256": numpy_engine_source_sha256 or None,
            "launcher_sha256": launcher_sha256,
            "prediction_execution": prediction_execution,
            "inference_engine": inference_engine,
            "cpu_set_request": cpu_set_request,
            "cpu_set": cpu_set,
            "model_n_jobs": int(model_n_jobs),
            "model_thread_limit": int(model_thread_limit),
            "bind": bind,
            "connect": connect,
            "model": model,
            "started_at": datetime.now(timezone.utc).isoformat(),
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
PY
    "${PYTHON_BIN}" - "${manifest_tmp}" <<'PY'
import os
import sys

with open(sys.argv[1], "rb") as handle:
    os.fsync(handle.fileno())
PY
    mv -f "${manifest_tmp}" "${RUNTIME_MANIFEST}"
    printf '%s\n' "${pid}" > "${pid_tmp}"
    "${PYTHON_BIN}" - "${pid_tmp}" <<'PY'
import os
import sys

with open(sys.argv[1], "rb") as handle:
    os.fsync(handle.fileno())
PY
    mv -f "${pid_tmp}" "${PID_FILE}"
    startup_complete=1
    trap - EXIT HUP INT TERM
    echo "started pid=${pid} log=${LOG_FILE}"
    exit 0
  fi
  sleep 1
done

echo "service did not become ready within 30 seconds" >&2
tail -n 50 "${LOG_FILE}" >&2
exit 4
