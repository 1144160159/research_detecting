#!/usr/bin/env bash
# Restore the exact USTC-TFC2016 PCAP paths required by the bounded A01--A10
# campaign.  Data stays on the GPU host; this script records source provenance
# and never treats a partial download or an extracted-but-unsealed file as done.

set -euo pipefail

readonly TARGET="/opt/data/private/wangwt/ParkAttackKE/datasets/USTC-TFC2016"
readonly REPOSITORY="https://github.com/davidyslu/USTC-TFC2016"
readonly COMMIT="4bc9683b996f582c3843815b68da8e4dce9c7e1e"
readonly TREE="fba77dcee81c1a6046eaf2f4de64c13ed4a3a1f8"
readonly RAW_ROOT="https://raw.githubusercontent.com/davidyslu/USTC-TFC2016/${COMMIT}"
readonly LOCK="/tmp/hft-ustc-tfc2016-restore.lock"

for command_name in curl 7z git sha256sum python3 capinfos flock find stat; do
  command -v "${command_name}" >/dev/null 2>&1 || {
    echo "missing required command: ${command_name}" >&2
    exit 20
  }
done

exec 9>"${LOCK}"
flock -n 9 || {
  echo "another USTC-TFC2016 restore owns ${LOCK}" >&2
  exit 21
}

umask 022
mkdir -p "${TARGET}/Benign" "${TARGET}/Malware" \
  "${TARGET}/_source_archives/Benign" \
  "${TARGET}/_source_archives/Malware" "${TARGET}/_control"

work_dir="$(mktemp -d "${TARGET}/.restore.XXXXXX")"
cleanup() {
  rm -rf -- "${work_dir}"
}
trap cleanup EXIT HUP INT TERM

source_table="${work_dir}/sources.tsv"
cat >"${source_table}" <<'EOF'
Benign/BitTorrent.pcap|7686388|b1f315db3165d188e590d5646d55ace3cefd9369|Benign/BitTorrent.pcap
Benign/Facetime.pcap|2519073|0ee8a2853b7d74bf11f743da2bc09eb3a1a46e0b|Benign/Facetime.pcap
Benign/FTP.pcap|63166447|ea2249b5ff25cbcd722d1fa6e51b09d779df7e70|Benign/FTP.pcap
Benign/Gmail.pcap|9497320|0195517b4ffcab454ffc5c75efe846b2e0ba2e0d|Benign/Gmail.pcap
Benign/MySQL.pcap|23450490|2786f8944e0a2de21ba5b580c8bb3994beb6da24|Benign/MySQL.pcap
Benign/Outlook.pcap|11711492|55974ca9245ea5c036ae97e0f97996320b9160b3|Benign/Outlook.pcap
Benign/Skype.pcap|4433982|b0aa82569ea6be06c810e0681d0a5537040a4f54|Benign/Skype.pcap
Benign/WorldOfWarcraft.pcap|15631895|e74376c46c8e2738b7acdfa16bea96a795ad5086|Benign/WorldOfWarcraft.pcap
Malware/Cridex.7z|9463176|42e3dc22d13710765b361be4e9be857b896201b6|Malware/Cridex.pcap
Malware/Geodo.7z|7254369|def47c79ad35a8112c6eb0fa2b4e02dea775ac3d|Malware/Geodo.pcap
Malware/Htbot.7z|34207966|2e23ca51d07f9d166212589cce6f1fdc22563299|Malware/Htbot.pcap
Malware/Miuref.pcap|17196739|070174d3486e74f04fccdc96504e6f4c60bf8333|Malware/Miuref.pcap
Malware/Neris.7z|27671368|b62d4ab875c6180711159c69d5047ba010bdc534|Malware/Neris.pcap
Malware/Nsis-ay.7z|38271959|a48559182e827dbbc8c6a77aa612e32976c93d75|Malware/Nsis-ay.pcap
Malware/Shifu.7z|4416510|10614ca107bc99f5130f8e9c4019e56e4ca15ea5|Malware/Shifu.pcap
Malware/Tinba.pcap|2680243|ec394babe99ccaef6c0fcfd60ca6ae57c154b5e9|Malware/Tinba.pcap
Malware/Virut.7z|31320373|6b1e1ee1a54111ab00cf45fd65b073d6391ba3fe|Malware/Virut.pcap
Malware/Zeus.pcap|14094482|80231c438781006535fff02e35fb518f41894bf5|Malware/Zeus.pcap
EOF

ledger="${work_dir}/restored.tsv"
: >"${ledger}"

verify_source_blob() {
  local path="$1" expected_size="$2" expected_blob="$3"
  [[ "$(stat -c %s -- "${path}")" == "${expected_size}" ]] || return 1
  [[ "$(git hash-object --no-filters -- "${path}")" == "${expected_blob}" ]]
}

