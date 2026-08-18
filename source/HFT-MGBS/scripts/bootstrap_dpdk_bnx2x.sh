#!/usr/bin/env bash
set -euo pipefail

CODE_ROOT="${CODE_ROOT:-/home/wangwt/phase_2/code/HFT-MGBS}"
DPDK_VERSION="${DPDK_VERSION:-25.11.2}"
DPDK_MD5="${DPDK_MD5:-a017927310a8a545b6bad8ade8a70c85}"
EXPERIMENTAL_BNX2X_RSS="${HFT_ENABLE_EXPERIMENTAL_BNX2X_RSS:-NO}"
DEPS_ROOT="${DPDK_DEPS_ROOT:-${CODE_ROOT}/.deps}"
CACHE_ROOT="${DEPS_ROOT}/cache"
SOURCE_ROOT="${DEPS_ROOT}/src"
BUILD_ROOT="${DEPS_ROOT}/build/dpdk-${DPDK_VERSION}"
INSTALL_ROOT="${DEPS_ROOT}/install/dpdk-${DPDK_VERSION}"
TOOLS_VENV="${DEPS_ROOT}/tooling"
ARCHIVE="${CACHE_ROOT}/dpdk-${DPDK_VERSION}.tar.xz"
SOURCE_DIR="${SOURCE_ROOT}/dpdk-stable-${DPDK_VERSION}"
PATCH_DIR="${CODE_ROOT}/patches/dpdk-${DPDK_VERSION}"
DOWNLOAD_URL="https://fast.dpdk.org/rel/dpdk-${DPDK_VERSION}.tar.xz"
BOOTSTRAP_LOG="${DEPS_ROOT}/bootstrap-dpdk-${DPDK_VERSION}.log"
BOOTSTRAP_PID="${DEPS_ROOT}/bootstrap-dpdk-${DPDK_VERSION}.pid"

if [[ "${1:-}" == "--detach" ]]; then
  mkdir -p "${DEPS_ROOT}"
  if [[ -f "${BOOTSTRAP_PID}" ]] \
    && kill -0 "$(cat "${BOOTSTRAP_PID}")" 2>/dev/null; then
    echo "DPDK bootstrap already running with PID $(cat "${BOOTSTRAP_PID}")"
    echo "${BOOTSTRAP_LOG}"
    exit 0
  fi
  nohup bash "$0" > "${BOOTSTRAP_LOG}" 2>&1 < /dev/null &
  echo "$!" > "${BOOTSTRAP_PID}"
  echo "DPDK bootstrap started with PID $!"
  echo "${BOOTSTRAP_LOG}"
  exit 0
fi
trap 'rm -f "${BOOTSTRAP_PID}"' EXIT

for command_name in curl md5sum patch python3 sha256sum tar; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "required command is unavailable: ${command_name}" >&2
    exit 4
  fi
done

mkdir -p "${CACHE_ROOT}" "${SOURCE_ROOT}" "$(dirname "${BUILD_ROOT}")" \
  "$(dirname "${INSTALL_ROOT}")"
if [[ ! -x "${TOOLS_VENV}/bin/python" ]]; then
  python3 -m venv "${TOOLS_VENV}"
fi
"${TOOLS_VENV}/bin/python" -m pip install --disable-pip-version-check \
  "meson==1.7.0" "ninja==1.11.1.3" "pyelftools==0.32"

if [[ ! -f "${ARCHIVE}" ]]; then
  curl --fail --location --retry 3 --retry-delay 2 \
    --output "${ARCHIVE}.part" "${DOWNLOAD_URL}"
  mv "${ARCHIVE}.part" "${ARCHIVE}"
fi
echo "${DPDK_MD5}  ${ARCHIVE}" | md5sum --check -

if [[ ! -f "${SOURCE_DIR}/meson.build" ]]; then
  rm -rf "${SOURCE_DIR}"
  tar -xJf "${ARCHIVE}" -C "${SOURCE_ROOT}"
