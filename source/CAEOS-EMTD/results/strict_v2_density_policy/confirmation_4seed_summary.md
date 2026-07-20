# Density reliability blend confirmation

Runs: 152; triggers: 35

Run-level rows below are descriptive because seeds within a scenario are correlated.

| Metric | Parent | Blend | Oriented delta | W/T/L |
|---|---:|---:|---:|---:|
| unknown_auroc | 0.778520 | 0.785437 | +0.006917 | 18/117/17 |
| unknown_aupr | 0.680531 | 0.681950 | +0.001419 | 15/117/20 |
| unknown_fpr95 | 0.451772 | 0.446577 | +0.005195 | 8/124/20 |
| oscr | 0.697289 | 0.703261 | +0.005972 | 19/117/16 |

## Scenario-blocked inference

Inference units: 38 scenarios; seed repeats are averaged within each scenario.
Unknown AUROC is the pre-specified primary metric. Holm p-values control the four-metric family.

| Metric | Parent | Blend | Oriented delta | W/T/L | Wilcoxon p | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| unknown_auroc | 0.778520 | 0.785437 | +0.006917 | 5/27/6 | 0.52 | 1 |
| unknown_aupr | 0.680531 | 0.681950 | +0.001419 | 4/27/7 | 0.966 | 1 |
| unknown_fpr95 | 0.451772 | 0.446577 | +0.005195 | 2/29/7 | 0.426 | 1 |
| oscr | 0.697289 | 0.703261 | +0.005972 | 5/27/6 | 0.577 | 1 |
