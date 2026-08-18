#!/usr/bin/env bash
# Two-phase, fail-closed R0 campaign harness for a newly accepted high-speed NIC.
#
# No authorization variables: create a hardware_pending audit and perform no
# NIC/PF/XDP/DPDK action.  EXECUTE phase: run only externally hash-frozen
# helpers, then restore and seal an untrusted candidate manifest.  COMPOSE phase:
# accept only the exact manifest SHA-256 recorded by an independent frozen
# trust-root helper outside the campaign directory and recompute the R0 verdict.
set -Eeuo pipefail
umask 077

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
contract="${HFT_NEW_NIC_R0_CONTRACT:-${project_root}/configs/new_nic_r0_campaign_contract_v1.json}"
composer="${project_root}/scripts/compose_new_nic_r0_acceptance.py"
evaluator="${project_root}/hft_mgbs/new_nic_r0.py"
evidence_root="${HFT_NEW_NIC_R0_EVIDENCE_ROOT:-/home/wangwt/task/datasets/replay}"
python_bin="${HFT_NEW_NIC_R0_PYTHON:-python3}"
phase="${HFT_NEW_NIC_R0_PHASE:-PENDING}"
authorization="${HFT_NEW_NIC_R0_AUTHORIZATION:-}"
maintenance_window="${HFT_NEW_NIC_R0_MAINTENANCE_WINDOW:-NO}"
change_ticket="${HFT_NEW_NIC_R0_CHANGE_TICKET:-}"
helper_manifest="${HFT_NEW_NIC_R0_HELPER_MANIFEST:-}"
trusted_helper_manifest_sha="${HFT_NEW_NIC_R0_TRUSTED_HELPER_MANIFEST_SHA256:-}"
execution_plan="${HFT_NEW_NIC_R0_EXECUTION_PLAN:-}"
trusted_execution_plan_sha="${HFT_NEW_NIC_R0_TRUSTED_EXECUTION_PLAN_SHA256:-}"
resume_dir="${HFT_NEW_NIC_R0_RESUME_DIR:-}"
trusted_evidence_manifest_sha="${HFT_NEW_NIC_R0_TRUSTED_EVIDENCE_MANIFEST_SHA256:-}"
trust_root_receipt="${HFT_NEW_NIC_R0_TRUST_ROOT_RECEIPT:-}"
arrival_evidence_dir="${HFT_NEW_NIC_R0_ARRIVAL_EVIDENCE_DIR:-}"
arrival_evidence_manifest="${HFT_NEW_NIC_R0_ARRIVAL_EVIDENCE_MANIFEST:-}"
trusted_arrival_manifest_sha="${HFT_NEW_NIC_R0_TRUSTED_ARRIVAL_MANIFEST_SHA256:-}"
restore_timeout_s="${HFT_NEW_NIC_R0_RESTORE_TIMEOUT_S:-180}"

mkdir -p "${evidence_root}"
exec 9>"${evidence_root}/.hft_new_nic_r0_campaign.lock"
if ! flock -n 9; then
  echo "another new-NIC R0 campaign is active" >&2
  exit 73
fi

sha_file() { sha256sum -- "$1" | awk '{print $1}'; }
is_sha() { [[ "$1" =~ ^[0-9a-f]{64}$ ]]; }
manifest_field() {
  local role="$1" field="$2"
  awk -v wanted="${role}" -v column="${field}" '$1 == wanted {print $column}' "${frozen_helper_manifest}"
}
frozen_helper_manifest="${helper_manifest}"
atomic_state() {
  local status="$1" mutations="$2" temporary="${run_dir}/runner_state.json.tmp.$$"
  "${python_bin}" - "${temporary}" "${status}" "${mutations}" "${phase}" "${change_ticket}" <<'PY'
import json, os, pathlib, sys
path = pathlib.Path(sys.argv[1])
payload = {
    "schema_version": 1,
    "scope": "new_nic_r0_runner_state",
    "status": sys.argv[2],
    "mutations_performed": sys.argv[3] == "true",
    "phase": sys.argv[4],
    "change_ticket": sys.argv[5] or None,
}
with path.open("w", encoding="utf-8", newline="\n") as handle:
    json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
    handle.write("\n")
    handle.flush()
    os.fsync(handle.fileno())
path.replace(path.with_name("runner_state.json"))
PY
}
verify_restoration_files() {
  "${python_bin}" - "$1" "$2" "$3" <<'PY'
import json, pathlib, sys
def pairs(items):
    value = {}
    for key, item in items:
        if key in value: raise ValueError("duplicate JSON key")
        value[key] = item
    return value
def nonfinite(value): raise ValueError("non-finite JSON")
def read(path):
    value = json.loads(pathlib.Path(path).read_text(encoding="utf-8"),
        object_pairs_hook=pairs, parse_constant=nonfinite)
    if not isinstance(value, dict): raise ValueError("JSON object required")
    return value
before, after, contract = map(read, sys.argv[1:4])
required = set(contract["restoration_gate"]["required_state_domains"])
if before.get("phase") != "before" or after.get("phase") != "after":
    raise SystemExit("restoration phase mismatch")
before_state, after_state = before.get("state_domains"), after.get("state_domains")
if not isinstance(before_state, dict) or not isinstance(after_state, dict):
    raise SystemExit("restoration state_domains missing")
if not required <= set(before_state) or not required <= set(after_state):
    raise SystemExit("restoration required domains missing")
if before_state != after_state:
    raise SystemExit("restoration state mismatch")
PY
}

