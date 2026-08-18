#!/usr/bin/env bash
set -euo pipefail

code_root="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/preprocessing/caeos_unified_multimodal_v5_20260802_r14"
output_root="/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v5"
control_root="${output_root}/_control"
run_root="${control_root}/audits/three_dataset_admission_20260808"
python_bin="/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python"
catalog="${code_root}/configs/unified_multimodal_v5_split_class.datasets.json"
registry="${code_root}/configs/unified_multimodal_v5.labels.json"
exclusions="${code_root}/configs/unified_multimodal_v5.exclusions.json"
source_manifest="${control_root}/source_manifest.json"
label_manifest="${control_root}/label_index_manifest.json"

mkdir -p "${run_root}/coverage" "${run_root}/index_audits" \
  "${run_root}/label_indices" "${run_root}/support" \
  "${run_root}/source_manifests" "${run_root}/validation" "${run_root}/logs" \
  "${control_root}/label_indices"
exec 9>"/tmp/caeos_three_dataset_admission.lock"
flock -n 9 || { echo "three-dataset admission is already running" >&2; exit 73; }
cd "${code_root}"

log_stage() {
  printf '%s\t%s\n' "$(date --iso-8601=seconds)" "$1" | tee -a "${run_root}/status.tsv"
}

require_gate() {
  local summary=$1
  jq -e '.formal_label_gate_passed == true and .effective_coverage_fraction >= 0.999999999999' \
    "${summary}" >/dev/null
}

log_stage labels_verify_existing_full_audits
require_gate /tmp/caeos-unsw-nb15-conflict-recovery-r21/summary.json
require_gate /tmp/caeos-5gad-2022-all-pcap-r19/summary.json
require_gate "${control_root}/audits/cicids2018_strict_r22_20260808/summary.json"

unsw_index=/tmp/caeos-unsw-nb15-all-pcap-r19/label_indices/unsw_nb15.sqlite
gad_index=/tmp/caeos-5gad-2022-all-pcap-r19/label_indices/5gad_2022.sqlite
cicids_index="${run_root}/label_indices/cicids2018.sqlite"

if [[ ! -s "${cicids_index}" ]]; then
  "${python_bin}" -u build_caeos_cicids2018_schedule_label_index.py \
    --schedule configs/cicids2018_official_attack_schedule.json \
    --registry "${registry}" --output-index "${cicids_index}" \
    --audit-output "${run_root}/support/cicids2018_schedule_index.json" \
    >"${run_root}/logs/build_cicids2018_index.json"
fi
"${python_bin}" -u validate_caeos_label_index.py \
  --path "${cicids_index}" --dataset-id cicids2018 --group-counts \
  --require-protocol-distribution \
  --output "${run_root}/support/cicids2018_index_validation.json" \
  >"${run_root}/logs/validate_cicids2018_index.json"

log_stage labels_reaggregate_cached_audits
"${python_bin}" -u audit_caeos_all_pcap_members.py \
  --dataset-id unsw_nb15 \
  --dataset-root /opt/data/private/wangwt/ParkAttackKE/datasets/UNSW-NB15 \
  --pcap-root /opt/data/private/wangwt/ParkAttackKE/datasets/UNSW-NB15/PCAPs \
  --label-index "${unsw_index}" --label-index-sha256 "$(sha256sum "${unsw_index}" | cut -d' ' -f1)" \
  --inventory-output /tmp/caeos-unsw-nb15-all-pcap-r19/inventory.json \
  --audit-dir /tmp/caeos-unsw-nb15-all-pcap-r19/audits/per_source \
  --summary-output "${run_root}/coverage/unsw_nb15.json" \
  --temporary-dir /tmp/caeos-unsw-nb15-all-pcap-r19/temporary \
  --tolerance-ns 1000000000 --idle-seconds 30 \
  --conflict-policy malicious_over_benign_bidirectional \
  --conflict-exclusion-policy binary_malicious_consensus_multiclass_ambiguous \
  --conflict-exclusion-evidence \
  /tmp/caeos-unsw-nb15-conflict-recovery-r21/audits/unsw_nb15_conflict_inventory_manifest.json \
  --summarize-existing-only >"${run_root}/logs/unsw_reaggregate.json"

