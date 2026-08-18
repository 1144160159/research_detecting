# CAEOS paper experiment closure execution record (2026-08-12)

## Frozen scope

- Paper closure contract: `contracts/caeos_paper_closure_contract_v1.json`.
- Multimodal ablation protocol: `protocols/caeos_paper_multimodal_ablation_v1.json`.
- Main development dataset: `ciciot2023`.
- Reserved confirmation datasets and seeds remain effect-blind until `M0`.
- `F0` training is forbidden until both `D0` and `P0` pass.

## Remote execution state

- GPU host: `10.0.5.103:25696`.
- Feature process PID: `1366369`.
- CICIoT2023 capture extraction: `309/309` capture markers complete.
- Current phase: class CSV merge, full-row validation, and final hashing.
- At `2026-08-12T08:24:49Z`, the dataset manifest and completion marker were absent.
- Twenty-second I/O sample: read bytes increased by `371,326,976` bytes and write
  bytes increased by `371,052,544` bytes; the process remained active with about
  `304 MiB` RSS. The exact read delta should be recomputed from the bound raw
  samples before publication; it is not a paper result.
- GPU utilization was `0%` because this phase is CPU/NFS I/O, not model training.

## Gate automation

- Active watcher PID at launch verification: `1679970`.
- Remote code root:
  `/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/paper_protocols/caeos_paper_closure_v3`.
- The watcher remains fail-closed and waits for both the CICIoT2023 dataset
  manifest and `completion.lane1.ciciot2023.json` with `all_complete=true`.
- After completion it runs, in order:
  1. disk-partitioned full-flow duplicate and cross-label fingerprint audit;
  2. exact train/deploy view-materialization equivalence audit;
  3. data card and duplicate-aware grouped split construction;
  4. `preprocess_v1` manifest construction;
  5. final paper-readiness audit.
- It does not train a model, reveal external confirmation effects, or run reserved
  confirmation seeds.

## Verification

- Remote targeted tests: `9 passed in 0.47s`.
- Remote shell syntax gate: passed.
- Local Python syntax compilation: passed.
- Local pytest is currently unavailable because the local Anaconda environment
  imports a broken `zipfile`/`pkg_resources` combination. No local pytest success
  is claimed.

### Remote SHA-256

```text
04a739df2dfd202954d087a1d830ce420150440fe757a00234da2ac60e512a5b  audit_caeos_flow_duplicates.py
3d57f750804f37b7fa3d468e37d579a90715054889cf5301557031c64c35ef08  audit_caeos_train_deploy_equivalence.py
082928c90c3a8808e18c4fb7e06e87dcc8397ab8cbf9f7d47a7c1dc6e729713e  build_caeos_paper_d0_p0_artifacts.py
417be3f59d73150801098f9b201ca5b7d6b7459aa27e1704d0302b9639469dbe  caeos_paper_views.py
b77353d07e82a37df17dd8e6da686b04eb32234cff3bf071df5afcad22792740  audit_caeos_paper_readiness.py
abf9c18ee2e7d2bb5325de1668bffd76dc4d27d1ace43536ff27b9d6263b6479  watch_caeos_paper_readiness_v1.sh
775473c2bf1759b68942684d5d1b5629d225afa06fdd1184f717a9e9f60b6497  contracts/caeos_paper_closure_contract_v1.json
bf7a5b7b41dcae00ec0e574ac74b13649e1c3df79a20c5f5234fdebd2ab26d74  protocols/caeos_paper_multimodal_ablation_v1.json
f300834ba34c47d1b8d4bbd5506f081b142889e51f12150ddf55608214ef6ce1  configs/unified_multimodal_v4.schema.json
3bf4061d62a4c10910f2740652f9676eab7b0f837c8a7bfb97746c2b64e3ad04  configs/unified_multimodal_v5.feature_views.json
```

## Current decision

`D0=FAIL`, `P0=FAIL`, and `F0_authorized=false` remain the only valid current
gate states. The next state change must be produced by the watcher from completed
artifacts, not by manually editing the readiness result.
