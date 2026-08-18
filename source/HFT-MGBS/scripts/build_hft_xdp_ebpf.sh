#!/usr/bin/env bash
set -euo pipefail

CODE_ROOT="${CODE_ROOT:-/home/wangwt/phase_2/code/HFT-MGBS}"
SOURCE_RELATIVE="rust/hft-capture/ebpf/hft_xdp_redirect.c"
SOURCE="${CODE_ROOT}/${SOURCE_RELATIVE}"
OUTPUT="${CODE_ROOT}/rust/hft-capture/target/hft_xdp_redirect.o"
TEMPORARY="${OUTPUT}.tmp.$$"

for command_name in clang uname; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "required command is unavailable: ${command_name}" >&2
    exit 2
  fi
done
if [[ ! -f "${SOURCE}" ]]; then
  echo "HFT XDP eBPF source is missing: ${SOURCE}" >&2
  exit 2
fi

case "$(uname -m)" in
  x86_64) target_arch=x86 ;;
  aarch64) target_arch=arm64 ;;
  *)
    echo "unsupported eBPF target architecture: $(uname -m)" >&2
    exit 2
    ;;
esac

mkdir -p "$(dirname "${OUTPUT}")"
cleanup() {
  rm -f -- "${TEMPORARY}"
}
trap cleanup EXIT INT TERM

(
  cd "${CODE_ROOT}"
  clang -O2 -g -target bpf \
    -D"__TARGET_ARCH_${target_arch}" \
    -fdebug-prefix-map="${CODE_ROOT}"=. \
    -I/usr/include \
    -I"/usr/include/$(uname -m)-linux-gnu" \
    -c "${SOURCE_RELATIVE}" \
    -o "${TEMPORARY}"
)
mv -f -- "${TEMPORARY}" "${OUTPUT}"
trap - EXIT INT TERM
sha256sum "${OUTPUT}"
