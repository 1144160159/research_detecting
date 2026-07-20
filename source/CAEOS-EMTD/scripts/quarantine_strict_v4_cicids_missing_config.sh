#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v4-20260717}"
SOURCE="$PROJECT_ROOT/runs/strict_v4_full103_pairwise_caeos_seed7/cicids2017"
DESTINATION="${DESTINATION:-$PROJECT_ROOT/results/strict_v4_full103_seed7/failed_attempts_cicids_missing_config}"
EXPECTED_COUNT="${EXPECTED_COUNT:-14}"
ALLOW_METRICS="${ALLOW_METRICS:-0}"

project_real="$(realpath -e "$PROJECT_ROOT")"
source_real="$(realpath -e "$SOURCE")"
case "$source_real" in
  "$project_real"/runs/strict_v4_full103_pairwise_caeos_seed7/cicids2017) ;;
  *) echo "refusing unexpected source path: $source_real" >&2; exit 1 ;;
esac
[[ ! -e "$DESTINATION" ]] || {
  echo "quarantine destination already exists: $DESTINATION" >&2
  exit 1
}
mapfile -t directories < <(find "$source_real" -mindepth 1 -maxdepth 1 -type d | sort)
[[ "${#directories[@]}" -eq "$EXPECTED_COUNT" ]] || {
  echo "expected $EXPECTED_COUNT failed directories, found ${#directories[@]}" >&2
  exit 1
}
for directory in "${directories[@]}"; do
  directory_real="$(realpath -e "$directory")"
  case "$directory_real" in
    "$source_real"/*) ;;
    *) echo "refusing path outside source: $directory_real" >&2; exit 1 ;;
  esac
  [[ -f "$directory_real/run.log" && -f "$directory_real/provenance.json" ]]
  if [[ "$ALLOW_METRICS" != "1" ]]; then
    [[ ! -e "$directory_real/metrics.json" ]]
  fi
done
mkdir -p "$DESTINATION"
for directory in "${directories[@]}"; do
  mv -- "$directory" "$DESTINATION/"
done
[[ "$(find "$source_real" -mindepth 1 -maxdepth 1 | wc -l)" -eq 0 ]]
printf 'quarantined=%s source=%s destination=%s\n' \
  "${#directories[@]}" "$source_real" "$DESTINATION"
