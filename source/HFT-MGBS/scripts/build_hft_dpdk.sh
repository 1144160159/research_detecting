#!/usr/bin/env bash
set -euo pipefail

CODE_ROOT="${CODE_ROOT:-/home/wangwt/phase_2/code/HFT-MGBS}"
DPDK_VERSION="${DPDK_VERSION:-25.11.2}"
DPDK_ROOT="${DPDK_ROOT:-${CODE_ROOT}/.deps/install/dpdk-${DPDK_VERSION}}"
MANIFEST="${CODE_ROOT}/rust/hft-dpdk/Cargo.toml"

for command_name in awk ldd nm; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "required command is unavailable: ${command_name}" >&2
    exit 4
  fi
done
if [[ ! -f "${DPDK_ROOT}/hft-build-manifest.txt" ]]; then
  echo "DPDK bootstrap is missing: ${DPDK_ROOT}" >&2
  exit 4
fi
export PKG_CONFIG_PATH="${DPDK_ROOT}/lib/pkgconfig${PKG_CONFIG_PATH:+:${PKG_CONFIG_PATH}}"
cargo fmt --manifest-path "${MANIFEST}" -- --check
cargo test --manifest-path "${MANIFEST}" --all-targets
cargo clippy --release --all-targets --no-deps --manifest-path "${MANIFEST}" \
  -- -D warnings
cargo build --release --manifest-path "${MANIFEST}"
DPDK_BINARY="${CODE_ROOT}/rust/hft-dpdk/target/release/hft-dpdk"
if ldd "${DPDK_BINARY}" | grep -q 'librte_'; then
  echo "DPDK libraries must be statically linked into ${DPDK_BINARY}" >&2
  exit 9
fi
for required_symbol in rte_pci_bus bnx2x_logtype_driver; do
  if ! nm "${DPDK_BINARY}" \
    | awk -v symbol="${required_symbol}" '$NF == symbol { found = 1 } END { exit !found }'; then
    echo "required static DPDK symbol is missing: ${required_symbol}" >&2
    exit 9
  fi
done
sha256sum "${DPDK_BINARY}"
