#!/usr/bin/env bash
set -euo pipefail

RELEASE_ROOT="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v4_20260802_r13"
OUTPUT_ROOT="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v4"
CONTROL_ROOT="${OUTPUT_ROOT}/_control"
PYTHON="/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python"
CATALOG="${RELEASE_ROOT}/configs/unified_multimodal_v1.datasets.json"
SCHEMA="${RELEASE_ROOT}/configs/unified_multimodal_v4.schema.json"
SOURCE_MANIFEST="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v1/_control/source_manifest.json"
LOG="${CONTROL_ROOT}/preprocessing.log"
RESOURCE_LOG="${CONTROL_ROOT}/resource_samples.log"
MIN_FREE_KIB=$((500 * 1024 * 1024))
LOCK_DIR="${CONTROL_ROOT}/preprocessing.lockdir"
GLOBAL_PAUSE_FILE="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/PAUSED_PREPROCESSING"
USER_MEMORY_BUDGET_BYTES=$((200 * 1024 * 1024 * 1024))
REQUESTED_MAX_MEMORY_CURRENT_BYTES=$((190 * 1024 * 1024 * 1024))
REQUESTED_CONTROLLED_STOP_MEMORY_BYTES=$((180 * 1024 * 1024 * 1024))
MAX_TSHARK_RSS_KIB=$((32 * 1024 * 1024))
TSHARK_SESSION_RESET_PACKETS=0
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
  PARSER_PROCESSES=2
  MAXIMUM_ACTIVE_FLOWS=25000
elif (( EFFECTIVE_MEMORY_BUDGET_BYTES <= 96 * 1024 * 1024 * 1024 )); then
  PARSER_PROCESSES=3
  MAXIMUM_ACTIVE_FLOWS=25000
else
  # Four parser/TShark pairs preserve every selected TShark field while
  # bounding the multiplicative cost of long-lived protocol session state.
  PARSER_PROCESSES=4
  MAXIMUM_ACTIVE_FLOWS=25000
fi
CGROUP_SAFE_CONTROLLED_STOP_MEMORY_BYTES=$((EFFECTIVE_MEMORY_BUDGET_BYTES * 90 / 100))
if (( REQUESTED_CONTROLLED_STOP_MEMORY_BYTES < CGROUP_SAFE_CONTROLLED_STOP_MEMORY_BYTES )); then
  CONTROLLED_STOP_MEMORY_BYTES="${REQUESTED_CONTROLLED_STOP_MEMORY_BYTES}"
else
  CONTROLLED_STOP_MEMORY_BYTES="${CGROUP_SAFE_CONTROLLED_STOP_MEMORY_BYTES}"
fi

CGROUP_SAFE_MAX_MEMORY_CURRENT_BYTES=$((EFFECTIVE_MEMORY_BUDGET_BYTES * 95 / 100))
if (( REQUESTED_MAX_MEMORY_CURRENT_BYTES < CGROUP_SAFE_MAX_MEMORY_CURRENT_BYTES )); then
  MAX_MEMORY_CURRENT_BYTES="${REQUESTED_MAX_MEMORY_CURRENT_BYTES}"
else
  MAX_MEMORY_CURRENT_BYTES="${CGROUP_SAFE_MAX_MEMORY_CURRENT_BYTES}"
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

cgroup_memory_current_bytes() {
  if [[ -r /sys/fs/cgroup/memory.current ]]; then
    cat /sys/fs/cgroup/memory.current
  elif [[ -r /sys/fs/cgroup/memory/memory.usage_in_bytes ]]; then
    cat /sys/fs/cgroup/memory/memory.usage_in_bytes
  else
    awk '/^MemTotal:/ {total=$2} /^MemAvailable:/ {available=$2} END {print (total-available)*1024}' /proc/meminfo
  fi
}

