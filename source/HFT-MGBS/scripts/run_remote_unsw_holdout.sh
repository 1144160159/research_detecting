#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/HFT-MGBS}"
CODE_ROOT="${CODE_ROOT:-${PROJECT_ROOT}/source/HFT-MGBS}"
CONDA="${CONDA:-/opt/data/private/wangwt/anaconda3/bin/conda}"
CONDA_ENV="${CONDA_ENV:-py3.9}"
TRAINING_MANIFEST="${TRAINING_MANIFEST:-${CODE_ROOT}/configs/ustc_tfc2016_binary_quality.json}"
HOLDOUT_MANIFEST="${HOLDOUT_MANIFEST:-${CODE_ROOT}/configs/unsw_nb15_holdout.json}"
REPEATS="${REPEATS:-3}"
MAX_TRAIN_PACKETS="${MAX_TRAIN_PACKETS:-20000}"
MAX_TRAIN_FLOWS="${MAX_TRAIN_FLOWS:-2000}"
MAX_TEST_PACKETS="${MAX_TEST_PACKETS:-50000}"
MAX_TEST_FLOWS="${MAX_TEST_FLOWS:-5000}"
ESTIMATORS="${ESTIMATORS:-200}"
N_JOBS="${N_JOBS:-8}"
BATCH_SIZE="${BATCH_SIZE:-512}"
BUDGET_US="${BUDGET_US:-5000}"
SAFETY_RATIO="${SAFETY_RATIO:-0.75}"
RUN_TAG="${RUN_TAG:-formal}"
RUN_PREFIX="${RUN_PREFIX:-HFT_G6_unsw_holdout}"
INPUT_HASH_MANIFEST="${INPUT_HASH_MANIFEST:-}"
THRESHOLD_POLICY="${THRESHOLD_POLICY:-fixed}"
CALIBRATION_GROUPS="${CALIBRATION_GROUPS:-}"
CALIBRATION_ATTACK_RECALL_FLOOR="${CALIBRATION_ATTACK_RECALL_FLOOR:-0}"
FEATURE_PROFILE="${FEATURE_PROFILE:-raw}"
CLASSIFIER="${CLASSIFIER:-extra_trees}"
ADAPTATION_POLICY="${ADAPTATION_POLICY:-none}"
ADAPTATION_GROUPS="${ADAPTATION_GROUPS:-}"
ADAPTATION_WEIGHT_MULTIPLIER="${ADAPTATION_WEIGHT_MULTIPLIER:-1.0}"
seeds=(7 11 19)

if ! [[ "${REPEATS}" =~ ^[1-3]$ ]]; then
  echo "REPEATS must be 1, 2, or 3" >&2
  exit 2
fi

RUN_ID="${RUN_PREFIX}_${RUN_TAG}_$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${PROJECT_ROOT}/runs/${RUN_ID}"
RESULT_DIR="${PROJECT_ROOT}/results/${RUN_ID}"
HASH_MANIFEST="${RUN_DIR}/input_sha256.json"
mkdir -p "${RUN_DIR}" "${RESULT_DIR}"

cd "${CODE_ROOT}"
"${CONDA}" run -n "${CONDA_ENV}" python scripts/check_local_policy.py
"${CONDA}" run -n "${CONDA_ENV}" python -m unittest discover -s tests -v \
  > "${RUN_DIR}/unit_tests.txt" 2>&1
if [[ -n "${INPUT_HASH_MANIFEST}" ]]; then
  if [[ ! -f "${INPUT_HASH_MANIFEST}" ]]; then
    echo "INPUT_HASH_MANIFEST is not a file: ${INPUT_HASH_MANIFEST}" >&2
    exit 3
  fi
  cp "${INPUT_HASH_MANIFEST}" "${HASH_MANIFEST}"
  echo "reused=${INPUT_HASH_MANIFEST}" > "${RUN_DIR}/input_hash_stdout.txt"
else
  PYTHONPATH=. "${CONDA}" run -n "${CONDA_ENV}" \
    python scripts/freeze_input_manifest.py \
    "${TRAINING_MANIFEST}" "${HOLDOUT_MANIFEST}" \
    --output "${HASH_MANIFEST}" > "${RUN_DIR}/input_hash_stdout.json"
fi

