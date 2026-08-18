#!/usr/bin/env bash
set -euo pipefail

code_root="${1:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/paper_protocols/caeos_paper_closure_v1}"
output_root="${2:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/datasets/caeos_unified_multimodal_v5}"
interval_seconds="${3:-300}"
launch_log="${output_root}/_control/paper_protocol_v1/readiness_launcher.log"

mkdir -p "$(dirname "${launch_log}")"
setsid -f "${code_root}/watch_caeos_paper_readiness_v1.sh" \
    "${code_root}" "${output_root}" "${interval_seconds}" \
    </dev/null >>"${launch_log}" 2>&1
sleep 2
pgrep -af "${code_root}/watch_caeos_paper_readiness_v1.sh" || true