while IFS='|' read -r source_path source_size source_blob output_path; do
  [[ -n "${source_path}" ]] || continue
  output="${TARGET}/${output_path}"
  if [[ "${source_path}" == *.7z ]]; then
    source_file="${TARGET}/_source_archives/${source_path}"
  else
    source_file="${output}"
  fi
  mkdir -p "$(dirname -- "${source_file}")" "$(dirname -- "${output}")"

  if [[ -L "${source_file}" ]]; then
    echo "refusing symlink source path: ${source_file}" >&2
    exit 22
  fi

  if ! [[ -f "${source_file}" ]] || \
     ! verify_source_blob "${source_file}" "${source_size}" "${source_blob}"; then
    if [[ -e "${source_file}" && ! -f "${source_file}" ]]; then
      echo "refusing non-regular source path: ${source_file}" >&2
      exit 22
    fi
    part="${source_file}.part"
    curl --proto '=https' --tlsv1.2 --fail --location \
      --retry 8 --retry-delay 2 --retry-all-errors --connect-timeout 30 \
      --continue-at - --output "${part}" "${RAW_ROOT}/${source_path}"
    verify_source_blob "${part}" "${source_size}" "${source_blob}" || {
      echo "source size or Git blob SHA-1 mismatch: ${source_path}" >&2
      exit 23
    }
    mv -f -- "${part}" "${source_file}"
  fi

  if [[ "${source_path}" == *.7z ]]; then
    extract_dir="${work_dir}/extract-${source_blob}"
    mkdir -p "${extract_dir}"
    7z x -bd -y -o"${extract_dir}" -- "${source_file}" >/dev/null
    mapfile -d '' extracted_pcaps < <(find "${extract_dir}" -type f -iname '*.pcap' -print0)
    [[ "${#extracted_pcaps[@]}" -eq 1 ]] || {
      echo "archive must contain exactly one PCAP: ${source_path}" >&2
      exit 24
    }
    candidate="${output}.tmp.$$"
    install -m 0444 -- "${extracted_pcaps[0]}" "${candidate}"
    if [[ -f "${output}" ]] && \
       [[ "$(sha256sum -- "${output}" | awk '{print $1}')" != \
          "$(sha256sum -- "${candidate}" | awk '{print $1}')" ]]; then
      echo "existing extracted PCAP differs: ${output}" >&2
      exit 25
    fi
    mv -f -- "${candidate}" "${output}"
  fi

  [[ -f "${output}" && ! -L "${output}" ]] || {
    echo "output is absent or a symlink: ${output}" >&2
    exit 26
  }
  capinfos -c -- "${output}" >/dev/null
  source_sha256="$(sha256sum -- "${source_file}" | awk '{print $1}')"
  output_sha256="$(sha256sum -- "${output}" | awk '{print $1}')"
  printf '%s|%s|%s|%s|%s|%s|%s\n' \
    "${source_path}" "${source_size}" "${source_blob}" "${source_sha256}" \
    "${output_path}" "$(stat -c %s -- "${output}")" "${output_sha256}" \
    >>"${ledger}"
done <"${source_table}"

[[ "$(wc -l <"${ledger}")" -eq 18 ]] || {
  echo "restored ledger is incomplete" >&2
  exit 27
}
[[ "$(find "${TARGET}" -type l -print -quit)" == "" ]] || {
  echo "symlinks are forbidden in the restored dataset" >&2
  exit 28
}
[[ "$(find "${TARGET}" -name '*.part' -print -quit)" == "" ]] || {
  echo "partial downloads remain" >&2
  exit 29
}

manifest_tmp="${TARGET}/_control/source_manifest_v1.json.tmp.$$"
python3 - "${ledger}" "${manifest_tmp}" "${REPOSITORY}" "${COMMIT}" "${TREE}" <<'PY'
import datetime
import hashlib
import json
import pathlib
import sys

ledger, output, repository, commit, tree = sys.argv[1:]
entries = []
for line in pathlib.Path(ledger).read_text(encoding="utf-8").splitlines():
    source, source_size, blob, source_sha, target, target_size, target_sha = line.split("|")
    entries.append({
        "source_path": source,
        "source_size_bytes": int(source_size),
        "source_git_blob_sha1": blob,
        "source_sha256": source_sha,
        "target_path": target,
        "target_size_bytes": int(target_size),
        "target_sha256": target_sha,
    })
payload = {
    "schema_version": 1,
    "scope": "hft_mgbs_ustc_tfc2016_campaign_input_restore",
    "source_repository": repository,
    "source_commit": commit,
    "source_tree": tree,
    "created_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "entry_count": len(entries),
    "entries": entries,
}
pathlib.Path(output).write_text(
    json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PY
mv -f -- "${manifest_tmp}" "${TARGET}/_control/source_manifest_v1.json"

(
  cd "${TARGET}"
  awk -F'|' '{print $7 "  " $5}' "${ledger}" | sort \
    >"_control/input_pcaps.sha256.tmp"
  mv -f -- "_control/input_pcaps.sha256.tmp" "_control/input_pcaps.sha256"
  sha256sum -c "_control/input_pcaps.sha256"
)

manifest_sha="$(sha256sum -- "${TARGET}/_control/source_manifest_v1.json" | awk '{print $1}')"
printf 'status=complete\nentry_count=18\nsource_commit=%s\nsource_manifest_sha256=%s\n' \
  "${COMMIT}" "${manifest_sha}" >"${TARGET}/_control/ALL_DONE.tmp.$$"
mv -f -- "${TARGET}/_control/ALL_DONE.tmp.$$" "${TARGET}/_control/ALL_DONE"

echo "USTC_TFC2016_RESTORE_COMPLETE target=${TARGET} entries=18 manifest_sha256=${manifest_sha}"
