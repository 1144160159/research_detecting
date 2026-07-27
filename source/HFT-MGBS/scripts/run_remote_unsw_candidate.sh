#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -lt 3 || "$#" -gt 5 ]]; then
  echo "usage: $0 FEATURE_PROFILE ATTACK_RECALL_FLOOR RUN_TAG [HOLDOUT_MANIFEST [INPUT_HASH_MANIFEST]]" >&2
  exit 2
fi

feature_profile="$1"
attack_recall_floor="$2"
run_tag="$3"
default_holdout_manifest=\
"/opt/data/private/wangwt/ParkAttackKE/HFT-MGBS/source/HFT-MGBS/"\
"configs/unsw_nb15_holdout.json"
default_input_hash_manifest=\
"/opt/data/private/wangwt/ParkAttackKE/HFT-MGBS/runs/"\
"HFT_G6_unsw_holdout_key_unconditional_safety050_formal_"\
"20260724T025042Z/input_sha256.json"
holdout_manifest="${4:-${default_holdout_manifest}}"

case "${feature_profile}" in
  raw|invariant_v1|invariant_no_ports_v1) ;;
  *)
    echo "unsupported feature profile: ${feature_profile}" >&2
    exit 3
    ;;
esac

if ! [[ "${attack_recall_floor}" =~ ^(0(\.[0-9]+)?|1(\.0+)?)$ ]]; then
  echo "invalid attack recall floor: ${attack_recall_floor}" >&2
  exit 4
fi

case "${run_tag}" in
  *[!A-Za-z0-9_.-]*|"")
    echo "invalid run tag: ${run_tag}" >&2
    exit 5
    ;;
esac

export RUN_PREFIX="${RUN_PREFIX:-HFT_G11_unsw_temporal_calibrated}"
export RUN_TAG="${run_tag}"
export REPEATS=3
export BATCH_SIZE=512
export BUDGET_US=5000
export SAFETY_RATIO=0.50
if [[ "$#" -ge 5 ]]; then
  export INPUT_HASH_MANIFEST="$5"
elif [[ "$#" -eq 4 ]]; then
  export INPUT_HASH_MANIFEST=""
else
  export INPUT_HASH_MANIFEST="${default_input_hash_manifest}"
fi
export HOLDOUT_MANIFEST="${holdout_manifest}"
export THRESHOLD_POLICY="calibration_macro_f1"
default_calibration_groups=\
"unsw_2015-01-22_shard1,unsw_2015-01-22_shard2,"\
"unsw_2015-01-22_shard3"
export CALIBRATION_GROUPS="${CALIBRATION_GROUPS:-${default_calibration_groups}}"
export CALIBRATION_ATTACK_RECALL_FLOOR="${attack_recall_floor}"
export FEATURE_PROFILE="${feature_profile}"
export CLASSIFIER="extra_trees"
export ADAPTATION_POLICY="${ADAPTATION_POLICY:-none}"
export ADAPTATION_GROUPS="${ADAPTATION_GROUPS:-}"
export ADAPTATION_WEIGHT_MULTIPLIER="${ADAPTATION_WEIGHT_MULTIPLIER:-1.0}"

exec bash "$(dirname "$0")/run_remote_unsw_holdout.sh"
