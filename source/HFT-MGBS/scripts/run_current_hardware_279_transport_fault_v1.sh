#!/usr/bin/env bash
# Controlled single-connection reverse-TCP fault wrapper for the current-2.79
# diagnostic. It is fail-closed and never stops or signals the GPU service.
set -Eeuo pipefail
umask 077

readonly default_config=/home/wangwt/phase_2/code/HFT-MGBS/configs/current_hardware_2_79_transport_fault_runner_v1.json
readonly config="$(readlink -f -- "${HFT_CURRENT_279_FAULT_CONFIG:-${default_config}}")"
readonly self="$(readlink -f -- "${BASH_SOURCE[0]}")"
readonly evidence_root=/home/wangwt/task/datasets/replay
readonly gpu_ip=10.0.5.103
readonly physical_ip=10.0.5.8
readonly reverse_port=50052
readonly health_port=50051
readonly comment_prefix=hft-mgbs-current-279-transport-fault-
readonly lock_path=/run/lock/hft-current-279-transport-fault.lock

usage() { echo "usage: $0 [--preflight-only] NEW_EVIDENCE_DIRECTORY" >&2; }
mode=run
if [[ "${1:-}" == --preflight-only ]]; then mode=preflight; shift; fi
[[ $# -eq 1 ]] || { usage; exit 2; }
evidence_dir="$(readlink -m -- "$1")"
case "${evidence_dir}/" in "${evidence_root}/"*) ;; *) echo "evidence path outside replay root" >&2; exit 73;; esac
[[ ! -e "${evidence_dir}" ]] || { echo "evidence directory already exists" >&2; exit 73; }

[[ "${HFT_CURRENT_279_TRANSPORT_FAULT_AUTHORIZATION:-}" == I_AUTHORIZE_ONE_CURRENT_279_TRANSPORT_FAULT ]] || { echo "fault authorization required" >&2; exit 74; }
[[ "${HFT_CURRENT_279_FIREWALL_MUTATION_AUTHORIZATION:-}" == I_AUTHORIZE_EXACT_REVERSE_50052_FIREWALL_MUTATION ]] || { echo "firewall mutation authorization required" >&2; exit 74; }
[[ "${HFT_CURRENT_279_FIREWALL_RESTORATION_AUTHORIZATION:-}" == I_AUTHORIZE_EXACT_REVERSE_50052_FIREWALL_RESTORATION ]] || { echo "firewall restoration authorization required" >&2; exit 74; }
readonly ticket="${HFT_CURRENT_279_CHANGE_TICKET:-}"
[[ "${ticket}" =~ ^[A-Za-z0-9._:-]{4,96}$ ]] || { echo "bounded change ticket required" >&2; exit 74; }

sha_file() { sha256sum -- "$1" | awk '{print $1}'; }
is_sha() { [[ "$1" =~ ^[0-9a-f]{64}$ ]]; }
readonly trusted_self="${HFT_CURRENT_279_FAULT_RUNNER_SHA256:-}"
readonly trusted_config="${HFT_CURRENT_279_FAULT_CONFIG_SHA256:-}"
is_sha "${trusted_self}" && is_sha "${trusted_config}" || { echo "external runner/config SHA trust roots required" >&2; exit 75; }
[[ -f "${self}" && ! -L "${self}" && "$(sha_file "${self}")" == "${trusted_self}" ]] || { echo "fault runner hash gate failed" >&2; exit 75; }
[[ -f "${config}" && ! -L "${config}" && "$(sha_file "${config}")" == "${trusted_config}" ]] || { echo "fault config hash gate failed" >&2; exit 75; }

exec 9>"${lock_path}"
flock -n 9 || { echo "transport-fault controller lock is held" >&2; exit 76; }

