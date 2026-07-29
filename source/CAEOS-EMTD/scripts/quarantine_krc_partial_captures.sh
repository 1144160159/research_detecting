#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 3 ]]; then
  echo "usage: $0 RUN_ROOT EXPECTED_COUNT QUARANTINE_TAG" >&2
  exit 2
fi

run_root="$(readlink -f "$1")"
expected_count="$2"
quarantine_tag="$3"
capture_root="${run_root}/captures"
quarantine_root="${run_root}/quarantine/${quarantine_tag}"

[[ -d "${capture_root}" ]]
[[ "${expected_count}" =~ ^[0-9]+$ ]]
[[ "${quarantine_tag}" =~ ^[A-Za-z0-9._-]+$ ]]
[[ ! -e "${quarantine_root}" ]]

mapfile -t partial_dirs < <(
  cd "${capture_root}"
  comm -23 \
    <(find . -name capture.log -printf '%h\n' | sort) \
    <(find . -name capture_manifest.json -printf '%h\n' | sort)
)

if [[ "${#partial_dirs[@]}" -ne "${expected_count}" ]]; then
  echo "partial capture count mismatch: expected=${expected_count} actual=${#partial_dirs[@]}" >&2
  exit 1
fi

for rel in "${partial_dirs[@]}"; do
  source_dir="$(readlink -f "${capture_root}/${rel#./}")"
  [[ "${source_dir}" == "${capture_root}/"* ]]
  [[ -f "${source_dir}/capture.log" ]]
  [[ ! -e "${source_dir}/capture_manifest.json" ]]
  [[ "$(find "${source_dir}" -mindepth 1 -maxdepth 1 -type f | wc -l)" -eq 1 ]]
  grep -Fq "ImportError: cannot import name 'PUG_RISK_NAME'" "${source_dir}/capture.log"
done

mkdir -p "${quarantine_root}"
printf '%s\n' "${partial_dirs[@]}" > "${quarantine_root}/partial_dirs.txt"
printf 'relative_path\tsize_bytes\tsha256\n' > "${quarantine_root}/capture_logs.tsv"
for rel in "${partial_dirs[@]}"; do
  log_path="${capture_root}/${rel#./}/capture.log"
  printf '%s\t%s\t%s\n' \
    "${rel}" \
    "$(stat -c '%s' "${log_path}")" \
    "$(sha256sum "${log_path}" | awk '{print $1}')" \
    >> "${quarantine_root}/capture_logs.tsv"
done

for rel in "${partial_dirs[@]}"; do
  destination="${quarantine_root}/${rel#./}"
  mkdir -p "$(dirname "${destination}")"
  mv -- "${capture_root}/${rel#./}" "${destination}"
done

remaining_partial="$(
  cd "${capture_root}"
  comm -23 \
    <(find . -name capture.log -printf '%h\n' | sort) \
    <(find . -name capture_manifest.json -printf '%h\n' | sort) \
    | wc -l
)"
quarantined_logs="$(find "${quarantine_root}" -name capture.log | wc -l)"
complete_captures="$(find "${capture_root}" -name capture_manifest.json | wc -l)"

[[ "${remaining_partial}" -eq 0 ]]
[[ "${quarantined_logs}" -eq "${expected_count}" ]]

sha256sum \
  "${quarantine_root}/partial_dirs.txt" \
  "${quarantine_root}/capture_logs.tsv" \
  > "${quarantine_root}/manifest.sha256"

printf 'quarantine_root=%s\n' "${quarantine_root}"
printf 'quarantined_dirs=%s\n' "${quarantined_logs}"
printf 'remaining_partial=%s\n' "${remaining_partial}"
printf 'complete_captures=%s\n' "${complete_captures}"
cat "${quarantine_root}/manifest.sha256"
