#!/usr/bin/env bash
# Frozen arrival-time harness for a new high-speed capture NIC.
#
# Default behaviour is read-only inventory/preflight.  The optional capability
# branch refuses to run unless a maintenance window, an explicit authorization,
# a change ticket, and a hash-frozen helper manifest are all present.  This file
# intentionally does not contain vendor-specific PF mutation commands.
set -Eeuo pipefail
umask 077

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
contract="${HFT_NEW_NIC_CONTRACT:-${project_root}/configs/new_nic_acceptance_contract_v1.json}"
evidence_root="${HFT_NEW_NIC_EVIDENCE_ROOT:-/home/wangwt/task/datasets/replay}"
python_bin="${HFT_NEW_NIC_PYTHON:-python3}"
interfaces_csv="${HFT_NEW_NIC_INTERFACES:-}"
worker_cpus="${HFT_NEW_NIC_WORKER_CPUS:-}"
stack_attestation="${HFT_NEW_NIC_STACK_ATTESTATION:-}"
generator_attestation="${HFT_NEW_NIC_GENERATOR_ATTESTATION:-}"
xdp_receipt="${HFT_NEW_NIC_XDP_RECEIPT:-}"
dpdk_receipt="${HFT_NEW_NIC_DPDK_RECEIPT:-}"
execute_probes="${HFT_NEW_NIC_EXECUTE_PROBES:-NO}"
authorization="${HFT_NEW_NIC_MUTATION_AUTHORIZATION:-}"
maintenance_window="${HFT_NEW_NIC_MAINTENANCE_WINDOW:-NO}"
change_ticket="${HFT_NEW_NIC_CHANGE_TICKET:-}"
helper_manifest="${HFT_NEW_NIC_HELPER_MANIFEST:-}"
restore_helper="${HFT_NEW_NIC_RESTORE_HELPER:-}"
trusted_manifest_sha256="${HFT_NEW_NIC_TRUSTED_MANIFEST_SHA256:-}"
restore_timeout_s="${HFT_NEW_NIC_RESTORE_TIMEOUT_S:-120}"
preflight_cli_path="${project_root}/scripts/preflight_new_nic.py"
preflight_pythonpath="${project_root}"

timestamp="$(date -u +%Y%m%dT%H%M%S%NZ)"
mkdir -p "${evidence_root}"
run_dir="$(mktemp -d "${evidence_root}/hft_new_nic_acceptance_${timestamp}_XXXXXX")"
exec 9>"${evidence_root}/.hft_new_nic_acceptance.lock"
if ! flock -n 9; then
  echo "another new-NIC acceptance is active" >&2
  exit 73
fi

baseline="${run_dir}/inventory.before.json"
preflight="${run_dir}/preflight.before.json"
restored_inventory="${run_dir}/inventory.after.json"
restored_preflight="${run_dir}/preflight.after.json"
authorization_record="${run_dir}/authorization.json"
restoration_record="${run_dir}/restoration.json"
mutations_started=0
restore_attempted=false
restore_succeeded=false
final_status=99

split_interfaces=()
if [[ -n "${interfaces_csv}" ]]; then
  IFS=',' read -r -a split_interfaces <<< "${interfaces_csv}"
fi