{
  echo "run_id=${RUN_ID}"
  echo "training_manifest=${TRAINING_MANIFEST}"
  echo "holdout_manifest=${HOLDOUT_MANIFEST}"
  echo "input_hash_manifest=${HASH_MANIFEST}"
  echo "input_hash_manifest_sha256=$(sha256sum "${HASH_MANIFEST}" | awk '{print $1}')"
  echo "repeats=${REPEATS}"
  echo "max_train_packets=${MAX_TRAIN_PACKETS}"
  echo "max_train_flows=${MAX_TRAIN_FLOWS}"
  echo "max_test_packets=${MAX_TEST_PACKETS}"
  echo "max_test_flows=${MAX_TEST_FLOWS}"
  echo "batch_size=${BATCH_SIZE}"
  echo "budget_us=${BUDGET_US}"
  echo "execution_budget_safety_ratio=${SAFETY_RATIO}"
  echo "threshold_policy=${THRESHOLD_POLICY}"
  echo "calibration_groups=${CALIBRATION_GROUPS}"
  echo "calibration_attack_recall_floor=${CALIBRATION_ATTACK_RECALL_FLOOR}"
  echo "feature_profile=${FEATURE_PROFILE}"
  echo "classifier=${CLASSIFIER}"
  echo "adaptation_policy=${ADAPTATION_POLICY}"
  echo "adaptation_groups=${ADAPTATION_GROUPS}"
  echo "adaptation_weight_multiplier=${ADAPTATION_WEIGHT_MULTIPLIER}"
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "${RUN_DIR}/manifest.txt"

calibration_args=()
if [[ -n "${CALIBRATION_GROUPS}" ]]; then
  IFS=', ' read -r -a calibration_group_names <<< "${CALIBRATION_GROUPS}"
  calibration_args+=(--calibration-groups "${calibration_group_names[@]}")
fi
adaptation_args=()
if [[ -n "${ADAPTATION_GROUPS}" ]]; then
  IFS=', ' read -r -a adaptation_group_names <<< "${ADAPTATION_GROUPS}"
  adaptation_args+=(--adaptation-groups "${adaptation_group_names[@]}")
fi

for mode in normal fallback; do
  extra=()
  if [[ "${mode}" == "fallback" ]]; then
    extra+=(--disable-deep)
  fi
  for repeat in $(seq 1 "${REPEATS}"); do
    seed="${seeds[$((repeat - 1))]}"
    PYTHONPATH=. "${CONDA}" run -n "${CONDA_ENV}" \
      python scripts/evaluate_unsw_independent_holdout.py \
      "${TRAINING_MANIFEST}" "${HOLDOUT_MANIFEST}" \
      --batch-size "${BATCH_SIZE}" \
      --budget-us "${BUDGET_US}" \
      --execution-budget-safety-ratio "${SAFETY_RATIO}" \
      --max-train-packets-per-capture "${MAX_TRAIN_PACKETS}" \
      --max-train-flows-per-capture "${MAX_TRAIN_FLOWS}" \
      --max-test-packets-per-capture "${MAX_TEST_PACKETS}" \
      --max-test-flows-per-capture "${MAX_TEST_FLOWS}" \
      --estimators "${ESTIMATORS}" \
      --n-jobs "${N_JOBS}" \
      --seeds "${seed}" \
      --summary-only \
      --input-hash-manifest "${HASH_MANIFEST}" \
      --threshold-policy "${THRESHOLD_POLICY}" \
      --calibration-attack-recall-floor \
        "${CALIBRATION_ATTACK_RECALL_FLOOR}" \
      --feature-profile "${FEATURE_PROFILE}" \
      --classifier "${CLASSIFIER}" \
      "${calibration_args[@]}" \
      --adaptation-policy "${ADAPTATION_POLICY}" \
      --adaptation-weight-multiplier \
        "${ADAPTATION_WEIGHT_MULTIPLIER}" \
      "${adaptation_args[@]}" \
      "${extra[@]}" > "${RESULT_DIR}/${mode}_repeat${repeat}.json"
  done
done

PYTHONPATH=. "${CONDA}" run -n "${CONDA_ENV}" \
  python scripts/summarize_unsw_holdout.py "${RESULT_DIR}" \
  --minimum-repeats "${REPEATS}" > "${RESULT_DIR}/summary.json"
find . -type f -not -path './__pycache__/*' -not -name '*.pyc' -print0 \
  | sort -z | xargs -0 sha256sum > "${RUN_DIR}/code_sha256.txt"
find "${RESULT_DIR}" -type f -print0 | sort -z | xargs -0 sha256sum \
  > "${RUN_DIR}/result_sha256.txt"
{
  echo "status=complete"
  echo "ended_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "result_dir=${RESULT_DIR}"
  echo "result_count=$(find "${RESULT_DIR}" -type f -name '*_repeat*.json' | wc -l)"
} >> "${RUN_DIR}/manifest.txt"

echo "Completed ${RUN_ID}; results: ${RESULT_DIR}"