"${python_bin}" -u audit_caeos_all_pcap_members.py \
  --dataset-id 5gad_2022 \
  --dataset-root /opt/data/private/wangwt/ParkAttackKE/datasets/5GAD-2022 \
  --pcap-root /tmp/caeos-5gad-2022-all-pcap-r19/selected_pcaps \
  --label-index "${gad_index}" --label-index-sha256 "$(sha256sum "${gad_index}" | cut -d' ' -f1)" \
  --inventory-output /tmp/caeos-5gad-2022-all-pcap-r19/inventory.json \
  --audit-dir /tmp/caeos-5gad-2022-all-pcap-r19/audits/per_source \
  --summary-output "${run_root}/coverage/5gad_2022.json" \
  --temporary-dir /tmp/caeos-5gad-2022-all-pcap-r19/temporary \
  --tolerance-ns 1000000 --idle-seconds 30 \
  --authority-granularity documented_single_class_capture \
  --conflict-policy reject --summarize-existing-only \
  >"${run_root}/logs/5gad_reaggregate.json"

cp -p "${control_root}/audits/cicids2018_strict_r22_20260808/summary.json" \
  "${run_root}/coverage/cicids2018.json"
sync -f "${run_root}/coverage/cicids2018.json" || true
require_gate "${run_root}/coverage/unsw_nb15.json"
require_gate "${run_root}/coverage/5gad_2022.json"
require_gate "${run_root}/coverage/cicids2018.json"

log_stage labels_persist_indices
"${python_bin}" -u persist_caeos_label_index.py \
  --dataset-id unsw_nb15 --source "${unsw_index}" \
  --destination "${control_root}/label_indices/unsw_nb15.sqlite" \
  --audit-output "${run_root}/index_audits/unsw_nb15.json" \
  >"${run_root}/logs/persist_unsw.json"
"${python_bin}" -u persist_caeos_label_index.py \
  --dataset-id 5gad_2022 --source "${gad_index}" \
  --destination "${control_root}/label_indices/5gad_2022.sqlite" \
  --audit-output "${run_root}/index_audits/5gad_2022.json" \
  >"${run_root}/logs/persist_5gad.json"
"${python_bin}" -u persist_caeos_label_index.py \
  --dataset-id cicids2018 --source "${cicids_index}" \
  --destination "${control_root}/label_indices/cicids2018.sqlite" \
  --audit-output "${run_root}/index_audits/cicids2018.json" \
  >"${run_root}/logs/persist_cicids2018.json"

log_stage sources_hash_three_new_datasets
addition="${run_root}/source_manifests/addition.json"
if [[ -e "${addition}" ]]; then
  jq -e '.full_source_hashes_computed == true and ([.datasets[].id] | sort) == ["5gad_2022","cicids2018","unsw_nb15"]' \
    "${addition}" >/dev/null || {
      preserved="${addition}.superseded.$(date -u +%Y%m%dT%H%M%S)"
      mv "${addition}" "${preserved}"
    }
fi
if [[ ! -e "${addition}" ]]; then
  "${python_bin}" -u caeos_unified_dataset.py \
    --catalog "${catalog}" --output "${addition}" --io-threads 2 \
    --dataset cicids2018 --dataset unsw_nb15 --dataset 5gad_2022 \
    >"${run_root}/logs/source_addition.json"
fi

log_stage sources_extend_manifest
source_stage="${run_root}/source_manifests/source_manifest.extended.json"
if [[ -e "${source_stage}" ]]; then
  preserved="${source_stage}.superseded.$(date -u +%Y%m%dT%H%M%S)"
  mv "${source_stage}" "${preserved}"
fi
"${python_bin}" -u extend_caeos_source_manifest.py \
  --base "${source_manifest}" --addition "${addition}" --catalog "${catalog}" \
  --output "${source_stage}" >"${run_root}/logs/source_extend.json"
"${python_bin}" - "${catalog}" "${source_stage}" <<'PY'
import json
import sys
from prepare_caeos_unified_multimodal_csv import validate_source_manifest

with open(sys.argv[1], encoding="utf-8") as handle:
    catalog = json.load(handle)
with open(sys.argv[2], encoding="utf-8") as handle:
    manifest = json.load(handle)
validate_source_manifest(catalog, manifest)
assert {item["id"] for item in manifest["datasets"]} >= {
    "cicids2018", "unsw_nb15", "5gad_2022"
}
PY