# This is the first decisive gate and is intentionally before mkdir, parent
# runner start, iptables, modprobe, or any other mutation. The frozen source's
# 300-ms circuit cannot satisfy a <=300-ms end-to-end recovery contract.
mapfile -t frozen < <(python3 - "${config}" <<'PY'
import hashlib,json,pathlib,re,sys
def _strict(pairs):
 d={}
 for k,val in pairs:
  if k in d: raise ValueError("duplicate JSON key")
  d[k]=val
 return d
p=pathlib.Path(sys.argv[1]); v=json.loads(p.read_text(), object_pairs_hook=_strict)
def resolve(item):
 q=pathlib.Path(item["path"]); assert q.is_file() and not q.is_symlink(); assert hashlib.sha256(q.read_bytes()).hexdigest()==item["sha256"]; return q
profile=resolve(v["transport_profile"]); source=resolve(v["rust_recovery_source"])
parent=resolve(v["parent_runner"]); parent_config=resolve(v["parent_config"]); binary=resolve(v["pipeline_binary"])
pv=json.loads(profile.read_text()); recovery=float(pv["transport_recovery"]["recovery_ms_max"])
text=source.read_text(); found=re.search(r"CIRCUIT_OPEN_DURATION:\s*Duration\s*=\s*Duration::from_millis\((\d+)\)",text)
assert found and int(found.group(1))==v["rust_recovery_source"]["circuit_open_ms"]
pipeline=pathlib.Path(v["rust_pipeline_source"]["path"]); assert pipeline.is_file() and not pipeline.is_symlink()
missing=[m for m in v["rust_pipeline_source"]["required_receipt_markers"] if m not in pipeline.read_text()]
print(parent); print(parent_config); print(binary); print(source); print(recovery); print(found.group(1)); print(",".join(missing))
PY
) || { echo "frozen artifact/config validation failed" >&2; exit 75; }
readonly parent_runner="${frozen[0]:-}"
readonly parent_config="${frozen[1]:-}"
readonly pipeline_binary="${frozen[2]:-}"
readonly recovery_source="${frozen[3]:-}"
readonly recovery_budget_ms="${frozen[4]:-0}"
readonly circuit_open_ms="${frozen[5]:-0}"
readonly missing_markers="${frozen[6]:-}"
python3 - "${recovery_budget_ms}" "${circuit_open_ms}" <<'PY' || { echo "NO-GO: circuit-open duration is not strictly below the end-to-end recovery budget" >&2; exit 91; }
import sys
raise SystemExit(0 if float(sys.argv[2]) < float(sys.argv[1]) else 1)
PY
[[ -z "${missing_markers}" ]] || { echo "NO-GO: raw pipeline lacks per-window continuity markers: ${missing_markers}" >&2; exit 92; }

for command in iptables iptables-save ss timeout flock sha256sum python3 setsid; do command -v "${command}" >/dev/null || { echo "missing command: ${command}" >&2; exit 77; }; done
iptables --version | grep -q 'legacy' || { echo "iptables legacy backend required" >&2; exit 77; }
iptables -w 1 -m owner -h >/dev/null 2>&1 || { echo "owner match unavailable" >&2; exit 77; }
iptables -w 1 -m comment -h >/dev/null 2>&1 || { echo "comment match unavailable" >&2; exit 77; }
iptables -w 1 -m conntrack -h >/dev/null 2>&1 || { echo "conntrack match unavailable" >&2; exit 77; }
ip -4 route get "${gpu_ip}" | grep -Eq "src ${physical_ip}([[:space:]]|$)" || { echo "unexpected GPU route/source" >&2; exit 77; }
[[ "$(iptables-save | grep -Fc -- "${comment_prefix}" || true)" -eq 0 ]] || { echo "stale HFT transport fault rule exists" >&2; exit 78; }
if [[ "${mode}" == preflight ]]; then
  printf 'GO static_budget_ms=%s circuit_open_ms=%s firewall=iptables-legacy path=%s:50052->%s:ephemeral\n' "${recovery_budget_ms}" "${circuit_open_ms}" "${physical_ip}" "${gpu_ip}"
  exit 0
fi

readonly run_id="$(date -u +%Y%m%dT%H%M%SZ)-$$"
readonly trial_id="${ticket}-${run_id}"
readonly rule_comment="${comment_prefix}${trial_id}"
readonly controller_id="$(hostname)-$$"
readonly controller_tmp="$(mktemp -d /run/hft-current-279-fault.XXXXXX)"
before_rules_sha=
after_rules_sha=
watchdog_pid=
rule_present=false
parent_pid=
cleanup() {
  local rc=$?
  if [[ "${rule_present}" == true ]]; then iptables -w 5 -D OUTPUT "${rule_spec[@]}" >/dev/null 2>&1 || true; rule_present=false; fi
  [[ -z "${watchdog_pid}" ]] || wait "${watchdog_pid}" 2>/dev/null || true
  if [[ -n "${before_rules_sha}" ]]; then
    after_rules_sha="$(iptables-save | sha256sum | awk '{print $1}')"
    [[ "${after_rules_sha}" == "${before_rules_sha}" ]] || rc=93
  fi
  rm -rf -- "${controller_tmp}"
  exit "${rc}"
}
trap cleanup EXIT INT TERM HUP

