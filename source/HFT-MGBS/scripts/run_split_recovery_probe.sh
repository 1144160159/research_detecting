#!/usr/bin/env bash
set -euo pipefail

CODE_ROOT="${CODE_ROOT:-/home/wangwt/phase_2/code/HFT-MGBS}"
REPLAY_ROOT="${REPLAY_ROOT:-/home/wangwt/task/datasets/replay}"
LISTEN="${LISTEN:-0.0.0.0:50053}"
MAX_RECOVERY_MS="${MAX_RECOVERY_MS:-300}"
run_id="hft_split_recovery_$(date -u +%Y%m%dT%H%M%S%NZ)"
run_dir="${REPLAY_ROOT}/${run_id}"
output="${run_dir}/recovery.json"
mkdir -p "${run_dir}"

cargo build --release --quiet \
  --manifest-path "${CODE_ROOT}/rust/hft-capture/Cargo.toml" \
  --bin split_recovery_probe
"${CODE_ROOT}/rust/hft-capture/target/release/split_recovery_probe" \
  --listen "${LISTEN}" \
  --output "${output}" \
  --max-recovery-ms "${MAX_RECOVERY_MS}" \
  > "${run_dir}/stdout.json" 2> "${run_dir}/stderr.log"
sha256sum "${output}" "${run_dir}/stdout.json" "${run_dir}/stderr.log" \
  > "${run_dir}/evidence_sha256.txt"
echo "${run_dir}"