log_stage labels_assemble_extended_manifest
label_stage="${run_root}/label_index_manifest.extended.json"
arguments=()
while IFS= read -r path; do
  [[ -n "${path}" ]] && arguments+=(--index-audit "${path}")
done < <(jq -r '.datasets[].index_audit_path // empty' "${label_manifest}")
while IFS= read -r path; do
  [[ -n "${path}" ]] && arguments+=(--coverage-audit "${path}")
done < <(jq -r '.datasets[].coverage_evidence[]?.path // empty' "${label_manifest}")
arguments+=(
  --index-audit "${run_root}/index_audits/cicids2018.json"
  --index-audit "${run_root}/index_audits/unsw_nb15.json"
  --index-audit "${run_root}/index_audits/5gad_2022.json"
  --coverage-audit "${run_root}/coverage/cicids2018.json"
  --coverage-audit "${run_root}/coverage/unsw_nb15.json"
  --coverage-audit "${run_root}/coverage/5gad_2022.json"
)
"${python_bin}" -u assemble_caeos_label_index_manifest.py \
  --registry "${registry}" --exclusion-policy "${exclusions}" \
  --output "${label_stage}" "${arguments[@]}" \
  >"${run_root}/logs/label_manifest.json"

"${python_bin}" -u validate_caeos_label_delivery.py \
  --manifest "${label_stage}" --source-manifest "${source_stage}" --full-hash \
  --dataset cicids2018 --dataset unsw_nb15 --dataset 5gad_2022 \
  --output "${run_root}/validation/prepublish.json" \
  >"${run_root}/logs/prepublish_validation.json"

log_stage publish_atomic_manifests
stamp="$(date -u +%Y%m%dT%H%M%S)"
cp -p "${source_manifest}" "${source_manifest}.pre_three_dataset.${stamp}"
cp -p "${label_manifest}" "${label_manifest}.pre_three_dataset.${stamp}"
mv "${source_stage}" "${source_manifest}"
mv "${label_stage}" "${label_manifest}"
sync -f "${source_manifest}" || true
sync -f "${label_manifest}" || true

"${python_bin}" -u validate_caeos_label_delivery.py \
  --manifest "${label_manifest}" --source-manifest "${source_manifest}" --full-hash \
  --dataset cicids2018 --dataset unsw_nb15 --dataset 5gad_2022 \
  --output "${run_root}/validation/final.json" \
  >"${run_root}/logs/final_validation.json"

"${python_bin}" - "${source_manifest}" "${label_manifest}" \
  "${run_root}/validation/final.json" "${run_root}/completion.json" <<'PY'
import json
import sys
from caeos_unified_dataset import atomic_json, sha256_file

source_path, label_path, validation_path, output_path = map(__import__("pathlib").Path, sys.argv[1:])
source = json.loads(source_path.read_text(encoding="utf-8"))
labels = json.loads(label_path.read_text(encoding="utf-8"))
validation = json.loads(validation_path.read_text(encoding="utf-8"))
ids = ("cicids2018", "unsw_nb15", "5gad_2022")
source_by_id = {item["id"]: item for item in source["datasets"]}
label_by_id = {item["id"]: item for item in labels["datasets"]}
payload = {
    "schema_version": "caeos_three_dataset_admission_completion_v1",
    "status": "complete",
    "datasets": [
        {
            "dataset_id": dataset_id,
            "source_file_count": source_by_id[dataset_id]["source_file_count"],
            "capture_count": source_by_id[dataset_id]["capture_count"],
            "source_size_bytes": source_by_id[dataset_id]["source_size_bytes"],
            "label_status": label_by_id[dataset_id]["status"],
            "gate_types": label_by_id[dataset_id]["admission_gate_types"],
            "effective_coverage_fraction": label_by_id[dataset_id]["effective_coverage_fraction"],
            "label_record_count": label_by_id[dataset_id]["record_count"],
        }
        for dataset_id in ids
    ],
    "source_manifest": str(source_path),
    "source_manifest_sha256": sha256_file(source_path),
    "label_manifest": str(label_path),
    "label_manifest_sha256": sha256_file(label_path),
    "delivery_validation": validation,
}
atomic_json(output_path, payload)
PY
log_stage complete
