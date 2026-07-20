#!/usr/bin/env bash
set -euo pipefail

PROJECT=/opt/data/private/wangwt/ParkAttackKE/APT-Chain-Reconstruction
BASE=/opt/data/private/wangwt/ParkAttackKE/datasets/apt_public
CONDA=/opt/data/private/wangwt/anaconda3/bin/conda
ENVIRONMENT=py3.9
SOURCE="$PROJECT/source/EACR-APT"
LOG_DIR="$PROJECT/logs/public_datasets"
BATCH=first

usage() {
  printf 'Usage: %s [--batch first|second|third|web|all]\n' "${0##*/}"
}

if (($#)); then
  if [[ $1 == --batch && $# -eq 2 ]]; then
    BATCH=$2
  elif [[ $1 == --help || $1 == -h ]]; then
    usage
    exit 0
  else
    usage >&2
    exit 2
  fi
fi
if [[ $BATCH != first && $BATCH != second && $BATCH != third && $BATCH != web && $BATCH != all ]]; then
  printf 'Unknown batch: %s\n' "$BATCH" >&2
  exit 2
fi

mkdir -p "$BASE" "$LOG_DIR" "$PROJECT/manifests/public_datasets"
if [[ ! -e "$PROJECT/datasets/public" && ! -L "$PROJECT/datasets/public" ]]; then
  ln -s ../../datasets/apt_public "$PROJECT/datasets/public"
fi

is_complete() {
  local state=$1
  [[ -f "$state" ]] && grep -q '"complete": true' "$state"
}

launch() {
  local name=$1
  local state=$2
  shift 2
  local pid_file="$LOG_DIR/$name.pid"
  local log_file="$LOG_DIR/$name.log"

  if is_complete "$state"; then
    printf 'complete\t%s\n' "$name"
    return 0
  fi
  if [[ -s "$pid_file" ]] && kill -0 "$(<"$pid_file")" 2>/dev/null; then
    printf 'running\t%s\t%s\n' "$name" "$(<"$pid_file")"
    return 0
  fi
  # A collector may have been started manually during an interactive recovery.
  # Detect its dataset root before launching another writer for the same state.
  local root_marker=${state%/manifests/collection_state.json}
  local external_pid
  external_pid=$(pgrep -f -- "$root_marker" | head -n 1 || true)
  if [[ -n $external_pid ]]; then
    printf 'running_external\t%s\t%s\n' "$name" "$external_pid"
    return 0
  fi
  nohup "$@" >"$log_file" 2>&1 &
  printf '%s\n' "$!" >"$pid_file"
  printf 'started\t%s\t%s\n' "$name" "$!"
}

ZENODO="$SOURCE/scripts/collect_zenodo_dataset.py"
ZENODO_PARALLEL="$SOURCE/scripts/collect_zenodo_parallel.py"
DATAVERSE="$SOURCE/scripts/collect_dataverse_dataset.py"
DATAVERSE_PARALLEL="$SOURCE/scripts/collect_dataverse_parallel.py"
HTTP_MANIFEST="$SOURCE/scripts/collect_http_manifest.py"
S3_PREFIX="$SOURCE/scripts/collect_s3_prefix.py"
MENDELEY="$SOURCE/scripts/collect_mendeley_dataset.py"

if [[ $BATCH == first || $BATCH == all ]]; then
launch ait_lds_v2_1 "$BASE/ait_lds_v2_1/manifests/collection_state.json" \
  "$CONDA" run --no-capture-output -n "$ENVIRONMENT" python "$ZENODO" \
  --record 19483937 --root "$BASE/ait_lds_v2_1" --connections 2 --files \
  fox_no-pcaps.zip harrison_no-pcaps.zip shaw_no-pcaps.zip wardbeck_no-pcaps.zip \
  wheeler_no-pcaps.zip wilson_no-pcaps.zip russellmitchell_no-pcaps.zip santos_no-pcaps.zip

launch ait_nds "$BASE/ait_nds/manifests/collection_state.json" \
  "$CONDA" run --no-capture-output -n "$ENVIRONMENT" python "$ZENODO" \
  --record 6610489 --root "$BASE/ait_nds" --connections 2

launch ait_ads "$BASE/ait_ads/manifests/collection_state.json" \
  "$CONDA" run --no-capture-output -n "$ENVIRONMENT" python "$ZENODO" \
  --record 8263181 --root "$BASE/ait_ads" --connections 2

launch cam_lds "$BASE/cam_lds/manifests/collection_state.json" \
  "$CONDA" run --no-capture-output -n "$ENVIRONMENT" python "$ZENODO_PARALLEL" \
  --record 18861762 --root "$BASE/cam_lds" --connections 2 --jobs 4

launch ainception "$BASE/ainception/manifests/collection_state.json" \
  "$CONDA" run --no-capture-output -n "$ENVIRONMENT" python "$ZENODO_PARALLEL" \
  --record 17659656 --root "$BASE/ainception" --connections 2 --jobs 8

launch dedale_v2 "$BASE/dedale_v2/manifests/collection_state.json" \
  "$CONDA" run --no-capture-output -n "$ENVIRONMENT" python "$DATAVERSE_PARALLEL" \
  --base-url https://entrepot.recherche.data.gouv.fr \
  --persistent-id doi:10.57745/Y5JLDG --root "$BASE/dedale_v2" --connections 2 --jobs 4 \
  --file-ids 717871 717872 717873 717874 717875 717876 717877 717878 \
  717879 717880 717881 717882 717889 717890 717892 722195
fi

if [[ $BATCH == second || $BATCH == all ]]; then
  launch unraveled_processed "$BASE/unraveled_processed/manifests/collection_state.json" \
    "$CONDA" run --no-capture-output -n "$ENVIRONMENT" python "$S3_PREFIX" \
    --bucket dapt2021 --prefix processed/ --root "$BASE/unraveled_processed" \
    --expected-bytes 3736148033 --connections 2 --jobs 8

  launch pwnjutsu_json_reference "$BASE/pwnjutsu_json_reference/manifests/collection_state.json" \
    "$CONDA" run --no-capture-output -n "$ENVIRONMENT" python "$HTTP_MANIFEST" \
    --manifest "$SOURCE/configs/http_manifests/pwnjutsu_json_reference.json" \
    --root "$BASE/pwnjutsu_json_reference" --connections 2 --jobs 8

  launch saga_v2 "$BASE/saga_v2/manifests/collection_state.json" \
    "$CONDA" run --no-capture-output -n "$ENVIRONMENT" python "$HTTP_MANIFEST" \
    --manifest "$SOURCE/configs/http_manifests/saga_v2.json" \
    --root "$BASE/saga_v2" --connections 1 --jobs 3
fi

if [[ $BATCH == third || $BATCH == web || $BATCH == all ]]; then
  launch linux_apt_dataset_2024 "$BASE/linux_apt_dataset_2024/manifests/collection_state.json" \
    "$CONDA" run --no-capture-output -n "$ENVIRONMENT" python "$ZENODO_PARALLEL" \
    --record 10685642 --root "$BASE/linux_apt_dataset_2024" \
    --expected-files 18 --expected-bytes 208382833 --connections 2 --jobs 6

  launch apt_sandworm "$BASE/apt_sandworm/manifests/collection_state.json" \
    "$CONDA" run --no-capture-output -n "$ENVIRONMENT" python "$ZENODO_PARALLEL" \
    --record 16911636 --root "$BASE/apt_sandworm" \
    --expected-files 3 --expected-bytes 1816085762 --connections 4 --jobs 3

  launch windows_apt_2025_mendeley_v3 "$BASE/windows_apt_2025_mendeley_v3/manifests/collection_state.json" \
    "$CONDA" run --no-capture-output -n "$ENVIRONMENT" python "$MENDELEY" \
    --dataset-id b8fmtzvpy8 --version 3 --folder-id root \
    --root "$BASE/windows_apt_2025_mendeley_v3" \
    --expected-files 21 --expected-bytes 480856926 \
    --connections 2 --jobs 6
fi
