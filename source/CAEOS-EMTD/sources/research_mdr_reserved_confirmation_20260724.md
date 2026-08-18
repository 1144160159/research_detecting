# MDR-CAEOS reserved confirmation branch

## Purpose

The frozen MDR v2 pilot already declared three reserved training seeds and
three paired corruption seeds, but a positive pilot had no executable full102
branch. This change closes that result-after-pilot gap without modifying any
file bound by the active pilot protocol.

## Frozen conditional universe

- Candidate: `mdr_caeos_v1`
- Incumbent: `caeos_pairwise`
- Pilot-selected parameter reused: one global augmentation weight selected
  from known-validation only
- Training seeds: `347/349/353`
- Corruption seeds: `359/367/373`, paired by position
- Suites/scenarios: `7/102`
- Captures: `102 x 3 = 306`
- Fits: `306 x 2 = 612` clean/robust fits
- Conditions: clean plus five frozen corruption families
- Evaluations: `306 x 6 = 1836`
- Execution: four independent outer workers, eight trainer jobs each, only
  after five consecutive resource-idle observations

The protocol can only be created after a canonical positive pilot summary and
passing independent pilot audit, and only while confirmation capture,
evaluation, summary, audit, and completion counts are all zero.

## Gates

The confirmation re-applies all `5 families x 7 suites x 5 metrics = 175`
frozen threshold checks, the 25 aggregate family checks, clean Known Macro-F1
mean/worst non-inferiority, exact Pairwise output on every inactive route, and
the no-unknown/test-selection boundary. It additionally averages the three
reserved seed pairs within each scenario and requires the 95% bootstrap lower
bound of the equal-suite primary composite degradation advantage to be
strictly positive.

Every gate must pass to select MDR. Otherwise the branch retains Pairwise.
Neither outcome can set `comprehensive_sota_confirmed=true`; external data,
efficiency, deployment, and system gates remain mandatory.

## Implementation identity

- Protocol creator: `fa2e7ffe839c8e7f580c9caa1a89493fa763d3f543d50101102dabe7c2ea7e58`
- Confirmation evaluator: `52de34fe744c363d0a5fc524ebed1757011f2ebef30b2e8e371afd4bc68e37ff`
- Resumable four-worker runner: `ed148e78dd2e1c88dfa5c0df7c0771d3d802cdbc42b766267c17e1f005f6dc57`
- Summarizer/final selector: `791815c72cdb7bad98b7278589cd1ff7efefefd3979820f883db5c7360b81320`
- Independent auditor: `c8b16d8fbca1ff7c88bf992f113f856d9367fc269b9e8f19a8e120246877a1ac`
- Conditional watcher: `ffaa3dbc1dad56fe843b7c516b6ba66c45d12ca0d49529d8b87f91c0bc5ea717`
- MEDAF resume monitor: `b64cee40433de87dccf3ba77af472321a6a8a6626e5e6382c37900a8f137dab8`

All nine new implementation/test files have identical local/GPU SHA-256.
Local Python 3.12 static compilation passed. The target GPU Python 3.9
combined MDR suite passed `15/15`; the confirmation/resume subset separately
passed `6/6`. The only warnings were the pre-existing numexpr and bottleneck
version warnings.

## Scheduling state

At `2026-07-24T08:51Z`, the Pairwise-OpenDetect comparative chain had
`137/306` paired blocks, `685/1530` conditions, `274` captures, and zero
failures. MDR pilot watcher PID `1091078` remains waiting for that summary.
MDR confirmation watcher PID `3578270` waits for the pilot marker.

The existing MEDAF watcher PID `2021310` was stopped before it trained or
created metrics. Resume monitor PID `3602612` verifies its PID, command, and
stopped state, then resumes it only after MDR confirmation writes
`branch_complete`. This changes scheduling only and does not modify the MEDAF
protocol or implementation.

No MDR pilot or confirmation effect result exists at this snapshot. Pairwise
remains the accuracy incumbent, not a comprehensive robustness SOTA.
