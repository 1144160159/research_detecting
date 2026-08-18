# Final closure development boundary (2026-08-14)

## Outcome

The repository now contains an executable, fail-closed path from bounded
algorithm-campaign evidence through candidate sealing and production Pareto
selection.  This change completes missing engineering paths; it does not turn
pending hardware or experimental evidence into a production acceptance.

## Implemented paths

1. The algorithm promotion materializer performs authoritative raw replay and
   creates a versioned promotion package.  The release-config materializer
   binds the verified winner, formal receipt, campaign contract, deployment
   candidate, real new-NIC trust-profile instance, release manifest, and Pareto
   policy without editing the source templates.
2. Stage materialization supports both one independently recomputed raw receipt
   and a complete atomic R1--R4 campaign.  The campaign path recomputes repeat
   counts, dual-backend roles, identity invariants, independence, hard gates,
   and the production Pareto metric vector before sealing any output.
3. Candidate materialization emits the previously missing
   `sealed_unified_candidate_evidence_receipt`, seals candidate records, and
   builds an exact multi-candidate set for the production selector.
4. The new-NIC R0 execution layer now includes all eight declared helper roles,
   an exact execution-plan schema, a helper-manifest builder, and a mutating
   XDP-to-DPDK runtime executor with explicit authorization, health checks,
   rollback, restoration, and create-only receipts.  The trust profile remains
   `hardware_helpers_pending` until external hardware approval binds the real
   manifest and receipt.
5. The DPDK crate now has a full capture/parse/feature/schedule/GPU-dispatch
   binary rather than only a synthetic R0 probe.  Its report output is absolute,
   canonical-parent checked, symlink rejecting, and create-only.
6. The portable A09 Rust fallback is wired into the generic XDP/AF_PACKET,
   TPACKET_V3, and DPDK full-pipeline entry points.  It can activate only when
   all artifact and quality-receipt arguments are supplied and externally
   SHA-256 pinned.  Per-flow local completion receipts and conservation are
   distinct from remote completion receipts.
7. The Python A09 exporter is deterministic and training-free, re-hashes all
   source roots before and after export, rejects symlink/hard-link ambiguity,
   and publishes the portable artifact create-only.
8. Unified release auditing and the GPU service accept a verified dynamic
   algorithm winner.  The current manifest now references the actual pending
   trust-profile instance, not its JSON Schema.  A non-A09 winner still requires
   a matching exported model and deployment candidate; the materializer will
   not synthesize those experiment artifacts.

## Verification

- Focused Python closure suite: 169 passed, 0 failed, 1 Linux-only skipped.
- Stage evidence plus campaign materialization: 23 passed.
- Physical-host isolated `hft-capture`: locked all-target check passed; 66
  tests passed, 0 failed, 4 explicit microbench tests ignored.
- Physical-host isolated `hft-dpdk`: locked all-target check passed; 21 tests
  passed, 0 failed; release full-pipeline binary SHA-256
  `f1d732a6cd3af7f0fd4585ccf67424d90eb959d2b7d51a29e6b427441ab99a9c`.
- Release capture binaries: generic SHA-256
  `5913993b1984c1efba79e2ece062a72021b44aa71c752098daae868d4b971bc4`,
  TPACKET_V3 SHA-256
  `fa2dc52e59d07f40c7494703cd8ff544543fdbd87fb18d5e9c0b5b84b604196e`.
- Current unified audit exits 2 and current production Pareto exits 10.  Both
  report pending evidence and keep production acceptance false; neither path
  crashes or silently promotes the diagnostic evidence.

## Remaining external evidence (not code completion)

Production release still requires a supported new NIC and independent traffic
generator, an externally approved 12-role R0 trust manifest, formal algorithm
campaign receipt and winner artifact, A09 local-fallback equivalence plus
physical benchmark receipt when A09 is deployed, complete primary/fallback
R1--R4 receipts, two distinct sealed joint candidates, and a successful final
Pareto recomputation.  Until those artifacts exist, all release claims remain
false by design.
