# Algorithm campaign shared release gate

## Problem

The bounded A01--A10 campaign contract existed, but neither the unified
candidate audit nor the production Pareto selector bound its formal receipt.
The older algorithm-search JSON and cached optimality audit therefore formed a
separate, incomplete path: they could not prove that all ten candidates had
been rerun under the current uniform normal/fallback protocol.

The physical current-hardware campaign is a different receipt type.  It proves
three normal and three fallback full-pipeline runs and must not be reused as an
algorithm campaign receipt.

## Fix

`hft_mgbs.algorithm_campaign_gate` is the single shared import boundary used
by both release entry points.  It performs the summary/projection checks and
then invokes the frozen read-only raw replay API:

- rehashes and replays the frozen algorithm campaign contract;
- requires the formal `hft_mgbs_algorithm_qualification_campaign_receipt_v1`;
- rehashes its projected search and all ten candidate receipts;
- checks A01--A10 completeness and candidate/campaign/contract/search reverse
  bindings;
- checks that the projected mode contracts and metrics equal the corresponding
  candidate receipts;
- rejects a symlink at the declared file or any lexical parent before calling
  `resolve()`;
- maps formal POSIX absolute paths through an explicit mirror root while
  retaining the original paths for receipt/projection reverse binding, and
  rejects non-absolute, backslash, lexical `.` and lexical `..` spellings;
- recomputes the algorithm optimality audit and requires one practical winner;
- invokes `verify_algorithm_campaign_raw_replay` against the sealed campaign
  root derived from the formal receipt and refuses to trust a persisted replay
  summary;
- requires the replay to prove the unchanged before/after tree, exact 27 input
  entries, A01--A10 and ten evaluated/qualified candidates, normal/fallback,
  seeds 7/11/19, exactly 60 raw repeats, exactly 12 regenerated artifacts, and
  the same selected winner as the independently audited projection;
- requires candidate, projection and formal-receipt equality with the raw
  replay, exact receipt/contract/search hashes, `accepted=true`, no replay
  errors and `writes_campaign_tree=false`;
- preserves `production_joint_optimum_proven=false` and
  `final_pareto_ingestion_allowed=false` at the algorithm-only boundary.

The replay API calls the formal finalizer validation chain with its writer
captured in memory, compares all would-be outputs against the sealed artifacts,
and snapshots the entire campaign tree before and after.  A ten-item summary
receipt therefore still cannot substitute for the raw run, code, result,
environment and input manifests.  Any replay exception, missing prerequisite,
field drift, write attempt or tree drift keeps the shared gate closed.

`configs/release_manifest_v2.json` and `configs/final_pareto_policy_v1.json`
bind the current contract SHA-256
`3ba9a81f3099c4aa5de111c9c9eef4ad0c347b65b8af8d1eacc1d2a9c61ad10b`.
Their receipt is intentionally `null` until the GPU campaign is formally
completed, so both paths currently fail closed with
`algorithm_campaign.receipt.reference`.

The unified CLI reuses its existing `--receipt-root` for this mapping.  The
production selector provides `--algorithm-receipt-root`; without a mirror it
may still run directly on the GPU host where the bound absolute paths exist.

The physical Stage A/B receipt chain was not changed.  Stage A continues to
prove full-pipeline normal3/fallback3 evidence, and Stage B continues to
compare at least two distinct physical evaluation identities.  Directly
binding the algorithm-campaign result into that separate scoped Stage B path
remains an explicit release-wiring gap; until it is added, that path must not
be treated as proof of algorithm-global optimality.

## Verification

- `python tests/test_algorithm_campaign_gate.py -v`: covers null receipt,
  lexical symlinks, strict mirror mapping, hash drift, raw-replay success, and
  fail-closed mutation of every release-critical replay field.
- `python tests/test_final_pareto_selector.py -q`: 19/19 passed.
- `python -m py_compile ...`: passed for the shared verifier and both release
  entry points.
- Current unified CLI exits 2 and production Pareto CLI exits 10; both include
  `algorithm_campaign.receipt.reference`, confirming the pending state cannot
  be promoted.

The local bundled pytest environment is broken by an unrelated `zipfile`
shadow/import failure.  Tests above were therefore executed with the standard
library `unittest` runner.  The unified test module's existing package import
also cannot be loaded directly in this checkout, but the unified CLI and the
new gate-specific tests were executed successfully.

The currently versioned release candidate remains A09.  If a formal campaign
selects another winner, it must still require a new candidate, policy, manifest
and corresponding physical evaluation version; it must never silently rewrite
the released algorithm identity.