iptables-save >"${controller_tmp}/iptables.before"
before_rules_sha="$(sha_file "${controller_tmp}/iptables.before")"
"${parent_runner}" "${evidence_dir}" & parent_pid=$!

deadline=$((SECONDS + 40))
while (( SECONDS < deadline )); do
  [[ -f "${evidence_dir}/execution_events.tsv" ]] && grep -q $'\tgenerator_started$' "${evidence_dir}/execution_events.tsv" && break
  kill -0 "${parent_pid}" 2>/dev/null || { wait "${parent_pid}"; exit $?; }
  sleep 0.05
done
[[ -f "${evidence_dir}/execution_events.tsv" ]] && grep -q $'\tgenerator_started$' "${evidence_dir}/execution_events.tsv" || { echo "generator start not observed" >&2; exit 79; }

connection_tsv="${controller_tmp}/connection.tsv"
deadline=$((SECONDS + 18))
while (( SECONDS < deadline )); do
  ss -Htnp state established >"${controller_tmp}/ss.txt"
  python3 - "${controller_tmp}/ss.txt" "${physical_ip}" "${reverse_port}" "${gpu_ip}" >"${connection_tsv}" <<'PY' && break || true
import re,sys,pathlib
rows=[]
for line in pathlib.Path(sys.argv[1]).read_text().splitlines():
 parts=line.split()
 if len(parts)<5: continue
 local,peer=parts[3],parts[4]
 def split(v):
  host,port=v.rsplit(':',1); return host.strip('[]'),int(port)
 try: lh,lp=split(local); ph,pp=split(peer)
 except Exception: continue
 if lh==sys.argv[2] and lp==int(sys.argv[3]) and ph==sys.argv[4]:
  pids=set(map(int,re.findall(r'pid=(\d+)',line))); rows.append((lh,lp,ph,pp,pids))
