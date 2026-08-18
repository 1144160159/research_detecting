#!/usr/bin/env bash
set -euo pipefail

RELEASE_ROOT="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v2_20260801_r6"
OUTPUT_ROOT="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v2"
CONTROL_ROOT="${OUTPUT_ROOT}/_control"
PYTHON="/opt/data/private/wangwt/anaconda3/bin/conda run -n py3.9 python"
CATALOG="${RELEASE_ROOT}/configs/unified_multimodal_v1.datasets.json"
SCHEMA="${RELEASE_ROOT}/configs/unified_multimodal_v2.schema.json"
SOURCE_MANIFEST="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v1/_control/source_manifest.json"
LOG="${CONTROL_ROOT}/preprocessing.log"
RESOURCE_LOG="${CONTROL_ROOT}/resource_samples.log"
MIN_FREE_KIB=$((500 * 1024 * 1024))
LOCK_DIR="${CONTROL_ROOT}/preprocessing.lockdir"
GLOBAL_PAUSE_FILE="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/PAUSED_PREPROCESSING"
USER_MEMORY_BUDGET_BYTES=$((200 * 1024 * 1024 * 1024))
USER_CPU_BUDGET=32
TARGET_CPU_PERCENT=80

if [[ -e "${GLOBAL_PAUSE_FILE}" ]]; then
  echo "preprocessing is paused by ${GLOBAL_PAUSE_FILE}" >&2
  exit 78
fi

CGROUP_MEMORY_LIMIT_BYTES="${USER_MEMORY_BUDGET_BYTES}"
if [[ -r /sys/fs/cgroup/memory.max ]]; then
  VALUE=$(cat /sys/fs/cgroup/memory.max)
  if [[ "${VALUE}" != "max" ]]; then
    CGROUP_MEMORY_LIMIT_BYTES="${VALUE}"
  fi
elif [[ -r /sys/fs/cgroup/memory/memory.limit_in_bytes ]]; then
  CGROUP_MEMORY_LIMIT_BYTES=$(cat /sys/fs/cgroup/memory/memory.limit_in_bytes)
fi
if (( CGROUP_MEMORY_LIMIT_BYTES < USER_MEMORY_BUDGET_BYTES )); then
  EFFECTIVE_MEMORY_BUDGET_BYTES="${CGROUP_MEMORY_LIMIT_BYTES}"
else
  EFFECTIVE_MEMORY_BUDGET_BYTES="${USER_MEMORY_BUDGET_BYTES}"
fi

if (( EFFECTIVE_MEMORY_BUDGET_BYTES <= 40 * 1024 * 1024 * 1024 )); then
  PARSER_PROCESSES=16
  MAXIMUM_ACTIVE_FLOWS=6000
  MAX_ANON_RSS_BYTES=$((22 * 1024 * 1024 * 1024))
elif (( EFFECTIVE_MEMORY_BUDGET_BYTES <= 96 * 1024 * 1024 * 1024 )); then
  PARSER_PROCESSES=24
  MAXIMUM_ACTIVE_FLOWS=12000
  MAX_ANON_RSS_BYTES=$((EFFECTIVE_MEMORY_BUDGET_BYTES * 70 / 100))
else
  PARSER_PROCESSES=$(((USER_CPU_BUDGET * TARGET_CPU_PERCENT + 99) / 100))
  MAXIMUM_ACTIVE_FLOWS=25000
  MAX_ANON_RSS_BYTES=$((EFFECTIVE_MEMORY_BUDGET_BYTES * 70 / 100))
fi

cgroup_anon_rss_bytes() {
  if [[ -r /sys/fs/cgroup/memory.stat ]]; then
    awk '$1 == "anon" {print $2}' /sys/fs/cgroup/memory.stat
  elif [[ -r /sys/fs/cgroup/memory/memory.stat ]]; then
    awk '$1 == "total_rss" {print $2}' /sys/fs/cgroup/memory/memory.stat
  else
    awk '/^AnonPages:/ {print $2 * 1024}' /proc/meminfo
  fi
}

mkdir -p "${CONTROL_ROOT}"
if ! mkdir "${LOCK_DIR}" 2>/dev/null; then
  echo "another unified preprocessing coordinator holds ${LOCK_DIR}" >&2
  exit 73
fi
trap 'rmdir "${LOCK_DIR}" 2>/dev/null || true' EXIT