if [[ "${phase}" == "PENDING" ]]; then
  timestamp="$(date -u +%Y%m%dT%H%M%S%NZ)"
  run_dir="$(mktemp -d "${evidence_root}/hft_new_nic_r0_${timestamp}_XXXXXX")"
  atomic_state hardware_pending false
  set +e
  PYTHONPATH= "${python_bin}" "${composer}" --hardware-pending \
    --contract "${contract}" --output "${run_dir}/r0_audit.json"
  rc="$?"
  set -e
  [[ "${rc}" -eq 20 ]] || exit "${rc}"
  (
    cd "${run_dir}"
    sha256sum r0_audit.json runner_state.json > evidence.sha256.tmp
    mv evidence.sha256.tmp evidence.sha256
    sha256sum -c evidence.sha256 > evidence.sha256.check.tmp
    mv evidence.sha256.check.tmp evidence.sha256.check
  )
  echo "evidence_dir=${run_dir}"
  exit 20
fi

if [[ "${phase}" == "RECOVER" ]]; then
  if [[ "${authorization}" != "I_AUTHORIZE_NEW_NIC_R0_RECOVERY" \
     || "${maintenance_window}" != "YES" \
     || ! "${change_ticket}" =~ ^[A-Za-z0-9._:-]{4,128}$ ]]; then
    echo "RECOVER requires exact recovery authorization, maintenance window, and change ticket" >&2
    exit 74
  fi
  [[ -n "${resume_dir}" && -d "${resume_dir}" ]] || exit 74
  run_dir="$(cd "${resume_dir}" && pwd -P)"
  case "${run_dir}" in
    "$(cd "${evidence_root}" && pwd -P)"/hft_new_nic_r0_*) ;;
    *) echo "recovery directory is outside the R0 evidence root" >&2; exit 74 ;;
  esac
  [[ -f "${run_dir}/frozen_helper_manifest.txt" && ! -L "${run_dir}/frozen_helper_manifest.txt" ]] || exit 74
  frozen_helper_manifest="${run_dir}/frozen_helper_manifest.txt"
  frozen_execution_plan="${run_dir}/frozen/configs/new_nic_r0_execution_plan_v1.json"
  [[ "$(sha_file "${frozen_helper_manifest}")" == "${trusted_helper_manifest_sha}" ]] || exit 74
  [[ -f "${frozen_execution_plan}" && ! -L "${frozen_execution_plan}" \
    && -f "${run_dir}/execution_plan.sha256" && ! -L "${run_dir}/execution_plan.sha256" \
    && "$(cat "${run_dir}/execution_plan.sha256")" == "$(sha_file "${frozen_execution_plan}")" ]] || exit 74
  expected_restore_sha="$(manifest_field restore_helper 3)"
  frozen_restore="${run_dir}/frozen/restore_helper"
  is_sha "${expected_restore_sha}" && [[ -x "${frozen_restore}" && ! -L "${frozen_restore}" \
    && "$(sha_file "${frozen_restore}")" == "${expected_restore_sha}" ]] || exit 74
  atomic_state recovering true
  set +e
  timeout --signal=TERM --kill-after=15s "${restore_timeout_s}s" \
    "${frozen_restore}" --mode restore --execution-plan "${frozen_execution_plan}" \
    --change-ticket "${change_ticket}" --run-dir "${run_dir}"
  restore_rc="$?"
  set -e
  if [[ "${restore_rc}" -ne 0 ]]; then
    atomic_state recovery_failed true
    printf '%s\n' "restore_failed rc=${restore_rc}" > "${run_dir}/RECOVERY_REQUIRED"
    exit 97
  fi
  "${frozen_restore}" --mode snapshot-after --execution-plan "${frozen_execution_plan}" \
    --change-ticket "${change_ticket}" \
    --run-dir "${run_dir}" --output "${run_dir}/restoration_after.json"
  if ! verify_restoration_files "${run_dir}/restoration_before.json" \
    "${run_dir}/restoration_after.json" \
    "${run_dir}/frozen/configs/new_nic_r0_campaign_contract_v1.json"; then
    atomic_state recovery_failed true
    printf '%s\n' "restoration_state_mismatch" > "${run_dir}/RECOVERY_REQUIRED"
    exit 97
  fi
  printf '%s\n' "recovery_completed" > "${run_dir}/recovery_complete"
  sync "${run_dir}/restoration_after.json" "${run_dir}/recovery_complete"
  atomic_state recovery_completed true
  exit 0