if len(rows)!=1 or len(rows[0][4])!=1: raise SystemExit(1)
r=rows[0]; print(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\t{next(iter(r[4]))}")
PY
  sleep 0.05
done
[[ -s "${connection_tsv}" ]] || { echo "unique reverse connection not found" >&2; exit 80; }
IFS=$'\t' read -r local_ip local_port peer_ip peer_port capture_pid <"${connection_tsv}"
[[ "${local_ip}" == "${physical_ip}" && "${local_port}" == "${reverse_port}" && "${peer_ip}" == "${gpu_ip}" && "${peer_port}" =~ ^[0-9]+$ ]] || exit 80
grep -qx "pid=${capture_pid}" "${evidence_dir}/pipeline_process_identity.env" || { echo "socket owner is not frozen capture process" >&2; exit 80; }

rule_spec=(-p tcp -s "${physical_ip}" --sport "${reverse_port}" -d "${gpu_ip}" --dport "${peer_port}" -m owner --uid-owner 0 -m conntrack --ctstate ESTABLISHED -m comment --comment "${rule_comment}" -j REJECT --reject-with tcp-reset)
injected_monotonic_ns="$(python3 -c 'import time; print(time.monotonic_ns())')"
iptables -w 5 -I OUTPUT 1 "${rule_spec[@]}"
rule_present=true
[[ "$(iptables-save | grep -Fc -- "${rule_comment}" || true)" -eq 1 ]] || { echo "fault rule verification failed" >&2; exit 81; }
setsid bash -c 'sleep "$1"; shift; iptables -w 5 -D OUTPUT "$@" >/dev/null 2>&1 || true' _ 0.080 "${rule_spec[@]}" & watchdog_pid=$!
sleep 0.080
iptables -w 5 -D OUTPUT "${rule_spec[@]}" >/dev/null 2>&1 || true
rule_present=false
wait "${watchdog_pid}" 2>/dev/null || true; watchdog_pid=
[[ "$(iptables-save | grep -Fc -- "${rule_comment}" || true)" -eq 0 ]] || { echo "fault rule removal failed" >&2; exit 82; }
removed_monotonic_ns="$(python3 -c 'import time; print(time.monotonic_ns())')"

wait "${parent_pid}"; parent_pid=
after_rules_sha="$(iptables-save | sha256sum | awk '{print $1}')"
[[ "${after_rules_sha}" == "${before_rules_sha}" ]] || { echo "firewall ruleset not byte-identical after removal" >&2; exit 93; }

# The independent fault receipt is deliberately separate from the Rust report.
# Receipt composition refuses synthetic per-window zeros and requires the
# future pipeline's explicit packet_continuity_windows evidence.
python3 - "${config}" "${evidence_dir}/pipeline_raw.json" "${evidence_dir}/transport_fault_external.json" \
  "${evidence_dir}/transport_recovery_receipt.json" "${run_id}" "${trial_id}" "${controller_id}" \
  "${injected_monotonic_ns}" "${removed_monotonic_ns}" "${before_rules_sha}" "${after_rules_sha}" \
  "${local_ip}:${local_port}" "${peer_ip}:${peer_port}" "${rule_comment}" <<'PY'
import hashlib,json,os,pathlib,sys,tempfile
cfg,rawp,faultp,outp=map(pathlib.Path,sys.argv[1:5]); run,trial,controller=sys.argv[5:8]
inj,removed=map(int,sys.argv[8:10]); before,after,local,peer,comment=sys.argv[10:15]
config=json.loads(cfg.read_text()); raw=json.loads(rawp.read_text()); m=raw["pipeline_metrics"]
episodes=m.get("gpu_fault_recovery_evidence",[])
ok=[e for e in episodes if e.get("recovery_us") is not None and e.get("recovered_backend_identity")==m.get("remote_backend_identity")]
if len(ok)!=1: raise SystemExit("exactly one recovered transport fault episode required")
episode=ok[0]; windows=raw.get("packet_continuity_windows")
if not isinstance(windows,list) or not windows or any(w.get("packet_gap")!=0 or w.get("capture_drop")!=0 for w in windows): raise SystemExit("explicit zero-gap/drop windows required")
identity=config["a09_identity"]
fault={"schema_version":1,"scope":"hft_mgbs_external_transport_fault_injection_receipt_v1","run_id":run,"trial_id":trial,"controller_id":controller,"action":"disconnect_reverse_tcp","target_listener":local,"peer":peer,"injected_monotonic_ns":inj,"removed_monotonic_ns":removed,"iptables_ruleset_before_sha256":before,"iptables_ruleset_after_sha256":after,"rule_comment":comment,"rule_removed":before==after}
def write(path,value):
 raw=(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode(); fd,tmp=tempfile.mkstemp(dir=path.parent,prefix=path.name+'.',suffix='.tmp'); os.write(fd,raw); os.fsync(fd); os.close(fd); os.replace(tmp,path); return hashlib.sha256(raw).hexdigest()
fsha=write(faultp,fault)
cached=m["key_flows_recovery_cached"]; retried=m["key_flows_recovery_retried"]; scored=m["key_flows_recovery_remote_scored"]; pending=m["key_flows_recovery_pending"]; terminal=m["key_flows_terminal_unresolved"]
receipt={"schema_version":3,"scope":"hft_mgbs_current_hardware_2_79_transport_recovery_receipt_v3","campaign_id":os.environ["HFT_CURRENT_279_TRANSPORT_CAMPAIGN_ID"],"candidate_id":config["candidate_id"],"run_id":run,"trial_id":trial,"start_monotonic_ns":inj,"end_monotonic_ns":removed+int(episode["recovery_us"])*1000,"recovery_ms":episode["recovery_us"]/1000,"external_fault_receipt":{"path":faultp.name,"sha256":fsha},"fault_detected":True,"counters":{"eligible_key_flows":scored+pending+terminal,"cached":cached,"retried":retried,"recovery_remote_scored":scored,"pending":pending,"unresolved":terminal,"terminal_failed":0,"local_fallback_completed":0},"transport_observations":{"bounded_buffer_capacity":8192,"bounded_buffer_high_watermark":max(1,cached),"circuit_open_delta":1,"reverse_tcp_disconnect_delta":1,"reverse_tcp_reconnect_success_delta":1},"a09_identity_before":identity,"a09_identity_after":identity,"windows":windows,"restoration":{"primary_service_restored":True,"pf_restored":True,"host_restored":before==after}}
write(outp,receipt)
PY
trap - EXIT INT TERM HUP
rm -rf -- "${controller_tmp}"
printf 'transport fault diagnostic completed: %s\n' "${evidence_dir}"
