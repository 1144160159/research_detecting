# Current-hardware 2.79 transport-recovery v3 contract

## Problem

The v2 release profile correctly requires a real local A09 fallback.  The
physical Rust node has no equivalent local A09 model, so a reverse-TCP retry to
the GPU host must not be labelled as local fallback.

## Fix and boundary

An independent v3 evidence contract now covers only bounded buffering, circuit
handling, and reverse-TCP reconnection to the same frozen A09 identity.  It
requires three unique, non-overlapping externally injected trials; positive
cached/retried/remote-scored counters; eligible-flow conservation; zero pending,
unresolved, terminal-failed, packet-gap, and capture-drop counts; recovery within
300 ms; and restoration of the primary service, PFs, and physical host.

The external injection receipt is a separately hashed artifact. Self-reported
step lists, identity drift, local-field forgery, and missing injection hashes
fail closed.

The output always fixes `local_fallback_completed=0`,
`local_quality_qualified=false`, `production_high_availability_qualified=false`,
and `production_pareto_ingestion_allowed=false`. It does not modify or weaken
the old v1/v2 contracts or production Pareto chain.

The independent CLI is `scripts/current_hardware_279_transport_recovery_v3.py`;
it writes the audit atomically and returns `0` only for a qualified transport
recovery campaign (`2` for a fail-closed audit).

## Verification

`tests/test_transport_recovery_279_v3.py` covers one positive case and negative
cases for self-reporting, duplicate trials, A09 identity drift, recovery over
300 ms, unresolved work, packet gaps, missing external-injection hash, and local
fallback field forgery.