fi

if [[ "${phase}" == "COMPOSE" ]]; then
  [[ -n "${resume_dir}" && -d "${resume_dir}" ]] || {
    echo "COMPOSE requires an existing HFT_NEW_NIC_R0_RESUME_DIR" >&2; exit 74; }
  run_dir="$(cd "${resume_dir}" && pwd -P)"
  case "${run_dir}" in
    "$(cd "${evidence_root}" && pwd -P)"/hft_new_nic_r0_*) ;;
    *) echo "resume directory is outside the R0 evidence root" >&2; exit 74 ;;
  esac
  [[ -f "${run_dir}/execution_complete" && ! -L "${run_dir}/execution_complete" ]] || {
    echo "campaign execution is not durably complete" >&2; exit 74; }
  [[ -f "${run_dir}/frozen_helper_manifest.txt" && ! -L "${run_dir}/frozen_helper_manifest.txt" ]] || exit 74
  frozen_helper_manifest="${run_dir}/frozen_helper_manifest.txt"
  [[ "$(sha_file "${frozen_helper_manifest}")" == "${trusted_helper_manifest_sha}" ]] || {
    echo "COMPOSE requires the original external helper-manifest trust root" >&2; exit 74; }
  [[ -f "${run_dir}/evidence.manifest.json" && ! -L "${run_dir}/evidence.manifest.json" ]] || exit 74
  [[ -n "${trust_root_receipt}" && -f "${trust_root_receipt}" && ! -L "${trust_root_receipt}" ]] || {
    echo "external trust-root receipt is missing" >&2; exit 74; }
  trust_root_receipt="$(cd "$(dirname "${trust_root_receipt}")" && pwd -P)/$(basename "${trust_root_receipt}")"
  case "${trust_root_receipt}" in "${run_dir}"/*) echo "trust root may not live in campaign directory" >&2; exit 74;; esac
  recorded_sha="$(awk 'NF == 1 {print $1}' "${trust_root_receipt}")"
  if ! is_sha "${trusted_evidence_manifest_sha}" \
    || [[ "${recorded_sha}" != "${trusted_evidence_manifest_sha}" ]] \
    || [[ "$(sha_file "${run_dir}/evidence.manifest.json")" != "${trusted_evidence_manifest_sha}" ]] \
    || [[ "$(cat "${run_dir}/execution_complete")" != "${trusted_evidence_manifest_sha}" ]]; then
    echo "evidence manifest does not match both external trust roots" >&2
    exit 74
  fi
  expected_composer_sha="$(manifest_field composer 3)"
  expected_evaluator_sha="$(manifest_field evaluator 3)"
  expected_contract_sha="$(manifest_field contract 3)"
  expected_runner_sha="$(manifest_field runner 3)"
  for entry in \
    "${run_dir}/frozen/scripts/compose_new_nic_r0_acceptance.py:${expected_composer_sha}" \
    "${run_dir}/frozen/hft_mgbs/new_nic_r0.py:${expected_evaluator_sha}" \
    "${run_dir}/frozen/configs/new_nic_r0_campaign_contract_v1.json:${expected_contract_sha}" \
    "${run_dir}/frozen/scripts/run_new_nic_r0_campaign.sh:${expected_runner_sha}"; do
    artifact="${entry%:*}"; expected="${entry##*:}"
    is_sha "${expected}" && [[ -f "${artifact}" && ! -L "${artifact}" \
      && "$(sha_file "${artifact}")" == "${expected}" ]] || {
      echo "frozen core artifact drifted before COMPOSE" >&2; exit 74; }
  done
  set +e
  PYTHONPATH= "${python_bin}" "${run_dir}/frozen/scripts/compose_new_nic_r0_acceptance.py" \
    --artifact-root "${run_dir}" \
    --manifest "${run_dir}/evidence.manifest.json" \
    --trusted-manifest-sha256 "${trusted_evidence_manifest_sha}" \
    --output "${run_dir}/r0_audit.json"
  rc="$?"
  set -e
  atomic_state "$("${python_bin}" -c 'import json,sys;print(json.load(open(sys.argv[1], encoding="utf-8"))["status"])' "${run_dir}/r0_audit.json")" true
  exit "${rc}"
fi

[[ "${phase}" == "EXECUTE" ]] || { echo "invalid HFT_NEW_NIC_R0_PHASE" >&2; exit 74; }
if [[ "${authorization}" != "I_AUTHORIZE_NEW_NIC_R0_MUTATION" \
   || "${maintenance_window}" != "YES" \
   || ! "${change_ticket}" =~ ^[A-Za-z0-9._:-]{4,128}$ ]]; then
  echo "EXECUTE requires exact authorization, maintenance window, and change ticket" >&2
  exit 74
fi
if [[ ! -f "${helper_manifest}" || -L "${helper_manifest}" ]] \
  || ! is_sha "${trusted_helper_manifest_sha}" \
  || [[ "$(sha_file "${helper_manifest}")" != "${trusted_helper_manifest_sha}" ]]; then
  echo "helper manifest does not match the external trusted SHA-256" >&2
  exit 74
fi
if [[ ! -f "${execution_plan}" || -L "${execution_plan}" ]] \
  || ! is_sha "${trusted_execution_plan_sha}" \
  || [[ "$(sha_file "${execution_plan}")" != "${trusted_execution_plan_sha}" ]]; then
  echo "execution plan does not match the external trusted SHA-256" >&2
  exit 74
fi
if [[ -z "${trust_root_receipt}" ]]; then
  echo "EXECUTE requires an explicit external trust-root receipt path" >&2
  exit 75
fi
evidence_root_resolved="$(cd "${evidence_root}" && pwd -P)"
trust_root_parent="$(cd "$(dirname "${trust_root_receipt}")" && pwd -P)" || exit 75
trust_root_receipt="${trust_root_parent}/$(basename "${trust_root_receipt}")"
case "${trust_root_receipt}" in "${evidence_root_resolved}"/*) echo "trust root must be outside evidence root" >&2; exit 75;; esac
[[ ! -e "${trust_root_receipt}" && ! -L "${trust_root_receipt}" ]] || {
  echo "trust-root receipt path must be new" >&2; exit 75; }

timestamp="$(date -u +%Y%m%dT%H%M%S%NZ)"
run_dir="$(mktemp -d "${evidence_root}/hft_new_nic_r0_${timestamp}_XXXXXX")"
frozen_helper_manifest="${run_dir}/frozen_helper_manifest.txt"
cp --no-preserve=mode,ownership,timestamps -- "${helper_manifest}" "${frozen_helper_manifest}"
chmod 0400 "${frozen_helper_manifest}"
[[ "$(sha_file "${frozen_helper_manifest}")" == "${trusted_helper_manifest_sha}" ]] || exit 74

required_roles=(contract runner composer evaluator xdp_runner dpdk_runner generator_runner resource_sampler fallback_orchestrator restore_helper campaign_executor trust_root_recorder)
executable_roles=(runner composer xdp_runner dpdk_runner generator_runner resource_sampler fallback_orchestrator restore_helper campaign_executor trust_root_recorder)
mkdir -p "${run_dir}/frozen/scripts" "${run_dir}/frozen/hft_mgbs" "${run_dir}/frozen/configs"
for role in "${required_roles[@]}"; do
  source_path="$(manifest_field "${role}" 2)"
  expected_sha="$(manifest_field "${role}" 3)"
  is_sha "${expected_sha}" || { echo "invalid ${role} manifest SHA" >&2; exit 74; }
  [[ -f "${source_path}" && ! -L "${source_path}" && "$(sha_file "${source_path}")" == "${expected_sha}" ]] || {
    echo "${role} failed initial hash gate" >&2; exit 74; }
  case "${role}" in
    contract) destination="${run_dir}/frozen/configs/new_nic_r0_campaign_contract_v1.json" ;;
    evaluator) destination="${run_dir}/frozen/hft_mgbs/new_nic_r0.py" ;;
    composer) destination="${run_dir}/frozen/scripts/compose_new_nic_r0_acceptance.py" ;;
    runner) destination="${run_dir}/frozen/scripts/run_new_nic_r0_campaign.sh" ;;
    *) destination="${run_dir}/frozen/${role}" ;;
  esac
  cp --no-preserve=mode,ownership,timestamps -- "${source_path}" "${destination}"
  [[ "$(sha_file "${destination}")" == "${expected_sha}" ]] || exit 74
done
frozen_execution_plan="${run_dir}/frozen/configs/new_nic_r0_execution_plan_v1.json"
cp --no-preserve=mode,ownership,timestamps -- "${execution_plan}" "${frozen_execution_plan}"
[[ "$(sha_file "${frozen_execution_plan}")" == "${trusted_execution_plan_sha}" ]] || exit 74
printf '%s\n' "${trusted_execution_plan_sha}" > "${run_dir}/execution_plan.sha256"
chmod 0400 "${frozen_execution_plan}" "${run_dir}/execution_plan.sha256"
printf '' > "${run_dir}/frozen/hft_mgbs/__init__.py"
for role in "${executable_roles[@]}"; do
  case "${role}" in
    composer) path="${run_dir}/frozen/scripts/compose_new_nic_r0_acceptance.py" ;;
    runner) path="${run_dir}/frozen/scripts/run_new_nic_r0_campaign.sh" ;;
    *) path="${run_dir}/frozen/${role}" ;;
  esac
  chmod 0500 "${path}"
done
chmod 0400 "${run_dir}/frozen/configs/new_nic_r0_campaign_contract_v1.json" \
  "${run_dir}/frozen/hft_mgbs/new_nic_r0.py" "${run_dir}/frozen/hft_mgbs/__init__.py"
frozen_path_for_role() {
  case "$1" in
    contract) printf '%s\n' "${run_dir}/frozen/configs/new_nic_r0_campaign_contract_v1.json" ;;
    evaluator) printf '%s\n' "${run_dir}/frozen/hft_mgbs/new_nic_r0.py" ;;
    composer) printf '%s\n' "${run_dir}/frozen/scripts/compose_new_nic_r0_acceptance.py" ;;
    runner) printf '%s\n' "${run_dir}/frozen/scripts/run_new_nic_r0_campaign.sh" ;;
    *) printf '%s\n' "${run_dir}/frozen/$1" ;;
  esac
}
verify_frozen_role() {
  local role="$1" path expected
  path="$(frozen_path_for_role "${role}")"
  expected="$(manifest_field "${role}" 3)"
  is_sha "${expected}" && [[ -f "${path}" && ! -L "${path}" \
    && "$(sha_file "${path}")" == "${expected}" ]]
}
verify_all_frozen_artifacts() {
  local role
  for role in "${required_roles[@]}"; do verify_frozen_role "${role}" || return 1; done
}
verify_execution_plan() {
  [[ -f "${frozen_execution_plan}" && ! -L "${frozen_execution_plan}" \
    && -f "${run_dir}/execution_plan.sha256" && ! -L "${run_dir}/execution_plan.sha256" \
    && "$(cat "${run_dir}/execution_plan.sha256")" == "${trusted_execution_plan_sha}" \
    && "$(sha_file "${frozen_execution_plan}")" == "${trusted_execution_plan_sha}" ]]
}
verify_all_frozen_artifacts || { echo "frozen artifacts drifted before arrival gate" >&2; exit 74; }
verify_execution_plan || { echo "frozen execution plan drifted before arrival gate" >&2; exit 74; }

# Bind a previously completed arrival-capability run before any R0 mutation.
# The exact checksum-list hash must have been recorded outside that run.
if [[ -z "${arrival_evidence_dir}" || ! -d "${arrival_evidence_dir}" \
   || -z "${arrival_evidence_manifest}" || ! -f "${arrival_evidence_manifest}" \
   || -L "${arrival_evidence_manifest}" || ! "${trusted_arrival_manifest_sha}" =~ ^[0-9a-f]{64}$ \
   || "$(sha_file "${arrival_evidence_manifest}")" != "${trusted_arrival_manifest_sha}" ]]; then
  echo "externally rooted arrival evidence is required before EXECUTE" >&2
  exit 75
fi
"${python_bin}" - "${arrival_evidence_dir}" "${arrival_evidence_manifest}" \
  "${trusted_arrival_manifest_sha}" "${run_dir}" <<'PY'
import hashlib, json, math, os, pathlib, re, shutil, stat, sys, tempfile
root = pathlib.Path(sys.argv[1]).resolve(strict=True)
manifest = pathlib.Path(sys.argv[2]).resolve(strict=True)
trusted = sys.argv[3]
destination = pathlib.Path(sys.argv[4]).resolve(strict=True)
if manifest.is_symlink() or not re.fullmatch(r"[0-9a-f]{64}", trusted):
    raise SystemExit("invalid arrival trust root")
if hashlib.sha256(manifest.read_bytes()).hexdigest() != trusted:
    raise SystemExit("arrival manifest trust root mismatch")
try:
    manifest.relative_to(root)
except ValueError:
    raise SystemExit("arrival manifest is outside its evidence root")
entries = {}
for line in manifest.read_text(encoding="utf-8").splitlines():
    match = re.fullmatch(r"([0-9a-f]{64}) [ *](.+)", line)
    if not match or match.group(2) in entries:
        raise SystemExit("malformed or duplicate arrival manifest entry")
    relative = pathlib.PurePosixPath(match.group(2))
    if relative.is_absolute() or ".." in relative.parts:
        raise SystemExit("unsafe arrival artifact path")
    path = root.joinpath(*relative.parts)
    if path.is_symlink() or not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
        raise SystemExit("arrival artifact is not a regular non-symlink file")
    if hashlib.sha256(path.read_bytes()).hexdigest() != match.group(1):
        raise SystemExit("arrival artifact hash mismatch")
    entries[match.group(2)] = (match.group(1), path)
required = {"inventory.probes.json", "preflight.probes.json"}
if not required <= set(entries):
    raise SystemExit("arrival capability artifacts are incomplete")
def no_duplicate(pairs):
    result = {}
    for key, value in pairs:
        if key in result: raise ValueError("duplicate JSON key")
        result[key] = value
    return result
def nonfinite(value): raise ValueError("non-finite JSON")
def read_json(path):
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate,
                       parse_constant=nonfinite)
    if not isinstance(value, dict): raise ValueError("JSON object required")
    return value
inventory = read_json(entries["inventory.probes.json"][1])
preflight = read_json(entries["preflight.probes.json"][1])
canonical = json.dumps(inventory, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False).encode("utf-8")
if not (preflight.get("status") == "self_consistent_capability_receipts_only"
        and preflight.get("hardware_present") is True
        and preflight.get("self_consistent_capability_receipts_valid") is True
        and preflight.get("production_qualified") is False
        and preflight.get("inventory_sha256") == hashlib.sha256(canonical).hexdigest()):
    raise SystemExit("arrival preflight is not capability-ready")
copies = {
    "arrival_inventory.json": entries["inventory.probes.json"][1],
    "arrival_preflight.json": entries["preflight.probes.json"][1],
    "arrival_evidence_manifest.sha256": manifest,
}
hash_lines = []
for name, source in copies.items():
    target = destination / name
    handle = tempfile.NamedTemporaryFile("wb", dir=str(destination), prefix=name + ".", delete=False)
    with handle:
        handle.write(source.read_bytes()); handle.flush(); os.fsync(handle.fileno())
    pathlib.Path(handle.name).replace(target)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    hash_lines.append("{}  {}".format(digest, name))
(destination / "arrival_binding.sha256").write_text("\n".join(hash_lines) + "\n", encoding="utf-8")
PY
chmod 0400 "${run_dir}/arrival_inventory.json" "${run_dir}/arrival_preflight.json" \
  "${run_dir}/arrival_evidence_manifest.sha256" "${run_dir}/arrival_binding.sha256"

mutations_started=0
restore_succeeded=false
restoration_verified=false
final_status=99
finalize() {
  local observed="$?"
  trap - EXIT
  trap '' HUP INT TERM
  if ((mutations_started == 1)) && { [[ "${restore_succeeded}" != true ]] \
    || [[ "${restoration_verified}" != true ]]; }; then
    set +e
    if verify_frozen_role restore_helper; then
      timeout --signal=TERM --kill-after=15s "${restore_timeout_s}s" \
        "${run_dir}/frozen/restore_helper" --mode restore --execution-plan "${frozen_execution_plan}" \
        --change-ticket "${change_ticket}" --run-dir "${run_dir}"
      restore_rc="$?"
    else
      restore_rc=98
    fi
    set -e
    if [[ "${restore_rc}" -eq 0 ]] && verify_frozen_role restore_helper \
      && "${run_dir}/frozen/restore_helper" --mode snapshot-after \
        --change-ticket "${change_ticket}" --run-dir "${run_dir}" \
        --output "${run_dir}/restoration_after.json" \
      && verify_restoration_files "${run_dir}/restoration_before.json" \
        "${run_dir}/restoration_after.json" \
        "${run_dir}/frozen/configs/new_nic_r0_campaign_contract_v1.json"; then
      restore_succeeded=true
      restoration_verified=true
    fi
    if [[ "${restore_succeeded}" != true || "${restoration_verified}" != true ]]; then final_status=97; fi
  fi
  [[ "${final_status}" -ne 99 ]] || final_status="${observed}"
  atomic_state "$([[ "${final_status}" -eq 21 ]] && echo evidence_pending || echo execution_failed)" \
    "$([[ "${mutations_started}" -eq 1 ]] && echo true || echo false)"
  if ((mutations_started == 1)) && { [[ "${restore_succeeded}" != true ]] \
    || [[ "${restoration_verified}" != true ]]; }; then
    printf '%s\n' "restore_failed rc=${final_status}" > "${run_dir}/RECOVERY_REQUIRED"
    sync "${run_dir}/RECOVERY_REQUIRED"
  fi
  exit "${final_status}"
}
trap finalize EXIT
trap 'final_status=129; exit 129' HUP
trap 'final_status=130; exit 130' INT
trap 'final_status=143; exit 143' TERM

atomic_state authorized_not_started false
verify_all_frozen_artifacts || exit 74
verify_execution_plan || exit 74
"${run_dir}/frozen/restore_helper" --mode snapshot-before --execution-plan "${frozen_execution_plan}" \
  --change-ticket "${change_ticket}" --run-dir "${run_dir}" \
  --output "${run_dir}/restoration_before.json"
mutations_started=1
atomic_state executing true
verify_all_frozen_artifacts || exit 98
"${run_dir}/frozen/campaign_executor" \
  --contract "${run_dir}/frozen/configs/new_nic_r0_campaign_contract_v1.json" \
  --execution-plan "${frozen_execution_plan}" \
  --xdp-runner "${run_dir}/frozen/xdp_runner" \
  --dpdk-runner "${run_dir}/frozen/dpdk_runner" \
  --generator-runner "${run_dir}/frozen/generator_runner" \
  --resource-sampler "${run_dir}/frozen/resource_sampler" \
  --fallback-orchestrator "${run_dir}/frozen/fallback_orchestrator" \
  --arrival-evidence-manifest-sha256 "${trusted_arrival_manifest_sha}" \
  --change-ticket "${change_ticket}" --run-dir "${run_dir}" \
  --packet-size 64 --offered-mpps 12 --duration-seconds 15 \
  --xdp-repeats 3 --dpdk-repeats 3 --fallback-trials 3
(cd "${run_dir}" && sha256sum -c arrival_binding.sha256)
verify_all_frozen_artifacts || exit 98
verify_execution_plan || exit 98
timeout --signal=TERM --kill-after=15s "${restore_timeout_s}s" \
  "${run_dir}/frozen/restore_helper" --mode restore --execution-plan "${frozen_execution_plan}" \
  --change-ticket "${change_ticket}" --run-dir "${run_dir}"
restore_succeeded=true
verify_all_frozen_artifacts || exit 98
"${run_dir}/frozen/restore_helper" --mode snapshot-after --execution-plan "${frozen_execution_plan}" \
  --change-ticket "${change_ticket}" --run-dir "${run_dir}" \
  --output "${run_dir}/restoration_after.json"
if verify_restoration_files "${run_dir}/restoration_before.json" \
  "${run_dir}/restoration_after.json" \
  "${run_dir}/frozen/configs/new_nic_r0_campaign_contract_v1.json"; then
  restoration_verified=true
else
  restore_succeeded=false
  final_status=97
  exit 97
fi

# The campaign executor must emit all raw JSON receipts plus campaign.json;
# arrival inventory/preflight were externally rooted before mutation. Build a deterministic
# manifest whose role/path/hash identity is independently recorded next.
"${python_bin}" - "${run_dir}" <<'PY'
import hashlib, json, os, pathlib, sys, tempfile
root = pathlib.Path(sys.argv[1]).resolve()
roles = {
    "campaign": "campaign.json",
    "arrival_inventory": "arrival_inventory.json",
    "arrival_preflight": "arrival_preflight.json",
    "arrival_evidence_manifest": "arrival_evidence_manifest.sha256",
    "execution_plan": "frozen/configs/new_nic_r0_execution_plan_v1.json",
    "execution_plan_binding": "execution_plan.sha256",
    "restoration_before": "restoration_before.json",
    "restoration_after": "restoration_after.json",
    **{"xdp_run_{}".format(i): "xdp_run_{}.json".format(i) for i in (1,2,3)},
    **{"dpdk_run_{}".format(i): "dpdk_run_{}.json".format(i) for i in (1,2,3)},
    **{"fallback_trial_{}".format(i): "fallback_trial_{}.json".format(i) for i in (1,2,3)},
    "contract": "frozen/configs/new_nic_r0_campaign_contract_v1.json",
    "runner": "frozen/scripts/run_new_nic_r0_campaign.sh",
    "composer": "frozen/scripts/compose_new_nic_r0_acceptance.py",
    "evaluator": "frozen/hft_mgbs/new_nic_r0.py",
    **{name: "frozen/" + name for name in (
        "xdp_runner", "dpdk_runner", "generator_runner", "resource_sampler",
        "fallback_orchestrator", "restore_helper", "campaign_executor",
        "trust_root_recorder")},
}
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
artifacts = []
for role, relative in sorted(roles.items()):
    path = root / relative
    if not path.is_file() or path.is_symlink():
        raise SystemExit("missing regular campaign artifact: " + role)
    artifacts.append({"role": role, "path": relative, "sha256": digest(path)})
campaign = json.loads((root / "campaign.json").read_text(encoding="utf-8"))
value = {"schema_version": 1, "scope": "new_nic_r0_artifact_manifest",
         "campaign_id": campaign["campaign_id"], "artifacts": artifacts}
target = root / "evidence.manifest.json"
handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n",
    dir=str(root), prefix="evidence.manifest.", suffix=".tmp", delete=False)
with handle:
    json.dump(value, handle, ensure_ascii=False, sort_keys=True, allow_nan=False)
    handle.write("\n"); handle.flush(); os.fsync(handle.fileno())
pathlib.Path(handle.name).replace(target)
PY

manifest_sha="$(sha_file "${run_dir}/evidence.manifest.json")"
verify_all_frozen_artifacts || exit 98
trust_root_receipt_parent="$(cd "$(dirname "${trust_root_receipt}")" && pwd -P)"
trust_root_receipt="${trust_root_receipt_parent}/$(basename "${trust_root_receipt}")"
case "${trust_root_receipt}" in "${run_dir}"/*) echo "trust root may not live in campaign directory" >&2; exit 96;; esac
"${run_dir}/frozen/trust_root_recorder" \
  --change-ticket "${change_ticket}" --campaign-dir "${run_dir}" \
  --manifest "${run_dir}/evidence.manifest.json" --sha256 "${manifest_sha}" \
  --output "${trust_root_receipt}"
[[ -f "${trust_root_receipt}" && ! -L "${trust_root_receipt}" \
  && "$(awk 'NF == 1 {print $1}' "${trust_root_receipt}")" == "${manifest_sha}" ]] || exit 96
sync "${run_dir}/evidence.manifest.json" "${trust_root_receipt}"
printf '%s\n' "${manifest_sha}" > "${run_dir}/execution_complete.tmp"
mv "${run_dir}/execution_complete.tmp" "${run_dir}/execution_complete"
sync "${run_dir}/execution_complete"
final_status=21
echo "evidence_dir=${run_dir}"
echo "trusted_evidence_manifest_sha256=${manifest_sha}"
echo "external_trust_root_receipt=${trust_root_receipt}"
exit 21
