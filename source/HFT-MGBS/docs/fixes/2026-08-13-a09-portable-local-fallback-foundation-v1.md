# A09 portable local-fallback foundation v1

## Scope and status

This change adds an intentionally unwired foundation. It does not alter the
dispatcher, scheduler, metrics, runner, current-hardware validator, release, or
unified pipeline. It therefore must not increment `local_fallback_completed`
and must not set `quality_qualified=true`.

## Read-only feasibility evidence

- Frozen bundle: 8,541,522 bytes; SHA-256
  `fa9d29858bb7a20f9a66be2105a6182368e4b3029a59ead5fd77f6228b0eb5d2`.
- Three members, 200 trees/member, 262,358 total nodes.
- Member nodes: 87,866 / 87,672 / 86,820; maximum depth: 26 / 27 / 27;
  mean member maximum depth: 19.355 / 19.285 / 19.075.
- Frozen vectorizer: 34 projected features; Rust capture input: 38 raw features.
- Runtime engine identity observed in the frozen runtime manifest:
  `numpy_exact`, engine SHA-256
  `e4d18c67626b6b066ee740ad6dc722e3789e3a60dd18925ab47dffab702264c4`.

At 1,160 flows/s the upper-rate workload is 696,000 tree traversals/s, roughly
13.2 million branch decisions/s at depth 19. A compact Rust representation is
feasible; reserve two isolated physical cores until a release-build benchmark
on 10.0.5.8 proves the actual P99 and CPU budget. Three cores are the rollback
budget if cache misses or feature projection exceed that estimate.

## Artifact and arithmetic contract

`scripts/export_a09_portable_fallback.py` runs only on the GPU host where the
joblib bundle already exists. It requires operator-supplied SHA-256 roots for
the bundle, `a09_numpy_inference.py`, and campaign contract, hashes sources
before and after loading, validates A09/ExtraTrees/profile/seeds/tree count and
feature order, and atomically writes a deterministic little-endian artifact.
No model is copied to Windows by this workflow.

`rust/hft-capture/src/a09_fallback.rs` is not exported by `lib.rs` and is not
called by production code. Its standalone tests validate the artifact hash,
all embedded identities, feature order, tree topology, finite bounds, f32 split
input against f64 threshold, ordered tree reduction, ordered member reduction,
and threshold decision. The implementation has an internal SHA-256 function so
no dependency or Cargo lock change is required.

## Remaining hard gates before wiring

1. Run the exporter on the GPU host against a trusted current-hardware prepare
   receipt or release trust root; an arbitrary self-supplied hash is not enough.
2. Transfer only the exported portable artifact and an independent receipt to
   10.0.5.8, then verify artifact/source/engine/campaign hashes there.
3. On a frozen official holdout, compare every Rust probability bit and label
   with the bound `numpy_exact_v1` result. Any mismatch keeps quality false.
4. Benchmark batch 1 and expected fallback concurrency on isolated physical
   cores. Required evidence includes P50/P99/max, flows/s, node visits/s, CPU,
   RAM, artifact SHA, binary SHA, and compiler flags.
5. Only after gates 1–4 may a separate integration change add circuit-breaker
   routing, per-flow receipts, conservation accounting, fault injection, and
   recovery. Remote retry remains transport recovery and is never relabeled as
   local completion.

