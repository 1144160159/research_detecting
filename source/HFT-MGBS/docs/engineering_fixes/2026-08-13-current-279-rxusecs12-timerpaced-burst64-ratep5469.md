# Current 2.79 timer-paced pktgen capacity candidate

## Scope

This is a one-shot capacity diagnostic derived mechanically from the complete
`rx-usecs=12`, fixed64, `ratep=43750` runner. It does not qualify the full
pipeline and it does not authorize a retry or a parameter sweep.

The fixed capture binary remains SHA-256
`6112b2d6be166e7ce0a571727c98baff62524eee760838b2d683add19be8b7ca`.

## Evidence and diagnosis

The equal-rate baseline configured `burst=8`, `clone_skb=64`, and
`ratep=43750`, which Linux 5.10 converts to `delay=22857 ns`. In
`net/core/pktgen.c`, a remaining delay below 100000 ns uses a busy loop. The
run's pktgen CPUs were correspondingly saturated in system time. After the
ninth second, all eight receive workers fell together from about 350 kpps to
about 327 kpps. This was real generator slowdown rather than capture loss or a
clock-window artifact: TX NIC packets, RX NIC packets, and pipeline packets all
equalled 50,321,531; all loss counters, out-of-order counters, realtime clock
step count, and kernel timestamp anomaly count were zero.

The existing evidence has no historical CPU-frequency, thermal, or throttle
trace, so thermal throttling is not claimed as the proven cause. The candidate
tests the narrower supported hypothesis that moving pktgen from the busy-loop
branch to its hrtimer branch avoids sustained generator-core saturation and
the synchronized late-run slowdown.

## Approved single structural change

- `burst`: 8 to 64
- `clone_skb`: 64 to 8, preserving the 512-packet header group
- `ratep`: 43750 to 5469 burst calls per second
- expected Linux 5.10 delay: `floor(1e9 / 5469) = 182848 ns`
- nominal per-queue rate: `5469 * 64 = 350016 pps`
- nominal aggregate rate: `2,800,128 pps`

No `ratep=5600` executable candidate is retained. All other traffic, CPU,
IRQ, NIC, ring, coalescing, pipeline, authorization, restoration, and binary
settings remain unchanged.

## Fail-closed observation contract

Before traffic, all eight pktgen files must report exactly `delay=182848`,
`burst=64`, `clone_skb=8`, the fixed queue map, and the original traffic
profile. After traffic, all eight files must retain those values, report zero
errors, and report 345000 through 355000 pps per queue with aggregate at least
2,790,000 pps.

There must be at least 15 complete one-second windows. Every complete window
must contain at least 2,790,000 received packets. Capture NIC discard delta,
packet-socket drops and freezes, feature and key-feature queue drops, parse
rejects, and all internal loss/error gates must remain zero/true as specified.
Frozen artifact hashes, final evidence manifest verification, and full host
restoration must pass. Any failure stops this candidate; it must not be rerun
with another rate.

The inherited flow-density gate may still fail because this remains the old
`flowlen=36` diagnostic. That failure is reported separately from the capacity
gate and cannot be used to claim that a passing capacity observation failed.

## Executed evidence and disposition

The first authorized attempt is stored at
`/home/wangwt/task/datasets/replay/hft_current_279_tpacket_20260813T151309Z_timerpaced_burst64_ratep5469_capacity_r1`.
It stopped at the pktgen parameter-readback gate before capture or traffic
started because the initial contract rounded `1e9 / 5469` up to `182849 ns`,
while Linux integer division reports `182848 ns`. The runner returned `1`,
sealed the evidence, and restored ring, coalesce, all 16 IRQ affinities,
pktgen, and irqbalance with `restoration_failed=false`. It is retained as a
pre-traffic contract failure and does not count as a capacity run.

After correcting and re-freezing the one-nanosecond contract error, the sole
valid capacity run was executed at
`/home/wangwt/task/datasets/replay/hft_current_279_tpacket_20260813T154636Z_timerpaced_burst64_ratep5469_capacity_r2`.
Its evidence manifest verifies completely. The eight pktgen queues produced
341752 through 342875 pps, for 2738608 pps in aggregate, so the frozen rate
gate rejected the run. The 17 complete receive windows had a minimum of
2.617057 Mpps, a median of 2.774362 Mpps, and a maximum of 2.791930 Mpps;
only five reached 2.79 Mpps. NIC `rx_discards`, packet-socket drops/freezes,
feature/key-feature drops, and parse rejects were all zero. All 50866489
received packets used the fixed parser. The A09 path completed 218 of 218
batches and 1704 of 1704 key flows, with GPU round-trip P99/P999 of
16.596607/18.614589 ms. Host restoration passed with
`restoration_failed=false`.

The result is diagnostic-only: `runtime_identity_verified=false`,
`full_pipeline_qualified=false`, and `final_pareto_ingestion_allowed=false`.
Together with the earlier equal-paced minimum of 2.616893 Mpps, the two
independent pacing mechanisms reproduce the same sustainable lower bound.
The 2.79 Mpps every-window zero-loss target is therefore stopped as NO-GO in
this environment. No second rate or parameter sweep is authorized by this
candidate.

## Static verification

The contract test reverse-derives the runner from its complete baseline and
permits only the approved pacing changes plus the explicit per-second receive
gate. Local unit tests, JSON parsing, shell syntax, frozen hashes, and remote
safety gates must pass before any separately authorized execution.