preflight_command() {
  local output="$1"
  local inventory_output="$2"
  shift 2
  local -a command=(
    "${python_bin}" "${preflight_cli_path}"
    --contract "${contract}"
    --output "${output}"
    --inventory-output "${inventory_output}"
    --worker-cpus "${worker_cpus}"
  )
  if ((${#split_interfaces[@]})); then
    command+=(--interfaces "${split_interfaces[@]}")
  fi
  [[ -z "${stack_attestation}" ]] || command+=(--stack-attestation "${stack_attestation}")
  [[ -z "${generator_attestation}" ]] || command+=(--generator-attestation "${generator_attestation}")
  [[ -z "${xdp_receipt}" ]] || command+=(--xdp-receipt "${xdp_receipt}")
  [[ -z "${dpdk_receipt}" ]] || command+=(--dpdk-receipt "${dpdk_receipt}")
  command+=("$@")
  "${command[@]}"
}

write_restoration_record() {
  PYTHONPATH="${project_root}${PYTHONPATH:+:${PYTHONPATH}}" "${python_bin}" - \
    "${baseline}" "${restored_inventory}" "${restoration_record}" \
    "${restore_attempted}" "${restore_succeeded}" <<'PY'
import json
import pathlib
import sys

before_path, after_path, output_path = map(pathlib.Path, sys.argv[1:4])

before = json.loads(before_path.read_text(encoding="utf-8"))
after = json.loads(after_path.read_text(encoding="utf-8"))

# Import path is supplied by the runner environment below; duplicate the tiny
# fingerprint comparison here would risk contract drift.
from hft_mgbs.new_nic_acceptance import compare_restoration

result = compare_restoration(before, after)
result.update({
    "schema_version": 1,
    "scope": "new_high_speed_nic_restoration",
    "restore_attempted": sys.argv[4] == "true",
    "restore_helper_succeeded": sys.argv[5] == "true",
})
result["accepted"] = (
    result["verified"]
    and result["restore_attempted"]
    and result["restore_helper_succeeded"]
)
output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
}

finalize() {
  local observed="$?"
  # Cleanup is deliberately non-interruptible: a second signal must not kill
  # the shell between PF restoration and evidence sealing.
  trap - EXIT
  trap '' HUP INT TERM
  if (( mutations_started == 1 )); then
    restore_attempted=true
    if [[ -n "${frozen_restore_helper:-}" && -x "${frozen_restore_helper}" ]]; then
      if timeout --signal=TERM --kill-after=10s "${restore_timeout_s}s" \
        "${frozen_restore_helper}" --change-ticket "${change_ticket}" \
        --run-dir "${run_dir}"; then
        restore_succeeded=true
      fi
    fi
    set +e
    PYTHONPATH="${preflight_pythonpath}" \
      preflight_command "${restored_preflight}" "${restored_inventory}" \
      --baseline-inventory "${baseline}"
    after_status="$?"
    write_restoration_record
    restoration_accepted="$("${python_bin}" -c \
      'import json,sys; print(str(json.load(open(sys.argv[1], encoding="utf-8"))["accepted"]).lower())' \
      "${restoration_record}")"
    set -e
    if [[ "${restore_succeeded}" != true || "${restoration_accepted}" != true \
      || "${after_status}" -ne 26 ]]; then
      final_status=97
    elif (( final_status == 99 )); then
      final_status="${observed}"
    fi
  elif (( final_status == 99 )); then
    final_status="${observed}"
  fi
  (
    cd "${run_dir}"
    manifest_tmp="evidence.sha256.tmp.$$"
    check_tmp="evidence.sha256.check.tmp.$$"
    find . -maxdepth 1 -type f \
      ! -name 'evidence.sha256' \
      ! -name 'evidence.sha256.check' \
      ! -name 'evidence.sha256.tmp.*' \
      ! -name 'evidence.sha256.check.tmp.*' \
      -printf '%P\0' \
      | sort -z \
      | xargs -0 -r sha256sum > "${manifest_tmp}"
    mv -- "${manifest_tmp}" evidence.sha256
    sha256sum -c evidence.sha256 > "${check_tmp}"
    mv -- "${check_tmp}" evidence.sha256.check
  )
  exit "${final_status}"
}
trap finalize EXIT
trap 'final_status=129; exit 129' HUP
trap 'final_status=130; exit 130' INT
trap 'final_status=143; exit 143' TERM

set +e
PYTHONPATH="${preflight_pythonpath}" \
  preflight_command "${preflight}" "${baseline}"
preflight_status="$?"
set -e
preflight_state="$("${python_bin}" -c \
  'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["status"])' \
  "${preflight}")"

if [[ "${execute_probes}" != "YES" ]]; then
  final_status="${preflight_status}"
  exit "${final_status}"
fi

if [[ "${preflight_state}" != "capability_probe_pending" ]]; then
  echo "authorized probes are allowed only from capability_probe_pending" >&2
  final_status=64
  exit "${final_status}"
fi
if [[ "${authorization}" != "APPROVED_NEW_NIC_PF_MAINTENANCE" ]]; then
  echo "explicit new-NIC PF maintenance authorization is absent" >&2
  final_status=65
  exit "${final_status}"
fi
if [[ "${maintenance_window}" != "YES" ]]; then
  echo "maintenance window is not active" >&2
  final_status=66
  exit "${final_status}"
fi
if [[ ! "${change_ticket}" =~ ^[A-Za-z0-9][A-Za-z0-9._:-]{2,127}$ ]]; then
  echo "a non-empty change ticket is required" >&2
  final_status=67
  exit "${final_status}"
fi
if [[ ! -f "${helper_manifest}" ]]; then
  echo "frozen helper manifest is missing" >&2
  final_status=68
  exit "${final_status}"
fi
if [[ ! "${trusted_manifest_sha256}" =~ ^[0-9a-f]{64}$ \
  || "$(sha256sum "${helper_manifest}" | awk '{print $1}')" != "${trusted_manifest_sha256}" ]]; then
  echo "helper manifest does not match the externally supplied trusted SHA-256 root" >&2
  final_status=76
  exit "${final_status}"
fi
frozen_manifest="${run_dir}/frozen_helper_manifest.txt"
cp --no-preserve=mode,ownership,timestamps -- "${helper_manifest}" "${frozen_manifest}"
chmod 0400 "${frozen_manifest}"
if [[ "$(sha256sum "${frozen_manifest}" | awk '{print $1}')" \
  != "${trusted_manifest_sha256}" ]]; then
  echo "frozen helper manifest copy does not match trusted SHA-256 root" >&2
  final_status=78
  exit "${final_status}"
fi
helper_manifest="${frozen_manifest}"
if [[ ! -x "${restore_helper}" ]]; then
  echo "executable restore helper is missing" >&2
  final_status=69
  exit "${final_status}"
fi

for artifact_name in \
  xdp_probe dpdk_probe restore_helper runner preflight_cli acceptance_module contract; do
  artifact_path="$(awk -v name="${artifact_name}" '$1 == name { print $2 }' "${helper_manifest}")"
  artifact_sha="$(awk -v name="${artifact_name}" '$1 == name { print $3 }' "${helper_manifest}")"
  if [[ -z "${artifact_path}" || ! -f "${artifact_path}" \
    || ! -r "${artifact_path}" || ! "${artifact_sha}" =~ ^[0-9a-f]{64}$ ]]; then
    echo "invalid ${artifact_name} frozen artifact manifest entry" >&2
    final_status=70
    exit "${final_status}"
  fi
  if [[ "$(sha256sum "${artifact_path}" | awk '{print $1}')" != "${artifact_sha}" ]]; then
    echo "${artifact_name} frozen artifact hash mismatch" >&2
    final_status=71
    exit "${final_status}"
  fi
done

frozen_artifact_dir="${run_dir}/frozen_artifacts"
mkdir -p "${frozen_artifact_dir}"
for artifact_name in \
  xdp_probe dpdk_probe restore_helper runner preflight_cli acceptance_module contract; do
  artifact_path="$(awk -v name="${artifact_name}" '$1 == name { print $2 }' "${helper_manifest}")"
  artifact_sha="$(awk -v name="${artifact_name}" '$1 == name { print $3 }' "${helper_manifest}")"
  frozen_path="${frozen_artifact_dir}/${artifact_name}"
  cp --no-preserve=mode,ownership,timestamps -- "${artifact_path}" "${frozen_path}"
  chmod 0500 "${frozen_path}"
  if [[ "$(sha256sum "${frozen_path}" | awk '{print $1}')" != "${artifact_sha}" ]]; then
    echo "${artifact_name} frozen-copy hash mismatch" >&2
    final_status=77
    exit "${final_status}"
  fi
done
frozen_xdp_helper="${frozen_artifact_dir}/xdp_probe"
frozen_dpdk_helper="${frozen_artifact_dir}/dpdk_probe"
frozen_restore_helper="${frozen_artifact_dir}/restore_helper"
frozen_python_root="${run_dir}/frozen_python"
mkdir -p "${frozen_python_root}/hft_mgbs"
printf '%s\n' '"""Frozen new-NIC acceptance package."""' \
  > "${frozen_python_root}/hft_mgbs/__init__.py"
cp -- "${frozen_artifact_dir}/acceptance_module" \
  "${frozen_python_root}/hft_mgbs/new_nic_acceptance.py"
preflight_cli_path="${frozen_artifact_dir}/preflight_cli"
preflight_pythonpath="${frozen_python_root}"
for helper_name in xdp_probe dpdk_probe restore_helper; do
  helper_path="$(awk -v name="${helper_name}" '$1 == name { print $2 }' "${helper_manifest}")"
  if [[ ! -x "${helper_path}" ]]; then
    echo "${helper_name} frozen helper is not executable" >&2
    final_status=75
    exit "${final_status}"
  fi
done

declare -A frozen_core_paths=(
  [runner]="${project_root}/scripts/run_new_nic_acceptance.sh"
  [preflight_cli]="${project_root}/scripts/preflight_new_nic.py"
  [acceptance_module]="${project_root}/hft_mgbs/new_nic_acceptance.py"
  [contract]="${contract}"
)
for helper_name in runner preflight_cli acceptance_module contract; do
  frozen_path="$(awk -v name="${helper_name}" '$1 == name { print $2 }' "${helper_manifest}")"
  if [[ "${frozen_path}" != "${frozen_core_paths[${helper_name}]}" ]]; then
    echo "${helper_name} path does not match the active frozen artifact" >&2
    final_status=74
    exit "${final_status}"
  fi
done

# Switch to the frozen contract only after proving that the manifest named the
# active preflight contract.  Switching earlier would compare the original
# manifest path with the frozen path and make every authorized run exit 74.
contract="${frozen_artifact_dir}/contract"

if [[ "$(awk '$1 == "restore_helper" { print $2 }' "${helper_manifest}")" != "${restore_helper}" ]]; then
  echo "restore helper path does not match frozen manifest" >&2
  final_status=72
  exit "${final_status}"
fi

"${python_bin}" - "${authorization_record}" "${change_ticket}" "${helper_manifest}" <<'PY'
import hashlib
import json
import pathlib
import sys
from datetime import datetime, timezone

output, ticket, manifest = pathlib.Path(sys.argv[1]), sys.argv[2], pathlib.Path(sys.argv[3])
value = {
    "schema_version": 1,
    "scope": "new_high_speed_nic_explicit_authorization",
    "recorded_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "change_ticket": ticket,
    "helper_manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
    "authorization_present": True,
    "maintenance_window_present": True,
}
output.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

# This is the only transition after which a helper may change PF/XDP state.
mutations_started=1
"${frozen_xdp_helper}" --change-ticket "${change_ticket}" --run-dir "${run_dir}" \
  --receipt "${run_dir}/xdp_probe_receipt.json"
"${frozen_dpdk_helper}" --change-ticket "${change_ticket}" --run-dir "${run_dir}" \
  --receipt "${run_dir}/dpdk_probe_receipt.json"

xdp_receipt="${run_dir}/xdp_probe_receipt.json"
dpdk_receipt="${run_dir}/dpdk_probe_receipt.json"
xdp_helper_sha="$(awk '$1 == "xdp_probe" { print $3 }' "${helper_manifest}")"
dpdk_helper_sha="$(awk '$1 == "dpdk_probe" { print $3 }' "${helper_manifest}")"
"${python_bin}" - "${xdp_receipt}" "${xdp_helper_sha}" \
  "${dpdk_receipt}" "${dpdk_helper_sha}" <<'PY'
import json
import pathlib
import sys

for receipt_path, expected_sha in (
    (pathlib.Path(sys.argv[1]), sys.argv[2]),
    (pathlib.Path(sys.argv[3]), sys.argv[4]),
):
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("probe_binary_sha256") != expected_sha:
        raise SystemExit(
            "receipt probe_binary_sha256 does not match its frozen helper: {}".format(
                receipt_path
            )
        )
PY
set +e
PYTHONPATH="${preflight_pythonpath}" \
  preflight_command "${run_dir}/preflight.probes.json" \
  "${run_dir}/inventory.probes.json"
probe_validation_status="$?"
set -e
probe_validation_state="$("${python_bin}" -c \
  'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8"))["status"])' \
  "${run_dir}/preflight.probes.json")"
if (( probe_validation_status != 26 )) \
  || [[ "${probe_validation_state}" != "self_consistent_capability_receipts_only" ]]; then
  echo "capability receipts failed independent validation" >&2
  final_status=96
  exit "${final_status}"
fi
final_status=0
exit 0
