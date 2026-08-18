#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/jmhIcoding/splitpcap.git"
UPSTREAM_COMMIT="fca18e270fe49d0cf1ba37ffd2bab901a797401a"
DESTINATION="${1:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/tools/splitpcap-fca18e270fe4}"
PATCHER="${2:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/patch_splitpcap_upstream.py}"
PYTHON_BINARY="${PYTHON_BINARY:-/opt/data/private/wangwt/anaconda3/envs/py3.9/bin/python}"
BUILD_ROOT="${DESTINATION}.build"

rm -rf -- "${BUILD_ROOT}"
mkdir -p "${BUILD_ROOT}" "${DESTINATION}/bin"
git clone --no-checkout "${UPSTREAM_URL}" "${BUILD_ROOT}/source"
git -C "${BUILD_ROOT}/source" checkout --detach "${UPSTREAM_COMMIT}"
ACTUAL_COMMIT="$(git -C "${BUILD_ROOT}/source" rev-parse HEAD)"
test "${ACTUAL_COMMIT}" = "${UPSTREAM_COMMIT}"
"${PYTHON_BINARY}" "${PATCHER}" "${BUILD_ROOT}/source"
make -C "${BUILD_ROOT}/source" -j4
install -m 0755 "${BUILD_ROOT}/source/splitpcap" "${DESTINATION}/bin/splitpcap"
git -C "${BUILD_ROOT}/source" diff -- src/main.cpp > "${DESTINATION}/splitpcap-caeos-safety.patch"
sha256sum "${DESTINATION}/bin/splitpcap" "${DESTINATION}/splitpcap-caeos-safety.patch" > "${DESTINATION}/SHA256SUMS"
printf '%s\n' "${UPSTREAM_URL}" > "${DESTINATION}/UPSTREAM_URL"
printf '%s\n' "${UPSTREAM_COMMIT}" > "${DESTINATION}/UPSTREAM_COMMIT"
rm -rf -- "${BUILD_ROOT}"
"${DESTINATION}/bin/splitpcap" || test "$?" -ne 0
