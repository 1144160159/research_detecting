#!/usr/bin/env bash
set -euo pipefail

# Default operation is a read-only plan compilation.  Execution writes only to
# the contract-bound GPU campaign result root and requires three exact gates.

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(cd -- "${script_dir}/.." && pwd -P)"
contract="${HFT_ALGORITHM_CAMPAIGN_CONTRACT:-${repo_root}/configs/algorithm_qualification_campaign_v1.json}"
python_bin="${HFT_ALGORITHM_CAMPAIGN_PYTHON:-python3}"
execute="${HFT_ALGORITHM_CAMPAIGN_EXECUTE:-NO}"
authorization="${HFT_ALGORITHM_CAMPAIGN_AUTHORIZATION:-}"
trusted_contract_sha="${HFT_ALGORITHM_CAMPAIGN_TRUSTED_CONTRACT_SHA256:-}"

if [[ "${execute}" != "YES" ]]; then
  "${python_bin}" -I -S -B "${repo_root}/scripts/prepare_algorithm_campaign.py" \
    --repo-root "${repo_root}" \
    --contract "${contract}"
  exit "$?"
fi

if [[ "${authorization}" != "APPROVED_BOUNDED_A01_A10_QUALIFICATION" ]]; then
  echo "exact bounded-campaign authorization is missing" >&2
  exit 90
fi
if [[ -n "${HFT_ALGORITHM_CAMPAIGN_PYTHON+x}" ]]; then
  echo "formal execution forbids HFT_ALGORITHM_CAMPAIGN_PYTHON override" >&2
  exit 91
fi
bootstrap_python="/usr/bin/python3"
if [[ ! -x "${bootstrap_python}" ]]; then
  echo "fixed bootstrap Python is unavailable" >&2
  exit 91
fi
python_bin="${bootstrap_python}"
if [[ ! "${trusted_contract_sha}" =~ ^[0-9a-f]{64}$ ]]; then
  echo "trusted contract SHA-256 is missing or malformed" >&2
  exit 91
fi
actual_contract_sha="$("${bootstrap_python}" -I -S -B - "${contract}" <<'PY'
import hashlib, os, pathlib, stat, sys
path = pathlib.Path(sys.argv[1])
flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
descriptor = os.open(str(path), flags)
try:
    before = os.fstat(descriptor)
    if not stat.S_ISREG(before.st_mode):
        raise SystemExit("contract is not regular")
    digest = hashlib.sha256()
    size = 0
    while True:
        chunk = os.read(descriptor, 1024 * 1024)
        if not chunk:
            break
        size += len(chunk)
        digest.update(chunk)
    after = os.fstat(descriptor)
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns) or size != before.st_size:
        raise SystemExit("contract changed during hashing")
    print(digest.hexdigest())
finally:
    os.close(descriptor)
PY
)"
if [[ "${actual_contract_sha}" != "${trusted_contract_sha}" ]]; then
  echo "campaign contract does not match the externally supplied trust root" >&2
  exit 92
fi

mapfile -t execution_fields < <(
  "${python_bin}" -I -S -B - "${contract}" <<'PY'
import json, pathlib, sys
value = json.loads(pathlib.Path(sys.argv[1]).read_text("utf-8"))["execution"]
for name in (
    "gpu_project_root",
    "gpu_code_root",
    "gpu_campaign_result_root",
    "python_executable",
    "environment_prefix",
):
    item = value[name]
    if not isinstance(item, str) or not item or any(c in item for c in "\r\n\0"):
        raise SystemExit("invalid execution field: " + name)
    print(item)
PY
)
if [[ "${#execution_fields[@]}" -ne 5 ]]; then
  echo "could not read the contract-bound GPU execution roots" >&2
  exit 93
fi
gpu_project_root="${execution_fields[0]}"
gpu_code_root="${execution_fields[1]}"
campaign_result_root="${execution_fields[2]}"
target_python="${execution_fields[3]}"
environment_prefix="${execution_fields[4]}"

if [[ "${repo_root}" != "${gpu_code_root}" ]]; then
  echo "authorized execution is restricted to the contract-bound GPU code root" >&2
  exit 94
