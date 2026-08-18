#!/usr/bin/env bash
set -euo pipefail

scratch=/tmp/caeos_ciciot2023_duplicate_audit_v2
printf 'UTC=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf 'PROGRESS_FILES\n'
shopt -s nullglob
for path in "${scratch}"/partitions/*/*/progress.json; do
    jq -r '[.contract.shard, .aligned_range_start, .position, .contract.range_end, .rows, .elapsed_seconds] | @tsv' "${path}"
done
printf 'DONE_FILES=' 
find "${scratch}" -name done.json -type f 2>/dev/null | wc -l
du -sh "${scratch}" 2>/dev/null || true
uptime
ps -eo pid,etimes,%cpu,%mem,rss,stat,args \
    | grep audit_caeos_flow_duplicates.py \
    | grep ciciot2023.v2.json \
    | grep -v grep || true