fi
shopt -s nullglob
patch_files=("${PATCH_DIR}"/*.patch)
shopt -u nullglob
if (( ${#patch_files[@]} == 0 )); then
  echo "required DPDK compatibility patches are unavailable: ${PATCH_DIR}" >&2
  exit 5
fi
if [[ "${EXPERIMENTAL_BNX2X_RSS}" == "YES" ]]; then
  for patch_file in "${patch_files[@]}"; do
    if patch --dry-run --silent -d "${SOURCE_DIR}" -p1 < "${patch_file}"; then
      patch --silent -d "${SOURCE_DIR}" -p1 < "${patch_file}"
    elif ! patch --dry-run --silent --reverse -d "${SOURCE_DIR}" -p1 < "${patch_file}"; then
      echo "DPDK compatibility patch is neither applicable nor already applied: ${patch_file}" >&2
      exit 5
    fi
  done
elif [[ "${EXPERIMENTAL_BNX2X_RSS}" == "NO" ]]; then
  for ((index = ${#patch_files[@]} - 1; index >= 0; index--)); do
    patch_file="${patch_files[index]}"
    if patch --dry-run --silent --reverse -d "${SOURCE_DIR}" -p1 < "${patch_file}"; then
      patch --silent --reverse -d "${SOURCE_DIR}" -p1 < "${patch_file}"
    elif ! patch --dry-run --silent -d "${SOURCE_DIR}" -p1 < "${patch_file}"; then
      echo "DPDK source is neither pristine nor the expected experimental state: ${patch_file}" >&2
      exit 5
    fi
  done
else
  echo "HFT_ENABLE_EXPERIMENTAL_BNX2X_RSS must be YES or NO" >&2
  exit 5
fi

export PATH="${TOOLS_VENV}/bin:${PATH}"
meson_args=(
  "--prefix=${INSTALL_ROOT}"
  "--libdir=lib"
  "--buildtype=release"
  "-Dplatform=native"
  "-Dexamples="
  "-Dtests=false"
  "-Dmax_lcores=128"
  "-Dmax_ethports=8"
)
if [[ -f "${BUILD_ROOT}/build.ninja" ]]; then
  meson setup --reconfigure "${BUILD_ROOT}" "${SOURCE_DIR}" "${meson_args[@]}"
else
  meson setup "${BUILD_ROOT}" "${SOURCE_DIR}" "${meson_args[@]}"
fi
ninja -C "${BUILD_ROOT}"
meson install -C "${BUILD_ROOT}"

{
  echo "dpdk_version=${DPDK_VERSION}"
  echo "download_url=${DOWNLOAD_URL}"
  echo "archive_md5=${DPDK_MD5}"
  echo "archive_sha256=$(sha256sum "${ARCHIVE}" | awk '{print $1}')"
  echo "experimental_bnx2x_rss=${EXPERIMENTAL_BNX2X_RSS}"
  for patch_file in "${patch_files[@]}"; do
    echo "compatibility_patch_candidate=$(basename "${patch_file}")"
    echo "compatibility_patch_candidate_sha256=$(sha256sum "${patch_file}" | awk '{print $1}')"
  done
  echo "bnx2x_ethdev_sha256=$(sha256sum "${SOURCE_DIR}/drivers/net/bnx2x/bnx2x_ethdev.c" | awk '{print $1}')"
  echo "source_dir=${SOURCE_DIR}"
  echo "build_dir=${BUILD_ROOT}"
  echo "install_dir=${INSTALL_ROOT}"
  echo "pkg_config_path=${INSTALL_ROOT}/lib/pkgconfig"
  echo "built_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "${INSTALL_ROOT}/hft-build-manifest.txt"
sha256sum "${INSTALL_ROOT}/hft-build-manifest.txt"
echo "${INSTALL_ROOT}"
