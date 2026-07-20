# Strict-v4 known-validation router development analysis

Runs: 30; scenarios: 18.
Full-development rule: `cauchy_if_cauchy_class_q95_std_ge_q35`.
Freeze candidate: **true**.
Runtime inputs use known-validation only; development rule selection uses opened unknown test labels.

| Nested LOSO | AUROC | AUPR | FPR95 oriented | OSCR |
|---|---:|---:|---:|---:|
| Combined gain | +0.019106 | +0.023570 | +0.092942 | +0.028371 |

Nested selected paths: `{'cauchy_if_cauchy_class_q95_std_ge_q35': 14, 'cauchy_if_class_q95_std_delta_ge_q35': 2, 'cauchy_if_class_q95_std_delta_ge_q20': 1, 'cauchy_if_class_q95_std_delta_ge_q50': 1}`.