process_group_tshark_max_rss_kib() {
  ps -eo pgid=,comm=,rss= | awk -v pgid="${WORK_PID}" '
    $1 == pgid && $2 == "tshark" && $3 > maximum {maximum=$3}
    END {print maximum+0}
  '
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
echo "REQUESTED_MAX_MEMORY_CURRENT_BYTES ${REQUESTED_MAX_MEMORY_CURRENT_BYTES}"
echo "MAX_MEMORY_CURRENT_BYTES ${MAX_MEMORY_CURRENT_BYTES}"
echo "CONTROLLED_STOP_MEMORY_BYTES ${CONTROLLED_STOP_MEMORY_BYTES}"
echo "MAX_TSHARK_RSS_KIB ${MAX_TSHARK_RSS_KIB}"
echo "TSHARK_SESSION_RESET_PACKETS ${TSHARK_SESSION_RESET_PACKETS}"
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
  --packet-decoder tshark \
  --tshark-binary /usr/bin/tshark \
  --tshark-session-reset-packets "${TSHARK_SESSION_RESET_PACKETS}" \
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
  MEMORY_CURRENT_BYTES=$(cgroup_memory_current_bytes)
  TSHARK_MAX_RSS_KIB=$(process_group_tshark_max_rss_kib)
  if (( AVAILABLE_KIB < MIN_FREE_KIB )); then
    echo "LOW_SPACE available_kib=${AVAILABLE_KIB} threshold_kib=${MIN_FREE_KIB}"
    kill -TERM -- "-${WORK_PID}"
    wait "${WORK_PID}" || true
    exit 75
  fi
  if (( MEMORY_CURRENT_BYTES > MAX_MEMORY_CURRENT_BYTES )); then
    echo "MEMORY_CURRENT_HARD_LIMIT_EXCEEDED memory_current_bytes=${MEMORY_CURRENT_BYTES} threshold_bytes=${MAX_MEMORY_CURRENT_BYTES}"
    kill -TERM -- "-${WORK_PID}"
    wait "${WORK_PID}" || true
    exit 76
  fi
  if (( MEMORY_CURRENT_BYTES > CONTROLLED_STOP_MEMORY_BYTES )); then
    echo "MEMORY_CURRENT_CONTROLLED_STOP memory_current_bytes=${MEMORY_CURRENT_BYTES} threshold_bytes=${CONTROLLED_STOP_MEMORY_BYTES}"
    kill -TERM -- "-${WORK_PID}"
    wait "${WORK_PID}" || true
    exit 78
  fi
  if (( TSHARK_MAX_RSS_KIB > MAX_TSHARK_RSS_KIB )); then
    echo "TSHARK_RSS_LIMIT_EXCEEDED max_rss_kib=${TSHARK_MAX_RSS_KIB} threshold_kib=${MAX_TSHARK_RSS_KIB}"
    kill -TERM -- "-${WORK_PID}"
    wait "${WORK_PID}" || true
    exit 77
  fi
  {
    echo "SAMPLE $(date --iso-8601=seconds)"
    echo "AVAILABLE_KIB ${AVAILABLE_KIB}"
    echo "ANON_RSS_BYTES ${ANON_RSS_BYTES}"
    echo "MEMORY_CURRENT_BYTES ${MEMORY_CURRENT_BYTES}"
    echo "TSHARK_MAX_RSS_KIB ${TSHARK_MAX_RSS_KIB}"
    top -b -n 1 | head -n 5
    ps -o pid,ppid,pcpu,pmem,rss,etime,stat,cmd -p "${WORK_PID}"
  } >>"${RESOURCE_LOG}" 2>&1
  sleep 10
done

wait "${WORK_PID}"
${PYTHON} -c "import json,pathlib; p=pathlib.Path('${OUTPUT_ROOT}/completion.json'); d=json.loads(p.read_text()); assert d['all_csv_materialized']; print(d['completion_sha256'])"
touch "${OUTPUT_ROOT}/ALL_CSV_MATERIALIZED"
echo "COMPLETE $(date --iso-8601=seconds)"