exec >>"${LOG}" 2>&1
echo "START $(date --iso-8601=seconds)"
echo "HOST $(hostname)"
echo "NPROC $(nproc)"
echo "USER_CPU_BUDGET ${USER_CPU_BUDGET}"
echo "TARGET_CPU_PERCENT ${TARGET_CPU_PERCENT}"
echo "USER_MEMORY_BUDGET_BYTES ${USER_MEMORY_BUDGET_BYTES}"
echo "CGROUP_MEMORY_LIMIT_BYTES ${CGROUP_MEMORY_LIMIT_BYTES}"
echo "EFFECTIVE_MEMORY_BUDGET_BYTES ${EFFECTIVE_MEMORY_BUDGET_BYTES}"
echo "MAX_ANON_RSS_BYTES ${MAX_ANON_RSS_BYTES}"
echo "PARSER_PROCESSES ${PARSER_PROCESSES}"
echo "MAXIMUM_ACTIVE_FLOWS ${MAXIMUM_ACTIVE_FLOWS}"
df -h "${OUTPUT_ROOT}"

if [[ ! -f "${SOURCE_MANIFEST}" ]]; then
  ${PYTHON} "${RELEASE_ROOT}/caeos_unified_dataset.py" \
    --catalog "${CATALOG}" \
    --output "${SOURCE_MANIFEST}" \
    --io-threads 16
fi

setsid ${PYTHON} "${RELEASE_ROOT}/prepare_caeos_unified_multimodal_csv.py" \
  --catalog "${CATALOG}" \
  --schema "${SCHEMA}" \
  --source-manifest "${SOURCE_MANIFEST}" \
  --output-root "${OUTPUT_ROOT}" \
  --parser-processes "${PARSER_PROCESSES}" \
  --io-threads 16 \
  --maximum-active-flows "${MAXIMUM_ACTIVE_FLOWS}" \
  --dataset ciciot2023 \
  --dataset ciciot2022 \
  --dataset edge_iiotset \
  --dataset cicids2017 \
  --dataset cic_bot_iot \
  --dataset cic_ton_iot \
  --dataset cicddos2019 \
  --dataset dohbrw2020 \
  --dataset iscx_tor_nontor_2017 \
  --dataset iscx_vpn_nonvpn_2016 \
  --dataset parrot2025 \
  --dataset crossplatform_android_ios &
WORK_PID=$!
echo "WORK_PID ${WORK_PID}"

while kill -0 "${WORK_PID}" 2>/dev/null; do
  AVAILABLE_KIB=$(df --output=avail "${OUTPUT_ROOT}" | tail -n 1 | tr -d ' ')
  ANON_RSS_BYTES=$(cgroup_anon_rss_bytes)
  if (( AVAILABLE_KIB < MIN_FREE_KIB )); then
    echo "LOW_SPACE available_kib=${AVAILABLE_KIB} threshold_kib=${MIN_FREE_KIB}"
    kill -TERM -- "-${WORK_PID}"
    wait "${WORK_PID}" || true
    exit 75
  fi
  if (( ANON_RSS_BYTES > MAX_ANON_RSS_BYTES )); then
    echo "MEMORY_BUDGET_EXCEEDED anon_rss_bytes=${ANON_RSS_BYTES} threshold_bytes=${MAX_ANON_RSS_BYTES}"
    kill -TERM -- "-${WORK_PID}"
    wait "${WORK_PID}" || true
    exit 76
  fi
  {
    echo "SAMPLE $(date --iso-8601=seconds)"
    echo "AVAILABLE_KIB ${AVAILABLE_KIB}"
    echo "ANON_RSS_BYTES ${ANON_RSS_BYTES}"
    top -b -n 1 | head -n 5
    ps -o pid,ppid,pcpu,pmem,rss,etime,stat,cmd -p "${WORK_PID}"
  } >>"${RESOURCE_LOG}" 2>&1
  sleep 30
done

wait "${WORK_PID}"
${PYTHON} -c "import json,pathlib; p=pathlib.Path('${OUTPUT_ROOT}/completion.json'); d=json.loads(p.read_text()); assert d['all_csv_materialized']; print(d['completion_sha256'])"
touch "${OUTPUT_ROOT}/ALL_CSV_MATERIALIZED"
echo "COMPLETE $(date --iso-8601=seconds)"
