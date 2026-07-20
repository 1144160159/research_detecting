# Strict-v4 suite-aware known-validation router development

Runs: 60; unique suite/scenario blocks: 24.
Freeze candidate: **true**; manifest: `39f6f66d419d60ed808d07b8beed50350f5144d9bc248e56371323bbe9bb9aeb`.

| Suite | Rule | AUROC | AUPR | FPR95 oriented | OSCR | Nested pass |
|---|---|---:|---:|---:|---:|---:|
| cic_iot2023 | cauchy_if_class_q95_std_delta_ge_q35 | +0.018704 | +0.017513 | +0.081805 | +0.032754 | true |
| cic_ton_iot | cauchy_if_known_class_count_le_q65 | +0.028163 | +0.022101 | +0.116299 | +0.034499 | true |

Rules may use known suite identity and known-validation features only. All opened test outcomes are development evidence, not confirmation.
