#!/usr/bin/env bash
set -euo pipefail

WORKDIR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14
PYTHON=/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python
DATASET=/opt/data/private/wangwt/ParkAttackKE/datasets/cic/cic_cse_cic_ids2018
FLOWMETER=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/tools/CICFlowMeter/target/CICFlowMeterV3-0.0.4-SNAPSHOT.jar
NATIVE=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/tools/CICFlowMeter/jnetpcap/linux/jnetpcap-1.4.r1425
UNRAR=/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/tools/unrar-rar5-r20/bin/unrar
RUN_ROOT=/tmp/caeos-cicids2018-all-pcap-r20
TEMP_ROOT=/tmp/caeos-cicids2018-regeneration-r20
OUTPUT_ROOT=/opt/data/private/wangwt/ParkAttackKE/datasets/cic/cic_cse_cic_ids2018/derived/caeos_flow_identity_r20
MANIFEST=${DATASET}/pcap_sync_manifest.json

mkdir -p "${RUN_ROOT}/audits/archives" "${RUN_ROOT}/logs" "${TEMP_ROOT}" "${OUTPUT_ROOT}"
cd "${WORKDIR}"

"${PYTHON}" -u create_caeos_cicids2018_label_regeneration_protocol.py \
  --intake /tmp/caeos-four-new-label-datasets-r19/intake.json \
  --flowmeter-jar "${FLOWMETER}" \
  --output "${RUN_ROOT}/audits/regeneration_protocol.json"

mapfile -t archives < <("${PYTHON}" -c 'import json,sys; print("\n".join(x["local_path"] for x in json.load(open(sys.argv[1]))["objects"]))' "${MANIFEST}")
for archive in "${archives[@]}"; do
  day=$(basename "$(dirname "${archive}")")
  marker=${RUN_ROOT}/audits/archives/${day}.complete
  [[ -s "${marker}" ]] && continue
  extract_dir=${TEMP_ROOT}/${day}/extracted
  normalized_dir=${TEMP_ROOT}/${day}/normalized
  output_dir=${OUTPUT_ROOT}/${day}
  mkdir -p "${extract_dir}" "${normalized_dir}" "${output_dir}"
  printf '%s\n' "${day}" >"${RUN_ROOT}/current_archive"
  printf '%s\n' extracting >"${RUN_ROOT}/state"
  case "${archive}" in
    *.zip)
      if ! unzip -q -o "${archive}" -d "${extract_dir}"; then
        case "${extract_dir}" in
          "${TEMP_ROOT}"/*/extracted) ;;
          *) echo "unsafe CICIDS2018 extraction directory: ${extract_dir}" >&2; exit 2 ;;
        esac
        find "${extract_dir}" -mindepth 1 -delete
        7z x -y -o"${extract_dir}" "${archive}" >/dev/null
      fi
      ;;
    *.rar)
      [[ -x "${UNRAR}" ]] || { echo "RAR5 decoder unavailable: ${UNRAR}" >&2; exit 2; }
      "${UNRAR}" x -inul -o+ "${archive}" "${extract_dir}/"
      ;;
    *) echo "unsupported CICIDS2018 archive: ${archive}" >&2; exit 2 ;;
  esac
  find "${normalized_dir}" -mindepth 1 -maxdepth 1 -type l -delete
  while IFS= read -r -d '' source; do
    if file -b "${source}" | grep -qiE 'pcap|capture file'; then
      relative=${source#"${extract_dir}/"}
      digest=$(printf '%s' "${relative}" | sha256sum | cut -c1-16)
      ln -s "${source}" "${normalized_dir}/${digest}-$(basename "${source}").pcap"
    fi
  done < <(find "${extract_dir}" -type f -print0)
  count=$(find "${normalized_dir}" -maxdepth 1 -type l | wc -l)
  [[ ${count} -gt 0 ]] || { echo "no readable capture members in ${archive}" >&2; exit 3; }
  printf '%s\n' regenerating_flow_identity >"${RUN_ROOT}/state"
  java -Duser.timezone=Etc/GMT+4 -Djava.library.path="${NATIVE}" \
    -cp "${FLOWMETER}" cic.cs.unb.ca.ifm.Cmd "${normalized_dir}" "${output_dir}" \
    >"${RUN_ROOT}/logs/${day}.flowmeter.log" 2>&1
  flow_csv_count=$(find "${output_dir}" -maxdepth 1 -type f -name '*Flow.csv' | wc -l)
  [[ ${flow_csv_count} -eq ${count} ]] || {
    echo "flow CSV count mismatch for ${day}: ${flow_csv_count}/${count}" >&2
    exit 4
  }
  printf 'capture_members=%s\nflow_csvs=%s\narchive=%s\n' "${count}" "${flow_csv_count}" "${archive}" >"${marker}"
  find "${TEMP_ROOT:?}/${day}" -mindepth 1 -delete
done

printf '%s\n' waiting_for_exact_official_label_join >"${RUN_ROOT}/state"
