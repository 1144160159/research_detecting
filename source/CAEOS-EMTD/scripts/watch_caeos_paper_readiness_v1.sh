#!/usr/bin/env bash
set -euo pipefail

code_root="${1:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/paper_protocols/caeos_paper_closure_v1}"
output_root="${2:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v5}"
interval_seconds="${3:-300}"
control_root="${output_root}/_control/paper_protocol_v1"
contract="${code_root}/contracts/caeos_paper_closure_contract_v1.json"
auditor="${code_root}/audit_caeos_paper_readiness.py"
duplicate_auditor="${code_root}/audit_caeos_flow_duplicates.py"
equivalence_auditor="${code_root}/audit_caeos_train_deploy_equivalence.py"
gate_builder="${code_root}/build_caeos_paper_d0_p0_artifacts.py"
schema="${code_root}/configs/unified_multimodal_v4.schema.json"
feature_views="${code_root}/configs/unified_multimodal_v5.feature_views.json"
report="${control_root}/readiness.json"
log="${control_root}/readiness_watcher.log"

mkdir -p "${control_root}"
exec 9>"/tmp/caeos_paper_readiness_v1.lock"
if ! flock -n 9; then
    printf '%s %s\n' "$(date --iso-8601=seconds)" \
        '{"event":"watcher_rejected","reason":"already_running"}' >> "${log}"
    exit 73
fi

while true; do
    temporary="${report}.tmp"
    /opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python \
        "${auditor}" \
        --contract "${contract}" \
        --output-root "${output_root}" \
        --output "${temporary}" >/dev/null
    mv "${temporary}" "${report}"

    summary="$({
        /opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python -c '
import json, sys
value = json.load(open(sys.argv[1], encoding="utf-8"))
summary = value["summary"]
print(json.dumps({"event": "readiness_snapshot", **summary}, sort_keys=True))
' "${report}"
    })"
    printf '%s %s\n' "$(date --iso-8601=seconds)" "${summary}" >> "${log}"

    if /opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python -c '
import json, sys
value = json.load(open(sys.argv[1], encoding="utf-8"))
raise SystemExit(0 if value["summary"]["development_manifest_ready"] else 1)
' "${report}"; then
        completion="${output_root}/_control/feature_extraction/completion.lane1.ciciot2023.json"
        if [[ -f "${completion}" ]] && /opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python -c '
import json, sys
value = json.load(open(sys.argv[1], encoding="utf-8"))
raise SystemExit(0 if value.get("all_complete") else 1)
' "${completion}"; then
            break
        fi
    fi
    sleep "${interval_seconds}" 9>&-
done

printf '%s %s\n' "$(date --iso-8601=seconds)" \
    '{"event":"D0_P0_pipeline_started"}' >> "${log}"
duplicate_report="${control_root}/duplicate_audits/ciciot2023.json"
if [[ ! -f "${duplicate_report}" ]]; then
    mkdir -p "$(dirname "${duplicate_report}")"
    ionice -c3 nice -n 15 \
        /opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python \
        "${duplicate_auditor}" \
        --dataset-manifest "${output_root}/ciciot2023/dataset.manifest.json" \
        --scratch /tmp/caeos_ciciot2023_duplicate_audit_v1 \
        --output "${duplicate_report}" \
        >>"${log}" 2>&1
fi

/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python \
    "${equivalence_auditor}" \
    --dataset-manifest "${output_root}/ciciot2023/dataset.manifest.json" \
    --output "${control_root}/train_deploy_equivalence.json" \
    --samples-per-class 8 \
    >>"${log}" 2>&1

/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python \
    "${gate_builder}" \
    --contract "${contract}" \
    --output-root "${output_root}" \
    --schema "${schema}" \
    --feature-views "${feature_views}" \
    >>"${log}" 2>&1

/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python \
    "${auditor}" \
    --contract "${contract}" \
    --output-root "${output_root}" \
    --output "${report}" >/dev/null

printf '%s %s\n' "$(date --iso-8601=seconds)" \
    '{"event":"D0_P0_pipeline_completed","action":"inspect_readiness_before_F0"}' >> "${log}"