fi
case "${campaign_result_root}" in
  "${gpu_project_root}"/*) ;;
  *)
    echo "campaign result root escapes the GPU project root" >&2
    exit 95
    ;;
esac
case "${target_python}" in
  "${environment_prefix}"/*) ;;
  *)
    echo "contract-bound Python executable escapes the environment prefix" >&2
    exit 96
    ;;
esac
if [[ ! -x "${target_python}" || ! -d "${environment_prefix}" ]]; then
  echo "contract-bound Python executable or environment prefix is unavailable" >&2
  exit 96
fi
target_python_bootstrap_sha="$("${bootstrap_python}" -I -S -B - \
  "${target_python}" "${environment_prefix}" <<'PY'
import hashlib, os, pathlib, stat, sys
executable = pathlib.Path(os.path.abspath(sys.argv[1]))
prefix = pathlib.Path(os.path.abspath(sys.argv[2]))
if pathlib.Path(os.path.realpath(str(prefix))) != prefix:
    raise SystemExit("environment prefix contains a symlink or alias")
prefix_status = os.lstat(str(prefix))
if not stat.S_ISDIR(prefix_status.st_mode) or stat.S_ISLNK(prefix_status.st_mode):
    raise SystemExit("environment prefix is not a real directory")
if pathlib.Path(os.path.realpath(str(executable))) != executable:
    raise SystemExit("target Python contains a symlink or alias")
try:
    executable.relative_to(prefix)
except ValueError:
    raise SystemExit("target Python escapes environment prefix")
flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
descriptor = os.open(str(executable), flags)
try:
    before = os.fstat(descriptor)
    if not stat.S_ISREG(before.st_mode):
        raise SystemExit("target Python is not regular")
    digest = hashlib.sha256()
    size = 0
    while True:
        chunk = os.read(descriptor, 1024 * 1024)
        if not chunk:
            break
        digest.update(chunk)
        size += len(chunk)
    after = os.fstat(descriptor)
finally:
    os.close(descriptor)
current = os.lstat(str(executable))
identity = lambda value: (
    value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns
)
if identity(before) != identity(after) or identity(after) != identity(current) or size != before.st_size:
    raise SystemExit("target Python changed during bootstrap hashing")
print(digest.hexdigest())
PY
)"
if [[ ! "${target_python_bootstrap_sha}" =~ ^[0-9a-f]{64}$ ]]; then
  echo "could not bootstrap the target Python identity" >&2
  exit 96
fi

campaign_run_id="${HFT_ALGORITHM_CAMPAIGN_RUN_ID:-algorithm_qualification_$(date -u +%Y%m%dT%H%M%SZ)}"
case "${campaign_run_id}" in
  ""|*[!A-Za-z0-9_.-]*)
    echo "unsafe campaign run ID" >&2
    exit 97
    ;;
esac
campaign_root="${campaign_result_root}/${campaign_run_id}"
ensure_real_directory() {
  local path="$1"
  if [[ ! -e "${path}" && ! -L "${path}" ]]; then
    mkdir -- "${path}"
  fi
  if [[ -L "${path}" || ! -d "${path}" ]]; then
    echo "campaign path is not a real directory: ${path}" >&2
    return 1
  fi
  local physical
  physical="$(cd -- "${path}" && pwd -P)"
  if [[ "${physical}" != "${path}" ]]; then
    echo "campaign path contains a symlink or lexical alias: ${path}" >&2
    return 1
  fi
}
ensure_real_directory "${gpu_project_root}"
ensure_real_directory "${campaign_result_root}"
lock_root="/tmp/hft_algorithm_campaign_locks"
effective_uid="$(id -u)"
if [[ ! -d "/" || -L "/" || ! -d "/tmp" || -L "/tmp" ]]; then
  echo "campaign lock parent chain is not composed of real directories" >&2
  exit 98
fi
case "$(stat -f -c %T -- "/tmp")" in
  nfs|nfs4)
    echo "campaign lock parent must not use NFS" >&2
    exit 98
    ;;
esac
umask 077
if [[ ! -e "${lock_root}" && ! -L "${lock_root}" ]]; then
  mkdir -m 0700 -- "${lock_root}"
fi
if [[ ! -d "${lock_root}" || -L "${lock_root}" ]]; then
  echo "campaign lock root is not a real directory: ${lock_root}" >&2
  exit 98
fi
case "$(stat -f -c %T -- "${lock_root}")" in
  nfs|nfs4)
    echo "campaign lock root must not use NFS" >&2
    exit 98
    ;;
esac
lock_root_uid="$(stat -c %u -- "${lock_root}")"
lock_root_mode="$(stat -c %a -- "${lock_root}")"
if [[ "${lock_root_uid}" != "${effective_uid}" || "${lock_root_mode}" != "700" ]]; then
  echo "campaign lock root owner or mode is unsafe" >&2
  exit 98
fi
lock_path="${lock_root}/${campaign_run_id}.lock"
if [[ ! -e "${lock_path}" && ! -L "${lock_path}" ]]; then
  if ! (set -o noclobber; : > "${lock_path}") 2>/dev/null; then
    echo "could not create campaign lock file safely: ${lock_path}" >&2
    exit 98
  fi
fi
if [[ -L "${lock_path}" || ! -f "${lock_path}" ]]; then
  echo "campaign lock file is not a regular non-symlink: ${lock_path}" >&2
  exit 98
fi
lock_file_uid="$(stat -c %u -- "${lock_path}")"
lock_file_mode="$(stat -c %a -- "${lock_path}")"
lock_file_links="$(stat -c %h -- "${lock_path}")"
lock_file_identity="$(stat -c %d:%i -- "${lock_path}")"
if [[ "${lock_file_uid}" != "${effective_uid}" || "${lock_file_mode}" != "600" \
  || "${lock_file_links}" != "1" ]]; then
  echo "campaign lock file owner or mode is unsafe" >&2
  exit 98
fi
exec 9<> "${lock_path}"
if ! flock -n 9; then
  echo "another process owns the campaign lock: ${lock_path}" >&2
  exit 98
fi
lock_fd_identity="$(stat -L -c %d:%i -- "/proc/self/fd/9")"
lock_fd_links="$(stat -L -c %h -- "/proc/self/fd/9")"
lock_path_identity="$(stat -c %d:%i -- "${lock_path}")"
if [[ "${lock_fd_identity}" != "${lock_file_identity}" \
  || "${lock_path_identity}" != "${lock_file_identity}" \
  || "${lock_fd_links}" != "1" || -L "${lock_path}" || ! -f "${lock_path}" ]]; then
  echo "campaign lock file identity changed while acquiring the lock" >&2
  exit 98
fi
truncate -s 0 -- "/proc/self/fd/9"
printf 'pid=%s\ncampaign_root=%s\ncontract_sha256=%s\n' \
  "$$" "${campaign_root}" "${actual_contract_sha}" >&9
ensure_real_directory "${campaign_root}"
ensure_real_directory "${campaign_root}/runs"
ensure_real_directory "${campaign_root}/results"
ensure_real_directory "${campaign_root}/receipts"

safe_capture_output() {
  local target="$1"
  local merge_stderr="$2"
  shift 2
  "${bootstrap_python}" -I -S -B - "${campaign_root}" "${target}" \
    "${merge_stderr}" "$@" <<'PY'
import os, pathlib, secrets, stat, subprocess, sys

root = pathlib.Path(sys.argv[1])
target = pathlib.Path(sys.argv[2])
merge = sys.argv[3] == "YES"
command = sys.argv[4:]
root_real = pathlib.Path(os.path.realpath(str(root)))
parent = target.parent
parent_real = pathlib.Path(os.path.realpath(str(parent)))
try:
    parent_real.relative_to(root_real)
except ValueError:
    raise SystemExit("safe output escapes campaign root")
if parent_real != pathlib.Path(os.path.abspath(str(parent))):
    raise SystemExit("safe output parent contains a symlink or alias")
if not parent.is_dir():
    raise SystemExit("safe output parent is missing")

def identity(path):
    try:
        value = os.lstat(str(path))
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(value.st_mode) or value.st_nlink != 1:
        raise SystemExit("safe output target is not a single-link regular file")
    return (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)

before = identity(target)
temporary = parent / ("." + target.name + ".tmp." + secrets.token_hex(16))
flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
descriptor = os.open(str(temporary), flags, 0o600)
try:
    with os.fdopen(descriptor, "wb", closefd=True) as handle:
        completed = subprocess.run(
            command,
            stdout=handle,
            stderr=subprocess.STDOUT if merge else None,
            check=False,
        )
        handle.flush()
        os.fsync(handle.fileno())
    if completed.returncode:
        os.unlink(str(temporary))
        raise SystemExit(completed.returncode)
    if identity(target) != before:
        os.unlink(str(temporary))
        raise SystemExit("safe output target changed before publish")
    os.replace(str(temporary), str(target))
    directory_fd = os.open(str(parent), os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
except BaseException:
    try:
        os.unlink(str(temporary))
    except FileNotFoundError:
        pass
    raise
PY
}

status_path="${campaign_root}/execution_status.json"
write_status() {
  local status="$1"
  local exit_code="$2"
  safe_capture_output "${status_path}" NO "${python_bin}" -I -S -B -c '
import datetime, json, sys
payload = {
    "schema_version": 1,
    "scope": "hft_mgbs_algorithm_campaign_execution_status_v1",
    "campaign_run_id": sys.argv[1],
    "status": sys.argv[2],
    "exit_code": int(sys.argv[3]),
    "updated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "source_algorithm_search_modified": False,
    "raw_results_remain_on_gpu": True,
    "production_joint_optimum_proven": False,
    "final_pareto_ingestion_allowed": False,
}
print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
' "${campaign_run_id}" "${status}" "${exit_code}"
}
strict_json_valid() {
  local path="$1"
  "${python_bin}" -I -S -B - "${path}" <<'PY'
import json, pathlib, sys
def duplicate(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate JSON key: " + key)
        out[key] = value
    return out
def constant(value):
    raise ValueError("non-finite JSON number: " + value)
raw = pathlib.Path(sys.argv[1]).read_bytes()
if raw.startswith(b"\xef\xbb\xbf"):
    raise SystemExit(1)
json.loads(
    raw.decode("utf-8", errors="strict"),
    object_pairs_hook=duplicate,
    parse_constant=constant,
)
PY
}
stable_sha256() {
  "${bootstrap_python}" -I -S -B - "$1" <<'PY'
import hashlib, pathlib, sys
digest = hashlib.sha256()
with pathlib.Path(sys.argv[1]).open("rb") as handle:
    while True:
        chunk = handle.read(1024 * 1024)
        if not chunk:
            break
        digest.update(chunk)
print(digest.hexdigest())
PY
}

pycache_prefix="${campaign_root}/empty_pycache"
ensure_real_directory "${pycache_prefix}"
"${bootstrap_python}" -I -S -B -c '
import os, pathlib, stat, sys
path = pathlib.Path(sys.argv[1])
if pathlib.Path(os.path.realpath(str(path))) != pathlib.Path(os.path.abspath(str(path))):
    raise SystemExit("pycache prefix contains a symlink or alias")
value = os.lstat(str(path))
if not stat.S_ISDIR(value.st_mode) or list(path.iterdir()):
    raise SystemExit("pycache prefix is not an empty real directory")
' "${pycache_prefix}"

runtime_bootstrap_identity="${campaign_root}/runtime_bootstrap_identity.json"
runtime_bootstrap_verify="${campaign_root}/runtime_bootstrap_identity.verify.json"
capture_runtime_bootstrap_identity() {
  local output="$1"
  safe_capture_output "${output}" NO "${target_python}" -I -S -B -c '
import hashlib, json, os, pathlib, sys, sysconfig
prefix = pathlib.Path(os.path.realpath(sys.prefix))
executable = pathlib.Path(os.path.realpath(sys.executable))
if str(prefix) != sys.argv[1] or str(executable) != sys.argv[2]:
    raise SystemExit("formal runtime path does not match the contract")
if hashlib.sha256(executable.read_bytes()).hexdigest() != sys.argv[3]:
    raise SystemExit("formal runtime does not match the bootstrap identity")
if sys.version_info[:2] != (3, 9):
    raise SystemExit("formal runtime is not Python 3.9")
paths = sysconfig.get_paths()
site_packages = []
for name in ("purelib", "platlib"):
    value = pathlib.Path(os.path.realpath(paths[name]))
    try:
        value.relative_to(prefix)
    except ValueError:
        raise SystemExit("Conda site-packages escapes prefix")
    if not value.is_dir():
        raise SystemExit("Conda site-packages is missing")
    text = str(value)
    if text not in site_packages:
        site_packages.append(text)
print(json.dumps({
    "schema_version": 1,
    "scope": "hft_mgbs_stdlib_bound_python_runtime_v1",
    "prefix": str(prefix),
    "executable": str(executable),
    "executable_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
    "site_packages": site_packages,
}, ensure_ascii=False, indent=2, sort_keys=True))
' "${environment_prefix}" "${target_python}" "${target_python_bootstrap_sha}"
}
if [[ -e "${runtime_bootstrap_identity}" || -L "${runtime_bootstrap_identity}" ]]; then
  capture_runtime_bootstrap_identity "${runtime_bootstrap_verify}"
  cmp -s -- "${runtime_bootstrap_identity}" "${runtime_bootstrap_verify}" || exit 99
  rm -f -- "${runtime_bootstrap_verify}"
else
  capture_runtime_bootstrap_identity "${runtime_bootstrap_identity}"
fi
runtime_bootstrap_identity_sha="$(stable_sha256 "${runtime_bootstrap_identity}")"

bound_python_launcher='import hashlib, importlib.machinery, importlib.util, json, os, pathlib, runpy, stat, sys, sysconfig
repo = pathlib.Path(sys.argv[1])
script = pathlib.Path(sys.argv[2])
runtime_path = pathlib.Path(sys.argv[3])
cache = pathlib.Path(sys.argv[4])
binding_path = pathlib.Path(sys.argv[5])
script_arguments = sys.argv[6:]

def real_regular(path, label):
    absolute = pathlib.Path(os.path.abspath(str(path)))
    resolved = pathlib.Path(os.path.realpath(str(path)))
    if absolute != resolved:
        raise SystemExit(label + " contains a symlink or alias")
    value = os.lstat(str(path))
    if not stat.S_ISREG(value.st_mode):
        raise SystemExit(label + " is not regular")
    return resolved

def canonical(path):
    return os.path.normcase(os.path.realpath(os.path.abspath(str(path))))

runtime_file = real_regular(runtime_path, "runtime identity")
runtime = json.loads(runtime_file.read_text("utf-8"))
if set(runtime) != {"schema_version", "scope", "prefix", "executable", "executable_sha256", "site_packages"}:
    raise SystemExit("runtime identity fields drift")
if runtime["schema_version"] != 1 or runtime["scope"] != "hft_mgbs_stdlib_bound_python_runtime_v1":
    raise SystemExit("runtime identity scope drift")
prefix = pathlib.Path(os.path.realpath(sys.prefix))
executable = pathlib.Path(os.path.realpath(sys.executable))
if str(prefix) != runtime["prefix"] or str(executable) != runtime["executable"]:
    raise SystemExit("runtime executable or prefix drift")
if hashlib.sha256(executable.read_bytes()).hexdigest() != runtime["executable_sha256"]:
    raise SystemExit("runtime executable hash drift")
paths = sysconfig.get_paths()
site_packages = []
for name in ("purelib", "platlib"):
    value = pathlib.Path(os.path.realpath(paths[name]))
    try:
        value.relative_to(prefix)
    except ValueError:
        raise SystemExit("runtime site-packages escapes prefix")
    text = str(value)
    if text not in site_packages:
        site_packages.append(text)
if site_packages != runtime["site_packages"]:
    raise SystemExit("runtime site-packages drift")
cache = pathlib.Path(os.path.abspath(str(cache)))
if pathlib.Path(os.path.realpath(str(cache))) != cache:
    raise SystemExit("pycache prefix contains a symlink or alias")
cache_status = os.lstat(str(cache))
if not stat.S_ISDIR(cache_status.st_mode) or list(cache.iterdir()):
    raise SystemExit("pycache prefix is not empty")
sys.pycache_prefix = str(cache)
stdlib_paths = []
for raw in sys.path:
    if not raw:
        raise SystemExit("isolated runtime contains an empty import path")
    resolved = pathlib.Path(os.path.realpath(raw))
    try:
        resolved.relative_to(prefix)
    except ValueError:
        raise SystemExit("isolated stdlib path escapes runtime prefix")
    if str(resolved) in site_packages:
        raise SystemExit("site-packages was loaded before the bound launcher")
    if raw not in stdlib_paths:
        stdlib_paths.append(raw)
repo = pathlib.Path(os.path.abspath(str(repo)))
if pathlib.Path(os.path.realpath(str(repo))) != repo or not repo.is_dir():
    raise SystemExit("repository root contains a symlink or alias")
script = real_regular(script, "bound script")
binding = json.loads(real_regular(binding_path, "binding manifest").read_text("utf-8"))
artifacts = binding["bound_repository_artifacts"]
allowed = {}
module_sources = {}
for item in artifacts.values():
    relative = item["path"]
    pure = pathlib.PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or str(pure) != relative:
        raise SystemExit("bound artifact path is unsafe")
    source = real_regular(repo.joinpath(*pure.parts), "bound artifact")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    source_identity = canonical(source)
    if digest != item["sha256"] or source_identity in allowed:
        raise SystemExit("bound artifact identity drift")
    allowed[source_identity] = digest
    if relative.endswith(".py") and relative.split("/", 1)[0] in ("hft_mgbs", "scripts", "tests"):
        module = relative[:-3].replace("/", ".")
        is_package = module.endswith(".__init__")
        if is_package:
            module = module[:-9]
        if not all(part.isidentifier() for part in module.split(".")):
            raise SystemExit("bound Python module name is invalid")
        if module in module_sources:
            raise SystemExit("bound module identity collision")
        module_sources[module] = (source, digest, is_package)
if canonical(script) not in allowed:
    raise SystemExit("executed script is not contract-bound")
namespace_packages = {}
for module_name, (source, _digest, _is_package) in module_sources.items():
    parts = module_name.split(".")
    for length in range(1, len(parts)):
        parent = ".".join(parts[:length])
        if parent not in module_sources:
            directory = repo.joinpath(*parts[:length])
            previous = namespace_packages.get(parent)
            if previous is not None and canonical(previous) != canonical(directory):
                raise SystemExit("bound namespace package identity collision")
            namespace_packages[parent] = directory
protected_roots = {name.split(".", 1)[0] for name in module_sources}
sys.path[:] = stdlib_paths + site_packages
if "site" in sys.modules or "sitecustomize" in sys.modules or "usercustomize" in sys.modules:
    raise SystemExit("site initialization is forbidden")

class BoundSourceLoader:
    def __init__(self, fullname, source, digest, is_package):
        self.fullname = fullname
        self.source = source
        self.digest = digest
        self.package = is_package
    def create_module(self, spec):
        return None
    def exec_module(self, module):
        raw = self.source.read_bytes()
        if hashlib.sha256(raw).hexdigest() != self.digest:
            raise ImportError("bound module changed before execution: " + self.fullname)
        module.__file__ = str(self.source)
        module.__cached__ = None
        code = compile(raw, str(self.source), "exec", dont_inherit=True)
        exec(code, module.__dict__)

class BoundSourceFinder:
    def find_spec(self, fullname, path=None, target=None):
        root_name = fullname.split(".", 1)[0]
        if root_name not in protected_roots:
            return None
        if fullname in module_sources:
            source, digest, is_package = module_sources[fullname]
            loader = BoundSourceLoader(fullname, source, digest, is_package)
            locations = [str(source.parent)] if is_package else None
            return importlib.util.spec_from_file_location(
                fullname, str(source), loader=loader,
                submodule_search_locations=locations,
            )
        if fullname in namespace_packages:
            spec = importlib.machinery.ModuleSpec(fullname, loader=None, is_package=True)
            spec.submodule_search_locations = [str(namespace_packages[fullname])]
            return spec
        raise ImportError("unbound repository namespace module import: " + fullname)

sys.meta_path.insert(0, BoundSourceFinder())
sys.argv = [str(script)] + script_arguments
exit_code = 0
try:
    runpy.run_path(str(script), run_name="__main__")
except SystemExit as error:
    exit_code = error.code
finally:
    for name, module in sorted(sys.modules.items()):
        source = getattr(module, "__file__", None)
        if name in namespace_packages:
            if source is not None or list(getattr(module, "__path__", [])) != [str(namespace_packages[name])]:
                raise SystemExit("repository namespace package identity drift: " + name)
            continue
        if name.split(".", 1)[0] in protected_roots and name not in module_sources:
            raise SystemExit("unbound repository namespace module was imported: " + name)
        if source is None:
            continue
        resolved = canonical(source)
        try:
            inside_repo = os.path.commonpath((canonical(repo), resolved)) == canonical(repo)
        except ValueError:
            inside_repo = False
        if inside_repo:
            if resolved not in allowed:
                raise SystemExit("imported repository module is outside exact allow-set: " + name + ":" + resolved)
            if hashlib.sha256(pathlib.Path(source).read_bytes()).hexdigest() != allowed[resolved]:
                raise SystemExit("imported repository module hash drift: " + name)
if exit_code not in (0, None):
    raise SystemExit(exit_code)
'
bound_python_cmd=(
  "${target_python}" -I -S -B -c "${bound_python_launcher}" "${repo_root}"
)
simple_checkpoint_valid() {
  local output="$1"
  local checkpoint="$2"
  [[ -f "${output}" && -f "${checkpoint}" ]] || return 1
  strict_json_valid "${output}" || return 1
  (
    cd -- "$(dirname -- "${output}")"
    sha256sum -c --status "${checkpoint}"
  )
}
run_atomic_json() {
  local output="$1"
  local checkpoint="$2"
  local force="$3"
  local runner_args_sha="$4"
  shift 4
  verify_execution_identity
  if [[ "${force}" != "YES" ]] \
    && checkpoint_valid "${output}" "${checkpoint}" "${runner_args_sha}"; then
    verify_execution_identity
    return 10
  fi
  safe_replaceable_regular_or_missing "${output}"
  safe_replaceable_regular_or_missing "${checkpoint}"
  if ! safe_capture_output "${output}" NO "$@"; then
    return 1
  fi
  if ! strict_json_valid "${output}"; then
    return 1
  fi
  verify_execution_identity
  local digest
  digest="$(stable_sha256 "${output}")"
  safe_capture_output "${checkpoint}" NO "${python_bin}" -I -S -B -c '
import json, pathlib, sys
payload = {
    "schema_version": 1,
    "scope": "hft_mgbs_algorithm_repeat_checkpoint_v1",
    "output_path": str(pathlib.Path(sys.argv[1]).absolute()),
    "output_sha256": sys.argv[2],
    "input_manifest_sha256": sys.argv[3],
    "input_stat_manifest_sha256": sys.argv[12],
    "contract_sha256": sys.argv[4],
    "code_manifest_sha256": sys.argv[5],
    "algorithm_search_sha256": sys.argv[6],
    "plan_sha256": sys.argv[7],
    "runner_args_sha256": sys.argv[8],
    "environment_identity_sha256": sys.argv[9],
    "environment_files_manifest_sha256": sys.argv[10],
    "external_tools_manifest_sha256": sys.argv[11],
    "runtime_bootstrap_identity_sha256": sys.argv[13],
}
print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
' "${output}" "${digest}" \
    "${input_sha}" "${actual_contract_sha}" "${code_manifest_sha}" \
    "${algorithm_search_sha}" "${plan_sha}" "${runner_args_sha}" \
    "${environment_identity_sha}" "${environment_files_manifest_sha}" \
    "${external_tools_manifest_sha}" "${input_stat_manifest_sha}" \
    "${runtime_bootstrap_identity_sha}"
  return 0
}
write_job_status() {
  local candidate_id="$1"
  local run_id="$2"
  local state="$3"
  local result_dir="$4"
  local output="${campaign_root}/job_status/${candidate_id}.json"
  ensure_real_directory "${campaign_root}/job_status"
  safe_capture_output "${output}" NO "${python_bin}" -I -S -B -c '
import datetime, hashlib, json, pathlib, re, sys
result_dir = pathlib.Path(sys.argv[4])
records = []
pattern = re.compile(r"^(normal|fallback)_repeat([1-9][0-9]*)\.json$")
if result_dir.is_dir():
    for path in sorted(result_dir.iterdir()):
        match = pattern.fullmatch(path.name)
        if not path.is_file() or match is None:
            continue
        records.append({
            "mode": match.group(1),
            "repeat": int(match.group(2)),
            "path": str(path.resolve()),
            "size_bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        })
payload = {
    "schema_version": 1,
    "scope": "hft_mgbs_algorithm_campaign_job_status_v1",
    "candidate_id": sys.argv[1],
    "run_id": sys.argv[2],
    "status": sys.argv[3],
    "completed_repeat_count": len(records),
    "expected_repeat_count": 6,
    "completed_repeats": records,
    "updated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "counts_toward_campaign": False,
    "production_joint_optimum_proven": False,
    "final_pareto_ingestion_allowed": False,
}
print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
' "${candidate_id}" "${run_id}" "${state}" "${result_dir}"
}
finish_on_error() {
  local rc="$?"
  trap - EXIT INT TERM HUP
  write_status "execution_incomplete" "${rc}" || true
  exit "${rc}"
}
finish_on_signal() {
  local rc="$1"
  trap - EXIT INT TERM HUP
  write_status "execution_incomplete_signal" "${rc}" || true
  exit "${rc}"
}
trap finish_on_error EXIT
trap 'finish_on_signal 129' HUP
trap 'finish_on_signal 130' INT
trap 'finish_on_signal 143' TERM
write_status "preparing" 0

plan="${campaign_root}/plan.json"
legacy_manifest="${campaign_root}/legacy_evidence_discovery.json"
if [[ -f "${plan}" ]]; then
  mapfile -t frozen_plan_fields < <(
    "${bootstrap_python}" -I -S -B - "${plan}" <<'PY'
import json, pathlib, sys
plan = json.loads(pathlib.Path(sys.argv[1]).read_text("utf-8"))
print(plan["campaign_run_id"])
print(plan["created_at_utc"])
PY
  )
  if [[ "${#frozen_plan_fields[@]}" -ne 2 \
    || "${frozen_plan_fields[0]}" != "${campaign_run_id}" ]]; then
    echo "existing campaign plan identity is invalid" >&2
    exit 99
  fi
  plan_check="${campaign_root}/plan.resume-check.json"
  safe_capture_output "${plan_check}" NO \
    "${bound_python_cmd[@]}" "${repo_root}/scripts/prepare_algorithm_campaign.py" \
    "${runtime_bootstrap_identity}" "${pycache_prefix}" "${contract}" \
    --repo-root "${repo_root}" \
    --contract "${contract}" \
    --campaign-run-id "${campaign_run_id}" \
    --created-at-utc "${frozen_plan_fields[1]}"
  if ! cmp -s -- "${plan}" "${plan_check}"; then
    echo "existing campaign plan does not replay from the frozen contract" >&2
    exit 99
  fi
  rm -f -- "${plan_check}"
else
  safe_capture_output "${plan}" NO \
    "${bound_python_cmd[@]}" "${repo_root}/scripts/prepare_algorithm_campaign.py" \
    "${runtime_bootstrap_identity}" "${pycache_prefix}" "${contract}" \
    --repo-root "${repo_root}" \
    --contract "${contract}" \
    --campaign-run-id "${campaign_run_id}"
fi
safe_capture_output "${campaign_root}/legacy_discovery.stdout.json" NO \
  "${bound_python_cmd[@]}" "${repo_root}/scripts/prepare_algorithm_campaign.py" \
  "${runtime_bootstrap_identity}" "${pycache_prefix}" "${contract}" \
  --repo-root "${repo_root}" \
  --contract "${contract}" \
  --campaign-run-id "${campaign_run_id}" \
  --created-at-utc "$("${bootstrap_python}" -I -S -B -c 'import json,sys;print(json.load(open(sys.argv[1],encoding="utf-8"))["created_at_utc"])' "${plan}")" \
  --legacy-evidence-manifest "${legacy_manifest}"

mapfile -t plan_fields < <(
  "${bootstrap_python}" -I -S -B - "${plan}" <<'PY'
import json, pathlib, sys
plan = json.loads(pathlib.Path(sys.argv[1]).read_text("utf-8"))
gpu = plan["gpu_execution"]
protocol = plan["uniform_protocol"]
for value in (
    gpu["training_manifest"],
    gpu["holdout_manifest"],
    plan["algorithm_search"]["path"],
    plan["algorithm_search"]["sha256"],
):
    print(value)
PY
)
if [[ "${#plan_fields[@]}" -ne 4 ]]; then
  echo "compiled campaign plan is missing execution fields" >&2
  exit 99
fi
training_manifest="${plan_fields[0]}"
holdout_manifest="${plan_fields[1]}"
algorithm_search_path="${plan_fields[2]}"
algorithm_search_sha="${plan_fields[3]}"

write_status "freezing_inputs" 0
input_manifest="${campaign_root}/input_sha256.json"
ensure_real_directory "${campaign_root}/checkpoints"
input_checkpoint="${campaign_root}/checkpoints/input_sha256.json.sha256"
for control_path in "${input_manifest}" "${input_checkpoint}"; do
  if [[ -L "${control_path}" ]]; then
    echo "input-freeze control path is a symlink: ${control_path}" >&2
    exit 99
  fi
  if [[ -e "${control_path}" \
    && ( ! -f "${control_path}" || "$(stat -c %h -- "${control_path}")" != "1" ) ]]; then
    echo "input-freeze control path is not a single-link regular file" >&2
    exit 99
  fi
done
if ! simple_checkpoint_valid "${input_manifest}" "${input_checkpoint}"; then
  safe_capture_output "${input_manifest}" NO \
    "${bound_python_cmd[@]}" "${repo_root}/scripts/freeze_input_manifest.py" \
    "${runtime_bootstrap_identity}" "${pycache_prefix}" "${plan}" \
    "${training_manifest}" "${holdout_manifest}" \
    --output /dev/null
  strict_json_valid "${input_manifest}"
  input_digest="$(stable_sha256 "${input_manifest}")"
  safe_capture_output "${campaign_root}/input_hash.stdout.json" NO \
    "${bootstrap_python}" -I -S -B -c 'import pathlib,sys;sys.stdout.buffer.write(pathlib.Path(sys.argv[1]).read_bytes())' \
    "${input_manifest}"
  safe_capture_output "${input_checkpoint}" NO \
    "${bootstrap_python}" -I -S -B -c 'import pathlib,sys;print(sys.argv[1] + "  " + pathlib.Path(sys.argv[2]).name)' \
    "${input_digest}" "${input_manifest}"
fi

input_sha="$(stable_sha256 "${input_manifest}")"
plan_sha="$(stable_sha256 "${plan}")"
code_manifest="${campaign_root}/code_sha256.txt"
code_manifest_check="${campaign_root}/code_sha256.verify.txt"
code_manifest_output="${code_manifest}"
had_code_manifest="NO"
if [[ -e "${code_manifest}" || -L "${code_manifest}" ]]; then
  had_code_manifest="YES"
  code_manifest_output="${code_manifest_check}"
fi
safe_capture_output "${code_manifest_output}" NO "${bootstrap_python}" -I -S -B -c '
import hashlib, json, os, pathlib, stat, sys
plan = json.loads(pathlib.Path(sys.argv[1]).read_text("utf-8"))
root = pathlib.Path(sys.argv[2])
artifacts = plan["bound_repository_artifacts"]
if not artifacts:
    raise SystemExit("code manifest path set is not exact")
for name in sorted(artifacts):
    item = artifacts[name]
    relative = item["path"]
    pure = pathlib.PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or str(pure) != relative:
        raise SystemExit("code manifest path set is not exact")
    path = root.joinpath(*pure.parts)
    current = path
    while True:
        status = os.lstat(str(current))
        if stat.S_ISLNK(status.st_mode):
            raise SystemExit("bound code path contains a symlink: " + relative)
        if current == root:
            break
        current = current.parent
    if not path.is_file():
        raise SystemExit("bound code artifact is not a regular file: " + relative)
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    actual = digest.hexdigest()
    if actual != item["sha256"]:
        raise SystemExit("bound code artifact hash drift: " + relative)
    print("{}  ./{}".format(actual, relative))
' "${plan}" "${repo_root}"
if [[ "${had_code_manifest}" == "YES" ]]; then
  if [[ -L "${code_manifest}" || ! -f "${code_manifest}" \
    || "$(stat -c %h -- "${code_manifest}")" != "1" ]] \
    || ! cmp -s -- "${code_manifest}" "${code_manifest_check}"; then
    echo "existing code manifest is not the exact contract allow-set" >&2
    exit 99
  fi
  rm -f -- "${code_manifest_check}"
fi
code_manifest_sha="$(stable_sha256 "${code_manifest}")"

safe_replaceable_regular_or_missing() {
  local path="$1"
  if [[ -L "${path}" ]]; then
    echo "refusing symlinked campaign output: ${path}" >&2
    return 1
  fi
  if [[ -e "${path}" ]]; then
    if [[ ! -f "${path}" || "$(stat -c %h -- "${path}")" != "1" ]]; then
      echo "campaign output is not a single-link regular file: ${path}" >&2
      return 1
    fi
  fi
}

capture_environment_identity() {
  local output="$1"
  local files_manifest="$2"
  local tools_manifest="$3"
  local runtime_manifest="$4"
  safe_capture_output "${output}" NO "${target_python}" -I -S -B -c '
import hashlib, importlib, json, os, pathlib, platform, stat, sys, sysconfig

def sha256_file(value):
    digest = hashlib.sha256()
    with pathlib.Path(value).open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()

runtime_path = pathlib.Path(sys.argv[3])
runtime_raw = runtime_path.read_bytes()
runtime = json.loads(runtime_raw.decode("utf-8"))
prefix = pathlib.Path(os.path.realpath(sys.prefix))
executable = pathlib.Path(os.path.realpath(sys.executable))
if (runtime.get("scope") != "hft_mgbs_stdlib_bound_python_runtime_v1" or
        runtime.get("prefix") != str(prefix) or
        runtime.get("executable") != str(executable) or
        runtime.get("executable_sha256") != sha256_file(executable)):
    raise SystemExit("runtime bootstrap identity drift")
configured_sites = []
paths = sysconfig.get_paths()
for name in ("purelib", "platlib"):
    value = pathlib.Path(os.path.realpath(paths[name]))
    try:
        value.relative_to(prefix)
    except ValueError:
        raise SystemExit("Conda site-packages escapes prefix")
    text = str(value)
    if text not in configured_sites:
        configured_sites.append(text)
if configured_sites != runtime.get("site_packages"):
    raise SystemExit("runtime site-packages drift")
stdlib_paths = []
for raw in sys.path:
    if not raw:
        raise SystemExit("isolated environment identity contains cwd")
    resolved = pathlib.Path(os.path.realpath(raw))
    try:
        resolved.relative_to(prefix)
    except ValueError:
        raise SystemExit("isolated stdlib path escapes Conda prefix")
    if raw not in stdlib_paths:
        stdlib_paths.append(raw)
cache = pathlib.Path(os.path.abspath(sys.argv[4]))
if pathlib.Path(os.path.realpath(str(cache))) != cache:
    raise SystemExit("environment identity pycache path is unsafe")
cache_status = os.lstat(str(cache))
if not stat.S_ISDIR(cache_status.st_mode) or list(cache.iterdir()):
    raise SystemExit("environment identity pycache path is not empty")
sys.pycache_prefix = str(cache)
sys.path[:] = stdlib_paths + configured_sites
if "sitecustomize" in sys.modules or "usercustomize" in sys.modules:
    raise SystemExit("custom startup module executed")

packages = {}
for name in ("numpy", "scipy", "sklearn", "joblib"):
    module = importlib.import_module(name)
    module_file = pathlib.Path(module.__file__).resolve()
    packages[name] = {
        "version": str(module.__version__),
        "module_file": str(module_file),
        "module_file_sha256": sha256_file(module_file),
    }
python_executable = pathlib.Path(sys.executable).resolve()
if str(prefix) != sys.argv[5] or sha256_file(python_executable) != sys.argv[6]:
    raise SystemExit("environment identity runtime is not contract/bootstrap bound")
files_manifest = pathlib.Path(sys.argv[1])
files_raw = files_manifest.read_bytes()
files_payload = json.loads(files_raw.decode("utf-8"))
tools_manifest = pathlib.Path(sys.argv[2])
tools_raw = tools_manifest.read_bytes()
tools_payload = json.loads(tools_raw.decode("utf-8"))
thread_names = (
    "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS",
    "JOBLIB_TEMP_FOLDER", "PYTHONHASHSEED", "CUDA_VISIBLE_DEVICES",
)
payload = {
    "schema_version": 2,
    "scope": "hft_mgbs_algorithm_campaign_environment_identity_v2",
    "environment_prefix": str(prefix),
    "environment_files_manifest_path": str(files_manifest.resolve()),
    "environment_files_manifest_sha256": hashlib.sha256(files_raw).hexdigest(),
    "environment_files_manifest_entry_count": files_payload["entry_count"],
    "external_tools_manifest_path": str(tools_manifest.resolve()),
    "external_tools_manifest_sha256": hashlib.sha256(tools_raw).hexdigest(),
    "external_tools_manifest_entry_count": tools_payload["entry_count"],
    "runtime_bootstrap_identity_path": str(runtime_path.resolve()),
    "runtime_bootstrap_identity_sha256": hashlib.sha256(runtime_raw).hexdigest(),
    "python": {
        "version": platform.python_version(),
        "implementation": platform.python_implementation(),
        "executable": str(python_executable),
        "executable_sha256": sha256_file(python_executable),
        "site_packages": configured_sites,
    },
    "packages": packages,
    "thread_environment": {name: os.environ.get(name) for name in thread_names},
}
print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
' "${files_manifest}" "${tools_manifest}" "${runtime_manifest}" \
    "${pycache_prefix}" "${environment_prefix}" "${target_python_bootstrap_sha}"
  strict_json_valid "${output}"
}

capture_environment_files_manifest() {
  local output="$1"
  safe_capture_output "${output}" NO "${bootstrap_python}" -I -S -B -c '
import hashlib, json, os, pathlib, stat, sys

prefix = pathlib.Path(os.path.realpath(sys.argv[1]))
root_before = os.lstat(str(prefix))
if not stat.S_ISDIR(root_before.st_mode) or stat.S_ISLNK(root_before.st_mode):
    raise SystemExit("Conda prefix is not a real directory")

def identity(value):
    return (
        value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
        value.st_size, value.st_mtime_ns, value.st_ctime_ns,
    )

def identity_payload(value):
    return {
        "device": value.st_dev, "inode": value.st_ino, "mode": value.st_mode,
        "link_count": value.st_nlink, "size_bytes": value.st_size,
        "mtime_ns": value.st_mtime_ns, "ctime_ns": value.st_ctime_ns,
    }

def digest_regular(target, expected):
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(target), flags)
    digest = hashlib.sha256()
    size = 0
    try:
        before = os.fstat(descriptor)
        if identity(before) != identity(expected) or not stat.S_ISREG(before.st_mode):
            raise SystemExit("Conda environment file identity changed before hashing")
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            digest.update(chunk)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    current = os.lstat(str(target))
    if identity(before) != identity(after) or identity(after) != identity(current) or size != before.st_size:
        raise SystemExit("Conda environment file changed during hashing")
    return size, digest.hexdigest()

def walk_paths():
    collected = []
    def fail(error):
        raise error
    for current, directories, files in os.walk(
        str(prefix), topdown=True, followlinks=False, onerror=fail
    ):
        directories.sort()
        files.sort()
        retained = []
        for name in directories:
            target = pathlib.Path(current) / name
            collected.append(target)
            if not stat.S_ISLNK(os.lstat(str(target)).st_mode):
                retained.append(name)
        directories[:] = retained
        for name in files:
            collected.append(pathlib.Path(current) / name)
    return sorted(collected, key=lambda item: item.relative_to(prefix).as_posix())

entries = []
hashed_bytes = 0
regular_count = symlink_count = directory_count = 0
for target in walk_paths():
    relative = target.relative_to(prefix).as_posix()
    status = os.lstat(str(target))
    entry = {"path": relative}
    entry.update(identity_payload(status))
    if stat.S_ISREG(status.st_mode):
        size, digest = digest_regular(target, status)
        entry.update({"type": "regular", "sha256": digest})
        hashed_bytes += size
        regular_count += 1
    elif stat.S_ISLNK(status.st_mode):
        link_target = os.readlink(str(target))
        if not link_target or "\x00" in link_target or "\n" in link_target or "\r" in link_target:
            raise SystemExit("unsafe Conda symlink target")
        resolved = pathlib.Path(os.path.realpath(str(target)))
        try:
            resolved_relative = resolved.relative_to(prefix).as_posix()
        except ValueError:
            raise SystemExit("Conda symlink escapes environment prefix")
        resolved_status = os.lstat(str(resolved))
        entry.update({
            "type": "symlink",
            "link_target": link_target,
            "resolved_path": resolved_relative,
            "resolved_mode": resolved_status.st_mode,
            "resolved_device": resolved_status.st_dev,
            "resolved_inode": resolved_status.st_ino,
            "resolved_link_count": resolved_status.st_nlink,
            "resolved_size_bytes": resolved_status.st_size,
            "resolved_mtime_ns": resolved_status.st_mtime_ns,
            "resolved_ctime_ns": resolved_status.st_ctime_ns,
        })
        if stat.S_ISREG(resolved_status.st_mode):
            size, digest = digest_regular(resolved, resolved_status)
            entry.update({"resolved_type": "regular", "resolved_sha256": digest})
            hashed_bytes += size
        elif stat.S_ISDIR(resolved_status.st_mode):
            entry["resolved_type"] = "directory"
        else:
            raise SystemExit("unsupported resolved Conda symlink type")
        symlink_count += 1
    elif stat.S_ISDIR(status.st_mode):
        entry["type"] = "directory"
        directory_count += 1
    else:
        raise SystemExit("unsupported Conda environment tree entry type")
    entries.append(entry)
root_after = os.lstat(str(prefix))
if identity(root_before) != identity(root_after):
    raise SystemExit("Conda environment root changed during hashing")
print(json.dumps({
    "schema_version": 4,
    "scope": "hft_mgbs_python_environment_tree_sha256_v4",
    "environment_prefix": str(prefix),
    "root_identity": identity_payload(root_before),
    "entry_count": len(entries),
    "regular_file_count": regular_count,
    "symlink_count": symlink_count,
    "directory_count": directory_count,
    "total_hashed_bytes": hashed_bytes,
    "entries": entries,
}, ensure_ascii=False, indent=2, sort_keys=True))
' "${environment_prefix}"
}

verify_environment_files_fast() {
  "${bootstrap_python}" -I -S -B -c '
import json, os, pathlib, stat, sys
manifest = json.loads(pathlib.Path(sys.argv[1]).read_text("utf-8"))
if manifest.get("schema_version") != 4 or manifest.get("scope") != "hft_mgbs_python_environment_tree_sha256_v4":
    raise SystemExit("environment tree manifest scope drift")
prefix = pathlib.Path(os.path.realpath(manifest["environment_prefix"]))

def identity(value):
    return (
        value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
        value.st_size, value.st_mtime_ns, value.st_ctime_ns,
    )

def expected_identity(value, prefix_name=""):
    return tuple(value[prefix_name + name] for name in (
        "device", "inode", "mode", "link_count", "size_bytes", "mtime_ns", "ctime_ns"
    ))

if identity(os.lstat(str(prefix))) != expected_identity(manifest["root_identity"]):
    raise SystemExit("Conda environment root stat identity drift")

current_paths = []
def fail(error):
    raise error
for current, directories, files in os.walk(str(prefix), topdown=True, followlinks=False, onerror=fail):
    directories.sort()
    files.sort()
    retained = []
    for name in directories:
        target = pathlib.Path(current) / name
        current_paths.append(target)
        if not stat.S_ISLNK(os.lstat(str(target)).st_mode):
            retained.append(name)
    directories[:] = retained
    current_paths.extend(pathlib.Path(current) / name for name in files)
current_paths.sort(key=lambda item: item.relative_to(prefix).as_posix())
current_relatives = [item.relative_to(prefix).as_posix() for item in current_paths]
expected_relatives = [entry["path"] for entry in manifest["entries"]]
if current_relatives != expected_relatives:
    raise SystemExit("Conda environment exact tree path set drift")
for entry in manifest["entries"]:
    target = prefix / entry["path"]
    value = os.lstat(str(target))
    if identity(value) != expected_identity(entry):
        raise SystemExit("Conda environment entry stat identity drift: " + entry["path"])
    expected_type = entry["type"]
    if ((expected_type == "regular" and not stat.S_ISREG(value.st_mode)) or
        (expected_type == "directory" and not stat.S_ISDIR(value.st_mode)) or
        (expected_type == "symlink" and not stat.S_ISLNK(value.st_mode))):
        raise SystemExit("Conda environment entry type drift: " + entry["path"])
    if entry["type"] == "symlink":
        if os.readlink(str(target)) != entry["link_target"]:
            raise SystemExit("Conda environment symlink drift: " + entry["path"])
        resolved = pathlib.Path(os.path.realpath(str(target)))
        try:
            relative = resolved.relative_to(prefix).as_posix()
        except ValueError:
            raise SystemExit("Conda environment symlink escapes prefix")
        if relative != entry["resolved_path"]:
            raise SystemExit("Conda environment symlink resolution drift: " + entry["path"])
        resolved_value = os.lstat(str(resolved))
        if identity(resolved_value) != expected_identity(entry, "resolved_"):
            raise SystemExit("resolved Conda environment entry stat identity drift: " + entry["path"])
' "${environment_files_manifest}"
}

capture_external_tools_manifest() {
  local output="$1"
  shift
  safe_capture_output "${output}" NO "${bootstrap_python}" -I -S -B -c '
import hashlib, json, os, pathlib, sys
arguments = sys.argv[1:]
if len(arguments) % 2:
    raise SystemExit("external tool arguments do not pair")
entries = []
for index in range(0, len(arguments), 2):
    name, invoked = arguments[index:index + 2]
    resolved = pathlib.Path(os.path.realpath(invoked))
    digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
    entries.append({
        "name": name,
        "invoked_path": invoked,
        "resolved_path": str(resolved),
        "sha256": digest,
    })
entries.sort(key=lambda item: item["name"])
print(json.dumps({
    "schema_version": 1,
    "scope": "hft_mgbs_algorithm_campaign_external_tools_v1",
    "entry_count": len(entries),
    "entries": entries,
}, ensure_ascii=False, indent=2, sort_keys=True))
' "$@"
}

environment_identity="${campaign_root}/environment_identity.json"
environment_files_manifest="${campaign_root}/environment_files_sha256.json"
external_tools_manifest="${campaign_root}/external_tools_sha256.json"
environment_verify="${campaign_root}/environment_identity.verify.json"
environment_files_verify="${campaign_root}/environment_files_sha256.verify.json"
external_tools_verify="${campaign_root}/external_tools_sha256.verify.json"
safe_replaceable_regular_or_missing "${environment_identity}"
safe_replaceable_regular_or_missing "${environment_files_manifest}"
safe_replaceable_regular_or_missing "${external_tools_manifest}"

tool_arguments=(python3 "${bootstrap_python}")
for tool_name in bash cmp date dirname find flock id mkdir rm seq sha256sum stat truncate wc; do
  tool_path="$(command -v -- "${tool_name}")"
  if [[ "${tool_path}" != /* ]]; then
    echo "external tool does not resolve to an absolute path: ${tool_name}" >&2
    exit 99
  fi
  tool_arguments+=("${tool_name}" "${tool_path}")
done

if [[ -e "${environment_files_manifest}" ]]; then
  capture_environment_files_manifest "${environment_files_verify}"
  cmp -s -- "${environment_files_manifest}" "${environment_files_verify}" || exit 99
  rm -f -- "${environment_files_verify}"
else
  capture_environment_files_manifest "${environment_files_manifest}"
fi
if [[ -e "${external_tools_manifest}" ]]; then
  capture_external_tools_manifest "${external_tools_verify}" "${tool_arguments[@]}"
  cmp -s -- "${external_tools_manifest}" "${external_tools_verify}" || exit 99
  rm -f -- "${external_tools_verify}"
else
  capture_external_tools_manifest "${external_tools_manifest}" "${tool_arguments[@]}"
fi
if [[ -e "${environment_identity}" ]]; then
  capture_environment_identity "${environment_verify}" \
    "${environment_files_manifest}" "${external_tools_manifest}" \
    "${runtime_bootstrap_identity}"
  cmp -s -- "${environment_identity}" "${environment_verify}" || exit 99
  rm -f -- "${environment_verify}"
else
  capture_environment_identity "${environment_identity}" \
    "${environment_files_manifest}" "${external_tools_manifest}" \
    "${runtime_bootstrap_identity}"
fi
environment_files_manifest_sha="$(stable_sha256 "${environment_files_manifest}")"
external_tools_manifest_sha="$(stable_sha256 "${external_tools_manifest}")"
environment_identity_sha="$(stable_sha256 "${environment_identity}")"

verify_frozen_input_files() {
  "${bootstrap_python}" -I -S -B - "${input_manifest}" "${input_sha}" <<'PY'
import hashlib, json, os, pathlib, stat, sys
manifest = pathlib.Path(sys.argv[1])
raw = manifest.read_bytes()
if hashlib.sha256(raw).hexdigest() != sys.argv[2]:
    raise SystemExit("input manifest identity drift")
payload = json.loads(raw.decode("utf-8"))
entries = payload["entries"]
if payload.get("entry_count") != len(entries) or not entries:
    raise SystemExit("input manifest entry count drift")
seen = set()
for entry in entries:
    path = pathlib.Path(entry["path"])
    absolute = pathlib.Path(os.path.abspath(str(path)))
    if path != absolute or str(path) in seen:
        raise SystemExit("input manifest path set is invalid")
    seen.add(str(path))
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(str(path), flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise SystemExit("frozen input is not a single-link regular file")
        digest = hashlib.sha256()
        size = 0
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            digest.update(chunk)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    identity = lambda value: (
        value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
        value.st_size, value.st_mtime_ns, value.st_ctime_ns,
    )
    if identity(before) != identity(after) or size != before.st_size:
        raise SystemExit("frozen input changed during hashing")
    if size != entry["size_bytes"] or digest.hexdigest() != entry["sha256"]:
        raise SystemExit("frozen input content drift")
PY
}

capture_input_stat_manifest() {
  local output="$1"
  safe_capture_output "${output}" NO "${bootstrap_python}" -I -S -B -c '
import hashlib, json, os, pathlib, stat, sys
source = pathlib.Path(sys.argv[1])
payload = json.loads(source.read_text("utf-8"))
entries = []
for item in payload["entries"]:
    path = pathlib.Path(item["path"])
    value = os.stat(str(path), follow_symlinks=False)
    if not stat.S_ISREG(value.st_mode) or value.st_nlink != 1:
        raise SystemExit("frozen input is not a single-link regular file")
    entries.append({
        "path": str(path.absolute()), "device": value.st_dev,
        "inode": value.st_ino, "mode": value.st_mode,
        "link_count": value.st_nlink, "size_bytes": value.st_size,
        "mtime_ns": value.st_mtime_ns, "ctime_ns": value.st_ctime_ns,
    })
print(json.dumps({
    "schema_version": 1,
    "scope": "hft_mgbs_campaign_input_stat_identity_v1",
    "input_manifest_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "entry_count": len(entries), "entries": entries,
}, ensure_ascii=False, indent=2, sort_keys=True))
' "${input_manifest}"
}

verify_execution_identity() {
  [[ "$(stable_sha256 "${contract}")" == "${actual_contract_sha}" ]]
  [[ "$(stable_sha256 "${plan}")" == "${plan_sha}" ]]
  [[ "$(stable_sha256 "${algorithm_search_path}")" == "${algorithm_search_sha}" ]]
  [[ "$(stable_sha256 "${code_manifest}")" == "${code_manifest_sha}" ]]
  [[ "$(stable_sha256 "${runtime_bootstrap_identity}")" == "${runtime_bootstrap_identity_sha}" ]]
  (
    cd -- "${repo_root}"
    sha256sum -c --status "${code_manifest}"
  )
  capture_runtime_bootstrap_identity "${runtime_bootstrap_verify}"
  cmp -s -- "${runtime_bootstrap_identity}" "${runtime_bootstrap_verify}" || return 1
  rm -f -- "${runtime_bootstrap_verify}"
  verify_environment_files_fast
  capture_external_tools_manifest "${external_tools_verify}" "${tool_arguments[@]}"
  cmp -s -- "${external_tools_manifest}" "${external_tools_verify}" || return 1
  rm -f -- "${external_tools_verify}"
  capture_environment_identity "${environment_verify}" \
    "${environment_files_manifest}" "${external_tools_manifest}" \
    "${runtime_bootstrap_identity}"
  cmp -s -- "${environment_identity}" "${environment_verify}" || return 1
  rm -f -- "${environment_verify}"
  [[ "$(stable_sha256 "${environment_files_manifest}")" == "${environment_files_manifest_sha}" ]]
  [[ "$(stable_sha256 "${external_tools_manifest}")" == "${external_tools_manifest_sha}" ]]
  [[ "$(stable_sha256 "${environment_identity}")" == "${environment_identity_sha}" ]]
  capture_input_stat_manifest "${input_stat_verify}"
  cmp -s -- "${input_stat_manifest}" "${input_stat_verify}" || return 1
  rm -f -- "${input_stat_verify}"
}

hash_argument_vector() {
  "${bootstrap_python}" -I -S -B - "$@" <<'PY'
import hashlib, json, sys
raw = json.dumps(sys.argv[1:], ensure_ascii=False, separators=(",", ":")).encode("utf-8")
print(hashlib.sha256(raw).hexdigest())
PY
}

checkpoint_valid() {
  local output="$1"
  local checkpoint="$2"
  local runner_args_sha="$3"
  safe_replaceable_regular_or_missing "${output}" || return 1
  safe_replaceable_regular_or_missing "${checkpoint}" || return 1
  [[ -f "${output}" && -f "${checkpoint}" ]] || return 1
  strict_json_valid "${output}" || return 1
  strict_json_valid "${checkpoint}" || return 1
  "${bootstrap_python}" -I -S -B - "${output}" "${checkpoint}" "${input_sha}" \
    "${actual_contract_sha}" "${code_manifest_sha}" \
    "${algorithm_search_sha}" "${plan_sha}" "${runner_args_sha}" \
    "${environment_identity_sha}" "${environment_files_manifest_sha}" \
    "${external_tools_manifest_sha}" "${input_stat_manifest_sha}" \
    "${runtime_bootstrap_identity_sha}" <<'PY'
import hashlib, json, pathlib, sys
output = pathlib.Path(sys.argv[1])
checkpoint = json.loads(pathlib.Path(sys.argv[2]).read_text("utf-8"))
expected_keys = {
    "schema_version", "scope", "output_path", "output_sha256",
    "input_manifest_sha256", "contract_sha256", "code_manifest_sha256",
    "algorithm_search_sha256", "plan_sha256", "runner_args_sha256",
    "environment_identity_sha256", "environment_files_manifest_sha256",
    "external_tools_manifest_sha256", "input_stat_manifest_sha256",
    "runtime_bootstrap_identity_sha256",
}
if set(checkpoint) != expected_keys:
    raise SystemExit(1)
expected = {
    "schema_version": 1,
    "scope": "hft_mgbs_algorithm_repeat_checkpoint_v1",
    "output_path": str(output.absolute()),
    "input_manifest_sha256": sys.argv[3],
    "contract_sha256": sys.argv[4],
    "code_manifest_sha256": sys.argv[5],
    "algorithm_search_sha256": sys.argv[6],
    "plan_sha256": sys.argv[7],
    "runner_args_sha256": sys.argv[8],
    "environment_identity_sha256": sys.argv[9],
    "environment_files_manifest_sha256": sys.argv[10],
    "external_tools_manifest_sha256": sys.argv[11],
    "input_stat_manifest_sha256": sys.argv[12],
    "runtime_bootstrap_identity_sha256": sys.argv[13],
}
for name, value in expected.items():
    if checkpoint.get(name) != value:
        raise SystemExit(1)
digest = hashlib.sha256(output.read_bytes()).hexdigest()
if checkpoint.get("output_sha256") != digest:
    raise SystemExit(1)
PY
}

input_stat_manifest="${campaign_root}/input_stat_identity.json"
input_stat_verify="${campaign_root}/input_stat_identity.verify.json"
safe_replaceable_regular_or_missing "${input_stat_manifest}"
verify_frozen_input_files
if [[ -e "${input_stat_manifest}" ]]; then
  capture_input_stat_manifest "${input_stat_verify}"
  cmp -s -- "${input_stat_manifest}" "${input_stat_verify}" || exit 99
  rm -f -- "${input_stat_verify}"
else
  capture_input_stat_manifest "${input_stat_manifest}"
fi
input_stat_manifest_sha="$(stable_sha256 "${input_stat_manifest}")"

verify_execution_identity

safe_capture_output "${campaign_root}/local_policy.stdout.json" NO \
  "${bound_python_cmd[@]}" "${repo_root}/scripts/check_local_policy.py" \
  "${runtime_bootstrap_identity}" "${pycache_prefix}" "${plan}"
safe_capture_output "${campaign_root}/campaign_unit_tests.txt" YES \
  "${bound_python_cmd[@]}" "${repo_root}/tests/test_algorithm_campaign.py" \
  "${runtime_bootstrap_identity}" "${pycache_prefix}" "${plan}" -v

write_status "executing_candidates" 0
while IFS=$'\x1f' read -r candidate_id result_prefix run_tag repeats \
  batch_size budget_us safety_ratio max_train_packets max_train_flows \
  max_test_packets max_test_flows estimators n_jobs key_flow_ratio \
  max_payload_bytes alignment_tolerance_s feature_profile classifier \
  threshold_policy recall_floor calibration_groups adaptation_policy \
  adaptation_groups adaptation_multiplier; do
  [[ -n "${candidate_id}" ]] || continue
  run_id="${result_prefix}_${run_tag}"
  run_dir="${campaign_root}/runs/${run_id}"
  result_dir="${campaign_root}/results/${run_id}"
  checkpoint_dir="${run_dir}/checkpoints"
  ensure_real_directory "${run_dir}"
  ensure_real_directory "${result_dir}"
  ensure_real_directory "${checkpoint_dir}"
  started_path="${run_dir}/started_at.txt"
  if [[ ! -f "${started_path}" ]]; then
    safe_capture_output "${started_path}" NO date -u +%Y-%m-%dT%H:%M:%SZ
  fi
  started_at="$(<"${started_path}")"
  write_job_status "${candidate_id}" "${run_id}" "running" "${result_dir}"

  calibration_args=()
  if [[ -n "${calibration_groups}" ]]; then
    IFS=',' read -r -a calibration_group_names <<< "${calibration_groups}"
    calibration_args+=(--calibration-groups "${calibration_group_names[@]}")
  fi
  adaptation_args=()
  if [[ -n "${adaptation_groups}" ]]; then
    IFS=',' read -r -a adaptation_group_names <<< "${adaptation_groups}"
    adaptation_args+=(--adaptation-groups "${adaptation_group_names[@]}")
  fi
  seeds=(7 11 19)
  job_changed="NO"
  for mode in normal fallback; do
    extra=()
    if [[ "${mode}" == "fallback" ]]; then
      extra+=(--disable-deep)
    fi
    for repeat in $(seq 1 "${repeats}"); do
      seed="${seeds[$((repeat - 1))]}"
      output="${result_dir}/${mode}_repeat${repeat}.json"
      checkpoint="${checkpoint_dir}/${mode}_repeat${repeat}.checkpoint.json"
      eval_cmd=(
        "${bound_python_cmd[@]}"
        "${repo_root}/scripts/evaluate_unsw_independent_holdout.py"
        "${runtime_bootstrap_identity}" "${pycache_prefix}" "${plan}"
        "${training_manifest}" "${holdout_manifest}"
        --batch-size "${batch_size}"
        --budget-us "${budget_us}"
        --execution-budget-safety-ratio "${safety_ratio}"
        --max-train-packets-per-capture "${max_train_packets}"
        --max-train-flows-per-capture "${max_train_flows}"
        --max-test-packets-per-capture "${max_test_packets}"
        --max-test-flows-per-capture "${max_test_flows}"
        --estimators "${estimators}"
        --n-jobs "${n_jobs}"
        --key-flow-ratio "${key_flow_ratio}"
        --max-payload-bytes "${max_payload_bytes}"
        --tolerance-s "${alignment_tolerance_s}"
        --seeds "${seed}"
        --input-hash-manifest "${input_manifest}"
        --threshold-policy "${threshold_policy}"
        --calibration-attack-recall-floor "${recall_floor}"
        --feature-profile "${feature_profile}"
        --classifier "${classifier}"
      )
      eval_cmd+=("${calibration_args[@]}")
      eval_cmd+=(
        --adaptation-policy "${adaptation_policy}"
        --adaptation-weight-multiplier "${adaptation_multiplier}"
      )
      eval_cmd+=("${adaptation_args[@]}")
      eval_cmd+=("${extra[@]}")
      runner_args_sha="$(hash_argument_vector "${eval_cmd[@]}")"
      set +e
      run_atomic_json "${output}" "${checkpoint}" NO \
        "${runner_args_sha}" "${eval_cmd[@]}"
      atomic_rc="$?"
      set -e
      if [[ "${atomic_rc}" -eq 0 ]]; then
        job_changed="YES"
      elif [[ "${atomic_rc}" -ne 10 ]]; then
        echo "candidate ${candidate_id} ${mode} seed ${seed} failed" >&2
        exit "${atomic_rc}"
      fi
      write_job_status "${candidate_id}" "${run_id}" "running" "${result_dir}"
    done
  done

  summary_force="${job_changed}"
  summary_cmd=(
    "${bound_python_cmd[@]}"
    "${repo_root}/scripts/summarize_unsw_holdout.py"
    "${runtime_bootstrap_identity}" "${pycache_prefix}" "${plan}"
    "${result_dir}" --minimum-repeats "${repeats}"
    --algorithm-search "${algorithm_search_path}"
  )
  summary_args_sha="$(hash_argument_vector "${summary_cmd[@]}")"
  set +e
  run_atomic_json "${result_dir}/summary.json" \
    "${checkpoint_dir}/summary.checkpoint.json" "${summary_force}" \
    "${summary_args_sha}" "${summary_cmd[@]}"
  summary_rc="$?"
  set -e
  if [[ "${summary_rc}" -ne 0 && "${summary_rc}" -ne 10 ]]; then
    echo "candidate ${candidate_id} summary failed" >&2
    exit "${summary_rc}"
  fi
  write_job_status "${candidate_id}" "${run_id}" "sealing" "${result_dir}"
  verify_execution_identity
  run_code_manifest="${run_dir}/code_sha256.txt"
  if [[ -e "${run_code_manifest}" || -L "${run_code_manifest}" ]]; then
    if [[ -L "${run_code_manifest}" || ! -f "${run_code_manifest}" \
      || "$(stat -c %h -- "${run_code_manifest}")" != "1" ]] \
      || ! cmp -s -- "${run_code_manifest}" "${code_manifest}"; then
      echo "candidate code manifest is not the exact contract allow-set" >&2
      exit 99
    fi
  else
    if ! safe_capture_output "${run_code_manifest}" NO \
      "${bootstrap_python}" -I -S -B -c \
      'import pathlib,sys;sys.stdout.buffer.write(pathlib.Path(sys.argv[1]).read_bytes())' \
      "${code_manifest}"; then
      echo "could not create candidate code manifest safely" >&2
      exit 99
    fi
  fi
  safe_capture_output "${run_dir}/result_sha256.txt" NO "${bootstrap_python}" -I -S -B -c '
import hashlib, pathlib, sys
root = pathlib.Path(sys.argv[1])
for path in sorted(item for item in root.iterdir() if item.is_file()):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    print("{}  {}".format(digest, path))
' "${result_dir}"
  safe_capture_output "${run_dir}/manifest.txt" NO "${bootstrap_python}" -I -S -B -c '
import datetime, pathlib, sys
names = (
    "run_id", "training_manifest", "holdout_manifest", "input_hash_manifest",
    "input_hash_manifest_sha256", "input_stat_manifest_sha256", "repeats",
    "contract_sha256", "code_manifest_sha256", "environment_identity_sha256",
    "environment_files_manifest_sha256", "external_tools_manifest_sha256",
    "runtime_bootstrap_identity_sha256",
    "max_train_packets_per_capture", "max_train_flows_per_capture",
    "max_test_packets_per_capture", "max_test_flows_per_capture", "estimators",
    "n_jobs", "key_flow_ratio", "max_payload_bytes", "alignment_tolerance_s",
    "batch_size", "budget_us", "execution_budget_safety_ratio",
    "threshold_policy", "calibration_groups", "calibration_attack_recall_floor",
    "feature_profile", "classifier", "adaptation_policy", "adaptation_groups",
    "adaptation_weight_multiplier", "started_at", "status", "ended_at",
    "result_dir", "result_count",
)
values = sys.argv[1:]
if len(values) != len(names):
    raise SystemExit("manifest argument count drift")
for name, value in zip(names, values):
    if "\n" in value or "\r" in value:
        raise SystemExit("unsafe manifest value")
    print(name + "=" + value)
' "${run_id}" "${training_manifest}" "${holdout_manifest}" "${input_manifest}" \
    "${input_sha}" "${input_stat_manifest_sha}" "${repeats}" "${actual_contract_sha}" \
    "${code_manifest_sha}" "${environment_identity_sha}" \
    "${environment_files_manifest_sha}" "${external_tools_manifest_sha}" \
    "${runtime_bootstrap_identity_sha}" \
    "${max_train_packets}" "${max_train_flows}" "${max_test_packets}" \
    "${max_test_flows}" "${estimators}" "${n_jobs}" "${key_flow_ratio}" \
    "${max_payload_bytes}" "${alignment_tolerance_s}" "${batch_size}" \
    "${budget_us}" "${safety_ratio}" "${threshold_policy}" \
    "${calibration_groups}" "${recall_floor}" "${feature_profile}" \
    "${classifier}" "${adaptation_policy}" "${adaptation_groups}" \
    "${adaptation_multiplier}" "${started_at}" complete \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${result_dir}" \
    "$(find "${result_dir}" -type f -name '*_repeat*.json' | wc -l)"
  write_job_status "${candidate_id}" "${run_id}" "complete_unsealed_campaign" "${result_dir}"
done < <(
  "${bootstrap_python}" -I -S -B - "${plan}" <<'PY'
import json, pathlib, sys
separator = "\x1f"
plan = json.loads(pathlib.Path(sys.argv[1]).read_text("utf-8"))
fields = (
    "REPEATS", "BATCH_SIZE", "BUDGET_US", "SAFETY_RATIO",
    "MAX_TRAIN_PACKETS_PER_CAPTURE", "MAX_TRAIN_FLOWS_PER_CAPTURE",
    "MAX_TEST_PACKETS_PER_CAPTURE", "MAX_TEST_FLOWS_PER_CAPTURE",
    "ESTIMATORS", "N_JOBS", "KEY_FLOW_RATIO", "MAX_PAYLOAD_BYTES",
    "ALIGNMENT_TOLERANCE_S",
    "FEATURE_PROFILE", "CLASSIFIER", "THRESHOLD_POLICY",
    "CALIBRATION_ATTACK_RECALL_FLOOR", "CALIBRATION_GROUPS",
    "ADAPTATION_POLICY", "ADAPTATION_GROUPS",
    "ADAPTATION_WEIGHT_MULTIPLIER",
)
for job in plan["jobs"]:
    env = job["runner_environment"]
    values = [job["candidate_id"], job["result_prefix"], job["run_tag"]]
    values.extend(str(env[name]) for name in fields)
    if any(separator in value or "\n" in value or "\r" in value for value in values):
        raise SystemExit("unsafe compiled job field")
    print(separator.join(values))
PY
)

write_status "finalizing" 0
verify_frozen_input_files
capture_environment_files_manifest "${environment_files_verify}"
cmp -s -- "${environment_files_manifest}" "${environment_files_verify}" || exit 99
rm -f -- "${environment_files_verify}"
verify_execution_identity
set +e
safe_capture_output "${campaign_root}/finalize.stdout.json" NO \
  "${bound_python_cmd[@]}" "${repo_root}/scripts/finalize_algorithm_campaign.py" \
  "${runtime_bootstrap_identity}" "${pycache_prefix}" "${plan}" \
  "${campaign_root}" \
  --repo-root "${repo_root}" \
  --contract "${contract}" \
  --trusted-contract-sha256 "${actual_contract_sha}" \
  --output "${campaign_root}/receipts/campaign_receipt.json" \
  --projection-output "${campaign_root}/suggested_algorithm_search_projection.json"
finalize_rc="$?"
set -e

trap - EXIT INT TERM HUP
if [[ "${finalize_rc}" -eq 0 ]]; then
  write_status "completed_accepted_algorithm_only" 0
elif [[ "${finalize_rc}" -eq 2 ]]; then
  write_status "completed_fail_closed" 2
else
  write_status "execution_incomplete" "${finalize_rc}"
fi
exit "${finalize_rc}"
